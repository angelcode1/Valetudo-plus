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


## Stage 5: official 0.5.0 isolated short startup probe (2026-10-20)

The user ran the *official* Valetudo+ 0.5.0 binary, SHA-256 \`e0353c4f...\`, in a **disposable** \`VALETUDO_DATA_PATH=/data/x40-plus-baseline-probe-20261020\` directory containing a copy of the original \`valetudo_config.json\`, and redirected stdout and logger output to private files. The original config, loader and binary backup were not intentionally modified by this test.

Observed script output:

\`\`\`text
X40_BASELINE_PROBE_BEGIN
BASELINE_PROCESS_ALIVE_AFTER_10_SECONDS
BASELINE_HTTP_LISTENER_ABSENT
BASELINE_PROBE_STOPPED
=== SANITIZED DIAGNOSTIC MARKERS ===
X40_BASELINE_PROBE_COMPLETE
\`\`\`

**Interpretation:** a short-lived process existed at the ten-second check; the simplistic \`netstat -lnt | grep ':80 '\` check did not find a listener; \`SIGTERM\` was followed by a negative \`kill -0\` check after three seconds. This is **not** a confirmed working parent baseline and **not** a demonstrated \`pkg\` crash, because the script intentionally terminated the process. The empty marker list only states that none of eight exact patterns was matched in the two nominated log files. Their existence, sizes and other contents remain unknown; no exit code was captured for the running case. A still-in-progress process, failed/unsupported \`netstat\`, different HTTP port, pre-logger startup stall, or other condition remain possible.

**Source detail:** The 0.5.0 \`WebServer.js\` calls \`server.listen(this.port)\` synchronously during webserver construction (default \`webserver.port=80\`). The \`Valetudo.js\` constructor sets up logger and logs \`Starting Valetudo\` before it constructs the webserver. The optional X40 API and feature are not necessary for official 0.5.0. Importantly, \`MiioValetudoRobot.startup()\` logs \`CloudSecret\` and \`LocalSecret\`; do **not** upload or print raw \`stdio.log\`, \`valetudo.log\`, unredacted config or broad process environment.

**Next diagnostic:** Inspect the existing private probe directory *read-only* for file sizes, config-copy existence/comparison and presence-only markers, plus native \`/proc/net/tcp*\` listening port states. If still ambiguous, repeat a time-bounded observation with process state/elapsed time and safe port checks at intervals longer than 10 seconds, using the existing temporary config and keeping secrets local. Avoid modifying startup files or deploying the known-failed candidate until a verified healthy baseline is established. If service recovery is needed first, use the verified old executable backup and restart. Preserve the original \`/data/valetudo_config.json\`.


## Stage 6: official 0.5.0 60-second startup still incomplete (2026-10-20)

**New user output:** The pre-existing ten-second probe's \`stdio.log\` was 0 bytes with no \`valetudo.log\`, and its disposable config copy matched \`/data/valetudo_config.json\`. No Valetudo process was present before the follow-up test. A separate 60-second isolated probe of the **official Algid 0.5.0** binary used the original config snapshot in a distinct disposable directory and observed:

- At 5/10/20/40/60 seconds, \`/proc/$PID/status\` existed and showed **State R (running)**, **6 threads**, with \`VmRSS\` 33,300 / 37,184 / 41,552 / 58,772 / 58,640 kB respectively. The PID was therefore not an immediate early exit at the observed checkpoints.
- No listening ports among 80, 443, 8079 or 8080 were reported using \`/proc/net/tcp*\`. This observation applies to the ports checked by the script; it does not prove no open socket of any kind.
- \`stdio.log\` was 0 bytes through the 20-second sample, and 2,165 bytes by 40 seconds, unchanged at 60. The configured \`VALETUDO_LOG_PATH\` output file remained **missing**. The contents of stderr/stdout were **not** shared, and no diagnosis can safely be derived from byte count alone.
- A SIGTERM was sent to the process and after three seconds \`/proc/$PID/status\` still existed, so the script emitted \`WARNING_PROCESS_REMAINS\`. **This could represent a live process still responding slowly, a zombie process, or a process that was later reaped; the current state must be established before another launch.**
- Tag \`0.5.0\` source confirms \`Configuration\` initializes before \`Logger.setLogFilePath\`, and the normal HTTP webserver's \`listen\` call occurs in \`WebServer\` construction later in \`Valetudo\`. The first console output without the normal application logfile is therefore *consistent with* config-phase diagnostics, but could also originate elsewhere before logger reconfiguration.
- \`MiioValetudoRobot.startup()\` can log \`CloudSecret\` and \`LocalSecret\`; raw logs, raw process environments and raw configs must remain private.

**Next observation must be non-destructive:** Identify any surviving process by checking its **exact private-probe \`VALETUDO_DATA_PATH\`** in \`/proc/$pid/environ\` without printing the environment. Report only sanitized process state, two-point CPU ticks, log lengths, and presence-only fixed error/configuration markers. Do not start a second instance, edit the production postboot script, share raw logs or call the parent build healthy until the baseline webserver responds. Any stop must be limited to a PID positively identified as the specific disposable probe. Retain the known-good backup of original Valetudo and a pristine copy of \`/data/valetudo_config.json\`.


## Stage 7: 60-second probe postmortem and baseline readiness (2026-10-20)

The user submitted the sanitized Stage 6 output after the 60-second official Valetudo+ 0.5.0 probe:

- The disposable probe configuration **differs** from the protected original, and `valetudo_config.json.backup` was created inside the disposable probe folder. The console log has the markers `Loading configuration file`, `Migrating config`, `Error while validating configuration file`, `Invalid configuration file`, and `Writing new configuration file using defaults`. Therefore the inherited original configuration **failed the 0.5.0 schema** and Valetudo+ generated a new default configuration in the disposable test folder. No production config replacement has been shown.
- The console log also has markers `Starting Valetudo`, `Autodetected`, and `Webserver running on port`. The application logfile also has all three latter markers. This establishes the process eventually reached **robot detection and webserver's listening callback**, despite the earlier 60-second polling showing no known listener during its sample points. It does **not** yet establish persistent listener availability after reboot, which port was selected or the exact readiness time; no HTTP response or successful production auto-start has been shown.
- `stdio.log` reached 3,036 bytes, `valetudo.log` 2,087 bytes after the 60-second probe. Both logs contain `CloudSecret` and `LocalSecret` markers. These logs must remain private; never paste their raw contents, upload them or commit them.
- Subsequent read-only process enumeration showed **no remaining Valetudo PID**, and the stop-check did not identify a surviving probe PID. Thus the earlier `WARNING_PROCESS_REMAINS` did not prove a persistent orphaned process.
- The parent-fork baseline *is loadable and capable of starting an HTTP server in a disposable environment*. The narrowed practical blockers are an incompatible 2026.10.0 configuration, an incorrect boot-time environment variable, and as-yet-unverified readiness/persistence timing. No test has yet proved either blocker completely accounts for the earlier boot failure or our custom candidate's startup behaviour.

**Next gate:** (1) keep the immutable original and original configuration backups; (2) verify port 80 and a real local HTTP response on a longer bounded, single-instance **disposable baseline** test, preferably reusing a separately copied *0.5.0-generated* config to avoid another migration; (3) only after that, build a **separate persistent baseline configuration directory** and minimally update the production launcher while retaining the existing executable path. A boot/HTTP check and a documented original-binary rollback remain mandatory. No CleanGenius controls are validated by these observations.


## Stage 8: clean parent baseline HTTP 200 after ~80 seconds (2026-10-20)

The user performed a **bounded, manually controlled** Stage 7 diagnostic with the *official Algid Valetudo+ 0.5.0* AArch64 binary (known release SHA-256 `e0353c4feb141f48e3ab4a6ca6ca55ee6ffe21d7e63a0fc81547104762079e80`) and a separate disposable configuration directory cloned from the schema-reset configuration produced by the prior probe. It did not replace the protected original config, and the script required the saved original binary checksum match. It first checked there was no already running Valetudo PID.

**Observed progression:**
- 10–70 seconds: process present; RSS ~37,072–60,248 kB, state `R` and 6 threads, CPU ticks steadily increased; TCP port 80 not yet listening.
- At **80 seconds**: process state changed to `S`, 10 threads, RSS ~60,336 kB; **TCP port 80 was listening**, localhost HTTP GET produced status **200**. The script printed `BASELINE_HTTP_VALIDATED`.
- Both redacted/sanitized log marker groups included `Starting Valetudo`, `Autodetected`, and `Webserver running on port`. No config-validation markers were printed in this fresh-clone run.
- The test intentionally terminated and reaped the isolated instance, ending with `X40_STAGE7_CLEAN_BASELINE_COMPLETE`. Thus this is a validated **temporary** clean parent-binary startup, **not yet** a persistent unattended boot verification, and not a successful start of the custom forked X40 binary.

**Engineering conclusion:** Early negative 10/60-second listener checks were premature. The parent binary reaches healthy HTTP 200 after roughly 80 seconds given a valid fresh 0.5.0 configuration and `VALETUDO_DATA_PATH`; a substantial synchronous/CPU-bound pre-listener period remains to be characterized separately if needed. The original 2026.10.0 config is not accepted by the older parent schema and must not be overwritten or automatically reset as part of baseline selection.

**Persistent-baseline plan (pending user-side execution):** retain the original `/data/valetudo` executable backup and pristine `/data/valetudo_config.json`; place a **copy of the validated 0.5.0 config** in a dedicated private `/data/valetudo-plus-baseline-0.5.0/` directory. Adjust only the single verified Valetudo launch line in `/data/_root_postboot.sh`, retaining the original `VALETUDO_CONFIG_PATH` variable while adding `VALETUDO_DATA_PATH=/data/valetudo-plus-baseline-0.5.0` and a dedicated `VALETUDO_LOG_PATH`. Pre-stage an exact launcher backup and a verified original binary; reject unexpected script text, missing config or existing process. Boot, wait >100–180 seconds, verify that the **same** official executable remains, TCP port 80 and HTTP 200 persist, and that live environment points to the baseline directory. If unsuccessful, restore both original binary and original launcher from backups without using the original config as the parent's writable test config. No firmware edits or experimental CleanGenius writes.

The exact cause of the custom forked candidate's failed boot remains **unproven**; parent working startup is an important isolation baseline, not automatic proof that the configuration change fixes all custom features.


## Stage 9: controlled parent-versus-fork A/B startup result (2026-10-20)

User-executed, **explicitly authorized maintenance** using the Stage 9 scripts, with the production parent baseline and its already validated `VALETUDO_DATA_PATH`. The read-only preflight before downtime reported:

```text
X40_STAGE9_BASELINE_FINGERPRINT_BEGIN
PARENT_SHA256_PASS
CANDIDATE_SHA256_PASS
BASELINE_AND_ORIGINAL_CONFIG_PRESENT
RUNNING_PARENT_PATH_PASS
PORT_80_LISTENING
HTTP_STATUS=200
X40_STAGE9_BASELINE_FINGERPRINT_PASS
```

The working parent `/data/valetudo` has SHA-256 `e0353c4feb141f48e3ab4a6ca6ca55ee6ffe21d7e63a0fc81547104762079e80`; the previous failed X40 candidate was preserved with SHA-256 `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`. Config file hashes were also recorded without displaying contents.

The maintenance script verified the parent process, temporarily stopped it, made a *private executable copy* of the existing fork candidate and a *private configuration copy* of the parent baseline, and launched the fork with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Observed:

- At 10–70 seconds, the fork was present but there was no port-80 listener. Memory increased ~36–60 MiB, with six threads in most samples.
- At **80 seconds**, ten threads were observed; **port 80 listened and HTTP GET returned 200**.
- The fork-specific read-only `GET /api/v2/robot/clean-genius/status` returned **HTTP 200**.
- Presence-only logs included `Starting Valetudo`, `Autodetected` and `Webserver running on port`. Raw startup logs were **not** shared and must remain private because the application can log credentials.
- The script emitted `X40_STAGE9_FORK_HTTP_200_PASS` and then `X40_STAGE9_REBOOT_TO_RESTORE_OFFICIAL_BASELINE`. This final marker signifies the **reboot was requested**, **not** that the restored parent has been independently verified following that reboot.

**Conclusion:** Contrary to the original early-reboot inference, the exact previously failed candidate **can start successfully on the X40** with a compatible parent-fork configuration and ~80 seconds initialization. The original nonstartup incident is consistent with an incompatible/missing `VALETUDO_DATA_PATH`, old-config schema handling and/or an observation window shorter than the actual startup time; their individual causal contributions were not isolated. This is a *temporary A/B startup and endpoint reachability pass*, **not** validation of the returned CleanGenius/dock status payload, native dirtiness inference, cleaning features or unattended production startup.

**Next gates:** re-run the read-only parent fingerprint after the reboot and verify a live HTTP 200; separately validate a strictly sanitized X40 status JSON contract during a supervised candidate run with the experiment flag off; validate default SmartHost behaviour, maps and normal controls before considering permanent fork promotion. Keep the original upstream and working parent binaries and both configurations available for rollback. No experimental MIOT writes or device firmware modifications.

## Stage 10: HTTP/schema pass without live cache observations (2026-10-20)

The user completed the supervised Stage 10 fork A/B maintenance: startup and the X40-only read-only status endpoint responded HTTP 200, six captured status GETs returned HTTP 200, and the original **official Algid 0.5.0** baseline was confirmed again after reboot with matching parent/candidate SHA pins, HTTP 200 and unchanged baseline/original configuration hashes.

However the **six original JSON responses** and sanitized `X40_STAGE10_READONLY_CONTRACT_V1` report all have `state="unavailable"`, `observedAt=null`, all five CleanGenius-related settings `unavailable`, dock `unavailable`, zero dock transitions and no native dirtiness measurement. `contract_pass=true` means only **valid schema and disabled experimental policy**, not live observation.

**Call-chain correction:** Stage 10 polled only `GET /api/v2/robot/clean-genius/status`, which returns a pre-existing cache; it never invoked `GET /api/v2/robot/state`, which calls `robot.pollState()`. The X40 inherits from `DreameGen4ValetudoRobot` (not Gen2 directly). The **Gen4** `getStatePropertiesToPoll()` **does include MIOT 4:50**; the X40 override additionally polls mop-dock status. Therefore the earlier suspicion that the X40 ordinary poll lacks MIOT 4:50 was incorrect. No application modification or added MIOT polling property is justified yet. Actual cache population after a normal state poll remains unverified.

The next separate `Stage 11` diagnostic is designed to trigger ordinary `GET /state` before reading the status cache, six times, then sanitize output with a stronger **live-data gate**. Its self-test reproduces that Stage 10 samples pass the JSON contract but **fail** actual live-data evidence (`settings_observed_samples=0`, `dock_observed_samples=0`). **Safety qualification:** the state-poll GET may invoke existing automatic SmartHost disabling or water-hookup acknowledgement writes inside Valetudo; it is not a guaranteed firmware-read-only operation despite being an HTTP GET. Experimental CleanGenius writes remain off. It is a supervised, reversible maintenance test, not a new release or automatically approved deployment.

See [Stage 11 diagnostic plan](https://github.com/angelcode1/Valetudo-plus/blob/diagnostics/x40-stage9-parent-fork-ab/docs/X40_STAGE10_11_READONLY_OBSERVATION_GATE.md). The official baseline stays the only approved persistent installation.

## Stage 11: MIOT settings and dock status confirmed from normal state polls (2026-10-20)

The user submitted six individual **read-only status JSON snapshots** and a sanitized report `X40_STAGE11_POLL_CACHE_CONTRACT_V1`, captured in the supervised temporary fork run with the experimental controls disabled. The new diagnostic explicitly requested the normal robot `GET /api/v2/robot/state` endpoint **before** each cached `GET /api/v2/robot/clean-genius/status` read, correcting Stage 10's missing poll. The local files were independently checked on 2026-10-20; no raw logs/configuration, keys, maps, camera data or firmware binaries were committed.

**Verified results:** `sample_count=6`, `contract_pass=true`, `live_data_pass=true`, `settings_observed_samples=6`, `dock_observed_samples=6`. Each source response reported `state=observed`, `stale=false`, `dockWashActivity.state=observed`, `dockWashActivity.stale=false`, and `valetudoPolicy=auto_disable_smart_host_when_positive`. The six settings ages were 176, 98, 86, 102, 81 and 80 milliseconds; corresponding dock ages were 158, 97, 85, 101, 80 and 79 milliseconds, i.e., freshness is verified at the sample times. Successive readings were around 15 seconds apart.

All six sanitized samples agreed on these **settings**, not live cleaning events:

| Native key | Value | Interpretation |
| --- | ---: | --- |
| `SmartHost` | `0` | CleanGenius setting off |
| `SmartAutoMop` | `-1` | Unknown/sentinel; do not coerce or write |
| `SmartAutoWash` | `0` | Auto Rewash setting off |
| `StainIdentify` | `1` | Stain Identification setting on; **not** a detection event |
| `HotWash` | `1` | Hot Wash setting on; **not** a temperature measurement |
| `MOP_DOCK_STATUS` | `0` | Dock idle in all six samples; one initial idle transition, no observed wash/re-wash event |

All six returned `nativeMopDirtiness=unavailable_no_verified_local_status_interface`; no measured dirtiness, turbidity value, AI stain classification, automatic rewash decision or wash-trigger origin is established. The `SmartAutoMop=-1` observation matches the earlier R2416 device observation and must remain **unknown**, not "off". **Experimental controls were disabled**; do not enable them based on these results.

**Source closure:** `DreameX40UltraValetudoRobot` inherits `DreameGen4ValetudoRobot.getStatePropertiesToPoll()`, which already requests MIOT `4:50`, while the X40 override requests the mop-dock property. X40's parser populates both sanitized caches from a successful normal state response. Therefore **no new MIOT poll or parser fix is required for these two read-only observations**. Its read-only status route does not itself refresh the MIOT cache; the React page currently refreshes only that cached route at 15-second intervals. Without normal robot state traffic, the UI may legitimately show unavailable or stale observations even though the endpoint returns HTTP 200. Assess the UI behaviour separately instead of adding a new background hardware poll blindly.

**Remaining gates before fork promotion:** (1) verify post-maintenance parent baseline and preserved config hashes again (not provided with this Stage 11 upload); (2) validate normal robot state, maps, dock functionality and web UI with the fork under supervision; (3) verify unattended fork boot with explicit `VALETUDO_DATA_PATH`, proper rollback, and the experimental controls absent. Native dirtiness/event telemetry and writable CleanGenius remain **separate, unverified research**. The user has not authorized permanent candidate deployment by merely uploading these results.


## Stage 12: parent recovery verified and normal-function A/B planned (2026-10-20)

The user's latest **post-Stage-11** read-only fingerprint fully passed: `PARENT_SHA256_PASS`, `CANDIDATE_SHA256_PASS`, `BASELINE_AND_ORIGINAL_CONFIG_PRESENT`, `RUNNING_PARENT_PATH_PASS`, `PORT_80_LISTENING`, `HTTP_STATUS=200` and `X40_STAGE9_BASELINE_FINGERPRINT_PASS`. The baseline configuration SHA-256 remained `eca068eef7dfc1e1b6dd26a82aa25b7680a4586f63c892e5a29ab4805548fcb6` and the protected original configuration SHA-256 remained `f594fc798706c538d0d2c89f4be022af6ae8905f3c78d0e06f867e843d422018`. This confirms recovery of the unchanged parent **after** the successful Stage 11 poll/cache capture.

An independent operator-side `x40-stage12-normal-function.zip` test kit was built and its shell syntax and archive integrity checked **offline**. No Stage 12 robot test has been run by this assistant. Its **separately opted-in** maintenance script uses the now-proven approach: fingerprint the existing parent, inspect comparable baseline GET endpoint HTTP codes and downloaded byte counts without retaining response bodies, stop only the positively identified official parent, start a SHA-pinned private copy of the existing fork with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and a copied configuration, wait up to 240 seconds, probe the same normal robot endpoints plus the X40 status endpoint, and offer a bounded 120-second **manual UI inspection** window before attempting to stop the fork and reboot to restore the unchanged official parent.

The normal endpoint checks are `/api/v2/robot/`, `/api/v2/robot/properties`, `/api/v2/robot/capabilities/`, `/api/v2/robot/state`, `/api/v2/robot/state/attributes` and `/api/v2/robot/state/map`; the fork additionally checks `/api/v2/robot/clean-genius/status`. Responses are discarded; raw state, map, robot information, logs, and credentials are not included in shareable output. **A map HTTP 200 does not prove a nonempty or correct map**, capability endpoint success does not prove cleaning controls, and UI functionality is not validated without a human check. Ordinary state GETs can trigger existing firmware-level safety writes (e.g. SmartHost disable/acknowledgement), despite being HTTP GET methods; experimental writes stay disabled. The test requires idle/docked conditions, explicit maintenance opt-in, working SSH and independent recovery. It does **not** deploy the fork permanently, change the boot script or overwrite either existing config.

**Remaining gates:** actual Stage 12 execution, confirmation of post-maintenance restored parent, existing UI/map state and normal robot features, and separately authorized unattended fork boot/rollback validation. Do **not** claim native stain decisions or rewash telemetry from the existing MIOT setting observations.

## Stage 12: normal-function endpoint success, map payload still needs confirmation (2026-10-20)

The user executed the SHA-guarded Stage 12 maintenance A/B script and independently verified official Algid Valetudo+ 0.5.0 recovery with the fingerprint after reboot. Both before and after the test it reported `PARENT_SHA256_PASS`, `CANDIDATE_SHA256_PASS`, `BASELINE_AND_ORIGINAL_CONFIG_PRESENT`, `RUNNING_PARENT_PATH_PASS`, `PORT_80_LISTENING`, `HTTP_STATUS=200`, unchanged parent config SHA-256 `eca068eef7dfc1e1b6dd26a82aa25b7680a4586f63c892e5a29ab4805548fcb6`, unchanged original config SHA-256 `f594fc798706c538d0d2c89f4be022af6ae8905f3c78d0e06f867e843d422018` and `X40_STAGE9_BASELINE_FINGERPRINT_PASS`. Thus the maintained parent was restored and neither protected config changed.

**Stage 12 parent vs fork HTTP 200 comparison** (all endpoints returned HTTP 200):

| Endpoint | Warm parent bytes | Fresh fork bytes |
| --- | ---: | ---: |
| `GET /api/v2/robot/` | 232 | 232 |
| `GET /api/v2/robot/properties` | 26 | 26 |
| `GET /api/v2/robot/capabilities/` | 1729 | 1729 |
| `GET /api/v2/robot/state` | 11441 | 3696 |
| `GET /api/v2/robot/state/attributes` | 993 | 993 |
| `GET /api/v2/robot/state/map` | 10378 | 2633 |
| `GET /` | — | 831 |
| `GET /api/v2/robot/clean-genius/status` | — | 842 |

The fork became HTTP-ready after 80 seconds. The UI observation window completed and the user reported **"pages seemed to load"**, which is a useful subjective smoke check but does not certify visual map correctness, persisted rooms, all UI interactions, cleaning, docking or streaming. `STAGE12_NORMAL_ENDPOINT_HTTP_PASS`, `STAGE12_UI_WINDOW_COMPLETE`, and `STAGE12_ENDPOINT_GATE_PASS` were emitted before stopping the fork and requesting a reboot.

**Narrowed difference:** The total JSON response-size delta between parent and fork for `/state` equals **7,745 bytes**, precisely the map endpoint delta (10,378 − 2,633 = 7,745; 11,441 − 3,696 = 7,745). This is strong evidence that map payload differences explain the observed state-response size gap, rather than some missing ordinary robot attributes. It does **not** prove either map is correct or that all nonmap state content is equivalent.

The X40/Gen4 implementation seeds state with a `defaultMap:true` placeholder and receives normal map frames asynchronously through firmware map-poll/dummycloud paths. The Gen4 `determineNextMapPollInterval` implementation retries faster for a default map while `process.uptime() < 90` seconds, otherwise falling back to normal intervals. The 80-second fork map sample was therefore captured during an early, potentially cold-map interval. **Do not assert a map regression or claim successful map readiness solely from HTTP 200 or byte counts.**

**Next Stage 13:** Run a Mac-side in-memory JSON map structural classifier against the currently healthy parent, collecting only default-placeholder state, map layer/entity/segment counts and payload size, no coordinates or room labels. Then only with explicit maintenance authorization, temporarily run the SHA-pinned fork using the unchanged Stage12 safety pattern, grant a 240-second map observation window and collect six identical sanitized readings at ~30-second intervals. Visually confirm a nonplaceholder real map in the fork UI, and independently confirm the original parent, SHA pins and config hashes after maintenance. Keep both original and parent rollbacks, existing launcher and experimental-write-disable flag unchanged. Stage 13 is **not** yet user-executed. No production changes authorized by this finding.

## Stage 13: fork map reaches the same non-placeholder structure as parent (2026-10-20)

The user supplied the two **privacy-filtered map structural reports** `X40_STAGE13_SANITIZED_MAP_READINESS_V1` (`role=parent` and `role=fork`). They contain no coordinates or floorplan/map pixel data. Results were independently verified from their JSON files:

| Role / sample | Nominal relative time | Parse | Placeholder | JSON bytes | Layers | Entities | Segment layers | Positive layer area |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| Parent 1 | 0 s | yes | not_marked | 10,378 | 2 | 2 | 0 | yes |
| Fork 1–3 | 0, 30, 60 s | **no response parsed** | unknown | 0 | — | — | — | — |
| Fork 4 | 90 s | yes | **yes** | 2,633 | 2 | 3 | 0 | yes |
| Fork 5–6 | 120, 150 s | yes | **not_marked** | 10,378 | 2 | 2 | 0 | yes |

The fork therefore **progressed from no parsed HTTP map, to a default placeholder, to the same populated-map structural metrics and exact JSON byte count as the warm official parent**, with the final nonplaceholder structure observed twice. The Stage 12 state/map payload-size delta of 7,745 bytes is consistent with comparing a cold placeholder to a warmed map. This is strong evidence against a persistent basic-map-loading regression in the tested fork. **This does not prove bytewise map equality, visual room geometry, persisted segmented rooms, actual cleaning or dock-wash behavior.** Zero segment layers appeared in both reports; do not present room segmentation as validated. Nominal times are relative to the profiler, not known precise elapsed time since process launch. The initial three zero-byte samples do not distinguish pre-listener startup, connection failures or timeouts.

**Outstanding operational confirmation:** No post-Stage-13 *recovery fingerprint output* or human statement that the rooms displayed correctly was included with these two uploads. Even though the Stage 13 maintenance script normally requests reboot of the unchanged parent, only a fresh `X40_STAGE9_BASELINE_FINGERPRINT_PASS` with the same pinned configuration SHA values establishes that the parent is presently restored.

**Stage 14 proposed next gate, not yet executed or authorized by the upload:** an independent Mac-distributed `x40-stage14-fork-promotion.zip` kit has been created and statically validated offline. The kit provides the existing parent fingerprint, explicit user-initiated staging of the SHA-pinned fork as `/data/valetudo` with a **separate fork-specific copy** of the working parent configuration, fresh parent executable and launcher backups, the experimental flag explicitly `0`, a **separate manual reboot**, a read-only post-boot fork process/environment + HTTP verification, and an explicit user-initiated parent binary+launcher rollback script with a separate manual reboot. The scripts do not run automatically on the robot. The two-file executable/launcher replacement is not a single atomic transaction; interruption between the renames requires rollback. A successful HTTP 200 or map structural profile alone does not validate unattended ordinary cleaning, navigational integrity, multi-map, camera streaming, or docking actions. Keep native CleanGenius writes disabled and the original upstream executable/config protected.

## Stage 14: the SHA-pinned X40 fork is installed and boots normally (2026-10-20)

**New direct operator result:** The user explicitly executed `stage14_stage_fork.sh`, which printed `X40_STAGE14_PREFLIGHT_PASS`, `X40_STAGE14_FORK_STAGED_PASS`, `RUNNING_PARENT_IS_UNCHANGED_UNTIL_REBOOT` and `NEXT_STEP_MANUAL_SYNC_REBOOT`. They then manually ran `sync; reboot` and subsequently `stage14_verify_fork_boot.sh`, which printed:

```text
X40_STAGE14_BOOT_VALIDATION_BEGIN
FORK_HASH_AND_PROCESS_PATH_PASS
FORK_UI_HTTP=200
FORK_STATUS_API_HTTP=200
X40_STAGE14_BOOT_VALIDATION_PASS
```

The Stage 14 boot validator verifies actual executable `/data/valetudo` SHA-256 `45d42b35850e27a3c0d4f57204cd343a9c124aa6d381ad52ac5476a2ffd6fee6`, single process with expected binary path and `VALETUDO_DATA_PATH=/data/valetudo-x40-fork-stage14`, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, presence of the saved parent launcher, exact official Algid binary backup SHA-256 `e0353c4feb141f48e3ab4a6ca6ca55ee6ffe21d7e63a0fc81547104762079e80`, original upstream backup SHA and both protected config SHA pins. The user's printed output confirms **all those script assertions passed**, although it does not show the individual values or establish log/long-term health.

**Conclusion:** The forked CI candidate has now **passed persistent boot validation following a device reboot**. The prior failed startup is superseded by a verified functioning fork installation with the correct parent-compatible config directory, verified boot launcher, preserved parent and original binaries, and explicit experimental-control opt-out. This is *not* evidence that the fork is safe to enable experimental SmartHost/Auto Rewash writes, that ordinary cleaning/docking/streaming is fully validated, or that native dirtiness/turbidity or rewash-decision telemetry exists. The Stage 13 fork map became nonplaceholder structurally at later elapsed observations, but a post-Stage-14 map/UI check is still needed.

**Stage 15 planned acceptance:** A new operator-side `x40-stage15-postinstall-health.zip` monitor has been created and syntax/self-test checked offline only; it has **not been executed against this currently installed robot**. It reuses Stage 14's exact read-only SHA/process/env boot verifier and uses the Mac standard library to sample five fixed HTTP GET endpoints (UI root, robot identity, capability list, cached map and cached X40 settings) eight times at 30-second intervals. Only structural map metadata, read-only X40 observation/policy labels, HTTP statuses and counts are included in shareable JSON; never persist or print map/credentials/native values. The sampler **does not** GET `/state` or call firmware property polls and thus avoids intentionally triggering their existing SmartHost/water-hookup writes. A stable service requires persistent HTTP 200 and two or more populated, nonplaceholder map observations; cache stale/unavailable does not on its own fail this monitor, since it intentionally does not trigger MIOT refresh. After that, human-only supervised check of ordinary UI/map and optional physical cleaning and docking are still needed. Keep the Stage 14 parent rollback script and private logs/configs secure.

**Repository scope:** this is a documentation-only status update. It does not install/reboot/change the live robot or commit binary/config/logs. Do not execute rollback on a healthy instance.
