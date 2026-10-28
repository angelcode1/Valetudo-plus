# Dreame X40 R2416 v139 — compiled StationWash Blackboard forwarding

**25 October 2026. Offline, source-pinned original firmware audit.** No robot/cloud I/O, changes to Valetudo or proprietary binary distribution.

## The previously missing builder-to-node link

v138 proved that `node_lethe.so:ProcessModelInfo(std::shared_ptr<BT::Blackboard>&)` has a model-gated, typed `set<bool>("enable_turbidity")` on its input Blackboard (VA `0x47185c`). It also proved the separate station's `InitTurbidityCheckInfo()` obtains a Blackboard via `TreeNode::blackboard()` and tests a key-lookup result before potentially calling `TurbidityRecleanAndRewashSet()`. Shared object identity remained unknown.

The original **`liblethe_tree.so`** contains a compiled `buildStationWash(BT::BehaviorTreeFactory const&, std::shared_ptr<BT::Blackboard> const&)` at `0x358540` and a compiled `buildRobotNode(...)` at `0x312c6c`. Both use the common factory-context initializer `init_fac()` at `0x567b84`. The source ZIP's original `/ava/conf/setting.yaml` records `behavior_tree_path: RobotNode`; this is a **captured preference**, not proof that a specific tree instance is currently running. Original ELF includes generated `StationWash.xml` metadata, so the station tree is **compiled**, not dependent on finding a separate XML file in the captured archive.

Verified source opcode and ABI chain:

| Source library / PC | Compiled handoff |
|---|---|
| `liblethe_tree.so:0x358574` | `buildStationWash` calls `init_fac()` without overwriting its incoming factory / Blackboard inputs |
| `liblethe_tree.so:0x567ba0`, `0x567bd8` | `init_fac` preserves the incoming `shared_ptr<Blackboard> const&` argument in `x22`, placing it in the shared factory-context record |
| `liblethe_tree.so:0x567ec8`, `0x567ee8`, `0x567f00` | Child-node helper retrieves the record's Blackboard, forwards it as ABI argument 5 (`x4`) and calls `BehaviorTreeFactory::instantiateTreeNode()` |
| `libbehaviortree_cpp.so:0x5f504`, `0x5f634`, `0x5f638` | The native factory retains its incoming Blackboard argument and explicitly calls `TreeNode::setBlackboard()` on the new node with it |
| `libbehaviortree_cpp.so:0x5f650` | Factory then calls `TreeNode::initializeOnce()` |
| `libbehaviortree_cpp.so:0x4f8f0` | The native `TreeNode::blackboard()` accessor reads the node-associated Blackboard reference through the library's indexed storage representation |

**Proved, conditionally:** for nodes instantiated through the audited compiled StationWash factory path, the Blackboard supplied to `buildStationWash()` is carried into their `TreeNode::setBlackboard()`. This is a concrete path between tree-build-time Blackboard input and the station node's Blackboard access, improving on v138's opaque source mismatch.

**Not proved:** the original `ProcessModelInfo()` receives the *same runtime object* as `buildStationWash()`; the registered tree is the tree selected/executing on the live robot; nested tree remaps or changes are absent; the key has actually been set, is present or has a true value; or a station performs a dirt-triggered second physical mop wash. The station's key-lookup-result branch is still not a direct typed Boolean-value check. Merely containing a native plugin registration entry and generated tree metadata cannot prove that StationWash was instantiated. `TreeNode::setBlackboard()` is nontrivial; this is not a whole-program alias proof.

The v137/v138 exact-model static bound remains **ten possible positive-sourced direct writes** to the model-group flag: `0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`. No one site has been demonstrated to execute.

## Reproducibility

The separately delivered sanitized owner-side `X40-R2416-v139-sanitized-compiled-station-blackboard.zip` has SHA-256 **`9ab70fc6531a5bc2287d2a73a37a2b61928173054bfa4fee37504364be95a31a`**. It contains standalone Python-stdlib verifier `x40_r2416_v139_compiled_station_blackboard_forwarding_verify.py`, prior v112–v138 sanitized regression modules, complete report, aggregate result JSON, README and SHA256SUMS. The private original firmware ten-ELF ZIP and sanitized v128 model-site ZIP are **inputs**, not included.

```sh
unzip ~/Downloads/X40-R2416-v139-sanitized-compiled-station-blackboard.zip -d ~/Downloads
cd ~/Downloads/x40-v139-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v139_compiled_station_blackboard_forwarding_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --self-test
```

Checks passed against all ten original ELF SHA pins, the prior v138 producer/reader source verification, captured `RobotNode` root preference, exact compiled builder symbols, eight source-pinned instruction corridors across two original native libraries, the forward factory handoff, and v137's ten model-specific writer bound. **28 independent original instruction mutations** were rejected by feature-specific pinning without relying on whole-file ELF hash failures. ZIP-integrity, all SHA256SUMS checks, and clean-extraction re-execution passed.

**Next proof gate:** trace the caller(s) of `ProcessModelInfo()` and the selected `RobotNode` root builder to establish whether their supplied Blackboard values are the same live instance, then inspect any nested-tree remap. Do not force native settings, patch the tree, fake contamination, issue station actuator commands, or attach intrusive instrumentation.

**Safe baseline preserved:** last operator-confirmed Valetudo+ v74, SmartHost=0, writeGateOpen=false, original launcher and rollback assets intact. Original ELF files, original model string, device configs/secrets/maps/logs, and Android APKs are not committed or distributed. GitHub `master` unchanged.
