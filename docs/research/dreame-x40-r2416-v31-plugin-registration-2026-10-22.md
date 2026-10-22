# Dreame X40 R2416 — v31 plugin-registration and StationWash adjacency audit

**Scope:** Private/offline analysis of the owner's original SHA-pinned R2416 native libraries and previously collected matching runtime tree libraries. This report is sanitized: it contains no firmware binaries, extracted disassemblies, raw configurations, credentials, maps, or device-identifying data. No robot commands, Valetudo+ runtime changes, or firmware writes were performed.

## Result — default versus optimized `SubtreeCondition`

v30 demonstrated that the **built-in** `BT::SubtreeConditionNode` can resolve `StationWash.xml` to the registered `StationWash` builder, forwarding its Blackboard. The v30 uncertainty was whether native plugins change that node registration.

The **checked route-nodes plugin does not register the optimized node under the built-in name**:

| Binary | Registered node name / implementation | Static evidence |
| --- | --- | --- |
| `libbehaviortree_cpp.so` | `SubtreeCondition` → `BT::SubtreeConditionNode` | Built-in factory constructor, string reference `0x62edc`, registration `0x62f48` |
| `liblethe_route_nodes.so` | `SubtreeConditionOpt` → `utility::SubtreeConditionOptNode` | Exact NUL-terminated registration literal at `0xf9f318`, reference `0x4f2bf0`, typed builder setup at `0x4f2c04..0x4f2c38` |

The published `BT_RegisterNodesFromPlugin` entry in the route-nodes ELF (`0x48cc80`) branches to its registration routine. The optimized node therefore has a **distinct factory key**, not an alias that automatically shadows `SubtreeCondition`. Similarly named classes or prefixes are not interchangeable.

The built-in `BehaviorTreeFactory::registerBuilder` implementation checks for an existing name and follows an exception-construction/throw path when a duplicate is found (code at `0x5e22c..0x5e328`). The examined native plugin ELFs have no *direct dynamic-symbol import* of `unregisterBuilder`. Taken together, this **reduces** the plausibility of silent registration override by the checked plugins. It does **not** rule out an uncollected plugin, indirect registration manipulation, or all other possible runtime behavior.

## Actual AVA registration mechanism

`node_lethe.so`'s `AvaNodeRoute` constructor:

1. Obtains the configured plugin-library path through the `Parameter` object (v25/v27).
2. Opens and enumerates the plugin directory (`opendir` at `0x350e14`, `readdir` at `0x350e5c`), filtering the entries in the compiled loop.
3. Constructs `BT::BehaviorTreeFactory` at `0x350e80` (whose constructor supplies the built-in registrations).
4. Invokes `BehaviorTreeFactory::registerFromPlugin` at `0x350f00` for discovered plugin files, with a surrounding builder-count observation.

The one direct `registerFromPlugin` call site and directory-driven enumeration were verified against the pinned `node_lethe.so`. **Directory iteration order and successful registration of every candidate on the actual robot are not proven by offline static code.** This audit has not inspected a live factory registry.

## `RobotNode` child adjacency (bounded finding)

The generated `RobotNode` builder contains **two adjacent** `SubtreeCondition` child-instantiation sequences with the following parameter pairs:

| Compiled child call | `subtree_file_path` | Child-added helpers |
| --- | --- | --- |
| `0x30ee58` | `StationWash.xml` | `control_parent_addChild` at `0x30ee64`; `nodes_push_back_child_node` at `0x30ee68` |
| `0x30ee8c` | `RobotDropCharger` | `control_parent_addChild` at `0x30ee98`; `nodes_push_back_child_node` at `0x30ee9c` |

Both are compiled under a control-parent child-attachment mechanism. **No claim is made that these are the only branches of the parent, that the parent control's runtime condition is decoded, or that `StationWash` is ticked.** `RobotDropCharger` is an adjacent generated subtree, not evidence of a physical dock-wash event.

## What this changes and does not change

- **Stronger:** `RobotNode` is the configured tree (v27), its generated child contains `StationWash.xml` (v29), the built-in resolver can dispatch to the compiled `StationWash` builder using the node Blackboard (v30), and the checked route plugin registers `SubtreeConditionOpt` under a *different name* (v31).
- **Not established:** all plugins and their runtime order/registry state, actual tick of the StationWash child, exact identity and mutability of every Blackboard at runtime, an R2416-reachable alternate writer of `special_push_clean_dish`, or the second physical mop wash.
- The only specifically established direct initializer for `special_push_clean_dish` is still gated to other model identifiers (v20–v22). Do **not** infer that normal R2416 turbidity causes `TurbidityResultFail` plus this key plus `r2343_start_rewash`.
- Keep separate `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, `special_push_clean_dish`, and `r2343_start_rewash`.

## Reproduce and test limitations

```bash
python3 x40_r2416_v31_plugin_registration_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected terminal marker: `X40_V31_PLUGIN_REGISTRATION_STATIC_PASS`.

The verifier enforces **all five original whole-file SHA-256 pins**, the three original/runtime byte comparisons, and the complete v28–v30 static code/table/relocation checks, then adds name/registration/duplicate-name/plugin-loader/sibling assertions. It uses Python's standard library only and does not execute the native libraries. A private negative self-test additionally passes a deliberately modified library to the hash-checking function, which correctly rejects it. The standalone verifier is purposefully narrowly tied to this particular firmware build; it is not an emulator or runtime proof.

## Next constrained investigation

1. Identify the **compiled control/decorator ancestor** governing the `StationWash.xml` child, including any task-status or charging gates, without assuming that child construction equals a tick.
2. Trace the remaining R2416-compatible initialization/inheritance possibilities for `special_push_clean_dish` with precise object/Blackboard ownership. Its known native initializer remains gated away from R2416.
3. Only after those prerequisites are demonstrated should any downstream wash-control publication be interpreted as potential physical automatic rewash.

**Operational boundary:** keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No experimental writes, MIOT/AVA commands, live instrumentation, vendor binary publication, or modification of the existing Valetudo+ installation.
