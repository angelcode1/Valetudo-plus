# v143 reproducibility and source boundary

A complete offline Python-stdlib verifier and its v112–v142 sanitized dependencies are delivered in `X40-R2416-v143-sanitized-sttr-coverage.zip` (SHA-256 `bf5ecd2e7894838ddea3d3382c70e45b139506bdab1649eab0c049a7b830861c`). This repo contains the independent STTR opcode smoke test and sanitized report/aggregates, **not proprietary firmware**.

```sh
cd ~/Downloads
unzip X40-R2416-v143-sanitized-sttr-coverage.zip
cd x40-v143-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v143_unprivileged_store_coverage_verify.py --self-test
python3 x40_r2416_v143_unprivileged_store_coverage_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --self-test --out ~/Downloads/x40-v143-native-route-store-audit.json
```

The first three commands ran and passed in the analysis container (56 assertions, ZIP integrity and checksums). The final original-ELF command was not run because the owner-private archive could not be mounted, even though file metadata referenced the attachment. It needs only v62, **not v128**, and emits sanitized instruction counts/address categories, not source bytes.

An overlap is relative to the instruction's base register. It does not identify the live route object or an actually executed flag writer. Ten model-specific candidate writers remain unchanged.
