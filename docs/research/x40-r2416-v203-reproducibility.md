# X40 R2416 v203 — reproducibility and private-evidence boundary

**27 October 2026.** Extends v202 and retains the v195 native `RobotNode` correction. No robot access, AVA/MIOT writes, running Valetudo+ changes or `master` changes.

## Self-contained source-only offline archive

File: `X40-R2416-v203-sanitized-analysis-kit.zip`  
SHA-256: **`66c767868bd1ba63da6569bbd1a62ba5dbcf64d61667384622c4f23d78145d0f`**.

The ZIP has **22 files including its checksum manifest**. The **21 per-file SHA-256 checks** and ZIP CRC validation passed; extraction into a clean folder and the v203 test suite passed (11 focused tests). It contains the *complete v197–v203 Python 3 standard-library-only verifier chain*, tests, v203 instruction anchor map, sanitized research finding and machine-readable JSON. No original vendor ELFs, firmware archives, robot maps, credentials, video or unredacted configurations are distributed.

```sh
unzip X40-R2416-v203-sanitized-analysis-kit.zip
cd x40-r2416-v203-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V203_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V203_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v203.py

python3 verify_x40_r2416_v203.py \
  --prior-zip "$X40_V203_PRIOR_ZIP" \
  --delta-zip "$X40_V203_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v203-new-SANITIZED.json"
# X40_R2416_V203_CACHE_LIFETIME_STATIC_PASS
```

The report output must be a new path; overwriting is deliberately blocked.

The replay on the owner-private ZIPs passed all prior v197–v202 regressions, five original native ELF SHA-256 pins, and **18+7 saved collector payload checksums**. New v203 coverage comprises **63 exact native word anchors**, **20 decoded native edges**, a 352-byte destructor direct-call census, cache initialization, raw map pointer store, cached root attach and tree owner release. Negative tests reject altered ELF hash, altered native instruction, wrong branch target and report overwrite.

## Smaller standalone checker committed to this branch

`docs/research/x40-r2416-v203-tools/x40_r2416_v203_repo_check.py` imports the inherited v202 repo checker and requires the owner's private initial ZIP locally. It checks **25 of the v203 exact instruction anchors, nine branches including the static initializer guard, map symbol and bounded destructor direct-call census**, in addition to the inherited v202 checks. It is deliberately not a substitute for the full kit.

```sh
python3 docs/research/x40-r2416-v203-tools/x40_r2416_v203_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V203_REPO_CACHE_LIFETIME_STATIC_PASS
```

**Interpretation:** Static process-lifetime cache plus node-owner deletion reveals a conditional pointer lifetime hazard. No runtime use-after-free, cache hit after owner destruction, stale Blackboard, physical second wash, or AI-stain-triggered new floor task has been observed. Unknown indirect cleanup and actual node lifecycle remain open. Keep experimental writes disabled and never upload original firmware to the public repository.

See [v203 sanitized research](x40-r2416-v203-process-static-tree-cache-2026-10-27.md) and [v203 machine-readable evidence](x40-r2416-v203-static-cache-SANITIZED.json).
