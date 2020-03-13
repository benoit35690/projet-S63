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
        """
            Initialisation de la PIN du Raspberry reliée au cadran du S63
        """
        signal.signal(signal.SIGINT, self.OnSignal)

        self.Cadran = Cadran()
        self.Combine = Combine()

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        sys.exit(0)
