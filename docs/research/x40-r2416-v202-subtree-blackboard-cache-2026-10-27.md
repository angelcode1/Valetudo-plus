# X40 R2416 v202 — fresh versus cached subtree Blackboard binding

**27 October 2026.** Owner-private R2416 native ELF analysis, offline and read-only. Based on the corrected v195 native-`RobotNode` selection and verified v197–v201 native turbidity/station evidence. The robot and `master` were not changed; private binary/configuration bytes are excluded.

## New verified distinction

In the exact original `libbehaviortree_cpp.so` (SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`), `BT::SubtreeConditionNode::onInit()` begins at `0x757b0`, length **4112 bytes**. Its cached-root branch is distinct from the two fresh construction branches:

- At `0x75ac4`, the node tests a cached tree-object pointer at entry offset `+0x40`. A non-null pointer leads through `0x75acc` to the cached root and `0x75ad0`, which stores that root at the current node's `+0x20` field. The checked `CBZ` at `0x75ac8` instead branches to fresh build at `0x75b78` when the cached pointer is absent.
- Fresh file-backed construction acquires `TreeNode::blackboard()` at `0x75b8c`, forwards it as the third argument `x2` at `0x75ba0`, and invokes `buildTreeFromFile()` at `0x75bb0`.
- Fresh native registered-builder construction acquires `TreeNode::blackboard()` at `0x75f68`, forwards it in `x2` at `0x75f8c`, and invokes the registered callback indirectly at `0x75f9c`.
- The common fresh child factory `BT::BehaviorTreeFactory::instantiateTreeNode()` calls `TreeNode::setBlackboard()` at `0x5f638` (**PLT `0x398d0`**) before calling `TreeNode::initializeOnce()` at `0x5f650` (**PLT `0x398c0`**).
- In `TreeNode::setBlackboard()`, `0x5060c–0x50614` loads the stored slot pointer, compares it with the incoming pointer, and takes the equality branch directly to `0x506ac`. This identifies compiled same-object handling; it does **not** establish the live pointer value or equality between route and station controller.

The bound **direct-`BL` census** of `SubtreeConditionNode::onInit()` found **zero direct calls** to the `setBlackboard` implementation (`0x505b0`) or its checked PLT stub (`0x398d0`). The cached-root attach branch itself contains no direct Blackboard-get/bind call. This negative result covers precisely that function and those direct call targets; it is **not a proof against indirect calls, different lifecycle hooks, or runtime rebinding elsewhere**.

## Relation to R2416's compiled StationWash chain

- The configured native `RobotNode` root receives `AvaNodeRoute+0x30` Blackboard via host `buildTreeFromText()` at `0x3552c0–0x3552c8` (v195).
- `liblethe_tree.so` contains a generated `SubtreeCondition(subtree_file_path="StationWash.xml")` child at `0x30ee3c–0x30ee58` and registers a native `StationWash` builder.
- The native `buildStationWash` constructor calls `init_fac` at `0x358574`. Its shared child helper forwards the saved incoming Blackboard reference in `x4` to `instantiateTreeNode` at `0x567ee8–0x567f00` (previous v61–v62 plus v202 replay).
- Host `StationInfoProcessSUB` can publish `station_info_sub` through the route Blackboard, while `SweepStationContorl::InitTable` reads `station_info_sub` from its own node Blackboard (v201). **Equality of these actual live objects remains unknown.**

**Critical interpretation boundary:** The fresh path has explicit binding; the cached path attaches an existing root. Neither establishes that a cache was used on the live R2416, that a cache held stale state, or that the station controller did/did not receive `station_info_sub`. There is no live subtype, calibration choice, physical extra dock wash or AI-stain-triggered cleaning pass in this evidence. Do not treat a plausible stale-cache mechanism as an observed bug.

## Offline verification and next step

The owner-private source binaries are SHA-pinned; the v202 source-only verifier adds **88 exact AArch64 instruction anchors across four libraries** and **20 decoded branch/call edges** on top of the passing v197–v201 regressions. **10 focused tests passed**, including altered-ELF rejection, changed opcode/branch rejection, scoped direct-call census, and create-only report refusal. The earlier chain rechecks five original ELF SHA-256 fingerprints and saved-byte digests of **18+7** collector payloads. The source-only offline ZIP includes the complete verifier chain and tests, with no proprietary ELF or raw private settings.

The next useful offline gate is the **cache entry's producer/invalidation lifetime** and the root's node-handle assignment across subtree reuse, not another broad robot collection. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No physical reclean or rewash is claimed.
