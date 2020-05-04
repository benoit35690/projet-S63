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


class Telephonie:
    bus = None
    vcm = None
    mainloop = None

    def __init__(self):
        print "[Telephonie] __init__"

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),
                                 'org.ofono.Manager')
        modems = manager.GetModems()
        modem = modems[0][0]
        print("[Telephonie] __init__ Using modem %s" % modem)

        self.vcm = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                  'org.ofono.VoiceCallManager')

        self.bus.add_signal_receiver(handler_function=self.callAdded,
                                     signal_name="CallAdded",
                                     dbus_interface=
                                     "org.ofono.VoiceCallManager",
                                     bus_name="org.ofono")
        self.bus.add_signal_receiver(handler_function=self.callRemoved,
                                     signal_name="CallRemoved",
                                     dbus_interface=
                                     "org.ofono.VoiceCallManager",
                                     bus_name="org.ofono")

        self.mainloop = GLib.MainLoop()
        self.mainloop.run()
        print "[Telephonie] __init__ fin procedure"

    def __del__(self):
        self.mainloop.quit()
        print "[Telephonie] __del__ fin procedure"

    def RegisterCallback(self,
                         NotificationAjoutAppelEntrant,
                         NotificationSuppressionAppel):
        """
            Enregistrement des callbacks utilisées pour notifier quand
                un nouvel appel entrant est reçu (il peut y en avoir plusieurs)
                un appel est supprimé (fin d'appel entrant ou sortant)
        """

        self.NotificationAjoutAppelEntrant = NotificationAjoutAppelEntrant
        self.NotificationSuppressionAppel = NotificationSuppressionAppel

    def callAdded(name, value, member):
        """notification envoyee par dbus sur ajout d'un appel
           (entrant ou sortant)
           actions realisees
              ajout du numero (LineIdentification) dans la liste des numero
              envoie d'une notification (a Automate)
        """
        print "[Telephonie] callAdded new call"
        print "value = ", value, "member = ", member

    def callRemoved(name, member):
        """notification envoyee par dbus sur suppression d'un appel
           (entrant ou sortant)
           actions realisees
              retrait du numero (LineIdentification) de la liste des numero
              envoie d'une notification (a Automate)
        """
        print "[Telephonie] callRemoved"
        print "member = ", member
