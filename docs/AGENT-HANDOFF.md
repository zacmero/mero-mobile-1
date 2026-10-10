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
