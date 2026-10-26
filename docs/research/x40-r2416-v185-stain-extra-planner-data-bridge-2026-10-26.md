# X40 R2416 v185 — Stain-area to extra-clean planner interface

**26 October 2026 · Offline native-only findings.** Original `liblethe_route_nodes.so` fingerprint `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. The source ELF was provided privately by the user; its binary is not stored in this repository.

## Main finding

A **shared named Blackboard data interface** connects map-sensor processing, an AI-stain checking node and conditional extra-clean route construction. This narrows v184's separate stain-perception and extra-clean mechanisms without proving a new autonomous cleaning task.

- `cleanbot::MapSensor::CleanedAreaBuild` constructs the `stain_area_for_logic` key at **0xf8b528**, after a guarded `SafeAny::Any::cast<gte::AlignedBox<2,int>>` at **0xf8b508**. At **0xf8b560** it loads Blackboard vtable slot `+0x20` (compatible with the typed setter slot established in the v182 route analysis), and calls it at **0xf8b57c** with a staged value. Runtime value, origin, and whether this exact branch runs remain unknown.
- `utility::AiStainCheck::tick` constructs the *same key* at **0x5191c0**, checks Blackboard-entry type at **0x519208–0x51920c**, and looks up the key with a `std::Hashtable::find` call at **0x51921c**. This is compiled lookup behavior, not a proven write or command.
- `subregion::SetExtraCleanArea::tick` constructs the *same key* at **0xad944c**, calls its virtual test at **0xad9474** and branches on the result at **0xad9478–0xad947c**. The surviving branch includes `types::CleanList::append` at **0xad94bc** and an `Areas_Clean_List` typed Blackboard set at **0xad94ec**. This is a compiled condition in extra-clean route construction, not evidence that it executes in every cleaning run.
- The same `SetExtraCleanArea::tick` checks `stain_type_for_planning` at **0xad81ac** (conditional branch **0xad81dc**), and reads a typed `extra_clean_rooms` vector at **0xada194**, using key `0xada174`.

This is stronger than finding text strings in unrelated libraries: the key constructions, selected AArch64 instructions, conditional branches, typed `BL` destinations and `BLR` operations are all checked against the pinned original ELF.

## Key reference census — bounded form

| Exact Blackboard key | Adjacent `ADRP+ADD` sites |
|---|---:|
| `stain_area_for_logic` | 11 |
| `stain_type_for_logic` | 9 |
| `stain_type_for_planning` | 6 |
| `Areas_Clean_List` | 77 |
| `extra_clean_rooms` | 4 |

This count covers only strict **adjacent executable AArch64 ADRP+ADD** address constructions, not every possible relocation, indirect call, dynamic string construction or runtime reference. Other sites using `stain_area_for_logic` include `SetCurrentArea::tick`, `ResetPlanningCleanTaskBB`, `PresetBlackboard::tick`, `PointCloudProcess::tick_inner` and `LQRControlRunner::tick`; the existence of a key reference does not classify its access direction.

## Proof boundary

**Verified:** named compiled map-sensor-to-extra-clean-Blackboard interface; AI-stain checker accesses the same key; the extra-clean planner can condition its CleanList construction on that key; separate extra-clean type and room-list lookups.

**Not verified:** a real-world AI dirt event filling the key, that all operations address a single live Blackboard instance, direct AI-stain classification setting a new cleaning-task command, a physically repeated vacuum or mop pass, or the two v165 floor-revisit candidates being caused by CleanGenius. The existing v182–v183 `now_stain_cleaning_id` acknowledgement path is a **different** signal and has not been demonstrated to activate this route.

## Validated offline package

`X40-R2416-v185-sanitized-stain-extra-planner-data-bridge.zip`

SHA-256: `187db7510fca4f8d9e76937d52e3472fc48ca51a40526aa66119ef4761c74bbe`.

The self-contained ZIP holds v184 plus v185 stdlib-only verifiers and tests, a detailed technical report, reference sanitized output and a checksum manifest. On the original private ELF, **68/68 tests passed**, including changed-instruction mutations; without the ELF, **35 passed and 14 skipped** (49 tests counted). Clean ZIP extraction and SHA256SUMS verification passed. **The full executable verifiers and unit tests are inside the ZIP, not separately committed here.**

## Safety and next question

Maintain the last working v74 baseline with `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0` and `writeGateOpen=false`. No robot SSH, cleaning requests, feature activation, firmware patches or runtime repository changes were performed by the assistant. The next task is identifying the actual native scheduler action and branch conditions that would produce a second floor-cleaning pass after an AI stain event. More literal scanning by itself is unlikely to establish this.
