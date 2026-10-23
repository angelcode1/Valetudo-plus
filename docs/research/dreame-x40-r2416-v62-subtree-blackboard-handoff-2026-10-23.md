# Dreame X40 R2416 — v62: subtree Blackboard handoff and cache boundary

**Date:** 2026-10-23. **Scope:** Offline, read-only, SHA-pinned original firmware and byte-matched active tree libraries; no robot communication, MIOT write or firmware modification.

## Executive finding

The configured `RobotNode` wrapper forwards `AvaNodeRoute+0x30` Blackboard into `BT::buildTreeFromText()`. Both `buildTreeFromText()` and `buildTreeFromFile()` pass their incoming Blackboard to `XMLParser::instantiateTree()`. The compiled `RobotNode` contains a `SubtreeCondition(subtree_file_path=StationWash.xml)` child. Its resolver has two **conditional** builder routes, both of which obtain the wrapper node's Blackboard: a file-based `buildTreeFromFile()` route and an indirect registered-builder route. The registered native `StationWash` builder, and the separate `CleanSelectedAreas` / `FindNearbyMovablePoint` builders containing `MopDirtyAccumulator`, use the same child-instantiation convention.

**Critical limit:** These facts establish source-level pointer/reference forwarding at specific interfaces, **not equality of live Blackboard targets between producer and wash consumer**. Another `SubtreeCondition::onInit()` branch attaches a cached root without a fresh on-branch Blackboard accessor/rebind. Treat reuse differently from construction.

## Instruction evidence

| ELF and address | Verified behaviour |
|---|---|
| `node_lethe.so:0x3552b4–0x3552c8` | Pass retained route Blackboard into configured text-wrapper builder |
| `node_lethe.so:0x3552d8` | Retain built tree root at route field `+0xf48` |
| `libbehaviortree_cpp.so:0x70a3c,0x70a6c,0x70a84` | Text tree forwards incoming x2 to `XMLParser::instantiateTree()` |
| `libbehaviortree_cpp.so:0x7025c,0x7028c,0x702a4` | File tree likewise forwards Blackboard |
| `liblethe_tree.so:0x30ee3c–0x30ee64` | Compiled `RobotNode` → `StationWash.xml` condition subtree |
| `libbehaviortree_cpp.so:0x75b88–0x75bb8` | Resolver file branch gets wrapper Blackboard and forwards as x2 |
| `libbehaviortree_cpp.so:0x75f64–0x75f9c` | Resolver native callback branch gets wrapper Blackboard and forwards as x2 |
| `liblethe_tree.so:0x358574,0x567ec8,0x567ee8,0x567f00` | Native builder forwards inherited Blackboard as fifth factory parameter |
| `libbehaviortree_cpp.so:0x5f630–0x5f638` | Child factory calls `BT::TreeNode::setBlackboard()` with saved reference |
| `libbehaviortree_cpp.so:0x75ac4–0x75ad0` | Existing-root cache attach path, not demonstrated to rebind |

All listed checks are exact AArch64 word anchors and branch targets, with `R_AARCH64_JUMP_SLOT` relocation verification for `TreeNode::blackboard()`, `buildTreeFromFile()`, `TreeNode::setBlackboard()`, `XMLParser::instantiateTree()`.

## What remains open

The concrete per-node Blackboard token is resolved through a shared-pointer slot table (v61), but the **producer's and consumer's live token values were not observed**. Native callback branches are conditional; cache reuse further complicates per-instance assumptions. The R2416-reachable `special_push_clean_dish` producer remains unverified, and no physical second mop wash has been demonstrated. The v54 failure-marker erase-before-eligibility branch remains a plausible blocker.

## Reproduce

```bash
python3 x40_r2416_v62_subtree_blackboard_handoff_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected marker: `X40_V62_SUBTREE_BLACKBOARD_HANDOFF_STATIC_PASS`. New v62 tamper checks cover root, file route, native route, cached route and factory Blackboard bind. The committed verifier embeds earlier regressions and uses Python standard library. No original ELF binaries are committed.

**Next (v63):** Decode `XMLParser::instantiateTree()` Blackboard remapping/creation and cached-root lifetime. Continue independent bounded search for an R2416-reachable `special_push_clean_dish` writer. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.
