# Dreame X40 R2416 — v28 dynamic subtree construction and Blackboard propagation

**Date:** 2026-10-22  
**Scope:** Offline-only native-code investigation using the owner's SHA-256-pinned original R2416 binaries, the separately collected active tree-library copies, and the effective tree selector reported in v27. This research does **not** authorize or perform runtime changes, native injection, firmware patching, dock commands, MIOT writes, or live robot access. No vendor ELF, extracted runtime YAML, personal maps, secrets, or disassembly dumps are embedded here.

## Executive finding

v27 established that `RobotNode` is the configured tree selector and a registered compiled builder, but it searched only for **direct** `BL` calls to `buildStationWash()`. This v28 pass documents additional **dynamic tree-construction mechanisms**:

1. `node_lethe.so` implements `BtTask::BtTask(name, shared_ptr<BT::Blackboard>)` at `0x316410`. It constructs in-memory XML text wrapping a supplied name in a `<SubtreeCondition subtree_file_path="..."/>` node and calls `BT::buildTreeFromText(...)` at `0x316600`. The assembler code loads the existing supplied Blackboard holder as the third normal AArch64 argument (`x2`) to this call.
2. The generated `RobotNode` body of `liblethe_tree.so`, reached via `buildRobotNode()` (`0x312c6c`) and its generated-body entry (`0x30d8c0`), contains **six** direct `SubtreeCondition` node-name preparations which are each followed by `child_node_factory_instantiateTreeNode(...)`. These are compiled child-node construction sites, not proof that a node is ticked at runtime.
3. The original `libbehaviortree_cpp.so` **registers `SubtreeCondition` by that exact name in `BT::BehaviorTreeFactory::BehaviorTreeFactory()`** (`0x62edc..0x62f48`), via a `BT::SubtreeConditionNode` builder manifest and its `requiredNodeParameters()`. Its `BT::SubtreeConditionNode::onInit()` reads `subtree_file_path`, calls `BT::TreeNode::blackboard()` (`0x75b8c`) and supplies that Blackboard as argument `x2` to `BT::buildTreeFromFile` (`0x75bb0`) on a conditional branch. It also checks the registered tree-builders map (`0x75de8`). **This closes the default wrapper-name → built-in node-type registration mapping.**
4. Separately, `utility::SubtreeConditionOptNode::onInit()` in `liblethe_route_nodes.so` also reads `subtree_file_path`, uses `BT::TreeNode::blackboard()`, and conditionally calls `BT::buildTreeFromFile(factory, path, blackboard)` at `0x5b30bc`, with a separate tree-builder map lookup at `0x5b31c4`. This is a distinct implementation; it must not be identified with the default `SubtreeCondition` alias simply because it shares a parameter key.

**Remaining uncertainty:** The audit verifies the default `SubtreeCondition` builder mapping but does **not** prove whether plugin loading subsequently replaces or shadows it for the running robot, nor which subtree ID/file is selected by each generated node.

## Pins and evidence provenance

Five original ELF64/AArch64 SHA-256 pins are verified by the standalone verifier; three active `/tmp/lib/tree_lib/` copies are additionally compared byte-for-byte against the original archive members:

| ELF | SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The v27 collection confirms `behavior_tree_path: RobotNode` and active library path `/tmp/lib/tree_lib//`, which matches the original pinned tree libraries. A failed `RobotNode.xml` retrieval produced a zero-length local placeholder and is not an available vendor tree file. The v28 verifier reads only the two supplied ZIP files and never follows symlinks or extracts firmware members to disk.

## Instruction-level anchors (sanitized, no bulk disassembly)

