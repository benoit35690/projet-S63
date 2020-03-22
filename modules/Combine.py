# Rotary Dial Parser
# Expects the following hardware rules:
# 1 is 1 pulse
# 9 is 9 pulses
# 0 is 10 pulses

import RPi.GPIO as GPIO
from threading import Timer
import time

class Combine:

    # We'll be reading on/off hook events from BCM GPIO 3
    pin_onhook = 3

    # Timer to ensure we're on hook
    onhook_timer = None
    should_verify_hook = True

    def __init__(self):
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)

        # Listen for on/off hooks
        GPIO.setup(self.pin_onhook, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin_onhook, GPIO.BOTH, callback = self.HookEvent, bouncetime=100)

        self.onhook_timer = Timer(2, self.verifyHook)
        self.onhook_timer.start()

    # Wrapper around the off/on hook event
    def HookEvent(self, channel):
        input = GPIO.input(self.pin_onhook)
        if input:
            self.hook_state = 1
            self.OnHookCallback()
        else:
            self.hook_state = 0
            self.OffHookCallback()
        #self.OnHookCallback()

    def StopVerifyHook(self):
        print("[RotaryDial StopVerifyHook]", input)
        self.should_verify_hook = False

    def verifyHook(self):
        while self.should_verify_hook:
            state = GPIO.input(self.pin_onhook)
            #if state == GPIO.HIGH:
            #    print("[RotaryDial verifyHook] HIGH")
            #else:
            #    print("[RotaryDial verifyHook] LOW")
            self.OnVerifyHook(state)
            time.sleep(1)


    def RegisterCallback(self, OffHookCallback, OnHookCallback, OnVerifyHook):
        self.OffHookCallback = OffHookCallback
        self.OnHookCallback = OnHookCallback
        self.OnVerifyHook = OnVerifyHook
        input = GPIO.input(self.pin_onhook)
        if input:
            self.OffHookCallback()
        else:
            self.OnHookCallback()
