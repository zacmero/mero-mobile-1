# Bluetooth diagnostic link

Mero Link is a second MIDlet for measuring the phone and attempting a two-way Java Bluetooth connection. **The handset experiment found that the runtime cannot load `javax.bluetooth.LocalDevice`.** The owner launched through JAD and JAR and reported the same Bluetooth-unavailable/ClassNotFoundException result. The custom Java listener did not start. Built-in OBEX transfer and readback verification still work.

`Key: 0` is the Canvas's initial last-key value, not a Bluetooth error code. The next practical live-link experiment is Java HTTP over Wi-Fi; Java's Wi-Fi routing remains untested.

## Phone application

`src/MeroLink.java` displays connection status and key codes. It checks for `javax.bluetooth.LocalDevice`, then loads `BluetoothLink` reflectively. If the API is missing or initialization fails, it displays the error. It does not bundle a desktop Bluetooth stack.

`src/BluetoothLink.java` advertises a custom RFCOMM service with UUID `7ca9012e-6d15-4802-a320-a1b2c3d4e501` and name `MeroLink`. It requests authenticated, encrypted connections using the existing Bluetooth pairing. The missing LocalDevice class prevented reaching this stage on the current handset.

The connection sends a greeting and diagnostics immediately. Commands are ASCII lines terminated by LF; responses are UTF-8 lines terminated by a standalone `END` line. Supported commands:

| Command | Response |
| --- | --- |
| `PING` | `PONG` |
| `INFO` | Runtime properties, current Java heap, Canvas width/height, color count, last key and optional API class presence |
| `HEAP`, `SCREEN`, `KEY` | The same diagnostic snapshot, including the requested measurement |
| `BYE` | Closes this client connection; phone listens for the next connection |

The app measures Canvas dimensions, which may exclude soft-key/status areas. API class presence is not proof that every API feature works. Commands cannot execute native shell commands or change firmware. Exit closes the listener and active peer.

## Build and deliver

With a local Java 8+ runtime:

    rtk proxy python scripts/build.py --app link --java /path/to/bin/java
    rtk proxy python scripts/send-bluetooth.py PHONE_ADDRESS build/MeroLink.jar build/MeroLink.jad

This adds the SHA-256-pinned BlueCove 2.1.0 library for compile-time API definitions only. The app targets CLDC 1.0 / MIDP 2.0 and receives CLDC preverification. The first delivered build contains only three application classes plus its manifest.

Do not install or execute yet. Verify the actual saved files first:

    rtk proxy python scripts/verify-bluetooth.py PHONE_ADDRESS --folder Bt build/MeroLink.jar build/MeroLink.jad

The verifier uses OBEX FTP to list the chosen folder, checks exact reported byte sizes, reads back only the named artifacts, and compares all bytes to the local originals. It also prints the matching SHA-256. Downloaded copies are temporary and removed after comparison. A verification failure keeps installation/execution pending.

The initial delivered artifacts were verified on the phone:

| File | Exact bytes | Readback SHA-256 |
| --- | --- | --- |
| `MeroLink.jar` | 5,392 | `dddcb8988f760cd9a1f9e3516f49c43687456226989561bd9f8e02274aeabfd8` |
| `MeroLink.jad` | 302 | `9c31d2add47b7cf65dddc7307bc45a4caa10ba42a7a76d1945d82ba4869c856b` |

These values describe that build only. Rebuilds may change file contents, sizes and hashes. The owner confirmed the phone saved both artifacts under `Bt`.

## Computer client

Once the phone app says it is waiting for the computer:

    rtk proxy python scripts/bluetooth-link.py PHONE_ADDRESS

The client searches for the custom service UUID and uses its advertised RFCOMM channel, avoiding the unrelated native `sprd_com3` service. It reads the greeting, then requests INFO, PING and SCREEN. Diagnostics are saved to the gitignored `logs/bluetooth-link.log` for the agent to read directly.

Keep a connection open for repeated requests:

    rtk proxy python scripts/bluetooth-link.py PHONE_ADDRESS --interactive

Type `INFO`, `PING`, `HEAP`, `SCREEN`, `KEY` or `BYE`. The agent can drive that stdin through its terminal session. This provides a live channel while the MIDlet is running; it does not install an always-on system service on the phone.

## Source, JAR and JAD

- `.java`: source code compiled on the computer.
- `.jar`: the installable application archive containing compiled classes and a manifest; this is the app binary package.
- `.jad`: a small text installation descriptor. It names the app, declares required profiles, and points to the JAR with its exact byte size. It contains no executable app code.

Keep a JAD with its matching JAR in the same folder. Some installers accept the JAR alone; others use the JAD. A JAD's declared size is not a substitute for checking the actual saved file.

References: [BlueZ OBEX FileTransfer API](https://github.com/bluez/bluez/blob/master/doc/org.bluez.obex.FileTransfer.rst), [BlueCove JSR-82 LocalDevice API source](https://github.com/hcarver/bluecove/blob/master/bluecove/src/main/java/javax/bluetooth/LocalDevice.java).
