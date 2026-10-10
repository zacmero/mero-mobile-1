# Software routes toward native access

The owner explicitly authorized basic serial identification experiments and
USB cold-boot discovery, prioritizing software investigation before board
photographs. Native OS, chipset, console and shell remain unconfirmed.

## Native Bluetooth Serial Port

Earlier SDP advertised Serial Port `sprd_com3` on RFCOMM channel 3. A passive
connection succeeded once and produced no unsolicited bytes in eight seconds.

The subsequent identification experiment prepared `AT`, `ATI`, `AT+CGMI`,
`AT+CGMM`, and `AT+CGMR`, but both connection attempts returned Connection
refused before any query was sent. A refreshed SDP query did not yield an
RFCOMM channel for UUID 1101 in that phone state. Standard Bluetooth UUIDs
are now queried using their 16-bit SDP representation; custom UUIDs remain
128-bit. The earlier channel is therefore historical evidence, not proof
that the service is currently accepting connections.

Another channel-3 connection after the Java serial attempt also returned
Connection refused. No AT protocol, console or shell has been identified.
No guessed vendor configuration, reset or firmware commands were sent.

## Java serial port 0

Mero Files v0.6 reported CommConnection class presence and the literal property
`microedition.commports=0`. v0.7 adds a SERIAL mailbox command to test actual
port opening. It requests optional Connector.comm permission and attempts
`comm:0;blocking=off` with the default connection mode/framing. A worker is
observed for at most ten seconds; an opened connection is closed on timeout.
An underlying Connector.open blocked inside the VM may remain pending until
it returns; the app cannot forcibly interrupt that native call. Relaunch before
repeating a timed-out serial test rather than accumulating blocked workers.

If opening succeeds, the probe records the baud rate, makes a short passive
read, then sends only the five basic identification queries above. Responses
are bounded and encoded as hexadecimal in private runtime logs. No physical
UART, modem command processor, or shell is inferred from the Java interface.

The v0.7 artifacts in Bt passed exact-size and full-content readback:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 8,500 | 58b2ce25e0497e4c51328a3d155e48062e2fbde039ccc94d120b51df9edcd0f7 |
| MeroFiles.jad | 379 | 3747d476a9eec991e36c77ed4288bc985521c72452e56f8c8c4f290bd452b33b |

The owner installed/launched v0.7. A new 66-byte SERIAL command passed full
readback verification (SHA-256
0ae45d88f0d4d95c57f06239c0c2d0e98aed11a49c946aacbb010a61996f7109).
The host left Bluetooth idle for twenty seconds after reception to permit
permission prompts, then retrieved the matching acknowledgement:

| Field | Value |
| --- | --- |
| app_version | 0.7 |
| seq | 7 |
| result | SERIAL DONE |
| serial_status | timeout |
| serial_stage | open comm:0 |
| heap_free | 1736624 bytes |
| heap_total | 2486656 bytes |

SERIAL DONE means the diagnostic command completed its bounded observation,
not that the port opened. The owner saw the app accept the command without
manual action; that label does not establish a serial-permission confirmation.
No Java serial query was sent because opening did not complete in the bound.

## Continuous USB boot monitoring

Start the recorder before any cable or power operation:

    rtk proxy python scripts/usb-watch.py

It listens to kernel and udev USB events continuously, saving a filtered JSONL
record to ignored logs/usb-events.jsonl. It records add/remove/change events,
including short-lived devices, without serial-number properties. The process
must stay running through the owner's physical experiments; a one-time lsusb
snapshot is insufficient.

The first cold-boot experiment unplugged USB, powered the phone off, and
reconnected USB without switching it on. The owner observed charging; the
continuous monitor recorded no USB events. A centre/OK boot-key trial was then
requested with the monitor still running. Its result is pending.

Supported Spreadtrum feature-phone tools document transient USB ID 1782:4d00
and model-dependent boot keys. This is a candidate discovery route, not an
established identifier for this handset. Chipset-specific loaders are not yet
selected or executed. See the primary
[Spreadtrum dumper instructions](https://github.com/ilyakurdyukov/spreadtrum_flash).
