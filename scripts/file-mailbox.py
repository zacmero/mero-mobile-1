#!/usr/bin/env python3
"""Exchange bounded diagnostic commands using the phone's native OBEX FTP."""
import argparse
import json
from pathlib import Path
import tempfile
import time

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


def parse_response(data):
    if len(data) > 16384 or not data.endswith(b'\nend=1\n'):
        raise ValueError('Incomplete or oversized response')
    fields = {}
    for line in data.decode('utf-8').splitlines():
        key, separator, value = line.partition('=')
        if not separator or key in fields:
            raise ValueError('Malformed or duplicate response field')
        fields[key] = value
    if fields.get('protocol') != 'mero-files/1' or fields.get('end') != '1':
        raise ValueError('Wrong mailbox protocol')
    if not fields.get('seq', '').isdigit() or not fields.get('ack') or not fields.get('result'):
        raise ValueError('Missing response fields')
    return fields


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('address', help='Paired phone Bluetooth address')
    parser.add_argument('--folder', default='MeroMailbox', help='Mailbox path relative to OBEX root')
    parser.add_argument('--command', choices=('PING', 'INFO'), help='Omit to read startup diagnostics')
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 300:
        parser.error('Timeout must be 1..300 seconds')
    if not args.folder or any(part in ('.', '..') for part in args.folder.split('/')):
        parser.error('Use a mailbox folder path without dot components')
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    client = dbus.Interface(bus.get_object('org.bluez.obex', '/org/bluez/obex'), 'org.bluez.obex.Client1')
    session = None

    def transfer(operation):
        loop = GLib.MainLoop()
        outcome = {'status': None}
        active = {'path': None}

        def changed(interface, properties, invalidated, path):
            if path == active['path'] and interface == 'org.bluez.obex.Transfer1':
                status = properties.get('Status')
                if status is not None:
                    outcome['status'] = str(status)
                    if outcome['status'] in ('complete', 'error'):
                        loop.quit()

        def expired():
            outcome['status'] = 'timeout'
            loop.quit()
            return False

        receiver = bus.add_signal_receiver(changed, signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties', bus_name='org.bluez.obex', path_keyword='path')
        timer = GLib.timeout_add_seconds(args.timeout, expired)
        try:
            active['path'], properties = operation()
            outcome['status'] = str(properties.get('Status', 'queued'))
            if outcome['status'] not in ('complete', 'error'):
                loop.run()
            if outcome['status'] != 'complete':
                if outcome['status'] == 'timeout':
                    try:
                        dbus.Interface(bus.get_object('org.bluez.obex', active['path']),
                                       'org.bluez.obex.Transfer1').Cancel()
                    except dbus.DBusException:
                        pass
                raise RuntimeError('OBEX transfer ' + str(outcome['status']))
        finally:
            receiver.remove()
            if outcome['status'] != 'timeout':
                GLib.source_remove(timer)

    try:
        session = client.CreateSession(args.address, {'Target': dbus.String('ftp')}, timeout=35)
        ftp = dbus.Interface(bus.get_object('org.bluez.obex', session), 'org.bluez.obex.FileTransfer1')
        for part in args.folder.split('/'):
            if part:
                ftp.ChangeFolder(part, timeout=30)
        with tempfile.TemporaryDirectory(prefix='mero-mailbox-') as directory:
            local = Path(directory)

            def get_file(name, target, limit):
                entries = {str(entry['Name']): entry for entry in ftp.ListFolder(timeout=30)}
                entry = entries.get(name)
                if entry is None or str(entry.get('Type')) != 'file':
                    raise ValueError(name + ' is not available yet')
                if 'Size' not in entry or not 0 <= int(entry['Size']) <= limit:
                    raise ValueError(name + ' has an invalid size')
                transfer(lambda: ftp.GetFile(str(target), name, timeout=35))
                data = target.read_bytes()
                if len(data) > limit:
                    raise ValueError('Readback exceeds size bound')
                return data

            command_id = None
            if args.command:
                command_id = str(time.time_ns())
                command = ('protocol=mero-files/1\nid=' + command_id + '\ncommand='
                           + args.command + '\nend=1\n').encode('utf-8')
                source = local / 'command.txt'
                source.write_bytes(command)
                transfer(lambda: ftp.PutFile(str(source), 'command.txt', timeout=35))
                if get_file('command.txt', local / 'command-readback.txt', 4096) != command:
                    raise RuntimeError('Command readback differs from original')
                print('Command file verified by full readback', flush=True)
            deadline = time.monotonic() + args.timeout
            reason = 'No response'
            while time.monotonic() < deadline:
                try:
                    fields = parse_response(get_file('response.txt', local / 'response.txt', 16384))
                    if command_id is None or fields['ack'] == command_id:
                        if args.command == 'PING' and fields['result'] != 'PONG':
                            raise ValueError('PING did not return PONG')
                        if args.command == 'INFO' and fields['result'] != 'INFO OK':
                            raise ValueError('INFO did not return INFO OK')
                        logs = Path(__file__).resolve().parent.parent / 'logs'
                        logs.mkdir(exist_ok=True)
                        (logs / 'file-mailbox-latest.json').write_text(json.dumps(fields, indent=2) + '\n')
                        print(json.dumps(fields, indent=2))
                        return
                    reason = 'Waiting for matching command acknowledgement'
                except ValueError as error:
                    reason = str(error)
                time.sleep(2)
            raise RuntimeError(reason + ' (timed out)')
    finally:
        if session is not None:
            client.RemoveSession(session)


if __name__ == '__main__':
    main()
