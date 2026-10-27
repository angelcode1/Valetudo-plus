# X40 R2416 v219 — complete source-only offline reproducibility

**27 October 2026.** Research branch descends from v218; no robot contact, firmware write, live Valetudo+ changes, experimental CleanGenius activation, or changes to `master`. No owner-private ELF, ZIP, raw config, process data or map content published.

## Downloaded source-only kit

`X40-R2416-v219-sanitized-analysis-kit.zip`  
SHA-256: **`62b70968c651e9f14bf67191a0c7263692942c6a20bef31ba5ba00b3268ea6ab`**  
Size: **191,858 bytes**; **85 ZIP entries including manifest**, **84/84 SHA-256 payload checks**, ZIP CRC passed. Fresh extraction and **12/12 focused v219 tests** passed, including full inherited v197–v218 original firmware/private-evidence replay. All scripts use Python 3 standard library; original proprietary ELFs and private diagnostic inputs are external and not bundled.

```sh
cd ~/Downloads
unzip X40-R2416-v219-sanitized-analysis-kit.zip
cd x40-r2416-v219-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V219_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V219_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V219_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V219_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V219_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V219_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V219_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V219_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v219.py
python3 verify_x40_r2416_v219.py \
 --prior-zip "$X40_V219_PRIOR_ZIP" \
 --delta-zip "$X40_V219_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V219_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V219_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V219_SCOPE_SANITIZED" \
 --scope-private "$X40_V219_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V219_PROCESS_SANITIZED" \
 --process-private "$X40_V219_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v219-new-SANITIZED.json"
# X40_R2416_V219_NATIVE_DEBUG_TASK_STACK_BOUNDARY_PASS 51 33 10 3
```

The `--out` path must not exist; the verifier refuses overwrite. The resulting report contains no device identity, cwd, IP or private paths.

## Smaller independent repository checker

`docs/research/x40-r2416-v219-tools/x40_r2416_v219_repo_check.py` uses only the original collector ZIP to verify two original ELF SHA-256 pins, **30 direct host BL sites** to the DebugTask/Reset/Push trio and **three route BL sites** to Empty/Front/Pop, plus a virtual task method invocation, its continuation branch and actual host task-deque pointer advancement. The corresponding same-scope kit-local checker was run separately on the actual original ZIP and passed.

```sh
python3 docs/research/x40-r2416-v219-tools/x40_r2416_v219_repo_check.py \
 --prior-zip "$X40_V219_PRIOR_ZIP"
# X40_R2416_V219_REPO_DEBUG_TASK_STACK_PASS 30 3
```

For **all 51 exact opcode anchors, 33 sites, 12 negative/mutation tests, private evidence reconciliation and the entire historical chain**, use the complete release kit, not only the bounded repository checker.

## Scope and future evidence

The original host contains `TaskManager::TasksStackPush(BtTask&&)` and exactly ten **direct** push sites in the bounded host .text. Each is preceded by `DebugTask` construction and `TasksStackReset` from one of two named input handlers: `SignalCarpetProcessSUB` and `AppEditMap`. The original route plugin has exactly one direct Empty, Front and Pop caller apiece in `debug_mode::BtTaskExecutor::tick()`, including an indirect virtual call on the current task. **This is compiled debug-task plumbing**, not a verified autonomous CleanGenius scheduler.

No direct adjacency/ownership links the ten queue pushes to `AiStainCheck` or `SetExtraCleanArea`. Direct BL census cannot exclude aliases, indirect callbacks, other modules, a different scheduler or a live event path. No actual AI-stain-driven extra cleaning task, physical floor second pass or dock rewash has been observed.

**Next offline study:** production cleaning task root/state-machine transitions and their actual command/dispatch entry, not this debug task stack or generic CleanList copy. Keep original firmware and all PRIVATE evidence local. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [v219 technical findings](x40-r2416-v219-debug-task-stack-boundary-2026-10-27.md) and [v219 sanitized JSON](x40-r2416-v219-task-stack-SANITIZED.json).
