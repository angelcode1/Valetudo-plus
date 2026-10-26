# v188 offline verifier and source manifest

Download `X40-R2416-v188-sanitized-extra-clean-type-x50-ui.zip`, SHA-256 `39198cb2487bd5f0a01d9cf22eeee9c21dc302deee6513ffa499e01daad36e5c`.

```sh
cd ~/Downloads
unzip X40-R2416-v188-sanitized-extra-clean-type-x50-ui.zip
cd x40-v188-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py
```
73 pass, 30 original-ELF checks skip when private binary is not supplied.

Original native evidence replay uses the *privately retained* `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Point `X40_R2416_V184_ROUTE_ELF` through `X40_R2416_V188_ROUTE_ELF` to that file and rerun the above unit tests. All 145 tests passed against the original ELF. CLI:
```sh
python3 x40_r2416_v188_extra_clean_type_consumers_verify.py --route-elf /private/path/liblethe_route_nodes.so --out "$HOME/Downloads/X40-R2416-v188-new-SANITIZED.json"
```
The output JSON path must not already exist. This ZIP is the executable offline test and source archive; public repo commit tracks the sanitized result and immutable ZIP fingerprint. The screenshots and firmware ELFs are intentionally omitted.
