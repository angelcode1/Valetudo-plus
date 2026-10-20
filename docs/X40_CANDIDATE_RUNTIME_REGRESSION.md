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

## Stage 15: persistent fork health sampled successfully; cached status stale by design (2026-10-20)

The operator ran the Stage 15 self-test (pass: `no_network=true`, `no_raw_map_or_secrets=true`, `get_only=true`), followed by the **read-only installed-fork fingerprint**, 8 sampled network observations at 30-second intervals, and the same fingerprint after sampling. Both fingerprint runs reported `FORK_HASH_AND_PROCESS_PATH_PASS`, `FORK_UI_HTTP=200`, `FORK_STATUS_API_HTTP=200`, `X40_STAGE14_BOOT_VALIDATION_PASS`, and `X40_STAGE15_FORK_FINGERPRINT_PASS`. This means the SHA-pinned fork executable, process path, required environment, experimental opt-out and protected rollback checks passed **before and after** the network sample set; raw config contents and logs were not exposed.

**All eight monitor samples:** `HTTP_ALL_200=True`, `MAP=not_marked` (i.e., not the default placeholder), `MAP_BYTES=10378`, `STATUS=stale`, `DOCK=stale`, `POLICY_DISABLED=True`. Aggregate monitor output: `ALL_HTTP_200=True`, `ALL_X40_DRIVER=True`, `ALL_STATUS_CONTRACT_AND_POLICY=True`, `NONPLACEHOLDER_MAP_SAMPLES=8`, `STABLE_READINESS_PASS=True`. Eight samples with 30-second spacing cover ~210 seconds between the first and last measurements; this is a short-term service health pass, **not** long-term reliability, physical cleaning/docking, or map correctness proof.

**Freshness qualification:** Stage 15 intentionally used *only* cached read-only HTTP GET endpoints and did **not** request the firmware-backed `GET /api/v2/robot/state`. Therefore neither status nor dock cache was refreshed by this monitor, and their 120-second observation time-to-live expired. This is expected for the tested no-poll sequence and is **not** evidence of MIOT transport failure. In contrast, Stage 11's supervised `GET /state` followed by cached status produced **six fresh setting and dock observations out of six** on the same candidate executable. Do not "fix" stale cache by silently adding hardware polling to a GET-only monitor, and do not equate `getCleanGeniusReadOnlyStatus()` with a fresh hardware read. Frontend manual refresh currently re-GETs the cached endpoint; a separate future UX change could offer **explicit user-initiated** normal state polling (with a clear side-effect warning), but this has not been built or deployed.

**Next gates, without touching the healthy installation:** (1) visually verify the installed map, intended rooms and manual control UI; (2) perform a supervised normal cleaning/return-to-dock cycle initiated by the operator via established UI or physical controls, with standard physical stop accessible; (3) observe ordinary mop wash and dock status without claiming turbidity or native CleanGenius decisions; (4) separately validate camera/duststreaming, multi-map and MQTT integrations if those functions are required; (5) retain official Algid 0.5.0 and original upstream binary/config backups and keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Never send synthetic AVA messages or test experimental MIOT writes as part of this acceptance. Device firmware and installed executable are unchanged by this documentation update.


## Stage 16: installed fork refreshes native read-only caches in 13 of 13 samples (2026-10-20)

The operator supplied two privacy-filtered JSON artifacts from the **permanently installed** X40 fork: `x40-stage16-normal-state.json` (1 sample) and `x40-stage16-cycle-observations.json` (12 samples). Both identify `X40_STAGE16_NORMAL_STATE_CHECK_V1`, `normal_state_poll_cache_pass=true`, `no_raw_state_or_map_or_credentials=true`, `operator_initiated_http_get_only=true`, and `ordinary_valetudo_safety_writes_possible=true`. The samples were independently parsed and checked against the reported counts.

The single sample occurred at `2026-10-20T04:39:54Z`; the 12-sample collection spanned `2026-10-20T04:40:07Z` to `04:45:39Z` (332.28 seconds, approximately 5 minutes 32 seconds). Across all **13 / 13** samples, both settings and dock cache reported `observed` and `stale=false`; both tested HTTP endpoints returned 200 and experimental writes remained explicitly disabled. The native values were constant:

| Setting/status | Observed in 13/13 | Safe interpretation |
| --- | --- | --- |
| `SmartHost` / CleanGenius | `off` | Existing positive-SmartHost safety policy maintained |
| `SmartAutoMop` / Auto Reclean | `unknown` | Preserved the known `-1` sentinel; **do not equate with off** |
| `SmartAutoWash` / Auto Rewash | `off` | Setting off, no observed automatic rewash action |
| `StainIdentify` | `on_setting` | Native configuration, **not** a stain classification event |
| `HotWash` | `on_setting` | Native configuration, **not** a measured wash temperature |
| Mop dock | `idle` | One initial idle entry, **no recorded dock transitions** |
| Native mop dirtiness | `unavailable` | No verified native telemetry source |

**Interpretation and limitation:** The normal firmware-backed `GET /api/v2/robot/state` successfully populates both X40 status caches on the **persistent** fork in all 13 test samples. Stage 15's `stale` readings were the expected result of querying only the cache, without new MIOT state polls; that does **not** imply the driver or firmware is broken. However, nothing in these files establishes that a cleaning or mop-wash cycle was actually run during the twelve observations: all dock samples remained idle, the dock transition count remained one, and no native dirtiness or automatic rewash event was reported. A short-lived event between 30-second polls could also be missed. Do **not** mark the physical wash/dock cycle as validated.

**Next user-controlled acceptance, without new deployment:** observe the map and intended rooms in the UI, then run a small ordinary supervised cleaning/return-to-dock cycle using existing Valetudo controls with physical stop accessible. If a normal mop wash occurs, use the Stage 16 read-only observer to report dock activity while keeping actual native CleanGenius writes disabled. The observer uses ordinary `/state` GET, which can still invoke Valetudo's existing safety writes; do not label it guaranteed side-effect-free. Keep the official parent and original upstream backups available for rollback. After the physical cycle, decide separately whether to add **explicit user-initiated status refresh** UX, rather than unattended extra MIOT traffic. No application code, firmware, configuration or robot state was changed by this documentation commit.


## Stage 17: supervised dock-observer sample contained no activity transitions (2026-10-20)

The user uploaded `x40-stage17-dock-cycle.json`, independently inspected as a sanitized `X40_STAGE16_NORMAL_STATE_CHECK_V1` report. Its **12 samples** span `2026-10-20T04:50:29.471381+00:00` through `2026-10-20T04:56:01.292979+00:00` (**331.82 seconds, ~5m32s**). All twelve report `attributes_endpoint_http_200=true`, `status_endpoint_http_200=true`, `settings_observation=observed`, `settings_stale=false`, `dock_observation=observed`, `dock_stale=false` and `experimental_writes_disabled=true`. They show an unchanged `dock_state=idle`, `dock_transition_count=1` (only the initial idle entry), `native_dirtiness_telemetry=unavailable`. The safe settings labels match Stage 16: `cleanGenius=off`, `autoReclean=unknown` (preserve `SmartAutoMop=-1`), `autoRewash=off`, `stainIdentification=on_setting`, `hotWash=on_setting`.

