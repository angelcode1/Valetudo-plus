# Dreame X40 R2416 — v129 live-model comparison-site branch and execution boundary

**24 October 2026 · owner-supplied sanitized model-site evidence, offline original AArch64 ELF verification.** No robot access, runtime tracing, firmware modification, or private native binary publication.

## New evidence

The operator-provided `X40-R2416-v128-model-compare-site-20261024T112745Z.zip` passed ZIP integrity, exact two-member schema, and privacy checks. It reports the original firmware comparison-site identifier **`site_0x473540`**, a valid JSON runtime model read, `MODEL` coarse category `other_vendor_model`, and top-level `DEV_MODEL` category `absent`. No model string or original configuration is exported.

This site resolves **uniquely** against the 235 model strings and 294 compiled comparisons in the owner's original SHA-256-pinned `node_lethe.so`: it belongs to one of seven compiled **R2416-family variants**. The exact device-derived model literal remains private. All ten original firmware ELF SHA-256 source pins passed.

## Pinned native match path

| Original `node_lethe.so` VA | Compiled role |
|---|---|
| `0x473534–0x47353c` | Prepare primary-model `x20` and literal arguments |
| `0x473540` | Typed `std::string::compare(char const*)` PLT call `0x27ac00` |
| `0x473544` | `CBZ w0`: model-equality branch to `0x472968` |
| `0x472968–0x47296c` | Regex-object destructor through PLT `0x2737a0` |
| `0x472970` | Unconditional branch to common model setup at `0x470914` |

**This matched branch does not itself write the native `SP+0xBC` turbidity model-group flag.** Its cleanup and return to common initialization explain why finding the correct model comparison is not equivalent to finding a flag writer. These are original compiled control-flow edges, **not runtime observations**.

Using the exact model privately associated with the uploaded site, the v128/v129 source-pinned model CFG was recomputed across **294 strict comparisons and 23 native regex-result branch anchors**. It still permits **13 potential direct flag-writer sites** before the guarded native `enable_turbidity` setter: one zero-valued source and 12 locally positive sources (v124–v125). The downstream flag guard remains reachable. No single instruction can be labelled *executed* from this static result.

v127's observation that `DEV_MODEL` is absent in the JSON source does not itself prove the native missing-key fallback return value or a particular runtime branch. Model-specific aliases, indirect reads/writes, initialization order, final Blackboard values and a genuine dirt-triggered **second physical mop wash** remain unverified.

## Repeatable verification

The operator-side sanitized archive **`X40-R2416-v129-sanitized-live-model-branch.zip`** (SHA-256 `e20ab95eb4d3f91ea1439f78fe7f770ddf3dbf7deb1024403dc8c6880e3d9fca`) contains standalone Python-standard-library `x40_r2416_v129_model_site_branch_verify.py`, its sanitized v112–v128 dependency scripts, the full technical report, sanitized JSON, README and checksum manifest. Proprietary vendor binaries and native model values are **not** included or committed.

```sh
unzip ~/Downloads/X40-R2416-v129-sanitized-live-model-branch.zip -d ~/Downloads
cd ~/Downloads/x40-v129-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v129_model_site_branch_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Actual offline verification:

```text
X40_V129_MUTATION_TEST_PASS native_instruction_sites=8 evidence_schema_cases=8
X40_V129_SOURCE_PIN_PASS original_elves=10 strict_comparisons=294
X40_V129_LIVE_MODEL_SITE_PASS native_site=site_0x473540 unique=true
X40_V129_MATCH_BRANCH_AND_CLEANUP_PASS common_model_setup=true
X40_V129_ACTUAL_MODEL_CFG_PASS possible_direct_writers=13 gate_reachable=true
LIMIT: no single native flag writer is proven to have executed; no physical rewash evidence
```

The verifier rejects **eight independently modified original instruction sites** without relying on whole-file SHA mismatch, and rejects **eight malformed or inconsistent evidence records**. It performs no robot I/O.

## Next proof gate

Investigate the **native return for an absent `DEV_MODEL` key**, and pursue path-sensitive conditional/last-writer analysis. If the native branch condition remains ambiguous, the fact that one instruction **actually executed** would require an appropriately authorized, safe runtime observation—not a guessed address. Do not force it by attaching a debugger to the production `ava` process, changing SmartHost/write gates, or issuing guessed station commands.

**Safety unchanged:** last verified working Valetudo+ v74, native SmartHost=0, experimental `writeGateOpen=false`, original launcher and rollback files intact; GitHub `master`, executable Valetudo code and the robot remain unchanged.
