# X40 R2416 v215 — reproducibility and privacy-preserving research handoff

**27 October 2026.** Branch based on v214, not `master`. No live robot operation, firmware changes, Valetudo+ changes or experimental feature activation. All proprietary native ELFs, collector ZIPs, device settings and process details remain outside the public repository.

## Complete source-only replay

File: `X40-R2416-v215-sanitized-analysis-kit.zip`  
SHA-256: **`a2a3fa4580a1a1011d64c5b698df00e1a34ecef2958928787e0d9beb18d0edd7`**  
Size: **145,093 bytes**. **63 ZIP entries including SHA256SUMS.txt**. Fresh extraction passed ZIP CRC, **all 62 internal file SHA-256 checks**, **12 focused v215 tests**, and the complete inherited **v197–v214** Python 3 standard-library verifier replay against the owner's private original archives. The source-only archive includes all prior versioned verifier and unit-test modules, v215 report/JSON, and an additional small kit-local checker. No original vendor ELF or PRIVATE file is packaged.

```sh
cd ~/Downloads
unzip X40-R2416-v215-sanitized-analysis-kit.zip
cd x40-r2416-v215-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V215_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V215_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V215_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V215_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V215_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V215_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V215_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V215_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v215.py
python3 verify_x40_r2416_v215.py \
  --prior-zip "$X40_V215_PRIOR_ZIP" \
  --delta-zip "$X40_V215_DELTA_ZIP" \
  --offline-resolver-zip "$X40_V215_OFFLINE_RESOLVER_ZIP" \
  --live-resolver-zip "$X40_V215_LIVE_RESOLVER_ZIP" \
  --scope-sanitized "$X40_V215_SCOPE_SANITIZED" \
  --scope-private "$X40_V215_SCOPE_PRIVATE" \
  --process-sanitized "$X40_V215_PROCESS_SANITIZED" \
  --process-private "$X40_V215_PROCESS_PRIVATE" \
  --out "$HOME/Downloads/X40-R2416-v215-new-SANITIZED.json"
# X40_R2416_V215_REUSE_PLACEHOLDER_FALLBACK_STATIC_PASS 46 19 199
```

The generated `--out` report is **create-only** and sanitized; the full replay refuses to overwrite an existing file. v215 checks **46 original instruction words and 19 decoded AArch64 control-flow targets**, native `reuse` and missing-builder literals, plus all inherited 199 actual name/GOT builder callback registrations. Negative tests reject changed opcodes, branch targets, string literals, core or tree hashes, missing existing registration and report overwrite.

## Smaller GitHub checkout checker

The companion `docs/research/x40-r2416-v215-tools/x40_r2416_v215_repo_check.py` uses the inherited `docs/research/x40-r2416-v213-tools/x40_r2416_v213_repo_check.py` and is Python 3 stdlib-only. It passed separately on the owner-private original ELF ZIP. Its bounded scope is **20 exact instruction words, 12 decoded native edges and 199 registered name/export matches**; the complete ZIP is required for **all 46/19** checks, callback GOT relocation pairing and the historical v197–v214 replay.

```sh
python3 docs/research/x40-r2416-v215-tools/x40_r2416_v215_repo_check.py \
  --prior-zip "$X40_V215_PRIOR_ZIP"
# X40_R2416_V215_REPO_REUSE_FALLBACK_PASS 20 12 199
```

## Evidence limits and next priority

The opt-in generated `reuse/AiStainMop` path **can create a null cache entry and return on the first missing cache key**. On a later null entry, the core searches registered native tree builders and can emit ` is not a registered tree` before file fallback. **The conditional paths are compiled; they were not recorded executing on the running robot.** Thus no assertion that the feature is absent or broken, no live exception claim, and no stain-triggered second physical floor clean or dock rewash claim follows. Repeating directory scans without evidence of actual resolver entry is unlikely to help.

Keep all original firmware and PRIVATE diagnostics out of GitHub. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`, the running robot and `master`.

See [v215 research report](x40-r2416-v215-reuse-placeholder-builder-fallback-2026-10-27.md) and [sanitized machine evidence](x40-r2416-v215-reuse-placeholder-SANITIZED.json).
