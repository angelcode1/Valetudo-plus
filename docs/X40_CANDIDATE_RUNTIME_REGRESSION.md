# X40 Ultra: CI-built candidate not runtime-validated

**Incident (2026-10-19):** A CI-built Valetudo+ AArch64 static-PIE candidate passed Node 22 CI but did not start after installation on a rooted X40 Ultra (Athena `r2416_release`). After the reboot, SSH worked but there was no Valetudo process or HTTP listener. The original Valetudo executable was restored from a verified backup and the normal `/data/valetudo` process returned (PID 1753 after reboot).

## Verified facts

- Candidate file SHA-256: `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`; ELF AArch64, stripped, static-PIE. It was staged using legacy SCP (`scp -O`), and the on-device SHA-256 matched before atomic replacement.
- Previously working executable SHA-256: `cdc0c8723e2c924176f0d278df4e01899da10c3765acea97f0d3011ef845432d`. After restoring it and rebooting, a Valetudo process existed again.
- At the failed startup, no Valetudo process, port 80/8080 listener or relevant filtered `logread` entry was found. RAM and `/data` storage were sufficient.
- The failed candidate remains preserved privately on the device as `/data/valetudo.failed-cleangenius`; **do not** check it into GitHub.
- This is not evidence that the AArch64 architecture is wrong, nor proof of an application exception, memory exhaustion, syscall incompatibility, missing config, or launcher failure. The precise root cause **remains unknown**.

## Deployment and release guard

1. **Do not recommend or deploy the failed candidate.** A green GitHub CI build does not equal runtime validation on X40 firmware.
2. Keep the restored original binary and backup. Do not flash firmware, reset the robot, or change native Dreame services merely for this regression.
3. Collect only allowlisted, read-only executable metadata, kernel errors and launch script locations. Avoid collecting system identifiers, authentication values, maps, camera data, or full raw logs.
4. Compare the original and candidate's executable/Node packaging characteristics offline. Determine the actual failure reason before proposing a replacement build.
5. Fix, test, and validate a new candidate separately; require a successful real-device startup and rollback check before calling the feature deployable.
6. Native mop-dirtiness and rewash-decision interfaces remain unverified. Mapping work remains deferred; the experimental writable CleanGenius controls remain disabled by default.

The `GET /api/v2/robot/clean-genius/status` and corresponding UI were built and tested in CI, but were **not verified as running on the X40** due to this startup problem. No proprietary firmware binaries or code, passwords, keys, or maps are included in this document.


## Post-rollback read-only report (2026-10-19 23:04 Brisbane time)

The user supplied `X40_BOOT_READONLY_DIAGNOSTICS_V1`, collected *after* successfully restoring the original executable. Verified facts:

- Platform: Linux **4.9.191**, **aarch64**.
- Working Valetudo: PID **1753**, sleeping, **10 threads**, RSS approximately **64,440 kB**, executable `/data/valetudo`.
- Port **80** is listening, confirming the normal HTTP listener was restored.
- Restored executable and its separate backup are the same **38,815,132-byte** file, SHA-256 `cdc0c8723e2c924176f0d278df4e01899da10c3765acea97f0d3011ef845432d`.
- Preserved failed candidate is **38,913,544 bytes**, SHA-256 `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`.
- The report listed `/etc/inittab` but did not locate the Valetudo launcher script or show any filtered kernel executable-failure error. **Absence of a matching kernel log does not prove that the candidate did not exit with a userspace exception.**
- Native executable sizes differ by **98,412 bytes**. **A size difference is not a root-cause diagnosis**; kernel ABI, bundled Node runtime, executable packaging and JavaScript initialization must be distinguished by offline ELF comparisons and, eventually, safely captured startup stderr.

The next private diagnostic is an offline comparison of the working and failed ELF binaries' `.text`, `.rodata` and other section hashes. It runs on the user's Mac, reads the known-good binary over SSH without stopping it, verifies both full SHA-256 values and emits only structural metadata and hashes. Keep actual binary contents and any operational logs private. **Do not launch the failed candidate on the running robot to collect a stack trace.**


## Original vs failed AArch64 binary metadata (offline comparison)

A verified local comparison dated 2026-10-19 reports:

