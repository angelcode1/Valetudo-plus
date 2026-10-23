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
`/tmp/x40_v74_smart_host_temporary_gate.sh`. A manual reboot cleared `/tmp`, so follow-up `--check` and `--revert` commands returned `No such file or directory`. This is not evidence of launcher backup loss; the script's backup path is `/data/_root_postboot.sh.pre-smart-host-test-20261024`. The running Valetudo gate was observed as enabled before the first POST. **The operator has not yet provided evidence of launcher disarm and subsequent boot with writeGateOpen=false.**

Recovery plan: re-upload the identical guarded shell script into /tmp; run `--check`, `--revert`, check staged=false, then separately reboot and verify the process's `VALETUDO_X40_NATIVE_SMARTHOST_TEST` is no longer 1, preflight `writeGateOpen=false`, and fresh `SmartHost=0`. Do not repeat a native write. Keep pre-existing v70/v73 rollback copies, original/parent backups and configs protected.

No original vendor binaries, device secrets, maps or raw native payloads have been committed.
