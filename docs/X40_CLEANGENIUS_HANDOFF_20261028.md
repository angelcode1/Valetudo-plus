# X40 CleanGenius implementation handoff — 2026-10-28

**Read this before doing any work on X40 CleanGenius.** This handoff supplements the binding [AGENTS.md](../AGENTS.md) anti-rabbit-hole instructions and [supervised enablement runbook](./X40_CLEANGENIUS_SUPERVISED_ENABLEMENT.md). It records actual owner-confirmed device results and code/build status. Do **not** restart v291-style binary reverse-engineering, run more firmware collector kits, overwrite the live Valetudo installation, or assume an artifact was installed because CI passed.

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
