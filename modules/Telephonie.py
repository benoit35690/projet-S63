# -*- coding: utf-8 -*-
import Constantes
import dbus


class Telephonie:

    def __init__(self):
        print "[Telephonie] __init__"

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.ofono', '/'),
                                 'org.ofono.Manager')
        modems = manager.GetModems()
        mgr = None
        for path, properties in modems:
            print("[ %s ]" % (path))

            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue
            mgr = dbus.Interface(bus.get_object('org.ofono', path),
                                 'org.ofono.VoiceCallManager')

        if mgr is None:
            print "[Telephonie] __init__ no VoiceCallManager found "
            return

        mgr.connect_to_signal("CallAdded", self.callAdded)

    def callAdded(path, propertie):
        print "[Telephonie] callAdded new call ", path
        print("%s {%s}" % (path, propertie))
