#!/usr/bin/env python3
"""Read one owned Java suite's metadata after verifying its installed JAR."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address')
parser.add_argument('--suite', type=int, help='Omit to locate the unique JAR matching the original size')
parser.add_argument('--jar', type=Path, required=True, help='Known local original for suite verification')
parser.add_argument('--channel', type=int, choices=range(1, 31), default=5)
args = parser.parse_args()
if (args.suite is not None and not 0 <= args.suite <= 999) or not args.jar.is_file():
    parser.error('Supply a suite ID 0..999 and its known local JAR')
expected = args.jar.read_bytes()
if len(expected) > 1048576:
    parser.error('Probe JAR must be at most 1 MiB')
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
client = dbus.Interface(bus.get_object('org.bluez.obex', '/org/bluez/obex'), 'org.bluez.obex.Client1')
session = None
folder = Path(__file__).resolve().parent.parent / 'logs/own-java-metadata'
folder.mkdir(exist_ok=True)
try:
    session = client.CreateSession(args.address, {'Target': dbus.String('ftp'),
                                   'Channel': dbus.Byte(args.channel)}, timeout=35)
    ftp = dbus.Interface(bus.get_object('org.bluez.obex', session), 'org.bluez.obex.FileTransfer1')
    ftp.ChangeFolder('System', timeout=30)
    ftp.ChangeFolder('Java', timeout=30)
    entries = {str(entry['Name']): entry for entry in ftp.ListFolder(timeout=30)}

    def get(name, limit):
        entry = entries[name]
        size = int(entry['Size'])
        if str(entry.get('Type')) != 'file' or not 0 <= size <= limit:
            raise ValueError('Invalid file type/size for ' + name)
        loop = GLib.MainLoop()
        state = {'path': None, 'status': None}

        def changed(interface, properties, invalidated, path):
            if path == state['path'] and interface == 'org.bluez.obex.Transfer1' and 'Status' in properties:
                state['status'] = str(properties['Status'])
                if state['status'] in ('complete', 'error'):
                    loop.quit()

        def expired():
            state['status'] = 'timeout'
            loop.quit()
            return False

        receiver = bus.add_signal_receiver(changed, signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties', bus_name='org.bluez.obex', path_keyword='path')
        timer = GLib.timeout_add_seconds(45, expired)
        target = folder / name
        try:
            state['path'], properties = ftp.GetFile(str(target), name, timeout=35)
            state['status'] = str(properties.get('Status', 'queued'))
            if state['status'] not in ('complete', 'error'):
                loop.run()
        finally:
            receiver.remove()
            if state['status'] != 'timeout':
                GLib.source_remove(timer)
        if state['status'] != 'complete':
            raise RuntimeError(name + ': readback ' + str(state['status']))
        target.chmod(0o600)
        data = target.read_bytes()
        if len(data) != size:
            raise ValueError(name + ': metadata size mismatch')
        return data

    if args.suite is None:
        candidates = [name[:-4] for name, entry in entries.items()
                      if re.fullmatch(r'[0-9]{1,3}\.jar', name)
                      and str(entry.get('Type')) == 'file'
                      and int(entry.get('Size', -1)) == len(expected)]
        if len(candidates) != 1:
            raise ValueError('Cannot identify a unique owned suite by size; supply --suite')
        prefix = candidates[0]
    else:
        prefix = str(args.suite)
    if get(prefix + '.jar', 1048576) != expected:
        raise ValueError('Installed JAR differs from known original; refusing metadata read')
    print('Installed JAR verified; owned suite=' + prefix, flush=True)
    summary = {}
    for extension in ('jdx', 'mss', 'raw'):
        name = prefix + '.' + extension
        data = get(name, 4096)
        strings = [match.decode('ascii') for match in re.findall(rb'[\x20-\x7e]{4,}', data)]
        summary[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'strings': strings}
        print(name + ': ' + str(len(data)) + ' bytes; ' + str(len(strings)) + ' printable strings', flush=True)
    target = folder / (prefix + '-summary.json')
    target.write_text(json.dumps(summary, indent=2) + '\n')
    target.chmod(0o600)
    current = folder / 'current.json'
    current.write_text(json.dumps({'suite': int(prefix), 'jar_sha256': hashlib.sha256(expected).hexdigest(),
                                  'gfs_url': 'gfs://java/' + prefix + '.jar'}) + '\n')
    current.chmod(0o600)
except Exception as error:
    print('Owned Java metadata failed:', str(error))
    raise SystemExit(1)
finally:
    if session is not None:
        client.RemoveSession(session)
