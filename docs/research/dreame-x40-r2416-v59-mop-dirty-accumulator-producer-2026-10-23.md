# Dreame X40 R2416 — v59: verified `turbidity_clean_area` producer in MopDirtyAccumulator

**Date:** 2026-10-23  
**Scope:** Read-only offline analysis of five original SHA-256-pinned AArch64 firmware ELF images, cross-checked against three byte-identical active runtime tree libraries collected by the owner. No robot commands, firmware or MIOT writes, module injections, or Valetudo+ changes. The deliverable contains no proprietary ELF images or private configuration.

## Executive result

**`switch_mode::MopDirtyAccumulator::tick()` in `liblethe_route_nodes.so` is a compiled producer of Blackboard key `turbidity_clean_area`.** This resolves v58's bounded unknown, in which the same node's direct literal reference and hash lookup were not yet sufficient to establish a setter. The compiled `tick()` function spans `0xb46fd0..0xb49408`; the exact key literal is at `0x10080b0`. A stack-constructed `std::string` for that literal is passed as `x1` into **three virtual Blackboard set-slot (`+0x20`) calls** and into **one typed `Blackboard::set<float const&>()` call**.

The four key writes are on conditional paths, not guaranteed on every invocation of `tick()`. They do not prove that the node executes during any given R2416 cleaning cycle, that its Blackboard instance is the identical runtime instance consumed by the wash-state logic, or that a write returns successfully.

## Concrete write sites

| Address in route ELF | Code-path fact | Value representation |
|---|---|---|
| `0xb47674` | Calls virtual setter through Blackboard storage vtable slot `+0x20`, passing `x1=x23` (the key) and `x2=x21` (stack value). | Converts accumulated `s8` float to 64-bit `d8` and constructs `linb::any` with the **double** vtable. |
| `0xb47c8c` | Second virtual set, on a separately gated route through `0xb47c54`. | Same `float`→`double` conversion and double `linb::any` payload. |
| `0xb48930` | Third virtual set, following a conditional branch at `0xb47638`. | Converts a stored floating-point sentinel to **double** before the virtual set. |
| `0xb48960` | Direct PLT call to `BT::Blackboard::set<float const&>()` at `0x4526a0`, reached via `0xb47c50`. | Typed **float** payload, here sourced from a local sentinel value. |

These sites occur within the exact ELF symbol `switch_mode::MopDirtyAccumulator::tick()` (symbol begins `0xb46fd0`, declared size 9272 bytes). The virtual setter object is reached by `BT::TreeNode::blackboard()` then `[Blackboard+0x8]`, with a vtable load at offset `+0x20`. The double payload is backed by the `R_AARCH64_GLOB_DAT` relocation at `0x124ec30`, whose dynamic symbol is `linb::any::vtable_for_type<double>::table` (`...vtable_for_typeId...`). This avoids guessing the payload type from register width alone.

### Calculation and guards

- At `0xb478b4/0xb478bc`, `MopDirtyAccumulator::tick()` constructs the literal key `turbidity_clean_area` for the internal hash-map access. Its setup uses `BT::TreeNode::blackboard()` at `0xb478d0` and a hash operation at `0xb47958`.
- At `0xb47444..0xb47460`, a `float` derived from an integer Blackboard state is scaled by `400.0` and added to an existing `float` value or its zero default. The accumulated value is held in `s8`.
- The condition at `0xb47638` can send execution to the `0xb488f4..0xb48930` virtual-set path rather than the normal `0xb47640..0xb47674` virtual-set path.
- At `0xb47c24..0xb47c2c`, the code constructs a `float` with IEEE-754 bits `0x447a4000` (**`1001.0f`**) in stack slot `+0xfc`. Subsequent branches can use this sentinel via the third virtual setter or typed setter.
- At `0xb47c48..0xb47c50`, a comparison of accumulated `s8` against `20.0f` can branch to the typed `float` setter. This branch is itself reached only through preceding guards; **it does not imply every accumulated value above 20 is published on each invocation**.
- The comparison and early exits demonstrate that publishing is guarded. We have not reduced the entire 9272-byte function to an exhaustive truth table for every failure, missing input, or exception branch.

### Important type question for subsequent work

**The compiled writer uses both double-backed `SafeAny` and typed float publication for the same key.** Other relevant consumers identified in v58 use typed float getters (`CalTurbidArea`, `SendMap`) or a low-level Blackboard lookup followed by a single-precision load (`CheckIfNeedReClean`). Whether the particular Blackboard implementation and its `SafeAny` conversion rules normalize these values correctly across each writer/reader pairing must be examined before concluding there is a type mismatch or a compatible dataflow. Neither outcome is yet proven.

If the sentinel `1001.0` reaches the v58 `CheckIfNeedReClean` index-calculation path as an ordinary number, that consumer's documented `0..20` clamp would select index 20. This is **conditional interpretation**, not an observed runtime chain and not proof that any particular writer and reader share the same Blackboard.

## Updated model

v58 established consumers and an unresolved route-side hash lookup. **v59 resolves one direct native producer:**

1. `MopDirtyAccumulator::tick()` has conditionally reachable setters for `turbidity_clean_area` (this audit).
2. `CalTurbidArea::tick()` and `AvaNodeRoute::SendMap()` have read sites for the same literal key (v58).
3. `CheckIfNeedReClean()` reads or defaults its value, uses it in the dynamic B-table index, then attempts to erase the key (v58).
4. The above **does not establish** runtime pointer identity between the route node and the tactics library's Blackboard. `PresetBlackboard`, `WashErrorLogicRun` and `WashFloorTubidityCheck` have additional erase sites.
5. The separate `special_push_clean_dish` eligibility key is still only known to have a direct native setter model-gated to non-R2416 models. An alternative R2416-reachable writer remains unproven. Thus, **physical turbidity-triggered automatic mop rewash is still not demonstrated**.

## Verification

The standalone standard-library verifier `x40_r2416_v59_mop_dirty_accumulator_producer_verify.py` retains and executes v54–v58 instruction and SHA checks, and adds:

- Exact producer key literal and `ADRP`+`ADD` address verification.
- More than 60 individual AArch64 instruction anchors across the four Blackboard setters, accumulator arithmetic, type setup and guard branches.
- Branch destination checks for conditional setter selection and typed setter PLT target.
- Parsing the ELF's own `.rela.dyn` and `.dynsym` to verify the double `linb::any` vtable relocation identity at `0x124ec30`.
- Rejection of a deliberately altered original producer `blr` instruction (`0xb47674`) and the inherited independent SHA tamper test.

This is offline binary static proof only; it does not execute any firmware or communicate with the robot.

Expected proof markers include:

```
X40_V58_TURBIDITY_BLACKBOARD_PROVENANCE_STATIC_PASS
X40_V59_MOP_DIRTY_ACCUMULATOR_PRODUCER_STATIC_PASS
X40_V59_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V58_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V58_SHA_TAMPER_REJECTION_PASS
```

Run:

```bash
python3 x40_r2416_v59_mop_dirty_accumulator_producer_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

## Recommended v60 focus

Trace the low-level `BlackboardLocal::set` / `get` and `SafeAny` conversion path for `turbidity_clean_area`, distinguishing `double`-backed setter writes from `get<float>` and the tactics-side low-level `float` load. Next, prove (or bound the absence of) concrete shared Blackboard pointer lineage between `MopDirtyAccumulator`, the route-node consumers and the station-wash tactics. Continue searching independently for an R2416-reachable `special_push_clean_dish` initializer.

**Safety:** Retain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not write to the robot or flash proprietary firmware to reproduce this analysis.