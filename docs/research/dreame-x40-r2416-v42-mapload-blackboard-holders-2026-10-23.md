# Dreame X40 R2416 — v42 Start_Map_Load Blackboard-holder provenance

**Date:** 2026-10-23  
**Status:** SHA-pinned, read-only offline static analysis; no robot, network, MIOT, AVA, firmware or Valetudo+ operations. Original vendor ELFs and unredacted configurations must remain private.

## Summary

The v41 exact-key census established twelve typed `BT::Blackboard::set<bool>` instruction sites and one additional, unclassified `Start_Map_Load` literal reference in `node_lethe.so`. v42 classifies the latter as a virtual `set` dispatch in `ancp::AvaNodeRoute::MT_SetRunModeProcessSUB()`, subject to the concrete runtime Blackboard implementation. It also checks the class-member and tree-node accessor lineages used by representative writers. This **does not** prove that the initial `MapLoad` subtree sees the key when first ticked.

## Checked firmware provenance

- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`
- `liblethe_route_nodes.so`: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

The three active tree libraries in the v27 collection match original copies byte-for-byte. The effective private `setting.yaml` selects `RobotNode` and `/tmp/lib/tree_lib//`. These are configuration observations, not runtime tick events.

## New proof A — the previously unclassified `Start_Map_Load` reference

In `node_lethe.so`, `ancp::AvaNodeRoute::MT_SetRunModeProcessSUB()`:

| ELF VA | Instruction role |
|---|---|
| `0x447e1c` | Load holder pointer from `AvaNodeRoute+0x30` |
| `0x447e20–0x447e24` | Prepare literal `Start_Map_Load` |
| `0x447e2c` | Load stored Blackboard pointer through the holder |
| `0x447e34–0x447e38` | Load implementation pointer and guard against null |
| `0x447e44` | Prepare scalar value `1` (type is not independently established) |
| `0x447e50` | Supply key argument |
| `0x447e54` | Load vtable slot `+0x20` |
| `0x447e60–0x447e64` | Supply payload pointer, dispatch indirect call |

The earlier v18 audit matched slot `+0x20` to `set(key, SafeAny::Any)` on the `BlackboardRobinMap` and `StaticBlackboardRobinMap` implementations. The v42 verifier independently anchors the dispatch instructions and the exact literal reference. A different runtime concrete implementation or receiver remains unproven; do **not** treat the scalar `1` as a proven typed Boolean write. The call is conditional and is not a startup-execution observation.

With this additional virtual-set boundary, the scoped v41 direct-literal census comprises **12 typed `set<bool>` sites plus one virtual-set site**, not necessarily 13 executions, and not a census of dynamically generated keys.

## New proof B — three different access families

| Family | Static findings | Scope |
|---|---|---|
| `AvaNodeRoute` | Five `AppEditMap` typed setters each explicitly load the member at `+0x30`; `MT_ChangeMap` uses the same holder for `contains`; the newly classified Matter run-mode path uses it for virtual `set`. v22/v23 also documented constructor initialization of this member and its use in selected tree builds. | A structural **class-member** lineage, not live pointer equality with `MapLoad` |
| `SlamControl` | `CheckRelocDeal()` contains a typed `set<bool>` and a typed `get<bool>` referencing the `+0x30` field of its own receiver. | A distinct class; identical offset does **not** establish aliasing with `AvaNodeRoute+0x30` |
| Tactics behaviour-tree nodes | `MultMapRecover::StandbyAndReloadMap()`, `ChargingReloc::tick()` and `UpdateReuseAppMap()` each call `BT::TreeNode::blackboard()` immediately before their typed `set<bool>` paths. | Node-associated Blackboard accessor; the effective instance and potential parent/remapping remain unverified |

The verifier checks representative register/field loads, direct typed setters, two `SlamControl` member loads, the separate tree-node accessor calls, original library pins and regressions through v41. It does **not** follow arbitrary intervening calls, count actual invocations, or resolve all class instances. `SaveMap` and `DeleteMap` remain included in the v41 typed-call census; v42 does not claim full interprocedural holder provenance for those branches.

## Relation to the first `MapLoad` gate

The generated initial `MapLoad` subtree begins with `BlackboardContains(key=Start_Map_Load)` (v40). `AvaNodeRoute`'s `+0x30` member is supplied to several tree constructions (v23), but none of those facts alone proves that the initial `RobotNode` / `MapLoad` instance shares the *same live Blackboard object* or that a writer executes **before the first tick**. An earlier completion status, or later map-edit event, cannot be inferred from compiled availability.

The v20–v21 finding about `special_push_clean_dish` also remains unchanged: the known `ProcessModelInfo()` producer is gated to other model IDs, and no R2416-compatible writer has been established. `Start_Map_Load` is **not** an alias for `special_push_clean_dish`, `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, or `TurbidityResultFail`.

## Reproduce offline

Unpack the v42 audit ZIP, with its included v36–v41 dependency checkers, and run:

```bash
python3 x40_r2416_v42_mapload_holder_lineage_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V42_MAPLOAD_BLACKBOARD_HOLDER_STATIC_PASS`. The script fails on mismatched original/runtime SHA pins or any expected instruction, member load, literal preparation, or call target. It requires only Python's standard library, reads locally provided archives, and does not extract or execute vendor ELF files.

## Next decision

The highest-value remaining static task is to identify exactly which `BtTask` / `RobotNode` object is instantiated for the active task and whether its Blackboard argument is the `AvaNodeRoute+0x30` holder *through construction and subtree remapping*. Once pointer lineage is grounded, determine when `Start_Map_Load` is written relative to initial `MapLoad`, without touching the robot. Do not enable `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS`, publish AVA messages or force dock washing. Physical automatic rewash and an R2416-native `special_push_clean_dish` producer remain unproven.