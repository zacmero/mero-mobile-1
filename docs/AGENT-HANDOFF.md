# Pair-coding agent handoff

## Assignment
You are helping with **mero-mobile-1**, a playful hardware archaeology and Java ME learning project built around the **Powerpack GSTWF-4012** four-SIM feature phone. The user is on **Arch Linux**, works terminal-first, values practical code and wants to understand **Java, embedded systems, and what actually runs behind old phone UIs**. Explain small concepts when they become useful; prioritize repeatable experiments over speculative deep dives.

## Facts already confirmed by owner
- Java menu with **Application manager**, **Local install**, **Download** and SIM-related connection settings.
- Wi-Fi and phone-browser internet access work. Bluetooth pairing and file transfer to microSD succeeded.
- Working radio and television functions in stock UI.
- Two low-resolution cameras (main + top-facing).
- Four-SIM form factor.
- Connecting USB has **not yielded a mounted phone/card** on Linux. USB enumeration itself has *not* been established.
- Mero Hello installed and launched. Runtime reports configuration `CLDC1.1`, profile `MIDP-2.0`, platform `j2me`, locale `zh-CN`; heap free 1,846,308 bytes and total 2,486,656 bytes in one observation.
- Exact OS, SoC, physical RAM, storage map, native shell remain unknown. Photographs establish FileConnection and multimedia class presence, but actual API functionality remains unconfirmed. Java heap values are not physical RAM measurements.

## Instructions
1. Begin with docs/RECON-001.md and extend docs/HARDWARE.md using only measured/owner-observed facts.
2. Distinguish physical USB detection, interface enumeration, driver binding and mounted filesystems.
3. Investigate phone Java Local install and microSD reader route; Bluetooth file transfer is a fallback **only if supported**.
4. Mero Hello builds with `scripts/build.py` and has run on the handset. Keep subsequent probes small; do not infer optional APIs from successful installation.
5. Confirm CLDC/MIDP/packaging before wiring up an Arch build. Java ME often requires old bytecode and preverification.
6. Give micro-lessons: MIDlet lifecycle, events/commands, constrained heap, JAR/JAD, Java GCF, optional JSRs.
7. Treat a native OS console as **a separate hypothesis**. Java support does not imply Linux, Android or WinCE, nor does a modem serial port imply a shell.
8. Preserve original functionality. No factory reset, reflashing or hardware modifications during initial reconnaissance.
9. Repo is public: redact IMEI, full MAC addresses when unnecessary, contacts, passwords, SIM data and personal files.
10. Prefer one small documented experiment at a time; finish with observed result, explanation and next step.
11. **Owner requirement: verify the received file's exact byte size against the source before every installation or execution.** A first app transfer was truncated/corrupted despite host-side completion reports. Bluetooth or HTTP success is not evidence of an intact saved file. Rounded KB values are insufficient; if exact size cannot be checked, keep installation/execution pending. A matching size detects truncation but does not establish byte-for-byte integrity; compare a checksum too when feasible.
12. OBEX FTP readback verification works: `scripts/verify-bluetooth.py PHONE_ADDRESS --folder Bt LOCAL_FILES`. Use it after every artifact delivery. Mero Link was delivered and verified (5,392-byte JAR, 302-byte JAD), then launched through JAD and JAR. Both reported Bluetooth unavailable/ClassNotFoundException for the attempted `javax.bluetooth.LocalDevice`. No Java RFCOMM listener started; native OBEX still works. `Key: 0` is the app's initial keypad value. See `docs/BLUETOOTH-LINK.md`; Java HTTP/TCP experiments subsequently failed; the next route is a JSR-75 file mailbox over native Bluetooth.
13. HTTP server/client exist; see `docs/HTTP-LINK.md`. Phone browser reached the LAN server, but Java v0.2 GET failed at response status with IOException; v0.3 TCP failed at open TCP socket with ConnectionNotFoundException. Observed Java settings expose SIM/CMCC WAP/MMS profiles with no WLAN choice. No handset upload or command round trip is established. v0.3 was fully readback-verified (7,761-byte JAR, 329-byte JAD). The LAN firewall rule expires after one hour.
14. All owner-photographed diagnostics are transcribed in `docs/SCREEN-DIAGNOSTICS.md`, including exact heap, Canvas, key, counters and API/version values. JSR-75=true, JSR-135=true, JSR-82=false; FileConnection version 1.0 and media version 1.2. Presence is not a functional or permission test.
15. `MeroFiles` and `scripts/file-mailbox.py` implement a dedicated MeroMailbox folder with bounded PING/INFO command and response files. See `docs/FILE-MAILBOX.md`. Build succeeded (4,182-byte JAR, 342-byte JAD), but initial Bluetooth attempts timed out or returned OBEX Connect 0x40. A later retry after Bluetooth toggles succeeded: both files in Bt passed exact-size and full-content readback. Installation was requested; storage roots and actual file access remain pending. Ask the owner to exit the previous app and restore Bluetooth visibility; never install unverified files. Select the actual storage root, then map its mailbox to the OBEX path before writing commands.

