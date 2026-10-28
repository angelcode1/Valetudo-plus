# X40 R2416 v129 — sanitized reproduction record

The standalone Python-standard-library verifier and all v112–v128 sanitized Python dependencies are in the operator-side `X40-R2416-v129-sanitized-live-model-branch.zip`, SHA-256 `e20ab95eb4d3f91ea1439f78fe7f770ddf3dbf7deb1024403dc8c6880e3d9fca`.

```sh
unzip ~/Downloads/X40-R2416-v129-sanitized-live-model-branch.zip -d ~/Downloads
cd ~/Downloads/x40-v129-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v129_model_site_branch_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --self-test
```

Reproduced: 10 original private ELF SHA-256 pins, 294 strict native model comparisons, 23 source-verified regex branches, unique private-model comparison site `site_0x473540`, verified match path `0x473544→0x472968→0x470914`, bounded 13 possible flag-writer stores, 8 rejected native source mutations and 8 rejected evidence mutations.

The original vendor firmware ZIP, model literal, device configuration and executable native data are **private inputs only**. The GitHub commit contains no original firmware/Android binaries, logs, credentials, maps, model strings or hardware command values. No robot, Valetudo runtime, GitHub `master`, SmartHost=0, `writeGateOpen=false`, launcher or recovery files were changed.

An exact compiled model-comparison site is **not a record of executed native instructions**.
