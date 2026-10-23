# Dreame X40 R2416 — v49 GlobalHook callback replacement and pre-tick dispatch audit

**Evidence date:** 2026-10-23  
**Scope:** Offline, read-only inspection of the owner's SHA-pinned R2416 firmware (`node_lethe.so`, `liblethe_route_nodes.so`, other pinned dependency libraries) and exact-matching active tree-library copies. No commands to the robot; no runtime instrumentation, firmware changes, MIOT writes, Valetudo+ changes, or private binaries in the report.

## Executive result: correction to v48's default-callback interpretation

v48 independently established that the default `route_nodes::GlobalHook` callback is a one-instruction AArch64 `ret` in **both** `node_lethe.so` and `liblethe_route_nodes.so`. **v49 proves a compiled callback replacement path** in the route plugin's exported `route_bt_nodes_plugin::RegisterNodes(BT::BehaviorTreeFactory&)`. The registration function installs `route_nodes::odomProcessHook(unsigned long const&, std::shared_ptr<BT::Blackboard>&)` into the GlobalHook singleton's `std::function` storage. This is not a no-op handler: it can call `global_dispatcher::GlobalDispatcher::dispatch(...)` with the odometry value and Blackboard reference.

**Consequence:** It is not justified to treat the pre-`executeTick()` callback as harmless merely because its default handler is empty. If the checked registration path successfully runs and both modules resolve the same singleton, the callback invoked just before the retained tree tick is the dispatcher hook, unless replaced again.

## 1. Exact registration-site evidence

The original `liblethe_route_nodes.so` exports `route_bt_nodes_plugin::RegisterNodes` at `0x48bad0`.

| Address | Compiled role |
| --- | --- |
| `0x48c0d8` / `0x48c0dc` | Dereference the `GlobalHook::Instance(bool)::instance` GOT entry and obtain the singleton |
| `0x48c0e0` | If the singleton is null, enter lazy initialization; normal rejoin at `0x48c8b0 → 0x48c0e4` |
| `0x48c0fc` / `0x48c10c` | Retrieve the relocated `odomProcessHook` function pointer and place it in the new callable's payload |
| `0x48c110` / `0x48c118` | Stage its `std::function` manager/invoker and prepare an assignment |
| `0x48c128`–`0x48c150` | Transfer new `std::function` payload and manager/invoker into the singleton, displacing the old callable |
| `0x48c154`–`0x48c17c` | Conditionally clean up displaced/staged callback storage through manager calls |

The exact ELF GOT relocations establish the intended types and destinations:

| Relocation slot | Symbol and target |
| --- | --- |
| `0x124ed40` | `GlobalHook::Instance(bool)::instance` → `0x1255b60` |
| `0x124fab8` | `route_nodes::odomProcessHook` → `0x4a24e0` |
| `0x1249db0` | `std::_Function_handler<..., function-pointer>::_M_invoke` → `0x48ce10` |
| `0x1249e60` | `std::_Function_handler<..., function-pointer>::_M_manager` → `0x48d530` |

This is instruction-plus-relocation evidence of a **write**, rather than just another `GlobalHook` reference.

## 2. Concrete replacement handler and downstream work

`route_nodes::odomProcessHook` is an exported function at `0x4a24e0` (ELF symbol size 248 bytes). It checks/lazily obtains the `GlobalDispatcher` singleton and follows a branch reaching `0x4a2538–0x4a254c`, where it forwards the Blackboard reference and odometry number via a tail branch to the PLT for `GlobalDispatcher::dispatch(std::shared_ptr<BT::Blackboard>&, unsigned long)`.

`GlobalDispatcher::dispatch` is an exported 592-byte function beginning at `0xcf4220`. Verified compiled actions include:

- `0xcf4254`: store a Blackboard-related raw pointer in dispatcher-owned state.
- `0xcf429c`: store the supplied numeric odometry argument.
- `0xcf42b4`: direct call to `StopPauser::update(...)` through the PLT.
- `0xcf42f4`: indirect invocation of one registered dispatcher callback on an eligible branch.

The `GlobalDispatcher` state machine can therefore execute work **before** `OdomProcessSUB()` continues to the original `BT::SubtreeConditionNode::executeTick()` virtual dispatch (`0x3e1390–0x3e139c` in `node_lethe.so`). These actions are **not** evidence of any particular Blackboard key being written, of `StationWash` being ticked, or of the callback blocking/throwing on the live robot.

## 3. Native symbol identity caveat

Both ELFs export `GlobalHook::Instance(bool)::instance` as an ELF `OBJECT` with `STB_GNU_UNIQUE` binding. This supports the possibility that the two compiled modules use a coalesced singleton under normal dynamic-linker resolution. **Exact link-map namespace, symbol interposition, plugin registration completion, and current callback identity were not observed** on the live R2416 process. Do not collapse those distinct claims into "callback definitely replaced at runtime." The presence of a matching plugin under `/tmp/lib/tree_lib/` does not independently prove successful registration.

## 4. Reproducible verification and strict limits

The v49 verifier uses only the Python standard library plus the bundled v48 verifier. It independently confirms all five original SHA-256 ELF pins, three runtime/original byte comparisons, both default handler implementations (v48 regression), the four GOT relocations above, exact instruction anchors for callback replacement, the lazy singleton branch rejoin, the wrapper dispatch, and representative `GlobalDispatcher` operations. An altered copy of a runtime library is rejected at the integrity gate.

Expected success marker: `X40_V49_GLOBALHOOK_REPLACEMENT_STATIC_PASS`.

**Not proven:** actual registration callback completion, in-process singleton coalescing, active runtime callback target, effects on a specific Blackboard entry, odometry callback rate or errors, an R2416-compatible producer of `special_push_clean_dish`, threshold-to-`r2343_start_rewash` causality, or any second physical dock wash.

## 5. Next investigation

1. Continue the *offline* call-path audit from `GlobalDispatcher::dispatch` through `StopPauser::update` and registered dispatcher listeners. Differentiate runtime branch outcomes from mere compiled callbacks.
2. Look specifically for any bounded link from these paths into `special_push_clean_dish` or `r2343_start_rewash`. Preserve exact key spellings, distinct Blackboard holders and model-specific gates.
3. If a live observation is ever required, obtain separate authorization for a strictly read-only, bounded observation. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and the working robot unchanged.

No proprietary binary, raw configuration, factory credential, camera/map imagery, serial or device identifier should be published to GitHub.