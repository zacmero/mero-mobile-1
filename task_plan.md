# Phone software investigation

Goal: make this phone useful to the computer through a verified two-way link and investigate native access. Native OS and shell access remain unconfirmed.

## Completed evidence

- [x] Compile and deliver working CLDC/MIDP apps; require exact saved size and full-content readback before installation.
- [x] Identify missing Java JSR-82 and observed Java HTTP/TCP failures.
- [x] Establish a native Bluetooth OBEX file mailbox with matching command acknowledgements.
- [x] Retrieve runtime, display, storage and API diagnostics directly through the mailbox.
- [x] List System/Java and read this project's installed JAR through Java FileConnection; verify ownership before reading installer metadata.
- [x] Test fixed roots, current-suite GFS and parent traversal; record actual failures.
- [x] Observe USB continuously during owner-operated boot/battery experiments; stop monitoring at the owner's request.
- [x] Test native SPP, fresh pairing, a host SPP listener and Java comm:0. No Java serial link established.
- [x] Obtain native HFP AT responses; identification commands failed and no shell was obtained.
- [x] Verify and install Mero Files v0.10. Its fresh SERIAL command timed out at open comm:0 after the longer opening window.
- [x] Stop Bluetooth serial experiments at the owner's request and implement a native-browser HTML/WML LAN page.

## Current phase

- [x] Open the LAN page in the native Wi-Fi browser and capture its real request metadata; direct port 80 succeeded.
- [x] Confirm a phone message and an HTTP 200 computer response.
- [x] Implement a bounded persistent two-way inbox with computer CLI, separate compose page and one-second HTML/WML refresh requests.
- [x] Complete the authenticated service restart and confirm genuine phone acknowledgements and automatic polling, about 2.35 seconds between requests.
- [ ] Obtain native OS/shell access, if a supported route can be identified.

The native-browser message reached the direct port-80 server. Earlier failures used 197 instead of 192, according to the owner. Do not restart USB monitoring or Bluetooth serial retries without new owner direction. Board inspection is deferred.

Constraints: prefix shell commands with RTK; keep device identifiers, endpoint tokens and raw logs private; never execute a delivered artifact before exact-size and full-content verification. No firmware writes or loader execution have been performed.
