# Under the menus: layers and possible native access

## A useful mental model

    Java MIDlet (.jar)
       |
       | MIDP UI / CLDC / optional JSRs
       v
    Java ME virtual machine
       |
       | vendor platform services
       v
    Native phone OS or RTOS (UNKNOWN)
       |
       | device drivers
       v
    screen, keypad, storage, Wi-Fi, BT, radio, TV, cameras, modem

This is a **conceptual model**, not a statement about which OS/chip is installed in this device.

A built-in Java app manager grants a way to run Java software inside a managed environment. It is **not a general-purpose shell** and does not imply access to a POSIX command line, native binaries, flash contents, device drivers or privileged file trees.

## How to identify the underlying platform
1. First, find exact About/firmware details and transcribe only non-sensitive fields.
2. Inspect USB descriptors, *if* the device enumerates on the host; record VID:PID, interface classes, bound kernel drivers. Lack of USB mass storage reveals nothing conclusive about the native OS.
3. Inspect standard phone UI installation paths and Java runtime properties.
4. Check Bluetooth SDP services and whether any documented PC-suite interface is supported.
5. Later, if software-only methods are exhausted and owner wants to open the phone, photograph PCB/chip markings and connector layout. Avoid soldering or electrical probing until power rails and voltage levels are known.
6. Only pursue a vendor-native SDK, firmware format or developer console if a reliable match to the actual board/chipset is established.

## Possible outcomes (all educational)
- **No shell**: proprietary feature-phone OS exposed only through menus and Java ME; build interesting MIDlets and learn API constraints.
- **USB modem/serial**: AT-style commands may query modem status, but are not shell commands; scope depends on exposed function.
- **PC-suite link**: proprietary sync/media manager, possibly useful for file transfer and metadata.
- **Accessible documented native developer path**: explore after identification; no assumption it exists.
- **Physical board study**: a later optional electronics lesson, not phase-one work.

## Gentle hardware rules
Avoid factory reset, flash utilities, pin-short tricks, undocumented service codes and ROM replacement while identifying the platform. If later exploring TTL UART, establish ground and logic voltage before connections; never feed an unknown pin 5V just because a USB serial dongle is nearby.

## Integration architecture ideas (for later)
A tiny display can poll a user-controlled HTTP endpoint over Wi-Fi if Java GCF allows it. A game, photo-viewer, camera experiment or message terminal are all suitable learning projects. None require replacing the vendor OS or connecting Mero Protocol immediately.