## First success criteria
- OS/firmware evidence and actual USB behavior captured (even if no device detected).
- A viable program transfer route established.
- Java MIDlet installer expects known file format(s).
- An offline Mero Hello MIDlet launches, or an exact reproducible blocker is documented.

## Next experiments
- Owner reaffirmed that identifying the native OS and investigating genuine shell access are main goals, alongside making the phone useful to this computer. Treat Java diagnostics as an evidence-gathering route, not a promise of native access.
- Next live communication route: the dedicated JSR-75 file mailbox carried through native OBEX FTP. Java HTTP/TCP failed on this handset; a separate Java bearer limitation is suspected, not proven. Standard Java ME file access does not establish control of USB enumeration or native OS access.
- Native Bluetooth Serial Port `sprd_com3` (RFCOMM channel 3) remains a distinct candidate for protocol identification. Do not call it a shell or send guessed vendor/service commands without identifying the protocol.
- Display and input measurement, heap usage, optional APIs.
- LAN text fetch over Java if networking permissions/API permit it.
- Media, Bluetooth and file storage only where the runtime genuinely supports them.
- Separate deeper board/native OS study once enough evidence exists.

## Starter message for user/agent
Start RECON-001. Compare USB events before/after plugging the phone in with a known data cable, inspect Java menu details and Local install, then determine how to transfer a tiny MIDlet. Keep an evidence table and teach the Java concepts as we encounter them. Do not guess the OS or promise a shell.

## Current mailbox observation

Owner selected E:/ and reported Mailbox ready. Native OBEX retrieved the Java-written
MeroMailbox/response.txt startup snapshot; Java storage writes and Bluetooth reads
are proven. Initial FTP command PutFile timed out; PING acknowledgement is not yet
proven. See FILE-MAILBOX.md for the full automated snapshot and pending retry.

## Command delivery workaround

Native FTP PutFile showed a phone receive prompt but failed twice. Native OPP
delivered a 64-byte PING command into Ebook; full readback verified it. Mero Files
v0.2 now reads Ebook/command.txt, writes MeroMailbox/response.txt. The updated
4,193-byte JAR and 342-byte JAD were fully verified in Bt. Owner was asked to
install v0.2 and select E:/; matching PONG is pending. file-mailbox.py defaults
to OPP command delivery followed by readback verification and response polling.
Incoming-file acceptance remains manual. No unattended or low-latency claim.

## Latest mailbox delivery

v0.2 launched but only startup response was retrieved; no error on phone, no
command acknowledgement. Ebook/command.txt spelling/content verified again.
v0.3 adds command_status diagnostics and was fully readback-verified in Bt
(4,422-byte JAR, 342-byte JAD). Owner was asked to install/select E:/.
Use measured FTP channel 5 / OPP channel 1 to bypass intermittent SDP failures:
sender/verifier --channel; mailbox --ftp-channel / --opp-channel.

## v0.4 delivery

v0.3 reported file missing or oversized, confirmed by automated seq=2 response.
The 64-byte command in Ebook still matched original full contents. v0.4 adds
inbox_status (exact URL, missing file vs size, parent existence), changes the
inbox connection to default READ_WRITE as a compatibility experiment. The
4,586-byte JAR and 342-byte JAD were fully verified before installation was
requested. Wait for owner to launch v0.4/select E:/, then read via FTP channel 5.
Two-way PING remains unconfirmed; do not treat readiness as an acknowledgement.

## v0.5 delivery

v0.4 response reports command exists, bytes=64, exact URL E:/Ebook/command.txt
but ack=none. Source narrows null result to stream bound reached without EOF.
v0.5 reads exactly fileSize bytes with a 4 KiB bound and premature EOF rejection.
4,628-byte JAR and 342-byte JAD were fully verified (first connection failed,
retry passed). Owner says will install now; await readiness and retrieve response.
Do not claim PONG until its ack matches the verified command ID.

## Permission prompt sequencing

