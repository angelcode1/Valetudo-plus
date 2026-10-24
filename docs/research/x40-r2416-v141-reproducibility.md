# v141 offline verifier — owner side

Operator download: `X40-R2416-v141-sanitized-route-field-store-census.zip` SHA-256 `111fc7e3ef046ba81e16328e90a51065978ed9b1bc10faf88a84c3d4193c7a09`. Bundle contains the Python-standard-library standalone verifier, v112–v140 sanitized regression modules, full report, aggregate JSON and `SHA256SUMS.txt`.

Private original v62 ten-ELF ZIP plus existing **sanitized** v128 model comparison-site ZIP are needed locally. Neither is committed, and no robot is contacted.

```sh
unzip ~/Downloads/X40-R2416-v141-sanitized-route-field-store-census.zip -d ~/Downloads
cd ~/Downloads/x40-v141-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v141_route_blackboard_direct_store_census_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

v141 audits 3,194 instructions: 101 same-offset LDR X (98 from x0); 227 decoded direct immediate GPR stores; 0 relative offsets overlapping +0x30, in the stated forms. Nineteen in-memory/synthetic mutation and decoder tests pass. This is not a proof against pointer-aliasing or interprocedural writes; no executed native eligibility writer, Blackboard runtime value or physical mop rewash is claimed.

Do not redistribute original vendor binaries, raw runtime config, firmware secrets, device IDs, maps or control command payloads. GitHub master, the robot and the last known Valetudo safety baseline remain unchanged.