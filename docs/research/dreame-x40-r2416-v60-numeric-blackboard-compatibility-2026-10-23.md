# Dreame X40 R2416 — v60 float/double Blackboard numeric compatibility audit

**Date:** 2026-10-23  
**Scope:** Read-only static analysis of SHA-256-pinned original AArch64 firmware libraries, checked against the owner's byte-matched runtime tree libraries. **No** robot communication, firmware writes, MIOT calls, code injection, private source publishing or runtime modifications.

## Executive finding

**The mixed `double`/`float` representation of `turbidity_clean_area` is not intrinsically incompatible with the examined native readers.** v59 identified three double-backed `linb::any` writes and one typed `float` write in `switch_mode::MopDirtyAccumulator::tick()`. v60 verifies that the route `get<float>` reader and the tactics `CheckIfNeedReClean()` consumer each include explicit type checks and a compiled **double-to-float (`FCVT`) conversion path**, as well as their native float path.

This is a **static data-type compatibility result**, not a proof of shared live Blackboard identity, successful writes, read/write ordering, key retention, application-level eligibility or a second physical mop wash.

## Exact instruction-level evidence

| Library / consumer | Addresses | Proven operation |
|---|---|---|
| `liblethe_route_nodes.so`: `SafeAny::Any::cast<float>()` | `0x4c7c8c..0x4c7cdc` | Compares the actual value's runtime type against the `float` RTTI and loads `s0` for a float value |
| Same cast, double path | `0x4c7d74..0x4c7dd0` | Compares the actual type against `double` RTTI, loads `d0` at `0x4c7dc8`, performs `fcvt s0,d0` at `0x4c7dcc`, rejoins the shared return path |
| Route: `BT::Blackboard::get<float>()` | `0x51b4a8..0x51b514` | Checks float RTTI; returns a single-precision value (`ldr s0` at `0x51b50c`, `str s0` into result at `0x51b514`) |
| Same getter, double path | `0x51b588..0x51b718` | Checks double RTTI, loads `d0` at `0x51b710`, converts `fcvt s0,d0` at `0x51b714`, branches to the float-result assignment |
| `liblethe_tactics_tree.so`: `CheckIfNeedReClean()` | `0x253068..0x2530c8` | Checks `float` RTTI (`_ZTIf`) for the stored `SafeAny` and loads `s8` at `0x2530c8` |
| Same tactics consumer, double path | `0x253a88..0x253bbc` | Checks `double` RTTI (`_ZTId`), loads `d8` at `0x253bb4`, converts `fcvt s8,d8` at `0x253bb8`, branches to common calculation at `0x253944` |
| Route `BlackboardLocal::set()` | `0x4d9200..0x4d94f8` | Includes insert and existing-entry paths for `SafeAny` payloads; this check does not assume it canonicalizes the value to a float |

ELF relocation symbol identities independently checked:

| Library | Relocation slot | Symbol |
|---|---|---|
| Route | `0x12501a0` | `_ZTIf` (float RTTI) |
| Route | `0x124a5a8` | `_ZTId` (double RTTI) |
| Tactics | `0x3c5228` | `_ZTIf` (float RTTI) |
| Tactics | `0x3c5ed0` | `_ZTId` (double RTTI) |

Each slot is an `R_AARCH64_GLOB_DAT` relocation (type 1025) with zero addend in the pinned binary. These RTTI resolutions matter: interpreting a 64-bit load or branch alone would not demonstrate the represented numeric type.

### What v60 resolves and does not resolve

- **Resolves:** The route typed getter and tactics recheck both have a compiled path to read a valid double-backed value as a float. The separate typed-float producer matches the checked native float read paths.
- **Resolves:** The tactics recheck is **not** float-only: although its first path loads a float directly, its cold branch at `0x253a24` contains a real RTTI-guarded double conversion, verified at `0x253bb4–0x253bbc`.
- **Does not resolve:** Whether `MopDirtyAccumulator` and tactics `CheckIfNeedReClean` share the same concrete `BlackboardLocal` at runtime. Same key spelling and compatible types are insufficient.
- **Does not resolve:** Whether numeric boundary values (NaN, infinity, overflow, precision loss), exceptions, missing keys or concurrent erase/write ordering alter behaviour. An explicit `fcvt` is not an unconditional guarantee that every possible value is suitable for the downstream index logic.
- **Does not resolve:** R2416 eligibility key `special_push_clean_dish`. Previously documented writer remains gated to other model identifiers. The turbidity failure marker can still be erased before that eligibility gate is checked.
- **Does not prove:** Any on-device execution, rewash request acceptance, dock command or physical second wash.

## Reproduction and safety

The accompanying standard-library-only verifier includes the previous v54–v59 SHA/instruction regression tests and v60 type/branch/relocation checks. It tests changed conversion opcodes in **each** of the two producer/consumer libraries, as well as a modified SHA-pinned ELF.

```bash
python3 x40_r2416_v60_blackboard_numeric_conversion_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected new markers:

```
X40_V60_FLOAT_DOUBLE_READ_COMPATIBILITY_STATIC_PASS
X40_V60_ROUTE_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V60_TACTICS_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V60_SHA_TAMPER_REJECTION_PASS
```

The verifier does not connect to the robot. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.

## Recommended v61

Trace **runtime Blackboard pointer provenance** from the compiled `RobotNode` and `StationWash` subtrees to `MopDirtyAccumulator` and `CheckIfNeedReClean`. In parallel, audit the existing `special_push_clean_dish` consumer's model gate and plausible nonliteral writers. Avoid mistaking common key names for shared Blackboard identity; avoid treating a compiled numeric conversion as a live cleaning test.