Owner reported SecurityException during v0.5 launch: MIDlet state change
prevented user permission confirmation. Host polls overlapped installation/launch
and may have contributed; not proven. No more Bluetooth operations until owner
relaunches verified v0.5, selects E:/, completes file-access prompts and confirms
readiness. Last readback was the old v0.4 snapshot; no v0.5 PONG observed.

## Achieved: verified two-way Java file mailbox

Owner relaunched verified v0.5, completed permissions, and selected E:/ with
Bluetooth idle. Java reported read 64 chars, protocol=mero-files/1, end=true.
Host retrieved seq=4, result=PONG, and ack exactly matching the original verified
PING command ID. Command route is native OPP -> Ebook/command.txt; response is
Java -> E:/MeroMailbox/response.txt -> native FTP channel 5 -> host. See complete
snapshot in FILE-MAILBOX.md. Incoming-file acceptance remains manual. Java file
read/write and the actual two-way command round trip are now proven. Preserve
v0.5: 4,628-byte JAR, 342-byte JAD; verify every new delivery before execution.
No native shell/OS or unattended reception has been established.

## Fresh INFO achieved

A new 64-byte INFO command passed full readback and returned matching ack /
INFO OK, seq=9, heap_free=1270820. This confirms fresh command processing
beyond the first PONG. Host scripts now retry FTP session creation three times
and retain ignored/private logs/file-mailbox-command.txt for failed-readback
recovery. Owner acceptance is still needed per incoming file; no unattended
operation or native shell claim.

## v0.6 built, not delivered

Owner asked to continue. v0.6 adds a fixed metadata capability/property inventory
and selected-storage capacity counters, cached at startup; clock and heap are
fresh per response. Built successfully. Two OPP attempts failed Host is down
before delivery. Await phone Bluetooth on/visible confirmation, resend and
fully verify before installation. v0.5 remains the proven working app.

## v0.6 now verified

Retry succeeded after owner confirmed visibility. Both files in Bt verified
byte-for-byte: JAR 5,938 bytes, JAD 342 bytes. Owner was asked to launch v0.6
and select E:/; keep Bluetooth idle until readiness confirmed. Then retrieve
expanded metadata via file-mailbox.py --ftp-channel 5 (no command needed).

## Latest measured capabilities

Verified v0.6 launched and its complete inventory was retrieved. See
CAPABILITY-INVENTORY.md for every field. E:/ storage: total 987480064 bytes,
available 958971904, used 28508160. CommConnection loads; commports=0.
Media controls load but capture/recording properties are false. PIM version
1.0 reported despite PIM class load failure. OS/vendor properties unavailable.
Host passively connected native RFCOMM channel 3; no unsolicited data in
eight seconds, zero application bytes sent. No console/shell/protocol identified.
Do not send guessed native service commands; Java comm port 0 remains an
unproven candidate, not a demonstrated connection. v0.6 is the current app.

## Current native-access experiments

Owner authorized steps 1/2 serial identification followed by continuous USB
cold-boot monitoring, with board inspection deferred. See NATIVE-ACCESS.md.
Native SPP channel 3 refused current connections; no AT query delivered.
Verified v0.7 (8,500-byte JAR, 379-byte JAD) ran SERIAL; matching ack returned
SERIAL DONE, serial_status=timeout, serial_stage=open comm:0. No serial port
opened. Relaunch before repeating to avoid accumulating a blocked native open.
USB watcher is active as exec session 18312 and records logs/usb-events.jsonl
continuously. Power-off/USB-reconnect showed charging and no USB events.
Owner was asked to try holding centre/OK on reconnect; await that result.
No board work, firmware write, or loader execution has been performed.

## Latest battery/label evidence

Owner completed centre/OK and battery-removal/reinsertion steps: no response,
zero USB events in continuous monitoring. Without battery the phone does not
turn on in their tested setup; it operates only with battery installed.
Board-covering label reports model N2322. Full owner-supplied SN and IMEI are
in private/DEVICE-LABEL.md (ignored, 0600); never stage/repeat those publicly.
Exterior name remains Powerpack GSTWF-4012; exact chipset/OS still unknown.
Owner may remove label/photograph board later; do not shift to hardware now.
USB watcher session 18312 remains active. Other boot-key/cable routes are not
proven exhausted.

## Current phase — supersedes earlier active/pending state

