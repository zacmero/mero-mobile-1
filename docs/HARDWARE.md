# Device record — Powerpack GSTWF-4012

Evidence: **Confirmed** = physically reported by owner; **Unknown** = not yet measured; **Hypothesis** = plausible but needs testing.

## Identity
- **Confirmed:** Powerpack GSTWF-4012, a BlackBerry-style four-SIM feature phone.
- **Unknown:** exact board, chipset, CPU architecture, clock, RAM/flash, screen resolution, OS, Java VM/vendor, firmware and USB controller.
- **Hypothesis only:** classic Java ME CLDC/MIDP on a proprietary feature-phone platform, potentially MediaTek-family. Do not report this as a discovered SoC or OS.

## Interfaces observed

| Feature | Known from phone | Next question |
| --- | --- | --- |
| Java | Mero Hello installed and launched; reports `CLDC1.1`, `MIDP-2.0` | Display/input measurements and optional APIs? |
| Wi-Fi | Joined local Wi-Fi successfully | LAN HTTP from Java? IP and browser capabilities? |
| Bluetooth | Pairing, SDP service discovery and file delivery to microSD demonstrated | Reliability and exact received-file size verification? |
| FM radio | Working in original UI | Antenna requirement? Audio routes? |
| TV | Working in original UI | Technology and API accessibility? |
| Cameras | Main and extra top-facing “spy” camera; both low resolution | Capture dimensions and Java media support? |
| SIM | Four-SIM layout | How many can actually be used concurrently? |
| microSD | Device has microSD capability | Phone file-manager access and external card reader behavior |
| USB | No mounted device/card seen on Linux | Is anything new appearing in lsusb/kernel? |
| Power | Phone powers on | Battery health, external-power behavior |

**No mount is not the same as no USB enumeration.** A cable with charge-only wiring, damaged data contacts, unsupported device USB modes or different device function can explain the missing storage without implying missing Linux drivers.

## Facts to gather by hand
- About/System and Java manager info, firmware string and memory display.
- Model label and port appearance; mask IMEI, serial and SIM-related identifiers in public photos.
- On-screen USB mode prompt, if any.
- Phone file manager: SD visibility, folders, file extensions.
- Bluetooth profiles/services, camera capture format, screen dimension (eventually MIDlet).
- Linux USB ID and interface descriptors, **only if enumeration succeeds**.

## Initial interpretation
The Java menu is promising for Java ME applications but does not prove the phone runs Linux, Android, Windows CE, or exposes a native shell. Java applications normally run inside their virtual machine. Native OS investigation is a later, separate stage.

## Session log format

    Date:
    Phone power state:
    Data cable and PC port:
    Menu/setting:
    USB appears in lsusb?:
    Kernel events:
    microSD via external reader:
    Java install path:
    What succeeded / failed:
    Next hypothesis:

Do not commit raw contacts, messages, network passwords, IMEI, serials, or device identifiers to the public repo.

## RECON-001 computer inspection — 2026-10-09

### USB
- Inspected `lsusb`, USB topology, kernel history for the current boot, block devices, serial-device properties, network interfaces and desktop mounts.
- No enumerated USB device was identified as this phone. No phone/card block device, phone desktop mount or USB network interface was found.
- The only USB serial node, `/dev/ttyACM0`, belongs to USB ID `1a86:5722`, manufacturer `Turing`, product `UsbMonitor`. Its descriptors identify a USB display; it is not evidence of a phone modem.
- Current-boot USB history showed the existing mouse, game controller, Turing display, Bluetooth adapter and hubs, with no additional phone enumeration or USB descriptor errors found.
- Limitation: no controlled cable unplug/replug comparison was performed. These observations establish the current host state, not the cause of the phone's USB failure.
- Owner reports there is no phone-side connection-type option.

### Bluetooth — phone positively identified
- Owner supplied the Bluetooth name; classic Bluetooth discovery found that exact name and the device class/icon identified it as a phone. The personal device name and full address are omitted here.
- BlueZ reported legacy pairing, unpaired/unbonded status, and signal strength around -56 to -58 dBm.
- A direct, unpaired SDP query over L2CAP PSM 1 succeeded. A public browse-group query returned no records, but individual service searches and an L2CAP service search returned records.

| Advertised service | UUID | RFCOMM channel | Reported name |
| --- | --- | --- | --- |
| OBEX Object Push | `0x1105` | 1 | `OPP` |
| Serial Port | `0x1101` | 3 | `sprd_com3` |
| OBEX File Transfer | `0x1106` | 5 | `OBEX FileTransfer` |

