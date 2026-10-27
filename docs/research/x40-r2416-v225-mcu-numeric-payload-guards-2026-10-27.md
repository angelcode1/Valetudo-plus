# X40 R2416 v225 — two _CtrlMcuCMD numeric payloads and their bypass paths

**27 October 2026. Offline original native evidence only.** Branch descends from v224 and retains the v197–v224 read-only verifier chain, corrected native `RobotNode` provenance, and no robot/Valetudo+ or `master` changes. Original vendor binaries, private archives, settings, credentials, maps and process identifiers remain outside GitHub.

## Two verified numeric command objects, with guarded publication

Original `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` contains two direct calls to `AsyncDeque::MultAsyncPublish<_CtrlMcuCMD>` at PLT `0x275b10` within `AvaNodeRoute::SendMopStainCheckCmd` (VA `0x7b8360–0x7b977c`).

| Direct call | First 32-bit command field | Byte at offset +4 | Native construction |
|---|---:|---:|---|
| `0x7b88d8` | **32** (`0x20`) | **0** | `mov w3,#32` at `0x7b88c4`, `str w3,[sp,#0xc0]` at `0x7b88cc`; preceding `mov w26,#0` at `0x7b88a0` and `strb w26,[sp,#0xc4]` at `0x7b88d0` |
| `0x7b8c18` | **33** (`0x21`) | **1** on the direct counter branch | `mov w6,#33` at `0x7b8bfc`, `str w6,[sp,#0xc0]` at `0x7b8c10`; `mov w4,#1` at `0x7b8708` reaches `strb w4,[sp,#0xc4]` at `0x7b8c14` on the direct countdown route |

The command buffer's pointer goes into `x2` before both typed publish calls (`0x7b88c8`, `0x7b8c04`). These are **numeric payload fields**, not decoded OEM protocol constants. In particular, **no evidence establishes that 32/0 means stop washing or 33/1 means start washing**, and no physical action or MCU acknowledgment has been measured.

## Critical control-flow correction — neither local publication requires a current dirty-key lookup

Original code loads an `AvaSensorsMsg` pointer with typed Blackboard get at `0x7b840c`, and has additional guarded `get<bool>`, `get<_RobotMode>` and `get<WashStatus>` calls at `0x7b85a4`, `0x7b8618`, `0x7b8668`. The native `WashStatus` comparison at `0x7b8694` and other checks gate later logic. These typed reads cannot all be assigned to the named dirty-mop key.

For the **33/1** publish, the compiled branch at **`0x7b871c → 0x7b8bf4`** tests a retained countdown **≤ 0**, then directly builds the command at `0x7b8bfc–0x7b8c14` and invokes publisher `0x7b8c18`. On that direct path it **bypasses** the named `ai_set_mop_is_dirty_data` lookup at `0x7b8b10`. The code writes **750** to the retained counter on compiled paths, but its time unit is unknown.

For the **32/0** publish, the local `0x7b88a4` staged-state test can proceed through `0x7b88ac–0x7b88b4` to the command, again **without performing the dirty-key lookup in that same local branch**. The other branch can reach later code handling the named key. Prior state can influence both guards; this is **not** a claim of global causal independence or an exhaustive runtime proof.

The v224 confirmed key reference at `0x7b8b10`, guarded virtual lookup and potential MCU publisher sites remain valid, but co-location in one function does **not** prove that an inbound AI command code 15 caused either MCU publication or any station wash.

## Complete offline replay and limitations

`X40-R2416-v225-sanitized-analysis-kit.zip`, SHA-256 **`f10e4fe4ee31df60051b24f943313062dc7bcf71f7f6a4b43f6c0d5459d0b499`**, **258,403 bytes**, **121 source-only ZIP entries including SHA256SUMS**, **120/120 SHA-256 payload checks passed**, ZIP CRC verified. The v225 original-source suite passed **11/11 tests**, including the historical v197–v224 original-private regression replay; the exact status of a separate clean-extraction test is documented in the reproducibility handoff. New checks cover **56 exact original AArch64 instructions**, **17 decoded call/branch targets**, payload 32/0 and 33/1 construction and both publisher call sites. Mutation tests reject altered immediates, buffer stores, countdown guard, key lookup, original ELF hash, and an additional unanchored publisher call. A separate bounded standalone checker independently passed on original private evidence with **18 words and two calls**.

**Unproven:** exact vendor command schema and other payload fields, command publication at runtime, MCU delivery, code-15→command causation, station wash, stain-triggered additional floor pass, or dock rewash. Distinguish the mop-station MCU path from the independent `stain_area_for_logic`→`SetExtraCleanArea`→additional floor-task gap.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`, and do not change `master` or robot state.
