# X40 R2416 v193 reproducibility

The self-contained, original-ELF-mutation-tested full verifier suite is in **X40-R2416-v193-sanitized-dynamic-point-consumers.zip**, SHA-256 **7e3b23509728f3e434c4e6dfd63d35e6766c96de36bf15e31d3dde071ae48d43**. It includes Python standard-library-only v184–v193 verifier modules, all corresponding tests, source-grounded result/report, and 35-entry SHA256SUMS.txt. No proprietary ELF in ZIP or GitHub.

Original private ELF `liblethe_route_nodes.so`: SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.

```sh
cd ~/Downloads
unzip X40-R2416-v193-sanitized-dynamic-point-consumers.zip
cd x40-v193-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v193.py
# Without private original ELF: 5 passed, 12 skipped.
ROUTE_ELF="/private/path/liblethe_route_nodes.so"
for n in 184 185 186 187 188 189 190 191 192 193; do
  export "X40_R2416_V${n}_ROUTE_ELF=$ROUTE_ELF"
done
python3 -m unittest -q test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py test_x40_r2416_v192.py test_x40_r2416_v193.py
# Original ELF full regression: 239 passed.
python3 x40_r2416_v193_dynamic_point_consumers_verify.py --route-elf "$ROUTE_ELF" --out ~/Downloads/X40-R2416-v193-dynamic-point-SANITIZED.json
```

Fresh extracted ZIP with no private native module: 197 tests ran, 114 passed and 83 skipped. All 35 checksums matched. Original ELF run: 239 tests passed. Additional compact standalone repo checker and separate focused tests (not a replacement for ZIP):
```sh
cd docs/research/x40-r2416-v193-tools
python3 -m unittest -v test_v193_repo_check.py
python3 v193_repo_check.py --route-elf /private/path/liblethe_route_nodes.so
```

Research-only; static references do not prove motion, a task dispatch or sensor-triggered reclean.
