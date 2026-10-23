# Dreame X40 R2416 — v81: app-status registry callback to native Smart switches

**Date:** 2026-10-24. **Scope:** pinned, offline static analysis of the owner's original AArch64 `node_lethe.so` (SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`). No vacuum access, firmware write, native binaries or device secrets included.

## New confirmed native route

v78–v80 established MIOT service 4/property 50 string get/set/report, the `STATE_TO_LOGIC` publisher/subscriber and the receiver's JSON `k`/`v` decoding and reconstruction. **v81 identifies the missing registered app-status callback and follows it into the name-specific native Blackboard writers.**

`AvaNodeRoute` constructs a route-dispatch registry at `this+0xfa8` and stores its address at member offset `+0x30` (ELF VAs `0x34c088`, `0x34c098`). The `StateShowAndSave` constructor, whose second parameter is `AvaNodeRouteBase*`, copies that registry member from the passed route into its own base (VAs `0x88d0e4`, `0x88d0ec`, `0x88d130`, `0x88d13c`).

In `StateShowAndSave`'s constructor, VAs `0x88d404–0x88d4d0` obtain the registry, construct the exact key **`receive_app_status_msg`** (VA `0x9f7fa0`), and register a function object pointing to a local wrapper **`0x893800`**. In the other direction, `AvaNodeRoute::ReceiveStateListProcessSUB()` loads the registry at `0x5933b0`, constructs the **same key** at `0x5933dc–0x5933e0`, looks up a function object through an indirect method at `0x593414–0x593428`, and invokes the dynamically retrieved callback at **`0x5937a4`** after its `k`/`v` JSON processing.

The registered wrapper at `0x893800` contains a verified direct `BL` at **`0x893858 → 0x88f3d0`**. The target has a *separate native function prologue* and invokes RapidJSON `ParseStream` at `0x88f4c8`. The callback parsing routine has input-name comparisons and **typed `BT::Blackboard::set<int&>`** calls:

| Native setting | Input name literal VA | Setter call VA | Native Blackboard key |
|---|---|---|---|
| `SmartHost` | `0xa2f7a0` | `0x890360` | `smart_hosting_switch` |
| `SmartAutoMop` | `0xa2f7b0` | `0x890508` | `smart_auto_mop_switch` |
| `SmartAutoWash` | `0xa2f858` | `0x891780` | `smart_auto_wash_switch` |

The host setter has a `0..2` unsigned guard at `0x89032c–0x890330`. The two auto-switch paths normalize **signed -1/-2 to zero** on those specific nonzero setter branches (`0x8904d4–0x8904dc`, `0x89174c–0x891754`). That does **not** establish the meaning of the observed MIOT `SmartAutoMop=-1` readback or the live values read by the station gate.

## Corrections to the v76/v80 function attribution

The exported `StateShowAndSave::SyncStateChange()` begins at `0x88dab0` and has four known **direct PLT callers** in `WritePropIntProcessSUB` (`0x5842a4`, `0x584348`, `0x584698`, `0x58473c`). However, `0x88f3d0` is **a separate local entry** after an earlier function's exit/alignment, not a direct invocation of the exported `SyncStateChange` entry. Disassembly labels inherited from the last exported symbol made the setter routine appear to be inside `SyncStateChange()` in v76. The v80 direct-call inventory remains correct, but it did not exclude this **registry-selected wrapper → local parser** route. We now attribute the three setter calls to the independent app-status parser, not necessarily the exported named synchronizer.

## What is and isn't proven

The **compiled** native producer/subscriber, route registry sharing, matching callback key, registration, lookup, wrapper and typed Blackboard setters form a strong static ingress path. We have **not** observed runtime callback invocation, persistent MIOT settings propagation, or the identity of the Blackboard instance consumed by `liblethe_tactics_tree.so`'s `SweepStationContorl::TurbidityRecleanAndRewashSet()`. The latter is necessary before equating observed native property values with station rewash eligibility. Nor have we proven genuine dirt/turbidity input triggers an additional cleaning pass or second physical wash.

**Negative control preserved:** v77 enum-24 Smart Wash writes the separate `smart_wash_switch` **string**, not the integer `smart_auto_wash_switch` key.

## Offline verifier and operational state

The sanitized package `X40-R2416-v81-sanitized-app-status-blackboard-20261024.zip` contains Python standard-library verifier `x40_r2416_v81_app_status_switch_bridge_verify.py`, technical report and README. It checks 40 original instruction anchors, seven text literals, ADRP/ADD resolutions, typed PLT symbols, registered wrapper target and named export call inventory; **47 one-byte mutations were rejected**:

```text
X40_V81_SAME_DISPATCH_REGISTRY_CONSTRUCTOR_STATIC_PASS
X40_V81_APP_STATUS_HANDLER_REGISTER_LOOKUP_STATIC_PASS
X40_V81_CALLBACK_WRAPPER_TO_JSON_PARSER_STATIC_PASS
X40_V81_JSON_TO_NATIVE_TYPED_SMART_SWITCH_STATIC_PASS keys=3
X40_V81_NAMED_SYNCSTATECHANGE_ENTRY_SEPARATE_STATIC_PASS
X40_V81_STATIC_MUTATIONS_REJECTED count=47
LIMIT: runtime dispatch, MIOT readback persistence, cross-ELF Blackboard instance and physical reclean/rewash NOT proven
```

**Next:** determine cross-ELF shared Blackboard *object identity* and trace real turbidity decisions through `r2343_start_rewash` to the physical dock action. No guessed native settings writes or synthetic dirt triggers.

**Robot unchanged:** verified Valetudo+ v74 with native `SmartHost=0` after the user-confirmed 1→0 transport test; launcher restored and rebooted, `writeGateOpen=false`, unchanged baseline. Preserve active binary, parent/original files, v70/v73 rollback and configuration; do not install these research assets on the robot.