- Working and failed executables share the **identical 16,785,512-byte native `.text` section SHA-256** (`10b8c2c3f86b5959ac0584f05c341c80f9138e65e3e93431fbbca284367c1e86`), ELF entry **1920044**, section count **25**, no `PT_INTERP`, two identical-size RX/RW load segments and the same native `.init`, `.data`, `.data.rel.ro`, `.eh_frame` and `.comment` hashes.
- The `.rodata` section differs in content (each section is 7,802,924 bytes), as does the **application payload trailing the ELF section header table**. The total size difference, **98,412 bytes**, is entirely accounted for by the changed length of the package tail. These differences are consistent with a changed packaged application, but **they do not establish an exception type or exit cause**.
- The failed candidate's package is a `pkg` compressed embedded virtual filesystem. Its entrypoint is `/snapshot/Valetudo-plus/backend/index.js`, with **4,234 file records containing content**, of which **701** are first-party backend, **85** built frontend and **466** third-party dependency payload records (remaining records are other package data). The entrypoint is present; this is not proof that it loads or executes.
- A separate **read-only, no-dependency** Mac Python kit can compare the whole compressed `pkg` virtual filesystem against the known-working executable *in memory*, emitting only changed first-party JavaScript filenames and counts for other categories. The robot is accessed only via SSH `cat /data/valetudo`; it does not execute either binary or collect credentials, maps, camera images or source code into the output. It verifies the two known SHA-256 values. A same-binary test reported zero changes.
- **Do not reinterpret ELF section identity as successful runtime validation.** A bundled JavaScript module, package metadata, data resource, changed compression or boot invocation can still cause the candidate to exit, and no startup stderr or process exit code from the candidate has been captured.

**Next gate:** review the compressed-payload filename diff when available, then plan a reproducible *off-robot* launch diagnostic. Keep the user's restored Valetudo running and do not re-install the already failed candidate.


## Stage 2: compressed pkg payload comparison (2026-10-19 UTC)

The locally generated `X40_OFFLINE_PKG_DIFF_V2` JSON report compares the known-good executable SHA-256
`cdc0c8723e2c924176f0d278df4e01899da10c3765acea97f0d3011ef845432d`
with the failed candidate SHA-256
`45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`.
Both hashes agree with the earlier incident ledger. The report contains no executable or source bytes and reports **no candidate execution, no modifications to the working executable, and only an SSH read of `/data/valetudo`**.

### What the package diff proves

- The earlier “Unsupported pkg entry point” diagnostic-tool refusal was overcome by an offline parser supporting `pkg_brotli_compressed` snapshots. This does **not** mean the failed application can successfully start.
- The **packaged** `backend/index.js` entrypoint is identical across the working and failed binaries. Both package snapshots are parsed; the working contains **4,199** file records and the failed contains **4,234**.
- Grouped path counts (added and removed are relative to the **failed** package):

  | Category | Added | Changed | Removed | Identical |
  | --- | ---: | ---: | ---: | ---: |
  | First-party backend | 36 | 36 | 3 | 629 |
  | Built frontend | 3 | 6 | 3 | 76 |
  | Third-party dependencies | 2 | 0 | 0 | 464 |
  | Other package data | 0 | 1 | 0 | 2,981 |

- Added backend paths include `DreameX40CleanGeniusReadOnlyStatus.js`, `DreameX40CleanGeniusResearch.js`, `DreameX40DockWashReadOnlyStatus.js`, multiple-map and speaker capabilities, MQTT handlers and router modules. The changed-path list includes shared startup-adjacent modules such as `Configuration.js`, `DreameGen2ValetudoRobot.js`, `DreameX40UltraValetudoRobot.js`, `RobotRouter.js`, `WebServer.js`, and `Updater.js`. Missing in the candidate relative to the working package: `DreameMovaV50UltraValetudoRobot.js`, `DreameMovaZ60UltraRollerValetudoRobot.js`, and `GithubValetudoNightlyUpdateProvider.js`.
- `.text`, `.init`, `.data`, and `.data.rel.ro` are identical in the executable comparison. The 7,802,924-byte `.rodata` sections differ in **14 bytes across four disjoint runs** (largest contiguous run six bytes). The snapshot roots differ. These observations are not an identified execution fault.
- The report has only changed *filenames* and counts, not the content of changed modules or dependency names. File additions and removals may simply represent a different Valetudo+ version or baseline. The data does **not** isolate CleanGenius as the cause.

