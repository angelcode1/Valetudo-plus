# X40 R2416 v120 — replaying the Dreamehome 2.6.6.3 APK census

The **sanitized** companion ZIP `X40-R2416-v120-dreamehome-split-apk-static-analysis.zip` contains the standalone Python standard-library scanner, the full technical report, aggregate results JSON and SHA256SUMS. It requires the owner-held `com.dreame.smartlife.zip` with exactly three splits and never exports extracted binaries or embedded certificates.

Execute:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v120_dreamehome_split_static_census.py --self-test
python3 x40_v120_dreamehome_split_static_census.py ~/Downloads/com.dreame.smartlife.zip --out ~/Downloads/x40-v120-results.json
```

Checks performed: split structure, APK binary manifest identity/version, inner CRC, generic status table, 14 bounded ASCII case-insensitive literal searches over 3,927 APK entries and 391 nested mall entries. **No model-specific UI/plugin, SIID/PIID mapping, live device observation or native rewash behaviour is asserted.**

Only documentation and aggregate JSON are committed. The private APK package, app executable code, native binaries, keys and credentials are never published. No robot I/O or settings change.
