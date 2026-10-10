#!/usr/bin/env python3
"""Advertise a native SPP server for the paired phone's Java comm connection."""
import argparse
import json
from pathlib import Path
import socket
import threading

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address', help='Only accept this paired phone')
parser.add_argument('--channel', type=int, choices=range(1, 31), default=22)
parser.add_argument('--duration', type=int, default=600)
args = parser.parse_args()
if not 5 <= args.duration <= 3600:
    parser.error('--duration must be 5..3600 seconds')
parts = args.address.split(':')
if len(parts) != 6 or any(len(p) != 2 or any(c not in '0123456789abcdefABCDEF' for c in p) for p in parts):
    parser.error('Use a Bluetooth address with six hexadecimal octets')
suffix = '/dev_' + args.address.upper().replace(':', '_')
DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
loop = GLib.MainLoop()
target = Path(__file__).resolve().parent.parent / 'logs/java-serial-server.json'
target.parent.mkdir(exist_ok=True)
state = {'connected': False, 'events': []}
lock = threading.Lock()
connections = []

def save():
    with lock:
        target.write_text(json.dumps(state, indent=2) + '\n')
        target.chmod(0o600)

def serve(connection):
    replies = {b'AT': b'OK', b'ATI': b'MERO HOST BRIDGE', b'AT+CGMI': b'Mero',
               b'AT+CGMM': b'Computer bridge', b'AT+CGMR': b'mero-bridge/1'}
    connection.settimeout(1)
    pending = bytearray()
    received = 0
    try:
        while received < 8192:
            try:
                chunk = connection.recv(min(4096, 8192 - received))
            except TimeoutError:
                continue
            if not chunk:
                break
            received += len(chunk)
            pending.extend(chunk)
            while b'\r' in pending:
                line, remainder = bytes(pending).split(b'\r', 1)
                pending = bytearray(remainder)
                line = line.strip(b'\n')
                reply = replies.get(line)
                event = {'received_hex': line.hex(), 'sent_hex': ''}
                if reply is not None:
                    message = b'\r\n' + reply + b'\r\n'
                    connection.sendall(message)
                    event['sent_hex'] = message.hex()
                    print('Java query received and answered: ' + line.decode('ascii'), flush=True)
                state['events'].append(event)
                save()
    except OSError as error:
        state['last_error'] = str(error)
    finally:
        state['received_bytes'] = received
        state['pending_hex'] = pending.hex()
        save()
        connection.close()

class Profile(dbus.service.Object):
    @dbus.service.method('org.bluez.Profile1', in_signature='', out_signature='')
    def Release(self):
        loop.quit()

    @dbus.service.method('org.bluez.Profile1', in_signature='oha{sv}', out_signature='')
    def NewConnection(self, device, fd, properties):
        connection = socket.socket(fileno=fd.take())
        if not str(device).endswith(suffix):
            connection.close()
            raise dbus.exceptions.DBusException('Unexpected peer', name='org.bluez.Error.Rejected')
        connections.append(connection)
        state['connected'] = True
        save()
        print('Paired phone connected to the computer serial server', flush=True)
        threading.Thread(target=serve, args=(connection,), daemon=True).start()

    @dbus.service.method('org.bluez.Profile1', in_signature='o', out_signature='')
    def RequestDisconnection(self, device):
        for connection in connections:
            connection.close()

objects = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager').GetManagedObjects()
adapter_path = next((path for path in objects if str(path).endswith(suffix)), None)
if adapter_path is None:
    parser.error('Paired phone is not present in BlueZ')
adapter_path = str(adapter_path).rsplit('/dev_', 1)[0]
properties = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.freedesktop.DBus.Properties')
original = {key: properties.Get('org.bluez.Adapter1', key) for key in ('Discoverable', 'DiscoverableTimeout')}
manager = dbus.Interface(bus.get_object('org.bluez', '/org/bluez'), 'org.bluez.ProfileManager1')
path = '/org/mero/JavaSerial'
profile = Profile(bus, path)
record = '''<record>
<attribute id="0x0001"><sequence><uuid value="0x1101"/></sequence></attribute>
<attribute id="0x0004"><sequence>
<sequence><uuid value="0x0100"/></sequence>
<sequence><uuid value="0x0003"/><uint8 value="%d"/></sequence>
</sequence></attribute>
<attribute id="0x0005"><sequence><uuid value="0x1002"/></sequence></attribute>
<attribute id="0x0009"><sequence><sequence><uuid value="0x1101"/><uint16 value="0x0100"/></sequence></sequence></attribute>
<attribute id="0x0100"><text value="Mero Java Serial"/></attribute>
</record>''' % args.channel
registered = False
try:
    manager.RegisterProfile(path, '00001101-0000-1000-8000-00805f9b34fb', {
        'Name': 'Mero Java Serial', 'Role': 'server', 'Channel': dbus.UInt16(args.channel),
        'RequireAuthentication': dbus.Boolean(True), 'RequireAuthorization': dbus.Boolean(False),
        'ServiceRecord': record})
    registered = True
    uuids = [str(value).lower() for value in properties.Get('org.bluez.Adapter1', 'UUIDs')]
    if '00001101-0000-1000-8000-00805f9b34fb' not in uuids:
        raise RuntimeError('Serial service was not advertised; inspect Bluetooth logs for a channel bind failure')
    properties.Set('org.bluez.Adapter1', 'DiscoverableTimeout', dbus.UInt32(args.duration))
    properties.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(True))
    save()
    print('Computer SPP server ready; awaiting the paired phone on channel ' + str(args.channel), flush=True)
    GLib.timeout_add_seconds(args.duration, lambda: (loop.quit(), False)[1])
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    if registered:
        manager.UnregisterProfile(path)
    for connection in connections:
        connection.close()
    for key, value in original.items():
        properties.Set('org.bluez.Adapter1', key, value)
