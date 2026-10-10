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
launch `MERO FILES v0.1`, and allow filesystem access if prompted. The first
screen lists storage roots only. Select the microSD root if identifiable;
otherwise report the offered roots before choosing. The app creates
`MeroMailbox/` under the selected root and shows its full Java file URL.

The app accesses only `MeroMailbox/command.txt` and
`MeroMailbox/response.txt`. It does not list personal files. The response is
overwritten with a fresh snapshot at startup and after each accepted command.
The mailbox is intentionally a dedicated app folder; existing files bearing
these two names in that folder are mailbox data.

## Protocol

UTF-8 command files contain `protocol=mero-files/1`, a unique `id`,
`command=PING` or `command=INFO`, and a final `end=1` line. The app polls
every two seconds while running, executes each new ID once, and writes its
ID as `ack`. `PING` returns `result=PONG`; `INFO` returns `result=INFO OK`
with runtime and memory diagnostics. Commands have a 4 KiB bound.

The final marker lets the reader reject incomplete files, and command IDs
distinguish stale responses. A transfer may still race a read; the host must
retry incomplete reads and require the matching acknowledgement. This is
file-based communication with Bluetooth transfer latency, not a shell or
a guaranteed low-latency stream.

The computer uses the corresponding OBEX folder path, which may differ from
the Java root name. Both the Java write and the OBEX read/write permissions
must work. API presence alone is insufficient. Handset execution and a
real `PING` / `PONG` round trip are pending.

## Computer operation

After the phone shows Mailbox ready, read its startup response:

    rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --folder MeroMailbox

Then require a matching PING acknowledgement:

    rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --folder MeroMailbox --command PING

The client uses FTP PutFile into the mailbox, verifies command content by full
readback, then polls only response.txt. It validates protocol, unique fields,
size bounds, the final marker, and command acknowledgement/result. It saves
the snapshot in ignored logs/file-mailbox-latest.json. Logs may contain private
storage/runtime details; do not commit them. Override --folder if the Java root
maps to a different OBEX subtree. No automatic storage-root guessing is done.
