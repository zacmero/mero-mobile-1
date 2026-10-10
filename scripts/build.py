#!/usr/bin/env python3
"""Build a preverified CLDC 1.0 / MIDP 1.0 probe using a local Java runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / '.cache' / 'mero-mobile-toolchain'
TOOLS = {
    'ecj': ('org/eclipse/jdt/ecj/3.26.0/ecj-3.26.0.jar', 'ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5'),
    'proguard': ('net/sf/proguard/proguard-base/6.2.2/proguard-base-6.2.2.jar', '7587a3a415d6aea1946f597f4babe710a245f085bac4dc5e7cda653acfc39b03'),
    'cldcapi10': ('org/microemu/cldcapi10/2.0.4/cldcapi10-2.0.4.jar', '6b5753c830a966d91cbfcd5cde223a6899c6c69f021a8e38a429cec967bc290d'),
    'midpapi20': ('org/microemu/midpapi20/2.0.4/midpapi20-2.0.4.jar', 'b7f6ed5e0344c7000643ecc114e6edff3587e8e77face546af0e12ffd6dbe826'),
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--java', default=shutil.which('java'), help='Java executable (8 or later)')
parser.add_argument('--app', choices=('hello', 'link', 'http'), default='hello')
args = parser.parse_args()
if not args.java:
    parser.error('Java runtime missing; provide --java /path/to/bin/java')
CACHE.mkdir(parents=True, exist_ok=True)
if args.app == 'link':
    TOOLS['bluecove'] = ('net/sf/bluecove/bluecove/2.1.0/bluecove-2.1.0.jar', 'add9a58dbee3eaa35a062010a11066ba772a72119f24165f4adf0e19e60a4b8a')
for name, (url, digest) in TOOLS.items():
    file = CACHE / (name + '.jar')
    if not file.exists():
        with urllib.request.urlopen('https://repo.maven.apache.org/maven2/' + url, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != digest:
            raise RuntimeError('Download checksum mismatch: ' + name)
        file.write_bytes(data)
    if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise RuntimeError('Cached checksum mismatch: ' + name)

build = ROOT / 'build'
app = {'hello': 'MeroHello', 'link': 'MeroLink', 'http': 'MeroHTTP'}[args.app]
classes = build / (app + '-classes')
if classes.exists():
    shutil.rmtree(classes)
classes.mkdir(parents=True, exist_ok=True)
apis = [str(CACHE / (name + '.jar')) for name in ('cldcapi10', 'midpapi20')]
sources = [str(ROOT / ('src/' + app + '.java'))]
if args.app == 'link':
    apis.append(str(CACHE / 'bluecove.jar'))
    sources.append(str(ROOT / 'src/BluetoothLink.java'))
if args.app == 'http':
    settings = json.loads((build / 'http-settings.json').read_text())
    generated = build / 'HTTPSettings.java'
    generated.write_text('final class HTTPSettings { static final String URL = ' + json.dumps(settings['url']) + '; }\n')
    sources.append(str(generated))
subprocess.run([args.java, '-jar', str(CACHE / 'ecj.jar'), '-source', '1.3', '-target', '1.1',
                '-bootclasspath', ':'.join(apis), '-d', str(classes)] + sources, check=True)
name = {'hello': 'Mero Hello', 'link': 'Mero Link', 'http': 'Mero HTTP'}[args.app]
profile = 'MIDP-1.0' if args.app == 'hello' else 'MIDP-2.0'
version = '0.2.0' if args.app == 'http' else '0.1.0'
manifest = ('Manifest-Version: 1.0\r\nMIDlet-Name: ' + name + '\r\nMIDlet-Version: ' + version + '\r\n'
            'MIDlet-Vendor: Mero Lab\r\nMIDlet-1: ' + name + ', , ' + app + '\r\n'
            'MicroEdition-Configuration: CLDC-1.0\r\nMicroEdition-Profile: ' + profile + '\r\n')
if args.app == 'link':
    manifest += 'MIDlet-Permissions-Opt: javax.microedition.io.Connector.bluetooth.server\r\n'
if args.app == 'http':
    manifest += 'MIDlet-Permissions-Opt: javax.microedition.io.Connector.http\r\n'
unverified = build / (app + '-unverified.jar')
output = build / (app + '.jar')
with zipfile.ZipFile(unverified, 'w', zipfile.ZIP_DEFLATED) as jar:
    jar.writestr('META-INF/MANIFEST.MF', manifest + '\r\n')
    for file in sorted(classes.glob('*.class')):
        jar.write(file, file.name)
command = [args.java, '-jar', str(CACHE / 'proguard.jar'), '-injars', str(unverified), '-outjars', str(output)]
for api in apis:
    command.extend(['-libraryjars', api])
subprocess.run(command + ['-dontshrink', '-dontoptimize', '-dontobfuscate', '-microedition', '-target', '1.1'], check=True)
size = output.stat().st_size
jad = manifest.replace('Manifest-Version: 1.0\r\n', '') + 'MIDlet-Jar-URL: ' + app + '.jar\r\nMIDlet-Jar-Size: ' + str(size) + '\r\n'
descriptor = build / (app + '.jad')
descriptor.write_bytes(jad.encode('ascii'))
print('Built:', output, '(' + str(size) + ' bytes)', 'and', descriptor.name, '(' + str(descriptor.stat().st_size) + ' bytes)')
