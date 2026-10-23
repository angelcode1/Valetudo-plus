# Dreame X40 R2416 — CleanGenius / automatic mop-rewash handoff (2026-10-22)

**Scope:** Documentation-only investigation of preserved original vendor native ELFs. **No source or runtime changes are authorized by this handoff.** Do not put original proprietary firmware, extracted native libraries, passwords, device identifiers, or full private disassemblies in GitHub.

## Safety / current operational state

- Rooted Dreame X40 R2416 with functioning Valetudo+.
- Preserve all existing features and local modifications.
- Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not turn on experimental writes as an exploratory shortcut.
- No live robot commands, forced dock washing, firmware patching or hardware probes are required to continue static work.
- Private original firmware archive lives on the operator's Mac: `~/Documents/X40-Firmware-Reference/R2416/X40_R2416_original_vendor_native_ELFs.tar` (not in Git).

## Original-library pins

| Library | SHA-256 |
| --- | --- |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

Previously recorded offline validation: v16 checked 52 instruction anchors and 11 literal sequences in tactics; v17 checked 45 cross-library anchors and a relocated BT parameter pair. Numbers are test scopes, not a combined count of unique sites.

## Verified configuration gates

In `StationHandle::SweepStationContorl::TurbidityRecleanAndRewashSet()`, three named configuration descriptors are constructed and passed to a shared integer lookup helper:

- A = `smart_hosting_switch` (lookup call `0x24e680`)
- B = `smart_auto_wash_switch` (lookup call `0x24e708`)
- C = `smart_auto_mop_switch` (lookup call `0x24e790`)

The compiled boolean gates assigned to class receiver offsets are:

```text
wash_gate   [this + 0x688] = B > 0 && (A == 2 || (A == 1 && B == 2))
auto_mop_gate[this + 0x689] = C > 0 && (A == 2 || (A == 1 && C == 2))
```

`WashDonePrecess()` reads `[this+0x688]` as one prerequisite. Configuration values 1 and 2 are **not** yet mapped to user-facing modes. Neither gate proves turbidity exceeded a threshold.

## Distinct native paths — do not conflate the flags

1. **Threshold decision:** `CheckIfNeedReClean()` (`0x252f00..`) compares an internal delta, `[this+0x680]-[this+0x588]`, with a computed threshold at `0x2532e8..0x2532fc`. It uses mixed-case (vendor-spelled) `TubidityRecleanFlag` with textual `true` / `false`.
2. **Error/failure branch:** `WashErrorLogicRun()` and `WashFloorTubidityCheck()` have paths setting `TurbidityResultFail = "true"`, resetting **`TubidityRecleanFlag = "idle"`**, and decrementing/re-publishing `max_rewash_cnt`. They also refer to the distinct lowercase literal `turbidity_reclean_flag`. Do not alias these keys based on similar spelling.
3. **Conditional rewash request:** `WashDonePrecess()` (`0x235000..0x235804`) checks `TurbidityResultFail` (`0x23517c`), erases it (`0x235210`), tests wash gate `0x688` (`0x23522c`), checks `special_push_clean_dish` (`0x2352b4`), then conditionally constructs and sets integer `r2343_start_rewash = 1` (preparation `0x235318`, virtual dispatch `0x235328`). Previous intraprocedural CFG found six necessary branch conditions. This is a *request-marker* path, not proof of a physical wash.
4. **BT presence check:** Original `liblethe_tree.so` generated `StationWash.xml,HandleMopAgain` builder instantiates a `BlackboardContains` node with `key=special_push_clean_dish` (builder `0x3548cc..0x3548e4`; relocated parameter pair `0x707d70`). This tests key presence, not textual value.
5. **Special-push producer:** Original `node_lethe.so` `ProcessModelInfo()` constructs `special_push_clean_dish` and calls typed `BT::Blackboard::set<int>` with integer 1 (around `0x47052c..0x470554`). Runtime path/instance matching remains unobserved.
6. **Downstream bookkeeping:** `node_lethe.so` `ancp::AvaNodeRoute::SendStationTaskTip()` checks `special_push_clean_dish`, then `r2343_start_rewash` (around `0x7ca254` and `0x7ca394`); on the relevant path it increments `wash_times` and removes `r2343_start_rewash` (`0x7ca3c4..0x7ca434`). This does not itself demonstrate a dock motor command.

