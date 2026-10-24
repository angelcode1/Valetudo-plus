# X40 R2416 v128 — reproducibility and privacy

The full standalone Python-stdlib collector, CFG auditor and v112–v127 sanitized regression dependencies are distributed in the owner-side ZIP `X40-R2416-v128-sanitized-model-identity-kit.zip` (SHA-256 `a3ec1613f901164c0e820fbfdaa9cf9418e08b91a77238d3936833c9fe5cba7d`). This research commit contains only the sanitized report, aggregate JSON and reproduction instructions.

Locally available **private** inputs: `X40-R2416-v62-readonly-20261023T051829Z.zip`, and the operator's **sanitized** `X40-R2416-v127-json-model-evidence-20261024T105639Z.zip`.

```sh
unzip ~/Downloads/X40-R2416-v128-sanitized-model-identity-kit.zip -d ~/Downloads
cd ~/Downloads/x40-v128-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_v128_private_model_compare_id.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v127 ~/Downloads/X40-R2416-v127-json-model-evidence-20261024T105639Z.zip --self-test
python3 x40_r2416_v128_model_cfg_audit.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip
python3 x40_v128_private_model_compare_id.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v127 ~/Downloads/X40-R2416-v127-json-model-evidence-20261024T105639Z.zip --host root@192.168.8.149 --out ~/Downloads
```

The last command is operator-executed and only reads native runtime model categories. It creates a two-entry ZIP with a compiler comparison-site ID and fixed privacy metadata. No device config, `MODEL` value, secrets, log, binary or control messages are exported.

**Scope:** seven R2416-family exact compiler strings all leave 13 possible direct stores in the bounded static source flow. An actual executed writer, live turbidity state, and a second physical wash remain **unverified**. No robot change or `master` change was made.
