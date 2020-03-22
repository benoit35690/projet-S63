# import os
import Queue
from threading import Thread
# import threading
import signal
import sys
import RPi.GPIO as GPIO
import Constantes
# from threading import Timer
from modules.Ringtone import Ringtone
from modules.RotaryDial import RotaryDial
from modules.Cadran import Cadran
from modules.Combine import Combine

callback_queue = Queue.Queue()


class Message:
    message_type = 0
    chiffre = 0


class Automate_S63:
    dial_number = ""
    automate_actif = True
    offHook = False
    offHookTimeoutTimer = None

    def __init__(self):
        print ("[Automate_S63 __init__]")

        signal.signal(signal.SIGINT, self.OnSignal)

        # creation de la queue de messages
        self.message_queue = Queue.Queue(maxsize=0)

        # demarre le thread de la class Automate
        self.worker = Thread(target=self.FonctionWorkerThread)
        self.worker.setDaemon(True)
        self.worker.start()

        self.cadran = Cadran()
        self.cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)

        self.combine = Combine()
        self.combine.RegisterCallback(
                    NotificationDecroche=self.ReceptionDecroche,
                    NotificationRaccroche=self.ReceptionRaccroche,
                    NotificationVerifDecroche=self.ReceptionVerifDecroche)

        raw_input("Waiting.\n")

    def ReceptionChiffre(self, chiffre):
        #print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)
        message = Message()
        message.message_type = Constantes.MESSAGE_CHIFFRE
        message.chiffre = chiffre
        self.message_queue.put(message)

    def ReceptionDecroche(self):
        #print ("[Automate ReceptionDecroche]")
        message = Message()
        message.message_type = Constantes.MESSAGE_DECROCHE
        message.chiffre = 0
        self.message_queue.put(message)

    def ReceptionRaccroche(self):
        #print ("[Automate ReceptionRaccroche]")
        message = Message()
        message.message_type = Constantes.MESSAGE_RACCROCHE
        message.chiffre = 0
        self.message_queue.put(message)

    def ReceptionVerifDecroche(self, etat):
        #print ("[Automate ReceptionVerifDecroche]", etat)
        message = Message()
        message.chiffre = 0
        if etat == GPIO.HIGH:
            #print("[Combine VerifieCombine] HIGH -> Raccroche")
            message.message_type = Constantes.MESSAGE_RACCROCHE
        else:
            #print("[Combine VerifieCombine] LOW -> Decroche")
            message.message_type = Constantes.MESSAGE_DECROCHE
        self.message_queue.put(message)

    def FonctionWorkerThread(self):
        """
        Fonction Worker Thread
        S'execute en parallele des autres taches
        Boucle infinie (tant que l'automate est actif)
            - Extrait un message de la queue de message
            - Traite le message
        On attend un message au plus TIMEOUT_AUTOMATE
        """
        print "[Automate FonctionWorkerThread start]"
        while self.automate_actif:
            #print "[Automate FonctionWorkerThread wait for a message]"
            try:
                message = self.message_queue.get(True,
                                                 Constantes.TIMEOUT_AUTOMATE)
                if message is not None:
                    self.TraiteMessage(message)
            except Queue.Empty:
                # print("Automate FonctionWorkerThread message_queue empty")
                continue
        print "[Automate Fonction_Worker_Thread] sortie de la boucle"

    def TraiteMessage(self, message):
        print ("[Automate TraiteMessage] message_type=",
               message.message_type)

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        self.combine.ArretVerificationDecroche()
        self.automate_actif = False
        sys.exit(0)


def main():
    print "[main]"
    TDaemon = Automate_S63()


if __name__ == "__main__":
    main()
