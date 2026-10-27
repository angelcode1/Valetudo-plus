# X40 R2416 v226 — reproducible source-only research

27 October 2026. Research-only continuation of v225. The robot, firmware, running Valetudo+, experimental flags and master remain unchanged. No original vendor ELF, owner PRIVATE diagnostics, credentials, IPs, PIDs, paths or raw configs are committed.

## Complete offline release

File: X40-R2416-v226-sanitized-analysis-kit.zip
SHA-256: d7f198651f42c9d7137c4d21eeaf03f992158eebfe00593d4083f1f55692e0c3
Size: 269,347 bytes. 127 ZIP entries including SHA256SUMS.txt.
Fresh-extraction ZIP CRC and 126/126 per-file SHA-256 hashes passed.

Full source-directory test suite: 11/11 passed, including original PRIVATE v197–v225 regressions.
Clean-extraction isolated native/mutation tests: 10/10 passed. The independent repository checker also passed with 16 instruction words, 32 direct calls and two nearby 32/33 immediates.
The separate clean-extraction FULL historical replay exceeded the execution limit and is not claimed to have passed.

## Replay on macOS

Extract the ZIP under ~/Downloads; change to x40-r2416-v226-sanitized. Check the file hashes with:
  shasum -a 256 -c SHA256SUMS.txt

To run the bounded checker with only the owner PRIVATE archive:
  python3 x40_r2416_v226_repo_check.py --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"

To run the complete test suite, set environment variables X40_V226_PRIOR_ZIP, X40_V226_DELTA_ZIP, X40_V226_OFFLINE_RESOLVER_ZIP, X40_V226_LIVE_RESOLVER_ZIP, X40_V226_SCOPE_SANITIZED, X40_V226_SCOPE_PRIVATE, X40_V226_PROCESS_SANITIZED, X40_V226_PROCESS_PRIVATE to the original v197–v225 evidence files, then run:
  python3 -m unittest -v test_verify_x40_r2416_v226.py

Complete commands and original evidence filenames are in the kit README.md. The full verifier checks 22 exact original AArch64 instructions, 32 host typed MCU direct-publish sites, 18 native function owners, two restricted W-MOVZ 32/33 constructions, four top-level response selector codes, the typed subscriber and its original GOT callback relocation. It rejects overwriting the sanitized output.

GitHub independent checker: docs/research/x40-r2416-v226-tools/x40_r2416_v226_repo_check.py. This smaller Python 3 stdlib-only script verifies the original whole-ELF SHA, 16 native instruction anchors, all 32 direct publisher sites and both restricted nearby W-MOVZ sites; it does not replace the full chain.

## Interpretation boundary

The original typed MCU response callback binds McuSwitchRspProcessSUB. Its initial code selector compares 24, 26, 27 and 36, not 32 or 33. No OEM protocol meanings, actual MCU send/reply, dock wash, stain-triggered extra floor cleaning task or physical second pass has been demonstrated. A 144-byte preceding-MOVZ search cannot exclude other ways of constructing the same values.

Next: read-only cross-reference of other station/mop status consumers and original protocol constants; separately trace stain_area_for_logic / SetExtraCleanArea into a production new-task dispatch. Do not send numeric test commands to the robot.

Preserve VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0, SmartHost=0, SmartAutoMop=-1, SmartAutoWash=0 and writeGateOpen=false.

See the v226 technical research report and sanitized JSON alongside this file.
