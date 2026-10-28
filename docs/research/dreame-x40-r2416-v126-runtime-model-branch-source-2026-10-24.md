# Dreame X40 R2416 — v126 native runtime model source boundary

**24 October 2026 · offline static research on original SHA-256-pinned ARM64 firmware; sanitized only.** No robot connection or configuration change occurred.

## Why the v125 candidate stores cannot yet be treated as an executed one

The original `node_lethe.so` has **two independent runtime model-string reads** in `ProcessModelInfo()`, both through the original `ReadModleInfo()`:

| Original ELF VA | Verified compiled evidence |
|---|---|
| `0x46e8d8` | `ReadModleInfo()` calls native `std::basic_filebuf::open()` using path **`/var/run/runava.conf`** |
| `0x46fdc4` | `ReadModleInfo()` called with native **`MODEL`** key, return string managed at primary `x20` |
| `0x46fec0` | `ReadModleInfo()` called separately with **`DEV_MODEL`** key, result into the stack-backed string at `SP+0x240` |
| `0x478228` | Typed `std::string::compare` on the secondary string through **`x26`**, against `dreame.vacuum.r2416f` |
| `0x478238` | Secondary model compare against `dreame.vacuum.r2449b` |
| `0x47824c` | Secondary model compare against `dreame.vacuum.r2492x` |

The source-original literal bytes, return-slot/register transfer instructions and linked PLT call identities were independently checked.

The **primary** `MODEL` string is known to be the relevant exact `dreame.vacuum.r2416` comparison target in the earlier v119–v125 evidence; it is *not safe to substitute it for the separate `DEV_MODEL`*. The owner-private v62/v63 captures contain **no original `/var/run/runava.conf`**, so this secondary runtime value has not been observed.

In particular the original positive candidate sites `0x478160` and `0x47826c` are reached through model-group logic containing those secondary comparisons. **Their static inclusion in the bounded path graph is not an observation of their execution.**

v125 remains valid as a **bounded set of 13 potential last direct flag-store instructions**, one zero-sourced and twelve with locally positive sources. v126 does not claim those 13 have been further pruned, nor assign a live `enable_turbidity` value or prove a second physical mop wash.

## Safe next evidence input

The companion owner-delivered v126 ZIP has `x40_v126_model_key_readonly.py`, a root-SSH **read-only** probe that reads only `/var/run/runava.conf` and outputs **fixed classifications**, never its original content. It limits output to two named keys and categorizes only the exact model variants relevant to the firmware's known secondary comparisons. Unrecognized values are redacted, never echoed; other config keys, serials, credentials, maps, logs and firmware contents are excluded.

```sh
python3 x40_v126_model_key_readonly.py --self-test
python3 x40_v126_model_key_readonly.py --host root@192.168.8.149 --out ~/Downloads
```

The collector returns only a sanitized `X40-R2416-v126-model-class-evidence-*.zip`. **It has not been run on the robot.** A runtime model classification is only a further branch constraint, *not* a live execution trace, and it may still leave several possible stores.

The Python 3 standard-library-only offline verifier `x40_r2416_v126_runtime_model_source_verify.py` uses the owner's original private `X40-R2416-v62-readonly-20261023T051829Z.zip` and includes v112–v125 regression dependencies. Validated:

```text
X40_V126_TEN_ORIGINAL_ELF_SHA256_PINS_PASS count=10
X40_V126_V125_DUAL_POSITIVE_SOURCES_REGRESSION_PASS candidates=13
X40_V126_NATIVE_RUNTIME_MODEL_FILE_AND_TWO_KEY_READS_PASS
X40_V126_DISTINCT_PRIMARY_AND_SECONDARY_MODEL_COMPARISONS_PASS
X40_V126_INDEPENDENT_SOURCE_MUTATIONS_REJECTED count=29
LIMIT: DEV_MODEL runtime value absent; exact executed flag writer cannot yet be selected
```

The companion probe additionally passed local POSIX-shell parsing using synthetic secret-bearing config, five malformed protocol mutations and simulated SSH authentication failure refusal. No actual model value or other personal data was collected.

## Reproducibility, privacy and future proof

The separately provided, **sanitized** `X40-R2416-v126-sanitized-runtime-model-evidence-kit.zip` (SHA-256 `ff9bcfa139989805ba2bb5d008a4eae61e0659ecaac9c06a01a9471bb84adf9d`) contains both standalone scripts, all v112–v125 Python regression modules, complete report, sanitized results JSON, README and checksum manifest. It contains **no** vendor ELF, original runtime configuration, Android APK, serial, credentials, maps or native station-command values.

With the sanitized two-key result, use exact model classes to prune the remaining conditional paths. If competing stores remain because of other runtime-dependent conditions, only appropriately authorized, bounded runtime evidence—not more speculative static reachability—can identify which instruction **actually executed**.

**Preserved last-confirmed working device state:** Valetudo+ v74, SmartHost=0, experimental `writeGateOpen=false`, original launcher and all rollback files intact. No device actions, MIOT writes, runtime code changes or modification to GitHub `master` in v126.
