# v185 offline reproducibility and provenance

**Private original ELF:** `liblethe_route_nodes.so`; SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Private ELF not committed or included in the ZIP.

**Validated offline package:** `X40-R2416-v185-sanitized-stain-extra-planner-data-bridge.zip`; SHA-256 `187db7510fca4f8d9e76937d52e3472fc48ca51a40526aa66119ef4761c74bbe`.

```sh
cd ~/Downloads
unzip X40-R2416-v185-sanitized-stain-extra-planner-data-bridge.zip
cd x40-v185-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py
# Without private original ELF: 35 passed, 14 skipped (49 tests run).

export X40_R2416_V184_ROUTE_ELF="/private/path/liblethe_route_nodes.so"
export X40_R2416_V185_ROUTE_ELF="$X40_R2416_V184_ROUTE_ELF"
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py
# With exact original private ELF: 68 passed.

python3 x40_r2416_v185_stain_extra_bridge_verify.py \
    --route-elf "$X40_R2416_V185_ROUTE_ELF" \
    --out "$HOME/Downloads/X40-R2416-v185-stain-extra-SANITIZED.json"
```

No dependencies beyond Python 3 standard library. The last command refuses to overwrite its output path. This is read-only offline research; the compiled shared-key access does **not** prove an autonomous second cleaning pass. The public research commit records the bounded evidence and complete ZIP checksum, not the proprietary original binary or the full executable ZIP.
