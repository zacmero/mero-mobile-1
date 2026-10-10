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
