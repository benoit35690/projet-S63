# -*- coding: utf-8 -*-
# module Combine
"""
    Module qui gère le contact electrique reçue de l'interrupteur du combine
    du S63
    Notifie l'état du combiné
"""

import Constantes
# from threading import Timer
import time
if Constantes.IS_RASPBERRY_PI:
    import RPi.GPIO as GPIO


class Combine:
    detection_combine = True
    # Timer pour vérifier l'état du combiné
    timer_combine = None
    verification_combine_active = True

    def __init__(self):
        """
            Initialisation de la PIN du Raspberry reliée au combiné du S63
        """
        # Set GPIO mode to Broadcom SOC numbering
        if Constantes.IS_RASPBERRY_PI:
            GPIO.setmode(GPIO.BCM)

        # Configuration du GPIO pour écouter les mouvements du cadran
        # On utilise un "pull up" pour forcer l'état haut quand l'interrupteur
        # du combiné est ouvert
        # pour éviter d'être notifié plusieurs fois par évenement, on définie
        # un temps d'anti-rebond de 100 ms
        # A chaque changement d'état la callback EvenementDecroche est appelée
        if Constantes.IS_RASPBERRY_PI:
            GPIO.setup(Constantes.PIN_COMBINE, GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            try:
                GPIO.add_event_detect(Constantes.PIN_COMBINE, GPIO.BOTH,
                                      callback=self.EvenementDecroche,
                                      bouncetime=Constantes.PIN_COMBINE_ANTIREBOND)
                while self.detection_combine:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
            finally:
                GPIO.cleanup()

        # on arme un timer qui va vérifier périodiquement l'état du combiné
        # self.timer_combine = Timer(Constantes.TIMER_COMBINE,
        #                           self.VerifieCombine)
        # self.timer_combine.start()

    def ArretDetectionCombine(self):
        """
            Stop le mecanisme de detection des impulsions
        """
        self.detection_combine = False

    # Enregistrement des callbacks
    def RegisterCallback(self, NotificationDecroche, NotificationRaccroche):
    #                     NotificationVerifDecroche):
        """
            Enregistrement de la callbacks utilisée pour notifier quand
            l'état du combiné change
        """
        self.NotificationDecroche = NotificationDecroche
        self.NotificationRaccroche = NotificationRaccroche
#        self.NotificationVerifDecroche = NotificationVerifDecroche
        if Constantes.IS_RASPBERRY_PI:
            input = GPIO.input(Constantes.PIN_COMBINE)
        if input:
            self.NotificationDecroche()
        else:
            self.NotificationRaccroche()

    def ArretVerificationDecroche(self):
        self.verification_combine_active = False

#    def VerifieCombine(self):
#        while self.verification_combine_active:
#            state = 0
#            if Constantes.IS_RASPBERRY_PI:
#                state = GPIO.input(Constantes.PIN_COMBINE)
#            self.NotificationVerifDecroche(state)
#            time.sleep(Constantes.TIMEOUT_VERIF_COMBINE)

    def EvenementDecroche(self, channel):
        if channel == Constantes.PIN_COMBINE:
            if Constantes.IS_RASPBERRY_PI:
                input = GPIO.input(Constantes.PIN_COMBINE)
            if input:
                self.EtatDecroche = 1
                self.NotificationRaccroche()
            else:
                self.EtatDecroche = 0
                self.NotificationDecroche()
        else:
            print ("[Combine EvenementDecroche] channel incorect = ", channel)
