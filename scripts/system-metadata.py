#!/usr/bin/env python3
"""Inspect only the phone's exposed System-folder metadata through OBEX FTP."""
import argparse
import json
from pathlib import Path
import time
import dbus

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address', help='Paired phone address')
parser.add_argument('--folder', choices=('System', 'System/Java'), default='System')
parser.add_argument('--channel', type=int, choices=range(1, 31), default=5)
args = parser.parse_args()
bus = dbus.SessionBus()
client = dbus.Interface(bus.get_object('org.bluez.obex', '/org/bluez/obex'), 'org.bluez.obex.Client1')
session = None
try:
    for attempt in range(3):
        try:
            session = client.CreateSession(args.address, {'Target': dbus.String('ftp'),
                                           'Channel': dbus.Byte(args.channel)}, timeout=35)
            break
        except dbus.DBusException:
            if attempt == 2:
                raise
            time.sleep(2)
    ftp = dbus.Interface(bus.get_object('org.bluez.obex', session), 'org.bluez.obex.FileTransfer1')
    for folder in args.folder.split('/'):
        ftp.ChangeFolder(folder, timeout=30)
    entries = [{str(k): str(v) for k, v in entry.items() if str(k) in ('Name', 'Type', 'Size')}
               for entry in ftp.ListFolder(timeout=30)]
    target = Path(__file__).resolve().parent.parent / ('logs/' + args.folder.lower().replace('/', '-') + '-metadata.json')
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({'folder': args.folder, 'entries': entries}, indent=2) + '\n')
    target.chmod(0o600)
    print(args.folder + ' folder:', len(entries), 'entries; metadata saved privately; no file contents read')
    markers = ('java', 'jblend', 'jbed', 'mre', 'vxp', 'mocor', 'nucleus', 'sprd', 'firmware', 'boot', 'fdl')
    clues = [entry for entry in entries if any(marker in entry.get('Name', '').lower() for marker in markers)]
    print('Runtime/firmware filename clues:', json.dumps(clues))
except Exception as error:
    print('System metadata unavailable:', str(error))
    raise SystemExit(1)
finally:
    if session is not None:
        client.RemoveSession(session)
