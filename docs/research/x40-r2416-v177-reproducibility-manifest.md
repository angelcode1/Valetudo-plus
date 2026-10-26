# v177 reproducibility manifest

Original private ELF (not committed):
`b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0  node_lethe.so`

Sanitized offline kit, shared separately in the research conversation:
`88a35350a5892dea45048d8e3ddb5930336aaa109e31fdc403a9f9c8359a7b4a  X40-R2416-v177-sanitized-stain-id-async-boundary.zip`

The kit contains the v175 and v176 prerequisite Python stdlib verifiers, the v177 typed-int ELF/GOT verifier, 19 unit tests, `SHA256SUMS.txt`, report, and `v177-native-stain-id-async-SANITIZED.json`. No original firmware is in the kit or this commit.

To run after obtaining that kit:

```sh
unzip X40-R2416-v177-sanitized-stain-id-async-boundary.zip
cd x40-v177-sanitized
shasum -a 256 -c SHA256SUMS.txt
X40_R2416_PRIVATE_ELF=/private/path/node_lethe.so python3 -m unittest -v test_x40_r2416_v177.py
python3 x40_r2416_v177_stain_id_async_boundary_verify.py --node-elf /private/path/node_lethe.so --out /tmp/x40-v177-SANITIZED.json
```

This repository change documents research only. It does not change runtime behavior.
