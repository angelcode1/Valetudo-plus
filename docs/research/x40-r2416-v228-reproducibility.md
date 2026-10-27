# X40 R2416 v228 — complete source-only reproduction

**27 October 2026.** Research-only branch descended from v227. No robot access, MCU test commands, firmware write, running Valetudo+ modifications, enabled CleanGenius, or `master` changes. All original vendor ELFs and owner PRIVATE diagnostic/configuration archives remain outside this repo and the release.

## Verified offline ZIP

**`X40-R2416-v228-sanitized-analysis-kit.zip`** — SHA-256 **`f7de89e02ee788fdb5be67ce7d48395d74636e152a6208e54efba058bc33abb7`**, **292,943 bytes**. **139 ZIP entries including SHA256SUMS.txt**; fresh extraction passed ZIP CRC and **138/138 per-file SHA-256 checks**.

**11/11 v228 isolated original-native and mutation tests passed from the source directory and from the fresh extraction.** The standalone bounded checker independently passed 18 original native words, two `open_stain_identify` pointers, 47 `wash_status` references and 104 `RobotMode` references. The **additional full inherited v197–v227 private-evidence replay exceeded the execution window in the v228 run**, so **do not claim a completed v228 full-chain pass**. The historical v227 clean replay was verified separately in the preceding release.

The complete source-only kit includes all inherited v197–v228 Python 3 stdlib verifiers/tests and reports, `anchors_v228.py`, `verify_x40_r2416_v228.py`, `test_verify_x40_r2416_v228.py`, `x40_r2416_v228_repo_check.py`, 63 new original native-word anchors, six branch edges, four direct-call checks, two/47/104 exact native string-reference censuses, and the separate station-status selector check. No original proprietary ELF or owner PRIVATE ZIP/JSON is included.

## Run on macOS

```sh
cd ~/Downloads
unzip X40-R2416-v228-sanitized-analysis-kit.zip
cd x40-r2416-v228-sanitized
shasum -a 256 -c SHA256SUMS.txt

python3 x40_r2416_v228_repo_check.py \
 --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V228_REPO_SWITCH_SENSOR_PASS 18 2 47 104
```

To run the full 12-case suite, the owner needs the eight original PRIVATE/SANITIZED evidence files from v197–v227. Set these environment variables to the existing files (change the paths if needed):

```sh
export X40_V228_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V228_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V228_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V228_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V228_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V228_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V228_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V228_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v228.py
```

The complete verifier also accepts `--prior-zip`, `--delta-zip`, `--offline-resolver-zip`, `--live-resolver-zip`, `--scope-sanitized`, `--scope-private`, `--process-sanitized` and `--process-private`, and optional `--out` pointing to a **new** sanitized result filename. Existing output files are not overwritten. The independent repository-side checker lives at `docs/research/x40-r2416-v228-tools/x40_r2416_v228_repo_check.py` and only requires the original host collector ZIP; it does not replace the full verifier.

## Evidence limits and next step

The property callback compiles a typed Boolean writer for `open_stain_identify`, and the mop-stain checker has a typed Boolean getter. A successful get does not prove a true switch value. The `AvaSensorsMsg+0xfa == 4` branch resets a retained counter, **not** an MCU command, and the other `ava_mop_station_msg` decoder uses a distinct station message layout and `STATION_WASH_STATE_TYPE` selectors. The original evidence **does not resolve `RobotMode=16`, `WashStatus=2`, sensor value 4, actual station wash, or automatic AI-stain floor recleaning**.

Next read-only research should prioritize real OEM enum/field descriptions or signal producers; separately trace stain-area planning to a production new-floor-task dispatch rather than inferring it from dirty-mop keys.

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0` and `writeGateOpen=false`.

See [v228 native findings](x40-r2416-v228-stain-switch-sensor-boundary-2026-10-27.md) and [sanitized JSON](x40-r2416-v228-switch-sensor-SANITIZED.json).
