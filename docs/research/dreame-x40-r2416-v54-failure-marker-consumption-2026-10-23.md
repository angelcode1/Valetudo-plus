# Dreame X40 R2416 — v54 failure-marker consumption and rewash eligibility audit

**Date:** 2026-10-23  
**Scope:** Offline, read-only investigation of the owner's SHA-256-pinned original R2416 native libraries and corresponding matching runtime copies. This report contains only analysis and verification coordinates; no proprietary binaries, full disassembly, factory credentials, maps, personally identifying device data or unredacted configuration files.

## Executive finding

In `StationHandle::SweepStationContorl::WashDonePrecess()`, the compiled code **checks and attempts to erase `TurbidityResultFail` before checking the automatic-wash gate or `special_push_clean_dish`**. Thus, for an ordinary non-null Blackboard where the failure key exists and the erase completes, a later disabled wash gate or absent `special_push_clean_dish` can prevent the *direct* `r2343_start_rewash = 1` write **after the marker has already been consumed**.

The code also calls `SetRunState(WashStatus=1)` after passing the wash gate, *before* checking `special_push_clean_dish`. No user-facing or physical interpretation of status 1 is established.

This is **a compiled ordering observation, not a live demonstration of a lost request**. The failure key may be republished, another event may retry the logic, and other compiled rewash pathways may exist. Nothing here demonstrates a physical second mop wash.

## Instruction-level ordering

| Sequence | R2416 tactics-library address | Verified compiled role |
|---|---|---|
| 1 | `0x235134/0x235138` | Build the exact literal `TurbidityResultFail` |
| 2 | `0x23517c`, `0x235184` | Call virtual `contains` (`+0x28`) and branch to `0x235360` if absent |
| 3 | `0x235200`, `0x23520c`, `0x235210` | On non-null Blackboard, call virtual `erase` (`+0x30`) for that marker |
| 4 | `0x23522c`, `0x235230` | Read `this+0x688` and branch to `0x235644` if disabled |
| 5 | `0x235234/0x23523c` | Prepare value 1 and call `SetRunState(...)` |
| 6 | `0x23526c/0x235270` | Build exact literal `special_push_clean_dish` |
| 7 | `0x2352a4`, `0x2352b4`, `0x2352bc` | If valid Blackboard, call virtual `contains` (`+0x28`); absent key branches to `0x235758` |
| 8 | `0x2352e4/0x2352e8` | Build exact literal `r2343_start_rewash` |
| 9 | `0x2352fc`, `0x235308`, `0x235314`, `0x235318`, `0x235328` | If valid Blackboard, prepare integer 1 and dispatch virtual `set` (`+0x20`) |

The `contains`/`erase`/`set` slot interpretations were previously resolved for the inspected concrete Blackboard implementations; this v54 audit independently verifies the slot-load instructions and their order. The two `BT::TreeNode::blackboard()` acquisitions are compiled from the same receiver; this does not prove pointer equality under every possible runtime condition.

**Guard distinction:** the initial absence of `TurbidityResultFail` skips the inspected consumption path. The actual marker erase is conditional on a non-null Blackboard. A missing or null Blackboard at the later steps has separate bypass branches. The report does not claim that erasure always succeeds, only that the normal non-null branch invokes `erase` before later eligibility checks.

## R2416-specific producer limitation remains

The only directly established literal writer for `special_push_clean_dish` in the collected, SHA-pinned native set is `node_lethe.so` `ProcessModelInfo()` at `0x470554`. The known model-comparison entry branches admit `dreame.vacuum.r2432`, `mova.vacuum.r2432b`, and `dreame.vacuum.r9420`, while the unmatched-model branch at `0x4731ec` skips that writer. The R2416 model string was recorded in the original model configuration in the v20 audit. Other indirect/dynamic/inherited key sources are not ruled out.

### Cross-library direct-reference boundary

A v54 literal and bounded `ADRP+ADD` census across **ten collected ELFs** reconfirms:

- `special_push_clean_dish`: two direct construction references in `node_lethe.so` (known producer and consumer), one in `liblethe_tactics_tree.so` (presence check), and one static table literal in `liblethe_tree.so` (the `StationWash` `BlackboardContains` parameter, with no direct four-instruction-window `ADRP+ADD` pair).
- `r2343_start_rewash`: one direct construction reference in tactics (`WashDonePrecess()`) and one in `node_lethe.so` (`SendStationTaskTip()` bookkeeping). Other examined modules have no exact literal.
- `TurbidityResultFail` in tactics: three direct references, including the `WashDonePrecess()` check and earlier failure-related paths.

The census is exhaustive **only for exact string occurrence and direct references in a four-instruction `ADRP+ADD` window among the collected ELFs**; it cannot exclude computed keys, other access patterns, different builds, runtime state injection or other libraries.

## Interpretation for automatic mop rewash

1. A state-2 turbidity failure route may produce `TurbidityResultFail`, but a normal threshold event's complete runtime chain is not proven.
2. If `WashDonePrecess()` observes that marker and a valid Blackboard, it can erase it *before* confirming the wash-enable gate and `special_push_clean_dish` presence.
3. Without those later prerequisites, the verified direct request-marker write is bypassed. This establishes a **possible consume-without-request scenario** at this instruction path, not evidence it actually happened on the robot.
4. Even a successful `r2343_start_rewash` write would not prove dock motor actuation. The known `SendStationTaskTip()` path increments `wash_times` and erases a marker; further station-control events remain to be verified.

**Do not conflate keys:** `TurbidityResultFail`, `TubidityRecleanFlag`, lowercase `turbidity_reclean_flag`, numeric `TubidityState`, and `r2343_start_rewash` have different compiled uses. Nor should `special_push_clean_dish` be equated with automatic rewash capability across all pathways.

## Reproduction and validation

Use the bundled self-contained Python standard-library verifier, with owner-controlled, private archived inputs:

```bash
python3 x40_r2416_v54_failure_marker_consumption_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected terminal signatures:

```text
X40_V54_FAILURE_MARKER_CONSUMPTION_STATIC_PASS
X40_V54_TAMPER_REJECTION_PASS
```

The verifier checks five whole-library SHA-256 pins, three byte-identical active/original copies, bounded exact key/callsite references across ten ELFs, branch targets and anchored instruction bytes in the failure-marker path, and the known `ProcessModelInfo()` model bypass. Its in-memory tamper self-test flips a byte and requires the pin check to reject the changed binary.

## Next offline target

Investigate **whether a normal R2416 turbidity failure repopulates `TurbidityResultFail` after a failed eligibility check**, and whether any separate rewash-request path exists that does not need `special_push_clean_dish`. A first-pass, self-contained static producer/consumer investigation is safer and more informative than enabling experimental MIOT writes. Do not patch the model check as an exploratory shortcut: the presence of the eligibility key alone is not evidence of a safe or effective physical rewash sequence.

**Operational boundary:** Preserve the existing working Valetudo+ configuration, keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, do not send live AVA/MIOT commands, modify firmware, install hooks or publish original libraries to GitHub. No repository commit was made during v54.