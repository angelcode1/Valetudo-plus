# X40 R2416 — first native SmartHost 1 → 0 test (operator evidence, 2026-10-24)

## Installed firmware and build state

The operator reported the active Valetudo+ build as
`ref: refs/heads/research/x40-cleangenius-v74-dock-error-observer-20261023`.
After staging the temporary `VALETUDO_X40_NATIVE_SMARTHOST_TEST=1` launcher flag and manually rebooting, the read-only native preflight reported:

```text
writeGateOpen: True
canTestMode1: True
dockWashCode: 0
errorClear: True
baselineMatch: True
X40_NATIVE_TEST_PREFLIGHT_PASS
```

Earlier mode 6, task 0, charging 1, and the native settings baseline had been observed. These are operator-supplied results, not independently executed robot commands.

## Native MIOT 4:50 single-key write acceptance

The operator explicitly sent the v74 confirmed `target=1` request using the protected X40 test route, and supplied its returned allowlisted result:

```text
target: 1
observed: 1
changed: true
readbackVerified: true
SmartHost: 1
SmartAutoMop: -1
SmartAutoWash: 0
StainIdentify: 1
HotWash: 1
```

The operator immediately submitted the explicit `target=0` restore request; the response was:

```text
target: 0
observed: 0
changed: true
readbackVerified: true
SmartHost: 0
SmartAutoMop: -1
SmartAutoWash: 0
StainIdentify: 1
HotWash: 1
```

Therefore **native SmartHost=1 was accepted and read back, and SmartHost=0 was accepted and read back**, without intentionally changing the other four observed native settings. This validates the single-key settings transport and immediate readback. It does **not** prove retention over extended background polling, native dirt sensing, automatic reclean, or physical rewash.

## Deployment maintenance issue

The temporary launcher-gate management script was uploaded at
`/tmp/x40_v74_smart_host_temporary_gate.sh`. A manual reboot cleared `/tmp`, so initial `--check` and `--revert` calls returned `No such file or directory`. This was transient storage loss, not a failed settings rollback.

**Recovery and disarm subsequently verified by the operator:** after re-uploading the *same* script to `/tmp`, the guard returned:

```text
X40_V74_GATE_CHECK_PASS running_gate=1 launcher_staged=1 backup_exists=yes
NO_NATIVE_WRITES NO_RESTARTS
X40_V74_GATE_REVERTED_PASS active_process_unchanged=true
X40_V74_GATE_CHECK_PASS running_gate=1 launcher_staged=0 backup_exists=yes
NO_NATIVE_WRITES NO_RESTARTS
```

Following a separate manual `sync; reboot`, the operator executed the firmware-backed native preflight and supplied the following exact printed result:

```text
writeGateOpen: False
SmartHost: 0
baselineMatch: True
X40_SMARTHOST_TEST_SAFELY_DISARMED
```

**Disposition: final restoration and disarm PASS.** The launcher was restored, the restarted Valetudo process has a closed native writer gate according to preflight, and native `SmartHost=0` and the exact baseline were confirmed again. No further setting write, rollback or restart is necessary. Retain the v70/v73 recovery copies, original/parent backup binaries, launcher backup and configuration.

No evidence yet establishes retention of `SmartHost=1` during extended normal background polling, native dirt/stain triggers, automatic reclean, or a physical additional wash.

No original vendor binaries, device secrets, maps or raw native payloads have been committed.
