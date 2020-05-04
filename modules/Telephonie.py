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

    def pretty(d):
    	d = dbus2py(d)
    	t = type(d)

    	if t in (dict, tuple, list) and len(d) > 0:
    		if t is dict:
    			d = ", ".join(["%s = %s" % (k, pretty(v))
    					for k, v in d.items()])
    			return "{ %s }" % d

    		d = " ".join([pretty(e) for e in d])

    		if t is tuple:
    			return "( %s )" % d

    	if t is str:
    		return "%s" % d

    	return str(d)

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
                                bus_name="org.ofono",
                                path_keyword="path",
                                interface_keyword="interface")

        self.mainloop = GLib.MainLoop()
        self.mainloop.run()
        print "[Telephonie] __init__ fin procedure"

    def __del__(self):
        self.mainloop.quit()
        print "[Telephonie] __del__ fin procedure"

    def callAdded(name, value, member, path, interface):
        print "[Telephonie] callAdded new call"
        print "type name = ", type(name)
        print "type value = ", type(value)
        print "type member = ", type(member)
        print "type path = ", type(path)
        print "type interface = ", type(interface)

        print "name ="", str(name),
              "value = ", str(pretty(value)),
              "member = ", str(member)
