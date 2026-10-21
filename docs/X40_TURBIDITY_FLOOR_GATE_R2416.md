# X40 R2416 — lowercase turbidity marker in floor-turbidity control

**Scope:** Offline instruction-level analysis of SHA-256-pinned `liblethe_tactics_tree.so` (prefix `da7c04cab9c2dd0a`), supplementing [the final behaviour-tree audit](./X40_TURBIDITY_REWASH_BRANCH_R2416.md). This is compiled control flow only. No live process, vendor firmware, robot commands, credentials, or production code are changed.

## New native finding

At `StationHandle::SweepStationContorl::WashFloorTubidityCheck()`, beginning at ELF address `0x255a50`:

1. `smart_hosting_switch` is retrieved into a zero-initialized local integer via a Blackboard-associated helper. Exact helper failure/default semantics and user-facing switch values are not established.
2. `turbidity_reclean_flag` is tested using the Blackboard virtual `contains()` slot `+0x28`, saving a **key-existence** bit. It is not a comparison against stored Boolean `true`.
3. The integer at `this+0x674` is decremented **whether or not the marker exists**. The branch then checks whether the decremented countdown is nonpositive, `this+0x678` is positive, and two copied-buffer pointers are equal. This buffer comparison has not been semantically decoded.
4. On that identified downstream branch, `smart_hosting_switch > 0` **and absence of** `turbidity_reclean_flag` are jointly required to proceed further. The instruction `ccmp w27,#0,#0,gt` at `0x255db0` combines the signed mode comparison and saved marker-presence bit; `b.ne` at `0x255db4` skips the branch otherwise.
5. A further virtual `contains()` test for `robot_oversea_avoid_turbidity` suppresses the same downstream path if that key exists. If absent, execution continues through further turbidity-state handling, including subsequent `TubidityState` processing.

**Verified instruction sites:** lower-key contains `0x255ce4`–`0x255cf0`; countdown `0x255d0c`–`0x255d1c`; field and buffer checks `0x255d20`–`0x255d30`; mode/marker combined condition `0x255da8`–`0x255db4`; avoid-turbidity check `0x255de4`–`0x255e3c`.

## Interpretation and evidence boundary

The earlier three `IfThenElse` tree paths select `SetBlackboard(turbidity_reclean_flag,true)` or `EraseBlackboard(turbidity_reclean_flag)` based on `IsTurbidityReclean()`. That predicate tests key availability and nonempty `smart_host_clean_set` data—not the separate numeric sensor threshold in `CheckIfNeedReClean()`.

This follow-up identifies **a compiled suppressing/skip condition** for the lowercase marker in one floor-turbidity branch. It does **not** establish that the marker prevents physical rewashing, because this branch has not been mapped to a physical wash-start command. The mixed-case `TubidityRecleanFlag` is still a separate, unresolved key. Runtime Blackboard sharing, execution of this particular branch, the relation to `r2343_start_rewash`, and automatic mop rewash causation remain **unproven**.

## Reproducibility and closure

The companion verifier `util/x40_turbidity_floor_gate_verify.py` uses the pinned whole-file SHA-256, 25 instruction words, and three literal-key checks. It passed against the original owner-supplied ELF and refused an altered copy, with no device access. No proprietary binaries are committed.

Keep the installed Valetudo+ unchanged and `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; no live experiment is required for these findings.