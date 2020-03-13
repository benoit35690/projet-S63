# -*- coding: utf-8 -*-
# module Automate
"""

"""
# from threading import Timer
import time
from modules.cadran.cadran import Cadran
from modules.combine.combine import Combine


class Automate:
    automate_actif = True
    Cadran  = None
    Combine = None

    def __init__(self):
        print "[Automate __init__]"
        self.Cadran = Cadran()
        self.Combine = Combine()

        self.Cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)
        self.Combine.RegisterCallback(
            NotificationDecroche=self.ReceptionDecroche,
            NotificationRaccroche=self.ReceptionRaccroche)

        #while self.automate_actif:
        #    time.sleep(0.1)

    def ArretAutomate(self):
        print "[Automate Exit]"
        self.Cadran.ArretDetectionImpulsions()
        self.Combine.ArretVerificationDecroche()
        self.automate_actif = False
        #sys.exit(0)

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)

    def ReceptionDecroche(self):
        print ("[Automate ReceptionDecroche]")

    def ReceptionRaccroche(self):
        print ("[Automate ReceptionRaccroche]")

    def ReceptionVerifDecroche(self, etat):
        print ("[Automate ReceptionVerifDecroche]", etat)
