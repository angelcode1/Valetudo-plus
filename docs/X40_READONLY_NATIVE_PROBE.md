# Bounded X40 native read-only probe

This is a separate diagnostic executable, not a second full Valetudo process. It tests the shared fresh settings/preflight helpers through a dedicated local MIIO client while the original Valetudo process remains running. It does not validate the new browser UI, writable selectors, SmartHost persistence, signed-disable behavior or automatic cleaning.

## Fixed scope

- Requires Linux ARM64 and explicit `--readonly-x40-probe`; accepts only the R2416 device.conf models `dreame.vacuum.r2416`, `dreame.vacuum.r2416a` and `dreame.vacuum.r2416c` already recognised by the X40 implementation. Other X40-family identifiers remain outside this probe's scope.
- Reads the local device ID and token on the robot only; neither is exported. Logger output is suppressed before transport use because the general codec can log secrets on errors.
- Identity loading accepts LF/CRLF config lines and optional horizontal whitespace around the separator, rejects duplicate model/device-ID fields, and requires a decimal device ID within the existing MIIO range. Tokens must be exactly 16 binary bytes or 32 ASCII hex characters, with at most one optional LF/CRLF terminator. Arbitrary suffixes are rejected. Binary token bytes are preserved without a UTF-8 conversion. There is no fallback to a running Valetudo config or alternate credential path.
- Identity failures report only fixed codes: `identity_config_unavailable`, `identity_model_invalid`, `identity_device_id_invalid`, `identity_token_unavailable` or `identity_token_invalid`. Paths, field values, credential bytes and underlying filesystem errors are not included. All identity failures occur before a socket opens.
- Binds an ephemeral UDP port on 127.0.0.1 and connects only to local firmware port 54321. It does not bind Valetudo HTTP, cloud or map-upload ports.
- Sends one local handshake, then exactly one get_properties of mode/task/charging/error/dock, then one get_properties of 4:50 settings. The adapter rejects extra fields, unexpected properties, wrong ordering, extra requests and retries. It exposes no write/action method.
- Has a 20-second process deadline and 3-second per-request timeouts. Failure has a fixed non-sensitive envelope. It never switches to cloud transport or falls back to another command after failure.
- Uses the existing shared allowlisted parsers; output retains SmartAutoMop=-1 as unknown. A Powersave reading produces a blocked preflight but can still be a successful read-only observation. Prerequisite observations do not authorize a setting write.
- No HTTP server, scheduler, updater, map polling, normal state parser, process switch, reboot, boot edit, configuration edit or native setting write is performed.

The existing firmware and original Valetudo process continue their independent normal activity. No claim is made that all activity on the robot is read-only, or that a read has no effect on device power state. The precise claim is that this probe requests no native setting writes or actions.

## Host runner

The kit's `RUN.py` is tracked under `scripts/x40-readonly-probe/RUN.py`. It verifies the probe executable against the kit manifest, confirms the known original binary hash and records the original PID/start time plus binary/config/postboot hashes. It creates a unique private `/tmp/x40-ro-*` directory, streams the probe via SSH, verifies the remote hash, runs it once, removes only that temporary executable/directory, and compares original process/file identities afterwards. It never exports the configuration or token contents.

A local `probe-attempted.json` receipt prevents accidental repeat hardware execution from the same kit. A failed observation remains a bounded blocked result; send the result for review rather than deleting the receipt and retrying. If a connection is interrupted, the probe's own deadline remains its termination mechanism. The host does not kill or restart any robot process.

Before/after hash or process changes produce a blocked result. An independently changed original process is not silently attributed to the probe and does not trigger automatic restore/reboot. Temporary-file cleanup failures are reported with the exact staging path.

## Build and offline checks

```bash
npm ci
npm run generate_code --workspace=backend
npm run ts-check --workspace=backend
npm run lint --workspace=backend
npm test --workspace=backend
npm run build_x40_readonly_probe --workspace=backend
python3 scripts/x40-readonly-probe/test_runner.py
```

The build produces `build/x40-readonly-probe`. The package is compiled separately from the full Valetudo candidate. Its tests include actual encrypted loopback packet exchange against a fake firmware peer with fake on-device credentials, as well as scope/budget/error checks. This supplies no real hardware acceptance result.

The identity correction passed all 164 backend tests under Node 22.17.1, backend type checking and lint (six existing warnings), and standalone ARM64 packaging. These are offline results. They do not establish which identity check failed on the owner's device, that the corrected executable runs there, or that any CleanGenius write is accepted.

The owner's subsequent macOS test run passed 162 tests and failed the two CLI fixtures with `linux_arm64_required`: those fixtures mocked ARM64 but inherited the Mac's OS. Both now simulate Linux **and** ARM64 inside their isolated child processes. A separate refusal regression covers macOS/ARM64 and Linux/x64; the production platform guard is unchanged. This corrects host-test portability, not the earlier robot identity failure.

After the fixture fix, all 165 backend tests pass under Node 22.17.1. All nine probe tests also pass with a `NODE_OPTIONS` preload making both the test host and its spawned Node children initially report `process.platform=darwin`, so the isolated firmware fixtures must explicitly override it. This is a platform-value simulation on Linux, not a claim of an actual macOS run. Backend lint passes with the same six existing warnings. Runtime source and the packaged probe executable are unchanged by this fixture correction.

## Completed owner-run read checkpoint — 2026-10-30

The owner supplied `x40-readonly-result-3gjfr1_u.zip` from the delivered probe with executable SHA-256 `0cc7faad74367e9d4f1f28f3a1c443542ad5982c8de5407b2ffb89b718352524`. Its result was **blocked during identity loading**, with `local_read_unavailable`, `phase=identity`, zero property requests and zero native writes. No handshake was reached, so this result does not test or reject the firmware transport, preflight parser, settings parser or CleanGenius itself.

The runner confirmed original PID/start time and binary/config/postboot hashes unchanged, no SSH errors, and successful temporary-file removal. No restore or rerun is required. This is a completed checkpoint, not an instruction to run the kit again.

The original probe grouped all identity failures into one error. Source inspection found narrower R2416 model handling and token-terminator handling than intended. Neither issue is a confirmed root cause of this device result: the report contains no model, device ID, token representation or filesystem failure detail. The offline correction adds strict regional-model/token parsing and fixed failure codes, tested with synthetic credentials. A fake encrypted peer also exercises the real CLI using an R2416a identity, CRLF config and newline-terminated token. Separate real-CLI failure fixtures verify each identity code, zero property requests and refusal before socket creation.

**Go/no-go:** code-only correction and tests; hardware acceptance remains **PARKED**. No replacement owner-run kit or additional hardware trial is authorised by this correction. Keep the original process running and the existing attempted-run receipt. Do not infer activation permission, relax mode 14 or unknown-value guards, switch Valetudo processes, guess a write or launch another collector loop from this result. Any future hardware decision must have a distinct bounded acceptance criterion and explicit owner authorisation.
