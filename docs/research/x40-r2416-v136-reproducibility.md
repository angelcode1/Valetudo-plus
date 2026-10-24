# X40 R2416 v136 — offline reproduction

Standalone sanitized artifact: `X40-R2416-v136-sanitized-stack-alias-surface.zip`, SHA256 `172f238cecacbf36076865a0ce9a5f41d0d02c17558723bf52ea3e0b1546e2e7`.

Contents: Python stdlib verifier `x40_r2416_v136_flag_alias_surface_verify.py`, sanitized prior Python regression modules v112–v135, technical report, aggregate JSON, README and SHA256SUMS. This public GitHub commit documents the audit; the owner-side downloadable ZIP carries the executable checks.

```sh
unzip ~/Downloads/X40-R2416-v136-sanitized-stack-alias-surface.zip -d ~/Downloads
cd ~/Downloads/x40-v136-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v136_flag_alias_surface_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Expected: 10 pinned original ELFs; 61 SPBC-overlapping direct integer stores all STP W; no new direct GPR byte/halfword/X64 overlap; 62 explicit nonframe stack pointer constructions lowest +0x110; same 10 model-matched potential final direct stores and 35 conservative source combinations; 29 independent source-specific opcode mutations and 10 synthetic decoder tests pass. Archive checksum validation and *fresh unzip* replay passed.

Inputs are owner-private originals, never bundled, committed or disclosed. No hardware, robot runtime or `master` modification. No unique executed writer or physical rewash is established.
