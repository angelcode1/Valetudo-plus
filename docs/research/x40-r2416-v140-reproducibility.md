# Dreame X40 R2416 v140 — sanitized offline verifier

Owner-side package: `X40-R2416-v140-sanitized-route-tree-blackboard.zip` (SHA-256 `54238940e0e4e9c36dbabb9f86a0040935ade94e6bb41d60384a4e27a411ca72`). It includes the complete `x40_r2416_v140_route_tree_blackboard_verify.py`, all sanitized Python regression dependencies v112–v139, source research report, aggregate-only results JSON, README and SHA256SUMS.

```sh
unzip ~/Downloads/X40-R2416-v140-sanitized-route-tree-blackboard.zip -d ~/Downloads
cd ~/Downloads/x40-v140-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v140_route_tree_blackboard_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Checked and **re-run from clean extraction**: ten original SHA-256 vendor ELF pins, v139 station builder regression, single direct model call, four route tree-builder calls from the identical +0x30 Blackboard source, the separate fifth BtTask tree build call, XMLParser Blackboard argument forwarding, ten remaining static model flag-writer candidates, and 28 independent original instruction mutation rejections.

The two input ZIPs remain owner-private or sanitized user outputs; they are not bundled in v140 and no private vendor source, disassembly, raw MODEL, configs, maps, serial, keys, logs or hardware-command parameters are committed.

This only proves original compiled *argument provenance*, not live tree activation, Blackboard object identity at different times, effective runtime flag value, one executed flag writer or a real additional physical mop wash. No robot I/O, Valetudo binary change, safety gate change or `master` mutation.
