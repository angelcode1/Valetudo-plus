# X40 R2416 — v127 reproducibility and privacy

The full owner-side `X40-R2416-v127-sanitized-json-model-correction.zip`, SHA-256 `10c636568673be7638b05380382006127ae3e48cdf15e6a59b265dd8dfdf11c6`, includes:
- `x40_r2416_v127_rapidjson_native_reader_verify.py` with v112–v126 Python verifier dependencies;
- `x40_v127_json_model_class_collector.py` with bounded POSIX AWK JSON parsing, strict remote protocol and no robot writes;
- technical report, sanitized aggregate source-format JSON, README, `SHA256SUMS.txt`.

In the extracted `x40-v127-sanitized` directory:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v127_rapidjson_native_reader_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
python3 x40_v127_json_model_class_collector.py --self-test
python3 x40_v127_json_model_class_collector.py --host root@192.168.8.149 --out ~/Downloads
```

The original vendor v62 ZIP remains **private**; neither it nor `/var/run/runava.conf`, app APKs, maps, tokens, device identifiers, logs, or native station command parameters are included or committed. The operator should upload only the resulting `X40-R2416-v127-json-model-evidence-*.zip`.

GitHub changes contain **research documentation and sanitized JSON only**. They do not alter executable Valetudo code, GitHub `master`, the robot, native SmartHost=0, experimental writeGateOpen=false, launcher or backups. Any unique executed gate writer remains unproven until the new model evidence constrains all relevant native branches.
