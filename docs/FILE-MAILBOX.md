# Native Bluetooth / Java file mailbox

**Milestone achieved:** a verified PING was read by Java and its matching
PONG acknowledgement was retrieved by the computer through native OBEX FTP.
Incoming command-file acceptance remains manual; this is not unattended
operation, a native shell, or a guaranteed low-latency stream.

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

## v0.2 observed result and v0.3 diagnostic update

The owner launched v0.2, selected E:/, and reported Mailbox ready / Reading
Ebook/command.txt, with no error. A fresh response was retrieved: seq=1,
ack=none, result=startup, heap_free=1792884; other runtime fields matched the
previous startup snapshot. A new OPP PING attempt failed. The original command
remained in Ebook/command.txt at 64 bytes and passed full readback comparison
again. Folder/filename spelling was checked through OBEX, printing only the
app mailbox/inbox entries; no personal file contents were inspected.

Service discovery intermittently returned Unable to find service record.
Explicit use of the previously measured FTP channel 5 allowed successful
command and artifact readbacks. Optional --channel is now available in the
sender/verifier; the mailbox client accepts --ftp-channel and --opp-channel.
These are device-specific measured channels, not universal defaults.

v0.3 adds command_status to the response and phone UI. It reports whether Java
sees a command file and whether its protocol/end marker were recognized.
This avoids interpreting Mailbox ready as successful command reception.
The update was transferred through measured OPP channel 1 and verified through
FTP channel 5 before installation was requested:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 4,422 | dfd88126e4c490b70fc901c9092693a553ff287db66ab65f96ce31978dea9fdc |
| MeroFiles.jad | 342 | 103455e2e68a330522c9e6c026a76a8e7fde47e676fa21bccea79db735c9a421 |

Launch and command_status readback remain pending. PING/PONG is unconfirmed.
Example using this handset's measured service channels:

    rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --ftp-channel 5 --opp-channel 1 --command PING

## v0.3 result and v0.4 inbox probe

The owner launched v0.3 and reported file missing or oversized. The host
retrieved seq=2, ack=none, result=startup, command_status=file missing or
oversized, heap_free=1517412, and the same mailbox/runtime properties as
previous snapshots. The saved 64-byte Ebook/command.txt again passed exact
size and full-content readback, so Bluetooth-side corruption was not observed.
The combined status did not distinguish Java exists() from its size check.

v0.4 separates those checks, reporting inbox_status with the FileConnection
URL, parent-folder existence if the file is missing, and size if it exists.
It also uses the default read/write connection mode instead of explicit READ,
a compatibility experiment based on the working response-file route. This
change is not yet proof of a fix.

Both update artifacts passed full readback before installation was requested:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 4,586 | 1b53ba3a58eb7b984360859e78e4aa35de71494f55ca9273708ddc67e47da7a7 |
| MeroFiles.jad | 342 | 780773bee82d400000669a46bad2aceb8adb51f56aa0fa11d120b2329ead34f6 |

v0.4 launch/readback and PING/PONG remain pending.

## v0.4 result and v0.5 bounded stream read

The owner launched v0.4. Its automated response reported seq=2, ack=none,
result=startup, inbox_status and command_status both `command exists; bytes=64;
url=file:///E:/Ebook/command.txt`, heap_free=1530332. Java now reports the exact
file URL and size; this does not establish that the connection-mode change
caused that visibility, since v0.3 combined missing and oversized cases.

Given those values, the current readCommand code can return null only after
its stream read reaches the 4 KiB safety bound without EOF. This narrows the
next experiment to stream behavior rather than folder naming or transfer
corruption. v0.5 reads exactly the reported fileSize bytes, still rejecting
sizes outside 0..4096 and premature EOF. A nonstandard EOF implementation is
suspected, not yet independently proven.

The first verification connection returned Host is down; a retry succeeded.
Both artifacts passed exact size and full-content readback before installation:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 4,628 | d0d8bb93a634a1c97156a1b5630372a2dd7d5735cb597b67358227486cd87759 |
| MeroFiles.jad | 342 | 05e41a53ef1a5e8e07c2d147889ea8266ced4a3bbf147f7897ceb7846bf5fe93 |

The owner is installing v0.5; command acknowledgement remains pending.

