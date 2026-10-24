# v148 source-checked edge-cut necessity: reproducibility

The operator's `X40-R2416-v148-sanitized-necessary-branch-edges.zip` SHA-256 `4633b7490b82a3637449b507e3cee58e2c510d47b6a6fe40465a6fbffdffedb9` contains the complete Python standard-library `x40_r2416_v148_necessary_edge_cut_verify.py` with sanitized v112–v147 dependencies, full report, aggregate results JSON, README and SHA256SUMS.

Source-independent tests actually run: **11** targeted fixtures, **64** deterministic synthetic graphs, **192** v135 independent state/edge-deletion comparisons; v147 inherited source-free tests, clean-extraction replay, archive CRC and checksums all pass.

```sh
cd ~/Downloads
unzip X40-R2416-v148-sanitized-necessary-branch-edges.zip
cd x40-v148-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v148_necessary_edge_cut_verify.py --self-test
```

Original vendor firmware and sanitized model-compare input are kept private. **The following source-dependent command was not run in the assistant environment**, since both source files were not accessible:

```sh
python3 x40_r2416_v148_necessary_edge_cut_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --max-cut-edges 16 --self-test \
 --out ~/Downloads/x40-v148-necessary-branch-edges.json
```

The output describes branch edges whose deletion removes a candidate writer from *all bounded static paths*, and **does not establish which edge was taken in a real run**. Unchecked edges and implicit memory aliases are outside its claim. No original firmware bytes, raw model identity, private settings, log, APK, tokens, maps or command values are in the ZIP or this commit. Last known working robot and GitHub master remain unchanged.