**Evidence limit:** This proves the installed fork's existing MIOT polling and cached dock-state API remain responsive/fresh during the monitor. It **does not prove that a physical cleaning task, return-to-dock, or mop wash occurred**, because the Stage 16-derived report does not include ordinary cleaning/task state and all dock samples were idle. A short transition between ~30-second samples might be missed; no user visual confirmation of robot motion, dock arrival or wash was supplied alongside the upload. This is **not a negative physical wash test**; physical-functionality acceptance remains open.

A separate optional **Mac-side only** `x40-stage18-cycle-evidence.zip` was prepared with an offline-tested Python 3 script, using GET `/api/v2/robot/state/attributes` and cached `/api/v2/robot/clean-genius/status` at a configurable cadence (defaults 10 seconds) to record **only allowlisted** robot-status labels (`cleaning`, `returning`, `docked`, etc.), high-level dock activity labels and sanitized observation/policy fields. It does **not** issue cleaning commands, modify application settings or reboot. As before, the ordinary Valetudo `/state/attributes` endpoint may trigger built-in firmware safety writes such as SmartHost disable, so it requires a visible CLI opt-in. It never stores raw state, map, credentials, logs, sensor values or geometry and it never claims physical success from HTTP data alone. Offline unit self-test and Python compilation pass, and the ZIP integrity was checked. The tool is **not executed on the user's X40 by this commit**. The operator should initiate and physically supervise a small normal cleaning job if desired; keep the existing parent rollback backup, and leave experimental CleanGenius writes disabled.

**Do not mark physical cleaning/washing validated until the operator confirms a real cycle and the state sequence provides corroborating evidence.** Native stain/turbidity/rewash decision telemetry remains unavailable.

## Stage 18: partial supervised cleaning run, paused without a captured dock wash (2026-10-20)

The user uploaded `x40-stage18-cycle-sanitized.json` with marker `X40_STAGE18_SANITIZED_CYCLE_OBSERVATION_V1`. The diagnostic was **interrupted** after 57 of 90 requested samples, at 10-second cadence from approximately **2026-10-20T06:28:15.808Z** through **06:37:35.705Z** (9m20s). The JSON is sanitized and contains no raw map, state JSON or credentials; no robot job commands were issued by the observer. The user said they plan to run it again.

**All 57** samples: `state_http_200=true`, `cache_http_200=true`, `settings_observation=observed`, `dock_observation=observed`, `policy_disabled=true`. Normal high-level robot-state progression in the 57 samples was:
- **Samples 1–3**, 0–20s: `docked`.
- **Samples 4–26**, 30–250s: `cleaning` (reported state, not independent visual proof of motion).
- **Samples 27–57**, 260–560s: `paused` (reason unknown; no safe inference that the fork caused this or that the robot was stuck).

The ordinary dock state attribute was `emptying` at samples 3–4 (roughly 20–30s), then `idle`. This is compatible with a **dust auto-emptying state**, not a mop-wash event. The X40 native mop-dock status remained `idle` for **all 57** samples with `dock_transition_count=1` (initial idle only). `returning_observed=false` and `dock_wash_activity_observed=false`; the observer's `physical_cleaning_or_washing_confirmed=false` accurately limits any physical-functionality claims.

**Conclusion:** Persistent fork HTTP and MIOT observation remained healthy during a partial reported cleaning run, with experimental writable CleanGenius disabled. The transition to `cleaning` demonstrates normal task-state reporting through Valetudo, not completion of actual cleaning. Pausing is observed but the cause is unknown; don't attribute it to software or initiate unsupervised movement to reproduce it. The recording does **not** verify return-to-dock, native mop wash, rewash trigger or native dirtiness sensing.

**Next operator-controlled gate:** Repeat the existing Stage 18 observer, ideally starting before a small supervised normal cleaning cycle and continuing past its return to dock and any wash. Use `--samples 180 --interval 10` only if a longer window is desired, with the robot's normal physical controls accessible. Ask whether the pause was intentional if it recurs; avoid speculative diagnostics without evidence. No need to reinstall or change the existing fork. Maintain the Stage 14 parent rollback and explicit experimental-control opt-out. The uploaded sanitized JSON stays out of the public repository.

## Stage 19: CleanGenius research proceeds while physical-cycle validation is deferred (2026-10-20)

The user elected to **defer further physical cleaning/return-to-dock/wash testing** and advance the native CleanGenius investigation instead. Stage 18 remains a partial normal-state report (docked → cleaning → paused, brief emptying, no returning/wash evidence). The installed SHA-pinned X40 fork remains in place, with experimental CleanGenius controls disabled and official Valetudo+ / original upstream backups protected.

