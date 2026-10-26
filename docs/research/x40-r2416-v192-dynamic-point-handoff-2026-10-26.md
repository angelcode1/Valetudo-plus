# Dreame X40 R2416 v192 — Native dynamic-obstacle point selection and handoff

**26 October 2026.** Offline-only native AArch64 analysis of the private R2416 `liblethe_route_nodes.so` (SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`). No robot SSH, hardware changes, firmware patches, CleanGenius enablement, or task commands.

## New native mechanism

`GetNextDynamicObstaclesArea::getFirstCleanDynamicObstaclesData()` at `0xaead90` reads the Blackboard key `current_coord` using the typed `get<gte::Vector<2,int>>` at `0xaeadf0`, with key literal `0xfccda0` referenced at `0xaead98`. Failure of this coordinate read branches to an error path; an empty internal candidate vector results in a false outcome.

The helper loops through available integer-coordinate candidate points, computes squared coordinate differences and a square-root distance (instructions `0xaeae40`–`0xaeae70`), compares with the running best at `0xaeae78`, and updates its selection when the candidate is closer (`0xaeae7c`). It copies the chosen coordinate pair to an output argument at `0xaeae94`–`0xaeae98`, may move trailing vector entries via `memmove` at `0xaeaeac`, then decreases the candidate-vector end by eight bytes at `0xaeaeb4`. **This is an internal navigation-point selection/consumption mechanism, not a proven cleaning task dispatcher.**

The parent behavior-tree node `GetNextDynamicObstaclesArea::tick()` calls the first helper at `0xaee8f4` (PLT `0x447cb0`) and has a separate selected-area helper `getSelectedAreasDynamicObstaclesData()` invoked at `0xaeedcc` (PLT `0x44f440`). A comparison against integer `1` and equal-branch at `0xaee8d4`–`0xaee8dc` distinguishes these paths.

The same parent constructs two distinct Blackboard keys and performs setter-compatible indirect vtable-slot +0x20 calls:
- `original_dynamic_obstacles_point` (literal `0x1007ce0`, reference `0xaee92c`), virtual call `0xaee990`.
- `next_dynamic_obstacles_point` (literal `0x1007d08`, reference `0xaeee4c`), virtual call `0xaeee90`.

**Boundary:** Compiled references to both keys do *not* establish that both are assigned during the same runtime branch, nor the exact typed vtable target, an autonomous new-cleaning-task message, or a causal link from detected stains to physical recleaning. The prior v191 finding that a `get<bool>(need_extra_clean)` lookup-success branch can early-return remains important; stored Boolean truth and lookup success are distinct.

## Validation

Validated standalone kit `X40-R2416-v192-sanitized-dynamic-point-handoff.zip` SHA-256 `7bd8c90cc20f4b4ea4fbc2ef839083f0fda7dacf7d8b6df46ef11169d857263e`. Includes the **complete executable v184–v192 verifier chain**, negative mutation tests, sanitized reference result, technical report, README, and `SHA256SUMS.txt`. Against the original private native ELF **222 offline tests passed**. Fresh extraction without it ran **180 tests: 109 passed, 71 correctly skipped**, and every included file checksum passed. The ZIP and this GitHub commit contain **no proprietary original ELFs, screenshots, credentials, map coordinates, or robot-control code**.

## Release decision and next action

Preserve last working Valetudo+ v74 with `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. v192 requires no live robot interaction. Research should now follow the consumers of the next-point Blackboard value into the actual motion/task dispatcher, and independently establish a native dirt-detection event causing a new pass. A goal-point handoff alone is not the CleanGenius reclean feature.
