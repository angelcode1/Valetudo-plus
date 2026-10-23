# Dreame X40 R2416 — v45 retained-tree lifecycle and tick-boundary audit

**Date:** 2026-10-23  
**Scope:** Offline-only analysis of the user's original SHA-256-pinned AVA native ELF collection and byte-identical runtime tree libraries. Complements the v44 configured-`RobotNode` wrapper audit. No robot connection, MIOT calls, AVA instrumentation, runtime restart, changes to Valetudo+, or GitHub writes.

## Executive result

**The configured `RobotNode` wrapper is retained in the `AvaNodeRoute` object's embedded `BT::Tree` storage and its root is halted during destruction. However, `AvaNodeRoute`'s compiled virtual `ProcessEveryTick()` slot points to an inherited, four-byte `ret` stub.** Therefore that callback is **not** evidence of ticking the retained root. Actual root ticking, if it occurs, must be traced via a different path or dispatcher.

The separate `AvaNodeRoute::UpdateOutput()` routine is confirmed to call `PlanningFuncInUpdateOutput()` and access `AvaNodeRoute+0x30` (Blackboard). It is a candidate for later investigation, **not a proven `BT::TreeNode::tick()` caller**.

## Original library pins

| Binary | SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The verifier also checks byte equivalence of the three runtime tree libraries collected in the owner's v27 archive. Neither the binaries nor private `setting.yaml` are redistributed.

## A. Configured wrapper is retained and has a destructor cleanup path

v44 verified `buildTreeFromText()` at `node_lethe.so:0x3552c8` and the root-pointer move into `AvaNodeRoute+0xf48` at `0x3552d8`. v45 independently pins the relevant destructor sequence:

| Address | Native operation |
| --- | --- |
| `0x323c8c` | Destructor preserves its `this` pointer in `x21` |
| `0x325cb4` | `ldr x0, [x21,#0xf48]` (retained tree root pointer) |
| `0x325cb8` | Branch on null root (`cbz x0`) |
| `0x325cbc` | Call imported `BT::haltAllActions(BT::TreeNode*)` if non-null |
| `0x325cc0` | Load beginning of the adjacent `BT::Tree` node collection at `+0xf50` |

This is **compiled ownership/cleanup evidence**. It is not proof of successful initialization during a particular job or of a tick during normal operation. The guarded call only describes what the destructor would do if invoked with a non-null retained root.

## B. The class's per-tick virtual slot is a no-op

The exact `AvaNodeRoute` vtable symbol is at `0xb60d58`. With the standard two-word Itanium C++ vtable prefix, the method address point is `0xb60d68`. The dynamic relocation at `0xb60d88` (offset `+0x20` **from the address point**, or `+0x30` from the vtable symbol) resolves to:

`ancp::AvaNodeRouteBase::ProcessEveryTick()` at `0x376d20`.

The symbol is **four bytes long** and its only instruction is AArch64 `ret` (`0xd65f03c0`). The v45 verifier checks the relocation's symbol identity, type, addend, vtable offset, function address, symbol size, and exact instruction.

Consequently, a caller dispatching the `ProcessEveryTick()` virtual slot on an `AvaNodeRoute` instance would execute the inherited stub, not tick the retained tree. This does **not** rule out a separate scheduler, custom callback, direct virtual root dispatch, or an external process performing tree ticks.

## C. `UpdateOutput()` is a separate candidate path, not established root execution

`AvaNodeRoute::UpdateOutput()` is exported at `0x3daf20`. At `0x3daf64` it prepares its receiver in `x0` and at `0x3daf68` calls `AvaNodeRoute::PlanningFuncInUpdateOutput()` through the PLT. At `0x3dafd4`, the same routine loads `AvaNodeRoute+0x30` (the Blackboard holder). The checked entry segment does **not** itself establish a virtual `tick()` call on the retained root at `+0xf48`. Independently, the exported `PlanningFuncInUpdateOutput()` function has a 980-byte symbol extent (`0x3d3f90–0x3d4364`). A complete instruction census of that bounded body finds **no AArch64 `BLR` instruction and no direct 64-bit `LDR` at offset `+0xf48`**. Its visible direct calls involve reporting/health updates, command publication and standard-library operations. This is *negative evidence for an in-function direct root tick*, not proof that a called helper or some other scheduler never ticks the tree.

**Next offline investigation:** Inspect the broader scheduler/callback registrations and other tree-root dispatch sites; track root-node pointer provenance and the virtual tick slot before claiming actual execution. Avoid mistaking generic `ProcessEveryTick()` callbacks, destructor halts, model-name strings, or Blackboard reads for positive root-tick evidence.

## D. Unresolved CleanGenius / rewash mechanism

- `RobotNode` structurally contains `StationWash` through the compiled `SubtreeCondition`/registered-builder mechanism, but a real station-wash tick has not been demonstrated.
- The previously identified direct `special_push_clean_dish=1` initializer has a model gate that excludes R2416. No alternative R2416-compatible writer has been demonstrated.
- `TurbidityResultFail`, the wash gate, `special_push_clean_dish`, and the conditional `r2343_start_rewash` request remain distinct prerequisites. A written request marker is not equivalent to a physical dock-wash command.
- **No normal turbidity-triggered second physical mop wash has been proven.** Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.

## Reproduction

Unzip the complete v45 audit package, keeping the bundled v36–v44 scripts alongside the v45 script. Run:

```bash
python3 x40_r2416_v45_tree_lifecycle_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected final marker: `X40_V45_TREE_LIFECYCLE_TICK_BOUNDARY_STATIC_PASS`.

**Privacy and safety:** Keep proprietary ELF archives, device settings, root credentials, camera data and maps private; do not add them to a public GitHub repository. This report and verifier contain only independently described static code facts and standard-library-only offline checks.