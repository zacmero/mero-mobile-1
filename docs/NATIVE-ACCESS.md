# Software routes toward native access

The entries below record successive experiments. The latest outcome section supersedes earlier pending steps; USB monitoring and Bluetooth serial experiments are stopped at the owner's request.

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
requested with the monitor still running. The owner subsequently completed both battery-related steps and reported no
response. The monitor recorded zero USB events. The owner reports that the
phone does not turn on without its battery and works only with the battery
installed in the tested setup. No bootloader enumeration was observed.

Supported Spreadtrum feature-phone tools document transient USB ID 1782:4d00
and model-dependent boot keys. This is a candidate discovery route, not an
established identifier for this handset. Chipset-specific loaders are not yet
selected or executed. See the primary
[Spreadtrum dumper instructions](https://github.com/ilyakurdyukov/spreadtrum_flash).

## Newly observed label

The board-covering label reports model N2322. Owner-supplied SN and IMEI are
preserved exactly in private/DEVICE-LABEL.md and excluded from public Git.
No chipset inference is made from this model. Board inspection remains deferred.


## Subsequent software probes

USB monitoring was stopped at the owner's request. A further normal boot while
connected produced no recorded USB events. No USB monitor is currently running.

After refreshing Bluetooth inquiry, native RFCOMM channel 3 accepted a connection.
The host sent AT, ATI, AT+CGMI, AT+CGMM and AT+CGMR, each terminated by carriage
return, and received zero response bytes. This establishes connectivity, but
neither an AT interpreter nor a shell. A later passive connection was refused.

Native FTP listed System as containing MMS and Java. MMS contents were not read.
System/Java contained 20 entries; numbered JAR sizes matched the four apps delivered
by this project. Before reading suite 3 metadata, its installed 8,500-byte JAR was
read back and compared in full to the known v0.7 original. Only that owned suite's
3.jdx, 3.mss and 3.raw were then read, bounded by listed sizes (1,177, 58 and 404
bytes). Installer metadata was not modified. Raw captures remain private.

The owned 3.jdx contains gfs://java/3.jad and gfs://java/3.jar. This is an observed
installer namespace, not proof of an accessible GCF protocol or native shell.
The 3.raw contains this project's manifest; no firmware vendor was identified.
The binary 3.mss format is unknown and was not patched.

Mero Files v0.8 adds PATHS: bounded probes of E, C, D, A, F and Z roots, followed
by the owned gfs JAR URL. It records connection implementation classes and root
existence without directory traversal. Only the owned GFS JAR header may be read,
up to 16 bytes. A timeout stops remaining probes.

The delivered v0.8 artifacts passed exact saved-size and full-content readback:
JAR 10,704 bytes, SHA-256
fbc17695b668d159cb45131f94d30842ed9b7805fc6f5b39666a23ac0a7a9a2f;
JAD 380 bytes, SHA-256
fc3dcf2479624f9cb14a0b9cf7722f5f2cedbf558fd13968d1950bc095328114.
Installation and PATHS results are pending. Confirm the installed suite number
still belongs to this app before probing its internal GFS URL.


## v0.8 live results

Installation reassigned this app from suite 3 to suite 4. System/Java metadata
showed no remaining 3.jar; 4.jar was fully read back and matched the verified
10,704-byte v0.8 original and SHA-256 above. Future probes must not assume stable
suite numbers across updates.

A fresh 65-byte PATHS command passed full readback and the response matched its
command ID, app_version=0.8 and result=PATHS DONE. All six file URLs opened using
jp.co.aplix.cldc.io.file.FileConnectionImp. E:/ reported exists=true and
directory=true. C:/, D:/, A:/, F:/ and Z:/ reported exists=false. This identifies
an Aplix package in the Java runtime; it does not identify the chipset or OS.

The old gfs://java/3.jar URL returned javax.microedition.io.ConnectionNotFoundException.
Because suite 3 was absent, this does not establish how the current suite's GFS
URL behaves. No internal JAR header was read. The response also retains the serial
observation: timeout at open comm:0. Automatic command or permission acceptance
is not evidence of a successful serial connection. No native shell is obtained.


## v0.9 access implementation

The app now accepts OPEN with a supplied file: or gfs: URL, removing fixed suite
number assumptions and enabling further route tests without binary replacement.
Installed v0.9 JAR ownership was verified in suite 3. Java listed System/Java and
read the installed JAR through file:///E:/System/Java/3.jar; the 64-byte header
matched the local original exactly. Current-suite gfs access failed with
ConnectionNotFoundException. A parent traversal request, file:///E:/../, failed
with IllegalArgumentException. No installer metadata was changed.

The native serial utility now supports --line-ending crlf in addition to the
previous carriage-return terminator. A Java-closed retry is pending.


## Coordinated serial and native AT routes

With Java closed, current SDP exposed FTP channel 5 but no SPP channel; a raw
channel-3 connection was refused. A coordinated host-client retry while SERIAL
opened comm:0 timed out. After the owner allowed the local-connection prompt,
a fresh matching Java response reported serial_status=error at open comm:0,
with java.io.IOException: open failed. Neither client retry exchanged Java data.

Current native SDP exposes Hands-Free Gateway on channel 4 and Headset Gateway
on channel 6. A channel-4 RFCOMM session answered AT+BRSF=0 with +BRSF: 33 and OK,
and AT+CIND=? with service (0-1), call (0-1), callsetup (0-3) and OK.
AT+CGMI, AT+CGMM, AT+CGMR and AT+CLAC each returned ERROR. This is a working native
AT interpreter with a limited tested command set, not an OS shell. No dialing,
call control or contact queries were sent. Raw responses remain private.

Owner-observed activating/device-discovery failure during comm:0 suggests an
outgoing Bluetooth route, but the mapping remains unproven. A host SPP server
was implemented with BlueZ ProfileManager and paired-device filtering. Initial
channel 7 registration returned success but the Bluetooth journal revealed
rfcomm_bind Address already in use. No server was listening there. Channel 22
registration subsequently advertised Serial Port in the adapter UUIDs. Startup
now requires that advertisement check. The server replies only to five known
Java test queries and does not execute received input.

References: BlueZ ProfileManager API and src/profile.c, and the Spreadtrum
spd_dump.c CHECK_BAUD implementation (one 0x7e byte). A version-probe option was
implemented, but its connection was refused before the byte could be sent.
No bootloader version, loader execution or firmware memory access was obtained.


With the channel-22 server confirmed advertised, the next 66-byte SERIAL
command passed full saved-size and content readback and its matching response
still reported IOException: open failed. The host received no SPP connection.
A paired-device service refresh/manual Serial Port selection is the next live
step; no Java-to-host serial round trip is established yet.

Run the native host server with:

```sh
rtk proxy python scripts/java-serial-server.py PHONE_ADDRESS --duration 900
```

It registers SPP on channel 22 by default, requires pairing, accepts only the
specified device and makes the adapter discoverable for the bounded run. On
normal exit it unregisters the profile and restores prior discovery settings.
A server registration response alone is insufficient: startup also checks the
Serial Port UUID advertisement because BlueZ can silently fail a channel bind.
See the [BlueZ ProfileManager API](https://github.com/bluez/bluez/blob/master/doc/org.bluez.ProfileManager.rst)
and [profile implementation](https://github.com/bluez/bluez/blob/master/src/profile.c).


## Fresh pairing and v0.10

The owner removed the old phone-side pairing; the computer also removed its old
bond and prepared a default pairing agent while SPP channel 22 was advertised.
Legacy PIN pairing completed, confirmed by Paired=true and Bonded=true; phone
service discovery also completed. After the owner relaunched v0.9 and accepted
SERIAL, the startup response reported timeout at open comm:0. The host SPP server
received no connection. Fresh pairing did not establish Java serial access.

v0.10 increases the Java serial opening deadline from 10 to 90 seconds and tries
comm:0 without the optional blocking parameter. The longer deadline allows an
experiment with discovery/selection latency; it is not an established fix.
Startup now records the saved command ID without executing it, so an app launch
waits for a fresh command rather than replaying a previous SERIAL request.

v0.10 compiled and its delivered artifacts passed full saved-size and byte
readback before installation was requested:
JAR 11,457 bytes, SHA-256
e6b92bdaf13a02cad7b70811aa677448086ee6574981d73b71b7e57f2dfd6c76;
JAD 381 bytes, SHA-256
bec1c93b7be67cd6ca9c980428b67e3d59c381d0b1666135b0623ac6a3aee6e9.
The host server was renewed on channel 22 with a one-hour bounded lifetime.
The v0.10 live SERIAL result is pending. Use a fresh command, allow sufficient
permission/discovery time, and check both the matching mailbox response and host
server data; accepted commands alone do not prove serial connectivity.

## Latest outcome: v0.10 and stopped serial experiments

The owner installed the fully verified v0.10 artifacts: JAR 11,457 bytes and
JAD 381 bytes. A fresh 66-byte SERIAL command passed full saved-file readback;
the matching response reported app_version=0.10, result=SERIAL DONE,
serial_status=timeout and serial_stage=open comm:0. The longer opening window
and plain comm:0 URL did not establish Java serial access. The advertised host
SPP server received no Java peer connection and has now been closed.

An additional native HFP session accepted the four service initialization
commands AT+BRSF=0, AT+CIND=?, AT+CIND? and AT+CMER=3,0,0,1. Manufacturer/model/
version variants and AT+CLAC returned ERROR. No dialing, call control or
contact query was sent. This is measured limited AT access, not a native shell.

The host utility now has a restricted `--console` mode with service
initialization, `status`, `indicators`, `quit` and bounded unsolicited capture.
Its live retries on the historical channel 4 were refused. Subsequent discovery
reported HFP channel 7 after pairing; native channels must be rediscovered
rather than cached across bond changes. The console is not live-verified.

The owner requested ending the Bluetooth serial route. Do not restart those
experiments or USB monitoring without new direction. The current software
route is the native Wi-Fi browser endpoint in [HTTP-LINK.md](HTTP-LINK.md).
No bootloader response, loader execution, firmware write or OS shell was obtained.
