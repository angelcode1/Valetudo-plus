# v190 offline reproducibility

Validated package: **X40-R2416-v190-sanitized-need-extra-clean-role-audit.zip**

SHA-256: `8bdbb48242b4ecfe8fae9fc7cebef4411558aff0b822239e1857e41a31835222`

Private original `liblethe_route_nodes.so`, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Original ELF is not committed or distributed.

Extract on macOS:
```sh
cd ~/Downloads
unzip X40-R2416-v190-sanitized-need-extra-clean-role-audit.zip
cd x40-v190-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py
```
Without original ELF: 92 pass / 47 skip. With original ELF assigned to each `X40_R2416_V184_ROUTE_ELF` through `X40_R2416_V190_ROUTE_ELF`: 181 pass. Full verifier:
```sh
python3 x40_r2416_v190_need_extra_clean_consumers_verify.py --route-elf /private/path/liblethe_route_nodes.so --out ~/Downloads/X40-R2416-v190-need-extra-clean-SANITIZED.json
```
The verifier refuses to overwrite existing output. No robot connection required. All 22 files in the extracted kit match its SHA256SUMS. Bounded native key-reference role counts do not establish autonomous CleanGenius scheduling.