| Native binary / site | Verified meaning |
| --- | --- |
| `node_lethe.so:0x31642c..0x316430` | Save the constructor's supplied name and `shared_ptr<Blackboard>` reference |
| `node_lethe.so:0x9d3380,0x9d3400` | In-memory wrapper prefix and suffix around a supplied subtree name |
| `node_lethe.so:0x3165f4..0x316600` | `x2` receives stored Blackboard argument; direct `BL` to `BT::buildTreeFromText` import |
| `liblethe_tree.so:0x30dc20,0x30e3b8,0x30ee48,0x30f554,0x30ff8c,0x3111f0` | Six `SubtreeCondition` child-node factory instantiation sequences in the compiled `RobotNode` generated body |
| `libbehaviortree_cpp.so:0x62edc..0x62f48` | Default factory registers literal `SubtreeCondition` with `BT::SubtreeConditionNode` manifest |
| `libbehaviortree_cpp.so:0x757b8,0x75b8c..0x75bb0` | Built-in onInit reads subtree-file parameter and forwards its node Blackboard into `buildTreeFromFile` |
| `liblethe_route_nodes.so:0x5b29b8..0x5b2a20` | Separate optimized implementation's `subtree_file_path` parameter retrieval |
| `liblethe_route_nodes.so:0x5b3098,0x5b30b4..0x5b30bc` | Obtain node Blackboard and pass it in `x2` to the conditional `buildTreeFromFile` call |
| `liblethe_route_nodes.so:0x5b31c4` | Read registered tree-builder map on a separate conditional path |

The direct-import call census for `BT::buildTreeFromText()` in `node_lethe.so` contains five `BL` sites: one `BtTask` site and the four earlier AVA constructor sites. The direct-import call census for `buildTreeFromFile()` in the pinned `liblethe_route_nodes.so` contains the onInit site above. These are bounded **specific-import** checks only; they are not proof there are no virtual, wrapped, or alternative tree builders.

## Updated causal picture

```text
R2416 effective setting: RobotNode                               [CONFIGURED]
       |
       v
liblethe_tree.so: registered buildRobotNode and compiled body      [COMPILED]
       |
       +-- 6 child instantiations of SubtreeCondition               [VERIFIED COMPILED]
       |        |
       |        ?  selection values and actual node registration
       |        v
       |    dynamic subtree construction                            [MECHANISM EXISTS]
       |
       ?  does any subtree select StationWash, and with which BB?
       v
registered buildStationWash(factory, Blackboard)                   [COMPILED]
       |
       ?  required R2416 special_push_clean_dish producer
       v
WashDonePrecess: failure marker + wash gate + special-push key      [COMPILED]
       |
       ?  actual dock wash control/actuation
       v
physical automatic mop rewash                                      [NOT SHOWN]
```

The original three-model initializer for `special_push_clean_dish` still excludes the configured R2416 identifier. Another producer or inherited Blackboard entry has not been demonstrated. The distinct keys `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, and `r2343_start_rewash` must continue to be tracked independently.

## Reproduce offline

```bash
python3 x40_r2416_v28_dynamic_subtree_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V28_DYNAMIC_SUBTREE_STATIC_PASS`. The verifier uses Python's standard library, validates complete ELF SHA-256 hashes, independently compares the three runtime tree libraries with original archive members, checks the observed root selector, exact compiled wrapper strings, instruction operands, direct call destinations, and six generated child-instantiation sequences. A modified library was separately rejected at the hash gate. This is a **static-code verifier**, not an operational test.

## Next constrained investigation

1. Verify whether the runtime plugin-registration sequence preserves the built-in `SubtreeCondition` mapping or installs another builder for that name. Treat `utility::SubtreeConditionOptNode` as distinct unless an explicit registration ties it to the same key.
2. Decode the six compiled `RobotNode` child-node parameter sets (only static key/type relationships), looking for a provable route to a `StationWash` tree ID without assuming that generated debug labels are selected IDs.
3. If the factory selection can be established, trace the Blackboard argument across that builder and station-wash tactics nodes. The shared runtime instance, trigger conditions, and physical actuator remain unverified until independently demonstrated.

**Safety boundary:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No additional robot pull or MIOT/AVA commands are justified by this result. Preserve the working Valetudo+ installation; do not publish vendor binaries or private device configuration.
