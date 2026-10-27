# X40 R2416 v230 — two independent native consumers of AvaSensorsMsg

**27 October 2026. Offline SHA-pinned owner firmware analysis.** This branch descends from the v229 research branch, not `master`. No robot access, firmware/runtime changes, CleanGenius activation, original ELF, private evidence ZIP, raw device config, maps or identifiers committed.

## Separate, positive compiled message paths

The original **`node_lethe.so`** (SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`) registers **`AvaNodeRoute::SensorsProcessSUB(AvaSensorsMsg*)`** via typed `AsyncDeque::MultAsyncSubscribe<AvaSensorsMsg>` at **`0x783d84`**. Its helper stages **0x108 = 264 bytes** at `0x7932d4` and calls `memcpy` at **`0x7932e0`**. The original member callback relocation and typed subscription single-call census were independently established in v229.

The separate original **`node_health_lethe.so`** (SHA-256 `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`) defines **`AvaNodeHealth::Health_SensorProcessStatic(AvaSensorsMsg*)`** at **`0x4d220`**:

- `0x4d228`: stage exactly **0x108 = 264** bytes
- `0x4d238–0x4d250`: direct the input to a local stack copy and call **`memcpy@plt 0x49ef0`**
- `0x4d254–0x4d25c`: pass that copied object to **`Health_SensorData_Get@plt 0x4aec0`**
- `0x4d264–0x4d270`: increment a retained counter at object **`AvaNodeHealth+0x7b8`** on the compiled callback path

The health routine **`Health_SensorData_Get(AvaSensorsMsg*)`** at `0x4d1c0` forwards its typed argument to two distinct handlers: **`LogicSensorDataGet`** at **`0x4d1d4 → 0x4a420`** and **`PlanningSensorDataGet`** at **`0x4d1e0 → 0x4b7c0`**. It also reads message byte **`+0x58`** and stores it into a separate status field (`0x4d1ec–0x4d1fc`). These are compiled routes, not proof they ran together with the route-node callback.

## Bounded byte-250 evidence

v229 found **exactly three** direct AArch64 unsigned-immediate `LDRB Wt,[Xn,#0xfa]` sites in the original route host executable `.text` at **`0x7b872c`, `0x7b8808`, `0x7b8890`**—all inside `SendMopStainCheckCmd`. A complete corresponding exact-form census of the original **health** ELF `.text` VA **`0x4b800–0xbac20`** finds **zero** such instructions. A deliberate otherwise-unanchored injected `LDRB #0xfa` is detected by the v230 verifier.

The census is restricted to **that machine-instruction encoding**. It does not rule out address arithmetic, aliases, another module, or indirect access to the field. Neither module gives us an authoritative OEM name or physical meaning for byte 250. Equality with sensor value `4`, `RobotMode=16`, and `WashStatus=2` remain unidentified as protocol semantics.

## Critical non-inferences

Two different original libraries process the same C++ type and copy **264** bytes. This does **not** establish that they share one live publisher, receive the same message object, use the same Blackboard pointer, decode the same physical sensor, or cause any wash command. The upstream producer/transport has **not** been identified. The still-unproven `stain_area_for_logic` → `SetExtraCleanArea` → **new production floor-cleaning task** must remain a separate research question.

## Verified source-only release

`X40-R2416-v230-sanitized-analysis-kit.zip` SHA-256 **`1f63a1bacd72e7ff71cad337bdb130a46815d3fe676c38d96e5b06f05901e800`**, **317,341 bytes**, **151 ZIP entries including SHA256SUMS.txt**, **150/150 file SHA-256 hashes** and ZIP CRC verified on fresh extraction. The **14/14 full source-directory v230 test suite passed**, including the original private **v197–v229** historical replay. **13/13 native/mutation tests passed from clean extraction**; the separate clean-extraction full historical replay **timed out** and is not claimed as a pass. The new full verifier checks **25 host and 26 health original AArch64 instructions, ten decoded direct-call targets, four branch targets**, the two 264-byte copies and bounded +0xfa censuses. An independent 27-anchor two-ELF checker passed.

All scripts use Python 3 standard library. The original proprietary ELFs and PRIVATE reports are external, never included. No robot commands, firmware writes, feature flag changes or changes to `master`. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

**Next:** identify the actual producer/transport of `AvaSensorsMsg` or authoritative OEM field schema. More importantly, independently locate real production cleaning-task dispatch caused by AI-stain state rather than extrapolating from these sensor consumers.
