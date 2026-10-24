# X40 R2416 v121 — reproducibility and privacy

The operator-side downloadable `X40-R2416-v121-dreamehome-plugin-boundary.zip` contains a complete standalone Python-standard-library verifier `x40_v121_plugin_boundary_verify.py`, detailed research report, sanitized findings JSON, README and SHA256SUMS.

Inputs: **only** the operator's original `com.dreame.smartlife.zip` (three pinned APK splits, version 2.6.6.3). Checks: all split SHA-256 pins, ZIP safety/CRC, AArch64 Flutter ELF identity, 15 bounded AOT code markers, 5 React Native executor bridge markers, and 20 source-string mutation rejections without a full-file-hash shortcut.

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v121_plugin_boundary_verify.py --self-test
python3 x40_v121_plugin_boundary_verify.py ~/Downloads/com.dreame.smartlife.zip --self-test --out ~/Downloads/x40-v121-results.json
```

**Do not commit or upload** the original APK split bundle, compiled Flutter ELF, embedded certificate/private-key assets, native RN bridge JavaScript, user/account databases, cookies, bearer tokens, household maps or robot identifiers. Only the sanitized summary is present in the public repository.

This commit adds documentation/aggregate data only. It modifies neither device, Valetudo runtime, working firmware gates nor the `master` branch. A device-specific downloaded plugin, live protocol mapping, and physical rewash remain unverified.
