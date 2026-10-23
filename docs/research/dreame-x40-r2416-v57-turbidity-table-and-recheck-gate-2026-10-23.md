# Dreame X40 R2416 — v57 turbidity table selection and recheck gate audit

**Date:** 2026-10-23  
**Scope:** Read-only offline analysis of SHA-256-pinned original firmware and byte-matched R2416 runtime libraries; no robot communication, flashing, MIOT commands, patch deployment or changes to Valetudo+.

## Executive result

The native turbidity decision is **not one undifferentiated threshold**. `TurbidityMonitorGetAByTable(int,bool)` selects two table families depending on its boolean parameter: one path uses the C-table vector (`this+0x628..0x630`, `FindC`) and the other enters a separate Blackboard-aware lookup which can use the A-table vector (`this+0x5f8..0x600`, `FindA`). As shown in v56, `WashErrorLogicRun()` invokes the helper with **false**, while `WashFloorTubidityCheck()` invokes it with **true**. The threshold each obtains is stored at `this+0x58c` before the subsequent signed comparison that may write `TubidityState=2`.

Both functions additionally gate `CheckIfNeedReClean()` behind a test of failure counter `this+0x648 <= 9`; if `>9` the examined alternative writes numeric `TubidityState=4`. `CheckIfNeedReClean()` is **not** a simple unconditional retry: it includes Blackboard-dependent lookup, a second table helper `TurbidityMonitorGetBByTable(int)`, floating-point scaling of threshold field `+0x58c`, and a comparison of the reading difference against that scaled value. Neither helper proves a physical dock rewash or `special_push_clean_dish` eligibility.

## Native instruction anchors

| Finding | Virtual address / evidence |
|---|---|
| A-helper calls `InitTable()` | `0x252a40` |
| A-helper boolean `false` jumps to Blackboard-aware path | `0x252a44 -> 0x252ad8` |
| A-helper boolean `true` validates integer input | `0x252a48..0x252a5c` |
| `true` path references C-table vector | `0x252ab8`, `0x252abc` |
| `true` table helper | `FindC` tail-call at `0x252ad4` |
| Other path references A-table vector | `0x252c08`, `0x252c0c` |
| Other path helper | `FindA` tail-call at `0x252c5c` |
| B-helper range check | `0x252e78..0x252e84` |
| B-helper input `>19` fallback | floating-point `1.0` at `0x252e88` |
| B-helper input `<=0` fallback | approximately floating-point `0.33` at `0x252ed4..0x252edc` |
| B-helper table vector | `this+0x610..0x618` at `0x252eb0`, `0x252eb8` |
| B-helper table path | `FindB` tail-call at `0x252ed0` |
| B-helper empty A-table path | floating-point `0.0` at `0x252eec` |
| Recheck default B input | `mov w1,#20` at `0x2530e8` |
| Recheck dynamic input path | float clamp/convert at `0x2539e8..0x253a14`, rejoins `0x2530ec` |
| Recheck B-helper invocation | `0x2530f0` |
| Recheck threshold scaling | `0x2530f4..0x253104` |
| Recheck baseline/reading comparison | `0x2532e8..0x2532fc` |
| Two guarded recheck calls | `0x254ff4` and `0x256660`; following counter `<=9` branches at `0x254fb0` and `0x256620` |

### Subtlety: default 20 is not the only input to the B-table helper

The recheck has a direct `mov w1,#20` path, which enters the B-helper's **`>19 -> 1.0`** fallback rather than `FindB`. There is also a path converting a float value into an integer B-table index, with a nominal clamping range `0..20` (negative -> 0, greater than 20 -> 20, otherwise integer conversion). Thus the default index-20 route is a **constant scaling factor**, while other valid routes may actually read the B-table. Treating every recheck as `GetB(20)` or treating every recheck as B-table-dependent would both be incorrect.

The B helper checks an auxiliary A-table vector is nonempty before following its `FindB` path. A zero-vector branch yields `0.0`. These behaviours are direct compiled paths; neither lookup-table contents nor the runtime input values have been measured.

### Failure count versus request eligibility

The internal `+0x648` failure count controls a branch into `CheckIfNeedReClean()`; this is **not the same field** as `+0x678` (`max_rewash_cnt`) decremented in the v55 state-2 failure path. The `CheckIfNeedReClean()` table operations do **not** bypass the independent v54 `WashDonePrecess()` requirement for `special_push_clean_dish`, nor prove that a state-2 marker will be recreated after an erase. The model-gated producer of `special_push_clean_dish` directly identified to date excludes R2416, and no alternate R2416-reachable setter is established.

## Evidence and limits

- The standalone verifier checks five SHA-256 original-library pins, the three byte-matched runtime tree libraries, all v54–v56 regression assertions, instruction/register anchors for the table helpers and recheck, branches/call targets, and changed-ELF rejection.
- The `GetAByTable(false)` path is **Blackboard-dependent**; the existence of `FindA` on that path does not establish that it executes on every call.
- Table output values, calibration units, live Blackboard identity, counter initialization, automatic re-entry, and physical second-wash actuation remain unresolved.
- The verification checks a **particular binary revision**, not all Dreame firmware or a live X40 state.

## Reproduce

```bash
python3 x40_r2416_v57_turbidity_table_recheck_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected terminal lines:

```text
X40_V54_FAILURE_MARKER_CONSUMPTION_STATIC_PASS
X40_V55_FAILURE_MARKER_REARM_STATIC_PASS
X40_V56_TYPED_TURBIDITY_STATE_TRANSITION_STATIC_PASS
X40_V57_TABLE_LOOKUP_AND_RECHECK_GATE_STATIC_PASS
X40_V57_TAMPER_REJECTION_PASS
```

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; do not upload vendor native ELFs, unredacted configuration, credentials, maps, or command logs. No device modifications are necessary to run this audit.

## Next focus

Resolve the Blackboard-dependent `GetAByTable(false)` input path and the origin of the recheck float index, then revisit R2416-reachable `special_push_clean_dish` producers. A live second physical wash remains unproven.