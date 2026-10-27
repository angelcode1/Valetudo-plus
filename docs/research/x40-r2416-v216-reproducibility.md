# X40 R2416 v216 — reproducible source-only research handoff

**27 October 2026.** Research branch descends from v215; `master`, robot firmware and the running Valetudo+ installation remain unchanged. All original native ELFs, private collector archives, process metadata, maps, credentials and raw settings remain external PRIVATE inputs.

## Complete downloadable offline kit

File: **`X40-R2416-v216-sanitized-analysis-kit.zip`**  
SHA-256: **`839547a633bc18afe19f26f7659470a91d8ddca6dddceb4f6d9f2fac116aa85e`**  
Size: **156,681 bytes**. **68 ZIP entries**, including `SHA256SUMS.txt`. Fresh-extraction validation passed ZIP CRC, **67/67 internal file SHA-256 checks** and **12/12 v216 focused tests**, including complete v197–v215 original-native/private-evidence regression replay. No original firmware bytes included.

The main verifier checks **42 exact original AArch64 instruction words, 18 decoded call/branch targets, 160 generated node instantiations, 160 push-back calls, 159 child attachments, and 158 distinct generated `reuse/` subtree parameter tables**. Mutations of AlwaysSuccess's returned status, Fallback's early success branch, generated parent/child order, trailing child count and `reuse/AiStainMop` path table are rejected. Reports are sanitized and create-only.

```sh
cd ~/Downloads
unzip X40-R2416-v216-sanitized-analysis-kit.zip
cd x40-r2416-v216-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V216_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V216_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V216_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V216_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V216_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V216_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V216_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V216_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v216.py
python3 verify_x40_r2416_v216.py \
 --prior-zip "$X40_V216_PRIOR_ZIP" \
 --delta-zip "$X40_V216_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V216_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V216_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V216_SCOPE_SANITIZED" \
 --scope-private "$X40_V216_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V216_PROCESS_SANITIZED" \
 --process-private "$X40_V216_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v216-new-SANITIZED.json"
# X40_R2416_V216_REUSETREE_TICK_SHORT_CIRCUIT_STATIC_PASS 42 18 160 160 159 158
```

The `--out` destination must be **new**; overwrite is refused.

## Smaller, independent GitHub checker

`docs/research/x40-r2416-v216-tools/x40_r2416_v216_repo_check.py` is Python 3 stdlib-only and only needs the original PRIVATE collector archive. Its source was independently tested against the original owner evidence. It checks **22 representative exact native words**, original whole-file SHA pins, Fallback/AlwaysSuccess names, three generated creation/attachment positions, success control, and **160/160/159** generated calls. Use the ZIP's main verifier for the **full 42/18, all 158 subtree names, 12 mutation tests and historical replay**.

```sh
python3 docs/research/x40-r2416-v216-tools/x40_r2416_v216_repo_check.py \
  --prior-zip "$X40_V216_PRIOR_ZIP"
# X40_R2416_V216_REPO_REUSETREE_TICK_ORDER_PASS 22 160 160 159
```

## Interpretation boundary and next step

The generated `ReuseTree` puts `AlwaysSuccess` first under its `Fallback` root. The inspected built-in `AlwaysSuccess` returns status 2, which the original `FallbackNode::tick` short-circuits. On that normal compiled path, the remaining 158 reused children, including `reuse/AiStainMop`, are **not ticked by the root**. Construction-time initialization and cache-placeholder creation remain possible; runtime behavior, dynamic registrations and other task-planner consumers are unmeasured.

The next meaningful offline task is the **non-ReuseTree native stain-area / extra-clean planner dispatch**. Do not equate a `reuse/` name, Blackboard state or generic `need_extra_clean` flag with an observed second physical pass. No additional robot collection is needed at this stage.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; keep private archives and firmware out of public GitHub.

See [v216 technical research](x40-r2416-v216-reusetree-fallback-short-circuit-2026-10-27.md) and [v216 sanitized JSON](x40-r2416-v216-reusetree-tick-SANITIZED.json).
