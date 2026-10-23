# Dreame X40 R2416 — v50 GlobalDispatcher listener-gate audit

**Date:** 2026-10-23  
**Scope:** Static, offline inspection of the owner's preserved, SHA-256-pinned native ELFs and matching runtime tree libraries. No robot access, injected hooks, firmware modifications, MIOT writes, proprietary binaries, maps, device identifiers, credentials or private configuration are included here.

## Executive finding

v49 established that the `liblethe_route_nodes.so` registration code can replace `GlobalHook`'s default empty callback with `route_nodes::odomProcessHook(...)`, which invokes `global_dispatcher::GlobalDispatcher::dispatch(...)`. v50 resolves an important **internal callback gate** in that dispatcher: after `StopPauser::update()`, a nonzero state byte causes the dispatcher to **skip its ordered listener callbacks**, whereas a zero state permits traversal of the registered `std::function` listener tree.

**The listener bypass is not a direct bypass of `AvaNodeRoute::OdomProcessSUB()`'s later `RobotNode` `executeTick()` call.** That later call is reached if the dispatcher callback returns normally and other outer conditions permit it. This report does not establish that any listener is registered or invoked on a running X40.

## Verified native sequence

The SHA-pinned `liblethe_route_nodes.so` contains `GlobalDispatcher::dispatch(std::shared_ptr<BT::Blackboard>&, unsigned long)` at `0xcf4220` with a symbol size of 592 bytes.

| Address | Compiled operation | Consequence / limit |
| --- | --- | --- |
| `0xcf42a4–0xcf42a8` | Read state-machine singleton; null branches to initialization/wait path | Singleton availability matters for call completion |
| `0xcf42b4` | Call `StopPauser::update(...)` | Does not prove a real pause occurred |
| `0xcf42c0–0xcf42c8` | Re-read state machine; load byte `[x0+0x18]`; branch to `0xcf430c` if nonzero | Bypasses listener loop, *not* the caller's root tick |
| `0xcf42cc–0xcf42d8` | Load map-tree header/first entry (`dispatcher+0x60` / `+0x70`); check empty | No entries means no listener callbacks |
| `0xcf42e0–0xcf42f4` | Load `std::function` state from a tree entry and invoke handler indirectly (`blr x2`) | Target callback is dynamic; exact listener identity unproven |
| `0xcf42fc–0xcf4308` | Increment RB-tree iterator, loop while more entries | Can invoke multiple registered listeners |
| `0xcf430c` onward | Shared function-exit/check path | Not proof the function returns without throwing or blocking |

The `GlobalDispatcher` constructor begins at `0xcf4e90` and initializes its callback tree header around `dispatcher+0x60`, including an empty-entry count and sentinels at `0xcf4ef8–0xcf4f00`. This identifies the data structure as a genuine listener registry, not just an arbitrary function pointer.

### Singleton wait path

On the missing-state-machine branch, `dispatch` contains:

- `0xcf43a0`: `mov w0,#1`
- `0xcf43a4`: `bl usleep@plt`
- `0xcf43a8–0xcf43ac`: reload singleton and repeat if null
- `0xcf43bc`: update the `StopPauser` after an instance appears
- `0xcf43c8`: rejoin at `0xcf42c4` if available

This **could delay a tree tick when the callback executes**. It is not evidence of a device hang or a measured latency. The enclosing exception and initialization behaviour is not exhaustively analyzed.

### StopPauser state treatment

The `StopPauser::update` routine at `0xd0d630` contains a reset of its byte `+0x18` at `0xd0d680` and independently reads that byte at `0xd0d6ec` before branching at `0xd0d6f4`. The `dispatch` function reads the corresponding state-machine byte at `0xcf42c4` before deciding whether to traverse listeners. The precise user-facing meaning of this byte and every branch that changes it are **not** established here. In particular, do not equate it automatically with a physical pause, or with `special_push_clean_dish`.

## Relationship to CleanGenius and rewash

A literal census over the **entire pinned `liblethe_route_nodes.so` ELF** found zero exact occurrences of `special_push_clean_dish`, `r2343_start_rewash` and `TurbidityResultFail`. This is a bounded direct-literal negative result, **not** a proof of absent dynamic Blackboard accesses, external library callbacks, inherited aliases, or runtime string construction.

The evidence therefore supports **a dispatcher pre-tick listener gate** but no additional R2416-compatible producer of the rewash eligibility key. Normal turbidity → `r2343_start_rewash` → second physical mop wash remains unproven.

## Reproducibility

The bundled `x40_r2416_v50_dispatcher_listener_gate_verify.py` is standard-library-only and imports the bundled v48/v49 verifiers as dependencies. It uses the original ZIP and runtime ZIP solely as inert byte inputs. It validates five full original ELF SHA-256 pins, three byte-for-byte active/original library matches, previously checked GlobalHook callback replacement, selected opcode anchors, `BL` targets, `CBZ`/`CBNZ`/`B.cond` branch destinations, the listener callback loop, singleton polling and the exact-literal census. A tampered runtime archive is rejected at the hash/byte gate.

Run:

```bash
python3 x40_r2416_v50_dispatcher_listener_gate_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected completion marker: `X40_V50_DISPATCHER_LISTENER_GATE_STATIC_PASS`.

## Next bounded investigation

Identify the code that inserts/removes callback entries in the dispatcher tree, including the concrete targets if recoverable from pointer-relocation and constructor patterns. Then trace each identifiable listener's read/write relationships to *exact* rewash key names and Blackboard holder identities. Preserve the model-specific R2416 restriction and do not claim runtime registration or physical mop actuation from static code alone.

**Safety and repository:** Leave `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No live robot commands, MIOT/AVA publications, hooks, firmware modifications or production changes. Keep original ELFs and private config out of public GitHub.