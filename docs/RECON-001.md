# RECON-001: Know the beast

**Mission:** Identify the runtime and interfaces of the Powerpack GSTWF-4012 before making assumptions about its native OS.

## A. Phone-side inventory
1. Record About / Device info / firmware and installed memory if visible.
2. Open **Java > Application manager**, examine Local install and version/help information. Check whether it expects JAR, JAD or both.
3. Use the phone file browser to verify the microSD card and accessible directories.
4. Look for USB settings (Mass Storage, Modem/COM, PC connection or other modes). Do not assume they exist.
5. Note Wi-Fi IP/browser behavior and Bluetooth pairing/file reception.
6. Record behavior of radio, TV, both cameras, screen and QWERTY keys. Vendor features are not necessarily exposed through Java.

## B. USB observation on Arch Linux
Connect directly to a PC motherboard port using a **known data-capable cable**, not the old USB 1.1 hub.

Terminal A, started before connecting:

    sudo dmesg --follow --human

Terminal B, compare before and after:

    lsusb
    lsusb -t
    lsblk -o NAME,SIZE,FSTYPE,LABEL,MODEL,TRAN,MOUNTPOINTS
    ip -br link
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

Record the changed lines and the exact phone-side behavior. Test a second known-good cable and direct USB port if absolutely nothing changes.

**Interpretation:**
- No kernel event / no new USB ID: investigate cable data wires, connection mode, physical port and phone power first. Installing drivers is premature.
- USB device but no storage: inspect USB class/interfaces using lsusb -t, then (only for its actual discovered ID) lsusb -v -d VVVV:PPPP.
- Block device appears: inspect non-destructively; do not format, repartition or overwrite.
- Serial/modem interface appears: identify its protocol first; an AT modem channel is not an OS command shell.

A separate USB microSD reader can avoid the phone USB issue entirely for the first Java installation.

## C. Bluetooth and installation path
- Explore phone-to-PC file transfer and pairing.
- On Arch, a paired device can be inspected with: bluetoothctl info PHONE_MAC
- If installed, SDP browser: sdptool browse PHONE_MAC
- Pairing alone does not prove OBEX transfer, RFCOMM serial or Java Bluetooth support.
- If the phone's Local install menu reads the microSD card, put a *small, known-good* MIDlet there and install from the phone UI.

## D. Java ME measurements
Once a tiny MIDlet runs, capture:
- Java properties microedition.configuration, microedition.profiles, microedition.platform and microedition.locale.
- Heap size, display dimensions/color and key mapping.
- App lifecycle and the installation permissions displayed.
- Which optional APIs actually exist: JSR-75 file access, JSR-82 Bluetooth, JSR-135 camera/media and others as evidence warrants.
- Later test plain HTTP to a local server via Wi-Fi *if Java allows and after any permission prompt*.

Use src/MeroHello.java as an educational, uncompiled starter. It is NOT validated on this handset.

## Done when
- [ ] Device and firmware fields documented or marked unknown
- [ ] USB enumeration vs mount distinguished
- [ ] microSD or Bluetooth transfer path established or limitation recorded
- [ ] Java manager installer behavior observed
- [ ] First small MIDlet runs, or precise failure documented
- [ ] Next single hypothesis selected

Stay with reversible, low-cost experiments. No factory reset or firmware replacement in RECON-001.
