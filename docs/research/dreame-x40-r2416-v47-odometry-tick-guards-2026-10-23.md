# Dreame X40 R2416 — v47 odometry tick guard / rejoin audit

**Date:** 2026-10-23  
**Scope:** Offline read-only analysis of the user's preserved SHA-256-pinned original firmware and byte-matched runtime tree libraries. No robot communication, native payload modification, runtime hooks, experimental MIOT writes, firmware flashing or Valetudo+ changes. This report includes no firmware binaries, credentials, maps or unredacted private configuration.

## Executive result

The v46 finding stands: `ancp::AvaNodeRoute::OdomProcessSUB(OdometryMsg*)` has a compiled dispatch of the retained tree root at `AvaNodeRoute+0xf48` to the `BT::SubtreeConditionNode::executeTick()` virtual slot. v47 distinguishes three **branch detours that have a static return path to that dispatch** from a **null-callback branch that enters a C++ exception path**.

These are bounded intraprocedural control-flow facts, not observed runtime behaviour. In particular, one cannot convert a branch having a static path to `executeTick` into a claim that a live device necessarily reaches it: dynamic conditions, exceptions, other guards, indirect callbacks and scheduler delivery still matter.

## Original and runtime pins

| ELF | Original SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The three active `tree_lib` ELFs remain byte-identical to their original archive copies, as tested in the v36–v47 verifier chain.

## 1. Named global registration/initialization objects

Full `.rela.dyn` GOT relocation checks in original `node_lethe.so` identify:

| GOT slot | Native symbol | Relevant instruction |
| --- | --- | --- |
| `0xb7e238` | `dreame::route::SuspendableRegister::suspend_all` | `0x3e1238` obtains pointer; `0x3e1240` tests byte |
| `0xb79cb0` | C++ static initialization guard for `basic_actions::StateStack()::ins` | `0x3e12c4` loads guard; `0x3e12c8` checks its bit |
| `0xb7c9d8` | C++ static `route_nodes::GlobalHook::Instance(bool)::instance` | `0x3e1360–0x3e1370` loads and checks singleton |

A symbol's name does not automatically establish the semantic effect of a branch. In particular, `suspend_all` should not be interpreted as a *guaranteed* suppression of all `RobotNode` ticks; the compiled conditional branch enters additional work that can rejoin the tick path.

## 2. Exact conditional branch disposition

| Site | Branch target | Verified static route |
| --- | --- | --- |
| `0x3e1240` `cbnz` | `0x3e320c` | This detour contains a conditional jump at `0x3e3214` back to `0x3e1250`; both arms can reach `0x3e1390` |
| `0x3e12c8` `tbz` | `0x3e303c` | Uses `__cxa_guard_acquire`, conditionally initializes `StateStack`, releases guard, and returns to `0x3e12cc`; both arms can reach the root dispatch |
| `0x3e1370` `cbz` | `0x3e3650` | GlobalHook singleton setup path can return via `0x3e36cc` to `0x3e1374`; both arms can reach the root dispatch |
| `0x3e1380` `cbz` | `0x3e443c` | This target calls `std::__throw_bad_function_call()` at PLT `0x27cf20`; the nonnull callback arm can reach `0x3e1390`, the null arm does not have a normal-return route |

Immediately before the retained-root tick, `0x3e138c` calls a separate indirect function pointer (`blr x3`). Its successful return is an additional *practical* prerequisite; the v47 audit does not identify that callback's concrete runtime target or prove it cannot throw/block. The separate `root+0xf48` virtual call remains at `0x3e1390–0x3e139c` and the returned tick-status byte is preserved at `0x3e13a0`.

The global-hook singleton detour may block, throw, or behave differently based on runtime state. **The existence of a static rejoin path is not an unconditional guarantee of progress.**

## 3. Bounded graph method and validation

The standalone verifier uses only Python's standard library. It imports the original v36–v46 read-only verification chain, checks all five exact full-file SHA-256 hashes and three original/runtime byte comparisons, checks the four branch instruction words, checks the three named relocation entries, and reconstructs a bounded AArch64 direct-control-flow graph over the original `OdomProcessSUB` symbol range `0x3e02c0..0x3e5530`.

The graph recognizes direct `B`, conditional `B.cond`, `CBZ/CBNZ`, `TBZ/TBNZ`, `RET` and indirect `BR` exits, with ordinary calls conservatively treated as returning. The independently verified `std::__throw_bad_function_call` path is modeled as non-returning. It does **not** solve branch feasibility, model exceptions generally, or resolve indirect calls. The success criterion is syntactic reachability of the retained-root load site—not that the robot executes it.

Expected marker: `X40_V47_ODOMETRY_TICK_BRANCH_REJOIN_STATIC_PASS`.

## 4. Remaining work

1. Determine the concrete target/contract of the indirect callback invoked at `0x3e138c`, the final call before the tree root dispatch; identify any state it supplies and any failure or suspension behavior.
2. Trace the retained tick-status byte (`w25` after `0x3e13a0`) to its consumers and examine whether the same odometry path schedules or suppresses later ticks.
3. Revisit the **R2416-specific** producer of `special_push_clean_dish`. The previously identified `ProcessModelInfo` producer is gated to other models; exact-literal census has not found a demonstrated alternate for R2416.
4. Do not infer turbidity-driven rewash or a second physical wash without evidence connecting the normal threshold, Blackboard prerequisites, `r2343_start_rewash` and dock actuation.

## Reproduction

With the original private archives and the bundled verifier scripts in one directory:

```bash
python3 x40_r2416_v47_odometry_guard_paths_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not upload original native ELFs, private config, device identifiers, passwords, maps, or complete disassemblies to public GitHub. No device action or source-code/runtime change is authorized or necessary for this offline finding.