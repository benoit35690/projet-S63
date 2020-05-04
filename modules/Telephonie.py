# -*- coding: utf-8 -*-
import Constantes
import dbus.mainloop.glib
import dbus
import time


class Telephonie:
    bus = None
    vcm = None

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

        self.vcm.connect_to_signal("CallAdded", self.callAdded)
        self.vcm.connect_to_signal("PropertyChanged", self.propertyChanged)
        time.sleep(10)

    def callAdded(path, propertie):
        print "[Telephonie] callAdded new call ", path
        print("%s {%s}" % (path, propertie))

        # call = dbus.Interface(self.bus.get_object('org.ofono', path),
        #                      'org.ofono.VoiceCall')

    def propertyChanged(propertie, value):
        print "[Telephonie] propertyChanged propertie= ", propertie
