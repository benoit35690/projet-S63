# -*- coding: utf-8 -*-
# module Constantes
"""
    Definie les constantes utilisées dans le projet
"""

# liste des PIN du Raspberry
PIN_CADRAN             = 4
PIN_COMBINE            = 3
PIN_SOLENOIDE_GAUCHE   = 1
PIN_SOLENOIDE_DROIT    = 2
PIN_COMBINE_ANTIREBOND = 100


# aprés 0.9s on considère que le cadran a fini de numéroter le chiffre
TIMOUT_CHIFFRE_CADRAN  = 0.9
TEMPO_ENTRE_IMPULSIONS = 0.002

TIMER_COMBINE          = 2
TIMEOUT_VERIF_COMBINE  = 1

TIMEOUT_AUTOMATE       = 0.5

# liste des type de message de la queue de messages
MESSAGE_DECROCHE       = 1
MESSAGE_RACCROCHE      = 2
MESSAGE_CHIFFRE        = 3

# liste des états de l'automate

# liste des transitions de l'automate

# True si la machine est un Raspberry Pi
IS_RASPBERRY_PI = True
