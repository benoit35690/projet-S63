# -*- coding: utf-8 -*-
# module Cadran
"""
    Module qui gère les impulsions electriques reçues du cadran rotatif du S63
    Detecte le chiffre composé sur le cadran en comptant les impulstions
    Notifie le chiffre composé

    Regles materielles:
        1 impulsion -> chiffre 1
        9 impulsions -> chiffre 9
        10 impulstions -> chiffre 0
"""

import Constantes
from threading import Timer
import time
if Constantes.IS_RASPBERRY_PI:
    import RPi.GPIO as GPIO


class Cadran:
    detection_impulsions = True
    compteur_pulsations = 0
    numero_compose = ""

    # Timer pour gérer la numérotation d'un chiffre
    timer_chiffre = None
    last_input = 0

    notification_prefixe_envoye = False

    def __init__(self):
        """
            Initialisation de la PIN du Raspberry reliée au cadran du S63
        """
        print "[Cadran __init__]"
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)

        # Configuration du GPIO pour écouter les mouvements du cadran
        # On utilise un "pull up" pour forcer l'état haut quand le circuit
        # du cadran est ouvert
        # A chaque changement d'état la callback CompteImpulsions est appelée
        GPIO.setup(Constantes.PIN_CADRAN, GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)
        try:
            GPIO.add_event_detect(Constantes.PIN_CADRAN, GPIO.BOTH,
                                  callback=self.CompteImpulsions)
            #while self.detection_impulsions:
            #    time.sleep(0.1)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
        finally:
            GPIO.cleanup()

    def ArretDetectionImpulsions(self):
        """
            Stop le mecanisme de detection des impulsions
        """
        print ("[Cadran ArretDetectionImpulsions]")
        self.detection_impulsionn = False

    # Enregistrement des callbacks
    def RegisterCallback(self, NotificationChiffre):
        """
            Enregistrement de la callbacks utilisée pour notifier quand
            un chiffre est composé sur le cadran
        """
        print ("[Cadran RegisterCallback]")
        self.NotificationChiffre = NotificationChiffre

    def CompteImpulsions(self, channel):
        """
            Compte les impulsions reçues et arme un timer de fin
            Une impulsion est définie par une transition sur l'entrée PIN
            La fonction de callback est executée dans un thread séparé
            instancié par RPi.GPIO
        """
        print ("[Cadran CompteImpulsions]")
        if channel == Constantes.PIN_CADRAN:
            input = GPIO.input(Constantes.PIN_CADRAN)
            if input and not self.last_input:
                self.compteur_pulsations += 1

                if self.timer_chiffre is not None:
                    self.timer_chiffre.cancel()

                self.timer_chiffre = Timer(Constantes.TIMOUT_CHIFFRE_CADRAN,
                                           self.FinNumerotationChiffre)
                self.timer_chiffre.start()
            self.last_input = input
            time.sleep(Constantes.TEMPO_ENTRE_IMPULSIONS)
        else:
            print ("[Cadran CompteImpulsions] channel incorect = ", channel)

    # Quand la numérotation d'un chiffre est terminée
    def FinNumerotationChiffre(self):
        """
            Appelé par le timer quand la numérotation d'un chiffre est finie
            Envoie une notification avec le chiffre composé
        """
        print ("[Cadran FinNumerotationChiffre]")
        if self.compteur_pulsations == 10:
            self.compteur_pulsations = 0
        self.numero_compose += str(self.compteur_pulsations)
        self.NotificationChiffre(self.compteur_pulsations)
        self.compteur_pulsations = 0
