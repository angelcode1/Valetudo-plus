# Dreame X40 R2416 — v56 typed turbidity-state transition and threshold audit

**Date:** 2026-10-23  
**Scope:** Offline, read-only static analysis of the user's preserved original native ELFs and byte-matched independently collected R2416 runtime tree libraries. No robot communication, firmware edits, MIOT commands, runtime hooks, or Valetudo+ changes.

## Executive finding

The two known native failure-marker producers do not need an external `TubidityState=2` writer to become eligible. **Both `StationHandle::SweepStationContorl::WashErrorLogicRun(int,int&,int)` and `WashFloorTubidityCheck()` themselves contain a separate, compiled transition that writes `TubidityState=2`**, on a signed threshold branch. On those branches, the signed 32-bit comparison is:

`*(int32_t *)(this+0x58c) < (*(int32_t *)(this+0x680 or this+0x684) - *(int32_t *)(this+0x588))`.

This notation describes register usage and signed branch selection; it does **not** establish that the fields are actual sensor units, an absolute cleanliness score, or an observed threshold. Subtraction uses 32-bit native integer arithmetic.

When the comparison is true, the examined branch writes numeric state `2` via `BT::Blackboard::set<TubidityState&>`; the immediately adjacent alternative writes state `3`. Subsequent **separate** state-2 consumption within these functions can reset state to 0 and publish `TurbidityResultFail="true"` as established in v55. No runtime iteration order or actual successful re-arm has been observed.

## Instruction-level branch and setter anchors

| Operation | `WashErrorLogicRun()` | `WashFloorTubidityCheck()` |
|---|---|---|
| Load reference field `+0x588` | `0x255234` | `0x2568a0` |
| Load input variant `+0x680` / `+0x684` | `0x255238` | `0x2568a4` |
| Load threshold `+0x58c` | `0x25523c` | `0x2568a8` |
| Compute `variant - reference` | `0x255240` | `0x2568ac` |
| Compare threshold to difference | `0x255244` | `0x2568b0` |
| Signed `b.lt` selecting state 2 | `0x255248 → 0x2553a8` | `0x2568b4 → 0x256a10` |
| Alternative `mov state=3` | `0x25524c` | `0x2568b8` |
| Branch-selected `mov state=2` | `0x2553a8` | `0x256a10` |
| Typed state=2 setter | `0x2553d8` | `0x256a40` |

The source of the compared `+0x58c` field is, on other compiled paths in these same functions, `TurbidityMonitorGetAByTable(int,bool)`:

- `WashErrorLogicRun()`: sets the boolean argument **false** at `0x254f9c`, calls at `0x254fa0`, and stores result in `+0x58c` at `0x254fa4`.
- `WashFloorTubidityCheck()`: sets the boolean argument **true** at `0x25660c`, calls at `0x256610`, and stores result in `+0x58c` at `0x256614`.

The table helper itself begins at `0x252a10` and calls `InitTable()`. The existence of those assignments does not prove that a particular live execution has taken the same table-lookup path immediately before the compare; a field value may have been retained from earlier activity.

## Exhaustive *direct specialization call* census within one ELF

A word-by-word scan of the full executable `.text` section of the pinned **`liblethe_tactics_tree.so`** identified **13 direct `BL` instructions to `0xc83d0`**, the PLT entry for the specifically instantiated `BT::Blackboard::set<TubidityState&>` operation. Checking the immediate or zero-register store feeding each invocation gives:

| Value | Count | Direct setter addresses |
|---|---:|---|
| `0` | 2 | `0x254df4`, `0x256388` |
| `2` | 2 | `0x2553d8`, `0x256a40` |
| `3` | 7 | `0x254a80`, `0x254cec`, `0x254f8c`, `0x25527c`, `0x25609c`, `0x256258`, `0x2568e8` |
| `4` | 2 | `0x254fe4`, `0x256654` |

All thirteen are within the two named station-wash methods. This is an exhaustive census of **direct calls to this specialization and PLT entry in this exact ELF**, not of indirect calls, generic setters, other native libraries, strings or runtime keys.

### Additional bounded counter branch

Within the two functions, the internal counter at `this+0x648` is compared with **9** at `0x254fac` and `0x25661c`. Both `b.le` branches bypass adjacent assignments of state **4**; on the alternative path (greater than 9), state 4 is written. This shows an internal counter-related alternative but not an enforced physical mop-rewash quota. Separately, the state-2 failure-marker branches decrement `this+0x678` and publish `max_rewash_cnt` (v55). The `+0x648` counter and `+0x678` budget field must not be conflated.

## Relationship to v54–v55

The newly identified threshold/state-2 write is upstream of the v55 producer branch, **if** a later eligible invocation reads that Blackboard state. The v55 producer resets state 2 to 0 before writing `TurbidityResultFail`. Separately, the v54 `WashDonePrecess()` request path checks/erases this failure key **before** testing wash enable and `special_push_clean_dish`. Therefore a possible chain is threshold exceedance → state 2 → later failure marker → consumed at `WashDonePrecess()` → a rewash request only on the later eligible path. **An actual run traversing all edges, scheduling a second cycle, and physically washing again remains unobserved.**

The only directly identified model-gated writer of `special_push_clean_dish` remains restricted to other models, not R2416. The new discovery does not close that eligibility gap. Likewise, the two state-2 writers do not establish that the two functions necessarily re-enter after a failed request, or that a counter permits subsequent attempts.

## Reproduction and safety

The self-contained, standard-library verifier pins five whole original ELFs by SHA-256, independently compares three runtime tree library copies, replays the v54/v55 checks, scans the entire tactics ELF for the direct typed-setter call sites, checks every input state value and both signed comparison/branch targets, checks table lookup and state-4 counter branches, and rejects an altered whole-file image. It requires no internet or robot.

```bash
python3 x40_r2416_v56_turbidity_state_transition_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected final signatures:

```text
X40_V54_FAILURE_MARKER_CONSUMPTION_STATIC_PASS
X40_V55_FAILURE_MARKER_REARM_STATIC_PASS
X40_V56_TYPED_TURBIDITY_STATE_TRANSITION_STATIC_PASS
X40_V56_TAMPER_REJECTION_PASS
```

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not upload ELFs, full disassembly, maps, credentials or private configuration to GitHub. No GitHub changes are part of this run.

## Next investigation

Follow the `TurbidityMonitorGetAByTable` result provenance, the state-2 producer's re-entry conditions and the interplay of the `+0x648` failure count and `+0x678` remaining counter. For the overall CleanGenius goal, the missing R2416-reachable `special_push_clean_dish` producer or an alternate dock-actuation flow remains the most important unknown.