# -*- coding: utf-8 -*-
# module Telephonie
"""
    Module qui gère la couche telephonie oFono
"""
import Constantes
import dbus.mainloop.glib
from gi.repository import GLib
import dbus
import time
from threading import Thread


class Telephonie(Thread):
    appelEnCours = None
    appelEntrant = None
    bus = None
    # vcm = None
    mainloop = None

    def __init__(self):
        print "[Telephonie] __init__"
        Thread.__init__(self)

        try:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()
            # manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),
            #                         'org.ofono.Manager')
            # modems = manager.GetModems()
            # modem = modems[0][0]
            # print("[Telephonie] __init__ Using modem %s" % modem)

            # self.vcm = dbus.Interface(self.bus.get_object('org.ofono', modem),
            #                           'org.ofono.VoiceCallManager')
            # print("[Telephonie] __init__ vcm initialized ")

            self.bus.add_signal_receiver(handler_function=self.nouvelAppel,
                                         self=self,
                                         signal_name="CallAdded",
                                         dbus_interface=
                                         "org.ofono.VoiceCallManager",
                                         bus_name="org.ofono")
            print("[Telephonie] __init__  add_signal_receiver 1 OK")

            self.bus.add_signal_receiver(handler_function=self.appelSupprime,
                                         signal_name="CallRemoved",
                                         dbus_interface=
                                         "org.ofono.VoiceCallManager",
                                         bus_name="org.ofono")
            print("[Telephonie] __init__  add_signal_receiver 2 OK")

            self.appelEnCours = False
            print "[Telephonie] __init__ fin procedure"

        except Exception as inst:
            print "[Telephonie] __init__ Exception"
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasses
            x, y = inst.args     # unpack args
            print('x =', x)
            print('y =', y)

            raise inst
        finally:
            return

    def __del__(self):
        if self.mainloop is not None:
            self.mainloop.quit()
        print "[Telephonie] __del__ fin procedure"

    def run(self):
            self.mainloop = GLib.MainLoop()
            print("[Telephonie] run mainloop initialized")

            self.mainloop.run()
            print("[Telephonie] run  mainloop run OK")

    def registerCallback(self,
                         notificationAppelEntrant,
                         notificationFinAppel):
        """
            Enregistrement des callbacks utilisées pour notifier quand
                un nouvel appel entrant est reçu (il peut y en avoir plusieurs)
                un appel est supprimé (fin d'appel entrant ou sortant)
        """

        self.notificationAppelEntrant = notificationAppelEntrant
        self.notificationFinAppel = notificationFinAppel

    def refuserAppelEntrant(self):
        """ appelé par le client (Automate)
        """
        print "[Telephonie] refuserAppelEntrant"
        if self.appelEnCours is True:
            print "[Telephonie] accepterAppelEntrant appel deja en cours"
            return

        print "[Telephonie] accepterAppelEntrant"\
              "appel entrant =", self.appelEntrant
        calls = self.vcm.GetCalls()
        for path, properties in calls:
            state = properties["State"]
            print("[ %s ] %s" % (path, state))
            if state != "incoming":
                continue
            call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                  'org.ofono.VoiceCall')
            call.Hangup()
            print("appel entrant [ %s ] rejeté" % path)

    def accepterAppelEntrant(self):
        """ appelé par le client (Automate)
        """
        print "[Telephonie] accepterAppelEntrant"
        if self.appelEnCours is True:
            print "[Telephonie] accepterAppelEntrant appel deja en cours"
            return

        print "[Telephonie] accepterAppelEntrant"\
              "appel entrant =", self.appelEntrant
        calls = self.vcm.GetCalls()
        for path, properties in calls:
            state = properties["State"]
            print("[ %s ] %s" % (path, state))
            if state != "incoming":
                continue
            call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                  'org.ofono.VoiceCall')
            call.Answer()
            print("appel entrant [ %s ] rejeté" % path)
            self.appelEnCours = True
            return

    def numeroterAppelSortant(self, number):
        """ appelé par le client (Automate)
        """
        # print "[Telephonie] numeroterAppelSortant"
        path = self.vcm.Dial(number, "default")
        print("appel sortant [ %s ] rejeté" % path)
        self.appelEnCours = path

    def terminerAppel(self):
        """ appelé par le client (Automate) pour terminer un appel
        """
        print "[Telephonie] terminerAppel"

        manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),
                                 'org.ofono.Manager')
        modems = manager.GetModems()
        modem = modems[0][0]
        print("[Telephonie] terminerAppel Using modem %s" % modem)

        manager = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                 'org.ofono.VoiceCallManager')
        print("[Telephonie] terminerAppel manager initialized ")

        manager.HangupAll()

    def nouvelAppel(self, signal_name, dbus_interface, bus_name):
    # def nouvelAppel(signal_name, dbus_interface, bus_name):
        """notification envoyee par dbus sur ajout d'un appel
           (entrant ou sortant)
           actions realisees
              sauvegarder le numero (LineIdentification)
              si un appel est déjà en cours alors rejeter l'appel
              sinon envoier d'une notification (a Automate)
        """
        print "[Telephonie] nouvelAppel bus_name= {%s}" % bus_name
        print "[Telephonie] nouvelAppel signal_name= [%s]" % signal_name

        # self.notificationAppelEntrant()

    def appelSupprime(self, signal_name, dbus_interface, bus_name):
        """notification envoyee par dbus sur suppression d'un appel
           (entrant ou sortant)
           actions realisees
              retrait du numero (LineIdentification) de la liste des numero
              envoie d'une notification (a Automate)
        """
        print "[Telephonie] appelSupprime"
#        print("appel en cours [ %s ] terminé" % self.appelEntrant)
        self.notificationFinAppel()
