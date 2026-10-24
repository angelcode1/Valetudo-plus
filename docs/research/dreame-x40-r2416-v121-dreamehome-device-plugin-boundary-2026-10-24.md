# Dreame X40 R2416 — v121 downloaded-device-plugin infrastructure

**24 October 2026 · static offline inspection of only the owner's `com.dreame.smartlife.zip`, version 2.6.6.3.** No device I/O, app execution, cloud/API request, account login, firmware change, or private source redistribution.

## Finding

v120 established a three-split `com.dreame.smartlife` Android app package but found no exact ASCII R2416/CleanGenius/rewash literals in the complete APK-entry census. v121 pins all three source APK SHA-256 checksums, validates the ARM64 original Flutter AOT `libapp.so` (21,431,216 bytes, SHA-256 `a7364e7b1bcf27971b3e510115adf63d1a5a43892f6cbba3da571b1d175b4f6e`), and distinguishes **two plugin frameworks**.

### Flutter web/device-plugin infrastructure

A bounded exact printable marker census of `libapp.so` confirms:

| Marker | Count |
|---|---:|
| `Package.getPluginVersions` | 3 |
| `PackageBridgeMixin: Package.getPluginVersions called` | 1 |
| `H5PluginVersionModel` | 14 |
| `androidPluginUrl` | 2 |
| `ohosPluginUrl` | 2 |
| `downloadPlugin` | 3 |
| `WebPluginPage: loading Android local resource ` | 1 |
| `WebPluginPage: load resource url=` | 1 |
| `_currentPluginBaseUrl` | 1 |
| `WebPluginDreameBridgeMixin` | 31 |
| `DeviceBridgeMixin` | 26 |
| `updateDevicePlugin` | 1 |
| `DeviceInfoPlugin` | 1 |
| `get_properties` / `set_properties` | 1 / 1 |

These strings establish the **presence of web-plugin version fields, a version-query bridge, download-related code, local WebPluginPage loader, and device-property bridge infrastructure** in the compiled app. Co-occurrence **does not** prove direct control flow among these functions, prove an actual download, disclose an endpoint URL, or confirm the particular plugin/model on R2416.

### Separate generic React Native executor

Exactly two files occur under `base.apk/assets/plugin/`: `RNExecutorBase.jx` (7,390 bytes) and `RNExecutorTest.jx` (44 bytes). The base file has the generic `__fbBatchedBridge`, `__fbGenNativeModule`, `nativeFlushQueueImmediate`, `nativeModuleProxy` and `Native.JSCallee.receiveResult` glue. It contains no identifiable R2416 feature module in **that directory**. This does not rule out other bundled app resources, native AOT code or downloaded model-specific plugins.

Exact case-insensitive ASCII names `r2416`, `r2343`, `cleangenius`, `rewash`, `enable_turbidity` and `WASH_CONTROL` were absent in the Flutter AOT ELF. This is literal scope only, not proof of feature absence.

## Best next evidence

Seek an *operator-authorized, model-specific downloaded UI/plugin* **if one actually exists on the Dreamehome device using the X40**, plus non-sensitive plugin version/capability metadata. That may reveal device-specific property IDs and feature gates. **No R2416 plugin, actual plugin URL, download, app session or R2416 property mapping was obtained in v121.** App-private cache may not be readable by ordinary ADB without root or app-supported export; do not guess availability. Do not capture/export credentials, cookies, authorization headers, embedded client keys, household maps, account databases, device IDs or raw private traffic.

The robot-native `ProcessModelInfo()` turbidity eligibility research is **separate**: v119 still has 20 potential direct writes to `SP+0xBC` after exact-name pruning, with regex/group predicates unverified. App UI infrastructure cannot prove a genuine dirt-triggered **second physical mop wash**.

## Reproducible verification

The *separately delivered* sanitized ZIP `X40-R2416-v121-dreamehome-plugin-boundary.zip` contains the standalone standard-library script `x40_v121_plugin_boundary_verify.py`, full report, sanitized results JSON, checksums and README. Requires the owner-held `com.dreame.smartlife.zip`; neither original APK nor native ELF/JS, certificates, private keys or credential material is included in the published repo or ZIP.

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v121_plugin_boundary_verify.py --self-test
python3 x40_v121_plugin_boundary_verify.py \
  ~/Downloads/com.dreame.smartlife.zip --self-test \
  --out ~/Downloads/x40-v121-results.json
```

Verified:

```text
X40_V121_SELFTEST_PASS modified_marker_cases=20 source_pin_mutations=1 no_device_io=true
X40_V121_ORIGINAL_APP_MARKER_MUTATIONS_REJECTED count=20 no_hash_shortcut=true
X40_V121_SOURCE_SPLITS_PINNED_PASS count=3
X40_V121_FLUTTER_PLUGIN_VERSION_AND_LOCAL_H5_LOADER_PASS markers=15
X40_V121_GENERIC_RN_EXECUTOR_ONLY_PASS files=2 bridge_markers=5
X40_V121_NO_R2416_PLUGIN_IN_BUNDLED_BOOTSTRAP_PASS scoped=assets/plugin
LIMIT: no fetched plugin, actual R2416 URL, live cloud session or physical rewash verified
```

**No runtime change:** last operator-confirmed working Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher/rollback assets intact. The robot, GitHub `master`, executable Valetudo code and existing research files were not modified.
