# X40 R2416 v229 — complete offline replay and proof limits

**27 October 2026.** Research branch descended from v228; no robot connection, firmware or active Valetudo+ modification, feature activation, `master` update or publication of original proprietary ELFs and PRIVATE diagnostics.

## Source-only release (clean-tested)

**`X40-R2416-v229-sanitized-analysis-kit.zip`**

SHA-256: **`7e92b878e66a32e41b806c59aa77d7b7987db37b9392d7c8c075ae71d52c18be`**  
Size **306,427 bytes**; **145 entries** including `SHA256SUMS.txt`; all **144/144 file hashes** and ZIP CRC verified from fresh extraction.

**14/14 v229 tests passed in the original source directory and independently 14/14 passed in a fresh extraction**, including the **full v197–v228 original-native PRIVATE evidence replay**. The original `node_lethe.so` is checked by full SHA-256. New verifier: **66 exact AArch64 words, nine decoded direct calls, nine decoded guard branches, two original GLOB_DAT member-callback relocations**, bounded host direct caller censuses, three direct `LDRB [Xn,#0xfa]` sites, explicit 264-byte copy and retained previous-value state update. Mutation tests deliberately insert unanchored extra subscriber calls and `LDRB` sites and mutate the callback relocation, copy size or retain store; all are rejected.

All scripts use **Python 3 standard library** and take the owner's external original collector files as inputs. The ZIP does **not** contain proprietary original ELFs or PRIVATE ZIPs.

## Replay on the owner's Mac

```sh
cd ~/Downloads
unzip X40-R2416-v229-sanitized-analysis-kit.zip
cd x40-r2416-v229-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V229_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V229_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V229_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V229_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V229_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V229_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V229_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V229_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 x40_r2416_v229_repo_check.py --prior-zip "$X40_V229_PRIOR_ZIP"
python3 -m unittest -v test_verify_x40_r2416_v229.py

python3 verify_x40_r2416_v229.py \
 --prior-zip "$X40_V229_PRIOR_ZIP" --delta-zip "$X40_V229_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V229_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V229_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V229_SCOPE_SANITIZED" \
 --scope-private "$X40_V229_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V229_PROCESS_SANITIZED" \
 --process-private "$X40_V229_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v229-new-SANITIZED.json"
# X40_R2416_V229_SENSOR_RECEIPT_RETAINED_BYTE_STATIC_PASS 66 9 9 2 3 1 1
```

The output path must not already exist. Only sanitized JSON is emitted; test checks exclude IP, PID, working directory and PRIVATE input path strings. No network or robot runtime interaction.

## Smaller independent GitHub checker

`docs/research/x40-r2416-v229-tools/x40_r2416_v229_repo_check.py` requires **only the original owner-private collector ZIP**. It checks the original whole-ELF digest, **24 representative original instructions**, the two member-function GOT callback relocations, direct sensor/battery subscriber singletons and the **three exact offset-250 byte loads**. The equivalent complete package-local standalone checker independently passed:

```sh
python3 docs/research/x40-r2416-v229-tools/x40_r2416_v229_repo_check.py \
 --prior-zip "$X40_V229_PRIOR_ZIP"
# X40_R2416_V229_REPO_TYPED_SENSOR_PATH_PASS 24 2 3 264 250
```

Use the full release for 66/9/9 native and the historical chain.

## Exact proof limit

The original host registers a typed `AvaSensorsMsg` subscriber, copies **264 bytes** into a separately allocated object, and has a separately compiled mop-stain checker that reads byte **`+0xfa=250`**, compares it to value 4 and against a retained previous value, and stores an updated previous value. Callback registration **does not prove actual live message reception** or identity with the pointer retrieved later from a Blackboard. The original field label, physical sensor, `WashStatus=2`, `RobotMode=16`, MCU numeric 32/33 meaning, stain-triggered extra floor cleaning and station dock rewash **remain unverified**.

**Next offline research:** examine the typed incoming message publisher/source and any local OEM struct/enum definitions; separately continue the causal stain→new production cleaning task investigation. Do not issue test MCU commands.

Maintain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Keep `master` unchanged.

See [v229 findings](x40-r2416-v229-typed-sensor-retained-state-2026-10-27.md) and [sanitized evidence JSON](x40-r2416-v229-typed-sensor-SANITIZED.json).
