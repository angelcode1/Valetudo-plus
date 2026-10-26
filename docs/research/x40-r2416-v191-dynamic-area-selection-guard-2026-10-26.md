# X40 R2416 v191 — Next dynamic-obstacle area selection guard
**26 October 2026. Offline native static evidence.** Original user-supplied `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. No proprietary firmware or user screenshots are included here.

## Specific compiled branch, not a generic xref count
`subregion::GetNextDynamicObstaclesArea::tick()` at `0xaee540` reads `need_extra_clean` via typed `BT::Blackboard::get<bool>` at `0xaee5e4` (PLT `0x449720`). Immediately thereafter, `AND w22,w0,#0xff` at `0xaee5ec` saves the getter's **lookup-success return**, which is **distinct from the bool value** placed in the out-param at stack offset `+0x9e`. `CBNZ w22` at `0xaee608` branches to `0xaeee08` on lookup success. That destination executes `MOV w0,#3`, followed by stack-canary-safe epilogue ending in `RET` at `0xaeee3c`.

This verifies an **early-result branch on successful key retrieval**, regardless of the actual stored true/false bool value. Result integer `3` is intentionally not assigned a BehaviorTree status name without a binary-specific enum check. This path is **not a native command to start a new cleaning pass**.

## Other native inputs and area operations in the same node

Six exact adjacent AArch64 `ADRP+ADD` constructions are checked:
- `need_extra_clean` at `0xaee5a8`, literal `0xfd7d68`.
- `smart_hosting_switch` at `0xaee640`, literal `0xfd7878`; typed `Blackboard::get<int>` call at `0xaee684`.
- `smart_host_clean_set` at `0xaee6cc`, literal `0xfd2458`; hashed entry lookup then byte value read at `0xaee7ac`, **not** a verified typed direct getter.
- `use_mop` at `0xaee7e4`, literal `0xfd1e90`; address reference alone does not establish how mop state affects selection.
- `reuse_cleaning` at `0xaee804`, literal `0xfce630`; typed `get<int>` at `0xaee838`.
- `next_dynamic_obstacles_point` at `0xaeee4c`, literal `0x1007d08`; setter-compatible vtable slot `+0x20` indirect `BLR` at `0xaeee90`. Its exact typed virtual target and live execution remain unproven.

The node directly calls `initDynamicObstaclesData` at `0xaee86c` and `getFirstCleanDynamicObstaclesData` at `0xaee8f4`, with compiled result guards. These are **area selection/preparation routines**. No direct new-cleaning-task dispatch has been established.

## Relevance to preceding v182–v190 research

The stain-ID message path and perception-handled-stain record (v182–v183) are separate from extra-clean route-state logic (v184–v190). v190 mapped 11 `need_extra_clean` key accesses, including ordinary obstacle, human and LDS recovery code. v191 adds a **concrete selected next-area guard** showing why interpreting `need_extra_clean` as “start another pass” is unsafe. It does not demonstrate that an AI dirt event reaches the branch, nor explain the two coarse-area revisit candidates from v165.

## Independent replay and safety

Self-contained Python 3 stdlib-only ZIP `X40-R2416-v191-sanitized-dynamic-area-selection-guard.zip`, SHA-256 `e9aa20bfe12a03c933faf54fdc4fe4bd426ce81306a8afa0b579ad0c10bafdf2`. Includes full executable v184–v191 verifier chain, instruction oracle, tests, sanitized v191 result, README, detailed report and SHA256SUMS. Full offline regression on the exact private ELF: **201 passed**; clean ZIP without private ELF: **101 passed, 58 correctly skipped**; all packaged SHA256SUMS entries passed. No firmware binaries, map coordinates, passwords or UI screenshots included. The complete executable checker source lives in this ZIP; the GitHub branch records the findings and its immutable fingerprint.

The robot and `master` remain untouched. Keep the last working v74, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. These compiled findings do not authorize enabling CleanGenius or sending any device control request.

**Next useful proof:** an actual behavior-tree state transition from classification to enqueuing a new area-clean task, preferably backed by a passive runtime event. Generic next-area selection is not sufficient.
