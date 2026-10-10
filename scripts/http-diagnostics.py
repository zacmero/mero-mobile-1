#!/usr/bin/env python3
"""Serve LAN phone diagnostics, or queue a small diagnostic command."""
import argparse
from datetime import datetime, timezone
import hmac
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / 'logs'
SETTINGS = ROOT / 'build/http-settings.json'
COMMANDS = ('INFO', 'PING', 'HEAP', 'SCREEN', 'KEY', 'CAPABILITIES')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bind', default='127.0.0.1', help='Computer LAN address; default loopback')
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--command', choices=COMMANDS, help='Queue a command and exit')
args = parser.parse_args()
LOGS.mkdir(parents=True, exist_ok=True)
if args.command:
    pending = {'id': str(time.time_ns()), 'command': args.command}
    temporary = LOGS / 'http-command.tmp'
    temporary.write_text(json.dumps(pending))
    temporary.replace(LOGS / 'http-command.json')
    print('Queued', args.command, 'id', pending['id'])
    raise SystemExit(0)

SETTINGS.parent.mkdir(parents=True, exist_ok=True)
if SETTINGS.exists():
    token = json.loads(SETTINGS.read_text())['token']
else:
    token = secrets.token_hex(16)
settings = {'url': 'http://' + args.bind + ':' + str(args.port) + '/' + token, 'token': token}
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def log_request(self, code='-', size='-'):
        path = urlsplit(self.path).path
        route = 'health' if path == '/' else 'diagnostics' if hmac.compare_digest(path, '/' + token) else 'other'
        entry = {'received_at': datetime.now(timezone.utc).isoformat(), 'remote_address': self.client_address[0],
                 'method': self.command, 'route': route, 'status': code, 'http_version': self.request_version,
                 'user_agent': self.headers.get('User-Agent', ''),
                 'accept': self.headers.get('Accept', ''),
                 'wap_profile': self.headers.get('X-Wap-Profile', self.headers.get('Profile', ''))}
        with lock:
            with (LOGS / 'http-requests.jsonl').open('a') as log:
                log.write(json.dumps(entry) + '\n')
        if route == 'health' or code != 200:
            print('HTTP ' + self.command + ' ' + route + ' status=' + str(code), flush=True)

    def reply(self, code, body, content_type='text/plain; charset=utf-8'):
        data = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path.startswith('/link'):
            self.browser_link(url)
        elif url.path == '/':
            self.reply(200, '<html><body>Mero HTTP diagnostic server ready</body></html>\n', 'text/html; charset=utf-8')
        elif not hmac.compare_digest(url.path, '/' + token):
            self.reply(404, 'Not found\n')
        elif not url.query:
            self.reply(200, 'Mero HTTP diagnostic server ready\n')
        elif len(self.path) > 16384:
            self.reply(413, 'Request too large\n')
        else:
            try:
                query = parse_qs(url.query, strict_parsing=True, max_num_fields=1)
                if set(query) != {'data'} or len(query['data']) != 1:
                    raise ValueError('Invalid query')
                self.diagnostics(query['data'][0].encode('utf-8'))
            except ValueError:
                self.reply(400, 'Invalid diagnostics\n')

    def browser_link(self, url):
        if len(self.path) > 2048 or url.path not in ('/link', '/link.wml', '/link/status', '/link/send'):
            self.reply(404, 'Not found\n')
            return
        wants_wml = url.path == '/link.wml' or ('wml' in self.headers.get('Accept', '').lower()
                                              and 'text/html' not in self.headers.get('Accept', '').lower())
        title = 'Mero WiFi Link'
        message = 'Connected to the computer. No Java app is needed for this page.'
        if url.path == '/link/status':
            title = 'Computer answered'
            message = 'Computer time: ' + datetime.now(timezone.utc).isoformat()
        elif url.path == '/link/send':
            try:
                values = parse_qs(url.query, strict_parsing=True, max_num_fields=1)
                if set(values) != {'message'} or len(values['message']) != 1 or not 1 <= len(values['message'][0]) <= 160:
                    raise ValueError('Invalid message')
                text = values['message'][0]
            except ValueError:
                self.reply(400, 'Send 1..160 characters\n')
                return
            event = {'received_at': datetime.now(timezone.utc).isoformat(),
                     'remote_address': self.client_address[0], 'user_agent': self.headers.get('User-Agent', ''),
                     'message': text}
            with lock:
                target = LOGS / 'browser-link-events.jsonl'
                with target.open('a') as stream:
                    stream.write(json.dumps(event) + '\n')
                target.chmod(0o600)
            title = 'Computer received'
            message = text
            print('Phone browser message received', flush=True)
        title, message = escape(title), escape(message)
        if wants_wml:
            body = ('<?xml version="1.0"?>\n'
                    '<!DOCTYPE wml PUBLIC "-//WAPFORUM//DTD WML 1.1//EN" "http://www.wapforum.org/DTD/wml_1.1.xml">\n'
                    '<wml><card id="main" title="' + title + '"><p>' + message + '</p>'
                    '<p><a href="/link/status">Ping computer</a></p>'
                    '<p>Message: <input name="message" maxlength="160"/></p>'
                    '<do type="accept" label="Send"><go href="/link/send" method="get">'
                    '<postfield name="message" value="$(message)"/></go></do>'
                    '<p><a href="/link.wml">Home</a></p></card></wml>\n')
            self.reply(200, body, 'text/vnd.wap.wml')
        else:
            body = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
                    '<html><head><title>' + title + '</title></head><body><h3>' + title + '</h3><p>'
                    + message + '</p><p><a href="/link/status">Ping computer</a></p>'
                    '<form action="/link/send" method="get">Message: '
                    '<input name="message" maxlength="160"><input type="submit" value="Send"></form>'
                    '<p><a href="/link">Home</a> | <a href="/link.wml">WAP version</a></p></body></html>\n')
            self.reply(200, body, 'text/html')

    def do_POST(self):
        self.connection.settimeout(10)
        if not hmac.compare_digest(self.path, '/' + token):
            self.reply(403, 'Invalid endpoint\n')
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= 16384:
                self.reply(413, 'Invalid diagnostic size\n')
                return
            data = self.rfile.read(size)
            if len(data) != size:
                raise ValueError('Incomplete body')
        except (ValueError, TimeoutError):
            self.reply(400, 'Invalid diagnostics\n')
            return
        self.diagnostics(data)

    def diagnostics(self, data):
        try:
            if not 1 <= len(data) <= 16384:
                raise ValueError('Invalid size')
            fields = {}
            for line in data.decode('utf-8').splitlines():
                name, value = line.split('=', 1)
                if not name or name in fields:
                    raise ValueError('Invalid or duplicate field')
                fields[name] = value
            if fields.get('protocol') != 'mero-http/1' or not fields.get('seq', '').isdigit():
                raise ValueError('Unsupported protocol')
        except (ValueError, UnicodeError):
            self.reply(400, 'Invalid diagnostics\n')
            return
        snapshot = {'received_at': datetime.now(timezone.utc).isoformat(),
                    'remote_address': self.client_address[0], 'diagnostics': fields}
        with lock:
            with (LOGS / 'http-diagnostics.jsonl').open('a') as log:
                log.write(json.dumps(snapshot, ensure_ascii=True) + '\n')
            temporary = LOGS / 'http-latest.tmp'
            temporary.write_text(json.dumps(snapshot, indent=2))
            temporary.replace(LOGS / 'http-latest.json')
            command = {'id': '0', 'command': 'INFO'}
            pending = LOGS / 'http-command.json'
            if pending.exists():
                candidate = json.loads(pending.read_text())
                if candidate.get('command') in COMMANDS:
                    command = candidate
        print('Received seq=' + fields['seq'] + ' ack=' + fields.get('ack', '')
              + ' result=' + fields.get('result', ''), flush=True)
        self.reply(200, 'command_id=' + command['id'] + '\ncommand=' + command['command'] + '\ninterval=2000\n')


server = ThreadingHTTPServer((args.bind, args.port), Handler)
SETTINGS.write_text(json.dumps(settings, indent=2))
SETTINGS.chmod(0o600)
print('Listening on ' + args.bind + ':' + str(args.port) + '; private app settings saved in build/http-settings.json', flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
