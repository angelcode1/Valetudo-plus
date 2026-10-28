# X40 R2416 v233 — original health `SENSORS` subscription and callback provenance

**27 October 2026.** Offline read-only analysis of owner-private R2416 original firmware. Descends from [v229](x40-r2416-v229-typed-sensor-retained-state-2026-10-27.md) (commit `1f2b9957128332ad7ccfd7528a844953c717ce85`), incorporating the owner-provided v230 and v231 private collections. No robot access during analysis, firmware execution, runtime instrumentation, MCU commands, Valetudo+ writes, or `master` change. This documentation excludes original vendor ELFs, private archives, private filesystem paths, IDs, maps and raw configuration.

Original `node_health_lethe.so` full SHA-256: `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`.

## New positive original-native proof

Original `avanodehealth::AvaNodeHealth::InitRobotCheckSub()` starts at VA `0x5f090`. Its adjacent AArch64 `ADRP+ADD` at `0x5f2c4/0x5f2c8` constructs the exact original read-only string address `0xbc270`, which contains `SENSORS\0`. Its helper call at `0x5f2d0` constructs a string at `x20`. The original `0x5f358` passes `x20` as topic argument `x1` for `ava::AvaNode::SubscribeImpl` at **`0x5f36c → 0x4b540@plt`**. `w3` is set to raw numeric 9 at `0x5f364`, with no asserted OEM semantics.

A separate original `R_AARCH64_GLOB_DAT` relocation at GOT **`0xe8a38`** points exactly to `AvaNodeHealth::Health_SensorProcessStatic(AvaSensorsMsg*)` at **`0x4d220`**. The original `0x5f2f0` loads that callback from the GOT, and `0x5f2fc` saves its pointer into the binder used in the same named-topic subscription. The `AvaSensorsMsg` RTTI relocation at GOT **`0xe8ea0`** is independently loaded at `0x5f35c` and passed in `x4` to `SubscribeImpl`. The recovered original `ava` executable exports the matching `ava::AvaNode::SubscribeImpl` implementation.

The callback at `0x4d228` selects **264 bytes**, `0x4d250` calls `memcpy@plt`, and `0x4d25c` dispatches to `Health_SensorData_Get`. Separately, `LogicSensorDataGet` reads unsigned bytes `+0xf8` and conditionally `+0xf9` at `0x5e66c` and `0x5e67c`. A bounded census of exact unsigned-offset `LDRB [Xn,#0xfa]` instruction encoding over health-module `.text` finds **zero** such sites. Other addressing modes, other modules and runtime aliases are not excluded.

This proves a **compiled named-topic AVA subscriber** with exact sensor callback identity. It does *not* identify the topic's publisher, prove that it ran or received a live message, or prove that the original route host's **different** `AsyncDeque::MultAsyncSubscribe<AvaSensorsMsg>` interface shares this named topic or a Blackboard pointer.

## Evidence-chain boundaries

- v229 host: typed `AvaSensorsMsg` callback copies 264 bytes; three specific host `+0xfa` reads and a retained previous-value update exist in `SendMopStainCheckCmd`, without OEM field meanings or observed actuation.
- v230 gap collection: 35 SHA-verified original payloads; eight native and one XML among the newly captured files, including the health module and original `ava` executable. The `ai_model_inuse.json` file observed human and obstacle models, not stain; this is file-local, not a global inference.
- v231 gap completion: 46 stored payloads, but **27** duplicated v230 by actual full hash, leaving **19** distinct configuration/state file hashes and *no new native binary or authoritative sensor header*. The v232 corrected collector fixes content-addressed archive deduplication.
- v233 new step: exact `SENSORS` topic construction → AVA subscription → original callback and message-type relocation linkage. **No sensor publisher or new production task proof.**

## Reproducibility

The external source-only v233 verification kit accepts the owner's original v230 PRIVATE ZIP, checks all **35/35** SHA-256 payload hashes and CRC, the health ELF's full SHA-256, **18 exact AArch64 instruction words**, **three decoded BL targets**, **two exact relocations**, the literal topic address and the bounded negative `+0xfa` LDRB scan. **13 tests passed** (including seven original/private mutation/anchor tests). Source-only tests can run without the original firmware, but those do not reproduce the original-private checks. Full marker:

`X40_R2416_V233_HEALTH_SUBSCRIBE_STATIC_PASS 18 3 35`

No PRIVATE payloads are included in this repository. Original verified high-level facts appear in [v233 sanitized evidence](x40-r2416-v233-health-sensors-SANITIZED.json). Do not claim that a published `SENSORS` label establishes runtime delivery or sensor-value semantics.

## Still required

1. Recover **original publisher** of AVA topic `SENSORS` and authoritative OEM `AvaSensorsMsg` field/enum definitions, especially `+0xfa`.
2. Link original route `AsyncDeque` receiver to an actual live `AvaSensors` Blackboard pointer and retained sensor byte when observed. Health and route interfaces must not be conflated.
3. Independently establish `stain_area_for_logic` → `SetExtraCleanArea` → **production new cleaning-task launch** and observed extra physical floor pass. Dock dirty-mop/MCU paths are separate.
4. Avoid broad recollection; seek exact missing dependencies offline first. No experimental raw MCU testing.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No changes to robot, firmware, live Valetudo+, master, or existing v229 branch.
