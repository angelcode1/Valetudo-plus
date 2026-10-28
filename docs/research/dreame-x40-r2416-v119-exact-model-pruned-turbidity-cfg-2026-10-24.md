# Dreame X40 R2416 — v119 exact-model-pruned turbidity source-flag CFG

**24 October 2026 · offline, SHA-256-pinned original ELF analysis; sanitized for the public research fork.** No live device access, firmware or configuration changes, MIOT writes or proprietary ELF redistribution.

## Verified finding

The full original `node_lethe.so:ProcessModelInfo()` has 45,380 code bytes / **11,345 AArch64 instructions**. In the v118-bounded direct SP-relative 32-bit STP/STR census, **61 instruction sites** write the `[SP+0xBC]` model-group flag subsequently used to guard `enable_turbidity` via a typed `BT::Blackboard::set<bool>` at `0x47185c`.

v119 constructs an intraprocedural AArch64 branch/fallthrough graph (B, B.cond, CBZ/CBNZ, TBZ/TBNZ, BL/BLR fallthrough, terminal RET/BR), and recognizes **294 strict five-instruction exact model-compare patterns**. Each pattern uses the model argument in preserved register `x20` (initialized by `mov x20,x8` at `0x46fd60`), a literal ADRP+ADD, the linked `std::string::compare(char const*)`, and an immediately following CBZ/CBNZ of `w0`.

Only one such comparison names `dreame.vacuum.r2416`, at `0x47093c` with match branch `0x470940 → 0x470958`. The other **293** name different models. Under the explicit exact-model input assumption `dreame.vacuum.r2416`, the impossible equality edge at each foreign-model comparison can be pruned without making any claim about regex or model aliases.

| Bounded analysis | Verified count |
|---|---:|
| Full-function instructions | 11,345 |
| Direct SP+0xBC word/pair writer sites | 61 |
| Strict model-name compare patterns | 294 |
| Foreign-model equality branches removed | 293 |
| Remaining direct writer sites reachable on a CFG route from entry to the R2416 compare | **20** |
| Direct writers eliminated by bounded model-name constraints | **41** |
| Direct writer sites reachable from R2416 match-success into downstream guard | **0** |

Two earlier example positive initializers, `0x47227c` and `0x47373c`, are eliminated: their controlling exact-name comparisons are respectively for `dreame.vacuum.r2316o` and `dreame.vacuum.r2310`, not the R2416 model. The R2416 match can reach the downstream flag guard but does **not itself write this flag**; the value must be inherited from prior initialization paths.

## Precise limits

The remaining 20 are **potential writer instruction sites, not 20 actual executions or 20 distinct models**. They include direct initialization sites and broader model-group/regex paths. The analysis leaves nonexact comparisons, regex semantics, secondary model aliases, indirect stack-slot aliases, callback/nonlocal effects and runtime state **unconstrained**. This is a conservative narrowing of direct-static candidates only; it neither proves R2416's native `enable_turbidity` state is true nor that R2416 is excluded.

The continued gap to genuine automatic rewash remains: real turbidity-failure condition → eligible native station state → `r2343_start_rewash` → an additional physical mop wash. No such live sequence has been observed.

## Reproduction

The owner-delivered sanitized `X40-R2416-v119-sanitized-model-pruned-cfg.zip` contains `x40_r2416_v119_model_pruned_cfg_verify.py`, its v112–v118 sanitized regression modules, full report, JSON, README, and SHA256SUMS. It uses **Python 3 standard library only** and requires an owner-private `X40-R2416-v62-readonly-20261023T051829Z.zip` input, which **must never be committed**.

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v119_model_pruned_cfg_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Observed:

```text
X40_V119_TEN_ORIGINAL_SHA256_PINS_PASS count=10
X40_V119_V118_MODEL_GATE_REGRESSION_PASS
X40_V119_FULL_FUNCTION_DIRECT_WRITER_CENSUS_PASS count=61
X40_V119_STRICT_MODEL_COMPARISON_CENSUS_PASS total=294 foreign=293
X40_V119_R2416_PRUNED_PRIOR_WRITER_BOUND_PASS candidates=20 eliminated=41
X40_V119_NO_DIRECT_WRITER_AFTER_R2416_MATCH_PASS scoped=intraprocedural_cfg
X40_V119_INDEPENDENT_SOURCE_MUTATIONS_REJECTED count=36
LIMIT: regex/group branches and indirect sources not resolved; R2416 eligibility, native runtime values and second wash NOT proven
```

The self-test rejects 36 independently mutated original instructions without relying on full-file SHA rejection; original input verification separately pins ten ELF SHA-256 hashes.

## Next: v120

Evaluate regex/group predicates governing the remaining 20 direct stores for the exact R2416 name, including any documented secondary alias semantics. Do **not** substitute guessed model values or infer runtime Blackboard remapping or a second physical wash from compiler control flow. Authentic `StationWash.xml` was not present in the private v62/v63 original captures.

**Unchanged baseline:** last-confirmed working Valetudo+ v74, `SmartHost=0`, experimental `writeGateOpen=false`, original launcher and recovery artifacts intact. No device actions, runtime code or proprietary vendor data in this commit.
