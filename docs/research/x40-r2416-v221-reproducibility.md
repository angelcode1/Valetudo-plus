# X40 R2416 v221 — full source-only reproducibility and proof limits

**27 October 2026.** Research-only branch descends from v220. The robot, firmware, Valetudo+ runtime, experimental feature flags and GitHub `master` are unchanged. Original private ELFs, raw configuration, user collector ZIPs, process paths, PID/network identifiers and maps remain external inputs.

## Complete offline research kit

**`X40-R2416-v221-sanitized-analysis-kit.zip`**

SHA-256: **`28d2e493a30851e9baec88e4168576f646bfa530df7cdb78ff2406607d014636`**. Size: **215,356 bytes**; **97 ZIP entries**, including `SHA256SUMS.txt`. A fresh extraction passed ZIP CRC, **96/96 file hashes and all 13/13 focused v221 tests**, including the full original-native/private-evidence **v197–v220** chain. All scripts use Python 3 standard library. No original vendor ELF or owner PRIVATE ZIP is in the release.

```sh
cd ~/Downloads
unzip X40-R2416-v221-sanitized-analysis-kit.zip
cd x40-r2416-v221-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V221_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V221_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V221_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V221_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V221_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V221_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V221_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V221_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v221.py
python3 verify_x40_r2416_v221.py \
 --prior-zip "$X40_V221_PRIOR_ZIP" \
 --delta-zip "$X40_V221_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V221_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V221_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V221_SCOPE_SANITIZED" \
 --scope-private "$X40_V221_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V221_PROCESS_SANITIZED" \
 --process-private "$X40_V221_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v221-new-SANITIZED.json"
# X40_R2416_V221_AI_HANDLERS_STATIC_PASS 52 12 9 5 2
```

The full verifier refuses to overwrite existing output and writes only sanitized metadata; tests verify redaction of source paths, IP, PID and working directory. Unit tests run on the original evidence locally; on the owner's Mac, set `X40_V221_*` environment variables above.

## Bounded standalone repo checkout checker

`docs/research/x40-r2416-v221-tools/x40_r2416_v221_repo_check.py` needs **only the original owner PRIVATE collector ZIP** and no third-party dependencies. It SHA-pins the original host ELF, checks **24 representative exact instruction words**, five named literals, five positive direct-BL targets and zero direct calls from **either complete original AI handler body** to the four selected task-stack and named AI-send functions. The equivalent standalone checker bundled in the ZIP was run successfully on the original private firmware.

```sh
python3 docs/research/x40-r2416-v221-tools/x40_r2416_v221_repo_check.py \
 --prior-zip "$X40_V221_PRIOR_ZIP"
# X40_R2416_V221_REPO_AI_HANDLERS_BOUNDARY_PASS 24 5 0
```

Use the **complete ZIP** for all 52 instruction anchors, 12 direct-BL targets, nine conditional branch edges, typed-Blackboard and async-queue semantics, 13 native mutation/negative tests and v197–v220 replay.

## Exact result, without overstating it

`ProcessAiStrategy` has compiled `RobotAiSwitch` / `current_motion_type` / `Followwall` logic. `ProcessAiCleanBot` has compiled guarded `online_pqklfilename` and `ai_model_info` access plus an asynchronous callback queue notification path, involving `deque<function<void()>>`, `notify_one` and `write`. No direct `BL` in either exported body targets `TasksStackPush`, `SendAINewCmd`, `SendAITurbidityValue` or `BtTask::Run`. The verifier rejects an artificially added direct stack push even outside the pinned instruction anchors.

**These functions may still schedule work indirectly.** A native virtual callback, another loaded library, an async queue consumer, an alias or other production task state machine is not excluded. No same-instance runtime Blackboard proof, stain-caused task enqueue, second floor clean or dock rewash has been obtained. Do not treat the conditional queue operations as an observed robot action.

**Next:** inspect downstream async callback consumers and genuine production cleaning-task start/publication interface; distinguish from v219's separate debug stack. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Keep all proprietary original binaries PRIVATE and `master` unchanged.

See [v221 detailed native findings](x40-r2416-v221-production-ai-handlers-2026-10-27.md) and [sanitized JSON](x40-r2416-v221-production-ai-handlers-SANITIZED.json).
