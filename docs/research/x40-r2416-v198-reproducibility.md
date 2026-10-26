# X40 R2416 v198 — reproducibility and preservation

**26 October 2026; all offline.** Branch is based on v197 (and therefore includes the v195 correction: native `RobotNode` is the configured root; `RobotNode.xml` is not mandatory). `master` and the working Valetudo+ deployment were not changed.

## Available in this repository

- [Sanitized native finding](x40-r2416-v198-a-table-fallback-provenance-2026-10-26.md)
- [Machine-readable sanitized result](x40-r2416-v198-a-table-fallback-SANITIZED.json)
- [Standalone bounded Python verifier](x40-r2416-v198-tools/x40_r2416_v198_repo_check.py). This checks the exact original SHA-pinned tactics ELF, **32** distinct instructions and **12** decoded branches; it has no external dependencies.

From a checkout of this research branch, with the owner's private original collector ZIP kept **outside** the repository:

```sh
python3 docs/research/x40-r2416-v198-tools/x40_r2416_v198_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V198_REPO_NATIVE_BRANCH_PASS 32 anchors 12 edges
```

## Complete v197 + v198 self-contained offline kit

Artifact: `X40-R2416-v198-sanitized-analysis-kit.zip`

SHA-256: `b4d688bef97e5c817fb366854bf4e98f7a58c7120d3d82ae30111ebdca622042`

The kit includes the complete v197 verifier, full v198 verifier and tests, sanitized report/results, and its own checksum manifest. It was validated against the owner's two private ZIPs: **18 + 7** saved-payload checksums, five pinned original ELF SHA-256 fingerprints, **54 + 32 = 86** instruction anchors and **13** decoded edges. Six focused tests passed with private native mutation, an altered collector provenance record was rejected, and create-only report output refused overwrite.

```sh
unzip X40-R2416-v198-sanitized-analysis-kit.zip
cd x40-r2416-v198-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_verify_x40_r2416_v198.py
python3 verify_x40_r2416_v198.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip" \
  --delta-zip "$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip" \
  --out "$HOME/Downloads/X40-R2416-v198-new-SANITIZED.json"
```

**Security boundary:** No raw vendor ELF, unredacted robot configuration, personal maps, model weights or credentials should be uploaded to GitHub. The private collector ZIPs are required locally for the full replay. Their presence is not proof of a live stain-triggered task or a physical second wash.
