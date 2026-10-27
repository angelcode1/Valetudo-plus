# X40 R2416 v226 — native typed MCU publisher census and response selector

**27 October 2026. Read-only owner-authorized original firmware analysis.** Continues the v225 numeric 32/0 and 33/1 payload study and full v197–v225 verification. Original host `node_lethe.so` SHA-256: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`. No proprietary ELF, PRIVATE archive, raw configuration, device path/PID/IP or map is committed. No robot or `master` changes.

## Complete bounded direct MCU publication inventory

A direct AArch64 `BL` scan over original host executable addresses `0x2a0000–0x9c0000` identifies **exactly 32 direct call sites** to `AsyncDeque::MultAsyncPublish<_CtrlMcuCMD>` PLT **`0x275b10`**. Resolving those 32 sites to the original ELF native `.dynsym` **FUNC value/size intervals** yields **18 distinct owner functions**.

The owners span `EdgeMopStatusControl`, `SendCalibrateCmd`, `SendMsgToMcuWhenReboot`, `LiftLdsCtrl`, `LiftLdsUploadData`, `SendGyroCalibrateCmd`, `SendRobotRollBrushUpraiseStatus`, `SendPowerOffCmd`, `SendResetHoldCmd`, `SendIRTypeSetCmd`, `SendMcuBreak`, `SendRobotCecMode`, `SendCliffShieldCmd`, `SendLDS_SwitchCmd`, `SendWashLogicOTA`, `SendMopStainCheckCmd`, `UpdateLowerConsumptionStateForMcu` and `ControlStationCharge`.

In a **deliberately restricted 144-byte window** immediately before **each of these 32 calls**, a static scan for AArch64 `MOVZ W-register, #32` or `#33` finds exactly **two** occurrences:

| Typed publication | Immediate instruction | Loaded numeric value | Owning function |
|---|---|---|---|
| `0x7b88d8` | `0x7b88c4` | 32 | `SendMopStainCheckCmd` |
| `0x7b8c18` | `0x7b8bfc` | 33 | `SendMopStainCheckCmd` |

These are the numeric field constructions with following byte **0** and **1** respectively, already traced in v225. The 144-byte W-MOVZ search does **not** exclude constants set through other encodings, indirect callers, other libraries, or values staged earlier than the inspected window.

## Separate original typed response subscriber and four top-level cases

`AvaNodeRoute::McuSwitchRspProcess(_CtrlMcuCMD*)` at **`0x3cd730`** constructs a bound callback and calls typed `AsyncDeque::MultAsyncSubscribe<_CtrlMcuCMD,_CtrlMcuCMD&>` at **`0x3cd7c8 → 0x2726a0`**.

The original **`R_AARCH64_GLOB_DAT`** relocation at GOT **`0xb787f8`** resolves specifically to native **`AvaNodeRoute::McuSwitchRspProcessSUB(_CtrlMcuCMD*)`** at **`0x3d90f0`**—actual callback identity, not merely matching a symbol name.

`McuSwitchRspProcessSUB` reads a 32-bit code at message offset **0** (`0x3d910c`) and a byte at offset **4** (`0x3d911c`). Its initial selector directly compares the code against **26** (`0x3d9120`), **27** (`0x3d9128`), **36** (`0x3d9130`) and **24** (`0x3d9138`). The selector does **not** have an explicit top-level case for **32** or **33**. This is *not* proof that no other response code handler exists or that the original firmware cannot process 32/33 elsewhere.

## Verification, scope and next research

Source-only private-evidence release `X40-R2416-v226-sanitized-analysis-kit.zip`: SHA-256 **`d7f198651f42c9d7137c4d21eeaf03f992158eebfe00593d4083f1f55692e0c3`**, **269,347 bytes**, **127 ZIP entries including SHA256SUMS**, **126/126 internal checksums verified on fresh extraction**, ZIP CRC passed.

The full **11/11 v226 source-directory tests passed**, including the complete v197–v225 original private-evidence replay. From a fresh extraction **10/10 isolated native and mutation tests passed** plus independent **16-word/32-publisher/2-nearby-value** checker; its *separate full historical replay timed out*, so a clean-extraction full-chain pass is **not claimed**. The original-only full verifier checks **22 exact native instruction words, all 32 direct BL sites, the 18-owner census, two bounded immediates, four incoming selector comparisons and one exact GLOB_DAT callback relocation**; mutation tests reject changed selectors, added call sites, new immediate constructions, changed callback symbol and ELF SHA.

**Not established:** vendor numeric 32/33 command meanings, actual publication, MCU reply, station washing, dock rewash or AI-stain-caused additional floor-clean task. Next investigate separately recorded MCU protocol/response consumers and production station-wash state, and continue the distinct `stain_area_for_logic`→`SetExtraCleanArea`→new-task dispatch research. Never transmit experimental raw MCU commands.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Leave the robot, Valetudo+ and `master` unchanged.