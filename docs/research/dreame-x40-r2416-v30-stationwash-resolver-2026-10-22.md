# Dreame X40 R2416 — v30 StationWash native-subtree resolver audit

**Scope:** Read-only, private/offline static analysis of the user's original SHA-256-pinned native firmware libraries and matching collected runtime tree libraries, extending v29. **No changes to the X40, firmware, Valetudo+, or public repository.** No vendor ELF, full disassembly, credentials, personal maps, images, or complete private YAML are embedded here.

## Finding

The generated `RobotNode` body constructs a `SubtreeCondition` with `subtree_file_path=StationWash.xml` (v29). The **built-in** `BT::SubtreeConditionNode::onInit()` in the pinned `libbehaviortree_cpp.so` contains a pathname parsing and builder-map dispatch path which, for this exact simple filename, derives **`StationWash`** from `StationWash.xml`, probes registered tree builders and conditionally invokes the selected builder **with the node's Blackboard**. Separately, the pinned `liblethe_tree.so` registers `StationWash` with `buildStationWash(...)` (verified by named symbol and dynamic relocation), and that builder forwards the provided Blackboard to tree initialization.

This **closes the previously unverified compiled name-resolution gap**; it is not evidence the branch executes on the robot, that the effective node registration is the built-in one, or that an actual wash is triggered.

## Exact static relationship

1. **Configured main tree:** the collected `setting.yaml` selects `RobotNode` and `/tmp/lib/tree_lib//`; those runtime libraries match the original pinned libraries byte-for-byte (v27).
2. **Generated child:** `liblethe_tree.so:0x30ee48..0x30ee58` builds a `SubtreeCondition` using a pair table at `0x6f8350` whose `subtree_file_path` value is `StationWash.xml` (v29).
3. **Built-in parameter parser:** `BT::SubtreeConditionNode::onInit()` at `0x757b0` calls `std::string::find_last_of` using `.` (site `0x7584c`) and `/` (site `0x75870`). Its no-directory, nonempty-extension-prefix case reaches the basename-construction code (`0x76008..`). For `StationWash.xml`, that basename is `StationWash`. The substring result is then used for cache/registry lookup. This is an instruction-level trace, not host execution of firmware.
4. **Map and callback:** the same `onInit()` has a cached subtree lookup (around `0x759e8`), a registered `BehaviorTreeFactory::tree_builders()` lookup (`0x75de8`) on a conditional path, and an indirect registered-builder callback (`0x75f9c`). Immediately before that callback, it obtains the node's Blackboard at `0x75f68` and forwards the Blackboard pointer in `x2` at `0x75f8c`. A *different conditional path* invokes `buildTreeFromFile()` at `0x75bb0`. Avoid claiming every filename necessarily takes the same path.
5. **Native StationWash target:** the pinned tree library registers the literal `StationWash` (`0x578590`) with `buildStationWash()` at `0x358540`; the callback's dynamic relocation is at `0x7b1c50`, and the builder forwards the provided Blackboard to the initialization helper (prior v23 verification, repeated in v30).

## Meaning and important limits

| Question | v30 static evidence |
| --- | --- |
| Is `StationWash.xml` a real compiled `RobotNode` subtree parameter? | **Yes**, v29/v30 verified. |
| Does the built-in resolver have an extension-stripping path yielding `StationWash`? | **Yes**, for the simple filename case. |
| Is a native `StationWash` callback registered in the pinned library? | **Yes**, native registration and relocation verified. |
| Does the registered-builder invocation forward a Blackboard? | **Yes**, compiled argument flow in built-in resolver and native builder. |
| Is the actual node registration guaranteed to remain the built-in one? | **Not established.** Runtime registration order and possible plugin override still require proof. |
| Does a real R2416 job tick this child and share the effective wash-state Blackboard? | **Not established.** Compiled structure and argument transfer are not runtime execution. |
| Is `special_push_clean_dish` produced for R2416? | **Not established.** The only specifically identified literal producer is gated to three other model IDs (v20–v22). |
| Does normal turbidity cause another physical mop wash? | **Not established.** The downstream request marker and physical actuation chain remain unproven. |

In particular, do not conflate `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, `special_push_clean_dish`, and `r2343_start_rewash`. The known `WashDonePrecess()` request path requires a failure marker, a wash-mode gate, and presence of `special_push_clean_dish`; this audit does not prove that a normal dirtiness threshold satisfies these requirements.

## SHA-256 pins

- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`
- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`
- `liblethe_route_nodes.so`: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

## Reproduction

```bash
python3 x40_r2416_v30_stationwash_resolver_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V30_STATIONWASH_RESOLVER_STATIC_PASS`.

The standalone verifier uses only Python's standard library. It first runs the v28/v29 hash, origin/runtime, factory, parameter-table and registration checks, then checks the delimiter literal references, basename branch instructions and destinations, registered-builder lookup, function-pointer invocation, node-Blackboard forwarding and native StationWash callback forwarding. It deliberately does not execute, inject, load or modify any ARM firmware.

## Next bounded offline questions

1. Audit the order of `BT_RegisterNodesFromPlugin` calls and the effective `SubtreeCondition` registration mapping to reduce the plugin-override uncertainty.
2. Trace the generated parent control/decorator chain around the `StationWash.xml` subtree and its possible tick eligibility; distinguish structural presence from job-time execution.
3. Look for R2416-reachable producers or inherited entry injection for `special_push_clean_dish` without treating absence of a direct literal as a global proof of absence.
4. Only after eligibility and Blackboard lineage are established should the downstream dock publish/actuator chain be considered. Continue offline; do not enable experimental CleanGenius writes.

**Operational guardrail:** `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; preserve the existing Valetudo+ installation and all local functionality.
