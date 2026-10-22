# Dreame X40 R2416 — v27 effective selector and native tree-factory audit

**Date:** 2026-10-22  
**Method:** Offline inspection of the owner's `X40-R2416-v27.zip` and prior SHA-pinned X40 research. No live robot access, device commands, MIOT/AVA writes, firmware execution, or Valetudo+ changes were involved in this analysis. This report is sanitized; it does not reproduce vendor libraries, disassembly, runtime configuration contents, personal maps or credentials.

## Result

The collected `setting.yaml` specifies `behavior_tree_path: RobotNode`, `tree_lib_path: /tmp/lib/tree_lib//` and `robot_para_path: /data/Robot_Para.yaml`. These are **observed configuration values**, not inferred fallbacks. They correct the former assumption that the relevant tree must be an XML file at `/usr/lib/tree_lib/cleanbot_pro/RobotNode.xml`.

The three tree libraries collected from `/tmp/lib/tree_lib` have the **exact SHA-256 hashes** used by the earlier offline analysis:

| Library | SHA-256 |
|---|---|
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `liblethe_tactics_tree.so` | `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c` |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` |

The TAR and independent ZIP copies of all three libraries are byte-identical. Directory timestamps of 1970 are not informative about runtime execution or compile dates. The zero-byte `RobotNode.xml` in the ZIP is a failed-copy placeholder and **is not vendor XML**.

## New native builder-to-configuration match

Independently verified in `liblethe_tree.so`, through exported ELF symbols, AArch64 name preparation, calls to `BT::BehaviorTreeFactory::registerTreeBuilder`, and `R_AARCH64_GLOB_DAT` relocations:

| Registered builder name | Function / ELF VA | Registration call | Relocated GOT slot |
|---|---|---|---|
| `RobotNode` | `buildRobotNode()` at `0x312c6c` | `0x565c38` | `0x7b1c48` |
| `StationWash` | `buildStationWash()` at `0x358540` | `0x566278` | `0x7b1c50` |

`buildRobotNode()` calls `init_fac` at `0x312ca0`, then enters the large compiled generated builder body at `0x30d8c0` via a direct call at `0x312ca4`. The native library contains hundreds of generated `RobotNode.xml,...` node-location descriptors; these are embedded compiler-generated strings, not evidence of an XML file on the runtime filesystem.

Thus the configured value **matches an actually registered native factory key**. Runtime success of factory selection/ticking is still not observed in these archives.

## Negative reference census (bounded)

For the pinned `liblethe_tree.so`, a full `.text` scan of **direct ADRP + ADD-immediate reference pairs** targeting the *exact NUL-terminated* factory string `StationWash` at `0x578590` finds one pair, at `0x566240` and `0x566244`, in factory registration. A separate direct AArch64 `BL` target scan finds **no direct calls to `buildStationWash()`** in the tree library, including the compiled `RobotNode` generated-builder body.

This does **not** prove that `StationWash` is never instantiated. Calls may go through the registered factory's indirect function pointers, through runtime-selected subtree IDs, or through other native code. It only rules out those two *specific direct-reference mechanisms* in the inspected pinned file.

## Remaining causal gap

```text
R2416 setting.yaml: behavior_tree_path = RobotNode           [observed]
        |
        v
liblethe_tree.so registers RobotNode -> buildRobotNode      [verified compiled]
        |
        v
compiled RobotNode generated builder                         [verified compiled]
        |
        ?  dynamic station-wash selection and Blackboard propagation
        v
registered StationWash -> buildStationWash                   [verified compiled]
        |
        ?  runtime Blackboard identity / keys
        v
WashDonePrecess() requires failure marker, wash gate,
  special_push_clean_dish; request r2343_start_rewash = 1    [prior compiled finding]
        |
        ?  command delivery / physical dock rewash
```

The only *directly verified* `special_push_clean_dish` initializer from earlier v20–v22 work checks three non-R2416 model IDs. The v27 scan does not provide evidence for an alternative R2416 key producer. Neither the configured `RobotNode` selection nor station builder registration establishes that normal dirty-water detection leads to a second physical mop wash.

## Reproduce

```bash
python3 x40_r2416_v27_runtime_tree_verify.py ~/Downloads/X40-R2416-v27.zip
```

Expected ending: `X40_V27_RUNTIME_TREE_REGISTRATION_PASS`, followed by an explicit runtime-causality boundary. The script uses Python's standard library, reads the archive in memory, compares the duplicate TAR and ZIP entries, verifies complete SHA-256 pins, the effective selector entries, ELF64/AArch64 symbols, GOT relocations, factory registration branches, and the bounded direct-reference census.

An intentionally modified tree-library copy was rejected with `SHA-256 pin mismatch: liblethe_tree.so` in a separate offline test.

## Recommended next step, still offline

Trace the **native factory/tree execution-selection call sites** in `node_lethe.so` using the previously collected original SHA-pinned firmware archive. Distinguish `RobotNode` (factory tree ID) from a disk XML path, and trace any dynamic selection or subtree routing to `StationWash`; then examine how the `BT::Blackboard` argument is propagated. Do not assume a subtree is selected just because both are registered. No further robot pull or command is warranted on current evidence.

**Hard boundary:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and the working Valetudo+ deployment unchanged. Do not upload proprietary ELF/TAR, unredacted YAML, camera or map data, or full disassemblies to the public repository.
