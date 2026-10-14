# Mythroad (MRP) Native Execution Packages

This directory contains verified reference builds of Mythroad (MRP) application packages for native execution on the handset.

## Artifact Inventory

| File | Exact Bytes | SHA-256 Checksum | Description |
| :--- | :--- | :--- | :--- |
| `DSM_GM.mrp` | 41,315 | `e9e3b13c1de8829109a06e47febecb24922beee125577d422f82a88fa1ac7a75` | Primary native Mythroad bootloader and graphical menu launcher. |
| `helloworld.mrp` | 8,354 | `ddb0d7e92411a357dfacb5edf3ffedb11ec36afe6002a6ea9e55371d7bab4fe0` | Minimal native C test program rendering "Hello World" to the screen. |
| `mpc.mrp` | 147,505 | `1a734fca1b55bf811fda38b37162ce2c7c4e6ec02efab51b8a1c70afb9db195c` | Mythroad runtime component / community utility package. |

## Memory Card Placement

Place these files directly on the microSD card in a directory named `mythroad` at the root of the filesystem:

```text
microSD Root (E:/)
  └── mythroad/
        ├── DSM_GM.mrp      (or dsm_gm.mrp)
        └── helloworld.mrp
```

Note: Because FAT32 is case-insensitive, copy or symlink `DSM_GM.mrp` as lowercase `dsm_gm.mrp` if needed.

## Execution Procedure

1. Insert the microSD card into the phone.
2. Ensure the phone is on the standby/idle screen.
3. Dial **`*#220807#`**.
4. The screen will display "waiting" for 1–2 seconds while loading `dsm_gm.mrp`.
5. The graphical Mythroad launcher menu will open, displaying the available apps (including `Helloworld`).
6. Select `Helloworld` and press OK/Center to execute native ARM code.
