import os
import Queue
from threading import Thread
import threading
import signal
import sys
import RPi.GPIO as GPIO
import Constantes
from threading import Timer
from modules.Cadran import Cadran
from modules.Combine import Combine

callback_queue = Queue.Queue()


class Message:
    transition_automate = 0
    chiffre_compose     = 0
    numero_compose      = 0


class Automate_S63:
    dial_number = ""
    automate_actif = True
    etat_automate = Constantes.ETAT_INIT
    offHook = False
    offHookTimeoutTimer = None

    def __init__(self):
        print ("[Automate_S63 __init__]")

        signal.signal(signal.SIGINT, self.OnSignal)

        self.etat_automate = Constantes.ETAT_INIT

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
        message.transition_automate = Constantes.TRANSITION_CHIFFRE_COMP
        message.chiffre_compose = chiffre
        self.message_queue.put(message)

    def ReceptionDecroche(self):
        #print ("[Automate ReceptionDecroche]")
        message = Message()
        message.transition_automate = Constantes.TRANSITION_DECROCHE
        self.message_queue.put(message)

    def ReceptionRaccroche(self):
        #print ("[Automate ReceptionRaccroche]")
        message = Message()
        message.transition_automate = Constantes.TRANSITION_RACCROCHE
        self.message_queue.put(message)

    def ReceptionVerifDecroche(self, etat):
        #print ("[Automate ReceptionVerifDecroche]", etat)
        message = Message()
        if etat == GPIO.HIGH:
            #print("[Combine VerifieCombine] HIGH -> Raccroche")
            message.transition_automate = Constantes.TRANSITION_RACCROCHE
        else:
            #print("[Combine VerifieCombine] LOW -> Decroche")
            message.transition_automate = Constantes.TRANSITION_DECROCHE
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
        if message == Constantes.TRANSITION_RACCROCHE:
            self.TraiteTransitionRaccroche(message)
        elif message == Constantes.TRANSITION_DECROCHE:
            self.TraiteTransitionDecroche(message)
        elif message == Constantes.TRANSITION_APPEL_ENTRANT:
            self.TraiteTransitionAppelEntrant(message)
        elif message == Constantes.TRANSITION_FIN_APPEL:
            self.TraiteTransitionFinAppel(message)
        elif message == Constantes.TRANSITION_TIMER_OUBLIE:
            self.TraiteTransitionTimerOublie(message)
        elif message == Constantes.TRANSITION_ECHEC_NUM:
            self.TraiteTransitionEchecNumerotation(message)
        elif message == Constantes.TRANSITION_CHIFFRE_COMP:
            self.TraiteTransitionChiffreCompose(message)
        elif message == Constantes.TRANSITION_NUMERO:
            self.TraiteTransitionNumeroCompose(message)
        else:
            print ("[Automate TraiteMessage] MESSAGE INCONNU message_type=",
                   message.message_type)

    def TraiteTransitionRaccroche(self, message):
        print ("[Automate TraiteTransitionRaccroche] message_type=",
               message.message_type)



    def TraiteTransitionDecroche(self, message):
        print ("[Automate TraiteTransitionDecroche] message_type=",
               message.message_type)

    def TraiteTransitionAppelEntrant(self, message):
        print ("[Automate TraiteTransitionAppelEntrant] message_type=",
               message.message_type)

    def TraiteTransitionFinAppel(self, message):
        print ("[Automate TraiteTransitionFinAppel] message_type=",
               message.message_type)

    def TraiteTransitionTimerOublie(self, message):
        print ("[Automate TraiteTransitionTimerOublie] message_type=",
               message.message_type)

    def TraiteTransitionEchecNumerotation(self, message):
        print ("[Automate TraiteTransitionEchecNumerotation] message_type=",
               message.message_type)

    def TraiteTransitionChiffreCompose(self, message):
        print ("[Automate TraiteTransitionChiffreCompose] message_type=",
               message.message_type)

    def TraiteTransitionNumeroCompose(self, message):
        print ("[Automate TraiteTransitionNumeroCompose] message_type=",
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
