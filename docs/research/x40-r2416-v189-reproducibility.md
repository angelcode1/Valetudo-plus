# X40 R2416 v189 — reproduce and provenance

**Full validated standalone ZIP**: `X40-R2416-v189-sanitized-task-end-completion-boundary.zip`
SHA-256 `5e458ed0eb62ccf42dd551687178be55295e6eeadfa85c075741f06bcb5e4269`.

**Source ELF** (never committed or included): `liblethe_route_nodes.so`, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.

After downloading the ZIP into ~/Downloads:
```sh
cd ~/Downloads
unzip X40-R2416-v189-sanitized-task-end-completion-boundary.zip
cd x40-v189-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py
# 83 pass, 40 skip without original ELFs
for n in 184 185 186 187 188 189; do export "X40_R2416_V${n}_ROUTE_ELF=/private/path/liblethe_route_nodes.so"; done
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py
# All 165 tests passed against the exact original private ELF
```

This GitHub branch additionally commits `docs/research/x40-r2416-v189-tools/v189_repo_check.py` and a narrow independent test file. These two are **not** a replacement for the fully tested v184-v189 verifier suite in the ZIP; their scope is pinned original ELF, selected instruction, literal, PLT/GOT and complete direct-BL census of four exact PLT destinations. From this repo:
```sh
cd docs/research/x40-r2416-v189-tools
python3 -m unittest -v test_v189_repo_check.py
X40_R2416_V189_ROUTE_ELF=/private/path/liblethe_route_nodes.so python3 -m unittest -v test_v189_repo_check.py
python3 v189_repo_check.py --route-elf /private/path/liblethe_route_nodes.so
```
Both checks are read-only offline and make no live robot requests. No CleanGenius enablement or physical reclean is established.
