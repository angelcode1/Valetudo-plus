# v147 source-checked control-flow witness kit — reproducibility

Download `X40-R2416-v147-sanitized-correlated-flag-witnesses.zip`; SHA-256: `274dd4518f6b94195e384f904c1a2bb18b9b399f61318aa4dae63de18ac02269`.

Includes complete `x40_r2416_v147_flag_writer_witness_verify.py`, the sanitized v112–v146 Python dependencies, report, aggregated JSON, README, SHA256SUMS. The original private v62 firmware and sanitized v128 model-compare-site ZIP are **not bundled or committed**.

```sh
unzip ~/Downloads/X40-R2416-v147-sanitized-correlated-flag-witnesses.zip -d ~/Downloads
cd ~/Downloads/x40-v147-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v147_flag_writer_witness_verify.py --self-test
python3 x40_r2416_v147_flag_writer_witness_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --self-test --out ~/Downloads/x40-v147-flag-writer-witnesses.json
```

**Ran here:** source-independent self-test, refusal of missing private inputs without writing output, Python compile, complete checksum manifest, ZIP CRC and clean-extraction self-test. **Not run here:** original firmware v147 witness extraction, due to unavailable private bytes in the active runtime.

The generated JSON (when run on owner's Mac) reports *static* source-verified path examples; their branch choices are **not** unique or necessarily executed. Do not publish vendor binaries or sensitive config. No robot change; `master` remains intact.
