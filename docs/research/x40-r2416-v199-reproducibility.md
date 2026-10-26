# X40 R2416 v199 reproducibility

**27 October 2026.** This research branch extends v198 and retains the v195 native-`RobotNode` correction. No firmware/robot writes or `master` changes. Do not merge any private ELF or unredacted configuration into the public repo.

## Repo-side bounded check

```sh
python3 docs/research/x40-r2416-v199-tools/x40_r2416_v199_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V199_REPO_SUBTYPE_INDEX_STATIC_PASS 26 new word anchors 2 new edges
```

This standalone standard-library checker reuses the inherited v198 repo checker, SHA-pins the original tactics ELF, checks **26 new instruction words and two decoded edges** relating to A/B/C lookup records and subtype indexing, and prints no private data. Those checks are a deliberately smaller **repository-side** subset, not the full v199 replay.

## Full offline kit

File: `X40-R2416-v199-sanitized-analysis-kit.zip`. SHA-256: **`f441a20707261428a7796023edf787b09ff6482e32277f460225484c22437bcb`**.

Self-contained ZIP with the full v197, v198 and v199 verifier sources, `anchor_constants.py`, v198 and v199 tests, redacted machine result and detailed finding. Original proprietary firmware and private collector ZIPs are **not included**.

```sh
unzip X40-R2416-v199-sanitized-analysis-kit.zip
cd x40-r2416-v199-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V199_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V199_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v199.py
python3 verify_x40_r2416_v199.py \
  --prior-zip "$X40_V199_PRIOR_ZIP" \
  --delta-zip "$X40_V199_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v199-new-SANITIZED.json"
# X40_R2416_V199_NATIVE_TABLE_LAYOUT_STATIC_PASS
```

Offline replay passed with the two owner-private collector archives: **18 + 7** collected saved-byte SHA-256 checks, five original native ELF whole-file SHA-256 pins, all v197–v198 checks, **152** v199 additional native instruction anchors, **17** decoded additional branch edges, **10** focused v199 tests including 3 synthetic tests and 7 original-evidence tests; changed instruction, changed whole ELF, wrong calibration shape, unordered keys and output overwrite were rejected. Archive CRC and its **9** per-file checksums passed (ZIP contains 10 files including `SHA256SUMS.txt`).

Owner-claimed SSH provenance of deployed config from the collector manifests is not an independently authenticated SSH transcript. The running subtype value is not observed. A compiled subtype-to-A-vector branch is *not* proof of active 40-series calibration or a physical rewash. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [research finding](x40-r2416-v199-a-subtype-lookup-layout-2026-10-27.md) and [sanitized machine evidence](x40-r2416-v199-subtype-lookup-SANITIZED.json).
