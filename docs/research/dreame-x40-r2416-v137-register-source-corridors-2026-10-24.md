# Dreame X40 R2416 — v137 positive register source and branch corridor verification

**24 October 2026. Read-only offline original vendor firmware (ten SHA-256-pinned ARM64 ELF libraries) plus privacy-preserving owner model site evidence.** No robot, cloud, firmware or Valetudo runtime operations.

## New bound

The previous v136 source-specific direct GPR stack-store/explicit-pointer audit still permitted **ten** model-specific possible final stores of the `SP+0xBC` native turbidity eligibility word. v137 provides an executable, source-pinned **register-preservation** check, supplementing earlier v124/v125 local positive `MOVZ #1` source coverage.

For each of the ten possible store sites, the v137 source-constrained CFG makes that store **unreachable** if all of its checked positive-register initializers are cut. Seven sites have one such source, and three (`0x474cd0`, `0x4773dc`, `0x4775a4`) have two alternative positive initializer paths already identified and pinned by v125. For those three, native alternative jumps into the shared block are separately checked.

Native direct source-to-store code is partitioned into **16 contiguous instruction corridors**, including branch-entry shared-block segments. Both every individual source/store instruction opcode and the original bytes across the complete set of 16 corridor slices are pinned with feature-specific SHA256 digests. A deliberately narrow AArch64 instruction-family decoder checks that all **97** non-initializer/crossed instructions in the corridors preserve the relevant `W0`, `W23` or `W24` source register. The decoder recognizes only the actual original instruction families: `MOVZ W`, `MOV W/X` (ORR aliases), non-writeback `STR W`/`STP W`, `CBZ/CBNZ`, `B` and `BL`, and **refuses unfamiliar opcodes** rather than pretending they are non-clobbering.

The only two unique calls crossed on the audited segments, at `0x4774b8` and `0x47824c`, carry the positive source in **AAPCS64 callee-saved `W24` or `W23`**; the caller-saved `W0` source corridors cross **zero** function calls. Correctness for those two calls is conditional on normal AArch64 ABI compliance.

These tests strengthen v135b's conclusion about **positive direct-store value sourcing** within the modeled local native code. They do **not** shrink the set of ten possible stores or identify an actually executed one.

## Ten still-possible source-verified direct flag stores

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

The actual exact model identity is privately identified by the original native comparison site `site_0x473540`, without publishing the literal string. The original valid-JSON missing `DEV_MODEL` normal return route and prior exact-model/regex branch constraints are retained. The bounded path count from v135b remains **35 abstract terminal combinations**, not 35 real events.

### Evidence that remains missing

This is not full alias-aware memory SSA or an interprocedural proof. It cannot rule out implicit pointer aliases, nonlocal writes by called functions, unmodeled exceptional control flow, changed runtime configuration, mismatching native Blackboard scopes or unknown hardware state. No unique **executed** native flag writer, effective live `enable_turbidity` state, dirt-triggered rewash event or **second physical mop wash** has been observed. Do not infer any of those outcomes from positive compiled writer source coverage.

## Reproducibility

The separately delivered owner-side **sanitized** `X40-R2416-v137-sanitized-register-source-corridors.zip`, SHA-256 **`8ac6e6d6e4d0bca9b0f1aef605eb34bebe72025ba3e3947dd15a088204b5a560`**, contains:

- `x40_r2416_v137_register_corridor_verify.py`: standalone Python-stdlib original-ELF and source-preservation verifier;
- all required v112–v136 sanitized regression modules;
- full technical report, sanitized results JSON, README and SHA256SUMS.

It requires the operator's original owner-private v62 firmware ZIP and previously produced privacy-safe v128 model-site ZIP **only as local inputs**, neither bundled nor published.

```sh
unzip ~/Downloads/X40-R2416-v137-sanitized-register-source-corridors.zip -d ~/Downloads
cd ~/Downloads/x40-v137-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v137_register_corridor_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

A clean-extraction replay passed ZIP integrity, the full SHA256SUMS manifest and the original source checks:

```text
X40_V137_TEN_ORIGINAL_SHA256_ELF_PINS_PASS count=10
X40_V137_ALL_TEN_MODEL_WRITERS_HAVE_POSITIVE_SOURCE_CUT_PASS
X40_V137_NATIVE_REGISTER_CORRIDORS_PINNED_PASS corridors=16
X40_V137_ABI_CALL_PRESERVATION_AUDIT_PASS callee_saved_calls=2
X40_V137_CORRIDOR_REGISTER_WRITES_AUDITED_PASS instructions=97
X40_V137_MUTATED_SOURCE_INSTRUCTIONS_REJECTED count=25
X40_V137_SYNTHETIC_CLOBBER_DECODER_TESTS_PASS count=7
LIMIT: no uniquely executed writer, live effective turbidity switch, or physical second wash proven
```

**25** independent source-instruction mutations to the ten stores, positive setters and three alternate branches were rejected without treating a full-file ELF hash mismatch as the feature test. **Seven** synthetic decoder tests exercise MOVZ/register clobbers, benign stores, caller-saved vs callee-saved calls and unknown-opcode refusal.

## Next

Investigate the *actual* target Blackboard scope and indirect/memory-writing effects between the guarded source and the later station controller, or plan an expressly authorized **read-only, bounded, low-impact runtime observation** if purely static proof cannot select a uniquely executed store. Do **not** force native flags, enable SmartHost, issue guessed station opcodes, install intrusive instrumentation on production hardware, or fake contamination.

**Safety preserved:** last operator-confirmed Valetudo+ v74, SmartHost=0, experimental `writeGateOpen=false`, original launcher/rollback files intact. GitHub `master`, runtime code and robot were not modified.
