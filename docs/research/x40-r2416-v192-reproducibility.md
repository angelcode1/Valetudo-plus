# X40 R2416 v192 offline reproducibility

**Validated self-contained ZIP**: `X40-R2416-v192-sanitized-dynamic-point-handoff.zip`

SHA-256: `7bd8c90cc20f4b4ea4fbc2ef839083f0fda7dacf7d8b6df46ef11169d857263e`.

Original private `liblethe_route_nodes.so`: SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Do not put this ELF on a public GitHub branch.

```sh
cd ~/Downloads
unzip X40-R2416-v192-sanitized-dynamic-point-handoff.zip
cd x40-v192-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py test_x40_r2416_v192.py
# Without original ELF: 109 pass, 71 skip.
ROUTE_ELF="/private/path/liblethe_route_nodes.so"
for n in 184 185 186 187 188 189 190 191 192; do
  export "X40_R2416_V${n}_ROUTE_ELF=$ROUTE_ELF"
done
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py test_x40_r2416_v192.py
# With exact private ELF: 222 pass.
python3 x40_r2416_v192_dynamic_point_handoff_verify.py --route-elf "$ROUTE_ELF" --out ~/Downloads/X40-R2416-v192-point-handoff-SANITIZED.json
```

The output path must be new. All commands are offline and read-only. The full executable verifier, tests, reports, and checksums live inside the ZIP; GitHub stores sanitized findings and the immutable ZIP SHA-256. No live CleanGenius or physical second pass has been verified.
