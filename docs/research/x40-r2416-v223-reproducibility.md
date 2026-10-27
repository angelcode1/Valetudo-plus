# X40 R2416 v223 — complete source-only reproduction and evidence handoff

**27 October 2026.** Research branch descends from v222. Neither the robot, its running Valetudo+ installation, experimental safety gates nor GitHub `master` was changed. This repository contains only sanitized research and Python source. Original vendor ELF files, device settings, credentials, process paths, maps and uploaded owner PRIVATE ZIP/JSON reports are excluded.

## Verified complete offline kit

**`X40-R2416-v223-sanitized-analysis-kit.zip`**

SHA-256: **`df5dc8a0e3f28aaa4e89f1db46ffd670dbc941da3cb656359f90281e1e5634c1`**. Size: **236,932 bytes**. **109 archive entries** including `SHA256SUMS.txt`, **108/108 internal payload checksums** and ZIP integrity passed from fresh extraction. The original source-directory tests and the separately clean-extracted tests both passed **12/12 focused v223 cases**, including complete **v197–v222 original firmware/private evidence regression replay** (clean replay 56.894 seconds).

The bundle contains the complete inherited Python 3 standard-library-only verifier/test chain, `verify_x40_r2416_v223.py`, `test_verify_x40_r2416_v223.py`, `anchors_v223.py`, a standalone `x40_r2416_v223_repo_check.py`, full native report, sanitized result JSON, README, and checksums. No vendor library or owner-private collector inputs are included.

```sh
cd ~/Downloads
unzip X40-R2416-v223-sanitized-analysis-kit.zip
cd x40-r2416-v223-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V223_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V223_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V223_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V223_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V223_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V223_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V223_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V223_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v223.py
python3 verify_x40_r2416_v223.py \
 --prior-zip "$X40_V223_PRIOR_ZIP" \
 --delta-zip "$X40_V223_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V223_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V223_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V223_SCOPE_SANITIZED" \
 --scope-private "$X40_V223_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V223_PROCESS_SANITIZED" \
 --process-private "$X40_V223_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v223-new-SANITIZED.json"
# X40_R2416_V223_AI_COMMAND_SUBSCRIBER_STATIC_PASS 56 9 2 3 1
```

The `--out` target must be **new**. The verifier refuses overwriting existing reports; its output contains no private path/IP/PID or vendor file content.

The full release's independently tested standalone checker validates **22 exact original instructions, two GOT callback relocations, three code-to-key literal references and one outbound caller**:

```sh
python3 x40_r2416_v223_repo_check.py --prior-zip "$X40_V223_PRIOR_ZIP"
# X40_R2416_V223_REPO_CALLBACK_BOOLS_PASS 22 2 3 1
```

The **smaller repository-side** `docs/research/x40-r2416-v223-tools/x40_r2416_v223_repo_check.py` is intentionally narrower: eight pinned instruction words and three key literals, original host SHA-256 pin; the eight words and three keys were independently checked against the owner-private original ELF. Use the full ZIP for callback relocations, control flow and complete historical evidence replay.

## Interpretation boundary

Original `AiDetectResult()` binds `AiDetectResultSUB()` and invokes the typed `ava_ai_new_cmd` async subscription. `AiDetectResultSUB()` has native received command branches for **5→`start_offline`**, **6→`start_material_detect`**, **15→`ai_set_mop_is_dirty_data`**, each conditionally writing `true` through typed Blackboard set. `UpdateOutput()` separately calls `SendAINewCmd()` at the sole checked direct-BL site. These are compiled static facts, not a verified live message or connection to autonomous cleaning-task dispatch.

No observed AI-stain-triggered new cleaning-task start, second physical floor-clean pass, or dirty-mop dock rewash follows from this proof. Indirect callbacks, asynchronous subscribers and other modules remain open. Next: inspect the **readers/consumers of `ai_set_mop_is_dirty_data`** and the actual station wash decision state, while separately inspecting the outbound AI command schema and production scheduler.

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No robot access is needed to replay these native facts.

See [technical report](x40-r2416-v223-ai-command-subscriber-2026-10-27.md) and [sanitized JSON](x40-r2416-v223-ai-command-SANITIZED.json).
