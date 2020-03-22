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
import RPi.GPIO as GPIO

class Cadran:

    # We'll be reading BCM GPIO 4 (pin 7 on board)
    pin_rotary = 4

    # We'll be reading on/off hook events from BCM GPIO 3
#    pin_onhook = 3

    # After 900ms, we assume the rotation is done and we get
    # the final digit.
    digit_timeout = 0.9

    # We keep a counter to count each pulse.
    current_digit = 0

    # Simple timer for handling the number callback
    number_timeout = None

    last_input = 0

    # Timer to ensure we're on hook
#    onhook_timer = None
#    should_verify_hook = True

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
        GPIO.add_event_detect(Constantes.PIN_CADRAN, GPIO.BOTH,
                              callback=self.NumberCounter)

    # Handle counting of rotary movements and respond with digit after timeout
    def NumberCounter(self, channel):
        input = GPIO.input(self.pin_rotary)
        #print "NumberCounter [INPUT] %s (%s)" % (input, channel)
        if input and not self.last_input:
            self.current_digit += 1

            if self.number_timeout is not None:
                self.number_timeout.cancel()

            self.number_timeout = Timer(self.digit_timeout, self.FoundNumber)
            self.number_timeout.start()
        self.last_input = input
        time.sleep(0.002)

    # Wrapper around the off/on hook event
#    def HookEvent(self, channel):
#        input = GPIO.input(self.pin_onhook)
#        #if input == GPIO.HIGH:
#        #    print ("[RotaryDial HookEvent] HIGH")
#        #else:
#        #    print("[RotaryDial HookEvent] LOW")
#        if input:
#            self.hook_state = 1
#            self.OnHookCallback()
#        else:
#            self.hook_state = 0
#            self.OffHookCallback()
#        #self.OnHookCallback()

#    def StopVerifyHook(self):
#        print("[RotaryDial StopVerifyHook]", input)
#        self.should_verify_hook = False

#    def verifyHook(self):
#        while self.should_verify_hook:
#            state = GPIO.input(self.pin_onhook)
#            #if state == GPIO.HIGH:
#            #    print("[RotaryDial verifyHook] HIGH")
#            #else:
#            #    print("[RotaryDial verifyHook] LOW")
#            self.OnVerifyHook(state)
#            time.sleep(1)

    # When the rotary movement has timed out, we callback with the final digit
    def FoundNumber(self):
        if self.current_digit == 10:
            self.current_digit = 0
        self.NumberCallback(self.current_digit)
        self.current_digit = 0

    # Handles the callbacks we're supplying
    def RegisterCallback(self, NumberCallback):
        self.NumberCallback = NumberCallback

#    def RegisterCallback(self, NumberCallback, OffHookCallback, OnHookCallback, OnVerifyHook):
#        self.NumberCallback = NumberCallback
#        self.OffHookCallback = OffHookCallback
#        self.OnHookCallback = OnHookCallback
#        self.OnVerifyHook = OnVerifyHook
#        input = GPIO.input(self.pin_onhook)
#        if input:
#            self.OffHookCallback()
#        else:
#            self.OnHookCallback()
