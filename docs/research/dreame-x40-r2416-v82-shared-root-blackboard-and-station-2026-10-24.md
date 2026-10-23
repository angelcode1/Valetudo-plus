# X40 R2416 — v82 shared root Blackboard and station-node wiring

**2026-10-24 · Offline static research only.** All results come from the user's original privately retained SHA-pinned ELF archive. No robot access, MIOT writes, firmware install, proprietary binary upload, map, token, or device secret.

## Main finding

The previous v81 path from MIOT 4:50 → STATE_TO_LOGIC → registered app-status callback → typed `Blackboard::set<int&>` has been linked to **native root Blackboard propagation into behaviour-tree construction**. In `node_lethe.so`, `AvaNodeRoute` embeds a root Blackboard pointer at `this+0xfa8`, stores it as `this+0x30`, and passes `[route+0x30]` as the third argument to **four** `BT::buildTreeFromText` calls. Its `StateShowAndSave` app-status receiver copies the same root reference from the route's `+0x30` slot into its own `+0x30` slot; the registered parser writes `smart_hosting_switch`, `smart_auto_mop_switch`, and `smart_auto_wash_switch` using typed integer Blackboard setters.

The shared `libbehaviortree_cpp.so` `BT::buildTreeFromText` function forwards its incoming shared-Blackboard argument to `BT::XMLParser::instantiateTree`. The tactics-tree plugin registers `RobotTree` with the factory; `RobotTree` registers `StationHandle` nodes; and `StationHandle::SweepStationContorl::TurbidityRecleanAndRewashSet()` obtains the station node's current Blackboard using `BT::TreeNode::blackboard()` three times, then evaluates the three previously verified Smart switch keys.

**Bounded conclusion:** there is a compiled path propagating the *same root Blackboard* from settings callback ownership into top-level tree instantiation. It makes shared effective switch values plausible and is stronger than matching key names, but **it does not prove the runtime `StationWash` subtree node uses the identical Blackboard pointer**. Subtrees may be remapped/inherited and the v65–v66 research established conditional borrowed/cached subtree logic. Registration also does not establish active instantiation.

## Original native anchors

| Library | VA(s) | Pinned observation |
|---|---|---|
| `node_lethe.so` | `0x34c088`, `0x34c098` | `AvaNodeRoute` root Blackboard pointer from `this+0xfa8` stored at `this+0x30` |
| `node_lethe.so` | `0x88d130`, `0x88d13c` | `StateShowAndSave` copies the route Blackboard reference to its own `+0x30` |
| `node_lethe.so` | `0x88d404`, `0x890334–0x890360` | Registered app-status callback uses root reference and typed `Blackboard::set<int&>` |
| `node_lethe.so` | `0x355114→0x35511c`, `0x3552c0→0x3552c8`, `0x3553e8→0x3553f4`, `0x3554dc→0x3554e8` | Four `buildTreeFromText` calls load root `[route+0x30]` into argument register `x2` |
| `node_lethe.so` | `0x350f00` | `BehaviorTreeFactory::registerFromPlugin` call |
| `libbehaviortree_cpp.so` | `0x70a3c`, `0x70a6c`, `0x70a84` | Tree builder forwards its passed shared Blackboard pointer to `XMLParser::instantiateTree` |
| `liblethe_tactics_tree.so` | `0xd166c`, `0xd0d8c` | Plugin registers `RobotTree`, which registers `StationHandle` |
| `liblethe_tactics_tree.so` | `0x24e61c`, `0x24e6a4`, `0x24e72c` | Station `TurbidityRecleanAndRewashSet()` reads node's `TreeNode::blackboard()` three times |
| `libbehaviortree_cpp.so` | `0x4f8f0–0x4f908` | `TreeNode::blackboard()` reads a node-configuration reference; it is not an unconditional global singleton |

Original SHA-256 hashes:
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

## Reproducible offline test

The user's separately delivered sanitized `X40-R2416-v82-sanitized-shared-root-blackboard-20261024.zip` contains a Python-standard-library `x40_r2416_v82_root_blackboard_bridge_verify.py`, a longer technical report and README. It loads only the original private `X40-R2416-v62-readonly-20261023T051829Z.zip` in memory, pins all three ELF hashes, validates the instruction/call sites and verifies **29 independent one-byte mutation refusals**.

```text
X40_V82_ROUTE_ROOT_TO_APP_STATUS_BLACKBOARD_STATIC_PASS
X40_V82_ROOT_SHARED_BLACKBOARD_TO_FOUR_BEHAVIOR_TREES_STATIC_PASS trees=4
X40_V82_STATION_PLUGIN_REGISTRATION_CHAIN_STATIC_PASS
X40_V82_STATION_TREENODE_BLACKBOARD_READER_STATIC_PASS reads=3
X40_V82_BT_XML_SHARED_ROOT_INSTANTIATION_STATIC_PASS
X40_V82_INSTRUCTION_MUTATIONS_REJECTED count=29
LIMIT: actual station subtree node Blackboard instance, remapping/cache and physical rewash NOT demonstrated
```

## Open verification gates

1. Recover the **active** station XML and the `NodeConfig` Blackboard reference used by its `SweepStationContorl` node. Distinguish direct root inheritance from remapped/subtree-copy or cached child.
2. Confirm the effective runtime Smart switch values seen at that consumer without guessing or modifying native auto-switch settings; the MIOT `SmartAutoMop=-1` readback still has unknown semantics.
3. Connect genuine turbidity / floor-dirt evidence to `r2343_start_rewash`, actual subsequent station commands and a **second physical wash**, and separately prove native area reclean.

The previously verified live Valetudo+ **v74 stays untouched**: native SmartHost restored to 0, exact baseline retained, separate experimental write gate `writeGateOpen=false` after launcher revert and reboot. Preserve recovery binaries, the original launcher/config and vendor files. **No new on-robot test or firmware write is warranted from v82.**
