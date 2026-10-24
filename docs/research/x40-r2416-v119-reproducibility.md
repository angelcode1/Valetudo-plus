# X40 R2416 v119 — reproducing the sanitized model-pruned CFG

The owner-downloadable `X40-R2416-v119-sanitized-model-pruned-cfg.zip` contains the **complete Python 3 standard-library verification suite**, including `x40_r2416_v119_model_pruned_cfg_verify.py` and v112–v118 regression modules, its detailed report, sanitized JSON, README, and SHA256SUMS.

The verifier requires a separately held private `X40-R2416-v62-readonly-20261023T051829Z.zip` with ten SHA-256-pinned original AArch64 ELFs; **never publish that archive or original binaries**.

After unzipping, run `shasum -a 256 -c SHA256SUMS.txt`, then `python3 x40_r2416_v119_model_pruned_cfg_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test`. The verified source checks include 294 strict exact-name patterns, 61 direct flag writers, pruning to 20 candidates and 36 source mutation rejections.

This commit alters **documentation and sanitized JSON only**. It does not change the device, Valetudo runtime, `master`, firmware binaries or the existing v74 rollback configuration.
