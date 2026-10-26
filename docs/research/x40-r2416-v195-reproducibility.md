# X40 R2416 v195 — reproducibility and correction precedence

The full **self-contained offline** executable kit, including v184–v195 Python 3 standard-library native ELF verifiers, test modules, verified corrected provenance report and sanitized result:
`X40-R2416-v195-sanitized-native-robotnode-reconciliation.zip`
SHA-256: `c0aea5da94545c2fa2e43406a5617fd28a4dbd63f69fa3c749c8d2874563abbe`.

With original `node_lethe.so` (SHA `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`) and `liblethe_route_nodes.so` (SHA `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`): **277 passing tests**. Clean extraction without the original native binaries: **128 passed, 107 skipped**, all **42 checksums matched**.

```sh
unzip X40-R2416-v195-sanitized-native-robotnode-reconciliation.zip
cd x40-v195-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -q test_x40_r2416_v195.py
# For the complete regression, use README.md.
```

Main v195 native code: `x40_r2416_v195_selector_native_builder_reconcile.py`. This was independently run against the two exact original ELFs with 19 passing focused tests, including corrupted-instruction rejection.

**Prior source provenance, not newly re-verified raw assets:** owner-collected config selecting `RobotNode` and identical saved runtime tree modules are documented and originally tested in v27–v46 research. **Do not look for `RobotNode.xml` as a prerequisite** for analysis of the registered native `RobotNode` builder. The required next private original library is `liblethe_tree.so` (SHA `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`). No robot, network, MIOT or write operations required.
