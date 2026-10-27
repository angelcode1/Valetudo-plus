# X40 R2416 v230 — complete source-only verification and evidence boundary

**27 October 2026.** The v230 research branch descends from v229, not `master`. No robot access, firmware write, change to live Valetudo+, experimental CleanGenius enablement, or publication of owner-private original firmware/configuration, maps or diagnostic archives.

## Complete downloadable offline kit

**`X40-R2416-v230-sanitized-analysis-kit.zip`**  
SHA-256 **`1f63a1bacd72e7ff71cad337bdb130a46815d3fe676c38d96e5b06f05901e800`**.  
Size **317,341 bytes**. **151 ZIP entries** including `SHA256SUMS.txt`. Fresh extraction verified ZIP integrity and **150/150 internal file SHA-256 checks**.

Verification results, deliberately reported at their actual scopes:
- **Working-source full suite: 14/14 passed**, including complete v197–v229 historical private/original evidence replay and sanitized create-only report validation.
- **Clean-extraction isolated new native/mutation tests: 13/13 passed**. The independent 27-instruction, two-ELF original firmware checker also passed.
- The separate clean-extraction **full historical replay exceeded the execution limit**; do not claim that particular pass.

The complete v230 verifier checks **25 original route-host words, 26 original health-host words, ten decoded direct-call targets and four conditional branch targets**. It checks exactly **264 copied bytes** in *each* original module; a direct sensor-byte `+0xfa` census finds three selected instruction sites in `node_lethe.so` and **zero of that exact instruction form** in `node_health_lethe.so`. Original SHA-256 pins are enforced separately. Mutation tests reject changed copy lengths, health logic/planning calls, retained reception count, route subscription, and a newly inserted otherwise-unanchored health `LDRB #0xfa`.

All release files are sanitized Python source, reports, JSON or checksums; there are no proprietary original ELFs or PRIVATE collector ZIPs.

## Replay on macOS

```sh
cd ~/Downloads
unzip X40-R2416-v230-sanitized-analysis-kit.zip
cd x40-r2416-v230-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V230_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V230_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V230_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V230_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V230_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V230_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V230_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V230_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 x40_r2416_v230_repo_check.py --prior-zip "$X40_V230_PRIOR_ZIP"
python3 -m unittest -v test_verify_x40_r2416_v230.py

python3 verify_x40_r2416_v230.py \
 --prior-zip "$X40_V230_PRIOR_ZIP" --delta-zip "$X40_V230_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V230_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V230_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V230_SCOPE_SANITIZED" \
 --scope-private "$X40_V230_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V230_PROCESS_SANITIZED" \
 --process-private "$X40_V230_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v230-new-SANITIZED.json"
# X40_R2416_V230_TWO_SENSOR_CONSUMERS_STATIC_PASS 25 26 6 4 2 2 3 0
```

The `--out` path must not already exist: output is create-only sanitized JSON. The verifier tests exclude private IP, PID, working directories and source archive paths from output.

The smaller checkout-local `docs/research/x40-r2416-v230-tools/x40_r2416_v230_repo_check.py` only requires the original owner PRIVATE collector ZIP. It checks **14 representative route-host instructions, 13 health-host instructions, the two full-ELF hash pins, two 264-byte copy sequences and the absence of exact unsigned-offset byte-250 health reads**. The complete ZIP is needed for all 51 anchors and historical replay.

## Result and next boundary

Both original native modules implement an `AvaSensorsMsg` consumer with a 264-byte copy. The health module additionally delegates to `LogicSensorDataGet` and `PlanningSensorDataGet` and conditionally increments a reception counter. **None of this establishes the upstream publisher, live sensor object identity, physical byte-250 field meaning, dock wash or stain-triggered new production floor-cleaning task**. Search for original sensor producer/transport metadata or an authoritative OEM struct definition rather than guessing from code-value coincidences. Keep the independent stain-area-to-new-floor-task scheduling issue open.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0` and `writeGateOpen=false`. Do not transmit experimental raw MCU commands.

See [v230 detailed research](x40-r2416-v230-two-sensor-consumers-2026-10-27.md) and [sanitized findings](x40-r2416-v230-two-sensor-consumers-SANITIZED.json).
