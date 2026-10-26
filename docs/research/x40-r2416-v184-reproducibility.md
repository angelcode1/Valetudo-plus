# v184 complete offline artifact and procedure

The executable verifier, synthetic/negative mutation tests, sanitized result and documentation were released as:

`X40-R2416-v184-sanitized-extra-clean-planner-boundary.zip`

SHA-256: `a2b681998d2d057ced058616b366a8f34c396303e9179a6554c7de8acb39643f`

Contains source `x40_r2416_v184_extra_clean_planner_verify.py`, `test_x40_r2416_v184.py`, sanitized JSON, report, README, and SHA256SUMS.txt. No ELF included; no third-party package, network connection or root access is required to run the verifier.

```sh
cd ~/Downloads
unzip X40-R2416-v184-sanitized-extra-clean-planner-boundary.zip
cd x40-v184-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py
export X40_R2416_V184_ROUTE_ELF="/private/path/liblethe_route_nodes.so"
python3 -m unittest -v test_x40_r2416_v184.py
python3 x40_r2416_v184_extra_clean_planner_verify.py \
  --route-elf "$X40_R2416_V184_ROUTE_ELF" \
  --out ~/Downloads/X40-R2416-v184-extra-clean-SANITIZED.json
```

Original SHA: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Private binaries are never part of the ZIP or GitHub changes.

Independent clean ZIP extraction/checksum replay: passed. 29 tests pass when the private route ELF is present, 16 pass and 13 skip when absent.

**Research conclusion only:** compiled extra-clean Blackboard state verified; AI-dirt-to-extra-clean scheduling and a sensor-triggered second floor pass are not proven.
