# X40 R2416 v124 — sanitized provenance and reproduction

**Full verifier:** owner-downloadable `X40-R2416-v124-sanitized-flag-value-provenance.zip` SHA-256 `3927900acc2e0a3ef07e4906098b5b432c3a36c7ab066bcf39e5be23e765d88d`.

Included: standalone Python-standard-library `x40_r2416_v124_flag_value_sources_verify.py`, v112–v123 regression modules, complete technical report, aggregate result JSON, README and `SHA256SUMS.txt`. The owner-provided original `X40-R2416-v62-readonly-20261023T051829Z.zip` with ten SHA-pinned ELF libraries is **only a private input**.

```sh
unzip ~/Downloads/X40-R2416-v124-sanitized-flag-value-provenance.zip -d ~/Downloads
cd ~/Downloads/x40-v124-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v124_flag_value_sources_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verified results: one zero-register store, twelve local one-valued sources, eight source-dominated stores, four nondominated stores, thirteen remaining potential last direct writers, and 49 independent source mutations rejected. These checks do **not** establish any live native Boolean value or dirt-triggered physical additional wash.

No firmware ELF, Android APK/native library, original configs, serials, maps, logs, tokens, command parameter values or private assets are committed. Repository changes are **documentation and sanitized JSON only**. Valetudo runtime, GitHub `master`, last tested v74 device configuration and all recovery backups remain unchanged.
