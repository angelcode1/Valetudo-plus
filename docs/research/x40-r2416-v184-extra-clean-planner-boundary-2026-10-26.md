# Dreame X40 R2416 — v184 compiled extra-clean planning boundary

**26 October 2026. Offline native research.** Original user-supplied `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. This commit includes NO firmware binaries, private maps, credentials, or robot settings changes.

## New independently checked planning path

Native route-planner Blackboard entries:
- `is_extra_clean_area`, `.rodata` VA `0xfd7d50`: **16** strict adjacent AArch64 ADRP+ADD executable references.
- `need_extra_clean`, `.rodata` VA `0xfd7d68`: **11** references.
- `extra_clean_rooms`, `.rodata` VA `0x1007988`: **4** references.

Specific instruction connections against the original ELF:
- `types::ResetPlanningCleanTaskBB` direct BL at `0x5d2ec4` to the PLT for `subregion::SetExtraCleanArea::EndExtraCleanArea`.
- `EndExtraCleanArea` constructs `is_extra_clean_area` at `0xad4940`, calls `BT::Blackboard::get<bool>` at `0xad4964`, and branches based on successful read and value at `0xad4970/0xad4978`. It constructs `need_extra_clean` at `0xad4994`, stages a true value (`0xad49a8/0xad49b8`) and conditionally calls `BT::Blackboard::set<bool>` at `0xad49bc`. **Do not describe the reset helper as always clearing extra-clean state.**
- `SetExtraCleanArea::tick` separately stages false and calls `BT::Blackboard::set<bool>` for `need_extra_clean` at `0xad8cc8` and `0xad9d98`.
- `CleanedAreaCheckTool::GetExtraCleanType` constructs `is_extra_clean_area` at `0xb75e60` and `extra_clean_rooms` at `0xb76018`, and calls `BT::Blackboard::get<vector<int>>` at `0xb76058`.

These are **compiled planning-state operations**, not proof that a given cleaning session enters these branches. Counting adjacent literal references does not enumerate indirect references, and v184 does not establish every referenced key's direction of access. Other locations in the same binary include `subregion::SetCurrentArea`, `subregion::SetAllAreasFinished`, `switch_mode::PresetBlackboard`, and `cleanbot::MapSensor::CleanedAreaBuild`.

## Crucial boundary versus v182–v183

v182–v183 verifies the `now_stain_cleaning_id` typed Blackboard writer, `AI_STAIN_CLEANING` publisher/subscriber, and its perception-handled-stain state update. v184 establishes an **independent native extra-clean route-state mechanism**. It has **not** shown that AI stain detection writes `need_extra_clean` or populates `extra_clean_rooms`, nor any native task-command output or physical second-pass causation. The two v165 spatial revisit candidates remain unclassified.

Neither the key `need_extra_clean` nor a route tree-node name can be equated with the branded CleanGenius behavior, SmartHost, or a specific MIOT command without further compiled or passive runtime evidence.

## Offline verifier and tests

Private companion ZIP: `X40-R2416-v184-sanitized-extra-clean-planner-boundary.zip`, SHA-256 `a2b681998d2d057ced058616b366a8f34c396303e9179a6554c7de8acb39643f`. Includes original-ELF SHA checking, ELF64/AArch64 section bounds, literal-pointer construction, selected instruction/BL checks, full bounded ADRP+ADD count audit, 29 unit tests, reference JSON, README, and SHA256SUMS. With the original private ELF all 29 tests pass including changed-opcode and changed-literal mutations. Without the ELF, 16 pass and 13 skip. The complete verifier and test sources are in the separately distributed ZIP, not in this GitHub commit.

Do not activate CleanGenius or modify live state. Preserve working Valetudo+ v74 with `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

Next priority: trace what **sets** the extra-clean flags/room list and whether it accepts AI stain-derived information. Keep route planning distinct from generic obstacle, carpet, mop, and small-area extra-clean behaviors.
