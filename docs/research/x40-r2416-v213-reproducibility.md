# X40 R2416 v213 — complete reproducibility and privacy boundary

**27 October 2026.** The new research branch descends from v212. The robot and `master` are unchanged. The ZIP is source-only and does not contain original proprietary native binaries or the user's PRIVATE firmware archives, process reports, paths, credentials, maps, videos or configuration.

## Downloadable full offline source kit

**`X40-R2416-v213-sanitized-analysis-kit.zip`**

SHA-256: **`d1ca959ae0ba9be3d0ae2634b5b119a5fa9952ff8b55394463106290bf1d5e06`**

Includes **59 files**, including the checksum manifest. Clean extraction passed ZIP CRC, **all 58 internal SHA-256 checksums**, and **all 9 focused v213 tests**, including the complete v197–v212 original-native regressions and user-provided diagnostic evidence. Exact tests cover all 199 direct plugin register calls, 199 individual registered names, 199 `R_AARCH64_GLOB_DAT` callback relocation matches, the `R_AARCH64_JUMP_SLOT` import, 199 matching exported `build<Name>` symbols, altered ELF, altered BL/ADRP, incorrect callback symbol index, missing defined builder, bad expected site count, redaction and create-only output.

```sh
unzip X40-R2416-v213-sanitized-analysis-kit.zip
cd x40-r2416-v213-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V213_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V213_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V213_OFFLINE_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V213_LIVE_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V213_SCOPE_SAN="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V213_SCOPE_PRI="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V213_PROCESS_SAN="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V213_PROCESS_PRI="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v213.py

python3 verify_x40_r2416_v213.py \
  --prior-zip "$X40_V213_PRIOR_ZIP" \
  --delta-zip "$X40_V213_DELTA_ZIP" \
  --offline-resolver-zip "$X40_V213_OFFLINE_ZIP" \
  --live-resolver-zip "$X40_V213_LIVE_ZIP" \
  --scope-sanitized "$X40_V213_SCOPE_SAN" \
  --scope-private "$X40_V213_SCOPE_PRI" \
  --process-sanitized "$X40_V213_PROCESS_SAN" \
  --process-private "$X40_V213_PROCESS_PRI" \
  --out "$HOME/Downloads/X40-R2416-v213-new-SANITIZED.json"
# X40_R2416_V213_REGISTER_NAME_CALLBACK_STATIC_PASS 199 199 0
```

The output path must be **new**; existing files are never overwritten.

## Smaller repository-side bounded checker

`docs/research/x40-r2416-v213-tools/x40_r2416_v213_repo_check.py` has no external dependencies and verifies **199 direct registered NAME strings** versus **199 exported `build<Name>` functions**. Use the ZIP's full verifier when actual GOT callback pairing or historical regressions are required.

```sh
python3 docs/research/x40-r2416-v213-tools/x40_r2416_v213_repo_check.py \
  --prior-zip "$X40_V213_PRIOR_ZIP"
# X40_R2416_V213_REPO_DIRECT_REGISTERED_NAMES_PASS 199 199
```

The bounded name-only methodology was independently checked on the original collector archive locally; the complete ZIP's callback verifier and mutation tests received the full clean-extraction replay.

## Evidence limits and next step

Direct registered native names in the original **single** tree plugin are exhaustively covered within its known `BT_RegisterNodesFromPlugin` body. There is **no direct `AiStainMop` registered builder** there. Dynamic aliases, other plugins, effective runtime factory-map contents and file fallback remain unverified. Absence of four relative files in the one observed native process cwd is not evidence the fallback was invoked or failed. No autonomous extra floor-cleaning or dock-rewash event has been proven.

No robot collection is needed to reproduce v213; preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `writeGateOpen=false`.

See [v213 report](x40-r2416-v213-builder-registration-2026-10-27.md) and [v213 sanitized machine result](x40-r2416-v213-builder-registration-SANITIZED.json).
