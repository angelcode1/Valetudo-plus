# X40 R2416 v131 — reproduction and privacy

Sanitized operator-side kit: `X40-R2416-v131-sanitized-cross-input-regex-gate.zip`; SHA256 `27473b17002ee5429ebe58b2d233cd46c2dabf87d4bd488b4ad479b9d61979a9`.

Includes complete `x40_r2416_v131_cross_model_regex_gate_verify.py`, its v112–v130 sanitized Python regression modules, full technical report, aggregate result JSON, README and SHA256SUMS. The operator privately supplies the ten-ELF v62 archive and the privacy-preserving v128 model comparison-site ZIP.

```sh
unzip ~/Downloads/X40-R2416-v131-sanitized-cross-input-regex-gate.zip -d ~/Downloads
cd ~/Downloads/x40-v131-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v131_cross_model_regex_gate_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Validated: 10 original firmware SHA256 source pins, v130 regression (13 sites), 4 new typed direct regex branch constraints (2 on primary model, 2 on empty secondary model), one eliminated writer `0x4761c4`, 12 remaining possible direct flag writers, 24 original instruction/literal source mutations and 5 malformed model-evidence cases rejected.

No original firmware binaries, app executables, private native model literal, device config/logs/maps, hardware commands or secrets published. No robot actions or runtime changes. `master` unchanged. A unique *executed* store and physical extra mop wash are not proven.
