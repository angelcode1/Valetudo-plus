# Dreame X40 R2416 — v51 dispatcher Blackboard retention and listener call ABI

**Evidence date:** 2026-10-23  
**Scope:** Offline-only static audit of the owner's existing SHA-256-pinned original R2416 ELF archive and its exact-matching runtime tree-library copies. No robot access, runtime hooks, firmware changes, MIOT/AVA writes, or Valetudo+ changes. This document contains no proprietary firmware bytes, raw disassembly, private configuration, maps, credentials, or device identifiers.

## Executive result

The prior v49–v50 audits identified a `GlobalHook` replacement into `GlobalDispatcher::dispatch(...)` and an optional RB-tree listener loop before the retained `RobotNode` root tick. **v51 independently verifies the data contract at this loop:** the dispatcher saves the incoming Blackboard's raw pointer and ownership metadata in its own instance before invoking listeners, while the **direct argument** to each listener callback is a pointer to the saved odometry numeric value. The Blackboard is **not supplied as a separate direct argument to `blr x2` at `0xcf42f4`**.

This is important for the R2416 rewash analysis: a callback may *indirectly* obtain the Blackboard through captured state or dispatcher-owned fields, but merely observing its invocation does not establish that the callback writes `special_push_clean_dish`, `TurbidityResultFail` or `r2343_start_rewash`. The actual listener registrations and concrete callback implementations remain unidentified.

## Verified compiled dataflow (original `liblethe_route_nodes.so`)

The exported `global_dispatcher::GlobalDispatcher::dispatch(std::shared_ptr<BT::Blackboard>&, unsigned long)` has entry `0xcf4220`, 592 bytes in the pinned ELF.

| Address | Instruction-level finding | Narrow meaning |
| --- | --- | --- |
| `0xcf4234–0xcf4244` | Save dispatcher `this`, incoming `shared_ptr` reference, and numeric argument to stack | Identifies input roles in the call frame |
| `0xcf4254` | Store `shared_ptr`'s raw Blackboard pointer to `dispatcher+0x18` | Retains a raw pointer for subsequent dispatcher use |
| `0xcf4258–0xcf4264` | Compare existing owner field `dispatcher+0x20` against incoming `shared_ptr` control block | A change of owner is handled conditionally |
| `0xcf4278–0xcf4280` | Increment incoming control-block's strong-reference count on the applicable path | Supports retained shared ownership; not pointer equality across every tree object |
| `0xcf4284–0xcf4290` | Call old owner release helper if needed, then store new owner to `dispatcher+0x20` | Replaces the retained owner |
| `0xcf4298–0xcf429c` | Copy the saved numeric odometry argument to `dispatcher+0x08` | Stores the separate numeric input |
| `0xcf42cc–0xcf42d8` | Load RB-tree entry from `dispatcher+0x70`, use sentinel at `dispatcher+0x60`, test for empty registry | Identifies an optional list of registered callbacks |
| `0xcf42dc–0xcf42f4` | Prepare `x1=sp+0x38` (address of numeric argument), `x0=entry+0x40` (callback payload), then invoke callback through `blr x2` | **One direct callback argument:** odometry numeric reference, not the Blackboard reference |
| `0xcf42f8–0xcf4308` | Advance RB-tree iterator until the end sentinel | More than one listener may be invoked |

The branch at `0xcf42c8` that skips listeners when a state-machine byte is nonzero remains as documented in v50. These callbacks occur *before* the retained root `executeTick()` in the separately verified odometry path when all outer conditions are satisfied.

### Why the Blackboard is still a possible indirect dependency

`dispatcher+0x18` and `dispatcher+0x20` can allow dispatcher-owned code to reach the retained Blackboard even though the callback call does not pass it explicitly. No equivalence is asserted between this pointer and any of the distinct tree-node, `SlamControl`, or `AvaNodeRoute` Blackboard holders unless separately proven in a concrete runtime instance. The callback data and its captured objects remain dynamically typed/indirect in the checked call site.

### Registry identity is not established

This pass also inspected the singleton GOT usage and the constructor's empty-map initialization. Those checks **did not produce a verified source-level inventory of insertions or concrete listener callback targets**. In particular:

- The presence of an `std::function`-style callback entry is not proof that the registry is populated on R2416.
- The absence of exact rewash-key literals in `liblethe_route_nodes.so` (v50) is only a direct-literal result, not an exhaustive proof about generated strings or external callbacks.
- A callback can retain or access external state, so the single direct argument **does not** prove it cannot modify the Blackboard.
- No direct actuation path, positive dirty-water threshold transition, or successful second dock wash is demonstrated.

## Reproduction and negative test

The accompanying `x40_r2416_v51_dispatcher_callback_abi_verify.py` uses Python's standard library, with the bundled v48/v49/v50 verifiers as dependencies. Its input archives are treated as inert binary evidence. It first repeats the five full original ELF SHA-256 checks and three runtime/original library equality checks, then verifies **33 fixed AArch64 instruction words**, the dispatcher symbol size, two PLT call targets and one singleton GOT relocation. This is an explicit bounded check, not a whole-program proof of missing registrations.

```bash
python3 x40_r2416_v51_dispatcher_callback_abi_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V51_DISPATCHER_CALLBACK_ABI_STATIC_PASS`. A one-byte change to the runtime `liblethe_route_nodes.so` is rejected by the existing byte-for-byte SHA/ELF provenance gates.

## Next investigation

Identify concrete registry insertion and removal sites by tracking stores/operations on the dispatcher RB-tree fields `+0x60` and `+0x70`, across call boundaries and any inlined methods. Resolve callback target implementations and captured objects where possible before attributing Blackboard side effects. A separate candidate is tracing the actual model-gated producer and alternatives for `special_push_clean_dish` **without enabling experimental MIOT writes**. Preserve the exact key spellings and distinguish request bookkeeping from physical dock actuation.

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; no robot commands, firmware patching, runtime injection, proprietary file publication or production code changes. This is a static finding, not validation that CleanGenius automatic rewash works on R2416.