**New research-only prototype, not merged or deployed:** branch [`research/x40-cleangenius-passive-miot61`](https://github.com/angelcode1/Valetudo-plus/tree/research/x40-cleangenius-passive-miot61) contains a pure, value-free probe and an X40-only, naturally incoming `properties_changed` observation hook. The candidate is based on the saved R2416 `MsgClean::RptStationAutoWashState` compiled MIOT reporting path with **PIID 61, unverified SIID**. The hook counts only bounded SIID identities and timestamps and forwards each notification to the existing superclass handler. It neither requests nor writes MIOT properties, touches raw `value` fields, subscribes to private AVA traffic, nor changes normal Gen4 SmartHost safety behaviour. The GET-only X40 status API gains a **research-labelled** `nativeWashNotificationCandidate` field, explicitly `candidateIdentityVerified=false`, `semanticMeaningVerified=false`, `valuesCollected=false`. It cannot prove actual wash, native dirtiness, turbidity or rewash decisions, and it is not on the robot.

Seven offline Node tests of the pure probe passed (including a throw-on-access `value` getter, bounded count/services, no device commands and clock regression). The full fork backend tests and build were not run, and there is **no live notification evidence**. A separate ZIP provides an anchor-checked optional *Mac-source-only* patcher, dry-run by default. Do not promote research branch or deploy to robot until its SIID and protocol semantics are investigated through **private offline** firmware analysis and the user later opts into ordinary supervised observation. No AVA injections, capture hooks, synthetic messages or native experimental writes.

**Separation of paths remains critical:** the compiled AVA `AI_MOP_DIRTY_INFO` sender/Lethe receiver route is separate from the unverified external MIOT PIID 61 status property and the already device-proven MIOT 4:50 CleanGenius *settings*. Never reinterpret `SmartAutoMop=-1` as off or advertise a dirtiness measurement where none exists.

## Stage 20: offline-only wash reporter SIID gate (2026-10-20)

The user elected to continue native CleanGenius research **without running another physical wash/dock cycle**. The installed fork remains unchanged and the Stage 18 physical-cycle gate remains open.

**Known prior compiled evidence:** in the user's privately saved R2416 native `node_msg_cvt.so`, `MsgClean::RptStationAutoWashState` formats a property report with *PIID 61*, but the *SIID is instance-dependent and has not been recovered*. The compiled setter/getter/report routines alone do not demonstrate a live local MIOT property or native mop dirtiness. Separate `AI_MOP_DIRTY_INFO` AVA messages and the verified `4:50` *settings* are distinct sources and must not be conflated.

**New Stage 20 artifact:** `x40-stage20-offline-siid.zip` is a private-Mac offline tool requiring an existing, privately saved AArch64 `node_msg_cvt.so`. The analyzer performs narrow ELF symbol and disassembly checks and emits a bounded privacy-filtered JSON summary of `MsgClean` reporter/getter/setter/constructor presence and limited structural instruction evidence. It always leaves `candidate_service_id=null` and `service_id_established=false` because symbol/member-offset hints alone do not determine the configured service identity. It never connects to the robot, emits commands, logs raw disassembly, or exports proprietary binaries.

**Validation:** Script self-tests, `py_compile`, and ZIP integrity **passed**; a synthetic non-proprietary AArch64 ELF library built using clang/lld exposed all four target function categories, and the analyzer correctly detected those and its synthetic literal PIID 61. **The tool has not run on the user's real private firmware**, so the SIID and actual live event behavior are **still unknown**. Only a future `x40-stage20-sanitized.json` from the user-local analysis can narrow that gap. No full CI/build nor on-robot probe has been performed for Stage 19 source changes.

The research documentation was committed separately to `research/x40-cleangenius-passive-miot61` at [Stage 20 offline reporter audit](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md). Stage 19's passive property notification collector remains **research-only, not installed**; `master` and the live robot continue to use the validated read-only `4:50` cache and dock status. Preserve `SmartAutoMop=-1` as unknown, leave `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, and do not try speculative `4:61` polling or AVA injections.

## Stage 21: private CleanGenius inventory and corrected tar transfer (2026-10-20)

The operator ran the standalone `x40_cleangenius_collector.py` against the existing rooted X40. Its **read-only discovery** succeeded, producing `X40_CLEANGENIUS_READONLY_DISCOVERY_V1`: **122 candidate static files**, **114 selected for a local private archive**, **8 MNN model weights excluded**. It enumerated `/ava/conf/r2416.conf`, `dconf_runtime.json`, `turbidity_check_config.json`, `auto_water_ctrl_config.json`, `dreame_stain1_v1.3.0.json`, `node_lethe.so`, `node_signal.so`, `node_camera_ai.so`, `node_msg_cvt.so`, `node_iot.so`, and additional content-matched `/usr/lib/tree_lib/liblethe_route_nodes.so`, `liblethe_tactics_tree.so` and `liblethe_tree.so`. These additional libraries are promising private static call-graph targets, **not** evidence of actual native CleanGenius decisions. The device was not modified.

**Original transfer bug and correction:** After discovery, the first collector printed `X40_CLEANGENIUS_COLLECTOR_FAILED: empty file`. Root cause was the SSH command vector `ssh host sh -c "exec tar ..."`: SSH concatenates the remote arguments into `sh -c exec tar ...`, so `sh -c` executes only `exec`, exits 0 and returns an empty stdout stream. This behavior was reproduced locally, including a zero-byte stream with exit 0. It is a **collector implementation defect**, not evidence of missing firmware files.

A new standalone Mac script `x40_cleangenius_collector_v2.py` fixes the transfer to pass one complete remote shell command argument (`ssh -T ... host 'exec tar -cf - -C / ...'`), validates nonempty/valid tar output and exact regular-file/path membership, and adds `--resume-manifest` to reuse the already-completed discovery without rescanning. Its offline self-test runs a **fake SSH executable** executing a synthetic local tar transfer; payload and manifest tests pass without network access. The corrected script was **not executed against the user's robot by the assistant**. If the source file size changes during transfer, the script stops rather than silently producing a potentially inaccurate ZIP.

**Privacy fix:** the first collector classified certain `/ava/conf/ai_models/..._cache` and `_priors/_coords.txt` files as ordinary auxiliary files even when MNN weights were excluded. V2 excludes those model-like artifacts by default as well. Applied to the supplied existing manifest, the correction selects **106 files**, drops **8** additional model caches/auxiliaries, totaling **61,690,477** expected uncompressed bytes, with core wash/AI libraries retained. The resulting `x40-cleangenius-PRIVATE-evidence-*.zip` remains private on the operator's Mac; do not upload binary contents or copied configuration to public GitHub. Share only sanitized discovery/analysis reports. This counts as safe inventory progress only: **no new MIOT service ID, live mop dirtiness, wash decision or native rewash evidence has been established**.

The working fork's experimental native CleanGenius writes remain disabled; official parent rollback continues to be preserved.

## Stage 22: actual R2416 archive confirms compiled MIOT 4:61 and wash decision call graph (2026-10-20)

The operator uploaded `x40-cleangenius-PRIVATE-evidence-20261020T083237Z.zip` (proprietary firmware; **never add to Git**) and the sanitized file manifest. Private offline inspection verified all **106 / 106** captured firmware file SHA-256 checksums and sizes against the archive's embedded private manifest, with CRC ZIP integrity. The eight original MNN model weights and eight additional model caches/auxiliary artifacts were not part of the final captured ZIP.

**Major new direct static finding:** The previously unknown `MsgClean::StationAutoWashState` service is **compiled as MIOT SIID 4 / PIID 61**. Exact verified AArch64 steps in `node_msg_cvt.so`: `MsgClean::MsgClean` passes integer **4** to `MsgHandler::MsgHandler(int,...)`; the base stores that argument in its service-ID field; `RptStationAutoWashState` loads the same field and uses literal **61** when forming a MIOT property report; `MsgClean` registers get and report callbacks for property **61**. `SetStationAutoWashState` changes a stored integer and queues a property report when changed. This is proof of a **compiled property identity**, **not** proof that the running robot supports `get_properties(4,61)`, that notifications are naturally emitted, what the numeric values represent, or that Auto Rewash/Dirtiness is externally observable. No live MIOT query was performed in this stage.

**New topology from the previously uncollected `liblethe_tactics_tree.so`:** exact dynamic ELF-resolved ARM64 direct PLT calls show `ChooseWashType → ChooseSmartHostWashType`, `ChooseWashType → ChooseAICheckWashType`, `InitTurbidityCheckInfo → TurbidityRecleanAndRewashSet`, `WashFloorTubidityCheck → TurbidityMonitorLogicRunEx`, and a tail branch `WashStateLogic → WashRunningPrecess`. The newly available `liblethe_route_nodes.so` exports `MopDirtyAccumulator::tick` and `StateCurrent::WriteAiMopDirtyData(ava_msg_mop_dirty_info const&)`. These are **compiled decision functions and links**, not proof any ran or that sensor events were generated.

**R2416 saved configuration**: exact model key `dreame.vacuum.r2416` in `dconf_runtime.json` has `RUNTIME_TURBIDITY_DETECTION="Single_Channel"` and `RUNTIME_SELF_CLEANING_WASH_PLATE="Y"`; `turbidity_check_config.json` has boolean `turbidity_check_config=true`. These stronger static configuration facts supersede the earlier reports that redacted/uninterpreted those literals, but do not establish a functioning live turbidity sensor.

**Implementation action:** On the **unmerged, undeployed** `research/x40-cleangenius-passive-miot61` branch, the value-free passive notification observer was narrowed to strict `siid=4, piid=61`. It still never reads vendor `value` fields, issues new MIOT requests, injects AVA messages or enables experimental quirks. Its old multi-SIID test expectations were updated; **the changed complete test suite still needs to run in a repo checkout/CI**. The private firmware was not checked into Git. Research branch docs provide the detailed offline evidence and limitations. A separate sanitized human-readable report and JSON audit were created as conversation artifacts, with no proprietary firmware contents.

**Next action only if the user opts in:** supervised, **read-only** check whether property `4:61` exists through a single allowlisted local MIOT get, or strictly passive naturally emitted events if present. Do not start cleaning, infer rewash from unrecognized codes, enumerate other properties, send firmware writes, or install the research branch prematurely. The user has deliberately postponed a physical cleaning/dock wash retest. Preserve the current stable production fork at `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and the official parent rollback.

## Stage 23: compiled internal 4:61 status updater and dispatcher (2026-10-20)

Using the already archived and hash-validated **private** X40 R2416 `node_msg_cvt.so`, an additional targeted **offline-only** AArch64 disassembly audit found a verified **single exact tail branch** from `AvaNodeMsgCvt::SetPropIntMsg(int,int,bool)` to the `MsgClean::SetStationAutoWashState(int,bool)` PLT stub **within the dispatcher's declared ELF function extent**. The shared status member at instance offset **0x2d4** is read by the getter, setter and reporter. The setter compares the old/new 32-bit value, updates it on change, and schedules a report with literal **PIID 61** and stored instance service ID. Stage 22 had already established the constructor stores **SIID 4** and registers PIID 61 get/report handlers. Together this establishes a **compiled internal update/get/report chain for MIOT 4:61**, not a proven live public API or firmware-derived numeric value mapping.

The offline `x40-stage23-native-wash-audit.zip` contains the exact-symbol analysis Python script, synthetic parser self-test, README and **sanitized** JSON audit; proprietary firmware files and full disassembly remain private, outside Git. The script itself is no-network/no-SSH/no-robot-command, validates AArch64 ELF identity, declared symbol sizes, exact function headers, and detects the LLVM17 missing-symbol false-zero situation. It passed its synthetic self-test and confirmed the chain in the user's collected archive.

Research-only `research/x40-cleangenius-passive-miot61` branch further clarified that the candidate's `livePropertySupported` is **null (unverified)**, not false (unsupported); its strict incoming-notification filter remains **SIID 4/PIID 61** and deliberately never inspects or saves vendor values. The **pure probe suite 7/7 passed** in an offline local Node 22 mirror with a syntax check; full fork integration build and actual robot validation have *not* run. The branch has **not** been installed, merged, or used to issue any MIOT query.

**Hard boundary still pending:** no trustworthy local read result for 4:61, natural `properties_changed` event, numeric station status semantics, observed native mop dirtiness/turbidity, or automatic rewash decision. Do not interpret the internal setter as permission for external writes. Leave production fork, experimental flags and rollback backups untouched; user postponed physical washing/docking test. Next meaningful data must come from separately authorized *single allowlisted read-only* live 4:61 query or trusted passive natural-notification observation, with privacy filtering, after choosing a device-supported access method. Avoid speculative CLI syntax or AVA injections.

## Stage 24: compiled AVA integer-message path leads to MIOT 4:61 status setter (2026-10-20)

Continued research used **only the saved private R2416 archive**, which passed ZIP CRC integrity and AArch64 ELF identity checks. A standalone Python script `stage24_offline_prop_path.py` passed synthetic parser tests and real offline analysis, `X40_STAGE24_OFFLINE_AVA_PROPERTY_CHAIN_V1`, without connecting to the X40. Its short sanitized report and source are packaged as `x40-stage24-offline-prop-path.zip` outside this repo; no native code, raw disassembly, credentials or maps were added to GitHub.

Exact verified ELF branch chain in `node_msg_cvt.so`:

1. `AvaMsgCvtPropIntProcess(ava_msg_device_prop_int*)` (12-byte ELF extent, 3 instructions): **one exact tail `b` branch** to `PropIntMsgProcess(ava_msg_device_prop_int&)`.
2. `PropIntMsgProcess` (756 bytes, 188 instructions): **two exact PLT branches** (one `b`, one `bl`) to `SetPropIntMsg(int,int,bool)`.
3. `SetPropIntMsg` (4,248 bytes, 1,060 instructions): **one exact PLT `b` branch** to `MsgClean::SetStationAutoWashState(int,bool)`.
4. `SetStationAutoWashState` (48 bytes, 11 decoded instructions) updates the previously verified stored status member (offset `0x2d4`) and references property ID **61**, with SIID **4** established independently in Stage 22.

Separately, `node_lethe.so` defines `ancp::AsyncDeque::_ProcessAsyncPub<ava_msg_device_prop_int>`, a compiled typed publisher facility matching the converter's typed input. This **does not** by itself establish the publisher of **StationAutoWashState specifically**, or live AVA event delivery. No raw vendor property values were extracted, and no public MIOT status-value enum has been established.

**Operational boundary:** The compiled internal path is now well supported, but the robot's local `get_properties(4,61)` support, actual natural notifications, meaning of integers, native dirtiness measurements and decisions to rewash are **all unknown**. The existing stable production Valetudo fork stays installed with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; original and official parent rollback assets are preserved. The Stage 19 source probe remains research-only, unmerged and undeployed; no new MIOT commands or firmware writes were made. No need to redo the private firmware collection.

## Stage 25: verified offline station-auto-wash blackboard input calls (2026-10-20)

Using the user's preserved private X40 R2416 archive (same 106-file ZIP; no additional device access), a new offline `liblethe_tactics_tree.so` ELF audit established exact symbol-and-target call-site evidence:

1. `RobotWIFI_Deal::WIFIState_Send::tick()` makes one direct PLT call to `updateStationAutoWashState()` (offset +780 from caller entry; full 2988-byte / 747-instruction extent checked).
2. `updateStationAutoWashState()` makes one direct PLT call to `BT::Blackboard::get<WashStatus>` (+2232) and one to `BT::Blackboard::get<ava_mop_station_msg>` (+2704); full 7836-byte / 1959-instruction extent checked.

Python source, synthetic tests, sanitized JSON result and README are packaged as **`x40-stage25-offline-wash-state.zip`**. Python compilation, parser self-test, ZIP integrity and actual R2416 offline read-only analysis passed. An initial **false incomplete-disassembly failure** was diagnosed as the parser skipping `nop` lines due to whitespace/newline consumption and fixed; a synthetic regression test now covers those instructions. **No proprietary binaries or raw disassembly are published.**

**Boundary:** This establishes compiled wash-state input handling, **not** a verified edge connecting this particular blackboard updater to the compiled `4:61` status publisher, and not a live measurement or an automatic rewash decision. The static `4:61` identity and typed converter chain established in Stages 22–24 remain independently valid. The deployed Valetudo X40 fork is healthy and experimental writes remain off. Its `DreameMiotHelper.readProperty(4,61)` offers a source-level single-property `get_properties` mechanism but is not exposed by a confirmed user-facing read-only diagnostic endpoint. No CLI flags were invented and no live MIOT request was issued. Before runtime verification, first validate a trustworthy local transport with clear, separate opt-in. Physical wash/docking retest remains postponed. Preserve backup hashes and normal SmartHost safety behavior.

## Stage 26: opt-in single MIOT 4:61 read without an installed-fork change (2026-10-20)

To advance the remaining live-availability gate without deploying or modifying the healthy X40 fork, the assistant reviewed the public upstream `python-miio` local UDP API and the exact Valetudo source: `DreameMiotHelper.readProperties()` uses method `get_properties` with `did/siid/piid`; `DreameValetudoRobot` inherits local token `/data/config/miio/device.token` and model/DID `/data/config/miio/device.conf`. An **unexecuted, Mac-only diagnostic** was created as `x40-stage26-single-property-read.zip` (Python script + README/test notes).

**Safety contract:** Script requires `--confirm-one-read`, validates a numeric private IPv4 LAN address, uses SSH `cat` of **only those two fixed** existing files (read in memory, credentials not printed or persisted), verifies `model=dreame.vacuum.r2416`, and invokes `Device.send("get_properties", [{"did": deviceId, "siid":4, "piid":61}], retry_count=1)` exactly once at application level. `python-miio` handshake or retries may entail more than one UDP datagram. Any property response is summarized using schema/code allowlist; by default the raw property value is **discarded** and one small integer can only be recorded via explicit separate `--include-numeric-state`. File output is exclusive-create mode 0600 with no token, DID, configuration contents, raw vendor payload or raw errors. This is an active read, **not passive**, and underlying firmware read-handler effects cannot be absolutely excluded. No setting writes, action calls, device file modifications, experimental controls or robot software deployment are performed.

**Verification to date:** offline `--self-test` passed the fixed one-element command, credentials parsing, redaction and negative cases without networking, Python compilation passed, no-flag dry run did not connect, and ZIP integrity passed. **No live MIOT 4:61 read has been executed; support and numerical semantics remain UNKNOWN.** A successful read code zero would not establish a wash, native dirtiness, turbidity or rewash event; timeout/network failures cannot disprove compiled 4:61 capability. Operator remains responsible for any future choice to run the opt-in script locally and share only its sanitized JSON.

Detailed source-level observations and the package safety contract are documented on the unmerged `research/x40-cleangenius-passive-miot61` branch at [Stage20+ research evidence](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md). The deployed stable `master` executable, disabled experimental CleanGenius switch and official parent rollback files remain unchanged. Physical cleaning and docking test is still deferred.

## Stage 26 v2: pre-query ValueError and privacy-safe diagnostic fix (2026-10-20)

The operator ran Stage26 v1 on macOS with **python-miio 0.5.12** and confirmed `X40_STAGE26_SELFTEST_PASS`. The explicit live path prompted for **both** password-protected SSH reads, then exited with `X40_STAGE26_FAILED=ValueError (details redacted)`. Inspecting the **actual v1 source** shows that its `parse_conf(...)` and `Device(...)` constructor run **outside** the protected `dev.send` request/catch block. The exception occurred before the `fixed_query(...)` invocation; **no `get_properties(4,61)` command was issued** in this attempt. The console output alone cannot tell if parsing `device.conf` or MIIO client construction raised the error. No actual device configuration content is available in the failure log.

The v1 `did` regex `[1-9][0-9]{0,11}` was stricter than the actual Valetudo `MiioValetudoRobot.deviceId` getter, which uses `parseInt` on `did`. It may incorrectly reject larger positive decimal IDs or those starting with zero. This is a **plausible cause, not a confirmed diagnosis**. The existing token decode accepted the first SSH read because a second SSH password prompt appeared.

A corrected **Mac-only** source kit `x40-stage26-diagnostic-v2.zip` was created and validated offline. The included `x40_stage26_diagnostic_v2.py` supports `--preflight-only`: exactly two fixed, read-only SSH `cat` requests to the existing token/config paths, no UDP, and a sanitized 0600 JSON with explicit fixed `failure_stage`, `failure_category`, and `client_command_attempted=false`. It accepts leading-zero positive 64-bit decimal DIDs (within 20 ASCII digits), preserves exact `model=dreame.vacuum.r2416` matching, handles MIIO-client setup errors before attempting any command, never prints or stores token/DID/raw vendor exceptions, and defaults to **no-network**. Only `--confirm-one-read` initiates a library-level `get_properties` of the **sole allowlisted MIOT property 4:61**; the transport may handshake/retry. The default response redacts vendor values.

Offline synthetic no-network self-test, Python compilation, dry-run, strict 0600 exclusive-create report checks and ZIP integrity **all passed**. This revised kit has **not yet been run on the X40**. The operator should send only `x40-stage26-preflight-v2.json` from the preflight before deciding whether to retry the opt-in active MIOT read. The incident neither verifies nor disproves live MIOT 4:61 support, semantics or any CleanGenius wash/dirtiness decisions. No changes to installed fork, experimental policy, MIOT settings, AVA services or rollback backups.

## Stage 26 v3: model-family validator correction after preflight mismatch (2026-10-20)

The operator completed Stage26 v2 offline self-test and the **preflight-only** SSH check. The sanitized uploaded report `X40_STAGE26_DIAGNOSTIC_V2` shows `PREFLIGHT_FAILED_NO_MIOT_READ`, `failure_stage=CONFIG_VALIDATE`, `failure_category=CONFIG_MODEL_NOT_R2416`, and `client_command_attempted=false`. The two fixed SSH reads succeeded, so no MIOT command was sent. No user-provided raw model value or DID was exposed in the report.

**Root cause in source validation:** The Stage26 v2 diagnostic insisted on the exact `model=dreame.vacuum.r2416` string. The actual production `backend/lib/robots/dreame/DreameX40UltraValetudoRobot.js` implementation detection recognizes **five** model identifiers: `dreame.vacuum.r2416`, `dreame.vacuum.r2416a`, `dreame.vacuum.r2416c`, `dreame.vacuum.r2449a`, and `dreame.vacuum.r2449k`. Therefore v2 could reject a legitimate X40 variant. The raw device model was **not** captured; that exact mismatch remains an inference, not direct proof of which variant the user's X40 uses.

**Correction:** Standalone Mac-only `x40-stage26-diagnostic-v3.zip` now exactly recognizes the five model identifiers but stores only a coarse allowlisted family enum (`r2416_family` / `r2449_family`). Its preflight runs fixed read-only SSH `cat` commands for config/token and **no MIOT request**; it reports `PREFLIGHT_VALID_NO_MIOT_READ` for a permitted model and valid credentials. A future explicitly requested active MIOT 4:61 read remains limited to the three `r2416`-family variants because the underlying collected static native firmware evidence comes from R2416. For the two `r2449` variants the diagnostic refuses live reads **before fetching the token** with `MODEL_VARIANT_NEEDS_OWN_4_61_AUDIT`. Unknown models refuse even preflight. This intentionally avoids expanding compiled property claims across an unaudited firmware family.

Offline Python syntax check, fake credential and MIIO client self-test including all five model IDs, r2449 before-token guard, no-network default, and ZIP integrity all passed. The script was **not executed against the user's robot**. The prior `4:61` device-support result stays **unknown**. No production fork changes, AVA traffic, CleanGenius experimental firmware writes, map/dock commands, or rollback actions occurred. Next user action is the **v3 preflight only**, followed by separate opt-in for one read if the model family is confirmed eligible.

## Stage 26 v3: operator preflight passed for R2416 family (2026-10-20)

The operator supplied the sanitized `X40_STAGE26_DIAGNOSTIC_V3` report. **Conclusion `PREFLIGHT_VALID_NO_MIOT_READ`**; `model_family=r2416_family`, `x40_model_recognized=true`, `model_family_4_61_read_eligible=true`, `auth_preflight_passed=true`, `failure_stage=null`, `failure_category=null`, `client_command_attempted=false`, `live_property_supported=null`, and `firmware_writes_or_actions=false`. The output did not persist raw vendor values, credentials or DID. This resolves the prior v2's false-negative *model allowlist* failure and confirms SSH file access/format validation worked; it does **not** prove network MIIO authentication or availability of the actual live property.

The exact accepted X40 model remains intentionally undisclosed; only its R2416-family classification is retained. Because that family matches the compiled 4:61 property evidence in the user's archived firmware, the diagnostic's optional **single allowlisted, active, read-only** `--confirm-one-read` mode is now eligible for user execution. It will perform one application-level `get_properties` request for `(SIID 4, PIID 61)` via existing local MIIO transport with handshake/retry possible. It has **not** yet been executed in this stage. The default output redacts the raw numeric state; no state mapping, mop-dirtiness telemetry, turbidity or auto-rewash occurrence may be inferred without additional evidence.

No SSH writes, external MIOT request, AVA injection, cleaning cycle, parent rollback, runtime fork modification or experimental CleanGenius control change occurred during the preflight. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and the working fork.

## Stage 26: first successful live read of compiled MIOT 4:61 (2026-10-20)

The operator supplied **`x40-stage26-read-v3-retry.json`**, generated by the **Mac-side, allowlisted, single-property read** in `x40_stage26_diagnostic_v3.py` after correcting the local Python/venv issue. Its sanitized `X40_STAGE26_DIAGNOSTIC_V3` record confirms:

- `conclusion=LIVE_4_61_CODE_ZERO`; `mode=read`; `client_command_attempted=true`.
- `target_siid=4`, `target_piid=61`, `model_family=r2416_family`, `model_family_4_61_read_eligible=true`, `auth_preflight_passed=true`.
- A **valid matching MIOT response** with `firmware_code=0`, `response_shape_valid=true`, `value_type=integer`, `live_property_supported=true`.
- `firmware_writes_or_actions=false`, `credentials_or_did_persisted=false`, `raw_vendor_value_persisted=false`, `raw_vendor_payload_persisted=false`.
- `numeric_state_code=null`, `numeric_semantics_verified=false`. The null here is a **deliberate redaction / omitted capture** and does **not** mean the firmware property held a null or zero value.

**Significance:** The previously static-only Stage 22–24 conclusion is now independently verified **live** for this R2416-family robot: *authenticated local `get_properties(4,61)` returns an integer with code 0*. This is the first verified live reading of compiled `StationAutoWashState`; it is **not evidence of automatic rewash, mop dirtiness, turbidity reading, AI decision, or particular docking activity**. The report is a single time-point, and does not reveal numeric state or state transitions.

**Safe next observation (separate explicit operator action):** The already-installed v3 Mac collector supports `--confirm-one-read --include-numeric-state` for **one additional identical read**, optionally storing only a bounded signed 16-bit integer `numeric_state_code` (when the vendor returns one), with no raw response, DID or secrets. Use a **new filename** because reports are exclusive-create. Do not install an experimental fork, enumerate other MIOT properties, issue `set_properties`/action calls, or force a physical wash. Even the numeric integer needs independent firmware or observed-state corroboration before assigning status labels. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and parent/original rollback copies.

## Stage 27: verified live 4:61 zero and constructor-default zero initialization (2026-10-20)

The owner supplied sanitized `x40-stage26-numeric-state.json` from a second **single** authenticated, allowlisted, read-only `get_properties` for MIOT **SIID 4 / PIID 61**. Report `X40_STAGE26_DIAGNOSTIC_V3` has `model_family=r2416_family`, `auth_preflight_passed=true`, `client_command_attempted=true`, `firmware_code=0`, `code_zero=true`, `response_shape_valid=true`, `value_type=integer`, `numeric_state_code=0`, `allowlisted_numeric_state_persisted=true`, `numeric_semantics_verified=false`, and `firmware_writes_or_actions=false`. The number **0 is a real observed property value**, whereas the separate `firmware_code=0` means a successful protocol response. No token, DID or raw payload was captured.

An additional **offline** disassembly of the already collected R2416 `node_msg_cvt.so` independently establishes that the `MsgClean` constructor zero-initializes the object member containing this property:

- `MsgClean::MsgClean` copies its instance pointer to x20, then uses a zero-register 64-bit store at object offset **0x2d0**, covering bytes **0x2d0..0x2d7**.
- The 32-bit `StationAutoWashState` member resides at **0x2d4..0x2d7**. The getter passes exactly that member to the integer-to-JSON routine; the setter reads and writes it; the reporter loads it for formatting. Exact ELF function extents / full ARM64 instruction sequences were validated for all four functions.
- Therefore **zero is verified as an initial/default value when the handler instance is constructed**. The fact that the runtime property returned zero does **not** establish whether the live value remained unchanged since initialization or was changed/reset, and does **not** license interpreting numeric zero as *idle*, *wash disabled*, *no dirtiness*, *no rewash* or any other particular state.

A reproducible **Mac-side offline** verification kit is available as `x40-stage27-default-zero.zip` outside Git, with `stage27_default_zero_audit.py`, synthetic no-network tests, README, and a **sanitized** JSON audit `X40_STAGE27_DEFAULT_ZERO_OFFLINE_V1`. Python syntax, parser tests, private ZIP CRC, exact symbol-disassembly checks, matching member offset and ZIP integrity **passed**. No proprietary firmware, secrets, raw disassembly or camera/map data are included. No X40 network/robot commands were used for this *offline* step; the live integer is from the prior owner-triggered Stage26 read.

**Next evidence gate:** establish actual status-code semantics through independently corroborated natural-state transitions or further specific private offline control-flow analysis, without assuming zero means idle. A physical cleaning/wash retest remains deferred. Preserve the installed production fork, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, and original/official parent rollback backups. Do not change property `4:61`, inject AVA messages, or enable experimental SmartHost controls to force a transition.

## Stage 28: nine exact station-auto-wash blackboard string references in native R2416 (2026-10-20)

Continued analysis used **only the operator's previously provided, SHA-verified private R2416 firmware archive**; there was no robot access, SSH, MIOT query or firmware modification. A new **offline-only** Python3 audit parsed the actual `liblethe_tactics_tree.so` AArch64 ELF, verified the exact symbol `RobotWIFI_Deal::WIFIState_Send::updateStationAutoWashState()`, its 7836-byte function size, and all **1959 consecutive instructions**. It verified each key is uniquely present in the ELF `.rodata` segment and located exact within-function `ADRP` followed immediately by `ADD` references to the full corresponding address:

| Exact private blackboard key | Verified instruction references |
|---|---:|
| `station_auto_wash_stage` | 1 |
| `station_auto_wash_working` | 2 |
| `station_auto_wash_pause` | 3 |
| `station_auto_wash_out_time` | 1 |
| `station_auto_wash_happen_error` | 1 |
| `station_auto_wash_back_home` | 1 |

Direct named PLT calls in **that same compiled function**: `BT::Blackboard::get<WashStatus>` **1**, `get<ava_mop_station_msg>` **1**, `get<int>` **3**, `set<bool>` **6**, `set<int>` **1**, `set<int&>` **1**. These counts confirm **compiled internal wash-state blackboard inputs and updates**, beyond a mere binary string match. They are *not* proof of a direct producer-to-MIOT property `4:61` bridge, numeric enumeration, an actual wash, dirtiness or automatic rewash event.

The **separate validated live** `4:61=0` observation remains an unmapped integer. Stage 27 separately verified constructor initialization of that property to 0, not that the runtime value never changed. The Stage28 analyzer reports `COMPILED_WASH_BLACKBOARD_INPUT_OUTPUT_REFERENCES_VERIFIED`, explicitly `blackboard_state_compiled_to_live_miot_value_bridge_verified=false` and `live_miot_value_0_interpreted=false`. Self-test, Python compilation, real offline archive audit, and ZIP CRC **passed**. A privacy-filtered `x40-stage28-wash-blackboard.zip` package includes script, sanitized JSON and instructions **only**, with no raw binaries, full disassembly, private configs or credentials. Full research notes are in the unmerged [CleanGenius research branch](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md).

No installed executable, experimental write flag or rollback backups changed. The physical wash/dock retest remains deferred. Investigate the **actual typed AVA producer with station state context** or wait for independently observed natural state transitions before assigning labels or exposing the numeric property in production.

## Stage 29: native cross-library wash-state key and MCU-control publisher evidence (2026-10-20)

Continued research used **only the existing owner-uploaded, CRC/SHA-validated, 106-file private R2416 native archive**, without robot access or an additional MIOT command. A standalone **no-network** Python3 audit (packaged as `x40-stage29-native-bridge-audit.zip` with source, privacy-filtered JSON result and README, **no proprietary binaries**) examined the exact ARM64 ELF `.rodata` key materializations and named function extents:

- `node_lethe.so`: streamed 1,929,367 AArch64 instructions. **7** exact `ADRP`+`ADD` references to `station_auto_wash_working`; **1** to `station_auto_wash_happen_error`.
- `liblethe_tactics_tree.so`: independently checked the exact **7,836-byte** `RobotWIFI_Deal::WIFIState_Send::updateStationAutoWashState` function: **2** `station_auto_wash_working` and **1** `station_auto_wash_happen_error` references.
- Within `node_lethe.so`, the `station_auto_wash_working` references include `CheckRobotSelfClean`, `AvaNodeRoute::SendWashLogicOTA`, and other charger/standby/drain/gyro state paths. The `station_auto_wash_happen_error` reference belongs to `DeviceMsgFromAppDeal::ChangeDeviceMsg`. Each is a real in-function instruction-level key reference, not merely a binary string occurrence.
- `AvaNodeRoute::SendWashLogicOTA` has direct PLT call counts for `BT::Blackboard::get<WashStatus>` **1**, `get<int>` **1**, `set<int>` **3** and `AsyncDeque::MultAsyncPublish<_CtrlMcuCMD...>` **2**. This is a **compiled MCU-control publishing path**, not a verified typed `ava_msg_device_prop_int` producer.

**Critical boundary:** matching names in multiple compiled modules **do not** prove they share a particular runtime blackboard instance, and publishing `_CtrlMcuCMD` **does not** prove a producer-to-`MsgClean::SetStationAutoWashState` / live `4:61` data path. The already observed local read `4:61=0` still has **unverified numeric semantics**; constructor default 0 is separately verified. No automatic rewash, AI mop dirtiness, or actual turbidity event has been demonstrated. Sanitized report conclusion `NATIVE_WASH_KEY_CROSS_LIBRARY_XREFS_VERIFIED` deliberately marks `same_runtime_blackboard_object_proven=false`, `native_station_state_to_miot_4_61_producer_proven=false` and `numeric_miot_4_61_value_0_interpreted=false`.

Python compilation, synthetic parser guards, R2416 offline direct xref verification and output ZIP CRC all **passed**. The unmerged [CleanGenius research branch](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md) contains detailed non-proprietary evidence notes. Stable production Valetudo fork and original/parent rollback assets unchanged, CleanGenius experimental firmware writes disabled, and user's physical wash/dock retest deferred.

## Stage 30: exact native typed device-property blackboard call-site audit (2026-10-20)

Continuation used **only the previously uploaded private 106-file R2416 firmware archive**; no further robot connection, MIOT request, AVA injection, physical cleaning cycle or installed binary change. A standalone **no-network Python/LLVM** analyzer `stage30_typed_xrefs.py` counted direct **exact named PLT target** `b`/`bl` calls into the type-specific `BT::Blackboard::get<ava_msg_device_prop_int>` and `set<ava_msg_device_prop_int&>` routines. It refused nearest-symbol name suffixes and incomplete wash-updater instruction sequences.

**Verified AArch64 results:** full `node_lethe.so` scan covered **1,929,367** decoded instructions; **12 direct typed getter call sites**, **2 direct typed setter call sites**. Of ten counted getter owner-groups, **one getter site has no trustworthy named function extent** and remains unattributed (rather than being misclassified). Both named typed **set** calls reside in `AvaNodeRoute::ExtrStrAdd` and `AvaNodeRoute::CleanLogAndSetLastAppMap`; typed getter calls also occur in `SendRobotStatueToWIFI` (1), `SendRobotMapStateToWIFI` (1), `CleanAreaControlAndSend` (2), and other map/state processing. `AvaNodeRoute::SendWashLogicOTA` and `CheckRobotSelfClean` each have **zero such direct typed getter/setter calls**. The independently pinned `liblethe_tactics_tree.so` `WIFIState_Send::updateStationAutoWashState` contains **1,959 consecutive AArch64 instructions** and likewise has **zero** direct calls to those two type-specific blackboard functions. The generic typed `AsyncDeque::_ProcessAsyncPub<ava_msg_device_prop_int>` is present in the router library; no specific station-status publisher has yet been attributed.

**Meaning and limits:** These are **narrow direct call-site observations**, not a disproof of indirect/inlined message flow. Stage 24 independently established the typed **consumer** path `ava_msg_device_prop_int → SetPropIntMsg → MsgClean::SetStationAutoWashState`; the **producer feeding 4:61 remains unverified**. Stage 26 showed an actual live `4:61=0` MIOT integer; Stage 27 showed its constructor-default is zero; **neither gives numeric semantics**. No claimed observed auto-rewash, dirtiness or turbidity sensor measurement.

Package **`x40-stage30-typed-property-xrefs.zip`** holds only the offline Python3 analyzer, synthetic tests, README and sanitized `X40_STAGE30_TYPED_DEVICE_PROPERTY_CALLSITE_V1` JSON. Local `py_compile`, exact-target self-tests, real archive CRC/ELF scan, output ZIP CRC, and no-proprietary-binary checks **passed**. Full details are in the [unmerged CleanGenius research branch](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md). No firmware binaries or private configuration were checked in. Production Valetudo fork and original/parent rollbacks preserved; `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, physical wash/dock retest deferred.

## Stage 31: typed blackboard writer key-provenance audit (2026-10-20)

Continued **offline-only** analysis of the operator's previously preserved 106-file private R2416 native archive inspected the two precisely named **`BT::Blackboard::set<ava_msg_device_prop_int&>`** callers identified in Stage 30. The short standalone `x40-stage31-key-provenance.zip` contains Python3 ELF/disassembly audit code, negative self-tests, instructions and **sanitized** `X40_STAGE31_TYPED_WRITER_KEY_PROVENANCE_V1` JSON; no firmware binaries, raw disassembly, credential material, maps or camera files are packaged/committed.

**Verified** (real `node_lethe.so`, SHA-256 prefix `b34eb5c71bccd903`): The complete **29,824-byte** `AvaNodeRoute::CleanLogAndSetLastAppMap` function contains one direct exact typed-set PLT branch preceded closely by `ADRP` + `ADD` instruction setup for the verified `WIFI_Robot_State` `.rodata` string, plus temporary string-argument preparation. This is concrete **nearby key construction**, not an interprocedural whole-path guarantee that the setter always uses it. Its runtime payload values were not inspected.

**Unresolved**: The complete **64,180-byte** `AvaNodeRoute::ExtrStrAdd` function also contains one exact typed-set call, but its nearby `ADD #0x598` lacks proven source-register literal-page provenance; the base register has other writes along potentially reachable paths. A naive matching-offset heuristic would wrongly assert it uses `WIFI_Robot_State`; the Stage31 audit explicitly refuses that attribution. One Stage30 typed-getter site remains outside the named ELF function extent, not assigned to a nearest symbol.

Python syntax, synthetic exact-symbol/ADRP-source-clobber guards, full real-archive ELF function-instruction coverage, report format and output ZIP CRC **passed**. The sanitized report is `ONE_WIFI_ROBOT_STATE_KEY_SETUP_VERIFIED_OTHER_WRITER_UNRESOLVED`; `upstream_publisher_of_live_4_61_proven=false`, `same_runtime_blackboard_proven=false`, and `numeric_zero_status_meaning_verified=false`. The already observed `4:61=0` is not labelled idle, working, disabled, clean or rewash. No new robot connection, SSH/MIOT command, AVA injection, on-device modification or wash/dock cycle occurred. Preserve stable `master` fork, disabled experimental CleanGenius writes, original/parent rollback and user-deferred physical wash retest. Follow concrete typed payload construction/producer registration (not name/offset coincidence) for next offline work.

## Stage 32: exact internal typed selector 57 maps to compiled MIOT 4:61 setter (2026-10-20)

Additional **offline-only** static investigation used the owner's existing SHA/CRC-validated 106-file private R2416 firmware archive to map the **internal enum selector** used by the `ava_msg_device_prop_int` → `MsgClean::SetStationAutoWashState` path. It found a unique **`cmp w1, #0x39` / `b.eq`** dispatch that enters an exact local `SetPropIntMsg` block and then **tail-branches to the station-auto-wash setter PLT entry**. Thus **internal selector decimal 57 (hex 0x39)** maps to the station-auto-wash status setter. **Do not conflate selector 57 with MIOT PIID 61.** Stage 22 separately verified that the setter's report uses MIOT **SIID 4, PIID 61**; Stage 26 proved a real code-zero live GET `4:61=0`; Stage 27 verified constructor default 0 with **no status semantics**.

Additional exact binary facts: `AvaMsgCvtPropIntProcess` has **3** consecutive AArch64 instructions and an exact direct tail branch into `PropIntMsgProcess` (**189**); the latter contains **252-byte** `memcmp` / `memcpy` message-snapshot operations, an indexed-word selection path and a bulk-change scan calling `SetPropIntMsg` (**1062**) directly. Indexed selector 57 has observed byte offset **232** inside the typed input message layout. `MsgClean::SetStationAutoWashState` (**12**) uses the previously established stored status member `0x2d4` and queues a property-61 report on change. **All four ELF extents and 1,266 total instructions verified**, refusing missing LLVM headers, inexact branch targets or nearest-symbol guesses. This is direct converter-side evidence, **not** proof which concrete upstream function populates the indexed message, that the live status changes away from zero, or that dirtiness/turbidity/AI rewash decisions are visible.

A reproducible, **no-network** Stage32 package `x40-stage32-typed-selector.zip` (Python3 analyzer, synthetic negative tests, README, sanitized `X40_STAGE32_INTERNAL_SELECTOR_57_V1` JSON) passed Python syntax, self-test, real private archive audit and ZIP CRC checks. **No** firmware binaries, raw disassembly, proprietary configs, secrets, maps or camera content were included in the kit/Git. Research details are on [unmerged branch](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md). No robot commands, firmware writes, fork deployment or physical wash/docking retest were performed. Existing stable fork, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and parent/original rollbacks remain unchanged.

**Next gate:** producer-side exact-register and indexed-store analysis for **selector 57**, not another speculative enum/MIOT property probe. No named wash/rewash UI from integer 0 until independently validated.

## Stage 33: selector 57 producer triage and typed reader/output type distinction (2026-10-20)

Offline continuation reused the owner's **previously collected, SHA/CRC-validated private R2416 firmware archive**; no further SSH, MIOT requests, AVA messages, device settings, production fork executable or backup operations. Target remains identifying the **concrete native producer** of typed device-property integer selector **57** (Stage 32 consumer), later exposed by compiled and live-readable MIOT **4:61**.

A new standalone Mac/Linux `stage33_producer_triage.py` inspected the complete `node_lethe.so` AArch64 disassembly (**1,929,367 instructions**) and one exact **4,456-byte / 1,114-instruction** type-specific reader `AvaNodeRoute::SendRobotStatueToWIFI()`. **Verified direct calls:** **one** `BT::Blackboard::get<ava_msg_device_prop_int>`, **two** `AsyncDeque::MultAsyncPublish<ava_msg_device_status,...>`, and **no** direct typed `set<ava_msg_device_prop_int&>` calls. The output type of these two verified publisher calls is **`ava_msg_device_status`**, not `ava_msg_device_prop_int`. This shows a compiled reader-to-distinct-status-publication context, not the sought typed-property source. An indirect/inlined path remains possible.

An exact standalone immediate `#0x39` scan (explicitly excluding false prefixes such as `#0x390`) found instruction counts `cmp=8`, `mov=3`, `ror=3`, `ldrb=1`, `strb=1`; mere numeric coincidence is **not** a selector-57 producer. A restricted non-stack 32-bit store `str wN,[xBase,#0xe8]` found **five** call sites: three in mop-motor conversion, one in battery-state handling and one in compression. **None** has proved destination-buffer/type/register provenance to the 252-byte typed integer-message array or its index-57 word (byte offset **232**). No whole-program negative conclusion can follow because indexed, inlined, paired and copied stores are not captured by that instruction signature. The generic typed publisher template is compiled but its concrete station-status sender is **still unidentified**.

Result `X40_STAGE33_SELECTOR57_PRODUCER_TRIAGE_V1`: `TYPE_SPECIFIC_READER_AND_OFFSET_CANDIDATES_FOUND_PRODUCER_UNVERIFIED`; `actual_selector57_producer_identified=false`, `indirect_or_indexed_or_bulk_copy_producer_excluded=false`, `numeric_state_zero_semantics_verified=false`. Stage 32's exact converter mapping selector **57** → internal station setter → **4:61** remains valid; Stage 26 verified live `4:61=0`; Stage 27 independently verified the 0 constructor default. No status label or native dirtiness/rewash behavior should be inferred.

The companion **`x40-stage33-producer-triage.zip`** contains only the Python offline analyzer, self-tests, README and sanitized JSON result; no firmware, full disassembly, native runtime payload, map, credentials or camera content. Synthetic negative tests, Python syntax, pinned firmware hash/ELF/instruction-coverage checks, private input ZIP CRC and output ZIP integrity **passed**. Extended evidence is in [the unmerged Stage 33 CleanGenius research notes](https://github.com/angelcode1/Valetudo-plus/blob/research/x40-cleangenius-passive-miot61/docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md). No Valetudo binary changes or experiments on the X40. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, rollback assets and the physical wash/dock retest deferred.
