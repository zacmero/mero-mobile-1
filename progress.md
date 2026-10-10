# Progress

- Read build, sender and handoff. Downloaded compilation-only BlueCove API library into the external tool cache.
- Implementing the phone probe and host link next.
- Added optional Bluetooth helper, diagnostic Canvas and line-based INFO/PING/HEAP/SCREEN/KEY commands; added host SDP discovery and RFCOMM client with a private local log.
- Compilation/preverification succeeded. JAR contains only three app classes and manifest, all class version 45.3 with CLDC StackMap names. Exact current artifact sizes: JAR 5,392 bytes; JAD 302 bytes.
- ProGuard noted duplicate API definitions in the desktop BlueCove compilation library; app output does not bundle that library.
- Delivery started. Saved-size verification and handset Java Bluetooth support are pending.
- Both deliveries completed. Implemented read-only OBEX FTP verifier; both saved files passed exact-size and full-content readback comparison. User was then instructed to install/launch. Java Bluetooth support is awaiting that observation.
- SDP parser read the phone's recorded serial-service response correctly (channel 3) and rejected a truncated record.
- Handset launch confirmed through both JAD and JAR. Both reported Bluetooth unavailable/ClassNotFoundException for LocalDevice. Documented measured limitation and retained working native OBEX verification route. Explained source/JAR/JAD roles. Bluetooth-first delivery complete; live Java connection was not achieved.
- Committed and pushed the verified Java/Bluetooth milestone as `425f166`.
- Added Mero HTTP client and LAN diagnostic server, command queue, bounded messages and a private per-server endpoint. Local protocol checks passed for authentication, malformed requests, diagnostics, command delivery and acknowledgement; cleared synthetic logs before the phone test.
- HTTP build compiled/preverified: JAR 6,061 bytes; JAD 290 bytes. Bluetooth delivery started; saved-file verification and actual Java Wi-Fi routing remain pending.
- Both HTTP artifacts were delivered. First JAR readback reported an OBEX error; retry with discovery stopped verified both exact sizes and full contents. Matching SHA-256 values are recorded in HTTP-LINK.md. Owner was then instructed to launch and allow networking.
- v0.1 handset launch produced java.io.IOException. Owner reconnected Wi-Fi and downloaded the LAN server's browser health response, establishing browser reachability. Found active public-zone firewalld and added a one-hour source-LAN-only TCP 8765 rule.
- Fixed missing browser/rejection logs; health page is HTML. Added GET diagnostics and v0.2 error-stage UI/GET-POST selection. Local GET protocol/command/rejection/redacted-log checks passed. v0.2 artifacts: JAR 6,846 bytes, JAD 290 bytes; delivery started.
- v0.2 delivery and full-content readback succeeded for both artifacts. User was instructed to install the update and report its GET failure stage; waiting for handset observation. No live Java diagnostic snapshot is present yet.

## Current phase — 2026-10-10

The preceding entries are historical. Current state supersedes their pending-delivery and active-monitor statements.

- v0.3 Java TCP failed at socket opening. Native-browser reachability was owner-reported; a genuine browser request has not yet been captured in the current logs.
- Built, delivered and fully verified successive Mero Files versions. Established the OBEX file mailbox and retrieved matching PING and diagnostic responses directly.
- v0.6 returned runtime/API/storage inventory. v0.7 serial opening timed out; continuous USB boot/battery observation recorded no events. Stopped USB monitoring at the owner's request.
- v0.8 identified the Aplix FileConnection implementation and E:/ root. v0.9 listed System/Java and read this project's installed JAR header. Current-suite GFS and parent traversal probes failed. Installer slots changed; full JAR verification now precedes owned metadata reads.
- Native HFP returned BRSF/CIND/CMER AT responses, while identity queries returned ERROR. Native SPP and coordinated Java/host serial attempts did not establish a data link. No shell or firmware access was obtained.
- Implemented a paired-device host SPP listener. Fixed a silent channel-bind failure using channel 22 and an advertisement check. Fresh legacy pairing completed, but no Java peer connected.
- v0.10 passed full readback (JAR 11,457 bytes, JAD 381 bytes), was installed and returned a matching fresh SERIAL response: timeout at open comm:0. Same-ID OPP retries were committed and pushed as 2104c27.
- Added a restricted interactive native AT console; live console attempts on the previously observed HFP channel were refused. Later discovery reported a changed HFP channel. The console remains unverified.
- Owner stopped the Bluetooth serial route. Closed the host SPP listener and switched to the native Wi-Fi browser. Added HTML/WML pages, computer-time replies, bounded message echo and request-header capture to the LAN server; compiled and started it on 192.168.1.97:8765. A live phone visit remains pending.
- Owner requested committing the entire current phase, explicitly including Serena configuration and all planning files. Updated findings, plan and handoff for that snapshot; commit/push result will be reported after Git completes.

