# X40 R2416 v225 — source-only offline replay

**27 October 2026.** Read-only research; no robot communication, firmware patch, Valetudo+ change or master modification. All original vendor ELFs, owner-private archives, maps, settings and personal data stay outside GitHub.

## Complete ZIP and clean verification

Artifact: X40-R2416-v225-sanitized-analysis-kit.zip
SHA-256: f10e4fe4ee31df60051b24f943313062dc7bcf71f7f6a4b43f6c0d5459d0b499
Size: 258,403 bytes; 121 ZIP entries including SHA256SUMS.txt.

Verified: 120/120 internal SHA-256 checks; ZIP CRC; all 11 tests passed from source and all 11 passed from clean extraction. The test suite includes the complete original-private v197–v224 regression replay, 56 new native AArch64 instruction anchors, 17 decoded call/branch edges, exact 32/0 and 33/1 numeric command-field constructions, and mutation tests. All code uses Python 3 standard library; no original vendor binary is included.

Extract the ZIP under ~/Downloads, change directory to x40-r2416-v225-sanitized, and run:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v225_repo_check.py --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
```

The kit README contains the complete replay commands and environment variables for the other seven prior PRIVATE/sanitized evidence files. Full replay: python3 -m unittest -v test_verify_x40_r2416_v225.py. The full verifier's --out path is create-only and private fields are redacted.

Repository checker: docs/research/x40-r2416-v225-tools/x40_r2416_v225_repo_check.py. It independently checks the original host whole-ELF SHA-256, 18 instruction words, the named dirty-mop key, and two MCU publication sites. It returned X40_R2416_V225_REPO_NUMERIC_MCU_PAYLOADS_PASS 18 2 32 33 against the owner's original archive. Use the downloadable kit's full verifier for the 56/17 checks and inherited history.

## Bounded finding and next target

The two original _CtrlMcuCMD publish sites construct numeric fields 32/0 and 33/1. There are local paths to each publication that bypass the dirty-mop named-key lookup in the same iteration; prior retained state may still matter. The values' OEM meanings, station wash or stop commands, MCU delivery, live AI command causation, and physical second cleaning pass have not been established.

Next inspect the consumers/known constants for MCU numeric values 32 and 33, without attempting commands on the robot, and separately trace stain-area updates to actual autonomous floor-clean task-start.

Preserve VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0, SmartHost=0, SmartAutoMop=-1, SmartAutoWash=0, writeGateOpen=false.

See the v225 technical report and sanitized findings JSON beside this file.
