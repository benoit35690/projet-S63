# -*- coding: utf-8 -*-
# module test_cadran
"""
    Module de tests unitaires du module cadran
    le module RPi.GPIO est émulé pour les tests
    les tests unitaires sont à executer sur linux (pas Raspberry)
"""

import unittest
from unittest.mock import Mock
import RPi.intern
# from modules.cadran import Cadran
from modules.cadran import Cadran
import Constantes
import time


class Test_Cadran(unittest.TestCase):

#    RPi.intern.i = True
#    Cadran = None

#    def __init__(self):
#        print ("[Test_Cadran __init__ ]")
#        self.Cadran = Cadran()
#        self.Cadran.RegisterCallback(NotificationChiffre=self.GotDigit)

#    def GotDigit(self, digit):
#        print ("[Module Cadran notifies a digit]: ", digit)

    def test_Digit_1(self):
        print ("[test_Digit_1]")
        cadran = Cadran()
        f = Mock()
        cadran.RegisterCallback(f)

        RPi.intern.i = True
        time.sleep(Constantes.TEMPO_ENTRE_IMPULSIONS)
        RPi.intern.i = True

        f.assert_called_with("1")


if __name__ == '__main__':
    unittest.main()
