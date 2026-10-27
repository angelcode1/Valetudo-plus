# Dreame X40 R2416 v223 — received AI command callback and dirty-mop Blackboard flag

**27 October 2026. Read-only, original SHA-pinned firmware analysis.** This branch descends from v222, preserves the corrected v195 native `RobotNode` provenance and the complete v197–v222 private-evidence regression chain. No robot commands, firmware write, running Valetudo+ modification, CleanGenius activation, original ELF, PRIVATE diagnostic JSON/ZIP, raw settings, maps, credentials or process paths are committed.

## Verified typed subscriber registration and concrete callback identity

Original `node_lethe.so`, SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, defines `AvaNodeRoute::AiDetectResult(ava_ai_new_cmd*)` at **`0x5db3e0`**. Its original code constructs a member-function callback bound to the `AvaNodeRoute` object and calls **`AsyncDeque::MultAsyncSubscribe<ava_ai_new_cmd,ava_ai_new_cmd&>`** at **`0x5db478 → PLT 0x27bbe0`**.

This is not just a matching symbol name. The original **`R_AARCH64_GLOB_DAT` relocation at GOT `0xb7a300` points to `AiDetectResultSUB(ava_ai_new_cmd*)` at `0x5dc910`**; separate GOT `0xb7e840` points to `AiDetectResult()` at `0x5db3e0`. The original member callback also uses C++ `std::_Function_handler` invoke and manager pointers. Both concrete function-value relocations are checked by the v223 full verifier and smaller independent checker.

A **compiled typed subscriber callback** is established. Whether the subscription ran successfully, received any specific message or used the same live queue as another producer is not measured.

## Received message command codes → typed Blackboard Boolean flags

`AiDetectResultSUB` copies the message's code field from `[x20,#0x10]` at `0x5dc99c–0x5dc9a0` and compares it against several constants. Three exact cases build a key and call typed **`BT::Blackboard::set<bool>`** with a byte set to **true**:

| Received code | Native command comparison | Exact key literal | Typed setter call |
|---|---|---|---|
| **5** | `0x5dc9c0` | `start_offline` at `0xa12820` | `0x5dcf84 → 0x2795c0` |
| **6** | `0x5dc9c8` | `start_material_detect` at `0xa12830` | `0x5dcfd8 → 0x2795c0` |
| **15** | `0x5dc9d0` | `ai_set_mop_is_dirty_data` at `0xa13488` | `0x5dd010 → 0x2795c0` |

The key strings, adjacent same-register ADRP+ADD address constructions, route Blackboard load and typed setter instructions are checked against the pinned original ELF. The original function also tests code **8, 9, 11 and 16** and contains several additional indirect callback branches; v223 does not classify all of their consequences.

**Interpretation limit:** The exact `ai_set_mop_is_dirty_data` name suggests a mop-dirt interface, but a compiled Boolean set does **not** prove dirt actually detected, station rewash commanded, or a physical floor reclean. No specific sender→subscriber event was captured on the robot.

## Separate outbound processing: only one direct SendAINewCmd call

Original host `AvaNodeRoute::UpdateOutput()` at `0x3daf20` contains the direct **`SendAINewCmd()`** call at **`0x3db598 → PLT 0x275de0`**. Bounded executable-host `.text` direct-BL scan **`0x2a0000–0x9c0000`** finds **exactly one** call to that PLT target. `SendAINewCmd()` at `0x5d1fd0` reads the route Blackboard (`0x5d1fec`) and tests a command-like value (`0x5d2178`).

The **inbound** `AiDetectResultSUB` flags and the **outbound** `SendAINewCmd` path are separately verified code paths. Their specific runtime causal relation, the outbound command schema and any downstream cleaning-task scheduler are **not established**. The single direct-BL count is not an exhaustive indirect, alias or cross-library caller census.

## Full reproducibility and safety

Complete source-only release: **`X40-R2416-v223-sanitized-analysis-kit.zip`**, SHA-256 **`df5dc8a0e3f28aaa4e89f1db46ffd670dbc941da3cb656359f90281e1e5634c1`**, **236,932 bytes**, **109 ZIP entries including SHA256SUMS**, **108/108 internal file hash checks** and ZIP CRC passed on clean extraction. **12/12 v223 focused tests passed from source and clean extraction** (clean test runtime 56.894s), including the complete inherited **v197–v222 native/private evidence replay**. Verifier checks **56 exact original instruction words, nine decoded direct BL targets, two GOT callback relocations, three code/key/typed-Boolean guards, and one direct outbound caller**. Mutation tests reject modified callback binding, subscriber call, selector, flag setter, inserted unanchored outbound BL, changed original ELF digest, private-field leakage and output overwrite. Full source-only ZIP also includes the independent, tested **22-word/two-relocation/three-key** checker; Python 3 standard library only. Owner-original firmware and private diagnostic archives are external inputs, not redistributed.

**Next:** trace actual consumers of `ai_set_mop_is_dirty_data` and whether any leads to dock-wash task state; separately identify runtime outbound `SendAINewCmd` payloads and a genuine stain→additional floor-clean task-start edge. Do not infer AI dirt-driven recleaning from generic keys or function names. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Robot, firmware, Valetudo+ and `master` unchanged.
