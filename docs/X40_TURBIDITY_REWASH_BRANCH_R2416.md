# X40 R2416 — final offline turbidity-marker branch audit

**Status:** Compiled control flow verified against the three private, SHA-256-pinned R2416 ELF libraries. This documents research findings only. **No physical rewash causation established; no production behaviour changed.** Research stop point: 2026-10-22.

## Verified branch structure

`liblethe_tree.so` constructs an identical three-child `IfThenElse` in each of `AreaSelectModeIndex.xml`, `AutoModeIndex.xml` and `DrawAreaModeIndex.xml`:

1. **Condition:** `IsTurbidityReclean`
2. **Success branch:** `SetBlackboard(key=turbidity_reclean_flag, value=true)`
3. **Failure branch:** `EraseBlackboard(key=turbidity_reclean_flag)`

These are not six independent, unconditional set/erase operations: they are two mutually selected children of a condition in **three** task trees. The tree builder's node factories, parent/child registration calls, depth operations and literal bindings support this ordering. Separately, the pinned `libbehaviortree_cpp.so` `BT::IfThenElseNode::tick()` maps condition result **2** (success) to child index **1**, and result **3** (failure) to child index **2**. Compiled semantics do not prove that a node was ticked during a real cleaning job.

## What the native condition actually tests

The exported `WashStationManag::IsTurbidityReclean(BT::TreeNode&)` in `liblethe_tactics_tree.so` checks that **both** Blackboard keys `enable_turbidity` and `smart_host_clean_set` exist, retrieves the second entry, and returns success when its accessed data span is **nonempty**. Missing keys or an empty span lead to failure in the verified path.

The `enable_turbidity` check is **key existence**, not a comparison of the stored value with Boolean `true`. The function does **not** compute or compare a numeric turbidity sensor threshold.

The lowercase `turbidity_reclean_flag` should therefore be interpreted as a **task-tree predicate/eligibility marker**, **not** a confirmed dirty-water detection or physical rewash request. The application-level meaning of `smart_host_clean_set`'s stored data is not fully decoded.

## Keep separate: other rewash-related paths

- `CheckIfNeedReClean()` is a **different function**, with an internal numeric threshold comparison; it sets the **mixed-case** `TubidityRecleanFlag` to `"true"` or `"false"`. Other routines use `"idle"`. The lowercase and mixed-case keys are **not proven aliases**.
- `WashDonePrecess()` has a conditional `r2343_start_rewash=1` write path. The AVA `SendStationTaskTip()` consumer looks for that exact marker, increments `wash_times` and erases it. That demonstrates compiled bookkeeping, **not** physical wash actuation.
- The wash-state machine has a compiled idle/state-1 to running/state-2 transition and a tag-45 wash-control message whose constructed data includes continuation-step and wash-type bytes. It is **not established** that either turbidity flag or `r2343_start_rewash` directly drives that transition.
- Earlier live, count-only observation during natural dock washing recorded **257** entries at `SendWashContrlInfo()` and **10** hits at the typed `MultAsyncPublish<WashControlMsg>` PLT boundary in roughly 10.28 seconds. This is a real execution-boundary observation, **not** evidence of message payload, delivery, dirtiness classification or rewash causation.

**Unproven:** shared runtime Blackboard instance, actual tick of these three compiled condition branches, positive sensor threshold causing either marker, equivalence of the flag names, any resulting physical rewash, and whether X40 R2416's experimental MIOT controls are safe or effective.

## Offline verification record

Verified full SHA-256 pins:

| Library | SHA-256 |
|---|---|
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The standalone offline verifier checked the three branch layouts, literal keys, conditional status return, `IfThenElse` tick selection, and all three full-library hashes. It passed against the original owner-supplied libraries and rejected an intentionally modified ELF. A synthetic `--self-test` alone does **not** repeat full ELF verification.

**Safety/closure:** This final pass did not connect to the robot, instrument AVA, issue commands, modify firmware or touch Valetudo+. Do not upload proprietary binaries, maps or credentials to this public repository. Preserve the running vacuum and keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Stop research here as requested.

Related background: [X40 CleanGenius research](./X40_CLEANGENIUS_RESEARCH.md).
