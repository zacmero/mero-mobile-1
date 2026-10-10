# Findings

## Device and runtime

- Exterior name: Powerpack GSTWF-4012; board-covering label model: N2322. Exact SN/IMEI remain only in ignored private storage. Chipset and native OS are unknown.
- Owner-confirmed Java configuration: CLDC1.1, MIDP-2.0, j2me, zh-CN. Heap total 2,486,656 bytes is Java heap, not physical RAM.
- FileConnection uses jp.co.aplix.cldc.io.file.FileConnectionImp. JSR-75 file access works; E:/ is the only demonstrated filesystem root.
- Java cannot load javax.bluetooth.LocalDevice. Java HTTP failed at response status; TCP failed at socket opening. Observed Java network accounts offer SIM/CMCC WAP/MMS, with no WLAN choice observed.
- The owner reports working internet access in the native Wi-Fi browser and an earlier LAN download. A genuine native-browser message and request metadata have now been captured; see the confirmed connection below.

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
- Browser integration has been implemented and started on 192.168.1.97:8765. A real phone message has now been received through the direct port-80 server; browser messaging does not provide native shell access.

## Confirmed native-browser connection

A real phone request from 192.168.1.77 reached the direct port-80 server. The
message was received and the server returned HTTP 200. The owner reported
entering 197 instead of 192 in earlier attempts; those timeouts do not establish
that the browser blocks custom ports or that Java's networking issue is resolved.

User-Agent: Dorado WAP-Browser/1.0.0. The phone supplied WAP profile URL
http://www.spreadtrum.com/wap/6600L_DORADO_UAProfile.xml. This is a firmware/browser
clue, not proof of the exact chipset or native OS. HTTP and HTTPS retrieval attempts failed because the hostname did not
resolve on this computer; the profile contents remain unavailable. Accept includes WML, XHTML, HTML and several image types; actual
rendering support beyond the demonstrated page remains to be measured.

## Automatic two-way inbox confirmed

The native browser acknowledged a queued computer message and sent "hello ghost"
through TX. A fresh computer reply was acknowledged too. Automatic page requests
continued without manual refresh: about 3.2 seconds with a two-second delay,
then about 2.35 seconds after reducing the delay to one second. Computer-message
follow-up acknowledgement took 5.659 seconds across the update, not a directly
measured display latency. HTML is now pure white on black with monospace RX/TX
labels. The exact SoC/OS and any native shell remain unconfirmed.

## Native investigation resumed

The owner confirms the specified white-on-black colors work in Firefox but not
on the phone. Leave the appearance alone; do not claim phone dark mode works.
All 22 initially checked Wi-Fi TCP service ports refused connections. The subsequent full TCP scan was stopped incomplete after slowing progress
and increased phone response latency; remaining ports are not ruled out. No native Wi-Fi service is yet identified.
Matomo's OS classifier maps the observed Dorado browser to Mocor OS; this is
supporting evidence for a Mocor-family hypothesis, not exact firmware/SoC proof.
A firmware/About screenshot is requested. The reported UA profile is unavailable
and Internet Archive returned no snapshot. Optional browser capability probe
implementation is deployed; no genuine phone callbacks have yet been captured.

The owner reports no firmware/About screen after searching the menus. Native FTP root lists 11 entries, rejects parent navigation and exposes no new firmware tree in the tested view. No Device ID modalias or cached Device ID service is reported. Native MRP runtime support is an unconfirmed candidate to investigate; no native payload has been built or executed.

Owner photos confirm exact label 4-GSTWF-4012 and Model:N2322. Multimedia > Games exists, but the submenu is not pictured and native/MRP support remains unconfirmed. Standby date 01.01.2011 is not firmware-build evidence. No chipset marking appears in these photos.