- Installed app: Mero Files v0.10. Both artifacts passed exact saved-size and full-content readback before installation: JAR 11,457 bytes, JAD 381 bytes. Fresh verified SERIAL command returned matching app_version=0.10 and timeout at open comm:0. No Java serial port opened.
- Working route: native OBEX file mailbox, E:/Ebook/command.txt to E:/MeroMailbox/response.txt. Incoming acceptance remains manual. Same-ID OPP retries are available. Preserve full readback verification before installation/execution.
- Java can list E:/System/Java and read this project's installed JAR. Suite IDs change across updates; use full JAR ownership verification before reading only owned installer metadata. Current-suite gfs access failed. Aplix FileConnection package is observed; OS/chipset remain unknown.
- Native HFP answered service initialization/status commands; identification variants returned ERROR. This is limited AT access, not a shell. HFP channel changed from 4 to 7 after pairing. Interactive console attempts used the stale channel and were refused; the console remains unverified.
- USB monitoring is stopped. Bluetooth serial experiments are stopped at the owner's request and the host SPP server is closed. Do not resume these routes without new owner direction. Hardware inspection remains deferred.
- Current direction: native Wi-Fi browser. The Python HTTP server is running on 192.168.1.97:8765; `/link` provides HTML and `/link.wml` WML, computer-time replies and bounded message echo. Request metadata and received messages stay in ignored logs. No phone visit or browser message round trip has yet been confirmed in the current logs.
- Next concrete action: open http://192.168.1.97:8765/link in the phone's native browser, send a short message and inspect incoming request metadata. Try /link.wml if needed. A prior one-hour LAN-only firewall rule may have expired; check it if the phone cannot reach the server.
- Owner explicitly requested tracking Serena project configuration and all three Planning with Files files in this milestone. Serena cache/local overrides, build artifacts, raw logs and private device identifiers remain excluded.
- No OS shell, bootloader version, firmware memory access or loader execution has been established. Exact SN/IMEI remain in ignored private/DEVICE-LABEL.md; never copy them into tracked files.

## Latest: native Wi-Fi browser confirmed

A real message reached the computer from phone IP 192.168.1.77 via
http://192.168.1.97/link; HTTP status was 200. The owner reported entering 197
instead of 192 during earlier failures. Do not claim a browser custom-port
restriction or that Java's networking issue is resolved.

Current native-browser User-Agent is Dorado WAP-Browser/1.0.0, with WAP profile
http://www.spreadtrum.com/wap/6600L_DORADO_UAProfile.xml. This is a useful vendor
clue, not a demonstrated SoC or OS identity. Profile retrieval is pending.
Direct port-80 server is transient systemd unit mero-phone-page.service; it runs
as zacmero with CAP_NET_BIND_SERVICE. Its phone-IP-only firewall rule expires
after one hour. Previous port-80 redirect was removed. Port-8765 server remains
separate. Private browser message/request logs are ignored. No shell obtained.

## Inbox update awaiting deployment

scripts/http-diagnostics.py now provides /link/inbox, /link/inbox.wml, --message
and --inbox. Private SQLite history retains 100 messages; the phone displays six.
Refresh is configured for two seconds, with manual SYNC fallback. Sending a
message leaves the phone on compose; return to RX for updates. A follow-up
request acknowledges only the computer IDs included on the previous inbox page.
The user's desired aesthetic is sparse, dark, monospace and cryptic RX/TX text.

The first computer message is queued. Restart of mero-phone-page.service needs
Linux desktop authentication; the old process was still serving when checked.
Deployment and live auto-refresh/acknowledgement remain pending. Do not claim
fast polling is confirmed before genuine requests and delivery acknowledgements
appear. No phone JAR/JAD update is needed for this browser feature.

## Current: automatic browser inbox is live

The service restart completed. Genuine phone requests acknowledged computer
message #1, submitted #2 "hello ghost", and acknowledged computer reply #3.
Automatic refresh is confirmed: initial two-second delay yielded about 3.2-second
request gaps; the updated one-second delay yields about 2.35 seconds. Reply #3
queue-to-follow-up acknowledgement was 5.659 seconds across the update, not
measured display latency. Old pending-deployment statements are historical.

Use http://192.168.1.97/link/inbox on the phone. Keep RX open for incoming
messages; TX opens compose without automatic refresh, then return to RX.
Send with scripts/http-diagnostics.py --message and inspect with --inbox, always
RTK-prefixed. SQLite history is private/ignored. The user's requested styling
is now pure white text/links on black with monospace and cryptic RX/TX labels.
HTML body attributes are the fallback; input CSS/WML appearance may depend on
browser support. Port-80 firewall authorization is still time-limited.
No native OS shell or exact chipset identity has been obtained.

