# Dreame X40 R2416 — v123 delayed regex-result turbidity model gate

**24 October 2026 · offline SHA-256-pinned original AArch64 ELF research.** No robot I/O, firmware settings writes, proprietary source redistribution or runtime changes.

## Finding

v122 reduced a bounded intraprocedural `ProcessModelInfo()` model-group gate census to **17** potential direct 32-bit SP-relative writer sites overlapping `SP+0xBC`. The program later reads this byte/word field before guarded typed Blackboard `enable_turbidity` initialization.

v123 verifies **nine additional native `std::regex_match()` result-to-branch paths**, which v122's immediate-result scanner had not audited. Each is separately anchored to an exact compiled ECMAScript regex literal, constructor, typed `regex_match` call fed by the model argument at `[x20]`, low-byte mask, and a later CBZ/CBNZ. Some paths preserve the result across C++ regex destructors in callee-saved `w21`, `w22` or `w24`; one explicitly spills the mask to `SP+0xF8` and reloads that same slot before the branch. The intervening native instructions are checked through *local* window signatures, separately from whole-original-ELF SHA-256 pins, to prevent unknown clobbers. The nine regex patterns all **fail to match the bare exact `dreame.vacuum.r2416` name**.

| `regex_match` site | Delayed consumer | Verified result path |
|---|---|---|
| `0x4703c4` | `0x4703d4` | masked `w24`, destructor, CBNZ |
| `0x4721b0` | `0x4721bc` | masked `w0`, stack store, CBZ |
| `0x474494` | `0x4744b4` | masked `w24`, destructor, CBZ |
| `0x4745c0` | `0x4745e0` | masked `w1` moved to `w21`, two destructors, CBNZ |
| `0x474784` | `0x474794` | masked `w24`, destructor, CBZ |
| `0x47498c` | `0x4749a4` | masked `w1` moved to `w21`, destructor, CBZ |
| `0x474d20` | `0x474d50` | masked `w1` spilled to/reloaded from `SP+0xF8`, CBZ |
| `0x4757e4` | `0x4757f4` | masked `w22`, destructor, CBZ |
| `0x478654` | `0x47866c` | masked `w1` moved to `w21`, destructor, CBNZ |

Applying only those verified outcomes to the v122 CFG **eliminates four direct writer candidates**: `0x471a90`, `0x474500`, `0x474578`, `0x474958`.

Thirteen possible direct sites remain: `0x4703fc`, `0x474cd0`, `0x475bc4`, `0x4761c4`, `0x476598`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

**Limits:** these are possible *direct store instruction sites*, not live writes or proven values. Exact R2416 model-match success can still reach the `enable_turbidity` guard. Alternate regex/group conditions, indirect stores, unmodelled aliases, runtime Blackboard scopes and effective native turbidity feature eligibility remain unresolved. No genuine dirt-triggered **second physical mop wash** has been established.

## Reproducibility

The separately delivered owner-side sanitized package `X40-R2416-v123-sanitized-delayed-regex-model-gate.zip` (SHA-256 `196f36d85ccd4852a5cb398933bf8dcba9fe475760a383259755a7eedb0287d4`) includes the complete Python-standard-library `x40_r2416_v123_delayed_regex_cfg_verify.py`, its v112–v122 sanitized dependencies, detailed report, results JSON and checksum manifest. Original owner-private `X40-R2416-v62-readonly-20261023T051829Z.zip` is required as **private input** and is not included or committed.

```sh
cd ~/Downloads
unzip X40-R2416-v123-sanitized-delayed-regex-model-gate.zip
cd x40-v123-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v123_delayed_regex_cfg_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verified:
```text
X40_V123_TEN_ORIGINAL_ELF_SHA256_PINS_PASS count=10
X40_V123_V122_REGEX_CFG_REGRESSION_PASS candidates=17
X40_V123_NINE_DELAYED_REGEX_RESULT_BRANCHES_PASS matching=0 nonmatching=9
X40_V123_PRUNED_MODEL_FLAG_DIRECT_WRITERS_PASS remaining=13 eliminated=4
X40_V123_R2416_MATCH_STILL_REACHES_GUARD_NO_DIRECT_POSTMATCH_WRITER_PASS
X40_V123_INDEPENDENT_NATIVE_SOURCE_MUTATIONS_REJECTED count=44
LIMIT: remaining 13 possible direct sites do NOT prove live turbidity eligibility or a second physical wash
```

44 source-level single-location mutations of original instruction or literal bytes were rejected by scoped source assertions/local flow pins, not by whole-file-hash mismatch alone.

**v124 next:** trace the remaining thirteen source sites and actual reaching flag value, constraining only source-verified model predicates. Avoid guessed station commands, synthetic contamination or setting writes. Keep working Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher, rollback assets and repository `master` untouched.
