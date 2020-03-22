import os
import Queue
import threading
import signal
import sys
import yaml

from threading import Timer
from modules.Cadran import Cadran

callback_queue = Queue.Queue()

class Automate_S63:
    dial_number = ""
    offHook = False
    offHookTimeoutTimer = None
    RotaryDial = None

    def __init__(self):
        print ("[Automate_S63 __init__]")

        signal.signal(signal.SIGINT, self.OnSignal)

        self.cadran = Cadran()
        self.cadran.RegisterCallback(NumberCallback = self.ReceptionChiffre)
        raw_input("Waiting.\n")

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)
#        message = Message(message_type=Constantes.MESSAGE_CHIFFRE,
#                          chiffre=chiffre)
#        self.message_queue.put(message)

#    def OnHook(self):
#        print "Daemon OnHook [PHONE] On hook"
#        self.offHook = False

#    def OffHook(self):
#        print "Daemon OffHook [PHONE] Off hook"
#        self.offHook = True
#        self.dial_number = ""

#        self.offHookTimeoutTimer = Timer(5, self.OnOffHookTimeout)
#        self.offHookTimeoutTimer.start()

#    def OnVerifyHook(self, state):
#        #print("[Daemon OnVerifyHook %s]" % state)
#        #if not state:
#            #self.Ringtone.stophandset()
#        if state == 1:
#            self.offHook = False
#        else:
#            self.offHook = True

#    def OnIncomingCall(self):
#        print "[Daemon OnIncomingCall]"

    def OnOutgoingCall(self):
        print "[Daemon OnOutgoingCall] "

    def OnRemoteHungupCall(self):
        print "[Daemon HUNGUP] Remote disconnected the call"

    def OnSelfHungupCall(self):
        print "[Daemon HUNGUP] Local disconnected the call"

    def OnOffHookTimeout(self):
        print "[Daemon OFFHOOK TIMEOUT]"

    def GotDigit(self, digit):
        print "[Daemon GotDigit DIGIT] Got digit: %s" % digit
        self.dial_number += str(digit)
        print "[Daemon GotDigit NUMBER] We have: %s" % self.dial_number
        print "[Daemon GotDigit NUMBER] len = %s" % len(self.dial_number)
        if self.dial_number == "0666":
            os.system("halt")

        if len(self.dial_number) == 2:
            if self.offHook:
                print "[Daemon GotDigit PHONE] Dialing number: %s" % self.dial_number
                self.dial_number = "malo35"
                print "[Daemon GotDigit PHONE] Dialing number: %s" % self.dial_number
                self.dial_number = ""

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        sys.exit(0)

def main():
    print "[main]"
    TDaemon = Automate_S63()

if __name__ == "__main__":
    main()
