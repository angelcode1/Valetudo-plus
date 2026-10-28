# X40 R2416 CleanGenius — supervised activation candidate

**Status (2026-10-28): implementation hardened and fake-MIOT tested; NOT installed or hardware-validated.**
This is a controlled evaluation of the *existing native* `SmartHost` mode. It is not a restored stain-triggered scheduler, not proven auto-reclean, and not proven dock rewash. No serial static-ELF collectors are part of this plan. Follow [AGENTS.md](../AGENTS.md).

## Already implemented in this branch

- `DreameX40UltraValetudoRobot` exposes the **CleanGenius (SmartHost) selector only** when `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1` is set before process startup. Without opt-in, generic Gen2 logic still disables positive `SmartHost` observations. Advanced Auto Reclean/Auto Rewash selectors remain hidden unless `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED=1` is also set. **Do not set the advanced flag in the first trial**; it is not validated on hardware.
- Manual `SmartHost` selection: off (0), routine (1), deep (2), using a *single-key* MIOT SIID 4 PIID 50 update. In the first-trial configuration **Auto Reclean/Auto Rewash are not exposed at all**. A separate advanced opt-in exists solely to preserve future explicit testing; it is not part of this candidate's initial acceptance.
- Setters check cached idle mode=0 AND taskStatus=0, verify the device presents a known current value, **then make a fresh batched MIOT read of both MODE (4:1) and TASK_STATUS (4:7)** immediately before any write. Both responses must be successful and zero, with the expected property IDs. This avoids treating the Gen2 constructor's unobserved zero defaults as proof of idleness. Setters serialize selector operations and verify the requested value with a second MIOT 4:50 read. No automatic retry or blind rollback.
- `SmartAutoMop=-1` remains an unsupported sentinel; the reclean control must reject it. The user's observed baseline is `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`.
- Read-only X40 state and dock status APIs remain passive. A successful setting readback is **not** evidence that robot cleaning behavior changed.

## Test before any installation

Run the actual project tests and build from the branch on the development machine, following the repo's workspace setup. **The PR's Node.js CI is required before any candidate is called validated.** A passing push-branch CI run uploads an AArch64 candidate to the run's Artifacts section for this specific branch. Downloading it is not an installation or permission to use it on the robot:

```sh
npm ci
node --test backend/test/lib/robots/dreame/DreameX40CleanGeniusResearch_test.js
npm run lint --workspace=backend
npm run ts-check --workspace=backend
```

If the current workspace does not support one of these commands, record the failure. Do not imply passing CI or a complete build on the basis of stubbed tests.

## One bounded supervised device evaluation (only after user approval)

1. Preserve the currently working Valetudo binary/configuration and establish a tested way to return to it. Keep the robot physically accessible, with its normal stop controls available, and do not test unattended. Verify mapping, normal start/stop and docking are already functioning. **If any precondition fails, stop; do not install or test this candidate.**
2. With the existing working software unchanged, record a read-only MIOT 4:50 baseline, model and firmware IDs, and idle mode/task status. Confirm `SmartHost=0` and note `SmartAutoMop=-1` without coercing it. Do not expose credentials, maps or camera imagery.
3. If the user explicitly authorizes installing the candidate, use the verified deployment/rollback process appropriate to their environment. Enabling the env var alone on a **stock build** does nothing; the branch must actually be built and deployed. No automatic deployment is included here.
4. Start the candidate with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1`, leaving `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED` unset. This **exposes only the native CleanGenius selector**; it does **not** turn on CleanGenius by itself. Confirm all ordinary state/stop/dock actions work before changing settings.
5. While both mode and taskStatus read 0, set **CleanGenius = routine** (`SmartHost=1`) *once*. The setter must return successfully only after strict readback shows 1. If the write is rejected, if readback mismatches, if state changes unexpectedly, or if the robot misbehaves: **stop the experiment**. Do not repeatedly toggle or brute-force other properties.
6. If the setting is accepted and ordinary controls remain safe, run **at most one** small attended cleaning test using the existing normal UI. Log state transitions and whether a genuine second floor pass or mop wash occurs. Distinguish optional native mode acceptance, automatic stain detection, physical re-clean and dock rewash: they are separate observations.
7. While idle, manually select CleanGenius = off and verify `SmartHost=0` on readback. Restore the previous binary/configuration and omit the experimental env flag. The generic Gen2 auto-disable on future positive observations is a fallback policy, **not** an emergency stop or proof of instant rollback. If the robot cannot safely be controlled, use its normal physical stop and recover through the previously verified method.

**Go/no-go criteria:** if `SmartHost=1` cannot be accepted and read back in a single supervised test, or basic operations are impaired, mark this approach **blocked**. Do not start another loop of firmware probes. If it can, record “native mode accepted” only, then separately determine whether any observed second pass or wash actually occurred. A second-pass feature is **not shipped** until its behavior is demonstrated.

## Current evidence versus unresolved behavior

| Capability | Status |
| --- | --- |
| X40 opt-in quirks and Gen2 override | Code present |
| Guarded single-key MIOT write, fresh idle status, and strict readback | Code + 16 focused fake-helper tests (full CI pending this commit) |
| Candidate build and live MIOT behavior | Unverified |
| Native CleanGenius effective mode | Unverified |
| Scheduler task enqueue triggered by stain | Unproven |
| Automatic second physical floor pass | Unproven |
| Automatic dock rewash | Unproven |

## Stop rule

The previously created v249–v290 analysis and reports are archived research, not a mandatory prerequisite for this trial. Do not request another Mac collector ZIP or incremental opcode decoder. The next useful input is an intentional implementation test result or an explicit go/no-go decision.
