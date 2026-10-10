#!/usr/bin/env python3
"""Read diagnostics and send commands to the Mero Link MIDlet over RFCOMM."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import socket
import sys
from bluetooth_sdp import find_channel

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address', help='Paired phone Bluetooth address')
parser.add_argument('--channel', type=int, help='Use a known RFCOMM channel instead of SDP discovery')
parser.add_argument('--log', type=Path, default=Path(__file__).resolve().parent.parent / 'logs/bluetooth-link.log')
parser.add_argument('--interactive', action='store_true', help='Keep connected and read commands from stdin')
parser.add_argument('commands', nargs='*', help='Commands; default INFO PING SCREEN')
args = parser.parse_args()
allowed = {'INFO', 'PING', 'HEAP', 'SCREEN', 'KEY', 'BYE'}
commands = args.commands or ['INFO', 'PING', 'SCREEN']
if any(command not in allowed for command in commands):
    parser.error('Commands: ' + ', '.join(sorted(allowed)))
if args.channel is not None and not 1 <= args.channel <= 30:
    parser.error('RFCOMM channel must be 1..30')
args.log.parent.mkdir(parents=True, exist_ok=True)
try:
    channel = args.channel or find_channel(args.address)
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock, args.log.open('a') as log:
        sock.settimeout(20)
        sock.connect((args.address, channel))
        with sock.makefile('rb') as stream:
            def receive(label):
                lines = []
                total = 0
                while True:
                    line = stream.readline(4097)
                    total += len(line)
                    if not line or len(line) > 4096 or total > 16384:
                        raise RuntimeError('Incomplete or oversized diagnostic response')
                    text = line.decode('utf-8').rstrip('\r\n')
                    if text == 'END':
                        break
                    lines.append(text)
                text = '\n'.join(lines)
                entry = datetime.now(timezone.utc).isoformat() + ' ' + label + '\n' + text + '\n'
                print(entry, end='', flush=True)
                log.write(entry)
                log.flush()
                return lines

            greeting = receive('connected')
            if not greeting or greeting[0] != 'MERO-LINK/1':
                raise RuntimeError('Unexpected Bluetooth service greeting')
            for command in commands:
                sock.sendall((command + '\n').encode('ascii'))
                reply = receive(command)
                if command == 'PING' and reply != ['PONG']:
                    raise RuntimeError('PING response was not PONG')
                if command == 'BYE':
                    break
            if args.interactive and 'BYE' not in commands:
                print('Connected. Commands: INFO PING HEAP SCREEN KEY BYE', flush=True)
                for line in sys.stdin:
                    command = line.strip().upper()
                    if command not in allowed:
                        print('Unknown command', flush=True)
                        continue
                    sock.sendall((command + '\n').encode('ascii'))
                    receive(command)
                    if command == 'BYE':
                        break
except Exception as error:
    print('Bluetooth link failed: ' + str(error), file=sys.stderr)
    sys.exit(1)
