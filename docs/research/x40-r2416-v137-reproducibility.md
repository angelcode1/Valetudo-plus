# X40 R2416 v137 — replay and privacy

The complete operator-side sanitized kit is `X40-R2416-v137-sanitized-register-source-corridors.zip` SHA-256 `8ac6e6d6e4d0bca9b0f1aef605eb34bebe72025ba3e3947dd15a088204b5a560`. It contains standalone Python 3 stdlib verifier `x40_r2416_v137_register_corridor_verify.py`, v112–v136 sanitized Python modules, report, aggregate JSON, README and checksum manifest.

```sh
unzip ~/Downloads/X40-R2416-v137-sanitized-register-source-corridors.zip -d ~/Downloads
cd ~/Downloads/x40-v137-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v137_register_corridor_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Verified: ten original firmware SHA256 pins, ten candidate direct stores, ten initializer-cut CFG checks, 16 source-byte-pinned corridors, 97 source-clobber instructions decoded, two ABI-preserved W23/W24 calls, 25 independent original-source mutations and seven synthetic decoder tests. ZIP CRC/checksum and fresh-extraction offline replay passed.

Original vendor ELF files, native disassembly, raw MODEL/DEV_MODEL, private device configs, serials, maps, logs, credentials, control opcode payloads and Android APKs were **not** included in this kit or committed to GitHub. The robot, Valetudo executable, `master`, working v74 baseline and rollback assets are untouched.

These bounds **do not** identify an actually executed instruction, live turbidity/rewash enablement or a physical additional mop wash.