## Permission-lifecycle interruption during v0.5 launch

While installing/launching v0.5, the owner reported SecurityException with
wording: "for midilet state change, user permission confirmation cannot be
continued" (owner transcription). Host Bluetooth polling overlapped this
period and may have contributed to a MIDlet state transition; causality is
not established. The last readbacks still contained the prior v0.4 snapshot.

Do not rebuild or infer missing filesystem support from this exception.
Stop Bluetooth traffic while the owner launches the already verified app,
selects E:/, and completes permission prompts. Resume retrieval only after
the owner confirms readiness. Retry result and PING/PONG remain pending.

## Confirmed two-way milestone

After relaunching verified v0.5 with Bluetooth idle during permission prompts,
the owner reported `read 64 chars; protocol=mero-files/1; end=true`.
The computer retrieved this snapshot through native FTP channel 5:

| Field | Value |
| --- | --- |
| protocol | mero-files/1 |
| seq | 4 |
| ack | Exactly matched the verified command.txt PING ID |
| result | PONG |
| inbox_status | command exists; bytes=64; url=file:///E:/Ebook/command.txt |
| command_status | read 64 chars; protocol=mero-files/1; end=true |
| mailbox | file:///E:/MeroMailbox/ |
| config | CLDC-1.1 |
| profiles | MIDP-2.0 |
| platform | j2me |
| locale | zh-CN |
| heap_free | 1755492 bytes |
| heap_total | 2486656 bytes |
| colors | 65535 |
| fileconnection_version | 1.0 |
| media_version | 1.2 |
| end | 1 |

The host compared ack against the original verified build/command.txt ID and
required result=PONG. This establishes computer-to-phone command delivery,
Java command reading/processing, Java response writing, and phone-to-computer
response retrieval. It confirms that the bounded file-size read works for
this command. It does not independently characterize every stream EOF behavior.

The successful route is OPP command reception in Ebook plus FTP response reads
in MeroMailbox. Keep the phone app running and accept each incoming command
file. Finish Java permission prompts before Bluetooth retrieval; retry transient
connection failures without assuming new files were delivered. INFO can request
fresh automated runtime diagnostics using the same route. Native OS, shell,
USB support, and unattended reception remain separate open questions.

## Fresh INFO command confirmed

With Mero Files v0.5 running, a fresh INFO command was delivered through native
OPP, verified by exact-size and full-content FTP readback, and acknowledged
with matching ID and result=INFO OK. The 64-byte command readback SHA-256 was
04efe20e95ad31b883fbfe3d360dd63d30dcd3a06fa6daa255be6b49b693dba1.

The retrieved snapshot reported seq=9, command_status=accepted INFO,
inbox_status=command exists; bytes=64; url=file:///E:/Ebook/command.txt,
heap_free=1270820 and heap_total=2486656. Runtime/configuration/profile/locale,
mailbox URL, color count and API version properties matched the confirmed
PONG snapshot. The final marker was end=1. This was a fresh command round trip,
not merely rereading the earlier PONG.

Transient OPP/FTP connection failures occurred before this successful run.
The verifier and mailbox reader now retry FTP session creation up to three
times with two-second gaps. Transfer-content mismatches still fail verification.
The mailbox client retains the latest requested command privately in ignored
logs/file-mailbox-command.txt (mode 0600), allowing exact comparison if a
readback connection fails. It does not silently resend commands on connection
failure. Native reception still requires the owner to accept each file.

## v0.6 capability inventory build (delivery pending)

v0.6 extends snapshots with app version, phone clock milliseconds, encoding and
serial-port properties, generic vendor/OS properties, multimedia capture and
encoding properties, optional API class presence, storage roots, and selected
storage total/available/used byte counts. Queries use a fixed metadata allowlist;
no contacts, personal file listing, media capture, native commands, or firmware
writes are performed. Properties are limited to 256 characters with a visible
truncation marker. Unavailable/denied properties are reported individually.

The inventory is collected once at app startup after choosing storage. Storage
capacity and capability fields therefore describe that startup observation;
heap, clock and command acknowledgement are refreshed per response. API class
presence and advertised capture properties do not prove hardware operation or
native shell availability. Generic OS properties may be unavailable or identify
only the runtime. Negative storage counters indicate unsupported/unknown values
and must not be interpreted as measured capacity.

