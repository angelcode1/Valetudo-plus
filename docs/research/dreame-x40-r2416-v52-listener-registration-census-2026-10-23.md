# Dreame X40 R2416 — v52 GlobalDispatcher listener-registration census

**Evidence date:** 2026-10-23  
**Scope:** Offline static examination of the owner's SHA-256-pinned native R2416 libraries, verified against the previously collected runtime library copies. No robot access, firmware modification, AVA/MIOT messages, hooks, maps, credentials, or proprietary binaries are included in this report.

## Executive result

Unlike v51, which established only the ABI of an *unidentified* listener, v52 finds **seven concrete callback-map insertion sites within the original `global_dispatcher::GlobalDispatcher::GlobalDispatcher()` constructor** in `liblethe_route_nodes.so`. Each path prepares an edge-detector object, a named string key, and a `std::function<void(unsigned long const&)>` handler. These are **motion/search/carpet-related listener registrations**, not verified rewash-marker producers. This is a bounded census of one native constructor, not a claim that no other code can register listeners dynamically.

## Proven registry relationship

The dispatcher constructor starts at `0xcf4e90` and has declared size `6596` bytes. Its initialization at `0xcf4eb4–0xcf4f00` sets up an initially empty red-black-tree listener map with its container beginning at `this+0x58`, header at `this+0x60`, and its first-entry link at `this+0x70`. This matches v50/v51's `dispatch()` listener iteration over the latter fields.

Seven direct calls within **that constructor's declared ELF extent** reach the same imported `std::map<std::string,std::function<void(unsigned long const&)>>::operator[]` at `0x44f640`. The callback assignment blocks following these calls install an `std::function` manager/invoker pair. Exact source names and addresses were checked against the pinned ELF's compiled string bytes and AArch64 instruction words, not recovered from a runtime trace.

| Key in callback registry | Typed edge-detector constructor (name-derived) | Callback-map access | `std::function` invoker |
| --- | --- | --- | --- |
| `awesome_search` | `EdgeDetector<AwesomeInEvt,AwesomeOutEvt>` | `0xcf5324` | `0xcf2310` |
| `follow_wall` | `EdgeDetector<FollowInEvt,FollowOutEvt>` | `0xcf5500` | `0xcf2820` |
| `follow_with_chain` | `EdgeDetector<AnonymousInEvt,AnonymousOutEvt>` | `0xcf56d8` | `0xcf0d00` |
| `carpet_follow` | `EdgeDetector<CarpetFollowInEvt,AnonymousOutEvt>` | `0xcf58fc` | `0xcf1e70` |
| `maybe_carpet_follow` | `EdgeDetector<AnonymousInEvt,CarpetFollowOutEvt>` | `0xcf5adc` | `0xcf19e0` |
| `carpet_back_done` | `EdgeDetector<CarpetBackDownInEvt,CarpetBackDownOutEvt>` | `0xcf5cbc` | `0xcf1540` |
| `confirm_carpet` | `EdgeDetector<CarpetConfirmStart,CarpetConfirmEnd>` | `0xcf5eac` | `0xcf1120` |

Each invoker belongs to a handler that captures an edge-detector shared pointer and dispatcher-related state. The callback ABI from v51 remains `unsigned long const&` for the odometry-like numeric argument. We have **not** proven the actions of every nested event/state-machine callback or whether any indirect downstream code changes the station-wash Blackboard.

### Why this matters for the R2416 rewash investigation

There is now a positive, verifiable identity for all seven constructor registrations, rather than an unexplained listener loop. No listener in this list is identified as a producer of `special_push_clean_dish`, `TurbidityResultFail`, or `r2343_start_rewash`; the v50 exact-literal census also found none of those three literal key strings in `liblethe_route_nodes.so`. **This does not rule out** callbacks registered later, callbacks in another library, dynamically generated key names, or effects mediated through state-machine messages and shared Blackboard pointers.

This distinction is especially important because the known `special_push_clean_dish` writer in `node_lethe.so` is gated to model identifiers other than `dreame.vacuum.r2416`. That known producer is not evidence that the R2416 initializes the key. The v52 listener census does not resolve this model-specific eligibility issue.

## Verification scope and procedure

`x40_r2416_v52_dispatcher_registration_verify.py` uses only the Python standard library and the bundled v48–v51 dependencies. It first checks all five full original ELF SHA-256 pins, three active-vs-original byte comparisons, earlier GlobalHook and dispatcher proofs, and then verifies:

- The constructor symbol's exact address and size.
- Initialization of the empty listener map at `this+0x58/+0x60/+0x70`.
- **Exactly seven direct calls** within this constructor to the callback `std::map::operator[]` PLT target.
- Seven exact key string bytes, seven edge-detector constructor calls, seven map accesses, and seven decoded AArch64 function-pointer staging pairs.
- Tampered runtime ELF rejection via the full-image byte-integrity check.

Reproduce using the original owner's local ZIPs:

```bash
python3 x40_r2416_v52_dispatcher_registration_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected marker: `X40_V52_DISPATCHER_CONSTRUCTOR_LISTENERS_STATIC_PASS`.

## Remaining questions

1. Search for **post-construction** listener insertion/removal methods or writes to the same registry, not just call sites in this constructor.
2. Trace the seven concrete invoker functions into their state-machine event effects, separating Blackboard reads, writes, and publication boundaries.
3. Re-focus on all possible R2416-reachable producers of the *exact* `special_push_clean_dish` key and its runtime Blackboard identity, rather than treating similarly named markers as equivalent.
4. Continue to distinguish a rewash request marker and `wash_times` bookkeeping from actual physical dock actuation.

**Limits:** None of these static results proves completion of live plugin initialization, invocation frequency, live state-machine events, normal turbidity triggering a rewash, or physical mop washing. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. The live robot and public Valetudo+ repository are unchanged.