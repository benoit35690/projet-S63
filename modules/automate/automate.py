# -*- coding: utf-8 -*-
# module Automate
"""
    Classe automate
    demarre un thread et gere une queue de messages
    chaque notification reçue empile un message dans la queue
    la fonction worker thread dépile les messages et les traite
    le traitement consiste à gérer les transitions de l'automate
    à chaque changement d'état une ou plusieurs actions seront faites
"""
# from threading import Timer
import Constantes
import Queue
from threading import Thread
from modules.cadran.cadran import Cadran
from modules.combine.combine import Combine


class Message:
    message_type = 0
    chiffre = 0


class Automate:
    automate_actif = True
    cadran  = None
    combine = None

    def __init__(self):
        """
            Fonction __init__
            creation d'une queue de messages
            creation d'un thread
            initialisation des modules Cadran et Combine
            enregistrement des fonctions de callback
        """
        print "[Automate __init__]"
        # creation de la queue de messages
        self.message_queue = Queue.Queue(maxsize=0)

        # demarre le thread de la class Automate
        self.worker = Thread(target=self.FonctionWorkerThread)
        self.worker.setDaemon(True)
        self.worker.start()

        self.cadran = Cadran()
        self.combine = Combine()

        # enregistre les fonctions de callback des modules Cadran et Combine
        self.cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)
        self.combine.RegisterCallback(
            NotificationDecroche=self.ReceptionDecroche,
            NotificationRaccroche=self.ReceptionRaccroche)

    def FonctionWorkerThread(self):
        """
        Fonction Worker Thread
        S'execute en parallele des autres taches
        Boucle infinie (tant que l'automate est actif)
            - Extrait un message de la queue de message
            - Traite le message
        On attend un message au plus TIMEOUT_AUTOMATE
        """
        print "[Automate FonctionWorkerThread start]"
        while self.automate_actif:
            #print "[Automate FonctionWorkerThread wait for a message]"
            try:
                message = self.message_queue.get(True,
                                                 Constantes.TIMEOUT_AUTOMATE)
                if message is not None:
                    self.TraiteMessage(message)
            except Queue.Empty:
                #print("Automate FonctionWorkerThread message_queue empty")
        print "[Automate Fonction_Worker_Thread] sortie de la boucle"

    def ArretAutomate(self):
        print "[Automate Exit]"
        self.cadran.ArretDetectionImpulsions()
        self.combine.ArretVerificationDecroche()
        self.automate_actif = False
        #sys.exit(0)

    def ReceptionChiffre(self, chiffre):
        print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)
        message = Message(message_type=Constantes.MESSAGE_CHIFFRE,
                          chiffre=chiffre)
        self.message_queue.put(message)

    def ReceptionDecroche(self):
        print ("[Automate ReceptionDecroche]")
        message = Message(message_type=Constantes.MESSAGE_DECROCHE, chiffre=0)
        self.message_queue.put(message)

    def ReceptionRaccroche(self):
        print ("[Automate ReceptionRaccroche]")
        message = Message(message_type=Constantes.MESSAGE_RACCROCHE, chiffre=0)
        self.message_queue.put(message)

    def ReceptionVerifDecroche(self, etat):
        print ("[Automate ReceptionVerifDecroche]", etat)

    def TraiteMessage(self, message):
        print ("[Automate TraiteMessage] message_type=",
               message.message_type)
