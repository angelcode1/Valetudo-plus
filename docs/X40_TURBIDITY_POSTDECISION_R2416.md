# X40 R2416 — post-decision turbidity state split

**Offline-only evidence**, verified against the private SHA-256-pinned `liblethe_tactics_tree.so` (SHA-256 `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`). No robot activity or production changes.

This extends [floor-to-threshold analysis](./X40_FLOOR_TO_THRESHOLD_R2416.md) and corrects a possible over-reading of the mixed-case `TubidityRecleanFlag` string.

## Two separate comparisons

`WashFloorTubidityCheck()` conditionally calls `CheckIfNeedReClean()` at virtual address `0x256660`. The callee's **B-table threshold** decides the string prepared for the mixed-case `TubidityRecleanFlag` (`"true"` or `"false"`). After the call, the caller **does not branch on that string**.

Instead, the caller performs an **A-table** comparison using three internal fields:

- `this+0x58c`: result from `TurbidityMonitorGetAByTable(...)`, prepared at `0x256610`–`0x256614`;
- `this+0x684`: first comparison value;
- `this+0x588`: second comparison value.

At `0x2568ac`–`0x2568b4`, it compares the signed A-table result against `this+0x684 - this+0x588`, with the following compiled outcomes.

| A-table result vs difference | `TubidityState` | `TubidityResult` |
|---|---:|---|
| Smaller | `2` | `"fail"` |
| Equal or greater | `3` | `"success"` |

The **success** arm performs a typed `BT::Blackboard::set<TubidityState>` call at `0x2568e8`, writes the literal `"success"` to `TubidityResult` at `0x256934`, zeroes `this+0x648` at `0x256950`, and updates the reference field `this+0x684` from `this+0x588` at `0x25699c`–`0x2569d0`.

The **fail** arm begins at `0x256a10`, writes `TubidityState=2` at `0x256a40`, and `TubidityResult="fail"` at `0x256a8c`. Its jump at `0x256a90` merges at `0x256984`, *bypassing the success-only counter reset*.

## Mixed-case key reference audit

A full pinned tactics `.text` direct `ADRP+ADD` reference census located exactly **four** pairs targeting `TubidityRecleanFlag`: `0x253328`, `0x25346c` (the true/false preparations in `CheckIfNeedReClean()`), and `0x254da0`, `0x256334` (idle string resets). These verified direct references are writer/preparation contexts. **This is not proof that no indirect or dynamically resolved reader exists**, nor that other libraries or runtime Blackboard instances never consume the key.

## Evidence limitations and test

Do **not** interpret enum values `2`/`3` as physical wash-actuator states. The `"success"`/`"fail"` strings are compiled turbidity-result literals, not established user-facing outcomes. There is still no proven positive-threshold → `r2343_start_rewash` → additional physical mop-wash chain.

The companion private-offline verifier, distributed separately, checks **the full ELF SHA-256, 32 instruction words, eight branch destinations, four literal locations and all four direct string-reference pairs**. It passed on the original R2416 ELF; an intentionally altered ELF was rejected. No proprietary binaries or disassembly are included in the repository.

**Safety:** No X40 connection, MIOT writes, AVA instrumentation, firmware changes or Valetudo+ production-code edits. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.
