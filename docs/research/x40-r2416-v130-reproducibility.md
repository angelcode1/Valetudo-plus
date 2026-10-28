# X40 R2416 v130 — reproducibility

Owner-side downloadable `X40-R2416-v130-sanitized-missing-dev-model-fallback.zip` (SHA-256 `00b9100d7fc49346bb8009c1b07c5305d96fdfd0d348c797d061307b0e9ca236`).

Contains the **complete** Python-standard-library v130 verifier, v112–v129 sanitized regression modules, full report, aggregate JSON, README and `SHA256SUMS.txt`. The original firmware archive and the owner-provided v128 model-site evidence are required *locally*, not bundled or committed.

```sh
unzip ~/Downloads/X40-R2416-v130-sanitized-missing-dev-model-fallback.zip -d ~/Downloads
cd ~/Downloads/x40-v130-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v130_missing_dev_model_cfg_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Expected: 10/10 original ELF SHA-256 pins; source-pinned missing `DEV_MODEL` normal empty-string fallback; three secondary equality branch decisions; 13 candidate direct flag stores, not an executed store; **32** independent native source/corridor mutations and **5** evidence mutations rejected.

No proprietary ELF, Android APK, model literal, raw robot configuration, serial, maps, tokens, logs or hardware command parameters committed. No robot or GitHub `master` change.
