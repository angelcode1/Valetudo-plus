# X40 R2416 v139 — offline verification and preservation

Complete source-verification ZIP for the operator: `X40-R2416-v139-sanitized-compiled-station-blackboard.zip`, SHA-256 `9ab70fc6531a5bc2287d2a73a37a2b61928173054bfa4fee37504364be95a31a`.

Includes Python 3 standard-library `x40_r2416_v139_compiled_station_blackboard_forwarding_verify.py`, sanitized v112–v138 Python verifier dependencies, report, aggregate JSON, README and SHA256SUMS. Only private local input archives are required:

```sh
unzip ~/Downloads/X40-R2416-v139-sanitized-compiled-station-blackboard.zip -d ~/Downloads
cd ~/Downloads/x40-v139-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v139_compiled_station_blackboard_forwarding_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

All ten source ELF SHA pins, v138 source regression, captured configured root, compiled `buildStationWash` + `buildRobotNode` symbols, factory Blackboard argument propagation, TreeNode setter call, 28 independently mutated instruction rejection cases, and clean extraction/checksums pass.

This is a **static source proof**, not actual Blackboard pointer identity or executed-writer evidence. It does not prove active native turbidity or a real second physical mop wash. No vendor binaries, raw configs, map data, model literal, credentials or native actuator data were uploaded to the public fork. No changes to robot, `master`, Valetudo runtime, SmartHost=0, writeGateOpen=false or rollback assets.
