# X40 R2416 v190 — Bounded producer/consumer audit of need_extra_clean

2026-10-26. Offline-only read-only analysis on original R2416 **liblethe_route_nodes.so**, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. No live device access, task command, firmware change, original ELF upload to GitHub, or working Valetudo+ runtime modifications.

## Principal finding
A complete scan of the available ELF's **strict adjacent executable AArch64 ADRP+ADD references** to the unique key literal `need_extra_clean\0` at VA `0xfd7d68` finds **11 sites**, classified into:
- **Four direct typed `Blackboard::set<bool>` calls**: one guarded true in `SetExtraCleanArea::EndExtraCleanArea` at `0xad49bc`, plus three independently compiled false stores in `SetExtraCleanArea::tick` at `0xad8cc8`, `0xad9d98` and **`0xadfa70`**. The third false setter extends v184's two specifically reported sites.
- **Five direct typed `Blackboard::get<bool>` calls**, at `0xaee5e4` (`GetNextDynamicObstaclesArea::tick`), `0xb3ed28` (`CheckHumanInRoom::tick`), `0xd47994` (`CalculateMaxLiftUnderBedArea::tick`), `0xd4a15c` (`FindRecoverPt::tick`) and `0xee3e20` (`SaveDynamicObstaclesArea::SaveArea`). These demonstrate broad state sharing outside extra-clean planner code.
- **One MapSensor setter-compatible virtual operation** inside `cleanbot::MapSensor::CleanedAreaBuild`: key at `0xf8b664`, immediate integer `1` at `0xf8b690`, virtual slot **+0x20** loaded at `0xf8b69c`, and `BLR` dispatch at `0xf8b6b0`. The direct static C++ signature of that virtual operation is not independently identified, and its branch has not been observed live.
- **One reset-side virtual operation with unresolved direction** at key site `0x5d2f64` in `types::ResetPlanningCleanTaskBB` (slot **+0x30** at `0x5d2f80`). Do not relabel this as a typed get/set without proof.

## Essential AArch64 semantic distinction
`Blackboard::get<bool>(key, bool& out)` returns **lookup success** in `w0` and stores the actual `bool` into an independent out-parameter. `GetNextDynamicObstaclesArea` tests the lookup-success register after the getter (branch at `0xaee608`), as does `SaveDynamicObstaclesArea` (branch at `0xee3e44`). These specific branches are **not direct tests of the stored need_extra_clean bool being true**. Previous inferences about task selection must preserve this distinction.

The 11 direct literal address-construction sites span reset bookkeeping, extra-clean state, dynamic-obstacle workflows, a human-presence workflow, LDS under-bed/recovery handling, and map-sensor state. That broad fan-out makes the key **insufficient as an autonomous CleanGenius-reclean event identifier**.

## Proof boundary
The audit verifies original instructions, key address construction, typed direct BL destinations, MapSensor virtual dispatch staging, and all 11 bounded references. It **does not** prove: same live Blackboard instance and timing; any AI dirt event setting the bit; any behavior-tree scheduler dispatch of another area-clean task; a physical repeated vacuum/mop pass; or that the two v165 anonymous-grid revisits were CleanGenius-triggered. Dynamic/indirect references outside the bounded ADRP+ADD form are not excluded. Unreadable/video controls from other models are not X40 native evidence.

## Verification and provenance
Full self-contained release ZIP: `X40-R2416-v190-sanitized-need-extra-clean-role-audit.zip`.
SHA-256: `8bdbb48242b4ecfe8fae9fc7cebef4411558aff0b822239e1857e41a31835222`.

Contains the **complete executable standard-library-only v184–v190 verifier chain**, all eight associated unittest modules (including v188 screenshot metadata test), sanitized results, technical report, README and SHA256SUMS. Original private ELF replay **181 tests passed**. Clean ZIP replay without original ELF: **92 pass, 47 skip**, with **22 file SHA-256 checks passed**. The full script checks independently mutated instructions even when disabling pinned whole-file SHA only for that negative check. No original firmware binaries, user map files, private screenshots or credentials included.

This Git commit includes the sanitized conclusions and reproducibility manifest; all full executable verifier source and tests are inside the separately released checksum-pinned ZIP.

## Safety and research direction
Keep original working Valetudo+ v74: `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No robot or runtime change was made.

Next decisive goal: inspect *behavior-tree / area selection* transitions and an actual new task command, then establish whether native dirt classification causes that event. Do not equate flag retrieval, cleanup, or staged value with automatic reclean.
