# HTTP diagnostic connection

Mero HTTP sends bounded diagnostic snapshots to this computer over LAN HTTP and receives small diagnostic commands in each response. The v0.1 handset attempt produced `java.io.IOException` without a received diagnostic snapshot. The phone browser could download the LAN server response, establishing browser reachability. v0.2 failed on the handset at `response status` with `java.io.IOException`. The observed Java connection settings offer SIM profiles (CMCC WAP/MMS), with no WLAN choice observed. v0.3 adds a direct TCP HTTP request to test whether the Java HTTP proxy layer is involved; a handset command round trip remains unconfirmed.

## Start the computer server

Use the computer's LAN address, reachable from the phone's Wi-Fi:

    rtk proxy python scripts/http-diagnostics.py --bind COMPUTER_LAN_IP

The default port is 8765. The server binds only to the supplied address. It creates a private endpoint and saves its URL/token in gitignored `build/http-settings.json`. The default bind address is loopback; specify the LAN address for phone access. A browser can check `http://COMPUTER_LAN_IP:8765/` for a simple readiness message.

The server uses Python's standard library and accepts bounded UTF-8 `key=value` diagnostics via POST bodies or a percent-encoded GET `data` query at the private endpoint. It rejects invalid endpoints, malformed/duplicate fields, unsupported protocol and oversized messages. It records the latest snapshot in gitignored `logs/http-latest.json` and history in `logs/http-diagnostics.jsonl`. `logs/http-requests.jsonl` also records browser and rejected requests, methods, HTTP versions and user agents, with URL tokens/query payloads omitted. Runtime logs may contain device/network details; do not commit them.

The computer had active firewalld on its public LAN zone. The test used a one-hour runtime rule allowing TCP 8765 from its own IPv4 LAN subnet only. If the rule expires, re-establish an appropriate LAN-only rule before testing. Do not disable the firewall globally.

## Build, transfer and verify

With the server settings created and a Java runtime available:

    rtk proxy python scripts/build.py --app http --java /path/to/bin/java
    rtk proxy python scripts/send-bluetooth.py PHONE_ADDRESS build/MeroHTTP.jar build/MeroHTTP.jad
    rtk proxy python scripts/verify-bluetooth.py PHONE_ADDRESS --folder Bt build/MeroHTTP.jar build/MeroHTTP.jad

The build generates an ignored `HTTPSettings.java` from the private URL. No address typing is needed on the phone. The app targets CLDC 1.0 / MIDP 2.0, uses legacy bytecode and CLDC preverification, and requests optional HTTP and socket permissions. It does not use the missing Java Bluetooth API.

Before installation/launch, require a passing exact-size and full-content Bluetooth readback. OBEX completion alone is insufficient. A rebuild or endpoint change requires transferring and verifying the new artifacts again.

The v0.1 build passed exact-size and full-content Bluetooth readback verification (a first readback attempt returned an OBEX error; the retry succeeded). These values are build-specific:

| File | Bytes | Readback SHA-256 |
| --- | --- | --- |
| `MeroHTTP.jar` | 6,061 | `c5de3340bb5ab8a107b178c8b9a18c4d0906031e4bd5ca7c83c597918a25af5d` |
| `MeroHTTP.jad` | 290 | `1e4c920ab31000cd65f4fe077f42967b604ecdc7e7044be0f16877cbc5b876d2` |

The v0.2 update also passed full readback verification:

| File | Bytes | Readback SHA-256 |
| --- | --- | --- |
| `MeroHTTP.jar` | 6,846 | `5fac1bbe2bfd28932aa3e1926751860f08889431e409e435b0f8fc508e135d23` |
| `MeroHTTP.jad` | 290 | `b1c9de53759ede12b4f9743e7eb85aea7e8c8b352a49cd2b06d5900fa0dca693` |

## Phone operation and commands

Install Mero HTTP from the verified files and launch it. Allow network access and select Wi-Fi if the phone offers a connection choice. Internet access in the built-in browser does not establish that Java uses Wi-Fi.

The app uploads every two seconds plus request duration while active. v0.3 defaults to TCP and offers a `GET / POST / TCP` command to switch transport. TCP sends a bounded HTTP/1.0 request directly to the same LAN server; it still requires a working Java network bearer. The Details screen shows diagnostics locally even when networking fails. It displays the failing stage (preparing diagnostics, opening a connection, request headers, output body, response status or response reading). The title `MERO HTTP v0.3` distinguishes it from the earlier install. Stop closes the current HTTP or TCP connection; Connect restarts a stopped worker; Exit stops the app. Background pause suppresses requests until resume. `Key` is the last keypad code, not part of an exception.

Each snapshot includes configuration/profile/platform/locale, Java heap, Canvas dimensions/color count, last key code, JSR-75/135/82 class-presence results, filesystem/media version properties and command acknowledgement. Class presence does not prove full feature functionality; heap is not physical RAM; Canvas size may exclude system UI areas.

Queue a command from the computer:

    rtk proxy python scripts/http-diagnostics.py --command PING

Available commands: `INFO`, `PING`, `HEAP`, `SCREEN`, `KEY`, `CAPABILITIES`. The app receives a command ID in the HTTP response, processes each ID once, and returns the ID and result in its next upload. `PING` returns `PONG`; other commands acknowledge a fresh diagnostic snapshot. Commands cannot run native shell instructions or change firmware.

The agent can read `logs/http-latest.json` directly. A matching command ID and `PONG` establish an actual two-way application round trip. Native OS and shell access remain separate investigation goals.

## Host validation

Local checks passed for server readiness, invalid-endpoint rejection, malformed/duplicate-field rejection, valid POST/GET diagnostic storage, queued PING delivery and acknowledgement storage. Additional checks confirmed HTML health responses, rejected GET logging and omission of the private URL token from request records. Synthetic diagnostic snapshots were cleared before the handset experiment. This validates the host protocol only; actual Java phone communication remains unconfirmed.

## Verified v0.3 update

The JAD initially failed to transfer; resending succeeded. Both saved files then passed exact-size and full-content Bluetooth readback before requesting installation.

| File | Bytes | Readback SHA-256 |
| --- | --- | --- |
| `MeroHTTP.jar` | 7,761 | `16cee52d694733968d1114cefbea8201bc2d543ed0a22b2a2f0bb734e7fac480` |
| `MeroHTTP.jad` | 329 | `28fb8c08612f66bb4981a4b8297ae79942dcf9b132c05847b9dead42483f2b05` |

A host TCP request matching the new transport received HTTP 200 and a diagnostic command. Packaging checks confirmed socket permission in the manifest and descriptor. These checks do not establish handset socket support or Wi-Fi routing. No handset request was present in the server logs at delivery; The owner subsequently reported TCP failing at `open TCP socket` with `javax.microedition.io.ConnectionNotFoundException` and a socket-open failure message. No handset connection or two-way command round trip is established. Combined with the HTTP response-status failure and observed SIM/WAP-only Java settings, this suggests a Java network-bearer limitation; it does not prove that all Java networking is impossible. The next capability to check is JSR-75 FileConnection for a possible file mailbox carried through native Bluetooth OBEX.

All photographed local diagnostics are transcribed in [screen diagnostics](SCREEN-DIAGNOSTICS.md).
The confirmed FileConnection class/version motivates the [file mailbox experiment](FILE-MAILBOX.md).
