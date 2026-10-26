# Dreame X40 R2416 v195 — Configured native RobotNode reconciliation

**26 October 2026. Corrective research follow-up to v194.** The key project-level correction is that the real previously collected R2416 config selected `behavior_tree_path: RobotNode` and `tree_lib_path: /tmp/lib/tree_lib//`, whereas `cleanbot_pro/RobotNode.xml` and `/usr/lib/tree_lib` are compiled **fallbacks** for the host YAML loader. Therefore, locating a `RobotNode.xml` file is **not necessarily required** to reconstruct the effective cleaning behavior tree.

## Distinct evidence provenance

**Prior independently verified findings** (the original prior ZIP and YAML were not reacquired in v195):
- [v25 config provenance](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v25-selector-provenance-2026-10-22.md): the model's `/ava/conf/r2416.conf` identifies `/ava/conf/setting.yaml`, which `Parameter` loads via `YAML::LoadFile`.
- [v27 runtime native factory](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v27-runtime-tree-factory-2026-10-22.md): the owner had **already collected the effective YAML**, with selector `RobotNode` and tree library path `/tmp/lib/tree_lib//`; byte-identical runtime and archived tree plugins. Native `liblethe_tree.so` SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` exports registered factory `RobotNode` (builder `0x312c6c`; generated body `0x30d8c0`; factory registration `0x565c38`). The zero-byte `RobotNode.xml` in the old ZIP was a **failed-copy placeholder**, not valid vendor XML.
- [v29 child parameter](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v29-robotnode-stationwash-parameters-2026-10-22.md): generated `RobotNode` builder includes `SubtreeCondition(subtree_file_path="StationWash.xml")`. This is an instantiated native child, not runtime actuation.
- [v30 conditional resolution](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v30-stationwash-resolver-2026-10-22.md) and [v31 plugin names](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v31-plugin-registration-2026-10-22.md): the built-in resolver can strip `.xml` and look up a registered `StationWash` builder, and the checked optimized `SubtreeConditionOpt` plugin does not register under the same name as built-in `SubtreeCondition`. No actual second mop wash proven.
- [v44 native wrapper](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v44-configured-robotnode-wrapper-2026-10-23.md): the host combines a `SubtreeCondition` wrapper with the configured selector and passes the route's Blackboard into tree construction.
- [v46 virtual root tick](https://github.com/angelcode1/Valetudo-plus/blob/master/docs/research/dreame-x40-r2416-v46-odometry-root-tick-2026-10-23.md): compiled retained-root `executeTick` call from `AvaNodeRoute::OdomProcessSUB`. Static dispatch eligibility, not proof that a particular cleaning run ticked it.

**Independently reverified in v195 against locally available, SHA-pinned original host and route ELFs:**
- Original `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`; original `liblethe_route_nodes.so` SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.
- `node_lethe.so:0x3551ec–0x3551f8` builds wrapper string from native prefix at `0x9d3380`.
- `0x355210` obtains `Parameter::GetInstance`; `0x355228` loads selector pointer and length from `Parameter+0x8`; `0x355264` appends this configured value.
- `0x3552a0–0x3552b0` appends the fixed 25-byte wrapper suffix at `0x9d3400`.
- `0x3552c0` obtains `AvaNodeRoute+0x30` Blackboard, `0x3552c8` calls `BT::buildTreeFromText`, and `0x3552d8` retains the root at `AvaNodeRoute+0xf48`.
- Distinct auxiliary `FollowWallModeDeal` factory call at `0x355058` refers to the literal at `0x9d64b8`; it is **not** the main configured `RobotNode`.

These new checks pin machine-code instruction words, literal addresses, target calls and whole-file hashes. Native mutation cases intentionally flip relevant opcodes and must fail. The previously collected *raw* `setting.yaml` and *original* `liblethe_tree.so` are **not reverified against their bytes in v195**; their status is prior-source-verified, not invented or treated as a fresh measurement.

## Revised next step

Use the *already saved private firmware archive* containing **`liblethe_tree.so`** (SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`). Reconstruct the generated `RobotNode` control/decorator graph from `buildRobotNode`, preserving child factory name, parameter pairs, status gates, port bindings and parent attachments. Locate the branches containing `AiStainCheck`, `SetExtraCleanArea`, and any actual new-area task dispatch. Optional `liblethe_tactics_tree.so` expected SHA-256 `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`.

Searching for real XML remains reasonable if a *specific unresolved subtree* is proven to load from a file. A default path or a `.xml`-suffixed parameter is not evidence of an effective file dependency.

**Unproven:** installed tree registry and runtime effective configuration in this current run, actual tick of any stain subtree, AI dirt event causing a new cleaning task, and physical floor reclean. v165 spatial revisits remain unattributed.

## Reproducibility

Offline release: `X40-R2416-v195-sanitized-native-robotnode-reconciliation.zip`; SHA-256 **`c0aea5da94545c2fa2e43406a5617fd28a4dbd63f69fa3c749c8d2874563abbe`**. Contains full standard-library-only v184–v195 verifiers and tests, sanitized JSON and source-provenance report. Original two-ELF replay **277 tests passed**, including 19 v195-specific tests and mutation cases. Clean ZIP: **235 tests run; 128 passed, 107 skipped**; **42 file checksums match**. No copyrighted original ELF binaries, raw private YAML, screenshots, map coordinates, credentials, network actions or robot control code. The v194 read-only XML discovery guide is intentionally omitted to avoid prioritizing a nonessential step.

Preserve Valetudo+ v74 (`SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`). No robot access or runtime changes. `master` untouched.
