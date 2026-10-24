# v146 bounded execution-proof gate — replay

The full Python stdlib source `x40_r2416_v146_execution_evidence_gate.py`, prior v112–v145 verifier imports, and synthetic 1,857-case oracle are in the separately delivered **`X40-R2416-v146-sanitized-evidence-gate.zip`** (SHA-256 `80033a695eeaf047c8ab15b6dfc6a7bb29026cbb4ad75be0fc913e3bda10fc98`).

```sh
unzip ~/Downloads/X40-R2416-v146-sanitized-evidence-gate.zip -d ~/Downloads
cd ~/Downloads/x40-v146-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v146_execution_evidence_gate.py --self-test
python3 x40_r2416_v145_assembled_oracle_and_source_gate_verify.py --self-test

# Real source run (NOT run in model's container):
python3 x40_r2416_v146_execution_evidence_gate.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --self-test --out ~/Downloads/x40-v146-validated-native-constructor-census.json
```

Original-source mode runs v145 SHA256/anchor checks, then whitelists the result. Imported v145 JSON can be consistency checked with `--v145-source-json`, but its unverified flags are explicitly treated as **reported claims**, not fresh source authentication. Missing original sources fail closed. The output cannot show which of ten `ProcessModelInfo` eligibility stores actually executed because the constructor census audits **a different function and memory field**.

Verified locally: **21** invalid synthetic evidence mutations rejected, zero-overlap synthetic case keeps all ten possible model flag writers, inherited v145 1,857-opcode synthetic oracle and 133 prior regression assertions pass; 44 ZIP manifest entries and ZIP CRC pass. No original ELF, APK or live device observation in this run. No bot firmware, Valetudo code, original launcher, master or safety gate modifications.