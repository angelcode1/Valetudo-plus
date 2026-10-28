# X40 R2416 v135 — reproducibility and privacy

The operator's validated ZIP `X40-R2416-v135-sanitized-correlated-flag-paths.zip`, SHA256 `ff74f02f9f9fc46d92b4e5b49b0de4ded54279310f4ca8117dc3d4f1f5608191`, contains the complete Python-stdlib v135 offline verifier, v112–v134 sanitized regression Python files, a detailed source-constrained technical report, aggregate JSON, README and SHA256SUMS.

The owner-held ten-ELF `X40-R2416-v62-readonly-20261023T051829Z.zip` and the privacy-preserving `X40-R2416-v128-model-compare-site-20261024T112745Z.zip` are required only as **local read-only inputs**.

```sh
unzip ~/Downloads/X40-R2416-v135-sanitized-correlated-flag-paths.zip -d ~/Downloads
cd ~/Downloads/x40-v135-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v135_correlated_store_reachability_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

**Observed on fresh ZIP extraction:** 10 original SHA256 pins, v134-source and ten-store opcode regression, overlapping wide-pointer SP98 kept unknown, SP100 zero-only, all-path conditional direct-store obligation, 10 potential positive-source last flag stores, 27 independent original ELF instruction-byte mutations rejected by targeted opcode checks.

The research GitHub commit includes only this report and aggregate JSON. Neither the ZIP nor GitHub includes original vendor ELF, disassembly, private model string, map, credentials, APK, original config or actuator commands. No live device action, runtime code change, `master` modification or rollback modification occurred.

All-path *bounded model* results are not runtime instruction traces and do not prove effective native enablement or an additional physical mop wash.
