# Dreame X40 R2416 — v29 RobotNode → StationWash parameter audit

**Date:** 2026-10-22  
**Scope:** Offline-only analysis of the owner's hash-pinned firmware binaries and independently collected active runtime tree libraries. No live robot access, MIOT/AVA commands, firmware writes, hook installation, or Valetudo+ changes were made. This report contains no proprietary ELF, unredacted settings, maps, camera content, or full disassembly.

## Executive result

**New confirmed static connection:** In the generated native `RobotNode` builder, the `SubtreeCondition` child instantiated at `liblethe_tree.so:0x30ee48..0x30ee58` is constructed from a **two-element `ConstStr` parameter-pair table** at `0x6f8350`. The values are exactly:

- `expand_in_logger` = `true`
- `subtree_file_path` = `StationWash.xml`

The table's `StationWash.xml` string pointer is `0x58eb2a` with length 15. The generated code supplies two pairs to its vector-construction helper (`0x2b390c`) and passes the resulting vector to `child_node_factory_instantiateTreeNode@plt` (`0x1c6620`) with node type `SubtreeCondition`. This is an actual compiled child-node construction site, not merely a string match.

The same SHA-pinned library also registers `StationWash` (no `.xml` suffix) to a native `buildStationWash` callback at `0x358540` through a verified GOT relocation (`0x7b1c50`); see v23. The compiled built-in `SubtreeConditionNode::onInit()` implementation has file-loading and registered-builder paths; see v28. **This does not independently establish that the file parameter resolves to that specific callback in a live job**, since the final conditional branch and effective runtime plugin registration are unverified.

## Provenance

The supplied effective `setting.yaml` reports `behavior_tree_path: RobotNode`, `tree_lib_path: /tmp/lib/tree_lib//`. The three active tree-library files copied from `/tmp/lib/tree_lib` match the archived originals byte for byte. The v29 verifier enforces all five pinned original ELF hashes and the three live/original byte comparisons, then repeats the v28 factory/Blackboard checks.

| Binary | SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

## Six *direct literal-preparation* sites

Each site has two `ConstStr` pairs. All share `expand_in_logger=true` and have the following distinct `subtree_file_path` values:

| Native literal preparation | Pair-table VA | `subtree_file_path` value |
| --- | --- | --- |
| `0x30dc20` | `0x6fd0d0` | `PlanningReuseRestartCleaning` |
| `0x30e3b8` | `0x6ee190` | `LongTimePauseStrategy.xml` |
| `0x30ee48` | `0x6f8350` | **`StationWash.xml`** |
| `0x30f554` | `0x6f7ff0` | `AlwaysSuccess.xml` |
| `0x30ff8c` | `0x6edab0` | `SearchChargeEnding` |
| `0x3111f0` | `0x6facf0` | `LabOldTestIndex` |

**Correction to an over-broad reading of the v28 count:** Six is **not** a count of *all* `SubtreeCondition` instantiations in the compiled RobotNode. Immediately after the `StationWash.xml` instantiation, code reuses a previously prepared callee-saved name register (`x21`) at `0x30ee80..0x30ee8c`, with another table at `0x6f8470` supplying `subtree_file_path=RobotDropCharger`. The v28 six-site census covered *direct ADRP+ADD preparations of the literal node name*, not register-reuse sites. The v29 verifier explicitly checks this additional example; an exhaustive control-tree reconstruction would require additional interprocedural/stack-aware analysis.

## What is established, and what remains open

Established from the SHA-pinned binaries:

1. `RobotNode` is the R2416 effective selector in the collected `setting.yaml`, and its registered native builder exists (v27).
2. A generated `RobotNode` child-instantiation site supplies the exact parameters `SubtreeCondition(subtree_file_path="StationWash.xml", expand_in_logger="true")` (new v29 result).
3. Built-in `SubtreeCondition` registration, a conditional build-from-file path with forwarded node Blackboard, and a separate `StationWash` registered builder exist (v23/v28).
4. The original/live tree-library hashes match; no newer runtime tree build needs reverse engineering for this sample.

Still **not** established:

- Whether the effective runtime `SubtreeCondition` registration is the built-in one or has been shadowed by a plugin.
- Whether the `StationWash.xml` parameter is actually resolved through the in-binary `StationWash` builder rather than through a conditional file path in the running system.
- Whether this generated node is ticked for ordinary R2416 cleaning, or with which runtime Blackboard instance and scope.
- An R2416-reachable producer of the required `special_push_clean_dish` key. Its only identified literal setter remains model-gated to three *other* model IDs (v20/v21).
- A successful chain from normal turbidity measurement through `TurbidityResultFail`, wash gate, `special_push_clean_dish`, `r2343_start_rewash`, to a **physical extra dock wash**.

Do not alias `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, and `r2343_start_rewash`: the keys have independently verified distinct uses.

## Offline reproduction

```bash
python3 x40_r2416_v29_robotnode_stationwash_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V29_ROBOTNODE_STATIONWASH_PARAMETER_PASS`. The verifier is self-contained and uses only Python standard library. It reads the input archives in memory, validates the five ELF SHA-256 pins and runtime/original byte equivalence, reproduces v28 tree factory checks, decodes seven specific fixed parameter-table sites with AArch64 operand checks, and rechecks the registered `StationWash` callback using an ELF relocation. Successful verification proves a **compiled static relationship**, not any actuator response or runtime ability to rewash. An intentionally altered library is rejected at the hash gate.

## Recommended v30 work (offline first)

1. Analyze `BT::SubtreeConditionNode::onInit()` and any plugin registration overrides to resolve the branch from parameter `StationWash.xml` to a registered compiled tree-builder or file-loader. Avoid assuming `StationWash.xml` and `StationWash` automatically alias.
2. Recover the static parent-chain context for the `0x30ee48` node within generated `RobotNode`, accounting for native depth and control/decorator child operations; do **not** present the six direct-literal sites as a complete tree.
3. If the factory path is resolved, trace its Blackboard origin to `WashDonePrecess` and evaluate whether any **R2416-compatible** key producer can satisfy `special_push_clean_dish`.
4. Do not enable `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS`; keep it `0`. No live robot or MIOT/AVA write tests are justified by v29.

**Repository handling:** Commit only this sanitized report and its standalone verifier if authorized. Do not upload original ELFs, proprietary configuration, runtime TAR/ZIP collections, credentials or disassembly dumps to public GitHub.