## Blackboard virtual-slot resolution (v18 continuation)

Inspection of concrete `ancp::BlackboardRobinMap` and `ancp::StaticBlackboardRobinMap` vtables in `node_lethe.so` matched:

| Offset | Method |
| --- | --- |
| `+0x20` | `set(key, SafeAny::Any)` |
| `+0x28` | `contains(key)` |
| `+0x30` | `erase(key)` |

This resolves method semantics for those implementation vtables and explains the contains/erase/set sequence described above. **Dynamic Blackboard instance identity / runtime dispatch remains unproven.** The v18 mapping was established in the continuation after the v17 packaged report; re-check the exact table offsets and implementation symbols before treating it as an independent reproducible test.

## What is and is not proven

**Established from offline static code:** named switch gates, threshold comparison, failure marker writes, native key set/contains/erase roles, the `special_push_clean_dish` producer and BT presence consumer, conditional `r2343_start_rewash` set, and downstream `wash_times` bookkeeping.

**Not established:** which runtime Blackboard instance each path uses, threshold result directly causing `TurbidityResultFail` or special-push key creation, normal clean-water/turbidity state into a rewash request, whether a request reaches the physical dock washing actuator, exact meanings of settings values 1/2, or that CleanGenius is fully operational under Valetudo+.

## Recommended next investigation (offline first)

1. Reproduce the v18 vtable mapping against the SHA-pinned `node_lethe.so`, including dynamic dispatch class/receiver lineage for the two `WashDonePrecess` contains calls and subsequent erase/set calls.
2. Track the producer(s) and consumers of `TurbidityResultFail`, `TubidityRecleanFlag`, lowercase `turbidity_reclean_flag`, and `special_push_clean_dish` **as distinct entries**, using bounded interprocedural dataflow and BT edges. Explicitly test whether any normal threshold outcome can satisfy the rewash-request prerequisites without an error marker.
3. Identify physical dock command/publish boundary downstream of `r2343_start_rewash` (versus only `wash_times` bookkeeping), still offline.
4. Only if static evidence leaves a genuinely unavoidable question should a separately authorized, short, read-only live observation be proposed; do **not** enable experimental write flows.

## Earlier evidence retained outside Git

Private local audit chain v3.1–v15; sanitized reports v16 `x40-r2416-v16-turbidity-rewash-keyflow.{md,json}`, v17 `x40-r2416-v17-cross-library-rewash-review.{md,json}`. Only summaries and checksums are committed here. Don't publish the original ELF archive.

**Handoff status:** Documentation-only; no firmware changes, no live robot access and no Valetudo+ code changes. This file should be used as the starting point in the next conversation.


## v19–v25 offline continuation (2026-10-22)

See [v25 selector-loader provenance and remaining evidence boundary](./dreame-x40-r2416-v25-selector-provenance-2026-10-22.md) and its independent [offline verifier](../../util/x40_r2416_v25_selector_provenance_verify.py). Follow-on static work verified the `AvaNodeRoute` Blackboard holder passed to several initialization trees, the registered `StationWash` builder, and native `Parameter` YAML-file loading and selector parsing. The actual `/ava/conf/setting.yaml`, effective `RobotNode.xml` selection, R2416-compatible `special_push_clean_dish` producer and physical rewash remain unproven. No live robot access or experimental writes were performed. Keep original firmware and unredacted config out of Git.


## Offline continuation v26–v32 (2026-10-23)

The v26–v32 sanitized reports and their SHA-pinned, standard-library-only verifiers are now in `docs/research/` and `util/`. They build on v25 without changing Valetudo+ production code.

