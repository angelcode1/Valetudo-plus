# Dreame X40 R2416 — v128 actual MODEL class and original native comparison identity

**24 October 2026 · fully offline analysis of uploaded sanitized v127 evidence and SHA-256-pinned original vendor ELF sources.** The new v128 remote collector was tested only on local synthetic data and **has not been run on a robot**. No firmware binaries, actual JSON configuration, raw credentials, device IDs or native actuator command values appear in this report or the companion kit.

## New observation

The operator supplied `X40-R2416-v127-json-model-evidence-20261024T105639Z.zip`. It passes archive/CRC checks and declares:

- `source_readable=true`, `source_format=json_object`
- `model_class=other_vendor_model`
- `dev_model_class=absent`
- `raw_config_exported=false`, `device_modified=false`

**Important correction:** `MODEL=other_vendor_model` is not the literal `dreame.vacuum.r2416` or `dreame.vacuum.r2416f`. The v127 classifier's broader vendor-model bucket may include different R2416 suffixes or other device-model names. It must **not** be treated as the exact native `dreame.vacuum.r2416` input used in v119–v125.

`DEV_MODEL=absent` is a literal top-level-key absence in the valid JSON snapshot; it does not independently prove how native `ReadModleInfo()` handles the missing value at runtime.

Therefore the v125 **13 possible direct writer sites** remain a valid *hypothetical exact-name source/CFG boundary*, **not** a claim about the live device's selected instruction or `enable_turbidity` value.

## Original native compiled model census

SHA-256 checking passed for **all ten** private original R2416 vendor ELF libraries. `node_lethe.so:ProcessModelInfo()` contains:

| Source-verified static census | Count |
|---|---:|
| Strict source-patterned direct model-name comparisons | **294** |
| Distinct compiled names | **235** |
| Native compiled `r2416` family names | **7** |
| Source-anchored audited native regex-result branches | **23** (14 immediate, 9 delayed) |

The seven compiled R2416-family names include the bare model and six suffixes. A separate source-pinned CFG regression evaluated each family name against all 294 strict compiled comparisons plus the 23 audited native regex branches, and **each model still admitted the same 13 potential direct `SP+0xBC` writer sites**. That is only a conservative CFG bound; none of those sites was observed executing.

## Targeted v128 read-only model comparison-site collector

The companion owner-downloadable `X40-R2416-v128-sanitized-model-identity-kit.zip` contains:

- `x40_v128_private_model_compare_id.py`: Python-standard-library collector that **locally** loads and SHA-pins the owner-private original ELF sources, derives all 235 native model names and their compiler comparison sites, and creates a temporary POSIX-AWK exact-equality table for SSH stdin. The robot reads only `/var/run/runava.conf` and returns a site identifier (`site_0x......`), `not_listed` or `not_classified`—**never** the raw native model string or configuration.
- `x40_r2416_v128_model_cfg_audit.py`: offline original-source/CFG verifier for seven family names and 23 audited regex source branches, without robot access.
- v112–v127 sanitized verifier modules, full report, aggregate-only JSON, README and a SHA256SUMS manifest.

A site identifier is an **exact compiled string-comparison reference**, not a native execution trace. Even a successful match cannot be equated with the execution of the `enable_turbidity` writer, a live native Blackboard value, or an additional physical mop wash.

The collector enforces the uploaded v127 observation, validates native site IDs against the SHA-pinned original comparison table, refuses changed/unexpected protocol fields, and keeps the actual `MODEL` string on-device. In synthetic tests it exported no tokens or serials. The configuration is never uploaded or written, and no guessed station command or MIOT property is transmitted.

### Repeat on the operator Mac

```sh
cd ~/Downloads
unzip X40-R2416-v128-sanitized-model-identity-kit.zip
cd x40-v128-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v128_private_model_compare_id.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v127 ~/Downloads/X40-R2416-v127-json-model-evidence-20261024T105639Z.zip \
  --self-test
python3 x40_r2416_v128_model_cfg_audit.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip
python3 x40_v128_private_model_compare_id.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v127 ~/Downloads/X40-R2416-v127-json-model-evidence-20261024T105639Z.zip \
  --host root@192.168.8.149 --out ~/Downloads
```

The optional SSH command has not been run by this assistant. Upload **only** the generated `X40-R2416-v128-model-compare-site-*.zip`, not the original JSON configuration.

### Offline verification

```text
X40_V128_NATIVE_COMPARISON_SOURCE_PASS original_elves=10 direct_comparisons=294 unique_names=235
X40_V128_V127_EVIDENCE_PASS model=other_vendor_model dev_model=absent
X40_V128_SELFTEST_PASS fixtures=6 protocol_refusals=6 synthetic_ssh=true secret_export=false no_device_io=true
X40_V128_OFFLINE_ORIGINAL_SOURCE_PASS elfs=10 strict_model_comparisons=294 unique_models=235
X40_V128_R2416_FAMILY_CFG_REGRESSION_PASS variants=7 possible_writers_each=13
X40_V128_NATIVE_REGEX_ANCHORS_PASS count=23
LIMIT: a compiled model comparison site is NOT an executed flag-writer instruction
```

The kit itself passed ZIP integrity and SHA256SUMS validation and contains no firmware or APK binaries. **Next:** use the category-only v128 evidence to identify the correct actual model's original comparison site and rebuild the bounded branch constraints. If multiple possible stores remain, only further source-conclusive analysis or expressly authorised safe runtime evidence—not an invented model name or an unobserved instruction—can establish which store executed.

**Preserved state:** last verified Valetudo+ v74, SmartHost=0, experimental `writeGateOpen=false`, original launcher and recovery backups intact; robot, runtime code, and `master` unchanged.
