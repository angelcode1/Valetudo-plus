# X40 R2416 v126 — verification and read-only input collection

The owner-side `X40-R2416-v126-sanitized-runtime-model-evidence-kit.zip` (SHA-256 `ff9bcfa139989805ba2bb5d008a4eae61e0659ecaac9c06a01a9471bb84adf9d`) contains both fully working Python 3 scripts, v112–v125 regression modules, sanitized report, aggregate JSON, and `SHA256SUMS.txt`.

Offline source verification from the extracted `x40-v126-sanitized` directory:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v126_runtime_model_source_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Optional operator-side **read-only**, category-only runtime input capture:

```sh
python3 x40_v126_model_key_readonly.py --self-test
python3 x40_v126_model_key_readonly.py --host root@192.168.8.149 --out ~/Downloads
```

Keep the original `/var/run/runava.conf` private; never upload its raw lines. The probe emits only whitelisted model comparison classes and stores no raw remote output, secrets or other keys. Its code passed local POSIX shell and parser mutation tests and simulated SSH failure handling, **not** a live-device run.

Neither the primary R2416 literal nor the mere presence of positive compiler branches proves which native instruction executes. This commit contains **only documentation and sanitized metadata**, not vendor firmware/app code, raw configs, maps, identifiers, or logs. Robot, Valetudo runtime, recovery artifacts and `master` stay unchanged.