- The privately collected effective `setting.yaml` selects `behavior_tree_path: RobotNode` and `tree_lib_path: /tmp/lib/tree_lib//`. All three observed active tree plugins have exact SHA-256 matches to the original native libraries; private configuration and binaries are not published.
- The compiled `RobotNode` builder includes `SubtreeCondition(subtree_file_path=StationWash.xml)`; the built-in resolver has a registered-builder lookup that can turn the simple basename into `StationWash`, forwarding the Blackboard. The checked route plugin separately registers `SubtreeConditionOpt`, not an automatic override of `SubtreeCondition`.
- The v32 bounded local parent audit confirms adjacent generated control-parent child attachment for `StationWash.xml` and `RobotDropCharger`, without a generated depth/decorator call between them. The intervening builder helper and enclosing control-parent runtime tick condition remain unresolved.
- No additional direct literal producer of `special_push_clean_dish` was established in the five primary pinned ELFs. The identified `ProcessModelInfo` producer is gated to other model identifiers, not R2416. Do not treat a negative exact-literal census as proof there is no dynamically generated or inherited key.
- **Unproven:** live registry/Blackboard identity, normal turbidity causing `TurbidityResultFail` and `r2343_start_rewash`, or any physical second dock wash. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not enable experimental write controls, change the robot, or commit raw private ELFs/configuration.

## Offline continuation v33–v36 (2026-10-23)

The public v33–v35 summary notes and v36 compact verifier extend the earlier v32 SHA-pinned studies. Complete independent v33–v36 packages are retained privately; no original native ELF or raw device configuration has been committed.

- v33 verifies a balanced generated nested helper and a SequenceStarRoF → Loop → DoWhile construction-depth stack surrounding StationWash.
- v34 verifies the bounded DoWhile direct-attachment order: StationWash is site 23, followed by RobotDropCharger at site 24. This is a compiled site count, not a live tick.
- v35 verifies SequenceStarRoF status-dependent advancement, Loop status behavior with num_cycles=-1, and 15 direct root attachments preceding the Loop.
- v36 names those 15 direct pre-Loop nodes. They include Blackboard initialization, MapLoad, RobotSysInit, StationSysInit, RobotmodeInit, AlwaysSuccess.xml and CountryGet.xml. One robot_power_on literal has a zero-length value, not a proven Boolean. The compact verifier imports the existing v32 hash-pinned loader.

The actual statuses of these initialization nodes, an R2416-compatible special_push_clean_dish producer, a shared effective runtime Blackboard, turbidity-caused rewash requests and any physical second dock wash remain unproven. Keep VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0, and make no firmware or runtime changes as part of this documentation research.


## Offline continuation v37–v48 (2026-10-23)

The individually checked sanitized v37–v48 reports are retained under `docs/research/`, and their offline Python verifiers under `util/`. v37–v47 use the full v36 verifier dependency (also retained in `util/`); v48 is self-contained. All use the previously collected, full-SHA-pinned private archives and do not change firmware, production Valetudo+ or robot state.

- v37–v40: the pre-Loop child gates were narrowed. CountryGet uses ForceSuccess but preserves running status; MapLoad, RobotSysInit and StationSysInit start under SequenceStarRoF and RobotmodeInit uses IfThenElseStarRoF. These are compiled control-flow observations, not successful runtime initialization claims.
- v41–v43: there are multiple compiled Start_Map_Load setters using distinct Blackboard access patterns. `AvaNodeRoute+0x30` is forwarded into several tree-build paths, but matching member offsets across classes and key literals do not establish all runtime Blackboard pointers coincide.
- v44: the direct factory call at `0x355058` creates auxiliary `FollowWallModeDeal`, not the configured main tree; the `buildTreeFromText` path at `0x3552c8` creates a wrapper from the selected `behavior_tree_path: RobotNode` and uses `AvaNodeRoute+0x30`.
- v45–v47: the configured tree root is retained at `AvaNodeRoute+0xf48`. `ProcessEveryTick()` is a no-op, but the odometry subscription dispatch has a compiled retained-root `executeTick()` call. Three upstream branch detours have conditional rejoin paths; a null pre-tick callback enters an exception path. Static reachability does not establish successful live ticks.
- **v48:** both checked native libraries have a one-instruction `ret` default `route_nodes::GlobalHook` callback, installed through verified `std::function` manager/invoker relocations. `OdomProcessSUB()` invokes the callback immediately before the root tick. **The active callback may be replaced at runtime**; no immutable callback or successful tick claim is made.

**Still unproven:** any R2416-compatible producer of `special_push_clean_dish`, normal turbidity threshold leading to `r2343_start_rewash`, runtime Blackboard identity throughout the wash subtree, or a second physical dock wash. Maintain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; do not publish original vendor ELFs, private settings, identifiers or complete disassembly.
