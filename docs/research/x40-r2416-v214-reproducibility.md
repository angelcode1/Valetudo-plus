# X40 R2416 v214 — reproducibility, privacy and next evidence

**27 October 2026.** Read-only original firmware analysis continuing v213. The complete release ZIP contains only versioned source, sanitized results and test fixtures. No original ELF, unredacted robot setting, map, process ID, private diagnostic JSON or PRIVATE collector ZIP is committed.

## Complete offline source-only release

File: `X40-R2416-v214-sanitized-analysis-kit.zip`  
SHA-256: **`cecec623d89b38324c654eeeaaeb14678e0830885311a2343997c191fb75eaee`**

There are **58 ZIP entries including `SHA256SUMS.txt`**. From clean extraction, ZIP CRC, **57 SHA-256 file checks** and **11 focused v214 tests** passed. The kit bundles the complete Python 3 standard-library verifier/test chain from v197 through v214, current and historical sanitized reports, 45 exact new native instruction-word checks, 17 decoded call/conditional branch edges, three original plugin ABI checks, and the full inherited v213 199 name/GOT callback tests. Negative tests reject altered source ELF, changed opcodes and branch targets, missing native plugin export and unexpected extra imported tree-builder API. Output-file overwriting is refused.

```sh
cd ~/Downloads
unzip X40-R2416-v214-sanitized-analysis-kit.zip
cd x40-r2416-v214-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V214_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V214_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V214_OFFLINE_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V214_LIVE_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V214_SCOPE_SAN="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V214_SCOPE_PRI="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V214_PROCESS_SAN="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V214_PROCESS_PRI="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v214.py

python3 verify_x40_r2416_v214.py \
  --prior-zip "$X40_V214_PRIOR_ZIP" \
  --delta-zip "$X40_V214_DELTA_ZIP" \
  --offline-resolver-zip "$X40_V214_OFFLINE_ZIP" \
  --live-resolver-zip "$X40_V214_LIVE_ZIP" \
  --scope-sanitized "$X40_V214_SCOPE_SAN" \
  --scope-private "$X40_V214_SCOPE_PRI" \
  --process-sanitized "$X40_V214_PROCESS_SAN" \
  --process-private "$X40_V214_PROCESS_PRI" \
  --out "$HOME/Downloads/X40-R2416-v214-new-SANITIZED.json"
# X40_R2416_V214_NATIVE_PLUGIN_LOADER_ABI_PASS 45 17 3 199
```

The full verifier's `--out` must be a new file and is sanitized.

## Bounded independent GitHub checker

The separately tested `docs/research/x40-r2416-v214-tools/x40_r2416_v214_repo_check.py` is a standalone stdlib script needing only the owner's original PRIVATE archive. It SHA-pins five ELFs, checks **14 representative instructions**, the exact plugin entry and .so literals, and the three entry-point/ABI imports. It does **not** replay all 17 control edges or all 199 name/GOT-callback pairs; use the complete ZIP for those.

```sh
python3 docs/research/x40-r2416-v214-tools/x40_r2416_v214_repo_check.py \
 --prior-zip "$X40_V214_PRIOR_ZIP"
# X40_R2416_V214_REPO_PLUGIN_ABI_STATIC_PASS 3 14
```

## Exact evidence boundary

Original host code filters .so filenames and attempts `BehaviorTreeFactory::registerFromPlugin`. Original BT core code dynamically resolves and calls `BT_RegisterNodesFromPlugin` when available. The three known original plug-ins export the entry point. Only the tree plugin directly imports `registerTreeBuilder`, with 199 names and callback relocations verified by v213. This is **not** a live loaded-factory registry, not a proof of plugin load success, and not an exhaustive proof against dynamically registered aliases, indirect invocation, other loaded libraries or XML fallback. It does not establish physical AI-stain reclean or dock rewash.

**Next:** audit the factory's native-builder-vs-file-fallback condition and possible dynamic registration paths with the original libraries, rather than repeat filesystem scans. No additional robot collection or experimental activation required. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [technical report](x40-r2416-v214-native-plugin-loader-abi-2026-10-27.md) and [sanitized JSON](x40-r2416-v214-plugin-loader-SANITIZED.json).
