# -*- coding: utf-8 -*-
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

        # path = self.vcm.Dial("0645848223", "default")
        # print(path)

        self.bus.add_signal_receiver(handler_function=self.callAdded,
                                signal_name="CallAdded",
                                dbus_interface="org.ofono.VoiceCallManager",
                                bus_name="org.ofono")

        self.mainloop = GLib.MainLoop()
        self.mainloop.run()
        print "[Telephonie] __init__ fin procedure"

    def __del__(self):
        self.mainloop.quit()
        print "[Telephonie] __del__ fin procedure"

    def callAdded(path, properties):
        print "[Telephonie] callAdded new call ", path
