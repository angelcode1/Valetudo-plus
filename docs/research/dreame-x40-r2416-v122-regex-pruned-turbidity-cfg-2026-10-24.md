# Dreame X40 R2416 — v122 native regex-aware model gate

**24 October 2026 · offline analysis, SHA-256-pinned original ELF evidence.** No robot I/O, app/cloud access, firmware change or proprietary source redistribution.

## Summary

v119 conservatively narrowed 61 direct 32-bit SP-relative writer instruction sites for the model-group turbidity eligibility flag at `SP+0xBC` to 20 candidates by pruning impossible *exact-name* comparisons for the known input `dreame.vacuum.r2416`.

v122 adds 14 **verified local C++ ECMAScript regex result branches** from the original `node_lethe.so:ProcessModelInfo()` function. Each audited site has a regex literal passed to the constructor, a typed `std::regex_match()` call whose string input is loaded from the preserved model-input register `x20`, and an immediate test of the low result byte by `ANDS/TST` followed by a `B.eq` branch, possibly separated by one flag-preserving word store. Nonlocal regex-result usages were not pruned.

The **bare** R2416 model matches 2 audited regex expressions and does not match 12. Thus these 14 branch outcomes can be used to further prune the exact-model CFG without guessing nonlocal branch conditions.

| Static analysis boundary | Verified result |
|---|---:|
| Original vendor ELF source pins | 10 of 10 |
| v119 prior direct writer candidates | 20 |
| Additional locally grounded regex-result decisions | 14 |
| Matched by `dreame.vacuum.r2416` | 2 |
| Not matched | 12 |
| Further excluded direct writer sites | **3** |
| **Remaining possible direct writer sites** | **17** |
| Source instruction/pattern mutations independently rejected | 36 |

A significant model-specific distinction: the native pattern `dreame\\.vacuum\\.r2416\\w?` matches the bare model name because the suffix is *optional*, while `dreame\\.vacuum\\.r2416[afc]` requires an extra character and does not match the bare name. Literal substring matching would be unsound here.

The additional eliminated writer addresses are `0x4785c4`, `0x47869c` and `0x478720`.

Remaining bounded direct instruction sites: `0x4703fc`, `0x471a90`, `0x474500`, `0x474578`, `0x474958`, `0x474cd0`, `0x475bc4`, `0x4761c4`, `0x476598`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

The exact R2416 comparison still has a path to the downstream `enable_turbidity` guard and has **no identified direct `SP+0xBC` store after its successful comparison**. The final input-flag value depends on earlier model-group logic, not on a name match alone.

## Limits

The remaining 17 addresses are potential direct source sites, **not** proved writes or runtime executions. Other regex results, alternative input aliases, indirect stores, exception paths, unmodelled branch dependencies, native Blackboard remapping and actual station runtime state are unconstrained. Neither native R2416 turbidity enablement nor a dirt-triggered second physical mop wash has been proven.

The companion v121 static Dreamehome split-APK analysis shows a generic device-plugin framework, but the APK installer itself contains no demonstrated R2416-specific downloaded plugin or live capability response. No Android-private plugin/cache collection occurred in v122.

## Repeatable verification

The sanitized owner-side download **`X40-R2416-v122-sanitized-regex-model-gate.zip`** contains the standalone Python standard-library verifier `x40_r2416_v122_regex_gate_cfg_verify.py`, v112–v119 regression dependencies, report, aggregate JSON, README and SHA256SUMS. Owner-held private `X40-R2416-v62-readonly-20261023T051829Z.zip` is an input, not included.

```sh
cd x40-v122-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v122_regex_gate_cfg_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Confirmed local output:

```text
X40_V122_TEN_ORIGINAL_SHA256_PINS_PASS count=10
X40_V122_V119_EXACT_MODEL_CFG_REGRESSION_PASS candidates=20
X40_V122_BOUNDED_NATIVE_REGEX_CONDITIONS_PASS tests=14 matching=2 nonmatching=12
X40_V122_R2416_REGEX_PRUNED_WRITERS_PASS remaining=17 eliminated=3
X40_V122_NO_DIRECT_WRITER_AFTER_EXACT_R2416_MATCH_PASS
X40_V122_INDEPENDENT_SOURCE_MUTATIONS_REJECTED count=36
LIMIT: remaining 17 direct writer candidates do not establish R2416 native enable_turbidity or physical rewash
```

The 36 source mutation cases modify 14 original branch instructions, 14 regex call instructions and eight original regex literal bytes. Mutations are rejected using feature-specific checks **without relying on whole-file SHA mismatch**; original ELF SHA pins are validated separately.

## Next

Constrain longer-lived regex results/aliases and explicit flag value propagation to the remaining 17 candidate sites. Do not infer support merely because a model-group regex matches, and do not issue guessed native station commands. The missing real turbidity failure → `r2343_start_rewash` → **extra physical mop wash** causality remains open.

**Safety unchanged:** last operator-confirmed working Valetudo+ v74, `SmartHost=0`, experimental `writeGateOpen=false`, original launcher, fallbacks and all rollback assets intact. No live device or repository runtime changes.
