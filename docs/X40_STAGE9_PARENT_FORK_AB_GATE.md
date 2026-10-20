# X40 Stage 9 — Official 0.5.0 baseline vs forked candidate

Status: **investigation only; no candidate promotion**. The official Algid Valetudo+ 0.5.0 build has now been observed to start with the correct `VALETUDO_DATA_PATH` and a compatible configuration, reaching localhost HTTP **200** at approximately **80 seconds** during an isolated probe. The owner subsequently reported that the persistent Valetudo+ 0.5.0 installation is working.

## Exact comparison

* Parent release: [Algid Valetudo+ 0.5.0](https://github.com/Algid/Valetudo-plus/releases/tag/0.5.0), AArch64 ELF SHA-256 `e0353c4feb141f48e3ab4a6ca6ca55ee6ffe21d7e63a0fc81547104762079e80`.
* Existing original upstream rollback: SHA-256 `cdc0c8723e2c924176f0d278df4e01899da10c3765acea97f0d3011ef845432d`.
* Previously failed forked X40 candidate: CI run [39252181608](https://github.com/angelcode1/Valetudo-plus/actions/runs/39252181608) at `5be3c3e53c3cb25e8408d23776200c57ddaa5353`; extracted ELF SHA-256 `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`.
* Source ancestry: [parent 0.5.0 → fork master compare](https://github.com/Algid/Valetudo-plus/compare/0.5.0...angelcode1:master): **13 production application files** (7 backend and 6 frontend), **4 backend test files**, **5 documentation files**, and **1 CI workflow** (23 total). There is exactly one feature merge adding the X40 changes, followed by docs-only commits.

## Hypothesis and outstanding gate

The earlier failed candidate reboot was not observed over a full 80+ seconds using the valid 0.5.0 configuration. Its reported absence shortly after reboot therefore **does not establish a regression caused by the CleanGenius changes**. A controlled one-process candidate startup must preserve the healthy official parent and use a *separate disposable copy* of its accepted configuration.

An operator-side Stage 9 kit is prepared for this purpose, with a **read-only fingerprint step** and a **separately opt-in maintenance test**. The latter verifies the three ELF hashes, refuses duplicate processes or unexpected live paths, never overwrites the working binary or launcher, runs the fork with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, checks a real port 80 HTTP response and the read-only X40 status endpoint, and attempts to reboot into the unchanged parent baseline at the end. It is deliberately **not installed** or executed as part of this repository commit.

**Caution:** The maintenance experiment temporarily stops robot-control software and reboots at completion; perform only docked and idle with SSH and an independent reboot/recovery method available. A disconnected SSH session may prevent the cleanup trap. Do not enable the experimental write controls.

## Security boundaries

* Preserve `/data/valetudo`, `/data/_root_postboot.sh`, the protected original binary, and the original `/data/valetudo_config.json`.
* Keep copied config and logs private. Valetudo startup logs can emit `CloudSecret` and `LocalSecret`; neither their values nor raw log files may be uploaded or committed.
* A successful temporary HTTP 200 is a necessary step but not complete device feature validation; require a successful persistent boot, safe state/status verification, and rollback verification before release.


## Stage 9 actual X40 result (2026-10-20)

The operator ran the maintenance A/B kit after `X40_STAGE9_BASELINE_FINGERPRINT_PASS`, recording identical preflight SHA pins for official Valetudo+ and the existing forked CI candidate. During temporary candidate execution, the fork showed no port-80 listener at 10–70 seconds, then at **80 seconds** it showed 10 threads, `FORK_HTTP_STATUS=200`, and `FORK_X40_STATUS_API_HTTP_STATUS=200`. The command printed `X40_STAGE9_FORK_HTTP_200_PASS`, then `X40_STAGE9_REBOOT_TO_RESTORE_OFFICIAL_BASELINE`.

**Limits:** This is a positive temporary startup and endpoint HTTP-reachability test. It is not yet a validated endpoint JSON contract or real CleanGenius/dock-sensor behaviour. The reboot marker means reboot was requested, not that a post-reboot parent fingerprint has been seen. The original no-start impression was confounded by a config-path mismatch and a 10–60-second listener observation window, versus the now-demonstrated ~80-second startup. Neither factor was proven individually causal.

## Stage 10 proposed gate

First obtain a **new** read-only Stage 9 baseline fingerprint after the recovery reboot. Then, only in a new supervised maintenance window, run the separate `x40-stage10-readonly-contract.zip` kit, which verifies the known-good parent, original-binary backup and SHA-pinned candidate before stopping anything; it starts the candidate with the experimental flag explicitly set to zero, checks HTTP 200, captures six **GET-only** `/api/v2/robot/clean-genius/status` responses into a private `/data/x40-stage10-readonly-capture-20261020/` directory, and attempts to reboot into the unchanged parent. The Mac-side Python sanitizer rejects incompatible API contract/policy and emits only allowlisted field **state labels**, observation state and bounded dock transition counts. It never includes raw MIOT values, credentials, map data or native events in its shareable report. The diagnostic itself issues no MIOT write request, but the running Valetudo implementation may perform ordinary poll and SmartHost auto-disable operations; do not claim that all firmware interactions are read-only.

**Final prerequisites for permanent fork promotion:** JSON contract and freshness verified, no regressions in existing robot status/maps/normal controls, unattended startup >120 seconds, parent baseline and original upstream rollback retained, and writable CleanGenius features still disabled. There is no proof of native dirtiness or automatic rewash decision telemetry.
