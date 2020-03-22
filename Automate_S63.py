import os
import Queue
import threading
import signal
import sys
import RPi.GPIO as GPIO

from threading import Timer
from modules.Cadran import Cadran
from modules.Combine import Combine

callback_queue = Queue.Queue()

class Automate_S63:
    dial_number = ""
    offHook = False
    offHookTimeoutTimer = None

    def __init__(self):
        print ("[Automate_S63 __init__]")

        signal.signal(signal.SIGINT, self.OnSignal)

        self.cadran = Cadran()
        self.cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)

        self.combine = Combine()
        self.combine.RegisterCallback(
                    NotificationDecroche=self.ReceptionDecroche,
                    NotificationRaccroche=self.ReceptionRaccroche,
                    NotificationVerifDecroche=self.ReceptionVerifDecroche)

        raw_input("Waiting.\n")

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)
#        message = Message(message_type=Constantes.MESSAGE_CHIFFRE,
#                          chiffre=chiffre)
#        self.message_queue.put(message)

    def ReceptionDecroche(self):
        print ("[Automate ReceptionDecroche]")
        #message = Message(message_type=Constantes.MESSAGE_DECROCHE, chiffre=0)
        #self.message_queue.put(message)

    def ReceptionRaccroche(self):
        print ("[Automate ReceptionRaccroche]")
        #message = Message(message_type=Constantes.MESSAGE_RACCROCHE, chiffre=0)
        #self.message_queue.put(message)

    def ReceptionVerifDecroche(self, etat):
        print ("[Automate ReceptionVerifDecroche]", etat)
        if etat == GPIO.HIGH:
            print("[Combine VerifieCombine] HIGH -> Raccroche")
        else:
            print("[Combine VerifieCombine] LOW -> Decroche")

    def TraiteMessage(self, message):
        print ("[Automate TraiteMessage] message_type=",
               message.message_type)

    def OnOffHookTimeout(self):
        print "[Daemon OFFHOOK TIMEOUT]"

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        self.combine.ArretVerificationDecroche()
        sys.exit(0)

def main():
    print "[main]"
    TDaemon = Automate_S63()

if __name__ == "__main__":
    main()