### Next diagnostic gate (no robot replacement or launch)

1. **Provenance:** establish the exact git revision, CI run, build manifest and `pkg` settings of the failed candidate; separately attempt to identify the original working executable's build provenance. Do not assume the working package came from this branch merely because paths overlap.
2. **Host-only package check:** in a deliberately network-isolated local Linux/AArch64 sandbox, verify the two captured executables' package metadata, `pkg` virtual-root mappings, bundled transitive imports and asset presence. Keep executable contents off the public repo. Perform any instrumented runtime experiment **only** with network isolation, disposable filesystem/configuration and a clear understanding that robot-specific runtime dependencies may be unavailable. Record sanitized exit status/stderr, never keys/maps/camera contents.
3. **Classify the failure before fixing:** distinguish `pkg` loader failure, unresolved module/resource, synchronous JS initialization error, environment/configuration error, or launcher/process-management failure. A filename diff cannot distinguish these.
4. **Preserve rollback and release block:** no firmware writes, new binary install, process replacement or reboot for this investigation. A successful CI build or sandbox launch alone is **not** X40 runtime validation. The restored executable continues to be the only known-good deployed candidate.
5. **Only after a discriminating failure is obtained:** prepare a minimal source change with offline tests; defer supervised device deployment until a separate explicit authorization and verified rollback plan.

This is a **diagnostic evidence checkpoint**, not a declaration of working CleanGenius, native dirtiness sensing or automatic rewash functionality.


## Stage 3: source-level startup triage and build provenance (2026-10-20 Brisbane)

This is a **source and GitHub Actions audit**, not a runtime validation or identification of the exit cause.

