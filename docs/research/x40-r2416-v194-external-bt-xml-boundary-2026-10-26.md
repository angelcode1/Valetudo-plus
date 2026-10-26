> **CORRECTION (v195, 26 October 2026):** This report accurately verifies *compiled fallback* XML path and plugin mechanisms, but its next-step suggestion to obtain `RobotNode.xml` overlooked earlier v27/v44 findings. The previously collected R2416 `setting.yaml` actually selected native factory ID `RobotNode`, and `liblethe_tree.so` contains a registered compiled `RobotNode` builder. The external XML is **not a prerequisite** for reconstructing that generated tree. See [`v195 native RobotNode corrigendum`](x40-r2416-v195-native-robotnode-corrigendum-2026-10-26.md) before applying the collection guidance below. The 2026-10-26 v194 test evidence remains valid in its bounded scope.

# X40 R2416 v194 — Verified external behavior-tree XML configuration boundary

**26 October 2026 — offline native analysis only.** Private, user-provided original R2416 source ELFs: `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`; `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Neither original ELF, robot files, nor video screenshots are committed or included in the companion ZIP.

## Concrete compiled host configuration

The host binary `node_lethe.so` at `Parameter::LOAD_behavior_tree_path(YAML::Node&)` (`0x2c4040`) reads YAML key `behavior_tree_path` from literal VA `0x9ce460`. Its fallback branch references `cleanbot_pro/RobotNode.xml` at `0x9ce478` and calls `YAML::Node::Assign(char const*)` at `0x2c4194`. The active deployed YAML value is **not known**. Fallback does not prove the file is present at that path.

Similarly `Parameter::LOAD_tree_lib_path` (`0x2c44c0`) reads `tree_lib_path`, fallback literal `/usr/lib/tree_lib` at VA `0x9ce4a8`, and assigns it at `0x2c4614`. This is a plugin-library-directory default, **not** evidence that the XML files live there.

The host's `BtTask::BtTask` constructor has a compiled XML wrapper beginning at `0x9d3380`; at `0x316600` it calls `BT::buildTreeFromText` through PLT `0x2753c0`. Four literal XML root **prefixes** are present as plain bytes in this host ELF, including wrappers for a subtree, `ReuseTree.xml`, `GridmapInit` and `TypeInterfaceInit`. These wrappers are not the full `RobotNode.xml` tree and are not an authoritative configuration of the production task scheduler.

## Native route-node side

In `liblethe_route_nodes.so`:
- Exported `BT_RegisterNodesFromPlugin` at `0x48cc80` directly branches to the `route_bt_nodes_plugin::RegisterNodes` PLT at `0x43f9b0`.
- `utility::SubtreeConditionOptNode::onInit` at `0x5b29b0` constructs string parameter `subtree_file_path` from VA `0xf9e498` and calls `BT::TreeNode::getParamImpl<std::string>` at `0x5b2a20` (PLT `0x44e820`).
- `basic_nodes::XmlControl::onInit` at `0x5e6880` acquires parent Blackboard at `0x5e6890` and calls `setBlackboard` on its child at `0x5e689c`, followed by child initialization. Shared-Blackboard *setup code* is proven, not a live sharing relationship among stain/reclean nodes.
- Literal names `RobotNode.xml` and `cleanbot_pro/RobotNode.xml` also occur in the route ELF.

Native registration and XML subtree parameters identify the **configuration boundary** needed to understand node ordering and port remapping. They do **not** show that `GetNextDynamicObstaclesArea`, `SetExtraCleanArea`, or `AiStainCheck` execute together. In particular, `next_dynamic_obstacles_point` has no proven downstream task-start binding simply because it exists on the Blackboard.

## Negative findings and next research step

Not recovered: the active YAML value; actual deployed root `RobotNode.xml`; imported subtrees; XML node order / `{port}` mappings; an AI-stain to task-dispatch transition; a new physical mop or vacuum pass. The v165 spatial revisits remain unclassified. The effective XML composition may reside in files outside these ELF bytes, so repeated direct-string scans of the same route library cannot close that gap.

Next: **optionally** identify the actual tree files with strictly read-only user-run access, privately inspect root and referenced subtree XML, and statically trace named nodes/ports into the native task-start entry. No robot access or activation was done in v194. No blanket interpretation of fallback paths as active runtime paths.

## Reproducibility

Companion **self-contained** offline ZIP `X40-R2416-v194-sanitized-external-bt-xml-boundary.zip`, SHA-256 `c8d2b952cd0a77d13d70e83c26e31861e0203e4fd259383ef7de6800f7f92ed5`. It includes the complete v184–v194 stdlib verifier chain, tests, the two-ELF v194 verifier, native report, sanitized results, checksum manifest and a clearly labeled *optional read-only* XML-discovery guide.

- Original two ELFs: **258 tests passed**.
- Fresh ZIP without originals: **216 tests run — 120 passed, 96 skipped**.
- **39 extracted file checksums passed**. The ZIP has 40 files including the SHA256SUMS file.
- Mutation tests reject changed config literal constructions, YAML default assignment, `BT::buildTreeFromText` call, plugin entry, parameter read and Blackboard-sharing call.
- No original binary or full XML is copied or redistributed.

Working Valetudo+ v74 remains intact; `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; `master` untouched.
