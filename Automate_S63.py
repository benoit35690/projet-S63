# -*- coding: utf-8 -*-
# import os
import Queue
from threading import Thread, Timer
import signal
import sys
import RPi.GPIO as GPIO
import Constantes
# from threading import Timer
from modules.Cadran import Cadran
from modules.Combine import Combine
from modules.Tonalite import Tonalite
from modules.Telephonie import Telephonie

callback_queue = Queue.Queue()


class Message:
    transition_automate = 0
    chiffre_compose     = 0
    numero_compose      = 0


class Automate_S63:
    dial_number = ""
    numeroCompose = ""
    automate_actif = True
    timerInialisation = None
    timerDecrocheRepos = None
    etat_automate = Constantes.ETAT_INIT
    etatCombine = Constantes.COMBINE_INITIALISATION
    offHook = False
    offHookTimeoutTimer = None
    worker = None
    cadran = None
    combine = None
    tonalite = None
    telephonie = None

    def __init__(self):
        print ("[Automate_S63 __init__]")

        signal.signal(signal.SIGINT, self.OnSignal)

        self.tonalite = Tonalite()

        self.etat_automate = Constantes.ETAT_INIT

        # creation de la queue de messages
        self.message_queue = Queue.Queue(maxsize=0)

        # demarre le thread de la class Automate
        self.worker = Thread(target=self.FonctionWorkerThread)
        self.worker.setDaemon(True)
        self.worker.start()

        # arme le timer d'initialisation
        self.timerInialisation = Timer(Constantes.TIMEOUT_INITIALISATION,
                                        self.ReceptionNotificationTimer,
                                        [Constantes.TIMER_INITIALISATION])
        self.timerInialisation.start()

        # initialisation du module Cadran
        self.cadran = Cadran()
        self.cadran.RegisterCallback(NotificationChiffre=self.ReceptionChiffre)

        # initialisation du module Combine
        self.combine = Combine()
        self.combine.RegisterCallback(
                    NotificationDecroche=self.ReceptionDecroche,
                    NotificationRaccroche=self.ReceptionRaccroche,
                    NotificationVerifDecroche=self.ReceptionVerifDecroche)

        self.timerDecrocheRepos = None

        # initialisation du module Telephonie
