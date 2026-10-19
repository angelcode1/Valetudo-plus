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
