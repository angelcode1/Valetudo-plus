# X40 R2416 v229 — incoming typed sensor and retained mop-stain state

**27 October 2026. Read-only, owner-provided original firmware.** Descends from v228; corrected v195 native `RobotNode` research and v197–v228 full replay retained. No robot access or modifications, no live experimental enablement and no proprietary ELF, PRIVATE diagnostic archive, raw configuration, PID/IP or maps committed.

Original host `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.

## Typed incoming sensor registration and copy

`AvaNodeRoute::SensorsProcess(AvaSensorsMsg*)` at **`0x783ce0`** constructs a bound callback and calls **`AsyncDeque::MultAsyncSubscribe<AvaSensorsMsg,AvaSensorsMsg&>`** at `0x783d84 → PLT 0x274b20`. Original ELF **`R_AARCH64_GLOB_DAT`** relocations resolve GOT `0xb784c0` to `SensorsProcess` at `0x783ce0`, and GOT `0xb7b1b0` to **`SensorsProcessSUB(AvaSensorsMsg*)`** at `0x783e70`. This is independently grounded callback identity, not an assumed subscriber based on a symbol name.

The typed `MultAsyncSubscribe<AvaSensorsMsg>` implementation at `0x793220` allocates **`0x118` (280) bytes** at `0x7932a4`, stages **`0x108` (264) message bytes** at `0x7932d4`, and calls `memcpy@plt` at `0x7932e0` to copy the incoming typed message into the allocated object. The original host bounded direct-BL census **`0x2a0000–0x9c0000`** finds exactly **one** call to this specific typed-subscription PLT, at `0x783d84`.

`SensorsProcessSUB` saves the incoming message pointer at `0x783e84` and passes **message offset `+0xfc`** to `SaveBatteryInfoSUB(ava_msg_battery*)` at `0x783ee4 → 0x27b120`. That battery-submessage call is also the **only** direct host BL to the selected PLT. Offset `0xfa = 250` falls within the 264-byte copied message and is **two bytes before** the embedded battery submessage boundary. Neither fact identifies which physical sensor the byte represents.

## Three unsigned-offset byte reads, one retained previous value

A complete original-host .text **unsigned-offset `LDRB Wt,[Xn,#0xfa]` encoding** scan finds exactly three sites, all within `AvaNodeRoute::SendMopStainCheckCmd()`, and none in the `SensorsProcessSUB` body in **that exact addressing form**:

| Original instruction | Compiled effect |
|---|---|
| `0x7b872c` | Read sensor byte; compare it to numeric 4 at `0x7b8730`. Equality branch `0x7b8734 → 0x7b8d7c` resets retained countdown 750 (v228), not direct MCU publication |
| `0x7b8808` | Read byte into a temporary stack record at `0x7b880c`; adjacent `time()` call at `0x7b8814`; persistence/logging not demonstrated |
| `0x7b8890` | Read byte and store to retained previous-value field at `0x7b8894` |

At `0x7b873c/0x7b8740`, the checker compares the previous retained byte with the current byte. The equality branch `0x7b8744 → 0x7b8898` skips its intervening changed-value path. Thus the code implements **compiled change detection and retention**, not just a status==4 guard.

**Negative-census limitation:** Other addressing modes, pointer arithmetic, dynamic aliases, separate modules and actual runtime callbacks are not excluded. This evidence does **not** prove that the incoming sensor callback delivered the same pointer/Blackboard object later read by the mop-stain checker. The external sender/transport and OEM meaning of byte 250 remain unknown.

## Verification, privacy and open gaps

Source-only offline release **`X40-R2416-v229-sanitized-analysis-kit.zip`**, SHA-256 **`7e92b878e66a32e41b806c59aa77d7b7987db37b9392d7c8c075ae71d52c18be`**, **306,427 bytes**, **145 ZIP entries including SHA256SUMS**, all **144/144 internal checksums** and ZIP CRC passed from clean extraction. **14/14 v229 tests passed** in the source directory and **14/14 again from clean extraction**, including the full **v197–v228 original-private historical evidence replay**. New full verifier checks **66 pinned exact AArch64 words, nine decoded direct BL targets, nine branch edges, two original callback relocations, the two direct-call singleton censuses and the three byte loads**. Mutations deliberately inject an *unanchored* extra subscription or `LDRB #0xfa`; both fail, as do altered callback relocation, copy length, store and original ELF hash. Python 3 standard library only. The smaller standalone checker passed **24 representative words, two callback relocations, three byte-read sites, and copy/field offsets 264/250**.

**Still not established:** actual sensor identifier or measured receipt, runtime Blackboard identity, OEM `RobotMode=16` / `WashStatus=2` / sensor byte 4 meanings, outgoing MCU 32/33 OEM meaning, real dock mop wash/rewash, stain-triggered new floor-cleaning task, or physical second pass. v223 AI code-15 dirty-mop flag and v224–v228 station branches are separate compiled paths, not an observed causal chain. Preserve the still-open `stain_area_for_logic`→`SetExtraCleanArea`→production new-task proof gap.

**Next:** identify any original incoming sensor publisher or authoritative struct/enum schema; separately trace new production floor-task dispatch. Do not use raw MCU commands as a shortcut.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. `master`, robot, firmware, active Valetudo+ unchanged.
