# Dreame X40 R2416 — v43 direct factory Blackboard lineage and BtTask call census

**Date:** 2026-10-23  
**Scope:** Private, read-only offline inspection of the owner's original SHA-pinned firmware archive and the separately collected matching runtime tree libraries. No robot, MIOT, AVA, firmware, Valetudo+, GitHub or network operations. The package contains no native vendor libraries, full disassembly, unredacted settings, passwords, device identifiers, camera images or maps.

## Executive result

There is a **direct native factory instantiation in the `ancp::AvaNodeRoute` constructor** that takes its Blackboard argument from the same `this+0x30` holder used by the map-operation writers studied in v42. At `node_lethe.so:0x355058`, the constructor calls the imported `BT::BehaviorTreeFactory::instantiateTreeNode(...)`. At `0x355010` it reloads the constructor receiver; at `0x355028` it supplies `[receiver+0x30]` as the AArch64 fifth argument `x4` for the `std::shared_ptr<BT::Blackboard>` argument.

This is a more direct compiled link than the four previously known `buildTreeFromText()` calls at `0x35511c`, `0x3552c8`, `0x3553f4`, and `0x3554e8`, which separately forward the same `+0x30` field as their third argument (`x2`). **It does not independently identify the tree-node name passed to the direct factory call** or prove the actual runtime `MapLoad` or `StationWash` Blackboard instance.

A second, corrective result is that the imported `BtTask` constructor has **one direct branch-link call site** in the scoped complete `node_lethe.so` `.text` code: `0x31697c`, inside `DebugTask::DebugTask()`. `DebugTask` forwards the Blackboard holder received in its own constructor to that `BtTask` constructor. Therefore the separate `BtTask` constructor is **not an established constructor of the active `RobotNode`**. An indirect caller, inlining, other module, or runtime remapping is not excluded by the direct-call census.

## Immutable source pins

| Original ELF | SHA-256 |
|---|---|
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The original-vs-runtime checks for the three tree plugins passed. The owner's private `setting.yaml` selects `behavior_tree_path: RobotNode` and `tree_lib_path: /tmp/lib/tree_lib//`; these values are observed configuration, not proof of live tick events. Full source inputs remain off GitHub.

## New proof A — direct `AvaNodeRoute` factory call

Addresses are static ELF virtual addresses, **not** commands to execute on the robot.

| Address | Verified action |
|---|---|
| `0x34c054` | Save `AvaNodeRoute` constructor receiver at `sp+0x68` |
| `0x34c088` | Form pointer to embedded Blackboard shared-pointer holder at `this+0xfa8` |
| `0x34c098` | Store that holder's address at `this+0x30` |
| `0x355010` | Reload constructor receiver into `x1` from saved stack slot |
| `0x355028` | Load `x4 = [x1+0x30]`; `x4` is the fifth normal AArch64 argument |
| `0x355050` | Reload first explicit factory argument, the node-name pointer (exact selected string unresolved) |
| `0x355054` | Reload factory receiver into `x0` |
| `0x355058` | Direct `BL` to `BT::BehaviorTreeFactory::instantiateTreeNode@plt` |

The ELF contains just this one **direct `BL` site to this specific imported factory PLT stub**. This bounded result does **not** rule out registration/factory activity via other functions, calls through pointers, or inline methods.

### Relationship to map writers

v42 establishes that `AvaNodeRoute::AppEditMap()`, `MT_ChangeMap()` and `MT_SetRunModeProcessSUB()` load the same class-member field `+0x30`. v43 now verifies that native factory construction is also explicitly supplied with that field. This is a compiled **member-field dataflow**, not a runtime pointer sample or a demonstrated `Start_Map_Load` set-before-first-tick event.

The separate `SlamControl+0x30` field and `BT::TreeNode::blackboard()` in tactics nodes remain distinct access paths. They must not be merged merely because their types or offsets look alike.

## New proof B — `BtTask` constructor's direct callers

The original `node_lethe.so` contains an exported `BtTask` constructor at `0x316410` and an imported PLT stub for it at `0x27d220`. A full `.text` census of AArch64 direct `BL` instructions to that **specific PLT stub** gives one site: `0x31697c` in `DebugTask::DebugTask()` (beginning `0x316940`). At `0x316968–0x31696c`, the constructor prepares the name as `x1` and forwards the incoming `DebugTask` Blackboard holder as `x2` to `BtTask`.

The `BtTask` constructor itself forwards its supplied Blackboard to `BT::buildTreeFromText()` at `0x316600`; however this constructor dataflow alone does **not** establish a call from ordinary `RobotNode` startup. Treat previous interpretations of this mechanism as *potentially relevant to debug tasks*, not proven main-tree runtime construction.

## Checks and limitations

The v43 standalone verifier:

- Runs v36–v42 regressions and enforces five SHA-256 pins and three runtime/original equality checks.
- Checks exact AArch64 instructions for receiver saving, holder creation, argument setup and imported factory dispatch.
- Rechecks the four prior `buildTreeFromText` holder-forwarding sites.
- Counts all direct branches to the *specific* factory, text-build and `BtTask` constructor PLT stubs in the pinned `.text` section.
- Refuses any mutated input hashes or changed expected instruction/callsite patterns.

**Not proven:** which node name is supplied to `instantiateTreeNode()` at `0x355058`, whether it is the running `RobotNode` instance or a different tree, whether that tree shares the effective first `MapLoad` Blackboard and receives `Start_Map_Load` before first tick, and whether the `StationWash` tactics-node Blackboard shares the same runtime state. The known `special_push_clean_dish` producer remains gated to other model identifiers; no R2416-compatible alternative or actual second dock wash has been shown. Static findings do not authorize the experimental CleanGenius writes.

## Offline reproduction

With the verifier and its v36–v42 dependencies in the same folder:

```bash
python3 x40_r2416_v43_factory_blackboard_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected success marker: `X40_V43_FACTORY_BLACKBOARD_STATIC_PASS`.

## Next research focus

1. Resolve the origin of the node-name reference supplied at the direct factory call (`0x355050`), distinguishing configured `RobotNode` from auxiliary initialization trees.
2. Identify when the root tree is ticked and how `Start_Map_Load` and station-wash nodes bind/remap the supplied Blackboard. Keep this static, offline-first.
3. Return to the separate R2416-specific `special_push_clean_dish` eligibility restriction before considering any physical rewash claims.

**Operational boundary:** No SSH to the robot, no MIOT/AVA publications or instrumented hooks, no firmware changes, no Valetudo+ modifications and no GitHub commits in this v43 pass. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.