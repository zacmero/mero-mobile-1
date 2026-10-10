#!/usr/bin/env python3
"""Continuously record USB add/remove events, including brief boot devices."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

logs = Path(__file__).resolve().parent.parent / 'logs'
logs.mkdir(exist_ok=True)
process = subprocess.Popen(['udevadm', 'monitor', '--kernel', '--udev', '--property',
                            '--subsystem-match=usb'], stdout=subprocess.PIPE, text=True, bufsize=1)
fields = ('ACTION', 'DEVPATH', 'DEVNAME', 'DEVTYPE', 'PRODUCT', 'ID_VENDOR_ID', 'ID_MODEL_ID',
          'ID_VENDOR', 'ID_MODEL', 'DRIVER')
header = None
properties = {}
print('USB monitoring active; recording filtered add/remove/change events', flush=True)
try:
    with (logs / 'usb-events.jsonl').open('a') as output:
        for raw in process.stdout:
            line = raw.strip()
            if line.startswith(('KERNEL[', 'UDEV  [', 'UDEV[')):
                header = line
                properties = {}
            elif '=' in line and header:
                name, value = line.split('=', 1)
                if name in fields:
                    properties[name] = value
            elif not line and header:
                event = {'observed_at': datetime.now(timezone.utc).isoformat(),
                         'source': header.split('[', 1)[0].strip(), **properties}
                output.write(json.dumps(event) + '\n')
                output.flush()
                product = properties.get('PRODUCT', '').split('/')
                vendor = properties.get('ID_VENDOR_ID', product[0] if product else '?')
                model = properties.get('ID_MODEL_ID', product[1] if len(product) > 1 else '?')
                print(event['observed_at'] + ' ' + properties.get('ACTION', '?') + ' '
                      + vendor + ':' + model + ' ' + properties.get('DEVTYPE', '')
                      + ' ' + properties.get('ID_MODEL', ''), flush=True)
                header = None
                properties = {}
except KeyboardInterrupt:
    pass
finally:
    process.terminate()
    process.wait(timeout=5)
