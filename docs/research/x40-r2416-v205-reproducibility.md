# X40 R2416 v205 — reproducibility and privacy boundary

**27 October 2026.** Extends v204, preserving the v195 native-`RobotNode` correction. All work used read-only private offline firmware archives. No robot collection, runtime action, firmware write or modification to `master`.

Complete kit: **`X40-R2416-v205-sanitized-analysis-kit.zip`**

SHA-256: **`102f2965bf2f773230f7dfe429ee0f98f0811b1c8eb1191b9c9c933314ae32c1`**

This source-only ZIP includes the full v197–v205 standard-library Python 3 verifier chain and v198–v205 focused tests, sanitized v205 report/JSON, native instruction anchors and SHA-256 manifest. It has **27 entries**, including the manifest; all **26 per-file hashes** and ZIP integrity passed. An independent clean extraction passed **all 11 v205 tests** and inherited v197–v204 regressions, checking five whole-ELF pins and 18+7 saved-payload SHA digests.

```sh
unzip X40-R2416-v205-sanitized-analysis-kit.zip
cd x40-r2416-v205-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V205_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V205_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v205.py
python3 verify_x40_r2416_v205.py \
 --prior-zip "$X40_V205_PRIOR_ZIP" \
 --delta-zip "$X40_V205_DELTA_ZIP" \
 --out "$HOME/Downloads/X40-R2416-v205-new-SANITIZED.json"
# X40_R2416_V205_REUSE_PATH_STATIC_PASS
```

Only specify a fresh `--out` path; overwrite is refused. Inputs remain private and are never packaged into the ZIP.

## Smaller standalone GitHub checker

The companion `x40-r2416-v205-tools/x40_r2416_v205_repo_check.py` has no external dependency. It pins two original ELF SHA-256s, **21 exact native words**, **eight decoded branch/call targets**, the `reuse` and path separators, the native generated `StationWash.xml` parameter and the absence of a contiguous static `reuse/StationWash` literal. It passed on the owner-private original ZIP.

```sh
python3 docs/research/x40-r2416-v205-tools/x40_r2416_v205_repo_check.py \
 --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V205_REPO_REUSE_BOUNDARY_STATIC_PASS 21 8
```

**Do not overinterpret:** An unprefixed `StationWash.xml` does not opt in to creating a cached entry on a miss, but may still reuse a prior populated key. Active node registration, live cache contents, route/station Blackboard identity, actual cache lifetime fault, AI-stain-to-task-start and physical extra wash/reclean remain unverified. Keep experimental CleanGenius writes disabled and proprietary robot evidence out of GitHub.

See [v205 research](x40-r2416-v205-reuse-prefix-stationwash-2026-10-27.md) and [v205 sanitized JSON](x40-r2416-v205-reuse-prefix-SANITIZED.json).
