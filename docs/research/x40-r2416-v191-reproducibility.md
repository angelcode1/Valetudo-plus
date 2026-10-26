# X40 R2416 v191 — Reproducibility and exact offline artifact

Validated release archive: `X40-R2416-v191-sanitized-dynamic-area-selection-guard.zip`

SHA-256: `e9aa20bfe12a03c933faf54fdc4fe4bd426ce81306a8afa0b579ad0c10bafdf2`.

The archive contains all Python standard-library verifiers and test files from v184–v191 (including v188 UI metadata fixtures), a detailed report, `v191-dynamic-area-guard-SANITIZED.json`, README and SHA256SUMS. No original native .so binaries or user screenshots are included.

Original private ELF: `liblethe_route_nodes.so`, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.

```sh
cd ~/Downloads
unzip X40-R2416-v191-sanitized-dynamic-area-selection-guard.zip
cd x40-v191-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py
# Clean ZIP without private ELF: 101 passed / 58 skipped.

ROUTE_ELF="/private/path/liblethe_route_nodes.so"
for n in 184 185 186 187 188 189 190 191; do export "X40_R2416_V${n}_ROUTE_ELF=$ROUTE_ELF"; done
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py
# With exact original private ELF: 201 passed.

python3 x40_r2416_v191_dynamic_area_guard_verify.py --route-elf "$ROUTE_ELF" --out ~/Downloads/X40-R2416-v191-dynamic-guard-SANITIZED.json
```

The output path must not already exist. All commands are read-only and offline. An exact named key and next-point virtual setter-compatible call are **not proof of autonomous sensor-triggered reclean**.
