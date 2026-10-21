# X40 R2416 — Floor-turbidity gate reaches re-clean threshold

**Scope:** Offline analysis only of the private SHA-256-pinned `liblethe_tactics_tree.so` (prefix `da7c04cab9c2dd0a`). No device access, runtime modification, proprietary binaries or robot commands. Extends [the floor gate audit](./X40_TURBIDITY_FLOOR_GATE_R2416.md).

## New compiled call-graph link

In `WashFloorTubidityCheck()`, a branch previously identified as requiring a nonpositive countdown, a positive field at `this+0x678`, additional buffer conditions, `smart_hosting_switch>0`, **absence** of `turbidity_reclean_flag`, and **absence** of `robot_oversea_avoid_turbidity` can reach further state handling.

In that downstream section:

1. `0x255ea4`–`0x255fbc`: prepare and process a Blackboard lookup associated with `TubidityState`.
2. `0x256048`–`0x256060`: when the field at `this+0x684` is nonzero, compare retrieved text to `"precleaning"`. A *non-equal* result branches to `0x256604`; the zero-field case takes another route.
3. `0x256604`–`0x256614`: call `TurbidityMonitorGetAByTable(int,bool)` with argument `1`, storing its computed result at `this+0x58c`.
4. `0x256618`–`0x256620`: compare `this+0x648` with `9`. Only the `<=9` branch reaches `0x25665c`.
5. `0x256660`: a direct `BL` reaches the `CheckIfNeedReClean()` PLT entry, which was separately established to compare an internal measurement difference against a B-table threshold and prepare mixed-case `TubidityRecleanFlag` as `"true"` or `"false"`.

This is a **compiled conditional link from the lowercase-marker floor gate into the separate threshold-based decision function**. The A-table helper and B-table threshold helper are distinct.

## Evidence boundaries

No evidence yet proves that these conditions held in a live X40, that the lowercase and mixed-case keys are aliases, that a positive threshold decision sets `r2343_start_rewash`, or that a physical repeat mop wash follows. Sensor/field units and the business meaning of `this+0x648`, `0x684` and `0x58c` remain unknown.

## Verification

The local offline audit checked the **full ELF SHA-256**, **30 instruction words**, **4 literals** and **5 branch targets**. The original library passed; an intentionally altered ELF was rejected. The companion read-only verifier and sanitized report were distributed with the offline X40 research package. No vendor binaries belong in this repository.

Retain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and the unchanged running Valetudo+ configuration. This finding does not justify a robot test or firmware modification.
