# Dreame X40 R2416 — v100: extensionless RobotNode lookup and optional-node registry boundary

**2026-10-24. Original SHA-pinned firmware evidence, offline-only.** This document is sanitized: no proprietary ELF binaries, original YAML/XML, maps, credentials, tokens or serial identifiers. No robot operations or changes.

## Finding 1 — RobotNode uses the full extensionless builder name

In original `libbehaviortree_cpp.so`, the core `BT::SubtreeConditionNode::onInit()` searches a subtree argument for its last `.` and `/` at AArch64 VAs `0x7584c` and `0x75870`. When neither exists, such as for v99's privately verified configured selector **`RobotNode`**, the guards at `0x75894` (no slash) and `0x758a0` (no dot) take the **`0x760d0`** branch. The block `0x760d0–0x76174` preserves the complete pointer/length, constructs the builder lookup name without appending `.xml`, and rejoins the ordinary native builder lookup at **`0x759b8`**.

Both extensionless `RobotNode` and dotted `StationWash.xml` (v97) reach `BehaviorTreeFactory::tree_builders()` at **`0x75de8`**, with the lookup-key handling at `0x75dd8–0x75de0`. If a registered key is found, `TreeNode::blackboard()` is retrieved at `0x75f68` and the builder is invoked at `0x75f9c`. If no registered builder is found, the existing XML file loader remains a separately guarded fallback.

**Bounded conclusion:** the compiled resolver looks up the exact native `RobotNode` name for the extensionless configured root selector. It does **not** require synthesizing `RobotNode.xml`, and it does not prove that any running process selected or ticked that root.

## Finding 2 — the optional subtree label is distinct from the default

The original `libbehaviortree_cpp.so` factory constructor explicitly registers the NUL-terminated name **`SubtreeCondition`** (literal VA `0xaa3c0`; reference `0x62edc–0x62ee0`) with the built-in `BT::SubtreeConditionNode` manifest at `0x62f20` and `registerBuilder()` at `0x62f48`.

The original `liblethe_route_nodes.so` route-plugin registration flow uses **`SubtreeConditionOpt`** (literal VA `0xf9f318`; reference `0x4f2bf0–0x4f2bf4`), calls its registration helper at `0x4f2c04 → 0x4e14c0`, and that helper calls `registerBuilder()` at `0x4e15c8`. The plugin export at `0x48cc80` delegates to `route_bt_nodes_plugin::RegisterNodes()`, which calls `utility::RegisterNodes()` at `0x48c224`. The optional class has its own native `utility::SubtreeConditionOptNode::onInit()` at `0x5b29b0`.

A byte census of **the full pinned route-plugin ELF** found exactly one `SubtreeConditionOpt\0` literal and **no exact standalone `SubtreeCondition\0` literal**. Thus the observed optional-node registration **does not itself register under the core default name**. This is a bounded static string/registration conclusion, **not** proof against computed names, another plugin, later factory registry changes or dynamic overrides. Route-plugin registration also has a library-version check at `0x48bb08–0x48bb1c`; a mapped `.so` is not proof all its registrations completed.

## Context and limits

v95–v96 proved the native `StationWash` builder's helper closure constructs 2 `ControlMachineState` and 1 `StartMachineCtrl_ELECT` nodes. v97 established the `StationWash.xml` basename lookup. v98 proved plugin discovery and shared root factory construction. v99 established `RobotNode` and `StationWash` registrations and `RobotNode`'s compiled `StationWash.xml` child. **v100 closes the different extensionless selector branch and distinguishes the optional subtree registration.**

None of these static findings is a runtime factory snapshot or observed tick. We still have no proven R2416-compatible `special_push_clean_dish` initializer, no causal bridge from `r2343_start_rewash` bookkeeping into `WASH_CONTROL`, no identified physical message receiver, and no confirmed second dirt-triggered mop wash.

## Independent validation

Owner-private SHA-256 pins:
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`
- `liblethe_route_nodes.so`: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`

The full sanitized, user-delivered ZIP `X40-R2416-v100-sanitized-extensionless-root-20261024.zip` includes `x40_r2416_v100_extensionless_root_and_opt_registration_verify.py` (Python standard library), a detailed report and README. The verifier uses the private v62 ZIP *in memory*, checks literal symbols, exact branch condition bits, ADRP+ADD and PLT relocations. **34 independently modified instruction/literal examples were refused**. The previous v99 verifier also passed its **18** existing mutation checks.

```bash
python3 x40_r2416_v100_extensionless_root_and_opt_registration_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V100_EXTENSIONLESS_ROBOTNODE_WHOLE_NAME_NATIVE_LOOKUP_STATIC_PASS
X40_V100_DOTTED_STATIONWASH_AND_EXTENSIONLESS_ROOT_SHARE_BUILDER_LOOKUP_PASS
X40_V100_CORE_SUBTREECONDITION_BUILDER_REGISTRATION_STATIC_PASS
X40_V100_ROUTE_OPTIONAL_SUBTREECONDITIONOPT_DISTINCT_REGISTRATION_PASS
X40_V100_ROUTE_PLUGIN_DIRECT_DEFAULT_NAME_LITERAL_ABSENT_PASS scoped=byte_cstring
X40_V100_TWO_REGISTERED_NATIVE_TREE_NAMES_STATIC_PASS
X40_V100_INDEPENDENT_OPCODE_LITERAL_MUTATIONS_REJECTED count=34
LIMIT: compiled registration paths are not runtime override census, factory state, tick or physical auto-rewash
```

Full verifier SHA-256: `e478a93bd3e542f82358df1457bde69c8d1897ed077b8be2e814c1f632e0ee19`. Sanitized ZIP SHA-256: `4318feeb9b15fc8a723bd824a328c47688d65121d5a65dedd2ceaae9f0c876f9`.

## Next research gate

Prefer private passive logs or a narrowly reviewed read-only observation proving the actual `RobotNode`/`StationWash` registrations and builder invocation, then child Blackboard scope and real `WASH_CONTROL` delivery. Never infer physical additional rewash from compiled constructor nodes alone. Do not inject soil signals, guess station opcodes, patch vendor firmware or toggle untested SmartAuto values.

**Safety:** last user-confirmed stable Valetudo+ **v74**, `SmartHost=0`, experimental `writeGateOpen=false`, launcher restored and v70/v73/parent/original recovery artifacts preserved. Nothing was changed on the X40 for v100.
