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
The proposed MeroHello seed at ../src/MeroHello.java uses only basic MIDlet/Form/Command APIs, reports a few runtime properties and heap numbers, and supports Refresh and Exit. **It has not been compiled or tested on the handset.**

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

## References
- Oracle Java ME / MIDP and CLDC: https://www.oracle.com/java/technologies/mobile-devices-downloads.html
- Sun WTK 2.5.2 CLI/preverify: https://docs.oracle.com/javame/dev-tools/wtk-cldc-2.5.2-01/UserGuide-html/commandline.html
- MicroEmulator example (third party; verify environment before using): https://github.com/SodalisRetro/j2me-example-microemu