- Additional records advertised audio source, AVRCP remote control, and voice gateway services. A Dial-up Networking (`0x1103`) search returned no records.
- This confirms Bluetooth discovery and SDP reachability. It does **not** establish successful pairing, file transfer, serial communication or Java Bluetooth API support.
- **Hypothesis:** `sprd_com3` suggests a possible Spreadtrum-related platform. It is a service-name clue, not a verified chipset, CPU or OS identification. The earlier MediaTek hypothesis remains unverified.

### Local network
- Host LAN interface is wired Ethernet, on the same reported router/LAN as the phone's Wi-Fi: `192.168.1.0/24`.
- A non-root discovery scan and neighbor table found several local devices, but none could be matched conclusively to the phone. The phone IP remains unknown; MAC vendor names alone do not identify it reliably.
- No mDNS service or mounted network resource was identified as the phone.

### Online research and next experiment
- Searches attempted for the exact model and spelling variants with USB/manual terms. The web-search tool failed to decode responses; alternate search endpoints returned challenges, rate limits, errors or irrelevant results. No reliable model-specific source was obtained, and no online specifications are treated as confirmed.
- Primary reference for discovery behavior: [BlueZ Adapter API](https://github.com/bluez/bluez/blob/master/doc/org.bluez.Adapter.rst). Discovery can create a device record without pairing.
- Next experiment: pair using the normal phone UI, then send one tiny harmless file through advertised OBEX Object Push and confirm its receipt. SDP advertises a plausible transfer route; actual transfer remains untested.

### Follow-up — Bluetooth file transfer succeeded
- Owner confirmed the phone's default Bluetooth receive destination is the microSD card; internet access also works in the phone browser.
- Owner reports USB was already tried through multiple ports and two computers. The failure cause remains unknown.
- Legacy PIN pairing completed successfully; BlueZ reported `Bonded: yes`, `Paired: yes` and resolved services. An initial connection attempt failed; a later pairing attempt succeeded.
- Sent the 89-byte ASCII file `mero-bluetooth-hello.txt` through BlueZ `org.bluez.obex.Client1` using target `opp`, then `org.bluez.obex.ObjectPush1.SendFile`. Automatic service selection established the OBEX session after initial direct-channel attempts returned connection errors.
- **Owner confirmed successful receipt.** Bluetooth is now a demonstrated computer-to-phone file-transfer route. Java JAR installation has not yet been tested.
- The host polling code observed a queued transfer, then the transient transfer object disappeared before the next poll. Owner confirmation establishes delivery; the polling output alone did not establish completion.
- Next experiment: prepare a compatible minimal MIDlet, transfer its JAR/JAD by Bluetooth, and inspect the phone's Java Local install behavior. Browser-based HTTP delivery remains an alternative for a later experiment.

### Mero Hello build and first JAR delivery
- Built `MeroHello.jar` (1,758 bytes) and a matching JAD (232 bytes), declaring CLDC 1.0 / MIDP 1.0. Compilation and CLDC preverification succeeded; actual handset runtime support remains unknown.
- Replaced `Form.deleteAll()` with MIDP 1-compatible deletion. Build and Bluetooth-send commands are documented in `docs/JAVA-ME.md`.
- BlueZ OBEX reported `MeroHello.jar: complete`: the JAR transfer succeeded at the protocol level. Handset installation and launch remain pending.
- The first JAD transfer reported `error`; a separate retry reported `MeroHello.jad: complete`. Both install artifacts were delivered at the protocol level.
- Owner reports the earlier text file was saved in the phone's `ebook` folder. The sender supplied no destination folder; the phone chose it. Sorting by `.txt` extension is plausible but unverified.

### First successful MIDlet launch — owner-observed
- Owner confirms Mero Hello installed and ran. Owner reports the first app transfer stopped midway and left a corrupted file; a later copy worked. The exact failing attempt and received byte count were not captured.
- Host OBEX `complete` reports above establish protocol status, **not integrity of the file saved by the phone**.

| Reported field | Exact owner transcription |
| --- | --- |
| Config | `CLDC1.1` |
| Profiles | `MIDP-2.0` |
| Platform | `j2me` |
| Locale | `zh-CN` |
| Heap free | 1,846,308 bytes |
| Heap total | 2,486,656 bytes |

- This confirms Java ME application execution and a runtime reporting CLDC 1.1 / MIDP 2.0. Preserve the configuration string as transcribed; do not silently add punctuation.
- Heap total is about 2.37 MiB; free heap was about 1.76 MiB at that moment. These are Java VM heap measurements, not the phone's physical RAM capacity. Free heap can change as the app runs.
- `j2me` does not identify the native OS or chipset. `zh-CN` is the Java locale and does not establish the language of all phone menus.
- **Required before every future installation/execution:** check the received file's exact byte size against the source. For this build, expected JAR size is 1,758 bytes and JAD size is 232 bytes. Rebuilds may change these numbers. Reject partial files and resend; never rely on rounded KB values or OBEX completion alone. Compare a checksum when available, since equal size alone cannot detect all corruption.

### Bluetooth readback verification and Mero Link delivery
- OBEX FTP sessions, remote folder listing and file readback succeeded without Java running. Owner confirmed JAR/JAD delivery destination `Bt`.
- Built and sent Mero Link: JAR 5,392 bytes; JAD 302 bytes. The remote folder reports those exact sizes. Both artifacts were downloaded back over OBEX FTP and their full contents matched the local originals; matching SHA-256 values are recorded in `docs/BLUETOOTH-LINK.md`.
- This establishes automatic saved-file verification from the computer. `scripts/verify-bluetooth.py` checks only the explicitly named artifacts and does not modify remote files.
- Owner launched Mero Link through both JAD and JAR and observed the same Bluetooth-unavailable/ClassNotFoundException result. The owner transcription names the missing LocalDevice class; the probe attempted `javax.bluetooth.LocalDevice`.
- **Measured limitation:** this Java environment cannot load the JSR-82 LocalDevice API through the probe. The custom Java RFCOMM listener never starts, so no two-way Java Bluetooth link was established. Built-in OBEX transfer and readback remain working.
- `Key: 0` is the app's initial last-key value, not part of the exception or a Bluetooth error code.
- Native `sprd_com3` remains an untested separate interface; it does not establish a path into the Java app.
- Next practical communication experiment: Java HTTP over Wi-Fi to a local computer server. Phone-browser internet access does not yet prove Java's Wi-Fi routing works.

### HTTP diagnostic delivery and networking investigation
- Built/delivered Mero HTTP v0.1 (6,061-byte JAR, 290-byte JAD), verified both saved files by full OBEX FTP readback, then owner launched it. It reported `java.io.IOException`; no valid Java diagnostic snapshot reached the server.
- Computer firewalld was active on the LAN interface. A one-hour runtime rule permits TCP port 8765 only from the local IPv4 LAN subnet.
- Owner reconnected phone Wi-Fi and successfully downloaded the server readiness response in the built-in browser. This confirms browser reachability, not Java's network routing. The original readiness response was text/plain and the phone offered it as a download; the server now sends a simple HTML page at `/`.
- Original server logs stored only validated diagnostic snapshots and omitted browser/rejected requests. Fixed logging to record redacted HTTP request metadata separately.
- Mero HTTP v0.2 uses GET by default, permits switching to POST and reports the failure stage. Delivered and read back the update: JAR 6,846 bytes, JAD 290 bytes; both full contents matched the originals. Exact hashes are in `docs/HTTP-LINK.md`.
- v0.2 handset observation and Java command round trip remain pending. Key code `-6` reported by the owner is the app's keypad measurement, separate from the network error.

## Photographed runtime diagnostics (2026-10-10 UTC)

See [the complete screen transcription](SCREEN-DIAGNOSTICS.md) for every field.
The app reports CLDC-1.1 / MIDP-2.0, j2me, zh-CN; Java heap free
1,611,804 bytes and total 2,486,656 bytes; Canvas 320 × 215 and 65,535
colors; last key -6. FileConnection class present, version 1.0; multimedia
class present, version 1.2; Java Bluetooth LocalDevice class absent.
Sequence 35, acknowledgement none and startup result do not establish any
successful network exchange. The photos do not identify the native OS.

Java HTTP failed at response status and TCP failed at open TCP socket with
ConnectionNotFoundException; native browser LAN access works. The observed
Java network settings offer SIM/CMCC WAP/MMS profiles. The next measured
experiment is filesystem access plus native Bluetooth mailbox transfer.

## Working two-way file mailbox

Verified Mero Files v0.5 read a 64-byte PING command from E:/Ebook/command.txt
and wrote PONG to E:/MeroMailbox/response.txt. The computer retrieved the
response through native Bluetooth FTP and confirmed the exact command ID
acknowledgement. Native OPP receives commands with manual acceptance. Java
filesystem read/write is therefore functional; the native OS and shell remain
unidentified. See [mailbox evidence](FILE-MAILBOX.md) for the complete snapshot.

## Automated capability inventory and passive serial result

Verified v0.6 reports storage root E:/, total 987,480,064 bytes, available
958,971,904 bytes, used 28,508,160 bytes. Java CommConnection loads and
microedition.commports=0; no Java serial connection has been attempted.
Multimedia Manager/VideoControl/RecordControl load, but capture/recording flags
are false. Generic OS/vendor properties are unavailable. PIM version property
1.0 conflicts with failure to load its PIM class. Phone clock reports a 2011
date. See [complete metadata inventory](CAPABILITY-INVENTORY.md).

Native RFCOMM channel 3 (sprd_com3) accepted a host connection. A passive
eight-second read received no data; zero application bytes were sent. This
proves service reachability, not a native console, shell, modem protocol,
specific chipset, or OS.
