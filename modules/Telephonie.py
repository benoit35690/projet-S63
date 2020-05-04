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

        self.bus.add_signal_receiver(self.callAdded,
                                     bus_name="org.ofono",
                                     signal_name="CallAdded",
                                     path_keyword="path",
                                     interface_keyword="interface")
        self.bus.add_signal_receiver(self.propertyChanged,
                                     bus_name="org.ofono",
                                     signal_name="PropertyChanged",
                                     path_keyword="path",
                                     interface_keyword="interface")

        self.mainloop = GLib.MainLoop()
        self.mainloop.run()
        print "[Telephonie] __init__ fin procedure"

    def __del__(self):
        self.mainloop.quit()
        print "[Telephonie] __del__ fin procedure"

    def callAdded(message, details, path, interface):
        print "[Telephonie] callAdded new call ", message
        for key in details:
            val = details[key]
            print("    %s = %s" % (key, val))

        # call = dbus.Interface(self.bus.get_object('org.ofono', path),
        #                      'org.ofono.VoiceCall')

    def propertyChanged(message, details, path, interface):
        print "[Telephonie] propertyChanged ", message
        for key in details:
            val = details[key]
            print("    %s = %s" % (key, val))
