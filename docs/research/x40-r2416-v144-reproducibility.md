# v144 sanitized offline reproduction

Complete tested verifier ZIP: `X40-R2416-v144-sanitized-lse-atomic-correction.zip`
SHA-256: `7dca82bb49859b1dd7eaae528601ce32f26a2a802416d8933cb84f2a1ff52f70`.

```sh
unzip ~/Downloads/X40-R2416-v144-sanitized-lse-atomic-correction.zip -d ~/Downloads
cd ~/Downloads/x40-v144-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v144_lse_atomic_store_decode_verify.py --self-test
python3 x40_v144_lse_atomic_standalone_regression.py
```

Validated: **133** main assertions, **21** assembled-word standalone test samples, **19** compiler/objdump source-to-opcode matches; manifests and clean extraction pass.

To scan the real pinned firmware (not performed during this turn because the restored v62 source was not available in the container), run locally on a trusted computer with the owner-held original archive:

```sh
python3 x40_r2416_v144_lse_atomic_store_decode_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --self-test --out ~/Downloads/x40-v144-native-store-census.json
```

This scans the native 3,194-instruction interval with both v143/v144 classifiers, source-pins the original ten ELFs and earlier handoffs, and writes only sanitized counts/sites. No live device operation. The 10 possible original R2416 model-flag writers are unchanged; no unique execution is claimed.
