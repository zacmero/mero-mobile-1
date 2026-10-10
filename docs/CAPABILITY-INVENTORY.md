# Automated v0.6 capability inventory

Retrieved directly from verified Mero Files v0.6 through native OBEX FTP.
Runtime properties and class loading are observations, not a native OS
identification or a guarantee that every reported API works. The app acknowledged
the already-saved INFO command after restart; this snapshot is not a newly
delivered INFO command.

## Complete response

| Field | Value |
| --- | --- |
| `protocol` | `mero-files/1` |
| `seq` | `4` |
| `ack` | `Matched previously verified INFO command ID` |
| `result` | `INFO OK` |
| `inbox_status` | `command exists; bytes=64; url=file:///E:/Ebook/command.txt` |
| `command_status` | `read 64 chars; protocol=mero-files/1; end=true` |
| `mailbox` | `file:///E:/MeroMailbox/` |
| `config` | `CLDC-1.1` |
| `profiles` | `MIDP-2.0` |
| `platform` | `j2me` |
| `locale` | `zh-CN` |
| `heap_free` | `1688164` |
| `heap_total` | `2486656` |
| `colors` | `65535` |
| `fileconnection_version` | `1.0` |
| `media_version` | `1.2` |
| `app_version` | `0.6` |
| `phone_time_ms` | `1296089725405` |
| `property.microedition.encoding` | `ISO-8859-1` |
| `property.microedition.commports` | `0` |
| `property.java.vendor` | `unavailable` |
| `property.java.version` | `unavailable` |
| `property.os.name` | `unavailable` |
| `property.os.version` | `unavailable` |
| `property.os.arch` | `unavailable` |
| `property.supports.audio.capture` | `false` |
| `property.supports.video.capture` | `false` |
| `property.supports.recording` | `false` |
| `property.audio.encodings` | `unavailable` |
| `property.video.encodings` | `unavailable` |
| `property.video.snapshot.encodings` | `unavailable` |
| `property.streamable.contents` | `unavailable` |
| `property.microedition.pim.version` | `1.0` |
| `property.microedition.location.version` | `unavailable` |
| `property.microedition.m3g.version` | `unavailable` |
| `property.microedition.amms.version` | `unavailable` |
| `property.microedition.sensor.version` | `unavailable` |
| `property.bluetooth.api.version` | `unavailable` |
| `class.javax.microedition.io.file.FileConnection` | `true` |
| `class.javax.microedition.media.Manager` | `true` |
| `class.javax.microedition.media.control.VideoControl` | `true` |
| `class.javax.microedition.media.control.RecordControl` | `true` |
| `class.javax.bluetooth.LocalDevice` | `false` |
| `class.javax.obex.ClientSession` | `false` |
| `class.javax.microedition.io.CommConnection` | `true` |
| `class.javax.microedition.pim.PIM` | `false` |
| `class.javax.microedition.location.LocationProvider` | `false` |
| `class.javax.microedition.m3g.Graphics3D` | `false` |
| `class.javax.microedition.sensor.SensorManager` | `false` |
| `storage_root_0` | `E:/` |
| `storage_total_bytes` | `987480064` |
| `storage_available_bytes` | `958971904` |
| `storage_used_bytes` | `28508160` |
| `end` | `1` |

## Interpretation

- The selected storage reports 987,480,064 bytes total (941.734375 MiB),
  958,971,904 bytes available (914.546875 MiB), and 28,508,160 bytes used
  (27.1875 MiB). Available plus used equals total. These are filesystem
  capacity counters, not physical RAM. Only E:/ is reported as a storage root.
- The runtime default encoding is ISO-8859-1. The mailbox explicitly uses UTF-8.
- CommConnection is present and microedition.commports reports the exact string
  0. This is a candidate Java serial identifier, not a demonstrated connection,
  a chipset identification, or a shell.
- Manager, VideoControl and RecordControl classes load, but capture/recording
  properties report false and encoding lists are unavailable. Native cameras
  may work independently; class presence does not establish Java capture support.
- The PIM version property says 1.0, while the PIM class cannot be loaded. This
  inconsistency illustrates why property strings alone are insufficient evidence
  of an implemented API. No contacts or other personal information were queried.
- Bluetooth LocalDevice and OBEX ClientSession classes are absent in Java.
  Native Bluetooth OPP/FTP remain the working transport outside Java.
- LocationProvider, Graphics3D and SensorManager classes did not load.
- Vendor, Java version and native OS/architecture properties are unavailable;
  the native OS remains unidentified.
- The reported phone clock is 2011-01-27T00:55:25.405+00:00 when interpreted as
  Unix epoch milliseconds. It is not a trustworthy host timestamp.
- Capacity/capability metadata is collected once at startup; heap and phone
  clock are refreshed with each response. Values marked unavailable/false retain
  their distinct meanings.

## Native serial service, passive observation

The host opened the previously advertised native Serial Port service on RFCOMM
channel 3 (service name sprd_com3). It sent zero application bytes and waited
eight seconds for unsolicited data. Connection succeeded, but no bytes arrived.
The socket was closed afterward. This establishes reachability only; neither a
serial console nor a modem/shell protocol was identified. The service name is a
Spreadtrum clue, not proof of a particular SoC or OS. No guessed service or
vendor commands were sent. Private raw observations remain in ignored logs.
