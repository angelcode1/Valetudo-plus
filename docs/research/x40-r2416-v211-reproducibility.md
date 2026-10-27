# X40 R2416 v211 — complete offline reproducibility and optional process-cwd probe

**27 October 2026.** All uploaded scope, firmware and resolver PRIVATE evidence stays local. This branch descends from v210, not `master`, and changes no robot state.

## Complete source-only offline kit

`X40-R2416-v211-sanitized-analysis-kit.zip`  
SHA-256: **`778330bb07cd217b24483999e02f25256cb96fb996bf2006f49c4384177c4b30`**

Contains **51 files including SHA256SUMS.txt**, all historical Python 3 stdlib v197–v211 verifiers and tests, `verify_x40_r2416_v211.py`, `test_verify_x40_r2416_v211.py`, `collect_x40_r2416_v211_process_cwd.py`, sanitized v211 finding and README. A clean extraction passed all **50 per-file SHA256 checks**, ZIP CRC, **14 focused v211 tests**, and the full inherited v197–v210 native regression replay with five original whole-ELF SHA pins. No original native ELF, private matching paths or uploaded owner-private ZIP or JSON appears in the release package.

```sh
unzip X40-R2416-v211-sanitized-analysis-kit.zip
cd x40-r2416-v211-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V211_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V211_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V211_OFFLINE_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V211_LIVE_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V211_SCOPE_SAN="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V211_SCOPE_PRI="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
python3 -m unittest -v test_verify_x40_r2416_v211.py
python3 verify_x40_r2416_v211.py \
 --prior-zip "$X40_V211_PRIOR_ZIP" \
 --delta-zip "$X40_V211_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V211_OFFLINE_ZIP" \
 --live-resolver-zip "$X40_V211_LIVE_ZIP" \
 --scope-sanitized "$X40_V211_SCOPE_SAN" \
 --scope-private "$X40_V211_SCOPE_PRI" \
 --out "$HOME/Downloads/X40-R2416-v211-new-SANITIZED.json"
# X40_R2416_V211_LIVE_SCOPE_STATIC_PASS 4 70 6 0
```

The `--out` path must not exist; overwrite is refused.

Small repository-side SHA-pinned metadata cross-check:

```sh
python3 docs/research/x40-r2416-v211-tools/x40_r2416_v211_repo_check.py \
 --scope-sanitized "$X40_V211_SCOPE_SAN" --scope-private "$X40_V211_SCOPE_PRI"
# X40_R2416_V211_REPO_SCOPE_CONSISTENCY_PASS 70 6 0
```

## Optional, owner-authorized read-only process working-directory diagnostic

The directory reports already cover four roots to depth eight and found no `AiStainMop`-named paths. The remaining file-resolution ambiguity is the actual process cwd. On the owner's Mac, optionally run **after extracting the kit**:

```sh
python3 collect_x40_r2416_v211_process_cwd.py \
 --ssh root@ROBOT_IP \
 --out-prefix "$HOME/Downloads/X40-R2416-v211-process"
```

Replace `ROBOT_IP` and choose whether to run SSH. This script reads only Linux process mapping *presence*, read-only cwd symlink metadata, and existence status of four candidate relative paths. No ELF, XML, config, logs, camera content, maps or model weights are collected. No firmware modification, commands to clean, or AVA/MIOT publish. It emits a LOCAL `-PRIVATE.json` (PIDs/cwd, chmod 0600) and `-SANITIZED.json` (counts only), both create-only. The script was fixture-tested but **not run against the robot**.

Even a zero-candidate result would not establish lack of other names, roots, dynamically registered subtrees, or effective file-fallback execution. No actual `AiStainMop` live resolution or stain-triggered physical second cleaning pass is demonstrated. Keep experimental gates off.

See [sanitized v211 research](x40-r2416-v211-live-scope-cwd-2026-10-27.md) and [structured finding](x40-r2416-v211-live-scope-SANITIZED.json).
