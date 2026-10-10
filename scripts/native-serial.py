#!/usr/bin/env python3
"""Probe an explicitly selected native RFCOMM serial service and optionally hold it."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import select
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('address')
parser.add_argument('--channel', type=int, choices=range(1, 31), default=3)
parser.add_argument('--inquiry', action='store_true', help='Refresh discovery before connecting')
parser.add_argument('--identify', action='store_true', help='Send only basic AT identity queries')
parser.add_argument('--line-ending', choices=('cr', 'crlf'), default='cr', help='AT query terminator')
parser.add_argument('--boot-version', action='store_true', help='Send one Spreadtrum CHECK_BAUD byte (0x7e); no loader or writes')
parser.add_argument('--java-bridge', action='store_true', help='Reply to the known Java SERIAL identity queries; never execute peer input')
parser.add_argument('--handsfree-identify', action='store_true', help='Query a measured HFP gateway channel; no dialing or call control')
parser.add_argument('--console', action='store_true', help='Keep native HFP open; accept status, indicators and quit on stdin')
parser.add_argument('--connect-wait', type=int, default=0, help='Retry refused connections for up to 30 seconds')
parser.add_argument('--hold', action='store_true', help='Keep the connection open after probing')
args = parser.parse_args()
if not 0 <= args.connect_wait <= 30:
    parser.error('--connect-wait must be 0..30 seconds')
if args.java_bridge and (args.identify or args.boot_version or args.hold or args.handsfree_identify or args.console):
    parser.error('--java-bridge cannot be combined with other probe modes or --hold')
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
    deadline = time.monotonic() + args.connect_wait
    while True:
        try:
            sock.connect((args.address, args.channel))
            break
        except OSError:
            if time.monotonic() >= deadline:
                raise
            sock.close()
            time.sleep(0.25)
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.settimeout(min(2, max(0.1, deadline - time.monotonic())))
    result['connected'] = True
    print('Native RFCOMM connected', flush=True)
    if args.java_bridge:
        replies = {b'AT': b'OK', b'ATI': b'MERO HOST BRIDGE', b'AT+CGMI': b'Mero',
                   b'AT+CGMM': b'Computer bridge', b'AT+CGMR': b'mero-bridge/1'}
        result['bridge'] = []
        sock.settimeout(0.25)
        pending = bytearray()
        received = 0
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and received < 8192:
            try:
                chunk = sock.recv(min(4096, 8192 - received))
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
                        sock.sendall(message)
                        event['sent_hex'] = message.hex()
                        print('Replied to Java query ' + line.decode('ascii'), flush=True)
                    result['bridge'].append(event)
                    save()
            except TimeoutError:
                pass
        result['bridge_received_bytes'] = received
        result['bridge_pending_hex'] = pending.hex()
        print('Bridge received ' + str(received) + ' bytes', flush=True)
    if args.boot_version:
        sock.sendall(b'\x7e')
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
        result['boot_version_probe'] = {'sent_hex': '7e', 'response_hex': data.hex()}
        print('CHECK_BAUD: ' + str(len(data)) + ' response bytes', flush=True)
        save()
    def query(command):
        started = time.monotonic()
        ending = '\r\n' if args.console or args.line_ending == 'crlf' else '\r'
        sock.sendall((command + ending).encode('ascii'))
        sock.settimeout(3)
        data = bytearray()
        deadline = time.monotonic() + 4
        while len(data) < 8192 and time.monotonic() < deadline:
            try:
                chunk = sock.recv(min(4096, 8192 - len(data)))
                if not chunk:
                    raise ConnectionError('Serial peer closed the connection')
                data.extend(chunk)
                if b'\r\nOK\r\n' in data or b'\r\nERROR\r\n' in data:
                    break
            except TimeoutError:
                break
        elapsed = round((time.monotonic() - started) * 1000, 1)
        result['queries'].append({'command': command, 'response_hex': data.hex(), 'elapsed_ms': elapsed})
        print(command + ': ' + str(len(data)) + ' response bytes, ' + str(elapsed) + ' ms', flush=True)
        save()
        return bytes(data)

    if args.identify or args.handsfree_identify or args.console:
        commands = ('AT+BRSF=0', 'AT+CIND=?', 'AT+CIND?', 'AT+CMER=3,0,0,1',
                    'AT+CGMI', 'AT+CGMM', 'AT+CGMR', 'AT+GMI', 'AT+GMM', 'AT+GMR', 'AT+CLAC') if args.handsfree_identify else (
                    ('AT+BRSF=0', 'AT+CIND=?', 'AT+CIND?', 'AT+CMER=3,0,0,1') if args.console else
                    ('AT', 'ATI', 'AT+CGMI', 'AT+CGMM', 'AT+CGMR'))
        for command in commands:
            reply = query(command)
            if args.console and b'\r\nOK\r\n' not in reply:
                raise ConnectionError('HFP initialization failed at ' + command)
    if args.console:
        print('Native AT console ready: status, indicators, quit', flush=True)
        allowed = {'status': 'AT+CIND?', 'indicators': 'AT+CIND=?'}
        while True:
            ready, _, _ = select.select([sock, sys.stdin], [], [], 1)
            if sys.stdin in ready:
                line = sys.stdin.readline()
                if not line or line.strip() == 'quit':
                    break
                command = allowed.get(line.strip())
                if command is None:
                    print('Use status, indicators or quit', flush=True)
                else:
                    reply = query(command)
                    print(reply.decode('ascii', 'replace').strip(), flush=True)
                continue
            if sock in ready:
                chunk = sock.recv(4096)
                if not chunk:
                    raise ConnectionError('Native peer disconnected')
                if len(result['unsolicited_hex']) >= 64:
                    raise RuntimeError('Unsolicited capture limit reached')
                result['unsolicited_hex'].append(chunk.hex())
                print('Native event received (' + str(len(chunk)) + ' bytes)', flush=True)
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
