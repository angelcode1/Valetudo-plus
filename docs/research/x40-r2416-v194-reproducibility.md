# X40 R2416 v194 reproducibility

Verified complete ZIP **X40-R2416-v194-sanitized-external-bt-xml-boundary.zip**, SHA-256 **c8d2b952cd0a77d13d70e83c26e31861e0203e4fd259383ef7de6800f7f92ed5**.

Original privately retained inputs:
- `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.
- `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.

```sh
cd ~/Downloads
unzip X40-R2416-v194-sanitized-external-bt-xml-boundary.zip
cd x40-v194-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v194.py
# Without exact original ELFs: native-dependent cases skip.
HOST_ELF="/private/path/node_lethe.so"
ROUTE_ELF="/private/path/liblethe_route_nodes.so"
for n in 184 185 186 187 188 189 190 191 192 193 194; do
  export "X40_R2416_V${n}_ROUTE_ELF=$ROUTE_ELF"
done
export X40_R2416_V194_HOST_ELF="$HOST_ELF"
python3 -m unittest -q test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py test_x40_r2416_v188.py test_x40_r2416_v188_ui.py test_x40_r2416_v189.py test_x40_r2416_v190.py test_x40_r2416_v191.py test_x40_r2416_v192.py test_x40_r2416_v193.py test_x40_r2416_v194.py
# 258 native tests passed.
python3 x40_r2416_v194_external_bt_xml_boundary_verify.py --host-elf "$HOST_ELF" --route-elf "$ROUTE_ELF" --out ~/Downloads/X40-R2416-v194-new-SANITIZED.json
```

The last output must be a new .json path. Full verifier source, all prior tests, checksums and the optional read-only XML-discovery procedure are in the ZIP. **No user-facing bot commands were performed.**

**Evidence boundary:** fallback XML path is not proof of active YAML, an XML file's presence, nor dirt-triggered second-pass scheduling. XML still needs to be collected privately and inspected before task port mapping can be verified.
