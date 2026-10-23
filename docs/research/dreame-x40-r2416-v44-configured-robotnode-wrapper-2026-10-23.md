# Dreame X40 R2416 — v44 configured RobotNode wrapper and factory-name audit

**Date:** 2026-10-23  
**Scope:** Offline-only instruction and literal analysis of the user's original SHA-256-pinned native libraries and the previously collected matching runtime tree libraries. No robot access, firmware writes, MIOT/AVA messages, injections, runtime restarts or Valetudo+ changes.

## Executive finding

The direct `BehaviorTreeFactory::instantiateTreeNode()` call at `node_lethe.so:0x355058` **does not instantiate `RobotNode`**. The immediately preceding calls build two `std::string` values from the identical literal `FollowWallModeDeal` (literal at `0x9d64b8`), and pass them as the factory registration and instance-name arguments. Its Blackboard argument is nevertheless read from the native `AvaNodeRoute+0x30` holder. The v43 unknown node-name finding is now resolved to an **auxiliary FollowWallModeDeal** factory construction path, not the root tree.

A different nearby call, `BT::buildTreeFromText()` at **`0x3552c8`**, builds a wrapper containing `<SubtreeCondition subtree_file_path="..."/>`. Its subtree-path value comes from the compiled native `Parameter` object at **`Parameter+0x8`**, accessed after `Parameter::GetInstance()`. The loader work in v24–v26 and the privately collected R2416 `setting.yaml` established `behavior_tree_path: RobotNode`; therefore **the configured value supplied to this wrapper is `RobotNode`**, subject to the setting actually used by the observed native process. The call passes the **same `AvaNodeRoute+0x30` Blackboard holder** as its third `buildTreeFromText` argument.

This is direct, instruction-level evidence for a *compiled, configuration-dependent tree-construction path* between the selected `RobotNode` and `AvaNodeRoute`'s Blackboard, stronger and more relevant than the auxiliary direct factory call described in v43.

## Exact original pins (unchanged)

| ELF | SHA-256 |
| --- | --- |
| `node_lethe.so` | `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` |
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

Three collected runtime tree plugins match their respective original libraries byte-for-byte. These checks are repeated through the v36–v44 verifier chain. The owner-supplied configuration selects `RobotNode` and `/tmp/lib/tree_lib//`. The original config and ELFs are deliberately **not** included in this audit package.

## Proof A — the factory call is `FollowWallModeDeal`

| Address | Operation |
| --- | --- |
| `0x9d64b8` | NUL-terminated `FollowWallModeDeal` string literal |
| `0x354fbc–0x354fc4` | Materialize the literal pointer and construct a `std::string` for the factory's registration ID |
| `0x354fc8–0x354fd0` | Construct a second `std::string` from the same literal for the instance name |
| `0x355028` | Load `x4 = [AvaNodeRoute+0x30]`, the fifth calling-convention argument |
| `0x355050` | Load first explicit name argument into `x1` |
| `0x355054–0x355058` | Set factory receiver in `x0`; call imported `instantiateTreeNode()` |

The same helper at `0x31cdc0` performs C++ `std::string` construction from the literal pointer. The relevant instructions and call targets are pinned in the verifier. Unlike the unknown-name reading in v43, both name-creation instructions are now accounted for.

## Proof B — the configured `RobotNode` wrapper

The original binary contains a literal **prefix** at `0x9d3380`:

```xml
<root main_tree_to_execute="BehaviorTree">
        <BehaviorTree ID="BehaviorTree"><SubtreeCondition subtree_file_path="
```

...and a literal **suffix** at `0x9d3400`:

```xml
"/></BehaviorTree></root>
```

This is an escaped, descriptive split representation, **not** an extracted root XML file. The code joins the parts with the selected parameter value. For the user-collected setting `behavior_tree_path: RobotNode`, the resulting wrapper corresponds to:

```xml
<root main_tree_to_execute="BehaviorTree">
  <BehaviorTree ID="BehaviorTree">
    <SubtreeCondition subtree_file_path="RobotNode"/>
  </BehaviorTree>
</root>
```

The above is a normalized reconstruction of the resulting wrapper's meaning (indentation is not the byte-for-byte generated layout).

| Address | Verified compiled operation |
| --- | --- |
| `0x3551e8–0x3551f8` | Initialize prefix string from the fixed XML literal |
| `0x355210` | Call native `Parameter::GetInstance()` |
| `0x355218–0x355230` | Load pointer/length from returned `Parameter+0x8` and construct a string from the parameter range |
| `0x355258–0x355264` | Append the parameter string to the wrapper |
| `0x3552a0–0x3552b0` | Append 25-byte fixed XML suffix |
| `0x3552b4–0x3552c0` | Reload `AvaNodeRoute` receiver and pass its `+0x30` Blackboard as the third argument |
| `0x3552c8` | Call imported `BT::buildTreeFromText()` |
| `0x3552cc–0x355308` | Move the resulting tree-object fields into `AvaNodeRoute+0xf48` and adjacent members |

This establishes that the **compiled wrapper uses the configured behaviour-tree path** and supplies the route's Blackboard to tree construction. It does **not** independently sample actual runtime values or prove which descendants tick during a wash.

## Other adjacent, auxiliary text-built trees

For completeness, the other three constructor `buildTreeFromText` calls use different static wrapper literals:

| Call | Wrapped native content |
| --- | --- |
| `0x35511c` | `SubtreeCondition(subtree_file_path=ReuseTree.xml)` |
| `0x3553f4` | `Condition(ID=GridmapInit)` |
| `0x3554e8` | `Condition(ID=TypeInterfaceInit)` |

All four tree-text builds use the same `AvaNodeRoute+0x30` holder. The `BtTask` imported-constructor direct-call census from v43 remains one call within `DebugTask`, so it should not be used to infer main-tree construction.

## What v44 resolves, and what it does not

**Now demonstrated statically:** the separate direct factory call's two names; the configured `RobotNode` wrapper's string assembly from native `Parameter`; the same `AvaNodeRoute+0x30` Blackboard holder being forwarded into that build, with the constructed tree retained in route member fields starting at `+0xf48`, alongside auxiliary text builds; and all original/runtime SHA checks.

**Still not proven:** the exact live Blackboard pointer shared by every descendant, when `Start_Map_Load` is written relative to `MapLoad` first tick, whether the `StationWash` subtree is actually ticked during normal cleaning, how `special_push_clean_dish` could be initialized on R2416 despite the known model gate, or a turbidity-triggered second dock wash. Do not infer physical rewash merely from successful construction of a tree.

**Next offline step:** trace the output tree root/result of `buildTreeFromText()` at `0x3552c8` through its stored `AvaNodeRoute` member and locate the runtime tick caller; distinguish the `RobotNode` wrapper from the three auxiliary trees. Only after that is resolved should alternate eligible `special_push_clean_dish` producers and physical wash command paths be revisited.

## Reproduction

With all bundled verifier dependencies in the same folder:

```bash
python3 x40_r2416_v44_node_name_and_robotnode_wrapper_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Success marker: `X40_V44_CONFIGURED_ROOT_WRAPPER_STATIC_PASS`.

**Safety:** This work is strictly static, offline, read-only. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not publish proprietary ELF files, the original settings YAML, credentials, maps, camera data or firmware archives. GitHub and Valetudo+ remain unchanged.