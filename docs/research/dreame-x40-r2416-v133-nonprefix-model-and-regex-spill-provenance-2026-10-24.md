# X40 R2416 v133 — non-prefixed primary model comparisons and stack-spill provenance

**24 October 2026 · offline, owner-private original firmware and sanitized v128 model identity only.** No device connection, control write, proprietary ELF/Android binary redistribution, private MODEL string or original configuration published.

## New native comparison census

The earlier strict AArch64 `std::string::compare(char const*)` census recognized **294** x20 primary-model comparison sites only when the literal began `dreame.`, `mova.` or `mijia.`. The exact original compiled instruction pattern actually occurs **297** times. Three additional comparisons have the same verified x20 input, ADRP/ADD literal address, typed comparison PLT call and immediate CBZ/CBNZ branch but a different literal prefix. All three literal operands are source-digest-pinned and **none matches the owner-derived exact model** (privacy-preserving original site `site_0x473540`).

| Original typed compare | Source branch | Impossible successor for actual MODEL | Writer effect |
|---|---|---|---|
| `0x472afc` | `0x472b00` CBZ | `0x4707f8` | Excludes the local positive assignment to `SP+0x100`; no additional flag writer eliminated |
| `0x47305c` | `0x473060` CBZ | `0x470758` | Constrains another model path; no additional flag writer eliminated |
| **`0x476534`** | **`0x476538` CBNZ** | **`0x47653c`** | Excludes possible direct flag writer **`0x476598`** |

This lowers the bounded native `[SP+0xBC]` direct writer set from **11 to 10**. Each branch was tested in isolation to ensure only the third removes a writer. Remaining static candidates:

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

All ten retain previously source-verified bounded positive-value sources. These are **possible instruction locations, not observed executions or a measured live Boolean**.

## Shared stored-regex consumer analysis

The v132 no-match regex at `0x472b3c` directly stores its low-byte result **zero** to `SP+0x100` at `0x472b44`. The only other inventoried direct 32-bit store into `SP+0x100` is a `MOVZ #1` source at `0x4707f8` followed by store at `0x4707fc`. The newly constrained nonmatching branch `0x472b00` makes this positive store unreachable from function entry. The v133 backwards **reaching last-direct-store** traversal at consumer `0x4710bc`, filtered to nodes forward reachable from entry, therefore reaches only `0x472b44`. The reader's branch is `0x4710c0`.

This is a bounded source/direct-store result; no claim about indirect pointer aliases or live runtime stack memory. It does not eliminate another turbidity eligibility flag writer. `SP+0x98` still has competing reaching values; **no global source value is assumed**. `SP+0x80`'s specific shared later consumer at `0x4782d4` is unreachable in the already source-constrained graph, but this does not prove other uses of the same slot.

## Reproducibility

The separately provided sanitized ZIP **`X40-R2416-v133-sanitized-nonprefix-model-spill.zip`**, SHA-256 **`8148200b25dacb080e792244a72b2d2ee71e45d06bc63febccb0a9d827363712`**, contains `x40_r2416_v133_nonvendor_model_spill_verify.py`, full v112–v132 sanitized regression dependencies, technical report, aggregate results JSON, README, SHA256SUMS.

```sh
unzip ~/Downloads/X40-R2416-v133-sanitized-nonprefix-model-spill.zip -d ~/Downloads
cd ~/Downloads/x40-v133-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v133_nonvendor_model_spill_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Verified **from a fresh extraction**:

```text
X40_V133_TEN_ORIGINAL_ELF_SHA256_PINS_PASS count=10
X40_V133_EXTENDED_PRIMARY_LITERAL_COMPARISON_CENSUS_PASS total=297 added=3
X40_V133_SOURCE_BOUND_NONMATCH_BRANCHES_PASS count=3
X40_V133_FLAG_WRITER_REDUCTION_PASS before=11 after=10 removed=0x476598
X40_V133_DIRECT_SP100_ZERO_REACHING_SOURCE_PASS source=0x472b44 consumer=0x4710bc
X40_V133_SP80_SHARED_RESULT_CONSUMER_UNREACHABLE_PASS scoped=bounded_cfg
X40_V133_ORIGINAL_SOURCE_MUTATIONS_REJECTED count=24
LIMIT: 10 static candidate direct stores, no executed instruction / live turbidity enablement / physical second wash
```

All **24 distinct single-byte mutations** of original typed comparison instructions, source literals and stack-result producer/consumer instructions are independently rejected **without relying on a whole-file ELF SHA mismatch**. One shared source literal is mutated only once; it is not double counted. Ten original ELF SHA-256 pins are checked separately.

## Next

Resolve `SP+0x98` competing reaching definitions with path-sensitive source proof, plus final last-direct-store order. Do not claim an executed address or runtime turbidity eligibility without actual deterministic native path proof or safe bounded observation. No genuine dirt-triggered **second physical mop wash** has been proven.

**Unchanged robot state:** last operator-confirmed Valetudo+ v74, SmartHost=0, `writeGateOpen=false`, original launcher and all rollback assets. No robot commands, no executable Valetudo change, no `master` change.
