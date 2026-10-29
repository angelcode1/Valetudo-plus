# Bounded X40 native read-only probe

This is a separate diagnostic executable, not a second full Valetudo process. It tests the shared fresh settings/preflight helpers through a dedicated local MIIO client while the original Valetudo process remains running. It does not validate the new browser UI, writable selectors, SmartHost persistence, signed-disable behavior or automatic cleaning.

## Fixed scope

- Requires Linux ARM64 and explicit `--readonly-x40-probe`; requires device.conf model `dreame.vacuum.r2416`.
- Reads the local device ID and token on the robot only; neither is exported. Logger output is suppressed before transport use because the general codec can log secrets on errors.
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

## One owner-run read checkpoint

Keep the robot physically accessible, docked and free of active cleaning/washing. Run the delivered `RUN.py` once from the Mac. No main/advanced/signed CleanGenius flags need to be enabled, and no full Valetudo candidate is installed. The runner prints a small result ZIP to upload. Hardware is unverified until that result is inspected.

Success criterion: two allowlisted get_properties responses decode through the new helpers, the exact original PID/start time and file hashes remain confirmed, and staging cleanup succeeds. Mode 14 is expected to remain blocked; do not treat a successful diagnostic as activation permission. A local-read failure settles this standalone transport approach as blocked; it does not justify another collector loop, automatic process replacement, guessed write, or unplanned wake/cleaning action.
