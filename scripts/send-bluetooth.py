#!/usr/bin/env python3
"""Send files through the user's BlueZ OBEX service; phone must be paired."""
import argparse
from pathlib import Path
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address', help='Paired phone Bluetooth address')
parser.add_argument('files', nargs='+', type=Path)
args = parser.parse_args()
for file in args.files:
    if not file.is_file():
        parser.error('File missing: ' + str(file))
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
client = dbus.Interface(bus.get_object('org.bluez.obex', '/org/bluez/obex'), 'org.bluez.obex.Client1')
session = None
try:
    session = client.CreateSession(args.address, {'Target': dbus.String('opp')}, timeout=35)
    push = dbus.Interface(bus.get_object('org.bluez.obex', session), 'org.bluez.obex.ObjectPush1')
    for file in args.files:
        expected_size = file.stat().st_size
        loop = GLib.MainLoop()
        result = {'status': None}
        transfer = None

        def changed(interface, properties, invalidated, path):
            if path != transfer or interface != 'org.bluez.obex.Transfer1':
                return
            if 'Status' in properties:
                result['status'] = str(properties['Status'])
                print(file.name + ': OBEX ' + result['status'], flush=True)
                if result['status'] in ('complete', 'error'):
                    loop.quit()

        def expired():
            result['status'] = 'timeout'
            loop.quit()
            return False

        receiver = bus.add_signal_receiver(changed, signal_name='PropertiesChanged',
                                           dbus_interface='org.freedesktop.DBus.Properties',
                                           bus_name='org.bluez.obex', path_keyword='path')
        timer = GLib.timeout_add_seconds(120, expired)
        try:
            transfer, properties = push.SendFile(str(file.resolve()), timeout=35)
            print('Sending ' + file.name + ' (' + str(expected_size) + ' bytes)', flush=True)
            loop.run()
        finally:
            receiver.remove()
            if result['status'] != 'timeout':
                GLib.source_remove(timer)
        if result['status'] != 'complete':
            raise RuntimeError(file.name + ': ' + str(result['status']))
        print('RECEIVED FILE UNVERIFIED: check ' + file.name + ' on the phone is exactly '
              + str(expected_size) + ' bytes before installation or execution. '
              'OBEX completion does not verify the saved file.', flush=True)
except Exception as error:
    print('Bluetooth transfer failed: ' + str(error), file=sys.stderr)
    sys.exit(1)
finally:
    if session is not None:
        client.RemoveSession(session)
