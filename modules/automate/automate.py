# -*- coding: utf-8 -*-
# module Automate
"""

"""
import sys
import signal
from modules.cadran.cadran import Cadran
from modules.combine.combine import Combine


class Automate:

    Cadran  = None
    Combine = None

    def __init__(self):
#        signal.signal(signal.SIGINT, self.OnSignal)
        fonctionnement_automate = True

        self.Cadran = Cadran()
        self.Combine = Combine()

        self.Cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)
        self.Combine.RegisterCallback(
            NotificationDecroche=self.ReceptionDecroche,
            NotificationRaccroche=self.ReceptionRaccroche),
            # NotificationVerifDecroche=self.ReceptionVerifDecroche)

        while fonctionnement_automate:
            # do nothing

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)

    def ReceptionDecroche(self):
        print ("[Automate ReceptionDecroche]")

    def ReceptionRaccroche(self):
        print ("[Automate ReceptionRaccroche]")

    def ReceptionVerifDecroche(self, etat):
        print ("[Automate ReceptionVerifDecroche]", etat)

    def Exit(self):
        print "[Automate Exit]"
        self.Cadran.ArretDetectionImpulsions()
        self.Combine.ArretVerificationDecroche()
        self.fonctionnement_automate = False

    def OnSignal(self, signal, frame):
        print "[Automate SIGNAL] Shutting down on %s" % signal
        sys.exit(0)
