# X40 R2416 v125 — reproducibility and privacy

The full Python-standard-library verifier is supplied separately to the operator as `X40-R2416-v125-sanitized-dual-positive-sources.zip` (SHA-256 `49ce508127c63bf571330a155021a590f990877520e69f425e3d60e6c38bdfad`). It contains `x40_r2416_v125_dual_initializer_paths_verify.py` and its v112–v124 imported verifier modules, the detailed report, aggregate JSON, README and checksum manifest.

Use the private original `X40-R2416-v62-readonly-20261023T051829Z.zip` as local input:

```sh
unzip ~/Downloads/X40-R2416-v125-sanitized-dual-positive-sources.zip -d ~/Downloads
cd ~/Downloads/x40-v125-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v125_dual_initializer_paths_verify.py ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Original binaries: 10/10 SHA-256 pins pass. Previous v124 regression: pass. Four second positive W24 sources and branch corridors: pass. Bounded two-source coverage: pass. Independent original-instruction mutation rejection: **28/28**.

This public research commit contains **only documentation and sanitized aggregate JSON**. Do not distribute the original vendor ELF files, original device settings, logs, maps, tokens, compiled app code or guessed hardware command values.

The last tested robot state (Valetudo+ v74, SmartHost=0, writeGateOpen=false), executable code and repository `master` are unchanged. Native model eligibility, actual gate value, and physical second wash are still unverified.