#        try:
        self.telephonie = Telephonie()
        print ("[Automate_S63 __init__] Telephonie initialized")
        self.telephonie.registerCallback(
                    notificationAppelEntrant=self.receptionAppelEntrant,
                    notificationFinAppel=self.receptionFinAppel)
        print ("[Automate_S63 __init__] Telephonie registerCallback OK")

        # demarrage du Thread du module Telephonie
        self.telephonie.start()
        print ("[Automate_S63 __init__] Telephonie start OK")

        raw_input("Waiting.\n")

    # fonctions permettant de recevoir les notifications des autres modules
    # ---------------------------------------------------------------------

    def ReceptionChiffre(self, chiffre):
        """ Notification envoyée par le module Cadran
            Contient le chiffre composé sur le cadrant rotatif
        """
        # print ("[Automate ReceptionChiffre] Chiffre recu = ", chiffre)
        message = Message()
        message.transition_automate = Constantes.TRANSITION_CHIFFRE_COMP
        message.chiffre_compose = str(chiffre)
        self.message_queue.put(message)

    def ReceptionDecroche(self):
        """ Notification envoyée par le module Combine
            A chaque fois que le combiné est décroché
            Tant que l'automate est en cours d'initialisation l'événement est
            ignoré
        """
        print ("[Automate ReceptionDecroche]")
        if self.etat_automate != Constantes.ETAT_INIT:
            message = Message()
            message.transition_automate = Constantes.TRANSITION_DECROCHE
            self.message_queue.put(message)
        else:
            self.etatCombine = Constantes.COMBINE_DECROCHE

    def ReceptionRaccroche(self):
        """ Notification envoyée par le module Combine
            A chaque fois que le combiné est raccroché
            Tant que l'automate est en cours d'initialisation l'événement est
            ignoré
        """
        print ("[Automate ReceptionRaccroche]")
        if self.etat_automate != Constantes.ETAT_INIT:
            message = Message()
            message.transition_automate = Constantes.TRANSITION_RACCROCHE
            self.message_queue.put(message)
        else:
            self.etatCombine = Constantes.COMBINE_RACCROCHE

    def ReceptionVerifDecroche(self, etat):
        """ Notification envoyée par le module Combine
            Périodiquement pour vérifier l'état du combiné
            Tant que l'automate est en cours d'initialisation l'événement est
            ignoré
        """
        # print ("[Automate ReceptionVerifDecroche]", etat)

        message = Message()
        if etat == GPIO.HIGH:
            # print("[Combine VerifieCombine] HIGH -> Raccroche")
            message.transition_automate = Constantes.TRANSITION_RACCROCHE
            self.etatCombine = Constantes.COMBINE_RACCROCHE
        else:
            # print("[Combine VerifieCombine] LOW -> Decroche")
            message.transition_automate = Constantes.TRANSITION_DECROCHE
            self.etatCombine = Constantes.COMBINE_DECROCHE

        if self.etat_automate != Constantes.ETAT_INIT:
            self.message_queue.put(message)

    def ReceptionNotificationTimer(self, *timer):
        """ Notification envoyée par la fonction Timer
            A chaque échéance de timer
        """
        print ("[Automate ReceptionNotificationTimer] timer= ", timer[0])
        message = Message()
        if timer[0] == Constantes.TIMER_INITIALISATION:
            if self.etatCombine == Constantes.COMBINE_DECROCHE:
                message.transition_automate = Constantes.TRANSITION_DECROCHE
            elif self.etatCombine == Constantes.COMBINE_RACCROCHE:
                message.transition_automate = Constantes.TRANSITION_RACCROCHE
            else:
                message.transition_automate = Constantes.TRANSITION_INIT
            self.message_queue.put(message)
        elif timer[0] == Constantes.TIMER_DECROCHER_REPOS:
            message.transition_automate = Constantes.TRANSITION_TIMER_OUBLIE
            self.message_queue.put(message)
        elif timer[0] == Constantes.TIMER_TONAL_ACHEMINEMENT:
            message.transition_automate = Constantes.TRANSITION_APPEL_SORTANT
            self.message_queue.put(message)

    def receptionAppelEntrant(self):
        """ Notification envoyée par le module Telephonie
            A chaque appel entrant
            Si une communication est établie, le module Telephonie rejete
                un autre appel entrant
        """
        print ("[Automate receptionAppelEntrant]")
        message = Message()
        message.transition_automate = Constantes.TRANSITION_APPEL_ENTRANT
        self.message_queue.put(message)
        return

    def receptionFinAppel(self):
        """ Notification envoyée par le module Telephonie
            A chaque appel terminé
            - appel entrant (communication pas encore acceptée)
            - appel en cours initié par le correspondant (appel entrant)
            - appel sortant  communication pas encore acceptée par le
              correspondant)
            - appel en cours (appel sortant)
        """
        print ("[Automate receptionFinAppel]")
        message = Message()
        message.transition_automate = Constantes.TRANSITION_FIN_APPEL
        self.message_queue.put(message)
        return

    # Focntion principale du thread
    # -----------------------------

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
            # print "[Automate FonctionWorkerThread wait for a message]"
            try:
                message = self.message_queue.get(True,
                                                 Constantes.TIMEOUT_AUTOMATE)
                if message is not None:
                    self.TraiteMessage(message)
            except Queue.Empty:
                # print("Automate FonctionWorkerThread message_queue empty")
                continue
        print "[Automate Fonction_Worker_Thread] sortie de la boucle"

    # Fonctions de traitement des messages de l'automate
    # une fonction par transition
    # --------------------------------------------------

    def TraiteMessage(self, message):
        # print ("[Automate TraiteMessage] transition=",
        #       message.transition_automate)
        if message.transition_automate == Constantes.TRANSITION_INIT:
            self.TraiteTransitionInitialisation(message)
        elif message.transition_automate == Constantes.TRANSITION_RACCROCHE:
            self.TraiteTransitionRaccroche(message)
        elif message.transition_automate == Constantes.TRANSITION_DECROCHE:
            self.TraiteTransitionDecroche(message)
        elif message.transition_automate == Constantes.TRANSITION_APPEL_ENTRANT:
            self.TraiteTransitionAppelEntrant(message)
        elif message.transition_automate == Constantes.TRANSITION_FIN_APPEL:
            self.TraiteTransitionFinAppel(message)
        elif message.transition_automate == Constantes.TRANSITION_TIMER_OUBLIE:
            self.TraiteTransitionTimerOublie(message)
        elif message.transition_automate == Constantes.TRANSITION_ECHEC_NUM:
            self.TraiteTransitionEchecNumerotation(message)
        elif message.transition_automate == Constantes.TRANSITION_CHIFFRE_COMP:
            self.TraiteTransitionChiffreCompose(message)
        elif message.transition_automate == Constantes.TRANSITION_NUMERO_VALIDE:
            self.TraiteTransitionNumeroValide(message)
        elif message.transition_automate == Constantes.TRANSITION_TIMER_SORTANT:
            self.TraiteTransitionTimerSortant(message)
        elif message.transition_automate == Constantes.TRANSITION_TIMER_NUMEROT:
            self.TraiteTransitionTimerNumerotation(message)
        elif message.transition_automate == Constantes.TRANSITION_FIN_TON_ECHEC:
            self.TraiteTransitionFinTonaliteEchec(message)
        elif message.transition_automate == Constantes.TRANSITION_TIMER_CONNEX:
            self.TraiteTransitionTimerConnection(message)
        elif message.transition_automate == Constantes.TRANSITION_APPEL_SORTANT:
            self.TraiteTransitionAppelSortant()
        else:
            print ("[Automate TraiteMessage] MESSAGE INCONNU transition=",
                   message.transition_automate)

    def TraiteTransitionInitialisation(self, message):
        print ("[Automate TraiteTransitionInitialisation] etat_automate=",
               self.etat_automate)

        # rearme le timer d'initialisation
        self.timerInialisation = Timer(Constantes.TIMEOUT_INITIALISATION,
                                        self.ReceptionNotificationTimer,
                                        [Constantes.TIMER_INITIALISATION])
        self.timerInialisation.start()

    def TraiteTransitionRaccroche(self, message):
        # print ("[Automate TraiteTransitionRaccroche] etat_automate=",
        #        self.etat_automate)
        if self.etat_automate == Constantes.ETAT_REPOS:
            return

        if self.etat_automate == Constantes.ETAT_INIT or \
           self.etat_automate == Constantes.ETAT_DECROCHE_REPOS or \
           self.etat_automate == Constantes.ETAT_DECROCHE_OUBLIE or \
           self.etat_automate == Constantes.ETAT_SONNERIE or \
           self.etat_automate == Constantes.ETAT_NUMEROTATION or \
           self.etat_automate == Constantes.ETAT_APPEL_ENTRANT or \
           self.etat_automate == Constantes.ETAT_TONALITE_SORTANT or \
           self.etat_automate == Constantes.ETAT_INIT_APPEL_SORTANT or \
           self.etat_automate == Constantes.ETAT_ECHEC_APPEL_SORTANT or \
           self.etat_automate == Constantes.ETAT_APPEL_SORTANT:
            self.ChangerEtat_Repos()
        else:
            print ("[Automate TraiteTransitionRaccroche] ERREUR TRANSITION"
                   "etat= ", self.etat_automate)

    def TraiteTransitionDecroche(self, message):
        print ("[Automate TraiteTransitionDecroche] transition=",
               self.etat_automate)

        if self.etat_automate == Constantes.ETAT_DECROCHE_REPOS or \
           self.etat_automate == Constantes.ETAT_DECROCHE_OUBLIE or \
           self.etat_automate == Constantes.ETAT_NUMEROTATION or \
           self.etat_automate == Constantes.ETAT_APPEL_ENTRANT or \
           self.etat_automate == Constantes.ETAT_TONALITE_SORTANT or \
           self.etat_automate == Constantes.ETAT_INIT_APPEL_SORTANT or \
           self.etat_automate == Constantes.ETAT_ECHEC_APPEL_SORTANT or \
           self.etat_automate == Constantes.ETAT_APPEL_SORTANT:
            return

        if self.etat_automate == Constantes.ETAT_INIT or \
           self.etat_automate == Constantes.ETAT_REPOS:
            self.ChangerEtat_DecrocheRepos()
        elif self.etat_automate == Constantes.ETAT_SONNERIE:
            self.ChangerEtat_AppelEntrant()
        else:
            print ("[Automate TraiteTransitionDecroche] ERREUR TRANSITION"
                   "etat= ", self.etat_automate)

    def TraiteTransitionAppelEntrant(self, message):
        print ("[Automate TraiteTransitionAppelEntrant] transition=",
               self.etat_automate)
        if self.etat_automate == Constantes.ETAT_REPOS:
            self.ChangerEtat_Sonnerie()
        else:
            print ("[Automate TraiteTransitionAppelEntrant] Rejet de l'appel "
                   "etat= ", self.etat_automate)
            self.telephonie.refuserAppelEntrant()

    def TraiteTransitionFinAppel(self, message):
        print ("[Automate TraiteTransitionFinAppel] transition=",
               self.etat_automate)
        if self.etat_automate == Constantes.ETAT_SONNERIE:
            self.ChangerEtat_Repos()
        elif self.etat_automate == Constantes.ETAT_APPEL_ENTRANT or \
                self.etat_automate == Constantes.ETAT_APPEL_SORTANT:
            self.ChangerEtat_DecrocheRepos()
        else:
            print ("[Automate TraiteTransitionFinAppel] ERREUR TRANSITION"
                   "etat= ", self.etat_automate)

    def TraiteTransitionTimerOublie(self, message):
        print ("[Automate TraiteTransitionTimerOublie] transition=",
               self.etat_automate)
        if self.etat_automate == Constantes.ETAT_DECROCHE_REPOS:
            self.ChangerEtat_DecrocheOublie()
        else:
            print ("[Automate TraiteTransitionTimerOublie] ERREUR TRANSITION"
                   "etat= ", self.etat_automate)

    def TraiteTransitionEchecNumerotation(self, message):
        print ("[Automate TraiteTransitionEchecNumerotation] transition=",
               self.etat_automate)
        if self.etat_automate == Constantes.ETAT_INIT_APPEL_SORTANT:
            self.ChangerEtat_EchecAppelSortant()
        else:
            print ("[Automate TraiteTransitionEchecNumerotation] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionChiffreCompose(self, message):
        print ("[Automate TraiteTransitionChiffreCompose] transition=",
               self.etat_automate)
        if self.etat_automate == Constantes.ETAT_DECROCHE_REPOS or \
           self.etat_automate == Constantes.ETAT_NUMEROTATION:
            self.ChangerEtat_Numerotation(message.chiffre_compose)
        else:
            print ("[Automate TraiteTransitionChiffreCompose] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionNumeroValide(self, message):
        print ("[Automate TraiteTransitionNumeroValide] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_NUMEROTATION:
            self.ChangerEtat_TonaliteSortante()
        else:
            print ("[Automate TraiteTransitionNumeroValide] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionTimerSortant(self, message):
        print ("[Automate TraiteTransitionTimerSortant] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_TONALITE_SORTANT:
            self.ChangerEtat_InitialisationAppelSortant()
        else:
            print ("[Automate TraiteTransitionTimerSortant] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionTimerNumerotation(self, message):
        print ("[Automate TraiteTransitionTimerNumerotation] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_NUMEROTATION:
            self.ChangerEtat_DecrocheOublie()
        else:
            print ("[Automate TraiteTransitionTimerNumerotation] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionFinTonaliteEchec(self, message):
        print ("[Automate TraiteTransitionFinTonaliteEchec] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_ECHEC_APPEL_SORTANT:
            self.ChangerEtat_DecrocheRepos()
        else:
            print ("[Automate TraiteTransitionFinTonaliteEchec] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionTimerConnection(self, message):
        print ("[Automate TraiteTransitionTimerConnection] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_INIT_APPEL_SORTANT:
            self.ChangerEtat_EchecAppelSortant()
        else:
            print ("[Automate TraiteTransitionTimerConnection] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    def TraiteTransitionAppelSortant(self, message):
        print ("[Automate TraiteTransitionAppelSortant] transition=",
               message.transition_automate)
        if self.etat_automate == Constantes.ETAT_INIT_APPEL_SORTANT:
            self.ChangerEtat_AppelSortant()
        else:
            print ("[Automate TraiteTransitionAppelSortant] ERREUR"
                   " TRANSITION etat= ", self.etat_automate)

    # Fonctions de changement d'état de l'automate
    # appelées par les fonctions de transition
    # --------------------------------------------

    def ChangerEtat_Repos(self):
        """
            Transition vers l'état ETAT_REPOS
            Liste des actions à faire si besoin
                terminer appel en cours (sortant ou entrant)
                terminer lecture tonalité
                reinitialisé numero composé
                annuler timer décrocher repos
        """
        print ("[Automate ChangerEtat_Repos] etat origine=",
               self.etat_automate)

        # termine un éventuel appel (en cours)
        self.telephonie.terminerAppel()

        self.numeroCompose = ""
        self.tonalite.stopLecture()
        if self.timerDecrocheRepos is not None:
            self.timerDecrocheRepos.cancel()
        self.etat_automate = Constantes.ETAT_REPOS

    def ChangerEtat_DecrocheRepos(self):
        """
            Transition vers l'état ETAT_DECROCHE_REPOS
            Liste des actions à faire si besoin
                appel terminé à l'initiative du corespondant -> terminer
                lecture tonalité TONALITE_INVITATION
                armer timer d'oublie
        """
        print ("[Automate ChangerEtat_DecrocheRepos] etat origine=",
               self.etat_automate)

        self.tonalite.stopLecture()
        self.tonalite.startLecture(Constantes.TONALITE_INVITATION, True)
        self.etat_automate = Constantes.ETAT_DECROCHE_REPOS
        self.timerDecrocheRepos = Timer(Constantes.TIMEOUT_DECROCHE_REPOS,
                                        self.ReceptionNotificationTimer,
                                        [Constantes.TIMER_DECROCHER_REPOS])
        self.timerDecrocheRepos.start()
        self.etat_automate = Constantes.ETAT_DECROCHE_REPOS

    def ChangerEtat_DecrocheOublie(self):
        """
            Transition vers l'état ETAT_DECROCHE_OUBLIE
            Liste des actions à faire si besoin
                terminer lecture tonalité décroché
                lecture tonalité TONALITE_OCCUPATION
                reinitialisé numero composé
        """
        print ("[Automate ChangerEtat_DecrocheOublie] etat origine=",
               self.etat_automate)
        self.tonalite.stopLecture()
        self.tonalite.startLecture(Constantes.TONALITE_OCCUPATION, True)
        self.etat_automate = Constantes.ETAT_DECROCHE_OUBLIE

    def ChangerEtat_Sonnerie(self):
        """
            Transition vers l'état ETAT_SONNERIE
            Liste des actions à faire si besoin
                demarrer sonnerie
        """
        print ("[Automate ChangerEtat_Sonnerie] etat origine=",
               self.etat_automate)
        # TO DO coder sonnerie
        self.etat_automate = Constantes.ETAT_SONNERIE

    def ChangerEtat_AppelEntrant(self):
        """
            Transition vers l'état ETAT_APPEL_ENTRANT
            Liste des actions à faire si besoin
                terminer sonnerie
                activer communication micro + haut parleur
                accepter l'appel entrant
        """
        print ("[Automate ChangerEtat_AppelEntrant] etat origine=",
               self.etat_automate)

        # TO DO arret sonnerie
        self.telephonie.accepterAppelEntrant()
        self.etat_automate = Constantes.ETAT_APPEL_ENTRANT

    def ChangerEtat_Numerotation(self, chiffreCompose):
        """
            Transition vers l'état ETAT_NUMEROTATION
            Liste des actions à faire si besoin
                arret lecture tonalité
                annuler timer décroché repos
                calculer numero composé
                identifier numéro valide
                appeler transition vers Appel1
        """
        print ("[Automate ChangerEtat_Numerotation] etat origine=",
               self.etat_automate)

        self.tonalite.stopLecture()
        if self.timerDecrocheRepos is not None:
            self.timerDecrocheRepos.cancel()
        self.numeroCompose = self.numeroCompose + chiffreCompose
        print "chiffreCompose = ", chiffreCompose,\
              " numeroCompose = ", self.numeroCompose

        self.etat_automate = Constantes.ETAT_NUMEROTATION
        self.verifieNumeroComposeValide()

    def ChangerEtat_TonaliteSortante(self):
        """
            Transition vers l'état ETAT_TONALITE_SORTANT
            Liste des actions à faire si besoin
                lecture tonalité mise en relation
                armer timer
        """
        print ("[Automate ChangerEtat_TonaliteSortante] etat origine=",
               self.etat_automate)
        self.tonalite.startLecture(Constantes.TONALITE_ACHEMINEMENT, False)
        self.timerTonaliteAcheminement = \
            Timer(3,
                  self.ReceptionNotificationTimer,
                  [Constantes.TIMER_TONAL_ACHEMINEMENT])
        self.timerTonaliteAcheminement.start()
        self.etat_automate = Constantes.ETAT_TONALITE_SORTANT

    def ChangerEtat_InitialisationAppelSortant(self):
        """
            Transition vers l'état ETAT_INIT_APPEL_SORTANT
            Liste des actions à faire si besoin
                etablissement connexion appel sortant
        """
        print ("[Automate ChangerEtat_InitialisationAppelSortant] etat"
               " origine=", self.etat_automate)
        self.etat_automate = Constantes.ETAT_INIT_APPEL_SORTANT

    def ChangerEtat_EchecAppelSortant(self):
        """
            Transition vers l'état ETAT_ECHEC_APPEL_SORTANT
            Liste des actions à faire si besoin
                terminer lecture tonalite etablissement connexion
                reinitialiser numero composé
                lecture tonalié erreur connexion
                armer timer
        """
        print ("[Automate ChangerEtat_EchecAppelSortant] etat"
               " origine=", self.etat_automate)
        self.etat_automate = Constantes.ETAT_ECHEC_APPEL_SORTANT

    def ChangerEtat_AppelSortant(self):
        """
            Transition vers l'état ETAT_APPEL_SORTANT
            Liste des actions à faire si besoin
                terminer lecture tonalite etablissement connexion
        """
        print ("[Automate ChangerEtat_AppelSortant] etat"
               " origine=", self.etat_automate)
        self.etat_automate = Constantes.ETAT_APPEL_SORTANT

    # Focntions diverses
    # ------------------

    def verifieNumeroComposeValide(self):
        """
            pour l'instant compare le numeroCompose avec un numero Fixe
            par la suite
            reperer un prefixe connue (mobile, pompier...)
        """

        print "[Automate] verifieNumeroComposeValide numeroCompose = ", \
              self.numeroCompose
        if self.numeroCompose == "01":
            message = Message()
            message.transition_automate = Constantes.TRANSITION_NUMERO_VALIDE
            self.message_queue.put(message)

    # Focntions appelée sur fin d'execution
    # -------------------------------------

    def OnSignal(self, signal, frame):
        """ Appelée sur reception du signal de fin d'éxécution
            CTRL + C
            Termine proprement l'execution des modules
        """
        print "[SIGNAL] Shutting down on %s" % signal
        self.combine.ArretVerificationDecroche()
        del self.tonalite
        del self.telephonie
        self.automate_actif = False
        sys.exit(0)

def main():
    print "[main]"
    TDaemon = Automate_S63()


if __name__ == "__main__":
    main()
