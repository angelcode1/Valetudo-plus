# X40 R2416 v227 — complete offline reproduction

**27 October 2026.** Read-only SHA-pinned analysis; v227 research branch descends from v226, not `master`. The robot, firmware, current Valetudo+, experimental flags and original PRIVATE owner evidence remain untouched. No proprietary original ELF or raw private archive published.

## Complete, freshly tested source-only archive

**`X40-R2416-v227-sanitized-analysis-kit.zip`**

- SHA-256: **`86cd852599e59a5406ed4cddf36122eb1e16d1d734759e9b654085334d145907`**
- Size: **280,507 bytes**. **133 ZIP entries** including `SHA256SUMS.txt`.
- **132/132 internal file hashes** verified on clean extraction; ZIP CRC integrity passed.
- **11/11 focused v227 tests passed** in the working source directory and **11/11 passed again from the fresh clean extraction**, including the complete original-owner PRIVATE **v197–v226 historical evidence replay**.
- Full native verifier pins **75 exact AArch64 instructions, six exact key-string ADRP+ADD constructions, seven direct typed getter/MCU publisher targets, 14 decoded guard branches** and four numeric station-state/sample values. Mutation tests reject altered original ELF SHA, station gates, time-parameter lookup and 25.0 multiplier.
- The independent bounded checker `x40_r2416_v227_repo_check.py` passed on the owner-original archive: **28 representative original instruction words, all six exact key pointers**, staging values **60/25/750/4499**.
- All scripts are Python 3 standard-library-only. Proprietary ELFs and private metadata are **never** packaged.

## Run on the owner's Mac

```sh
cd ~/Downloads
unzip X40-R2416-v227-sanitized-analysis-kit.zip
cd x40-r2416-v227-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V227_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V227_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V227_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V227_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V227_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V227_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V227_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V227_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v227.py
python3 x40_r2416_v227_repo_check.py --prior-zip "$X40_V227_PRIOR_ZIP"

python3 verify_x40_r2416_v227.py \
 --prior-zip "$X40_V227_PRIOR_ZIP" \
 --delta-zip "$X40_V227_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V227_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V227_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V227_SCOPE_SANITIZED" \
 --scope-private "$X40_V227_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V227_PROCESS_SANITIZED" \
 --process-private "$X40_V227_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v227-new-SANITIZED.json"
# X40_R2416_V227_STATION_STATE_THRESHOLD_STATIC_PASS 75 6 7 14 60 25 750 4499
```

The `--out` destination must be **new**, and generated output remains sanitized (no owner IP, PID, cwd, private paths, raw config, or original ELF bytes). The smaller checkout checker at `docs/research/x40-r2416-v227-tools/x40_r2416_v227_repo_check.py` needs only the original owner collector ZIP, but is **not** a replacement for the full v197–v227 history and 75/14 native checks.

## Interpretation boundary

`SendMopStainCheckCmd` has six compiled named-key bindings, typed station and sensor status lookups, integer comparisons `RobotMode=16`, `WashStatus=2`, `AvaSensorsMsg+0xfa=4`, and sampled-deque logic involving staged 60, multiplier 25.0, count 4499 and separate countdown reset 750. No time units, OEM enum meanings, numeric 32/33 MCU command semantics, actual station wash or AI-stain-triggered additional floor cleaning task have been verified. Local compiled publication paths can bypass a contemporaneous dirty-key lookup; earlier stored state may still matter.

**Next:** offline inspect original sensor/enum semantics and MCU consumer, separately retain the open stain-area→production new-floor-task dispatch question. Do not test experimental raw MCU commands on the robot.

Safety defaults: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`, `master` unchanged.

See [v227 report](x40-r2416-v227-station-sampling-guards-2026-10-27.md) and [v227 sanitized JSON](x40-r2416-v227-station-sampling-SANITIZED.json).
