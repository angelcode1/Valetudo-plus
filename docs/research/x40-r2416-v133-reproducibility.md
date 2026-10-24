# X40 R2416 v133 — offline reproducibility and privacy

Download the operator-side **sanitized** `X40-R2416-v133-sanitized-nonprefix-model-spill.zip` (SHA-256 `8148200b25dacb080e792244a72b2d2ee71e45d06bc63febccb0a9d827363712`). It contains Python 3 standard-library script `x40_r2416_v133_nonvendor_model_spill_verify.py`, all v112–v132 sanitized regression Python modules, detailed report, aggregate-only JSON, README and `SHA256SUMS.txt`.

Private local inputs (never included or committed): owner's SHA-pinned firmware `X40-R2416-v62-readonly-20261023T051829Z.zip`, plus *sanitized* `X40-R2416-v128-model-compare-site-20261024T112745Z.zip`.

```sh
unzip ~/Downloads/X40-R2416-v133-sanitized-nonprefix-model-spill.zip -d ~/Downloads
cd ~/Downloads/x40-v133-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v133_nonvendor_model_spill_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Passed: ZIP integrity, every checksum, fresh-unzip verifier replay, ten original ELF SHA256 pins, complete 297 direct primary literal comparison patterns, 3 new no-match source branches, isolated exclusion of one former direct writer (`0x476598`), conservative 10-site bound, scoped SP+0x100 last-store source, 24 independent native source-byte mutations rejected.

The **public GitHub commit includes only sanitized documentation and aggregate JSON**, never the proprietary firmware or original disassembly, private model literal, raw configs/maps/logs/device IDs/tokens, Android APK, or station-command values. The robot, working Valetudo+ safety configuration and `master` are untouched. These static paths are not an executed flag-writer trace or proof of real additional physical washing.
