# Dreame X40 R2416 v213 — direct native builder registration names and relocated callbacks

**27 October 2026.** Offline/read-only analysis of the owner's exact original R2416 AArch64 ELF, continuing the v195 native-`RobotNode` correction and complete v197–v212 verification. No robot activity, native execution, firmware patch, Valetudo+ runtime change, raw proprietary ELF, private paths, robot settings, map, camera content or credentials committed.

## New verified result: all 199 registration names paired with their callbacks

The original whole-file SHA-pinned `liblethe_tree.so`, SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`, defines **`BT_RegisterNodesFromPlugin`** at VA `0x562b4c` (20,268 bytes). It contains **199 direct AArch64 BL calls** to imported `BT::BehaviorTreeFactory::registerTreeBuilder` via PLT **`0x1c6930`**. The import is corroborated by its `R_AARCH64_JUMP_SLOT` relocation at `0x7b1928`.

For *every* registration, a distinct name is built from an ADRP+ADD literal pointer with a string-construction helper at `0x56299c`; the `std::function` callback pointer is loaded from its own GOT slot. The verifier resolves all **199 `R_AARCH64_GLOB_DAT` callback relocations** back to defined exported `build<Name>` functions and checks that each function's name matches the exact registration string. The 199 names also equal the ELF's bounded list of 199 defined exported `build<Name>` functions. There are **no registration-name/callback mismatches** in this direct entrypoint census.

| Bound static fact | Result |
|---|---:|
| Direct registerTreeBuilder sites | **199** |
| Distinct registration name strings | **199** |
| Names matching exported `build<Name>` functions | **199 / 199** |
| Names matching their actual relocated callback | **199 / 199** |
| Direct registered name `AiStainMop` | **0** |

Checked positive controls: `CleanSelectedAreas` registered at `0x563748`; `RobotNode` at `0x565c38`; `StationWash` at `0x566278`; `ReuseTree` at `0x566784`.

**Interpretation:** The compiled native `reuse/AiStainMop` subtree reference exists (v206), but this plugin does **not directly register an `AiStainMop` builder**. This is stronger than v207's missing-export observation. It does **not** rule out dynamically supplied builders, aliases, another plugin, external file-backed construction or alternate effective registrations. The live factory map and actual file-fallback execution were not measured. It does not show an exception, stale cache, physical extra floor clean, or extra dock rewash.

## Reproducibility

Complete sanitized, source-only offline kit: **`X40-R2416-v213-sanitized-analysis-kit.zip`**, SHA-256 **`d1ca959ae0ba9be3d0ae2634b5b119a5fa9952ff8b55394463106290bf1d5e06`**. It includes all v197–v213 Python 3 standard-library verifier scripts and focused tests, original instruction/relocation decoder, sanitized report and JSON, README and manifest; **59 ZIP entries including manifest, 58 internal SHA-256 checksums**. A clean extraction passed every checksum, ZIP CRC and **all nine focused v213 tests**, including original SHA tamper, mutated direct BL, mutated registration name instruction, altered `GLOB_DAT` callback relocation, wrong expected count, mismatched export set, full historical regression replay, redaction and create-only refusal.

The smaller repository checker only reconstructs the **199 registration names vs 199 exports**; the ZIP's full v213 checker independently verifies **all 199 actual callback GOT relocations**.

**Next:** narrow the remaining runtime native-factory registry/alias or file fallback decision, ideally with a passive record of the effective resolver choice rather than repeating filesystem surveys. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; preserve the robot and GitHub `master`.
