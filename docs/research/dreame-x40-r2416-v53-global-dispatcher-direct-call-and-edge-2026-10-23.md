# Dreame X40 R2416 — v53 GlobalDispatcher direct-call and callback-entry audit

**Date:** 2026-10-23  
**Scope:** Offline, read-only static audit of original SHA-pinned native ELF files and collected matching runtime tree libraries. This report contains no proprietary binary, raw disassembly, passwords, maps, camera frames, device identifiers or live telemetry. No robot connection or Valetudo+ changes.

## Executive result

The seven `std::map<std::string,std::function<void(unsigned long const&)>>::operator[]` registrations identified in v52 are **all the direct `BL` calls targeting that precise `operator[]` PLT entry (`0x44f640`) in the entire executable `.text` section** of the original `liblethe_route_nodes.so`, not just in the `GlobalDispatcher` constructor. All seven reside within the original constructor at `0xcf4e90` (declared size 6596 bytes). This tightens the bounds of the v52 census; it is **not** a census of all possible insertions into the map (other container methods, indirection, or code in other DSOs may exist).

Each of the seven registered `std::function` invokers has a common first-stage input-guard pattern: load an incoming 64-bit numeric value via its `unsigned long const&` argument, load a previously retained value from the captured detector object, compare them, take a separate branch for `incoming <= previous`, and test the difference against 1. These are compiled **edge/time-step style conditions**, consistent with the known typed edge-detector registrations. The units, downstream state events and any effects on the shared Blackboard are **not** thereby determined. No direct rewash or dock-actuator path was found by this v53 scope.

## Whole `.text` census

Scanned all aligned 32-bit instruction words in the ELF's `.text` section, decoded direct AArch64 `BL` immediates with sign extension, and counted only calls whose target exactly equals the already v52-verified map `operator[]` PLT address. The analysis is full-section rather than restricted to the constructor symbol bounds.

| Listener key | Verified direct map call | Registered invoker | First-stage input comparison |
| --- | ---: | ---: | --- |
| `awesome_search` | `0xcf5324` | `0xcf2310` | Incoming against prior value; delta=1 branch |
| `follow_wall` | `0xcf5500` | `0xcf2820` | Same pattern |
| `follow_with_chain` | `0xcf56d8` | `0xcf0d00` | Same pattern |
| `carpet_follow` | `0xcf58fc` | `0xcf1e70` | Same pattern |
| `maybe_carpet_follow` | `0xcf5adc` | `0xcf19e0` | Same pattern |
| `carpet_back_done` | `0xcf5cbc` | `0xcf1540` | Same pattern |
| `confirm_carpet` | `0xcf5eac` | `0xcf1120` | Same pattern |

**Result:** Seven direct calls in the complete `.text`; **zero direct calls** to this exact PLT destination outside the constructor. This says nothing about dynamically generated code, virtual dispatch, a different overload, other `std::map` modification APIs, or other libraries.

## Verified invoker entry pattern

All seven invokers load the incoming integer with `ldr x0,[x1]`, compare it with a retained value using `cmp x0,x1`, branch on `b.ls`, then compute and compare the difference with `1` before a conditional branch. Minor register-allocation differences do not affect that first-stage pattern. The v53 verifier validates the relevant exact instructions and narrowly accepts only the observed register variants at the remaining locations. This is **not** a complete interprocedural analysis of all callback event effects. In particular, the callback's state-machine event targets have not been individually validated, and no R2416 rewash-key producer can be assigned to them from these checks.

## Cross-reference to earlier evidence

- v46–v47 established the compiled odometry `OdomProcessSUB()` path to the retained `RobotNode` tree root and the `executeTick()` call.
- v48–v49 established that the `GlobalHook` callback starts as a no-op, but route-plugin registration can replace it with `odomProcessHook`, which enters `GlobalDispatcher::dispatch()`.
- v50–v51 established the listener loop and the BlackBoard-retaining dispatcher layout; the direct listener-call argument is the odometry-like numeric value, not a Blackboard pointer.
- v52 resolved seven constructor registration names and callback invoker pointers.
- v53 now excludes additional **direct** calls to the *same* map `operator[]` PLT entry elsewhere in that ELF; it adds identical first-stage edge checks for all seven invokers.

## Verification and reproducibility

The new script `x40_r2416_v53_listener_callsites_verify.py` is Python standard library only and imports the packaged v48–v52 scripts. It verifies full original SHA-256 pins, the three active-versus-original library byte comparisons, prior callback and registry findings, a full `.text` direct-call census, and seven independently anchored invoker entry patterns. It fails closed on changed instructions or hashes.

```
python3 x40_r2416_v53_listener_callsites_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Success marker: `X40_V53_WHOLE_TEXT_DIRECT_REGISTRATION_AND_EDGE_GUARDS_STATIC_PASS`.

## Remaining boundaries

1. No exhaustive census of **indirect** listener registration or removal is available; other APIs and DSOs remain possible.
2. Seven callback *entry guards* are verified, but their outgoing state-machine event effects and potential indirect writes have not been traced end-to-end.
3. The known `ProcessModelInfo()` producer of `special_push_clean_dish` is restricted to models other than R2416; no alternative R2416-compatible producer has been demonstrated.
4. The threshold-to-failure marker, Blackboard identity, `r2343_start_rewash` marker and actual physical dock wash are not proven as one continuous runtime path.

**Safety:** preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; no production modifications, robot commands, firmware writes or public release of the private ELF files. GitHub is unchanged by this audit.