Compilation succeeded, but two send attempts returned Host is down before file
delivery. Artifacts are not yet verified on the phone. Owner was asked to enable
Bluetooth visibility before resending. Keep verified v0.5 available until the
v0.6 update passes full saved-file verification. Do not poll Bluetooth while the
owner launches the new app or completes permission prompts.

### v0.6 verified delivery

After the owner confirmed Bluetooth visibility, another send succeeded. Both
files in Bt passed exact-size and full-content readback:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| MeroFiles.jar | 5,938 | 41a39a0cfe9c9311d19405b4f4d5fe5be8e9a102dc2f5d2fed9789f980362118 |
| MeroFiles.jad | 342 | cfdec032e56a83cffc8e6241e69a2e96903abceadd17da522ccc70d4b8238471 |

The owner was asked to install/launch v0.6 and select E:/, completing permission
prompts while host Bluetooth remains idle. Expanded handset inventory is pending.

### v0.6 actual inventory retrieved

Owner confirmed launch. A complete v0.6 snapshot was retrieved with INFO OK
for the previously saved command. See [every field and its interpretation](CAPABILITY-INVENTORY.md).
Storage capacity and Java serial/capture/API evidence are now recorded;
OS/vendor properties remain unavailable. A passive native SPP connection
succeeded but produced no unsolicited data or shell evidence.


## v0.9 remote file access

OPEN accepts a host-selected file: or gfs: URL (maximum 256 characters), opens
it read-only in an eight-second worker, reports its implementation class, and
lists at most 40 folder entries or reads a bounded file header. FileConnection
headers are limited to the smaller of the reported file size and 64 bytes; other
stream headers are capped at 16 bytes. No file writes or execution are performed.
PATHS no longer assumes an installer slot. A new installation can change that
slot; verify its JAR via native FTP before reading an internal installer URL.

Example (substitute the paired address):

```sh
rtk proxy python scripts/file-mailbox.py PHONE_ADDRESS --command OPEN \
  --url file:///E:/System/Java/ --ftp-channel 5 --opp-channel 1 \
  --permission-wait 15
```

The owner still needs to accept each native OPP command transfer. OPEN DONE means
the request produced observations; inspect path_0_status, exists, error and any
header/listing fields to determine whether access succeeded.

v0.9 compiled and delivered with full saved-size and byte-for-byte verification:
JAR 11,361 bytes, SHA-256
b2a4cb5d550fd7e0c2961555bdc4eab60caa558173fea191bffa6e469b5eae5b;
JAD 380 bytes, SHA-256
972ebb5f70daba6576216811fd94d4598961ceeb9469314a7b5b8b65a589175f.
Live OPEN results are pending.


### v0.9 confirmed operations

OPEN successfully listed E:/System/Java/ (20 entries, not truncated). Native FTP
then located the uniquely sized current JAR automatically, established suite 3
ownership by full-content comparison, and read only its installer metadata.

OPEN gfs://java/3.jar returned ConnectionNotFoundException even with the current
verified suite present. OPEN file:///E:/System/Java/3.jar succeeded, reported
11,361 bytes, and returned a 64-byte header exactly matching the local original.
Thus the ordinary file API provides the working installer-file route; GFS does
not provide a working route in this test. This is read access, not native code
execution or a shell. Future access can use OPEN without another app rebuild.


## v0.10 startup and serial timing

At startup the app reads the saved command ID and skips its execution. Send a
fresh ID after the mailbox is ready. Startup diagnostics can acknowledge that
saved ID with result=startup; only a matching operation result establishes a
new command response. SERIAL now waits up to 90 seconds for port opening and
uses comm:0 without optional flags. For this experiment allow network silence
through the opening window, for example --permission-wait 100 with --timeout 150.
Other operations and their bounds are unchanged. Live serial connectivity is
not yet confirmed.


The host CLI supports --send-attempts 1..6 for transient OPP failures. Retries
reuse the same command ID and exact bytes, preventing a received retry from
starting a second operation. After successful delivery, permission waiting and
full-content readback run once; response-readback failures do not resend a fresh
operation automatically.