## Native-browser message confirmed

The owner sent a message through http://192.168.1.97/link. The computer recorded
it from the phone's confirmed IP 192.168.1.77 and returned HTTP 200. The owner
explained that earlier requests used 197 instead of 192. Do not attribute those
timeouts to custom-port incompatibility. Real browser metadata identifies
Dorado WAP-Browser/1.0.0 and a Spreadtrum 6600L_DORADO UA profile URL; exact
chipset/OS remain unknown.

The server now runs directly on port 80 as transient systemd unit
mero-phone-page.service, under zacmero with CAP_NET_BIND_SERVICE. A one-hour
firewall rule permits port 80 from the phone's IP only. The previous port-80
forwarding rule was removed. The port-8765 server remains running separately.

Documented the confirmed browser milestone and reproducible port-80 service/firewall commands. Attempts to retrieve the reported Spreadtrum UA profile failed at hostname resolution; chipset identity remains unconfirmed. The next useful deliverable is a browser-compatible computer dashboard and bounded two-way message inbox, using explicit refresh before assuming automatic polling support.

## Two-way inbox implementation

Added persistent bounded SQLite messages, computer --message / --inbox commands,
phone message IDs, follow-up request acknowledgements, HTML meta-refresh and WML
timer inboxes with manual SYNC fallback. Compose stays separate from polling.
Preserved the owner's requested sparse, cryptic old-school style. Python source
compiled; no automated tests were added or run. Queued the first real computer
message. Deployment restart awaits desktop authentication; the old service still
returned Not found for /link/inbox. Live automatic refresh and delivery checks
remain pending.

## Inbox deployed and live

Desktop authentication completed and the updated port-80 service restarted.
The phone acknowledged computer message #1, sent #2 "hello ghost", and later
acknowledged fresh reply #3. Automatic requests initially arrived about every
3.2 seconds. Changed the refresh delay to one second; successful phone requests
then arrived about every 2.35 seconds. Updated the requested style to white text
and links on black, with optional inline CSS for input fields. The measured
5.659-second reply acknowledgement spans the update and is not screen latency.
No phone binary update was needed. Source compilation and live phone checks
were performed; no automated tests were added or run.

## Native investigation resumed

Stopped visual adjustments after owner confirmed Firefox applies colors while
the phone does not. Added optional bounded read-only browser reporting at
/link/probe; compiled and restarted the service. User prioritized shell/native
access, so no phone probe-page run was requested. Connect-only scan of 22 native
TCP service ports returned refusal for all. Started a rate-limited full TCP scan.
Research found Matomo's Dorado-to-Mocor classifier rule; this narrows the platform
hypothesis without confirming hardware. Archived UA profile lookup found no
snapshot. Sent About/Version instructions through RX; phone acknowledged them.

Full TCP scan stopped incomplete after about 2.5 minutes; progress was only about
8% and ping latency increased. No exhaustive negative result is claimed.
Owner reports no About/Version screen anywhere in the menus. A fresh native FTP
session listed 11 root entries, rejected parent navigation and reset to the same
root. Only metadata was read; no firmware exposed. Cached Device ID is absent.
Research found Mythroad native-app SDK sources as a possible additional route;
phone runtime support is unconfirmed. Visual adjustments remain stopped.

Inspected all four new owner photos. Transcribed the visible menus and non-sensitive label fields in docs/MENU-PHOTOS.md. Corrected exact commercial label to 4-GSTWF-4012 and visually corroborated N2322. Requested the submenu after pressing OK on Multimedia > Games; current photos stop one level above it. Originals, SN and IMEI remain outside tracked documentation.

Owner confirmed Sokoban is the only game and Java is the only visible installer. Recorded social/media menu inventory. Searched Sokoban/eBuddy/Spreadtrum/Mocor combinations through web and fallback endpoints; no reliable exact-model firmware source found. Recorded provider failures and kept Mocor classification as a hypothesis. No native runtime compatibility or shell was established.
