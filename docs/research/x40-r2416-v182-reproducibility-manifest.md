# X40 R2416 v182 — Offline reproducibility manifest

**User-provided private ELF hashes:** see accompanying report and sanitized JSON. The original firmware modules are not in this commit or the ZIP.

**Self-contained verified ZIP:** `X40-R2416-v182-sanitized-native-stain-id-writer-subscriber.zip`, SHA-256:
`c6704587b63f39031b32ac85b42ae204e4705644d0005272210ec641c4983745`.

Kit contents: `x40_r2416_v182_cross_module_native_verify.py`, `test_x40_r2416_v182.py`, `v182-cross-module-SANITIZED.json`, README, detailed report, SHA256SUMS. Python 3 standard library only; no robot network operations.

```sh
cd ~/Downloads
unzip X40-R2416-v182-sanitized-native-stain-id-writer-subscriber.zip
cd x40-v182-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v182.py
# 13 passed, 17 skipped without proprietary private ELF paths.
export X40_R2416_V182_LASER_ELF="/private/path/node_laser_transfer.so"
export X40_R2416_V182_ROUTE_ELF="/private/path/liblethe_route_nodes.so"
python3 -m unittest -v test_x40_r2416_v182.py
python3 x40_r2416_v182_cross_module_native_verify.py --laser-elf "$X40_R2416_V182_LASER_ELF" --route-elf "$X40_R2416_V182_ROUTE_ELF" --out ~/Downloads/X40-R2416-v182-native-evidence-SANITIZED.json
```

Original ELF execution with both private binaries: 30 tests passed. Independent instruction/literal/relocation mutations rejected. Clean ZIP extraction/checksum/test replay passed. The finding establishes compiled stain-ID producer/consumer paths, *not* an autonomous sensor-triggered floor reclean.
