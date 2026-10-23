# Dreame X40 R2416 — v40 first-child initialization branch audit

**Date:** 2026-10-23  
**Method:** read-only static instruction and native parameter-table checks against the SHA-256-pinned original firmware, repeated original/runtime tree binary comparisons, and the established v36–v39 regression chain. No runtime/vendor code executed. No commands sent to the robot, no MIOT/AVA writes, firmware modifications, or Valetudo+ changes.

## Question and result

The outer `RobotNode` root sequence must traverse initialization subtrees before its `Loop` containing `StationWash`. v39 established that the four pre-Loop `SubTree` wrappers forward their attached children's statuses; this v40 pass recovers the **first direct child operations** inside those trees and the distinct native branch dispatch of `RobotmodeInit`.

| Wrapper | First generated control | Bounded decoded first operations | Interpretation boundary |
| --- | --- | --- | --- |
| `MapLoad` | `SequenceStarRoF` | `BlackboardContains(key=Start_Map_Load)`; `SaySomething(message=MapLoad Start!)`; `EraseBlackboard(key=startup_clear_flag)` | `Start_Map_Load` is a **key-presence** check, not a comparison with textual `true`. These are compiled child-construction order, not measured ticks. |
| `RobotSysInit` | `SequenceStarRoF` | `SaySomething(message=Robot Running)` followed by a node with type literal `setKey_LongPress_Process` and instance name `RobotInitPara` | Neither the result of the next native node nor the entire subtree return status is established. |
| `StationSysInit` | `SequenceStarRoF` | `SaySomething(message=Station Sys Init)`; `SetBlackboard(continue_work=clean_none)`; `SetBlackboard(mode_dirty_record=none)`; `SetBlackboard(robot_in_station_flag=false)` | Static initialization values; **not observed station-state measurements**. Further children and statuses remain unchecked. |
| `RobotmodeInit` | `IfThenElseStarRoF` | Child 0 `DoesRobotGetCharger`, child 1 `SequenceStarRoF`, child 2 `Sequence`; child 1's early `SetBlackboard` prepares `chargemode_poweron=true` | A compiled charger-status branch exists; whether its condition succeeds/fails/runs on R2416 is not measured. |

## Evidence coordinates

Original SHA-pinned `liblethe_tree.so`:

- `MapLoad` first-child `SequenceStarRoF` attaches at `0x2eeb44`; first three child factory calls at `0x2eeb74`, `0x2eebac`, `0x2eebe4`. Typed `ConstStr` parameter tables at `0x6f97d0` (`Start_Map_Load`), `0x6f97f0` (`MapLoad Start!`) and `0x6f9850` (`startup_clear_flag`).
- `RobotSysInit` first-child `SequenceStarRoF` attaches at `0x30db8c`; first two child constructors `0x30dbbc` / `0x30dbf4`. The diagnostic parameter table at `0x6fcd30` includes the original generated stack label `RobotNode.xml,RobotSysInit,0 0`. The two subsequent type/instance string literals are at `0x585cdc` and `0x585e0d`.
- `StationSysInit` first-child attaches at `0x2ccb3c`; the first four child constructors at `0x2ccb6c`, `0x2ccba4`, `0x2ccbd8`, `0x2ccc0c`. Parameter tables at `0x6e4170`, `0x6e42f0`, `0x6e43d0` and `0x6e4550`.
- `RobotmodeInit` first-child `IfThenElseStarRoF` attaches at `0x2c76d4`; first three direct children construct at `0x2c76f8`, `0x2c7728`, `0x2c7844` and attach at `0x2c7704`, `0x2c7734`, `0x2c7850`. One branch's `SetBlackboard` constructs at `0x2c7764`; its parameter table is at `0x6e5950`.

Original SHA-pinned `libbehaviortree_cpp.so`: symbol `BT::IfThenElseStarRoFNode::tick()` at `0x95520`. The conditional child's returned status is dispatched at `0x955d4`, `0x95608`; status **2** when processing condition-child index 0 selects branch index **1** at `0x95640`, while status **3** when processing that child selects index **2** at `0x95620`. Running status **1** can return without that completed branch selection. These branches are compiled semantics and do not prove the charger condition's runtime result. The v35/v39 analyses cover the distinct `SequenceStarRoF` and `SubTree` status handling.

## Implications and restrictions

The v36 candidate list is now more concrete. For the initial `MapLoad` `SequenceStarRoF`, a missing `Start_Map_Load` entry is a plausible failure source at that inner sequence, subject to wider fallback or retry contexts. The presence check **does not prove** this key is missing in a live X40, nor that `MapLoad` permanently blocks the outer `RobotNode` sequence. `RobotmodeInit` contains an explicit condition with alternative branches rather than simply an unconditional initializer. The existing static path to the `StationWash` builder remains intact.

None of the verified initialization operations produces `special_push_clean_dish` as a demonstrated R2416-compatible key. The v20 finding that the **known** producer is model-gated away from R2416 remains unchanged. No normal turbidity-to-`r2343_start_rewash` causal path, Blackboard runtime instance identity, or physical second wash has been proven.

## Reproduce (fully offline)

With the private original archive and v27 collection on the analyst's Mac, extract the v40 package with its v36–v39 dependencies and run:

```bash
python3 x40_r2416_v40_init_branch_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected marker: `X40_V40_INITIALIZATION_BRANCHES_STATIC_PASS`. The verifier confirms the five original ELF SHA-256 pins, the three runtime/original library comparisons, and v36–v39 regression checks before validating the new child constructors, parameter tables, and `IfThenElseStarRoF` dispatch words. An intentionally modified runtime tree ELF is refused (`original/runtime differs: liblethe_tree.so`). No original vendor libraries or private configuration are in this package.

**Next audit:** bound `MapLoad`'s `Start_Map_Load` producer/consumer census and the `RobotmodeInit` charger branch's producer/consumer lineage; continue the distinct, previously unresolved `special_push_clean_dish` study. Offline-only; keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.