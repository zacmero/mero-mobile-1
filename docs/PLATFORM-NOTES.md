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

## Native execution and the Mythroad (MRP) layer

Keypad discovery (`*#220807#` and `*#777755999#`) confirmed that the underlying platform contains an active Mythroad native runtime alongside the Aplix Java ME VM:

```text
    +----------------------------------+     +----------------------------------+
    |         Java MIDlet (.jar)       |     |        Mythroad App (.mrp)       |
    |   MIDP 2.0 / CLDC 1.1 / JSR-75   |     |   Compiled ANSI C / ARM Binaries |
    +----------------------------------+     +----------------------------------+
                     |                                         |
                     v                                         v
    +----------------------------------+     +----------------------------------+
    |      Aplix JBlend Java VM        |     |      Sky-Mobi Mythroad VM        |
    +----------------------------------+     +----------------------------------+
                     |                                         |
                     +--------------------+--------------------+
                                          |
                                          v
    +---------------------------------------------------------------------------+
    |              Spreadtrum Mocor OS (Monolithic RTOS written in C)           |
    |         Device Drivers (LCD, Keypad, Audio, Modem, File System, Baseband) |
    +---------------------------------------------------------------------------+
                                          |
                                          v
    +---------------------------------------------------------------------------+
    |         Spreadtrum SC6600L SoC (ARM7EJ-S / ARM9 core, NOR Flash, PSRAM)   |
    +---------------------------------------------------------------------------+
```

### Architectural Principles

1. **Is the device OS written in C?**  
   Yes. Spreadtrum Mocor OS is a monolithic real-time operating system (RTOS) written entirely in C (with small ARM assembly bootstrap code). It runs on top of an embedded RTOS kernel (typically Nucleus RTOS or Spreadtrum's own RTOS). Drivers, networking, file systems, and the runtime engines are all native C.

2. **Does this allow running programs in C?**  
   Yes. Mythroad (`.mrp`) applications are written in standard ANSI C and compiled with an ARM toolchain (such as `arm-none-eabi-gcc` or ARM ADS) into native ARM machine code. The `.mrp` container packages this compiled binary along with assets. Programs interact with hardware and system services via the Sky-Mobi C API (`mrc_` function calls).

3. **Does this grant native shell access?**  
   - **Built-in OS shell:** No. Mocor OS is not Linux and does not contain a pre-existing Unix shell (like `sh` or `bash`) or a command interpreter.
   - **Constructed shell:** Yes. Because Mythroad grants arbitrary native ARM execution in C, we can compile a custom C program that acts as a shell:
     - Reading and writing files anywhere on `E:/` (microSD).
     - Dereferencing pointers across physical memory addresses, enabling a complete NOR Flash firmware dump directly to SD card without external flasher hardware.
     - Drawing an interactive monospace terminal on the 320 × 215 display and capturing raw keypad events.
     - Opening network sockets or serial streams to communicate directly with a host PC.
