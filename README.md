# mero-mobile-1

**Computer archaeology / Java ME / embedded systems learning lab**

Target: **Powerpack GSTWF-4012** (four-SIM feature phone).

This repository documents and experiments with an unusual older mobile phone. The goal is to learn **Java ME programming, USB/Bluetooth and networking, constrained-device interfaces, and the operating system beneath the vendor menus**. It is an experimental learning project, not a production phone or a firmware replacement project.

## What we know (owner-observed)

- A dedicated **Java** menu exists, including **Application manager**, **Local install**, **Download**, and connection settings for SIM cards.
- **Wi-Fi works**: the phone connected to the owner's local wireless network.
- **Bluetooth works:** pairing, OBEX service discovery and file transfer to microSD are confirmed. Verify exact received-file sizes before installation or execution; one app transfer was truncated/corrupted.
- **Radio and television have worked** in the original interface.
- **Two cameras**: a normal camera and an additional top-facing camera described by the owner as a “spy camera”; both are low-resolution.
- **Four-SIM design**; exact modem/chipset and whether all slots operate simultaneously have not been measured.
- Plugging its USB cable into an Arch Linux host has **not yet produced a usable mounted device**, including the microSD card. We must first determine whether USB enumerates at all.
- **Mero Hello runs:** the runtime reports `CLDC1.1`, `MIDP-2.0`, platform `j2me`, locale `zh-CN`, and a Java heap total of 2,486,656 bytes in one measurement. Screen dimensions, physical RAM, firmware, SoC and native OS remain unknown.

**Do not infer Android, Linux, a command shell, MediaTek chip identifiers, or any supported Java optional API from the Java menu alone.** A classic Java ME (J2ME) implementation on a proprietary feature-phone OS is plausible, but currently a hypothesis.

## First milestone: RECON-001

**Identify the beast using observations before writing device-specific software.**

1. Record the model/firmware screens and physical connectors; avoid checking personal identifiers or uploading IMEI, Wi-Fi credentials, contacts or SIM contents.
2. Compare Linux USB logs **before and after** connecting a known **data-capable** cable and a direct motherboard port.
3. Explore phone menus for USB connection modes, Java runtime details, memory/card browser, Bluetooth services and installed software.
4. Check whether a separately powered microSD reader makes the card accessible; do not format anything as a first test.
5. Prefer an initial **minimal Java MIDlet** installed by local microSD or Bluetooth file transfer if supported. Check actual API compatibility on-device.
6. Pursue OS-level access only once the platform is identified. **A MIDlet is not a native shell.**

See **[RECON-001](docs/RECON-001.md)** and **[agent handoff](docs/AGENT-HANDOFF.md)**.

## Learning progression

```text
Inspect hardware and OS clues
           ↓
Prove Java MIDlet installation
           ↓
Learn Java ME lifecycle, UI, heap and storage
           ↓
Discover supported networking / media APIs
           ↓
Build one useful tiny phone application
           ↓
Identify native OS/SoC and explore lower-level interfaces
```

The first app should be a short, offline **Mero Hello** with screen size, heap numbers, supported runtime properties and button input. Then a local-network text reader, camera/media tester or tiny remote display if the corresponding APIs work. No dependency on the existing Mero Protocol.

## Repository map

- [docs/HARDWARE.md](docs/HARDWARE.md) — evidence, unknowns and device record.
- [docs/RECON-001.md](docs/RECON-001.md) — first hands-on session and logging.
- [docs/JAVA-ME.md](docs/JAVA-ME.md) — Java ME primer and build/installation plan.
- [docs/PLATFORM-NOTES.md](docs/PLATFORM-NOTES.md) — how to reason about OS, USB and “shell” access.
- [docs/AGENT-HANDOFF.md](docs/AGENT-HANDOFF.md) — pair-coding instructions and milestones.
- [src/MeroHello.java](src/MeroHello.java) — minimal MIDlet probe; compiled, preverified and launched on the handset.
- [scripts/build.py](scripts/build.py) — produces `build/MeroHello.jar` and its matching JAD using a local Java runtime.
- [scripts/send-bluetooth.py](scripts/send-bluetooth.py) — sends files to a paired phone using BlueZ OBEX.
- [scripts/verify-bluetooth.py](scripts/verify-bluetooth.py) — checks exact phone-saved sizes and compares complete file readbacks with the originals.
- [docs/BLUETOOTH-LINK.md](docs/BLUETOOTH-LINK.md) — Mero Link probe and saved-file verification; Java cannot load the JSR-82 LocalDevice class on this handset.

## Current state

**First MIDlet milestone achieved.** Bluetooth delivery, Java installation and Mero Hello execution succeeded. The build targets CLDC 1.0 / MIDP 1.0; the phone reports CLDC 1.1 / MIDP 2.0. USB detection, native OS, display/input measurements and optional Java APIs remain open. See the hardware session log for results and the required received-file size check.

## References

- [Oracle: Java ME / MIDP and CLDC](https://www.oracle.com/java/technologies/mobile-devices-downloads.html)
- [Oracle: command-line MIDlet builds and preverification](https://docs.oracle.com/javame/dev-tools/wtk-cldc-2.5.2-01/UserGuide-html/commandline.html)
- [MicroEmulator project](https://github.com/MadRatSRP/microemu-1)

Keep experiments small, document what worked and what failed, and never replace an observation with a guessed specification.
