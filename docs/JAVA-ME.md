# Java ME field guide — learning from a 2010-era phone

## The vocabulary
**Java ME** (formerly often called J2ME) is not desktop Java SE and is not Android. Classic small phones often run a configuration called **CLDC**, a profile called **MIDP**, and optional Java Specification Request (JSR) packages.

- **CLDC**: small virtual-machine/runtime foundation and constrained core class library.
- **MIDP**: application model and phone-style GUI, commands, networking and lifecycle.
- **MIDlet**: the application entry-point class, which extends javax.microedition.midlet.MIDlet.
- **LCdui**: javax.microedition.lcdui; small UI toolkit with Form, Canvas, Display, Command.
- **GCF**: Generic Connection Framework, e.g. javax.microedition.io.Connector for compatible devices.
- **Preverification**: older CLDC class files normally require an extra verification/build step after compiling, before packaging for the phone.
- **JAR**: program classes/resources plus META-INF/MANIFEST.MF.
- **JAD**: optional/required-by-device descriptor containing metadata and a path/URL to the JAR.

The vendor Java menu *suggests* a classic MIDlet environment, but its exact CLDC/MIDP profile is still unknown.

## Our first program
MeroHello at ../src/MeroHello.java uses only basic MIDlet/Form/Command APIs, reports runtime properties and heap numbers, and supports Refresh and Exit. **It has been compiled, preverified, installed and launched on the handset.** The phone reports configuration `CLDC1.1` and profile `MIDP-2.0`; the lower CLDC 1.0 / MIDP 1.0 build target worked.

Learn these methods first:
- MIDlet.startApp() — app is started or resumed.
- MIDlet.pauseApp() — runtime pauses the app.
- MIDlet.destroyApp(boolean) — cleanup on exit.
- MIDlet.notifyDestroyed() — app notifies runtime that it has terminated.
- CommandListener.commandAction() — one entry point for soft-key/button actions.

## Candidate manifest (adjust after platform identification)
    Manifest-Version: 1.0
    MIDlet-Name: Mero Hello
    MIDlet-Version: 0.1.0
    MIDlet-Vendor: Mero Lab
    MIDlet-1: Mero Hello, , MeroHello
    MicroEdition-Configuration: CLDC-1.0
    MicroEdition-Profile: MIDP-1.0

This is a **minimal compatibility hypothesis**, not a verified device profile. Use correct CRLF/newline handling per packaging tool and do not duplicate incompatible attributes. If the handset requires JAD, create one with matching name/version/vendor, MIDlet-Jar-URL and exact MIDlet-Jar-Size.

## Build pipeline (to implement after recon)
    Java source
        -> legacy-compatible javac against CLDC/MIDP API stubs
        -> preverify with matching CLDC tools
        -> JAR containing preverified classes + manifest
        -> optionally JAD with exact byte size
        -> microSD local install / supported transfer
        -> test on real device

Current JDKs no longer generally support old -source/-target 1.3 arguments. Do not assume plain modern javac+jar makes a working MIDlet. An older JDK/WTK via isolated environment, or a verified modern tooling workaround, may be needed on Arch. Prefer reproducible tooling and licenses permitting distribution; **do not commit proprietary SDK binaries**.

Emulators such as MicroEmulator can help practice UI development, but a successful emulator run does NOT guarantee this phone will install the JAR or expose the same device APIs.

## After Hello
1. Make a Canvas measuring drawable width/height, font sizes, color capability and keypad.
2. Read Java heap numbers, test limited String operations and file-independent UI.
3. Identify actual optional JSR support using safe class availability checks and handset permissions.
4. If JSR-75 exists, access approved user files. If networking works, GET a tiny plaintext page from a LAN host.
5. Explore MMAPI (JSR-135) / camera, and Java Bluetooth (JSR-82) only if available.

Unlike full Java SE, Java ME can lack familiar tools: no java.nio, no Swing/AWT, typically no generics/modern language features, different collections and limited filesystem APIs.

## Working build — 2026-10-09

Run from the repository root with Java 8 or newer available:

    rtk proxy python scripts/build.py

If Java is outside PATH, pass `--java /absolute/path/to/bin/java`. This session used an existing Java 21 runtime bundled with the local Java language server; no host JDK installation was needed.

The script downloads version-pinned, SHA-256-checked tools from Maven Central into `~/.cache/mero-mobile-toolchain`: Eclipse ECJ 3.26.0, ProGuard 6.2.2, and MicroEmulator CLDC 1.0/MIDP API libraries 2.0.4. It compiles with `-source 1.3 -target 1.1` against those APIs, then applies ProGuard `-microedition` preverification. The MIDP API library contains MIDP 2 definitions; this probe deliberately uses only MIDP 1 APIs. `Form.deleteAll()` was replaced with `size()`/`delete(0)` for MIDP 1 compatibility.

Outputs are `build/MeroHello.jar` and `build/MeroHello.jad`. The observed JAR was 1,758 bytes, contained only the manifest and `MeroHello.class`, used class version 45.3 and contained the CLDC `StackMap` attribute name. The 232-byte JAD declares the exact JAR size and relative filename. These packaging observations do not prove the handset accepts the application.

Send to an already paired phone (replace `PHONE_ADDRESS` with the local Bluetooth address):

    rtk proxy python scripts/send-bluetooth.py PHONE_ADDRESS build/MeroHello.jar build/MeroHello.jad

Requires the user's BlueZ OBEX service, Python `dbus` and PyGObject. Accept each incoming file on the phone. The script monitors BlueZ transfer-status signals; `complete` confirms protocol completion, not saved-file integrity. **Before installation or execution, check the phone's received file has exactly the source byte count printed by the sender.** This is mandatory after the owner observed a truncated/corrupted app transfer. Rounded KB values are insufficient; if the phone cannot display exact bytes, use another method to inspect the saved file and keep installation pending. Matching size detects truncation but does not prove content integrity; compare a checksum when possible. Once verified, open the JAR or use Java Local install. If the phone requires the JAD, its referenced JAR must be in the same folder.

Primary references: [Oracle MIDP 1 Form API](https://docs.oracle.com/javame/config/cldc/ref-impl/midp1.0/jsr037/javax/microedition/lcdui/Form.html), [ProGuard preverification options](https://github.com/Guardsquare/proguard/blob/master/docs/md/manual/configuration/usage.md), and [BlueZ OBEX Client API](https://github.com/bluez/bluez/blob/master/doc/org.bluez.obex.Client.rst).

## References
- Oracle Java ME / MIDP and CLDC: https://www.oracle.com/java/technologies/mobile-devices-downloads.html
- Sun WTK 2.5.2 CLI/preverify: https://docs.oracle.com/javame/dev-tools/wtk-cldc-2.5.2-01/UserGuide-html/commandline.html
- MicroEmulator example (third party; verify environment before using): https://github.com/SodalisRetro/j2me-example-microemu
