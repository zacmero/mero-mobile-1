# Device record — Powerpack GSTWF-4012

Evidence: **Confirmed** = physically reported by owner; **Unknown** = not yet measured; **Hypothesis** = plausible but needs testing.

## Identity
- **Confirmed:** Powerpack GSTWF-4012, a BlackBerry-style four-SIM feature phone.
- **Unknown:** exact board, chipset, CPU architecture, clock, RAM/flash, screen resolution, OS, Java VM/vendor, firmware and USB controller.
- **Hypothesis only:** classic Java ME CLDC/MIDP on a proprietary feature-phone platform, potentially MediaTek-family. Do not report this as a discovered SoC or OS.

## Interfaces observed

| Feature | Known from phone | Next question |
| --- | --- | --- |
| Java | Dedicated menu: Application manager, Local install, Download, SIM connection settings | MIDP/CLDC versions? Local .jar/.jad install? |
| Wi-Fi | Joined local Wi-Fi successfully | LAN HTTP from Java? IP and browser capabilities? |
| Bluetooth | UI supports Bluetooth | Advertised services? Object transfer/serial? |
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
