# v149 short-path recovery — no stale filenames or archived v127/v128 required

1. Obtain the recovered *private* original v62 firmware ZIP from the user conversation and save it to `~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip`. Verify SHA-256 `f996955745d07786d6290fd7afad4970f4d2cd182a493d61d329230c8038e6f6`.
2. Download the sanitized `X40-R2416-v149-one-pass-model-evidence-recovery.zip` (SHA-256 `6fbed310690fbcc81a6aee91275a7e84b493bf0c73af1648eb142a7a121851e7`).
3. On Mac:

```sh
cd ~/Downloads
unzip X40-R2416-v149-one-pass-model-evidence-recovery.zip
cd x40-v149-sanitized
shasum -a 256 -c SHA256SUMS.txt
sh run-v149.sh root@YOUR_ROBOT_IP
```

This initiates exactly one **read-only**, operator-authorized SSH query and validates the original firmware's 10 ELF SHA pins and 235-name compiled comparison map. It creates both `X40-R2416-v127-json-model-evidence-<UTC>.zip` and `X40-R2416-v128-model-compare-site-<UTC>.zip`. No prior v127 capture is necessary; both reports come from the same device read. The wrapper and all underlying Python modules are included in the kit; it does not contain vendor source bytes. If source/model identity checks fail, it refuses without accepting guessed data.

**Tests run by assistant:** original v62 verification; v127/v128/v148 synthetic fixtures; original-source lookup integrity; a synthetic single-SSH read with freshly generated and validated paired sanitized ZIPs; separate clean-extraction wrapper replay; archive integrity and SHA checks. No real SSH, cloud request, robot write or physical wash.

The heavy optional `--run-v148` flag is disabled in `run-v149.sh`: v148 four-edge model-check dry run exceeded the test timeout. Upload the newly generated sanitized v128 ZIP to continue the necessary-edge analysis separately. Static CFG reachability remains distinct from observed instruction execution. Do not publish the original firmware ZIP or raw robot data.
