# -*- coding: utf-8 -*-
# module Automate
"""

"""
from modules.cadran.cadran import Cadran
from modules.combine.combine import Combine


class Automate:
    Cadran  = None
    Combine = None

    def __init__(self):
        self.Cadran = Cadran()
        self.Combine = Combine()

        self.Cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)
        self.Combine.RegisterCallback(
            NotificationDecroche=self.ReceptionDecroche,
            NotificationRaccroche=self.ReceptionRaccroche)

    def ArretAutomate(self):
        print "[Automate Exit]"
        self.Cadran.ArretDetectionImpulsions()
        self.Combine.ArretVerificationDecroche()

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)

    def ReceptionDecroche(self):
        print ("[Automate ReceptionDecroche]")

    def ReceptionRaccroche(self):
        print ("[Automate ReceptionRaccroche]")

    def ReceptionVerifDecroche(self, etat):
        print ("[Automate ReceptionVerifDecroche]", etat)
