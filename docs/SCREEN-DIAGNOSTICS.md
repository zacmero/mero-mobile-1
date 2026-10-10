# Photographed Mero HTTP v0.3 diagnostics

Source: owner-provided photos `IMG_8376.JPEG`, `IMG_8377.JPEG`, and
`IMG_8378.JPEG`, inspected on 2026-10-10 UTC. Photos show the app's
`Local diagnostics` screen; the original photos remain outside this repository.

Every displayed diagnostic field is transcribed below. Underscores come from
the application field names.

| Field | Displayed value |
| --- | --- |
| `protocol` | `mero-http/1` |
| `transport` | `TCP` |
| `seq` | `35` |
| `ack` | `none` |
| `result` | `startup` |
| `config` | `CLDC-1.1` |
| `profiles` | `MIDP-2.0` |
| `platform` | `j2me` |
| `locale` | `zh-CN` |
| `heap_free` | `1611804` bytes |
| `heap_total` | `2486656` bytes |
| `width` | `320` pixels |
| `height` | `215` pixels |
| `colors` | `65535` |
| `key` | `-6` |
| `jsr75` | `true` |
| `jsr135` | `true` |
| `jsr82` | `false` |
| `fileconnection_version` | `1.0` |
| `media_version` | `1.2` |

The UI also shows `Local diagnostics`, a `Back` softkey, and scroll arrows.
These photos contain diagnostics rather than an exception screen.

## Interpretation and limits

- `seq=35` is the snapshot counter. It does not mean 35 successful uploads:
  opening Details and attempting requests generate snapshots locally.
- `ack=none` and `result=startup` show that no computer command has been
  acknowledged in this app state.
- CLDC/MIDP identify the Java runtime interfaces. `platform=j2me` does not
  identify the native OS or establish shell access.
- The locale is `zh-CN`. Heap measurements describe the Java VM, not physical
  RAM; free heap changes as the app runs.
- Width and height describe this app's Canvas area, not the entire physical
  display. Preserve the reported color count `65535` exactly.
- `key=-6` is the last keypad code, not an error code.
- The JSR flags are class-loading checks: FileConnection and multimedia
  classes loaded, while `javax.bluetooth.LocalDevice` did not. These flags do
  not establish permissions, working storage access, recording support, or
  support for every API in those specifications.
- The filesystem and multimedia version properties report `1.0` and `1.2`.
  The next experiment checks actual file access through a dedicated mailbox.

Related results: [HTTP diagnostics](HTTP-LINK.md) and
[file mailbox experiment](FILE-MAILBOX.md).