- The successful feature-branch **push** workflow is [run 39252181608](https://github.com/angelcode1/Valetudo-plus/actions/runs/39252181608), head commit `5be3c3e53c3cb25e8408d23776200c57ddaa5353`, build job 118058432334. It ran npm install/validation, generated code, built the frontend and the three backend targets, and passed Node tests before publishing `x40-valetudo-aarch64-ci-candidate` (artifact ID 12185144962). The build log identifies `@yao-pkg/pkg 6.6.0`, `node22-linuxstatic-arm64`, Brotli compression and 64 MiB heap setting for the AArch64 output. Its artifact **ZIP** digest was `9f6445bbe4dd7ae009107c2e5f562c9485fa4ce3e5cfe9fab3bf02635f474d3e`; this is **not** the embedded ELF SHA-256. A local ZIP extraction verified that the single contained file `valetudo` is exactly **38,913,544 bytes** with SHA-256 `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`. Thus the failed candidate **is proven byte-for-byte identical to the successful workflow artifact**. The ZIP digest and embedded ELF digest refer to different byte sequences.
- The parent Valetudo+ example postboot scripts use `/data/valetudo/valetudo` with `VALETUDO_DATA_PATH=/data/valetudo`, whereas the known-working device process executable was `/data/valetudo`. These are *different installation conventions*. The actual X40 launcher and environment are **not yet established** by the example scripts.
- In `backend/lib/Configuration.js`, startup reads a configuration file at `VALETUDO_DATA_PATH/valetudo_config.json` (or under `os.tmpdir()` when the environment variable is absent). When the configuration version differs it can migrate and **persist** it; if schema parsing/validation fails it may rename the original to a `.backup` file and write defaults. This is a concrete reason **not** to launch the failed candidate on the robot or expose the real configuration to an offline trial.
- In `backend/lib/Logger.js`, logging initially writes to `/dev/null` on POSIX until the constructor configures a log file. The parent fork example boot scripts additionally redirect stdout/stderr to `/dev/null`. A process exit before logger setup can therefore leave little diagnostic evidence, but we have **not** observed any such exit.
- The X40 status endpoint's Express route uses a simple static `/clean-genius/status` path; the X40 read-only decoder modules have no top-level device I/O in the reviewed source. The experimental quirk factories are only called when their environment flag is set. These checks **do not** prove module resolution in the embedded compressed snapshot or successful constructor initialization.
- The fork currently includes historical Express 5 and dependency-compatibility fixes (e.g. commits `5ec1f5a`, `00c61e3`, `0f589c1`). None establishes the present X40 failure's cause.

**Next safe probe:** a separately distributed Mac-side `x40_stage3_readonly.py` kit performs one read-only SSH audit of the *currently working* process's executable path, first argument, allowlisted `VALETUDO_DATA_PATH` and `VALETUDO_LOG_PATH` values, plus presence-only checks for a short fixed list of launcher script paths. It collects **no full process environment, script contents, device configuration, logfile contents or credentials**. Its local `--self-test` passes; no live X40 probe has been run as part of this stage. Inspect the JSON before sharing. The absence of a matched launcher in the fixed path list is not evidence that no launcher exists.

**Still blocked:** failed candidate runtime execution, binary replacement, firmware or config modifications, and experimental CleanGenius writes. A successful Linux/AArch64 sandbox test would be informative but not a real-device startup pass.


## Stage 4: official Valetudo+ 0.5.0 baseline failed to start (2026-10-20)

**User-supplied device evidence:** The user downloaded the **uncompressed AArch64** asset from [Algid/Valetudo-plus release 0.5.0](https://github.com/Algid/Valetudo-plus/releases/tag/0.5.0), verified SHA-256 \`e0353c4feb141f48e3ab4a6ca6ca55ee6ffe21d7e63a0fc81547104762079e80\` on macOS, staged it, atomically replaced \`/data/valetudo\` and independently verified the same on-device SHA-256 before reboot. SSH returned after reboot, but \`pidof valetudo\`, \`ps\` and port 80 inspection found **no running service**. The original verified executable had been backed up as \`/data/valetudo.original-preplus-20261020\` with SHA-256 \`cdc0c8723e2c924176f0d278df4e01899da10c3765acea97f0d3011ef845432d\`. No successful parent baseline or post-reboot rollback has yet been reported.

**Critical startup environment difference, confirmed in tag sources:**
- The actual device \`/data/_root_postboot.sh\` uses \`VALETUDO_CONFIG_PATH=/data/valetudo_config.json /data/valetudo > /dev/null 2>&1 &\`.
- [Hypfer/Valetudo 2026.10.0 \`backend/lib/res/env.js\`](https://github.com/Hypfer/Valetudo/blob/2026.10.0/backend/lib/res/env.js) maps \`ConfigPath\` to \`VALETUDO_CONFIG_PATH\`, and its \`Configuration.js\` uses the environment's full **filename**.
- [Algid/Valetudo-plus 0.5.0 \`backend/lib/res/env.js\`](https://github.com/Algid/Valetudo-plus/blob/0.5.0/backend/lib/res/env.js) maps \`DataPath\` to \`VALETUDO_DATA_PATH\`, and its \`Configuration.js\` joins this **directory** to \`valetudo_config.json\`. The existing \`VALETUDO_CONFIG_PATH\` variable is ignored by this parent fork.
- The user's prior read-only Stage 3 report confirmed \`data_path: null\` while the old original process was running. This is expected for the original executable, not proof of a failure.
- Therefore, on the current postboot invocation, the official 0.5.0 baseline may load/create \`/tmp/valetudo_config.json\` rather than reading \`/data/valetudo_config.json\`. **This mismatch is confirmed; causation of the process exit is not.**
- **Correction to previous backup recipe:** the earlier \`DATA_DIR\` inference fell back to \`/tmp\` when \`VALETUDO_DATA_PATH\` was absent, so it must **not** be assumed to have backed up the original \`/data/valetudo_config.json\`. Verify and back up the explicit config file before any further test.
- The original sample postboot redirects stdout/stderr to \`/dev/null\`. The source may write a log at \`os.tmpdir()/valetudo.log\`, so use a read-only, sanitized inspection to classify the exit first.

**Safety-gated next step:** Do not delete anything, switch filesystem layouts or deploy our failed candidate. Back up \`/data/valetudo_config.json\` as a separate immutable snapshot; inspect presence-only config files and redacted startup error markers, then test the official 0.5.0 binary using \`VALETUDO_DATA_PATH\` pointing to a *disposable copy* of the saved configuration and an isolated log file, only when safely authorized. If not pursuing this investigation immediately, restore the original verified binary using the existing known-good backup and reboot. If a parent baseline starts with the correct config path, only then plan a reversible launcher change retaining both environment variables. No cause is yet proven for the forked binary, though the same launcher incompatibility is now a plausible common factor.
