# X40 R2416 v131 — primary/secondary native regex gate refinement

**24 October 2026 · Offline original firmware only.** Original ten SHA-256-pinned AArch64 ELF files and the owner-uploaded *sanitized* native model comparison evidence were verified locally. No robot I/O, settings write, patch, private model disclosure or vendor binary export.

## New reproducible result

v130 established the normal native missing-`DEV_MODEL` empty-string fallback and kept **13** possible direct stores to `[SP+0xBC]` in `node_lethe.so:ProcessModelInfo()`. v131 audits **four additional compiled `std::regex_match()` call→result→conditional-branch paths** not previously included in the 23 v122/v123 regex branches. Each has its original ECMAScript constructor, exact literal, source operand, typed `regex_match` call, low-byte `ANDS/TST`, conditional opcode/target and complete constructor-to-branch instruction corridor SHA-256 pinned.

| Regex call | Native input | Source branch | Source-proven no-match outcome | Candidate impact |
|---|---|---|---|---|
| `0x4721f0` | primary `MODEL` via `[x20]` | `0x472200` B.NE | fallthrough | none |
| `0x4738dc` | primary `MODEL` via `[x20]` | `0x4738e8` B.EQ | take `0x4739c4` | none |
| `0x476228` | secondary `DEV_MODEL` via `[SP+0x240]` | `0x476238` B.EQ | take `0x4762ac` | **exclude `0x4761c4`** |
| `0x476d24` | secondary `DEV_MODEL` via `[SP+0x240]` | `0x476d34` B.EQ | take `0x476d58` | none |

The source-pinned actual native primary model comparison is `site_0x473540` (its private exact model literal is **not** disclosed). Two foreign-model regex literals cannot match that model. The other two foreign-model patterns cannot match the **empty secondary string** on v130's normal successful JSON lookup with absent top-level `DEV_MODEL` (as reported by v127).

Reapplying all 294 original strict primary-model comparisons, the original 23 audited regex branches, the v130 three secondary comparison outcomes, and these **four** new results reduces the conservatively reachable direct flag-writer set from **13 to 12**.

The `0x476238` constraint **alone**, added on top of v130 constraints, gives the same one-site exclusion. It does not require assuming that the comparison at `0x476254` executes or succeeds.

The 12 remaining bounded possible sites are:
`0x4703fc`, `0x474cd0`, `0x475bc4`, `0x476598`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

**Limits:** 27 of 31 `regex_match` call outcomes are now anchored. The other four have more complex or reused result handling and were not pruned. Bounded direct AArch64 CFG paths are **possible code routes**, not an executed instruction trace or evidence of the live `enable_turbidity` Boolean. One zero-source store and eleven locally positive-store candidates remain. No dirt-triggered **second physical mop wash** has been proven.

## Standalone reproducibility

The separately supplied operator-side sanitized ZIP `X40-R2416-v131-sanitized-cross-input-regex-gate.zip` (SHA-256 `27473b17002ee5429ebe58b2d233cd46c2dabf87d4bd488b4ad479b9d61979a9`) contains the Python-stdlib verifier `x40_r2416_v131_cross_model_regex_gate_verify.py`, all v112–v130 sanitized regression dependencies, aggregate JSON, full report, README and checksums. No original ELF, APK, runtime config or credentials are included.

```sh
unzip ~/Downloads/X40-R2416-v131-sanitized-cross-input-regex-gate.zip -d ~/Downloads
cd ~/Downloads/x40-v131-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v131_cross_model_regex_gate_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Confirmed source verification:

```text
X40_V131_TEN_ORIGINAL_SHA256_ELF_PINS_PASS count=10
X40_V131_V130_EXACT_MODEL_AND_EMPTY_DEV_MODEL_REGRESSION_PASS candidates=13
X40_V131_FOUR_DIRECT_NATIVE_REGEX_RESULT_BRANCHES_PASS primary=2 secondary=2
X40_V131_SECONDARY_REGEX_ISOLATED_PRUNING_PASS excluded=0x4761c4
X40_V131_MODEL_AND_SECONDARY_REGEX_CFG_PASS remaining=12
X40_V131_INDEPENDENT_MUTATIONS_REJECTED source=24 evidence=5
LIMIT: 12 possible direct sites, NOT an executed store or physical second wash
```

24 single-location vendor-instruction/literal mutations are independently rejected by source-specific checks **without using original whole-file checksum mismatch as the test oracle**. Five malformed source-identity-evidence cases are rejected. Ten original vendor ELF SHA-256 pins are validated separately.

**Safety baseline unchanged:** last operator-confirmed Valetudo+ v74, SmartHost=0, writeGateOpen=false, original launcher and all rollbacks intact; GitHub `master`, unrelated branches, executable runtime code and robot unchanged.
