# X40 CleanGenius implementation handoff — 2026-10-28

**Canonical repository source:** [master](https://github.com/angelcode1/Valetudo-plus/tree/master) and [branch-consolidation manifest](./BRANCH_CONSOLIDATION_20261028.md). All prior `feature/`, `diagnostics/` and numbered `research/` branches were archived into Git ancestry and their refs removed in [one-time cleanup run 40656864797](https://github.com/angelcode1/Valetudo-plus/actions/runs/40656864797). References to the old branches elsewhere in this document are historical, not active work targets. PR #2 was closed as superseded. No robot changes were performed for the repository consolidation.

**Read this before doing any work on X40 CleanGenius.** This handoff supplements the binding [AGENTS.md](../AGENTS.md) anti-rabbit-hole instructions and [supervised enablement runbook](./X40_CLEANGENIUS_SUPERVISED_ENABLEMENT.md). It records actual owner-confirmed device results and code/build status. Do **not** restart v291-style binary reverse-engineering, run more firmware collector kits, overwrite the live Valetudo installation, or assume an artifact was installed because CI passed.

## Current consolidated source and validation — 2026-10-28

- **Source of truth:** `master` is the only active branch. The 90 deleted branch refs, captured commit hashes and 172 recovered research documents/tools are recorded in the [consolidation manifest](./BRANCH_CONSOLIDATION_20261028.md).
- **Verified code:** final source HEAD `177aa2526a0144f584475862fe8f087012e68d75` passed [full Node.js CI run 40657258670](https://github.com/angelcode1/Valetudo-plus/actions/runs/40657258670). Four normal workflow files remain. Cleanup workflow and trigger are removed.
- **PR #2:** closed as superseded. CI success does not imply a physical SmartHost acceptance.
- **X40:** the second supervised trial was closed with original PID 1752 and watchdog stopped. No X40 connection or change occurred during repository consolidation.
- **Decision:** guarded code and diagnostic build PASS; hardware CleanGenius acceptance PARKED. Do not revive deleted branches, weaken the idle guard or run another firmware collector.

## Historical pre-consolidation code-only checkpoint — 2026-10-28

- **Full CI PASS:** commit `942e3175a2ac26138cf90f6a852eb93444c6f9ff`; [Node.js CI run 40654460714](https://github.com/angelcode1/Valetudo-plus/actions/runs/40654460714) completed successfully, including TypeScript, lint, frontend/backend builds, backend tests and AArch64 upload. This supersedes the earlier failed polling-test fixture runs; the fixture-only correction was `ae5d4a0`.
- **Code change:** X40's passive `pollHealth` diagnostic now uses a monotonically increasing invocation generation, preventing an older polling attempt finishing late from replacing the diagnostic state of a newer attempt. If a stale/older request fails, it cannot invalidate the newer request's cached observations through the new X40 catch handler. The previous status API and frontend poll lifecycle labels are preserved.
- **Automated regression coverage:** older failure after newer success, and older success after newer failure; assertions ensure exactly the expected mock MIOT calls and no authorization from cached data. This is *diagnostic tracking*; it is not proof that all out-of-order MIOT responses or firmware state changes are serialized, nor does it authorize writes.
- **Historical PR state:** [PR #2](https://github.com/angelcode1/Valetudo-plus/pull/2) was open when this testing snapshot was written. It has since been closed as superseded after its guarded source was consolidated into `master` (not via the PR merge button). No upstream sync or device deployment occurred.
- **Device state:** the second trial was already closed: `STATE=ORIGINAL ORIGINAL_PID=1752`, `WATCHDOG=NOT_RUNNING`. No robot action occurred during this code-only pass. No hardware acceptance of `SmartHost=1`, automatic reclean or mop rewash has occurred.
- **Go/no-go:** PASS for code-only diagnostic CI, **PARK** hardware activation. Do not stage the CI artifact or initiate another device experiment merely because the software builds. Any future experiment needs a bounded, independently justified hardware acceptance decision; no new firmware collector loop or blind mode-guard relaxation.

## New code-only fix: report normal MIOT poll lifecycle — 2026-10-28

The original X40 is **still confirmed restored** after the second trial (`STATE=ORIGINAL ORIGINAL_PID=1752`, `WATCHDOG=NOT_RUNNING`). No new robot operations were run for this change.

- Issue: the read-only `/api/v2/robot/clean-genius/status` route does not initiate a normal MIOT poll. An empty status page on a newly started Valetudo process cannot distinguish "never polled" from a transport failure or a completed but incomplete/invalid reading.
- Implemented source change (pinned functional commit `c2ca9b9554d2016bfec97050f0220f0ec07978ed`): X40's existing `pollState()` now tracks `not_started`, `in_progress`, `succeeded`, `failed`, and last-attempt timestamp **without any new MIOT calls**. On error it still invalidates all three X40 cached observations and rethrows the original error; neither error text nor credentials appear in the status API. Success records poll completion **not** proof of valid 4:50/4:1/4:7 observations.
- API adds a passive `pollHealth` property to CleanGenius read-only status; TypeScript API types, OpenAPI and the CleanGenius Status UI reflect the same contract. UI explicitly warns if a poll succeeded but settings or cached mode/task readings remain absent, invalid or stale. It does not send a separate state poll or CleanGenius command.
- Backend fake-helper regression tests cover never-polled, pending poll, completed-without-valid-readings, failed after success with snapshot invalidation, and privacy of error reporting. Safety-critical `SmartHost` cached/fresh-idle guards, one-key writes, opt-in default and advanced controls remain unchanged.
- **Historical CI:** [run 40651539474](https://github.com/angelcode1/Valetudo-plus/actions/runs/40651539474) was an earlier failing test-fixture iteration, superseded by [passing run 40654460714](https://github.com/angelcode1/Valetudo-plus/actions/runs/40654460714) and the final consolidated [run 40657258670](https://github.com/angelcode1/Valetudo-plus/actions/runs/40657258670). CI is not hardware acceptance; no further collector cycle or unattended device experiment is planned.

## Read-only 20377ec hardware trial — recovered, diagnostic inconclusive (2026-10-28)

The owner reported the following exact checks for the already-validated `20377ec` candidate: local ZIP/executable SHA-256 PASS, separate staging under `/data/valetudo.cg-20377ec`, isolated config/data preparation PASS, readiness PASS on original PID 1788, detached watchdog smoke PASS, and an attended trial start reporting `TRIAL_STARTED=PASS CANDIDATE_PID=7402`, `WATCHDOG_ARMED=YES`. No MIOT write or CleanGenius mode change was reported for this session.

The screenshot of the new CleanGenius Status page showed *all* MIOT observations unavailable: no valid 4:50 observation, no cached 4:1/4:7 mode or task status, and no confirmed idle guard. It therefore does **not** show a nonzero docked mode or a rejected firmware setting; there is insufficient evidence to select an idle-guard code change. A newly launched Valetudo may not yet have a successful state poll, or a poll may have failed; the screenshot alone does not distinguish these.

**Recovery confirmed from owner's second-session status output:** `STATE=ORIGINAL ORIGINAL_PID=1752` and `WATCHDOG=NOT_RUNNING`. The original installation is restored; the second trial is CLOSED. Do not request another restore or reboot for this already-closed session. No more live setting changes/cleaning trials without a distinct go/no-go decision. Do not ask for another firmware collector, incremental static-analysis ZIP, or arbitrary new robot experiment.

**Bounded source-level decision:** The `/api/v2/robot/clean-genius/status` route in `backend/lib/webserver/RobotRouter.js` only returns `getCleanGeniusReadOnlyStatus()`; it does **not** call `pollState()`. In contrast, normal `/api/v2/robot/state` and `/state/attributes` routes call `pollState()` before responding. The status page's initial empty cache is therefore consistent with opening that page before a successful normal state poll. This explanation is plausible, not confirmed: transport errors, invalid property responses and incomplete paired 4:1/4:7 readings also remain possible. The decoder intentionally requires successful numeric 4:1 and 4:7 values to mark the cached idle pair valid. **Go/no-go: PARK hardware activation; do not weaken the guard, and do not launch a third collector/diagnostic cycle from this screenshot.** No accepted `SmartHost=1`, second floor pass or dock rewash has been demonstrated. If work resumes, make a specific code-and-test change with a named acceptance criterion, rather than another unbounded device trial.

## Archived preparation for completed passive idle diagnostic — 2026-10-28

**No device actions have occurred since the original Valetudo restoration reported `STATE=ORIGINAL ORIGINAL_PID=1788 WATCHDOG=NOT_RUNNING`.** The first trial was safely closed, and its `SmartHost` setter was blocked by the cached idle gate before any write. Do not repeat that setter attempt merely to obtain the error text.

- A passive-only X40 status enhancement was implemented on the same draft PR #2 branch: cache-only MODE `4:1` and TASK_STATUS `4:7` snapshots taken from the existing normal MIOT poll, with explicit stale/unavailable handling. The **CleanGenius Status** page now displays `Raw robot idle gate (read-only)`: raw mode, task status, and whether cached values exactly match zero/zero. It makes **no new robot reads or writes** and is **not** authorization to change a setting.
- Previously added rejection diagnostics remain intact. The original guarded SmartHost setter, initial-only SmartHost selector, advanced-gate exclusion, isolated config support, and default-off policy are unchanged. New tests cover malformed/partial/duplicate/stale cached pairs and poll-failure invalidation.
- **Code-validated commit:** `20377ecaaa720f791a2be5c163b0d6b9d39c3104`. Successful full push CI run: [40648346101](https://github.com/angelcode1/Valetudo-plus/actions/runs/40648346101). Matching artifact `x40-valetudo-aarch64-ci-candidate` ID `12798279924`, available through the push run. Published and independently checked artifact ZIP SHA-256: `6c8068f89c0bf535c3c41a93e1f4f7dcedce53272c4ff5495cda2ba41b407107`. Extracted AArch64 executable SHA-256: `6f7755d78830672d702f4a69f4b3fcbd2d6345182b2833336d3b926a5c4fc642`, size `38916587` bytes. **Never substitute older `ccaa64d` or `99c984c` binaries for this diagnostic.**
- Prepared offline Mac kit `x40-idle-diagnostic-20377ec-kit-20261028.zip` includes verified CI ZIP and checked shell scripts. It stages under new unique non-live name `/data/valetudo.cg-20377ec` and makes new private isolated config/data at `/data/valetudo.cg-20377ec-trial-20261028`, without overwriting original/old trial artifacts. A separately confirmed, detached reboot watchdog and explicit interactive confirmation are required for the one attended process switch. The original boot script remains unchanged.
- **Historical runbook, already executed:** the candidate was started once for read-only observation, the values were unavailable, and the original service was confirmed restored as PID 1752. Do not repeat the test simply because these former instructions remain in history. No v291+ collector or blind guard relaxation.
- The `20377ec` candidate **was run** in one attended read-only trial and then restored; the result is **inconclusive for the native idle gate** and **not** CleanGenius hardware acceptance. Refer to the latest result above.

## Latest supervised device result — 2026-10-28 (supersedes earlier pending-install status)

The user completed the staged `ccaa64d` supervised X40 trial and successfully restored the original service. These results are newer than the initial handoff below.

- Original boot recovery was verified through an actual reboot (original PID changed 1814 to 1773, checksums remained intact). The corrected `ccaa64d` candidate was staged with SHA-256 `28203537e31913f2ad94901e780fa23da3036dbb8e0e9f6b669116c51ef44cc8`.
- Isolated trial config/data copies passed integrity checks; the original executable, configuration and postboot remained unchanged.
- The independent detached-watchdog smoke test passed. The attended switch reported `TRIAL_STARTED=PASS CANDIDATE_PID=6547` and armed a bounded normal-reboot watchdog. The X40 experimental CleanGenius selector appeared under Quirks.
- **The one attempted Routine selection was blocked before any MIOT write:** `The X40 must be idle before changing SmartHost`. The UI still displayed `off`. Read-only page showed `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`, and mop dock idle; this dock observation does **not** establish native mode/task status or a successful mode transition.
- **Original recovery confirmed** from the user: `STATE=ORIGINAL ORIGINAL_PID=1788`, `WATCHDOG=NOT_RUNNING`. **Do not ask to run restore again for that completed session**. No accepted SmartHost transition, physical second pass, or automatic rewash was demonstrated.
- **Source insight:** Gen2 `STATUS_MAP` may present nonzero raw mode values as *docked*/*idle*, while the experimental `isIdle` requires cached raw `mode===0 && taskStatus===0`. The actual cached raw values at rejection were not captured; do not assume the robot was truly idle or weaken this safety gate based on the UI alone.
- After this result a strictly diagnostic-only change was committed to the draft feature PR: cache-only numeric mode/task reporting on idle rejection, and two no-MIOT-call regression tests. Latest diagnostic/test source commit: `73312a862a0db897f8f56806bf59b262d6441bf5`. **This commit's CI/artifact must be independently verified before any future hardware test.** The original `ccaa64d` CI artifact remains the validated source of the first trial, but cannot produce the new error details.

**Next decision:** Use at most one new bounded, supervised run with a freshly CI-verified diagnostic candidate to identify the raw cached mode/task; if the firmware reports a legitimate active task, park until idle. If the firmware reports a nonzero docked mode, determine the safe semantics before considering a guarded implementation change. No automatic MIOT writes, no repeated blind attempts, no new firmware collector loop. Maintain original executable, isolated config, watchdog and verified reboot recovery.

## Immediate objective and boundary

Move from an offline-tested native mode selector to **one bounded, supervised, reversible X40 R2416 hardware acceptance test**. Demonstrate `SmartHost=1` accepts and reads back, verify ordinary robot controls remain operational, then restore `SmartHost=0` and the working Valetudo process. This is **not** proof of stain-triggered second-pass cleaning or dock rewash, which remain unimplemented/unverified. No automatic robot commands or new research detour without an implementation decision.

## Repository state / preservation

- Repository: `angelcode1/Valetudo-plus`.
- Open **draft** PR: [#2](https://github.com/angelcode1/Valetudo-plus/pull/2). Feature branch: `feature/x40-cleangenius-supervised-activation-20261028`.
- PR base: `research/x40-cleangenius-v229-sensor-retention-20261027`. Neither PR #2 nor experimental code has been merged to `master`.
- **Last code-validated source commit before this documentation-only handoff:** `ccaa64d1a75c05e5a2e6f59256017fb820b322d0`. A subsequent handoff-only commit changes no implementation behavior; compare code against this pinned commit.
- Contract: preserve original robot installation, custom Valetudo code, other research branches, and recorded v249–v290 sanitized research. Do not force-push/reset master.

## What is implemented and validated in source

- X40 experimental opt-in via `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1`. Default remains off; generic Gen2 code otherwise auto-disables a positive `SmartHost` observation.
- Initial experimental UI exposes **only `SmartHost`** options: off (0), routine (1), deep (2). Auto Reclean/Auto Rewash are hidden behind *separate* `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED=1` and **must remain unset in the first trial**.
- Single-key MIOT 4:50 write, no bulk write or blind retry. Require cached idle, fresh read of mode 4:1 and task 4:7 both zero, serialized selector operations, and strict readback of requested 4:50 value. `SmartAutoMop=-1` is unsupported and must not be coerced.
- Configuration-compatibility fix is included in **`ccaa64d`**: `backend/lib/res/resolveConfigLocation.js` and updated `Configuration.js` honor an absolute `VALETUDO_CONFIG_PATH` when supplied, with prior `VALETUDO_DATA_PATH` behavior retained when absent. Added 4 focused resolver tests. Invalid *relative* override fails closed. **An absolute override pointing at a missing file may still cause Valetudo to create a new config; do not test against an unverified path.** Config migration may modify the file; use a separately backed-up *trial config copy* once the full launch plan is vetted.
- Prior CleanGenius controller: 16 focused behavioural tests. Full repo CI, not just stubs, passed for `ccaa64d`.

### Latest confirmed CI and matching artifact

At handoff, **push CI run [40641948911](https://github.com/angelcode1/Valetudo-plus/actions/runs/40641948911)** for `ccaa64d1a75c05e5a2e6f59256017fb820b322d0` **completed successfully**: npm install, OpenAPI generation, code generation, TypeScript, ESLint, frontend build, backend build, full backend tests, and artifact upload. Corresponding PR run `40641954476` also passed; its artifact upload is intentionally skipped.

- Artifact: `x40-valetudo-aarch64-ci-candidate`, GitHub artifact id **12795384901**.
- GitHub-published artifact ZIP SHA-256: `00d151aa7035086a43d1d985ff1a2c7fedf8d88e7bba70982864ef6b4f76dacb`.
- Artifact created 2026-10-28; listed expiry 2026-11-04. Retrieve via the **push** run, not the PR run, and verify ZIP and extracted executable hashes independently before moving it to the robot.
- There is **no evidence this corrected binary is staged or installed**. Do **not** reuse older `99c984c` as the live activation candidate.

## Owner-confirmed X40 installation and recovery state

The user ran **read-only SSH** and reported:

| Item | Observed |
| --- | --- |
| CPU architecture | `aarch64` |
| Running Valetudo at time of check | PID 1814, `/proc/<pid>/exe` → `/data/valetudo` |
| Live original executable | `/data/valetudo` (a **file**, not `/data/valetudo/valetudo`), executable; observed size 38,918,209 bytes |
| Existing config | `/data/valetudo_config.json` |
| Data directory | `/data/valetudo-x40-fork-stage14` |
| Startup | `/data/_root_postboot.sh` invokes the original binary directly |
| Existing env on startup | `VALETUDO_CONFIG_PATH=/data/valetudo_config.json`, `VALETUDO_DATA_PATH=/data/valetudo-x40-fork-stage14`, private log path in that directory, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` |
| Backup | User reported **BACKUP VERIFIED** after SHA-256 comparison of original binary, config and postboot against copies in a private Mac Desktop backup folder (`x40-rollback-20261028-155633`) |
| Staged *older* candidate | User reported **STAGED VERIFIED: `/data/valetudo.cg-99c984c`**; no process was stopped or started, no postboot edit |
| Native CleanGenius activation | **NOT performed**; current startup still sets experimental flag to zero |

**Important platform detail:** macOS `scp` default SFTP failed with `/usr/libexec/sftp-server: not found` on the robot. The user's successful backup used `ssh -T 'cat <remote-path>' > <local-file>` and verified SHA-256. Avoid claiming backup success just because a shell script printed a success line: enforce exit-on-error, nonempty files, and matching remote/local hashes. Do not commit or share the private backed-up configuration or logs.

**Observe-only flag:** The existing `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` was observed in the original startup command. Do not assume that flag has the intended effect in the new candidate; check actual code before relying on it.

## Where work stopped / next implementation steps

**No more code changes simply to produce progress.** A working candidate has cleared CI. The next actions must be bounded and useful:

1. **Retrieve and verify exactly `ccaa64d` CI artifact.** Hash ZIP against the published digest and determine executable digest. Stage under a **new, uniquely named** non-live file (for example `/data/valetudo.cg-ccaa64d`) using SSH streaming; verify remote hash, executable bit and architecture. Never overwrite original `/data/valetudo` or start the already-staged `99c984c`.
2. **Verify a safe test launch and rollback** specific to this device, including existing process ownership, any supervising service, availability of an independent recovery method, the config-path override, and a *separate trial copy* of the config to prevent migrations from touching the original. No concurrent Valetudo processes sharing the same port or mutable data. **Do not start the trial as an automated consequence of staging.**
3. Only after the owner explicitly approves the one-session switch, supervise stopping the original process, starting the corrected candidate with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1`, leaving advanced opt-in absent, and confirming the UI and normal stop/dock controls. Preserve the original postboot launch path for recovery. Need a reliable restoration method that does not depend only on a live SSH session or an untested timeout script.
4. **One attended setting acceptance test:** verify real MIOT idle status, select `SmartHost=routine (1)` once, verify readback and safe normal controls, then return to `off (0)` with readback. If rejected, inconsistent, unknown or unsafe, **stop and park**; no successive opcode/collector investigations.
5. Restore the original Valetudo process and verify `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and ordinary robot control. Any extra cleaning pass / dock rewash remains a separate hardware-observation goal and is not a supported claim from a 4:50 readback.

**No robot or installed binaries were changed in this handoff.** Local backup and the old staging candidate are user-reported completed steps; the corrected binary is CI-validated but not yet device-validated.

## Upstream fork-sync request (separate from this trial)

Owner explicitly requested **“also sync fork when ready.”** GitHub Issues are disabled, so PR #2 tracks this request; do not forget it. Fork ancestry `angelcode1/Valetudo-plus` → parent `Algid/Valetudo-plus` → original `Hypfer/Valetudo`. On 2026-10-28 fork master was **68 commits ahead and 13 behind** parent master (diverged). **Not a fast-forward.** After the supervised CleanGenius go/no-go, review 13 upstream commits on a separate integration branch from fork `master`, preserve existing X40/camera/multi-map/dock/custom work, run full CI, and submit a separate reviewed PR. No forced reset, blind Sync Fork, or unilateral merge to master.

## Explicit stop rules for the next assistant

- Do not ask for another series of R2416 firmware instruction-scanner ZIPs or “one more” Blackboard probe. The user has objected to this recurring dead end **four times**. Follow `AGENTS.md`.
- Do not claim a working CleanGenius feature merely because an option appears or MIOT acknowledges `SmartHost`; distinguish code-implemented, CI-validated, mode-accepted, and **physically demonstrated**.
- Do not ask the owner to repeat the preflight, backup or old-candidate staging, which are already confirmed. Investigate the **new** binary compatibility and rollback only.
- Preserve secrets: no raw config, device private logs, firmware blobs, or credentials in the repo or user-facing requests.
