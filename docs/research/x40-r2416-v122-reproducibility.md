# X40 R2416 v122 — verifier and privacy

The full Python-stdlib verifier is supplied to the operator in `X40-R2416-v122-sanitized-regex-model-gate.zip` (ZIP SHA-256: `5f69928fffaee10ccdd5deb0ea024d9db5a22d0aadc26b4996212f220abf7f79`). This repo commit contains only the research report and aggregate metadata. No vendor ELF or downloaded Dreamehome APK bytes are included.

The offline verifier imports v112–v119 sanitized regression scripts, opens the operator-private v62 firmware ZIP, validates ten original SHA-256 pins, reruns v119 and constrains **only 14 directly anchored C++ regex-result branch sites**. It independently rejects 36 native instruction/literal mutations without requiring a whole-file hash failure.

```sh
unzip ~/Downloads/X40-R2416-v122-sanitized-regex-model-gate.zip -d ~/Downloads
cd ~/Downloads/x40-v122-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v122_regex_gate_cfg_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

These findings do not determine the live Boolean switch, active StationWash Blackboard or an extra physical wash. They change **no** robot state, Valetudo code, `master`, original launcher, safety gate, app settings, or rollback files.
