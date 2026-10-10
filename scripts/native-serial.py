#!/usr/bin/env python3
"""Probe an explicitly selected native RFCOMM serial service and optionally hold it."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address')
parser.add_argument('--channel', type=int, choices=range(1, 31), default=3)
parser.add_argument('--inquiry', action='store_true', help='Refresh discovery before connecting')
parser.add_argument('--identify', action='store_true', help='Send only basic AT identity queries')
parser.add_argument('--line-ending', choices=('cr', 'crlf'), default='cr', help='AT query terminator')
parser.add_argument('--hold', action='store_true', help='Keep the connection open after probing')
args = parser.parse_args()
if args.inquiry:
    subprocess.run(['bluetoothctl', '--timeout', '12', 'scan', 'on'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
result = {'channel': args.channel, 'line_ending': args.line_ending, 'queries': [], 'unsolicited_hex': []}
logs = Path(__file__).resolve().parent.parent / 'logs'
logs.mkdir(exist_ok=True)
target = logs / 'native-serial-latest.json'

def save():
    target.write_text(json.dumps(result, indent=2) + '\n')
    target.chmod(0o600)

sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
sock.settimeout(8)
try:
    sock.connect((args.address, args.channel))
    result['connected'] = True
    print('Native RFCOMM connected', flush=True)
    if args.identify:
        for command in ('AT', 'ATI', 'AT+CGMI', 'AT+CGMM', 'AT+CGMR'):
            sock.sendall((command + ('\r\n' if args.line_ending == 'crlf' else '\r')).encode('ascii'))
            sock.settimeout(3)
            data = bytearray()
            deadline = time.monotonic() + 4
            while len(data) < 8192 and time.monotonic() < deadline:
                try:
                    chunk = sock.recv(min(4096, 8192 - len(data)))
                    if not chunk:
                        raise ConnectionError('Serial peer closed the connection')
                    data.extend(chunk)
                except TimeoutError:
                    break
            result['queries'].append({'command': command, 'response_hex': data.hex()})
            print(command + ': ' + str(len(data)) + ' response bytes', flush=True)
            save()
    if args.hold:
        print('Holding native serial connection; no further commands sent', flush=True)
        sock.settimeout(1)
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    raise ConnectionError('Serial peer closed the connection')
                if len(result['unsolicited_hex']) >= 16:
                    raise RuntimeError('Unsolicited capture limit reached')
                result['unsolicited_hex'].append(data.hex())
                print('Unsolicited serial data: ' + str(len(data)) + ' bytes saved privately', flush=True)
                save()
            except TimeoutError:
                pass
except KeyboardInterrupt:
    print('Native serial connection closed', flush=True)
except OSError as error:
    result['error'] = str(error)
    print('Native serial failed: ' + str(error), flush=True)
    raise SystemExit(1)
finally:
    sock.close()
    save()
