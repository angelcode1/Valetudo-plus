# X40 R2416 v123 — offline reproduction

The operator's validated sanitized download `X40-R2416-v123-sanitized-delayed-regex-model-gate.zip` (SHA-256 `196f36d85ccd4852a5cb398933bf8dcba9fe475760a383259755a7eedb0287d4`) contains the **complete standalone v123 verifier and its v112–v122 Python modules**, detailed report, sanitized JSON, README and `SHA256SUMS.txt`.

Use only the owner's **private** ten-ELF `X40-R2416-v62-readonly-20261023T051829Z.zip` as input. In extracted `x40-v123-sanitized` run `shasum -a 256 -c SHA256SUMS.txt` followed by `python3 x40_r2416_v123_delayed_regex_cfg_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test`.

Validated: 10 original source SHA-256 pins, v122 regression, 9 additional typed regex-result chains, four eliminated direct SP+0xBC writer candidate sites (17 to 13), 44 independent source mutation rejections. **No vendor binaries, app APKs, original device configs/logs/maps or secrets are included.** This GitHub commit adds research documentation/aggregate metadata only and does not change the robot, `master`, executable Valetudo code or experimental safety gates.

Do not interpret possible CFG paths as evidence that native turbidity/automatic second physical washing works on R2416.
