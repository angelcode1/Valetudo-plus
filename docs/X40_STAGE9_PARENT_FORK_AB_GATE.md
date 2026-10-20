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
