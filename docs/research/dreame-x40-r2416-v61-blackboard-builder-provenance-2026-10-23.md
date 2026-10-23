# Dreame X40 R2416 — v61: native builder Blackboard provenance and per-node handles

**Date:** 2026-10-23  
**Method:** Offline read-only analysis of the five owner-provided original SHA-256-pinned AArch64 ELF libraries and byte-matched runtime copies of three tree libraries. No device access, runtime test, firmware modification, MIOT operation or repository write.

## Executive finding

`MopDirtyAccumulator::tick()` and tactics `CheckIfNeedReClean()` use the **same imported native `BT::TreeNode::blackboard()` API** to obtain a `shared_ptr<BT::Blackboard>` reference. The common `libbehaviortree_cpp.so` accessor resolves a compact per-node handle through a shared-pointer slot table. Four compiled native subtree builders (`RobotNode`, `StationWash`, `CleanSelectedAreas`, `FindNearbyMovablePoint`) call a common child-construction helper that retains and forwards the **incoming Blackboard reference** to `BT::BehaviorTreeFactory::instantiateTreeNode()`.

Two native builder placements explicitly create a `MopDirtyAccumulator` child: `CleanSelectedAreas` and `FindNearbyMovablePoint`. **No evidence establishes equality of the runtime Blackboard handles of the producer and tactics consumer.** Identical API calls, compatible types and common builder convention do not by themselves demonstrate that these separately constructed nodes address the same `BlackboardLocal`, or that they run in the same tree instance at the required time.

## Instruction-level evidence

| Library | Address | Verified meaning |
|---|---:|---|
| `liblethe_tree.so` | `0x3c0d50–0x3c0d60` | `CleanSelectedAreas` builds child identified by literal `MopDirtyAccumulator` and invokes the factory child helper |
| `liblethe_tree.so` | `0x416380–0x416390` | `FindNearbyMovablePoint` has the second child placement for the same literal |
| `liblethe_tree.so` | `0x567ba0`, `0x567bd8` | `init_fac` saves incoming `shared_ptr<Blackboard>` reference in the child-builder frame |
| `liblethe_tree.so` | `0x567ec8`, `0x567ee8`, `0x567f00` | Child helper retrieves that saved reference and passes it as the fifth argument (`x4`) to `instantiateTreeNode` |
| `liblethe_tree.so` | `0x312ca0`, `0x358574`, `0x3bfe84`, `0x4158a4` | `RobotNode`, `StationWash`, `CleanSelectedAreas`, `FindNearbyMovablePoint` builders invoke common `init_fac` |
| `libbehaviortree_cpp.so` | `0x4f8f0` | `BT::TreeNode::blackboard()` loads each node's handle from `this+0x18` |
| `libbehaviortree_cpp.so` | `0x4f8f4`, `0x4f8fc` | Rejects invalid handle bit and extracts a 7-bit slot index |
| `libbehaviortree_cpp.so` | `0x4f900–0x4f908` | Resolves a 16-byte `shared_ptr` slot (index shifted by 4) and returns its address |
| `liblethe_route_nodes.so` | `0xb47640`, `0xb478d0` | `MopDirtyAccumulator::tick()` calls imported `TreeNode::blackboard()` |
| `liblethe_tactics_tree.so` | `0x252f40`, `0x252fdc` | `CheckIfNeedReClean()` calls the same imported `TreeNode::blackboard()` before turbidity key operations |

ELF relocation identities (each `R_AARCH64_JUMP_SLOT`, type **1026**, addend 0):

- `liblethe_tree.so`, slot `0x7b17b8`: `BT::BehaviorTreeFactory::instantiateTreeNode(..., std::shared_ptr<BT::Blackboard> const&)`.
- `liblethe_route_nodes.so`, slot `0x1240f20`: `BT::TreeNode::blackboard() const`.
- `liblethe_tactics_tree.so`, slot `0x3c11d8`: `BT::TreeNode::blackboard() const`.

These names are independently resolved from the binary relocation tables rather than inferred from nearby strings. The checked child-builder helper forwards a **reference** to the incoming `shared_ptr`, not a newly identified Blackboard allocation at that point. Whether its callers pass the **same** reference across the producer and wash-related subtrees requires further verification.

## Interpretation and limits

1. **Proven:** `MopDirtyAccumulator` is instantiated within two named native subtree builders; the builders use the shared helper and its incoming Blackboard reference.
2. **Proven:** The writer and tactics consumer both use the same exported accessor API; the accessor obtains the shared pointer through each node's compact handle and a slot table.
3. **Proven from v59–v60 regressions:** the writer contains four guarded setters for `turbidity_clean_area`, and the examined readers have a double-to-float compatibility path.
4. **Not proven:** Both nodes carry equal handle indexes, receive the same actual `shared_ptr` target, survive in the same dynamically constructed `RobotNode` tree, or execute in the expected producer-before-consumer order. The static binary does not encode live pointer equality.
5. **Not proven:** A corresponding on-device writer for `special_push_clean_dish` on R2416. The previously identified literal setter is model-gated to other models; indirect or computed producers remain possible.
6. **Not proven:** A physical second mop wash on X40 R2416. The v54 consume-before-eligibility branch remains a plausible obstacle, not an observed event.

## Reproduce safely

Extract the full audit ZIP and run:

```bash
python3 x40_r2416_v61_blackboard_builder_provenance_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected v61 markers:

```
X40_V61_BUILDER_BLACKBOARD_PROVENANCE_STATIC_PASS
X40_V61_BUILDER_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V61_HANDLE_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V61_CONSUMER_INSTRUCTION_TAMPER_REJECTION_PASS
```

The standard-library-only verifier runs the inherited v54–v60 checks, exact instruction and branch anchors, relevant imported-symbol relocations, and three separate altered-instruction rejection tests. Hash-pinned firmware is **input** only; the package does not distribute it.

## Recommended v62

Establish the chain of Blackboard forwarding through `RobotNode`, the `SubtreeCondition`/`StationWash` boundary, and the two builders containing `MopDirtyAccumulator`. Distinguish *passed pointer reference* from *new Blackboard allocation* and from *actual node handle equality*. In parallel, continue bounded R2416-specific `special_push_clean_dish` producer search. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; do not perform firmware or MIOT writes.