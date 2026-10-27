# X40 R2416 v220 — complete source-only offline reproduction

**27 October 2026.** This branch descends from the v219 research branch, not `master`. It changes no robot state or running Valetudo+ code. Original owner-private ELF, configuration, process metadata, maps, private resolver ZIPs and identities remain external and are never distributed in the release or GitHub.

## Verified offline release

**`X40-R2416-v220-sanitized-analysis-kit.zip`**  
**SHA-256:** `e88521a11729c88fbad956c55f15662674a4bc0e61345a016e8d9e3b6e9fdac2`  
**Size:** 203,263 bytes. **91 ZIP entries including SHA256SUMS**, all **90 internal SHA-256 file checks** passed on clean extraction; ZIP CRC verified. **All 12 focused v220 tests passed in clean extraction**, including the complete **v197–v219 original native/private evidence regression chain**. All scripts are Python 3 standard-library-only. No original firmware binaries are included.

```sh
cd ~/Downloads
unzip X40-R2416-v220-sanitized-analysis-kit.zip
cd x40-r2416-v220-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V220_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V220_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V220_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V220_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V220_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V220_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V220_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V220_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v220.py

python3 verify_x40_r2416_v220.py \
 --prior-zip "$X40_V220_PRIOR_ZIP" \
 --delta-zip "$X40_V220_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V220_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V220_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V220_SCOPE_SANITIZED" \
 --scope-private "$X40_V220_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V220_PROCESS_SANITIZED" \
 --process-private "$X40_V220_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v220-new-SANITIZED.json"
# X40_R2416_V220_PRODUCTION_ODOMETRY_TICK_STATIC_PASS 32 7 3 10
```

The full verifier's output file must **not already exist**: opening with create-only mode enforces no overwrite. Output is sanitized; tests verify that it does not contain private IP, PID, cwd or archive path.

## Smaller independent GitHub audit

The standalone `docs/research/x40-r2416-v220-tools/x40_r2416_v220_repo_check.py` is a bounded standard-library-only checker requiring just the original owner PRIVATE collector ZIP. The matching standalone script in the downloadable kit was independently run against the original private evidence and passed **16 original native word anchors, three singleton planning/AI direct-BL call sites, and the inherited ten direct DebugTask stack pushes**. Use the complete release kit for 32-word, seven-target checks, tests, private evidence reconciliation and v197–v219 replay.

```sh
python3 docs/research/x40-r2416-v220-tools/x40_r2416_v220_repo_check.py \
 --prior-zip "$X40_V220_PRIOR_ZIP"
# X40_R2416_V220_REPO_PRODUCTION_ROOT_PASS 16 3 10
```

## Native boundary and next offline step

The `AvaNodeRoute` constructor builds the configured production root with the route Blackboard and stores that root at object offset `+0xf48`. The odometry callback calls `PlanningFuncInOdomProcess()`, which contains `ProcessAiStrategy()` and `ProcessAiCleanBot()` calls; later the callback reloads the retained `+0xf48` root, invokes its virtual vtable slot `+0x18` and processes the status. Static direct-call census independently confirms all three planning/AI call sites and the **ten unrelated direct debug task pushes**.

**This establishes a compiled main-tree tick route, not a stain-caused new cleaning-task transition**. Branches may divert execution. The specific AI handlers' Blackboard state changes, runtime execution order of `AiStainCheck` and `SetExtraCleanArea`, cross-library indirect dispatch, a physical second floor pass and dock rewash remain unverified.

**Next:** inspect the original `ProcessAiStrategy` and `ProcessAiCleanBot` implementations and their effective route Blackboard operations before inferring production task-start causality. Do not enable experimental CleanGenius as a diagnostic shortcut. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `writeGateOpen=false`.

See [v220 technical research](x40-r2416-v220-production-odometry-root-2026-10-27.md) and [sanitized JSON](x40-r2416-v220-production-root-SANITIZED.json).
