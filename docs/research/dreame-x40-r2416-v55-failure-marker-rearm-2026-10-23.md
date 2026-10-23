# Dreame X40 R2416 — v55 state-2 failure-marker re-arm audit

**Date:** 2026-10-23  
**Method:** Offline, read-only inspection of SHA-256-pinned original native ELFs and independently collected byte-matched runtime tree libraries. **No robot access, firmware patching, MIOT/AVA commands, runtime hooks or Valetudo+ changes.**

## Executive finding

Two distinct native functions contain branches selected when a retrieved numeric `TubidityState` equals **2**. Each branch:

1. Writes **numeric `TubidityState=0`** back to a Blackboard via a typed setter.
2. Constructs `TurbidityResultFail` and invokes `BT::Blackboard::set<char const (&)[5]>` with the string **`"true"`**.
3. Sets internal field `[this+0x674]=100`, decrements `[this+0x678]`, and republishes the latter using `max_rewash_cnt`.
4. Increments `[this+0x648]` and tests whether the incremented value exceeds **9**, with a distinct follow-on branch for the greater-than case.

This demonstrates compiled capacity to *re-create* the failure marker following an appropriate subsequent state-2 entry. It does **not** demonstrate that the state-2 condition recurs following a wash-request rejection or that the same runtime Blackboard instance is involved.

## Instruction anchors

| Operation | `WashErrorLogicRun()` | `WashFloorTubidityCheck()` |
|---|---|---|
| Compare retrieved state with 2 | `0x2549c0` | `0x255fd8` |
| Branch to state-2 producer | `0x2549c4 → 0x254dc8` | `0x255fdc → 0x25635c` |
| Write `TubidityState=0` | `0x254df4` | `0x256388` |
| Construct `TurbidityResultFail` | `0x254e1c–0x254e20` | `0x2563b0–0x2563b4` |
| Typed setter carrying `"true"` | `0x254e40` | `0x2563d4` |
| Internal countdown assignment | `0x254e60–0x254e64` | `0x2563f4–0x2563f8` |
| Decrement `[this+0x678]` | `0x254e6c–0x254e70` | `0x256400–0x256404` |
| Increment failure counter `[this+0x648]` | `0x254eb8–0x254ec0` | `0x256458–0x256460` |
| Compare with 9 and conditional branch | `0x254ec4–0x254ec8` | `0x256464–0x256468` |

The setter arguments resolve to the exact `TurbidityResultFail` string and the `"true"` literal (`0x3277d8`) in this pinned build. Status 2 is a native internal enum, **not** an observed mop-rewash command.

### Relation to v54: consumption is earlier than eligibility

The verified `WashDonePrecess()` order remains:

`contains(TurbidityResultFail)` → `erase(TurbidityResultFail)` → wash gate `[this+0x688]` → `SetRunState(1)` → `contains(special_push_clean_dish)` → conditional `set(r2343_start_rewash=1)`.

The erase is attempted on the non-null Blackboard path; successful erasure, same-object identity, and run-time dispatch are not independently observed. The **39 direct `BL` instructions** in `WashDonePrecess()` have no target equal to either examined producer's entry address. This is an intraprocedural direct-call census, **not** proof that indirect dispatch or a subsequent event cannot re-enter one of them.

### State-machine interpretation (conditional)

A possible compiled sequence is: state 2 → producer resets numeric state to 0 and sets `TurbidityResultFail` → `WashDonePrecess()` consumes the flag → later eligibility fails → request marker not written. To make that **same direct failure-marker path** set the marker again on a later invocation, its retrieved state must again be 2. An external state transition or a different producer could do this; neither a scheduling guarantee nor a runtime re-arm event has been established.

The counter decrement, countdown and `>9` comparison are **not** evidence of an enforced rewash limit, a physical wash duration, or automatic retries. Exact retry policy is unresolved. The separate keys `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, `max_rewash_cnt` and `r2343_start_rewash` must remain distinct.

## Alternate rewash-request path: bounded negative finding

The v54/v55 ten-ELF exact-literal and short-window direct-reference census finds one directly constructed `r2343_start_rewash` marker in tactics (`WashDonePrecess()`) and one downstream reference in `node_lethe.so` (`SendStationTaskTip()`). It finds no second **direct exact-literal setter** in those collected ELFs using the checked reference pattern. This is **not** an exhaustive negative proof: computed key names, non-ADRP addressing, other firmware modules, indirect command publication and distinct rewash flows remain possible.

## Verification

The standalone standard-library verifier replays the existing v54 original/runtime pin and keyflow checks, then checks numeric state comparisons and branch targets, both reset-then-marker-set sequences, counter modifications, conditional branches, typed setter targets, exact literals and the bounded direct-call census. It rejects a deliberately changed ELF via its whole-file SHA-256 pin.

```bash
python3 x40_r2416_v55_failure_marker_rearm_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected signatures:

```text
X40_V54_FAILURE_MARKER_CONSUMPTION_STATIC_PASS
X40_V55_FAILURE_MARKER_REARM_STATIC_PASS
X40_V55_TAMPER_REJECTION_PASS
```

## Next investigation

The next offline target is **who sets `TubidityState=2` again and under which station-wash/event-loop conditions**, not an experimental write to force `special_push_clean_dish`. Also trace other *actual station-control message* publications without equating the rewash bookkeeping marker with dock actuation. The known model-gated `special_push_clean_dish` writer remains R2416-excluding; no fully operational CleanGenius rewash chain has been demonstrated.

**Safety / Git boundary:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not publish original ELF files, full disassembly, maps, credentials or private live configuration. This report is sanitized; no GitHub changes were made during v55.