## Current native-access evidence

The owner prioritizes learning/native shell access and asked to stop appearance
work. White-on-black works in Firefox but not on the phone. No About/Version UI
exists in menus the owner checked; do not repeat that request. Native Wi-Fi
connect checks refused all 22 common service ports. Full TCP scan was stopped
incomplete after slow progress and increased phone latency, not a complete
negative scan. A fresh native FTP root has 11 entries and rejects parent
navigation; metadata only was inspected. No firmware tree or Device ID clue
was exposed.

Matomo's maintained OS regex maps Dorado WAP-Browser to Mocor OS, strengthening
a Mocor-family hypothesis, while exact chipset/firmware remain unknown. The
Spreadtrum UA profile cannot currently be retrieved and has no snapshot in the
archive availability response. Candidate next software route: check whether a
native application runtime such as MRP is actually supported. Public Mythroad
SDK sources exist, but no runtime support or executable compatibility has been
demonstrated on this phone. No native package or loader has been executed.
The optional /link/probe browser page is deployed, but no phone callback has been
captured and it cannot access native files or execute OS commands.

## Latest menu/label photos

IMG_8381–IMG_8384 were inspected; see MENU-PHOTOS.md. Exact photographed label
is Powerpack 4-GSTWF-4012, Model:N2322. The leading 4- is now confirmed; earlier
shorter references are historical. Originals remain outside Git, especially the
label photo containing SN/IMEI. No chipset is visible. Clock date 01.01.2011
must not be treated as a firmware build. Multimedia > Games is highlighted but
not opened. Requested the next submenu photo via RX and the user question tool.
Native application runtime support remains unconfirmed.

## Latest Games/app inventory clarification

Owner opened Games: only Sokoban. Java is the only visible installer. No native
launcher, chipset or version info is exposed. Twitter/eBuddy/MSN/Facebook/Yahoo/
TV/FM are menu entries without visible versions; their native-versus-web nature
is unknown. Do not request the Games submenu again or assume MRP compatibility.
App-bundle searches yielded no reliable exact-firmware match. Strongest current
OS hypothesis is Mocor-family based on Dorado, Spreadtrum profile and native
sprd service clues plus Matomo's OS classifier; exact kernel/chipset/build and
shell availability remain unconfirmed. See NATIVE-ACCESS.md research limits.

## Software/physical feasibility clarification

Owner supplied a broad Powerpack/Spreadtrum overview. Correct interpretation:
our sprd_com3 is a Bluetooth SDP name; USB never enumerated in the tested
operations. Upstream tools support specific chips, not an established match to
this phone's 6600L profile clue. FPDoom proves native RAM loading on supported
devices; SD boot requires a firmware dump/installed patch first. No stock shell
or native execution is established here. Chip-marking photos could identify the
actual target without soldering; connector/UART intervention might be needed
later. Physical access is not proven mandatory. Keep firmware/loader operations
pending an actual compatible target and usable transport. USB watcher remains
stopped. Sources and detailed scope are in NATIVE-ACCESS.md.

## Mythroad (MRP) Native Execution Milestone

Dialer testing without a SIM card confirmed the active Mythroad runtime:
- `*#06#` displayed the IMEI, confirming active local MMI evaluation.
- `*#0000#` returned "not exist", confirming command interception against an unpopulated firmware release field.
- `*#220807#` invoked the native Mythroad launcher ("waiting" scanning `E:/` for `mythroad/dsm_gm.mrp`).
- `*#777755999#` returned `"ziyout L6320"`, confirming the internal platform build tag.

Verified reference artifacts are staged in `mrp/`:
- `mrp/DSM_GM.mrp` (41,315 bytes, SHA-256: `e9e3b13c1de8829109a06e47febecb24922beee125577d422f82a88fa1ac7a75`)
- `mrp/helloworld.mrp` (8,354 bytes, SHA-256: `ddb0d7e92411a357dfacb5edf3ffedb11ec36afe6002a6ea9e55371d7bab4fe0`)
- `mrp/mpc.mrp` (147,505 bytes, SHA-256: `1a734fca1b55bf811fda38b37162ce2c7c4e6ec02efab51b8a1c70afb9db195c`)

Next session step:
Place `DSM_GM.mrp` (and `dsm_gm.mrp`) plus `helloworld.mrp` in `E:/mythroad/` on the microSD card and dial `*#220807#` to launch the native menu and execute native ARM code.
