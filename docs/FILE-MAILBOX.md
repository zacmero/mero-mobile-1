# Native Bluetooth / Java file mailbox

The phone's Java Bluetooth API is unavailable and Java HTTP/TCP attempts have
failed. The photographed diagnostics show FileConnection present, version 1.0.
Mero Files tests actual storage access and a two-way mailbox transported by the
phone's native OBEX File Transfer service. This route does not require Java to
open Bluetooth or network connections.

## Phone setup

Build, transfer, and verify before installation:

    rtk proxy python scripts/build.py --app files --java /path/to/bin/java
    rtk proxy python scripts/send-bluetooth.py PHONE_ADDRESS build/MeroFiles.jar build/MeroFiles.jad
    rtk proxy python scripts/verify-bluetooth.py PHONE_ADDRESS --folder Bt build/MeroFiles.jar build/MeroFiles.jad

Require exact saved sizes and full-content readback. Install the verified files,
launch `MERO FILES v0.2`, and allow filesystem access if prompted. The first
screen lists storage roots only. Select the microSD root if identifiable;
otherwise report the offered roots before choosing. The app creates
`MeroMailbox/` under the selected root and shows its full Java file URL.

v0.2 reads only `Ebook/command.txt` and writes only
`MeroMailbox/response.txt` under the selected root. v0.1 originally read commands
inside MeroMailbox, but native FTP uploads failed. It does not list personal files. The response is
overwritten with a fresh snapshot at startup and after each accepted command.
The mailbox is intentionally a dedicated app folder; the existing response.txt in that folder is mailbox data. Ebook/command.txt
is the app command inbox, verified separately; no other ebook files are read.

## Protocol

UTF-8 command files contain `protocol=mero-files/1`, a unique `id`,
`command=PING` or `command=INFO`, and a final `end=1` line. The app polls
every two seconds while running, executes each new ID once, and writes its
ID as `ack`. `PING` returns `result=PONG`; `INFO` returns `result=INFO OK`
with runtime and memory diagnostics. Commands have a 4 KiB bound.

The final marker lets the reader reject incomplete files, and command IDs
distinguish stale responses. A transfer may still race a read; the host must
retry incomplete reads and require the matching acknowledgement. This is
file-based communication with Bluetooth transfer latency and manual incoming-file acceptance, not a shell or
a guaranteed low-latency stream. Each session connects and disconnects normally.

The computer uses the corresponding OBEX folder path, which may differ from
the Java root name. Java response writes, Java command reads, native Object
Push reception, and native OBEX FTP reads must work. API presence alone is insufficient. Handset execution and a
real `PING` / `PONG` round trip are pending.

## Computer operation

After the phone shows Mailbox ready, read its startup response:

    rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --folder MeroMailbox

Then require a matching PING acknowledgement:

    rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --folder MeroMailbox --command PING

By default, the client delivers command.txt through native Object Push,
verifies its content in Ebook by full FTP readback, then polls only response.txt
in MeroMailbox. Accept the phone reception prompt and overwrite the app command
file if offered. The experimental --transport ftp route is retained but timed out
on this phone. A successful OPP command save in Ebook was measured, not guessed. It validates protocol, unique fields,
size bounds, the final marker, and command acknowledgement/result. It saves
the snapshot in ignored logs/file-mailbox-latest.json. Logs may contain private
storage/runtime details; do not commit them. Override --folder if the Java root
maps to a different OBEX subtree. No automatic storage-root guessing is done.

## Delivery result

After the owner toggled Bluetooth on both devices, the next computer-to-phone
transfer succeeded. Both files in Bt passed exact-size and full-content
readback verification before installation was requested:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 4,182 | eb936a9138b35714c55587e023e03cbb4337e49941e11b599991b090cc420f32 |
| MeroFiles.jad | 342 | 63368a1da155f97ae53e00b865e837095220f6ab93bd363ed3e09619defe695e |

Storage-root selection, actual Java file access, and PING/PONG remain pending.

The owner reports the app launched successfully and lists storage root `E:/`.
The expected Java mailbox URL after selection is `file:///E:/MeroMailbox/`.
The first host attempt to enter `MeroMailbox` through OBEX returned `Not Found`;
root selection and the Mailbox ready screen still need confirmation.

## First actual filesystem result

The owner selected `E:/` and confirmed Mailbox ready. The host then retrieved
`MeroMailbox/response.txt` through native OBEX FTP. This establishes Java
filesystem writes and computer-side Bluetooth reads of those files, with the
OBEX root mapping to the Java `E:/` storage root for this experiment.

The automated startup snapshot contained:

| Field | Value |
| --- | --- |
| protocol | mero-files/1 |
| seq | 1 |
| ack | none |
| result | startup |
| mailbox | file:///E:/MeroMailbox/ |
| config | CLDC-1.1 |
| profiles | MIDP-2.0 |
| platform | j2me |
| locale | zh-CN |
| heap_free | 1798148 |
| heap_total | 2486656 |
| colors | 65535 |
| fileconnection_version | 1.0 |
| media_version | 1.2 |
| end | 1 |

The first command-file FTP PutFile attempt failed with a transfer error;
the host OBEX log reported a timeout waiting for response. The retry also failed with a transfer error; the owner was asked whether a
file/access prompt appeared. This is not yet a
successful two-way command exchange. Do not confuse the startup response with
a PING acknowledgement.

## v0.2 command inbox workaround

The owner confirmed the native FTP receive prompt appeared but the download
failed; Mero Files remained ready. Native Object Push then delivered the same
64-byte command successfully. Full FTP readback verified it in Ebook with
SHA-256 b4785fcb76d32dc13a57b85214073234a5382f499baaed58d7259f2834c205a3.
The command is bounded diagnostic data, not executable Java or native code.

v0.2 reads Ebook/command.txt and keeps responses in MeroMailbox. Its artifacts
were transferred and fully verified before requesting installation:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 4,193 | a4a34c989a725af5b60dd8bf13d499a7d6a3769ff97285cf5fb5e965f0ca23bf |
| MeroFiles.jad | 342 | c6033da45ce642e85f6e920765f899012b2eb1d92b7c857b61440fb01d8a28dd |

The v0.2 launch and matching PONG readback remain pending. Ordinary reconnects
between separate OPP/FTP sessions are expected. Reception prompts still require
the owner; fully unattended command delivery is not established.
