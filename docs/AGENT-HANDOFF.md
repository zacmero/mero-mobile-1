# Pair-coding agent handoff

## Assignment
You are helping with **mero-mobile-1**, a playful hardware archaeology and Java ME learning project built around the **Powerpack GSTWF-4012** four-SIM feature phone. The user is on **Arch Linux**, works terminal-first, values practical code and wants to understand **Java, embedded systems, and what actually runs behind old phone UIs**. Explain small concepts when they become useful; prioritize repeatable experiments over speculative deep dives.

## Facts already confirmed by owner
- Java menu with **Application manager**, **Local install**, **Download** and SIM-related connection settings.
- Wi-Fi connection was successful; Bluetooth exists.
- Working radio and television functions in stock UI.
- Two low-resolution cameras (main + top-facing).
- Four-SIM form factor.
- Connecting USB has **not yielded a mounted phone/card** on Linux. USB enumeration itself has *not* been established.
- Exact OS, SoC, RAM, storage map, Java ME profile, Java APIs and native shell **are all unknown**.

## Instructions
1. Begin with docs/RECON-001.md and extend docs/HARDWARE.md using only measured/owner-observed facts.
2. Distinguish physical USB detection, interface enumeration, driver binding and mounted filesystems.
3. Investigate phone Java Local install and microSD reader route; Bluetooth file transfer is a fallback **only if supported**.
4. Work toward the smallest portable MIDlet. src/MeroHello.java is an **untested starter**, not proof of a working compiler/toolchain.
5. Confirm CLDC/MIDP/packaging before wiring up an Arch build. Java ME often requires old bytecode and preverification.
6. Give micro-lessons: MIDlet lifecycle, events/commands, constrained heap, JAR/JAD, Java GCF, optional JSRs.
7. Treat a native OS console as **a separate hypothesis**. Java support does not imply Linux, Android or WinCE, nor does a modem serial port imply a shell.
8. Preserve original functionality. No factory reset, reflashing or hardware modifications during initial reconnaissance.
9. Repo is public: redact IMEI, full MAC addresses when unnecessary, contacts, passwords, SIM data and personal files.
10. Prefer one small documented experiment at a time; finish with observed result, explanation and next step.

## First success criteria
- OS/firmware evidence and actual USB behavior captured (even if no device detected).
- A viable program transfer route established.
- Java MIDlet installer expects known file format(s).
- An offline Mero Hello MIDlet launches, or an exact reproducible blocker is documented.

## Next experiments
- Display and input measurement, heap usage, optional APIs.
- LAN text fetch over Java if networking permissions/API permit it.
- Media, Bluetooth and file storage only where the runtime genuinely supports them.
- Separate deeper board/native OS study once enough evidence exists.

## Starter message for user/agent
Start RECON-001. Compare USB events before/after plugging the phone in with a known data cable, inspect Java menu details and Local install, then determine how to transfer a tiny MIDlet. Keep an evidence table and teach the Java concepts as we encounter them. Do not guess the OS or promise a shell.
