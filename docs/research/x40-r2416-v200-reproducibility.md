# X40 R2416 v200 — reproducibility

**27 October 2026.** Branch extends v199, v198, v197, and v195 corrective research. The robot and `master` remain unchanged.

## Repository-side bounded replay

This self-contained, Python 3 standard-library checker requires the **two locally held private collector ZIPs**, not checked-in raw firmware or unredacted configuration:

```sh
python3 docs/research/x40-r2416-v200-tools/x40_r2416_v200_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip" \
  --delta-zip "$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
# X40_R2416_V200_REPO_JSON_NATIVE_ORDER_PASS
```

The repository-side checker validates **44 exact instruction anchors, 8 decoded branches/calls**, original host ELF SHA-256, the saved redacted calibration JSON SHA-256, literal table keys, and the ordered A-series labels and lengths. It is a bounded subset of the full offline suite.

## Full v197–v200 standalone verification kit

`X40-R2416-v200-sanitized-analysis-kit.zip`

SHA-256 `959d8d77932e9632a1dc7c9002b57ae7809ba9fab904efaa0be25a031aa55b37`

It contains complete v197/v198/v199/v200 stdlib-only replay sources, fixed native anchor constants, focused regression tests, a sanitized machine-readable result, research findings and checksum manifest. The ZIP has **13 files including its manifest**. Its 12 per-file SHA-256 checks and ZIP CRCs passed.

```sh
unzip X40-R2416-v200-sanitized-analysis-kit.zip
cd x40-r2416-v200-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V200_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V200_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v200.py
python3 verify_x40_r2416_v200.py \
  --prior-zip "$X40_V200_PRIOR_ZIP" \
  --delta-zip "$X40_V200_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v200-new-SANITIZED.json"
# X40_R2416_V200_NATIVE_JSON_ARRAY_ORDER_STATIC_PASS
```

Choose a fresh output path. Existing reports are not overwritten. Against the two private owner-provided ZIPs, all **10** focused v200 tests passed, full v197–v199 replay passed, five original ELF SHA-256 pins and 18+7 saved-payload checks passed, and the new v200 checker validated **143** AArch64 instruction anchors and **18** decoded control-flow/call edges. Changed original ELF hash, changed native instruction, altered A-array order, altered JSON labels and attempted report overwrite were rejected.

**Interpretation limit:** The saved JSON has A[0]–A[3] in array order and the compiled loader appends those arrays in order. The station controller conditionally uses a bounds-checked subtype index in v199. Neither observation is a live measurement of subtype, effective A calibration, dynamic Blackboard equality or physical second cleaning/washing. Keep experimental CleanGenius writes disabled.

See [v200 findings](x40-r2416-v200-native-json-series-order-2026-10-27.md) and [sanitized JSON evidence](x40-r2416-v200-json-array-order-SANITIZED.json).
