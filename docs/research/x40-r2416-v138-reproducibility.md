# X40 R2416 v138 — offline replay and privacy

The complete owner-side sanitized bundle is `X40-R2416-v138-sanitized-blackboard-scope-boundary.zip`; verified SHA-256 `7aab034bcf7325476840996c76b537cb0b044fd9b99050649b5c0169ec6f7e39`. It contains the Python standard-library `x40_r2416_v138_blackboard_handoff_verify.py`, prior v112–v137 sanitized source verifiers, the full report, aggregate JSON, README and SHA256SUMS.

Only private *local inputs*: the original ten-ELF v62 firmware ZIP, and the owner-produced **sanitized** v128 model-compare-site ZIP.

```sh
unzip ~/Downloads/X40-R2416-v138-sanitized-blackboard-scope-boundary.zip -d ~/Downloads
cd ~/Downloads/x40-v138-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v138_blackboard_handoff_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Verified original SHA-256 pins: ten. Native model source/positive direct candidate regression: ten stores. Source-pinned exact native producer and station lookup/helper branch corridors: four. Independent original instruction and key-literal mutation rejections: **23**. Original v116 named helper regression and v117 typed Boolean setter/Blackboard key regression: PASS. ZIP CRC, SHA256SUMS and separate clean extraction: PASS.

**Never upload or commit** the original proprietary firmware, any native disassembly, original model literal or robot config, serials, maps, logs, tokens, APK, or hardware command values. This commit contains only this reproducibility note, sanitized report and aggregate JSON. Robot, `master`, Valetudo executable, SmartHost=0, writeGateOpen=false and recovery configuration unchanged.

A native Boolean setter through one Blackboard and a station entry lookup through another Blackboard accessor are not a proof of shared active scope, executed store, live turbidity enablement, or an actual second wash.
