#!/usr/bin/env python3
"""Verify transferred artifacts by reading their exact sizes and bytes back over OBEX FTP."""
import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
import time
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address', help='Paired phone Bluetooth address')
parser.add_argument('--folder', default='Bt', help='Phone folder path relative to OBEX root')
parser.add_argument('files', nargs='+', type=Path, help='Local originals to compare')
parser.add_argument('--channel', type=int, choices=range(1, 31), help='Known RFCOMM channel; bypass SDP discovery')
args = parser.parse_args()
for file in args.files:
    if not file.is_file():
        parser.error('Local original missing: ' + str(file))
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
client = dbus.Interface(bus.get_object('org.bluez.obex', '/org/bluez/obex'), 'org.bluez.obex.Client1')
session = None
try:
    options = {'Target': dbus.String('ftp')}
    if args.channel is not None:
        options['Channel'] = dbus.Byte(args.channel)
    for attempt in range(3):
        try:
            session = client.CreateSession(args.address, options, timeout=35)
            break
        except dbus.DBusException:
            if attempt == 2:
                raise
            time.sleep(2)
    ftp = dbus.Interface(bus.get_object('org.bluez.obex', session), 'org.bluez.obex.FileTransfer1')
    for folder in args.folder.split('/'):
        if folder:
            ftp.ChangeFolder(folder, timeout=30)
    entries = {str(entry['Name']): entry for entry in ftp.ListFolder(timeout=30)}
    with tempfile.TemporaryDirectory(prefix='mero-readback-') as directory:
        for file in args.files:
            entry = entries.get(file.name)
            expected = file.read_bytes()
            if entry is None or str(entry.get('Type')) != 'file':
                raise RuntimeError('Received file not found: ' + file.name)
            if 'Size' not in entry:
                raise RuntimeError('Phone did not report exact file size: ' + file.name)
            size = int(entry['Size'])
            if size != len(expected):
                raise RuntimeError(file.name + ': phone has ' + str(size) + ' bytes; expected ' + str(len(expected)))
            print(file.name + ': phone size matches, ' + str(size) + ' bytes', flush=True)
            target = Path(directory) / file.name
            loop = GLib.MainLoop()
            result = {'status': None}
            transfer = None

            def changed(interface, properties, invalidated, path):
                if path == transfer and interface == 'org.bluez.obex.Transfer1' and 'Status' in properties:
                    result['status'] = str(properties['Status'])
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
                transfer, properties = ftp.GetFile(str(target), file.name, timeout=35)
                loop.run()
            finally:
                receiver.remove()
                if result['status'] != 'timeout':
                    GLib.source_remove(timer)
            if result['status'] != 'complete':
                raise RuntimeError(file.name + ': readback ' + str(result['status']))
            actual = target.read_bytes()
            if len(actual) != len(expected) or actual != expected:
                raise RuntimeError(file.name + ': readback differs from original; do not install or execute')
            print(file.name + ': VERIFIED readback size and SHA-256 ' + hashlib.sha256(actual).hexdigest(), flush=True)
except Exception as error:
    print('Verification failed: ' + str(error), file=sys.stderr)
    sys.exit(1)
finally:
    if session is not None:
        client.RemoveSession(session)
