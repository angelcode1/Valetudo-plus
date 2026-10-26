# X40 R2416 v207 — reproducibility, private-input boundary and next evidence

**27 October 2026.** This v207 research branch extends v206 and preserves all v195–v206 corrections. The robot, firmware, live Valetudo+ installation and default `master` branch were not changed.

## Complete standalone source-only analysis

File: `X40-R2416-v207-sanitized-analysis-kit.zip`  
SHA-256: **`c829c327d2c7807faa84cfc8b14c9ea1f3296894fd8c229d670c911fb33d43a2`**

The ZIP contains **34 files including `SHA256SUMS.txt`**. It passed clean-extraction ZIP CRC validation and all **33 per-file SHA-256 checks**, plus all **nine** focused v207 unit tests when the owner's two private input ZIPs were available. It contains the full Python 3 stdlib-only v197–v207 regression/verifier chain, prior test modules, v207 original AArch64 anchors, an ELF64LE dynamic-symbol parser, an exact 158-child/199-export/138-match/20-unmatched census, a sanitized report and complete machine-readable results. No vendor native ELF, unredacted configuration, proprietary model weight, map, video or robot-secret payload is included.

```sh
unzip X40-R2416-v207-sanitized-analysis-kit.zip
cd x40-r2416-v207-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V207_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V207_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v207.py

python3 verify_x40_r2416_v207.py \
  --prior-zip "$X40_V207_PRIOR_ZIP" \
  --delta-zip "$X40_V207_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v207-new-SANITIZED.json"
# X40_R2416_V207_NATIVE_AISTAIN_RESOLUTION_STATIC_PASS
```

The report output must be a fresh path; overwrite is intentionally refused. The complete v197–v206 verification rechecks **five original whole-file ELF SHA256 pins** and **18 + 7** saved payload checksums; v207 adds **22 native instruction word anchors**, **nine decoded BL targets** and typed, bounds-checked `.dynsym` name parsing. Changed-ELF, changed-instruction, changed-branch and changed-expected-builder-census negatives all fail deliberately.

## Bounded repository-side executable checker

This branch includes `docs/research/x40-r2416-v207-tools/x40_r2416_v207_repo_check.py`, reusing the inherited SHA-pinned `x40-r2416-v206-tools/x40_r2416_v206_repo_check.py` and implementing an independent `.dynsym` coverage census.

```sh
python3 docs/research/x40-r2416-v207-tools/x40_r2416_v207_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V207_REPO_NATIVE_AISTAIN_EXPORT_CENSUS_PASS 158 199 138 20
```

The locally tested bounded checker printed exactly those numbers. Use the standalone ZIP for **full** inherited tests.

**Interpretation:** `buildAiStainMop` is missing from the defined *exported* dynamic symbols of the single original `liblethe_tree.so`. This is not proof of missing installed XML, no other plugin, failure at runtime, a cache bug, or a second physical cleaning pass. Do not enable experimental CleanGenius writes.

**Next private evidence, only if offline archives cannot resolve:** a small *read-only* inventory of installed tree-plugin filenames and direct `AiStainMop` resource paths, not a broad robot filesystem dump. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [v207 finding](x40-r2416-v207-aistain-builder-resolution-2026-10-27.md) and [machine-readable sanitized evidence](x40-r2416-v207-aistain-resolver-SANITIZED.json).
