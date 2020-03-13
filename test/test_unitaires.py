# -*- coding: utf-8 -*-
# module test_unitaire
"""
    Module de tests unitaires du projet
    le module RPi.GPIO est émulé pour les tests
    les tests unitaires sont à executer sur linux (pas Raspberry)
"""
import unittest
# from test.test_cadran import Test_Cadran
import test_cadran
# from test_cadran import Test_Cadran


class Test_unitaire(unittest.TestCase):

    Test_Cadran = None

    def __init__(self):
        print ("[STARTUP]")
        self.Test_Cadran = test_cadran.Test_Cadran()

    def test_cadran(self):
        print ("[test_cadran]")
        self.Test_Cadran.Test_Digit_1(1)
