# Dreame X40 R2416 — v46 odometry-driven retained-root `executeTick` audit

**Research date:** 2026-10-23  
**Scope:** Offline-only analysis of the original, SHA-256-pinned R2416 native libraries and the owner's byte-identical runtime tree plugins. No device connection, commands, hooks, MIOT writes, Valetudo+ changes, or firmware modifications.

## Executive finding

**A genuine compiled dispatch of the retained `AvaNodeRoute+0xf48` behaviour-tree root has been identified in `AvaNodeRoute::OdomProcessSUB(OdometryMsg*)`.** The function loads the retained root, retrieves its virtual method at offset `+0x18`, and calls it. The actual `BT::SubtreeConditionNode` vtable independently resolves that virtual slot to `executeTick()`.

This resolves v45's *identity-of-the-tick-caller* research gap: `ProcessEveryTick()` being a one-instruction `ret` does **not** mean no compiled tree-tick pathway exists. **Neither a successful runtime tick nor the occurrence of a second physical dock wash has been observed.**

## Verified source pins

| Original ELF | SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

As in v27–v45, the three original tree-library bytes match the owner's saved `/tmp/lib/tree_lib/` copies. Neither original proprietary ELF nor raw private device configuration is included in this package.

## A. Odometry callback binding

`node_lethe.so` exports:

- `ancp::AvaNodeRoute::OdomProcess(OdometryMsg*)` at `0x3cff50`.
- `ancp::AvaNodeRoute::OdomProcessSUB(OdometryMsg*)` at `0x3e02c0`.

At `0x3cff88/0x3cff98`, the compiled `OdomProcess()` constructs a bound method pointer by fetching the GOT slot `0xb7b710`. The corresponding `R_AARCH64_GLOB_DAT` relocation names `OdomProcessSUB` and resolves to `0x3e02c0`. A call at `0x3cffe8` invokes `AsyncDeque::MultAsyncSubscribe<OdometryMsg, OdometryMsg&>` through the PLT with the bound callback.

This is an **asynchronous odometry-processing callback path**. It does not demonstrate that a given message was delivered or that the worker executed on the owner's robot.

## B. Root pointer provenance and virtual dispatch

In the worker, `0x3e02d8` saves the method receiver in `x20`. On the relevant guarded path, the following instructions execute:

| Address | AArch64 instruction | Interpretation |
| --- | --- | --- |
| `0x3e1390` | `ldr x0, [x20,#0xf48]` | Load the tree root retained in v44/v45 |
| `0x3e1394` | `ldr x1, [x0]` | Load the root's vtable address point |
| `0x3e1398` | `ldr x1, [x1,#0x18]` | Fetch the virtual `executeTick`-position entry |
| `0x3e139c` | `blr x1` | Indirect method dispatch with root in `x0` |
| `0x3e13a0` | `and w25,w0,#0xff` | Retain the returned low status byte |

The surrounding worker contains conditional branches and status/data checks, including a bit-test branch at `0x3e12c8`. This is **not** an unconditional call on every odometry message. Static compilation does not reveal an actual tick rate or which guards hold during any particular cleaning operation.

## C. Exact virtual-slot identity

In the independently pinned `libbehaviortree_cpp.so`:

- The exported `BT::SubtreeConditionNode` vtable symbol is at `0xd65d0`.
- Its Itanium C++ address point is `0xd65e0` (the symbol plus the two prefix words).
- The relocation at `0xd65f8`, i.e. `+0x18` relative to that address point, names `BT::SubtreeConditionNode::executeTick()` at `0x74a80` (size 60 bytes).

This independently verifies that the observed call sequence is to the expected **tick-execution slot**, not `halt()`, a destructor, or `ProcessEveryTick()`. The configured wrapper created in v44 is a `SubtreeCondition` root, giving the lookup a concrete class context. This remains compiled class-dispatch evidence: it does not exclude runtime object/registry anomalies.

## What has changed since v45

v45 correctly established that `AvaNodeRouteBase::ProcessEveryTick()` is an inherited no-op and the retained root has destructor cleanup. It examined `UpdateOutput()`/`PlanningFuncInUpdateOutput()` as a candidate tick path and found no direct root dispatch in the bounded planning helper. **v46 finds the concrete root dispatch in a different routine, `OdomProcessSUB()`.** These findings are consistent, not contradictory.

## Remaining rewash questions

1. **Tick eligibility:** whether `OdomProcessSUB()` takes the guarded root-dispatch path during normal cleaning and what statuses `RobotNode` returns.
2. **StationWash ancestry:** the compiled `RobotNode` tree includes `StationWash` through `SubtreeCondition`, but entry into and execution of the wash subtree depend on parent-control conditions.
3. **R2416 eligibility key:** the identified `ProcessModelInfo()` initializer for `special_push_clean_dish=1` is gated to other model IDs; no R2416-reachable alternative producer has been demonstrated.
4. **Causality to hardware:** no observed positive turbidity threshold -> failure/eligibility state -> `r2343_start_rewash` -> physical dock wash chain. A virtual root tick alone is **not** a rewash or actuator command.

## Reproduction

With the unchanged private archives and the bundled `v36–v46` Python verifier files placed together:

```bash
python3 x40_r2416_v46_odom_tree_tick_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V46_ODOMETRY_ROOT_EXECUTETICK_STATIC_PASS`.

The verifier checks five full original ELF hashes, exact equality of three runtime/original libraries, v36–v45 static regression evidence, the exact odometry callback relocation and PLT call, the root-load/vtable/call sequence, and the exact `SubtreeConditionNode` `executeTick` relocation. It does **not** connect to the robot or execute ELF code.

**Operational boundary:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Preserve the working Valetudo+ installation, do not inject AVA messages or publish firmware/binaries/maps/credentials/private configuration. This research has made no GitHub changes.