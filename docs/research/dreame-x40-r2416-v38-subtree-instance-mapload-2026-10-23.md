# Dreame X40 R2416 — v38 pre-Loop SubTree instances and repeated MapLoad audit

**Date:** 2026-10-23  
**Scope:** Private, read-only static inspection of SHA-256-pinned original firmware ELFs and previously collected matching runtime tree libraries. No robot access, firmware edits, MIOT/AVA writes, Valetudo+ code changes, or publication of proprietary binaries.

## Question carried over from v37

The generated `RobotNode` contains four important direct pre-Loop attachments labelled `MapLoad`, `RobotSysInit`, `StationSysInit`, and `RobotmodeInit`. v37 resolved the later `AlwaysSuccess` and `CountryGet` checks, but did **not** resolve whether those four initialization subtrees return running, success or failure on R2416. This pass distinguishes the node **type** from the **instance name** and checks other uses of the `MapLoad` instance name.

## Finding A: one shared SubTree node type, four distinct instance names

`liblethe_tree.so` at `0x58fcdc` contains the exact NUL-terminated string `SubTree`. The generated `RobotNode` code loads its address into the factory node **type** argument (`x0`) and loads a separate per-instance string into `x1`. The constructor then calls `child_node_factory_instantiateTreeNode()` (PLT `0x1c6620`) and adds the result to the control parent (`0x1c6900`).

| Direct pre-Loop slot | Instance (`x1`) | Instance preparation | Native factory call | Parent attachment |
|---:|---|---|---|---|
| 10 | `MapLoad` | `0x30db08`–`0x30db0c` | `0x30db18` | `0x30db24` |
| 11 | `RobotSysInit` | `0x30db44`–`0x30db48` | `0x30db54` | `0x30db60` |
| 12 | `StationSysInit` | `0x30dec8`–`0x30decc` | `0x30ded8` | `0x30e03c` |
| 13 | `RobotmodeInit` | `0x30e05c`–`0x30e060` | `0x30e06c` | `0x30e078` |

These are compiled **node-construction** operations, not calls to `MapLoad::tick()` or equivalent methods. The `StationSysInit` constructor is followed by an unconditional branch at `0x30dedc` to `0x30e034`, skipping C++ exception cleanup before its parent-attachment call. The address gap is therefore not evidence of an omitted node.

The common node type is an intentionally reused **suffix** of a longer read-only data string (`ClearFluctuationSubTree`). The generated assembly addresses exactly the `SubTree` suffix at `0x58fcdc`. Do not assume the whole longer string is the registered node name.

## Finding B: base factory registration and Blackboard initialization

The pinned `libbehaviortree_cpp.so` has a `SubTree` manifest string at `0xa9ae8`, referenced by its `BehaviorTreeFactory` constructor at `0x62c0c`–`0x62c10`; registration calls `registerBuilder` at `0x62c74`. The generated tree helper (`0x567e90`) calls `BehaviorTreeFactory::instantiateTreeNode` through PLT `0x1c6650` at `0x567f00`. The base factory's instantiation routine has explicit calls to `TreeNode::setBlackboard` (`0x5f638`) and `initializeOnce` (`0x5f650`).

These checks establish a **construction and initialization** chain. They do **not** identify the concrete tick implementation or the status outcomes for the four instances, nor prove that they were created/ticked on the running robot.

None of the four names appears as a matching `buildMapLoad`, `buildRobotSysInit`, `buildStationSysInit`, or `buildRobotmodeInit` **export** in this library's `.dynstr`. This is a bounded symbol-table observation; it does not imply that the subtrees are missing or that all their code must be externally named.

## Finding C: a second MapLoad instance construction

The exact `MapLoad` string at `0x585df8` has **two** direct ADRP+ADD references in the checked `.text` section:

1. `0x30db08`–`0x30db0c` — the pre-Loop node above, constructed at `0x30db18`.
2. `0x30e614`–`0x30e618` — a separate generated node constructed at `0x30e624`, attached at `0x30e630`.

The second instance is after the compiled root Loop attachment at `0x30e11c`. The surrounding code also constructs a neighbouring `MultMapRecover` node, but these instruction-order facts alone do not establish **why** the second MapLoad might execute, or which live map lifecycle state reaches it. Do not treat `MapLoad` as an exclusively one-time startup operation.

## Implications for station-wash research

The pre-Loop slots 10–13 remain genuine **potential progression gates**, because their parent `SequenceStarRoF` advances according to returned child statuses (v35). v38 does **not** identify their returned status or a live failure. The generated node **type/name distinction** and duplicate MapLoad construction show why searching for `buildMapLoad()` alone would be insufficient.

Separately, the presence of `StationWash.xml` in `RobotNode`, the registered native `StationWash` builder, and Blackboard forwarding (v29–v31) establishes compiled structural capability—not successful runtime ticking, special-push eligibility or physical rewash.

**Still unproven:** how the four named `SubTree` instances resolve to concrete tick paths; successful completion of each R2416 initialization child; an R2416-compatible source for `special_push_clean_dish` on the effective Blackboard; a normal turbidity result reaching `r2343_start_rewash`; a second physical dock wash.

The unrelated keys `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TurbidityResultFail`, and `r2343_start_rewash` must remain distinct.

## Reproducibility

The v38 script invokes the full v37/v36 verification chain before its own assertions, including five original-library SHA-256 pins, three runtime/original byte comparisons, and the effective `RobotNode` selector. It then verifies the four instance literals, five constructor/attachment pairs, the additional `MapLoad` reference, the `SubTree` registration, the factory calls, and the bounded export census.

```bash
python3 x40_r2416_v38_subtree_instance_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Keep `x40_r2416_v36_preloop_nodes_verify.py` and `x40_r2416_v37_countryget_gate_verify.py` alongside the v38 verifier, as included in the package. Expected terminal marker: `X40_V38_SUBTREE_IDENTITY_STATIC_PASS`. The result applies only to the exact pinned binaries. An intentionally tampered *private copy* of one runtime library must be rejected by the SHA/runtime comparison gate.

## Next bounded offline task

Trace the factory's **SubTree builder implementation and target-selector mechanism**, rather than guessing tick outcomes from instance names. Work from symbol/vtable/registration evidence to identify the concrete paths for `MapLoad`, `RobotSysInit`, `StationSysInit`, and `RobotmodeInit`. Keep pursuing a bounded R2416-specific `special_push_clean_dish` producer census separately. No further live collection or experimental write path is justified by this v38 result alone.