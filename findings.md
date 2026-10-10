# Findings

## Device and runtime

- Exterior name: Powerpack GSTWF-4012; board-covering label model: N2322. Exact SN/IMEI remain only in ignored private storage. Chipset and native OS are unknown.
- Owner-confirmed Java configuration: CLDC1.1, MIDP-2.0, j2me, zh-CN. Heap total 2,486,656 bytes is Java heap, not physical RAM.
- FileConnection uses jp.co.aplix.cldc.io.file.FileConnectionImp. JSR-75 file access works; E:/ is the only demonstrated filesystem root.
- Java cannot load javax.bluetooth.LocalDevice. Java HTTP failed at response status; TCP failed at socket opening. Observed Java network accounts offer SIM/CMCC WAP/MMS, with no WLAN choice observed.
- The owner reports working internet access in the native Wi-Fi browser and an earlier LAN download. No genuine native-browser request metadata or message round trip has yet been captured.

## Proven computer access

- Native Bluetooth OPP/FTP works intermittently. JAR/JAD files sort into Bt; text files sort into Ebook.
- An early transfer was corrupted. Exact saved sizes and full readback byte equality/SHA-256 are required before installation or execution.
- The working mailbox reads E:/Ebook/command.txt and writes E:/MeroMailbox/response.txt. Matching command IDs establish two-way communication, with manual acceptance of incoming files still needed.
- Java lists E:/System/Java and reads this project's installed JAR header through file: URLs. Installer slots change across updates; ownership is verified using the entire JAR before reading only owned metadata.
- Current-suite gfs: access failed with ConnectionNotFoundException; parent traversal failed with IllegalArgumentException. Installer metadata was not modified.

## Native routes tested

- No USB events were recorded during the tested cold boot, key, battery and normal boot operations. USB monitoring is stopped at the owner's request.
- Native SPP accepted basic AT queries once but returned no bytes. Java comm:0 never opened successfully, including fresh pairing and v0.10's longer deadline. The host SPP listener received no Java connection.
- HFP accepted BRSF/CIND/CMER service initialization and returned native AT replies. Manufacturer/model/version and command-list queries returned ERROR. This is limited AT access; no OS shell was obtained.
- Native RFCOMM channels changed after pairing: HFP was observed on channel 4, then channel 7. Console retries on the stale channel were refused; the new interactive console is not live-verified.
- Bluetooth serial experiments and the host SPP listener are stopped at the owner's request. No firmware loader was executed and no firmware was written.

## Current implementation

- Mero Files v0.10 is installed. Verified JAR: 11,457 bytes; JAD: 381 bytes. A fresh fully verified SERIAL command received a matching timeout response at open comm:0.
- The LAN server now provides simple HTML 3.2 and WML pages at /link and /link.wml, computer-time replies and bounded message echo. Request metadata includes User-Agent, Accept and WAP profile headers; received messages remain in ignored private logs.
- Browser integration has been implemented and started on 192.168.1.97:8765. Phone-side verification is pending; browser messaging does not provide native shell access.
