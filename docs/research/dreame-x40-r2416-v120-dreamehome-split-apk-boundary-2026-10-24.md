# Dreame X40 R2416 — v120 Dreamehome Android split-APK static boundary

**24 October 2026 · owner-supplied package, offline analysis only.** The prior APK upload was ignored. Only the replacement `com.dreame.smartlife.zip` was inspected; no device access, app execution or network login.

## Identified bundle

- Three APK members: `base.apk`, `config.arm64_v8a.apk`, `config.xhdpi.apk`.
- Android binary-manifest package: `com.dreame.smartlife`.
- App version: **2.6.6.3**; versionCode **102060603**.
- **3,927 APK entries** inspected across all splits, plus **391 nested mall-web-resource entries**.
- ARM64 split includes Flutter AOT `libapp.so` and the Flutter engine `libflutter.so`; app signing/distribution authenticity not verified.

## Verified generic status translations

The bundled `assets/flutter_assets/assets/home_device/common_device_protocol.json`, at `keyDefine["2.1"]["en"]`, maps:

| Code | Exact label |
|---|---|
| 8 | Mop Drying |
| 9 | Mop Washing |
| 10 | Returning to wash |
| 25 | The second cleaning underway |
| 37 | Heading to the extra cleaning area... |
| 38 | Extra Cleaning in Progress |

**These generic labels do not prove R2416 runtime support.** In particular the second/extra *cleaning* labels are not equivalent to a second *mop washing*.

## Android app shell / protocol hints

The Flutter AOT library contains printable markers `get_properties`, `set_properties`, `getCurrentAIModePiidByCurrentUserMode`, `updateDevicePlugin` and `DeviceInfoPlugin`. These are **string-presence evidence**, not verified call sites, message parameters, or R2416-specific SIID/PIID/AIID mappings. `set_properties` also appears in unrelated `libgpac.so`, so raw global counts must not be treated as robot-specific usage.

The app has a device-plugin workflow, but the bundle has no separately verified R2416-specific plugin. This makes an authorized model-specific downloaded plugin or sanitized device-capability payload a better next source than additional generic app-shell string scanning. A downloaded plugin's existence for this specific device has *not* yet been observed.

`washing_machine_smart_hosting` is a **laundry-appliance localization key**. It must not be conflated with the robot-native `smart_hosting_switch`.

## Exhaustive-by-entry, bounded-by-encoding negative census

An **ASCII case-insensitive literal-byte search** of the APK entries and nested mall files found zero instances of `r2416`, `r2343`, `cleangenius`, `clean_genius`, `rewash`, `turbidity`, `enable_turbidity`, `smart_auto_wash_switch`, `r2343_start_rewash`, or `WASH_CONTROL`.

This is not a proof of feature absence: native code, obfuscation, alternative encodings, computed strings, runtime-loaded modules and server-delivered plugin data remain outside literal discovery. The app bundle **does not close** the v119 firmware's remaining 20 possible model-group turbidity flag writers or prove any physical extra wash.

## Reproduce

The owner-delivered sanitized archive `X40-R2416-v120-dreamehome-split-apk-static-analysis.zip` includes a Python 3 standard-library-only scanner, sanitized aggregate JSON, detailed technical report, README and SHA256SUMS. It consumes the owner's `com.dreame.smartlife.zip` locally without modifying it:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v120_dreamehome_split_static_census.py --self-test
python3 x40_v120_dreamehome_split_static_census.py \
  ~/Downloads/com.dreame.smartlife.zip --out ~/Downloads/x40-v120-results.json
```

Verified output:

```text
X40_V120_SELFTEST_PASS string_pool_lengths=true input_shape=true no_device_io=true
X40_V120_SPLIT_BUNDLE_PASS app=com.dreame.smartlife version=2.6.6.3
X40_V120_BOUND_LITERAL_CENSUS_PASS entries=3927 terms=14
X40_V120_GENERIC_STATUS_TABLE_PASS keys=8,9,10,25,37,38
LIMIT: not an R2416 model-plugin audit or runtime evidence
```

**Privacy:** Do not commit APK files, original Flutter AOT libraries, embedded certificate/key assets, logs, credentials or account/device identifiers to this public fork. This commit contains only sanitized research, not the scanned APK or source app code. No robot changes, native firmware settings, guessed command invocation or runtime Valetudo implementation modifications have been performed.

**Working baseline preserved:** last operator-confirmed Valetudo+ v74, SmartHost=0, `writeGateOpen=false` and original recovery/launcher intact.
