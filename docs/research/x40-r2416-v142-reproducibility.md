# v142 expanded store decoder — reproduction and evidence boundaries

Download `X40-R2416-v142-sanitized-extended-store-boundary.zip` SHA-256 `448c4ee519f9cb1f710d7146cd157ffdab5500835bacc95f8b0d65f516655df7`; extract `x40-v142-sanitized`.

```sh
cd ~/Downloads/x40-v142-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v142_extended_store_boundary_verify.py --self-test
```

**Ran successfully:** 18 assembled-form examples, 5 negative controls, 3 load-bit mutations = 26. v141 misses post-indexed STP and STNP synthetic originals in the new fixture. These examples were independently generated; the real Dreame code was **not** opened in this run.

**Private source-dependent, prepared but not run in this environment** (two owner-only inputs missing):

```sh
python3 x40_r2416_v142_extended_store_boundary_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --self-test --out ~/Downloads/x40-v142-native-audit-results.json
```

The verifier will check original source pins and prior regressions, produce only a sanitized count/type/address report, and refuse overwriting its output. It will *not* contact the robot or identify the executed direct flag writer without additional source-specific proof.

No proprietary ELF bytes, raw model data, app binaries, tokens, maps or hardware commands belong in the public repo. All reported synthetic tests and the archive integrity were independently validated. Runtime state and `master` remain unchanged.
