# Dreame X40 R2416 — v26 native YAML selector-branch audit

**Date:** 2026-10-22  
**Scope:** Offline-only extension of the v25 research handoff. This report contains no proprietary ELF payloads, raw user configuration, firmware extracts, device IDs, secrets, personal maps, disassembly dumps or model weights. The robot and Valetudo+ are untouched.

## Result

The pinned, original `node_lethe.so` contains **three distinct YAML-configured path loaders**: `Parameter::LOAD_behavior_tree_path`, `Parameter::LOAD_tree_lib_path`, and `Parameter::LOAD_robot_para_path`. v25 verified `Parameter::Parameter` calls `YAML::LoadFile` and invokes these loaders in order. v26 independently checks each loader's branch shape, key and fallback literal, conversion, fallback assignment, explicit invalid-node path, and destination `Parameter` field. **A fallback literal is not an unconditional runtime default** and cannot be used to infer the running X40's behaviour-tree selection.

| Loader | Entry VA | `Parameter` storage | String-conversion call | Conditional fallback `YAML::Node::Assign` | Explicit InvalidNode branch | Compiled fallback |
|---|---:|---:|---:|---:|---:|---|
| `behavior_tree_path` | `0x2c4040` | `+0x08` | `0x2c40c8` | `0x2c4194` | `0x2c4184 → 0x2c4240` | `cleanbot_pro/RobotNode.xml` |
| `tree_lib_path` | `0x2c44c0` | `+0x28` | `0x2c4548` | `0x2c4614` | `0x2c4604 → 0x2c46c0` | `/usr/lib/tree_lib` |
| `robot_para_path` | `0x2c4940` | `+0x68` | `0x2c49c8` | `0x2c4a94` | `0x2c4a84 → 0x2c4b40` | `/data/Robot_Para.yaml` |

*VA = virtual address in the original ELF, not a physical device address.*

## Evidence and bounded meaning

For each of the three loader functions, the verifier checks:

1. An initial `YAML::Node` lookup and `CBZ w0` conditional branch into a fallback-handling arm, and a normal-path `YAML::Node::as<std::string>()` call.
2. The fallback arm performs a **second** node lookup, followed by a separate `CBZ w0` to code that allocates and constructs `YAML::InvalidNode` if the node is invalid.
3. The branch's valid fallback case calls `YAML::Node::Assign(char const*)` with the corresponding compiled literal; it also constructs a string in a distinct `Parameter` field.
4. The full `node_lethe.so` SHA-256 and the other four previous SHA pins match the original R2416 firmware reference.

**Important limitation:** Static disassembly alone does not identify which runtime YAML representations cause either branch, nor guarantee that absent keys, null keys, invalid strings or an absent `setting.yaml` will fall back cleanly. It establishes the fallback and exception *possibilities*. `YAML::LoadFile` itself may fail before these loaders run. Therefore neither the compiled fallback `cleanbot_pro/RobotNode.xml` nor the registration of `StationWash` establishes that the X40 actually instantiates that tree.

The model `r2416.conf` continues to identify `/ava/conf/setting.yaml` as the Lethe configuration file. In the **supplied** `X40-Firmware-Reference.zip`, that YAML file, `RobotNode.xml` and `Robot_Para.yaml` are absent. Absence from this limited archive is not absence from the robot or from other saved rootfs images.

## Verification

From a checkout of `Valetudo-plus` with v25 and v26 tools present:

```bash
python3 util/x40_r2416_v26_selector_paths_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip
```

Expected status: `X40_V26_SELECTOR_BRANCHES_PASS`. The verifier is **read-only, standard-library-only**, checks the five whole-file SHA-256 pins and selected fixed AArch64 instructions/branch destinations; it does not execute vendor code. It imports the existing adjacent `util/x40_r2416_v25_selector_provenance_verify.py` for the pinned archive and ELF readers.

## Remaining question and next evidence

The shortest useful next input is the original `setting.yaml` from a **previously saved/extracted R2416 rootfs** (or just a locally generated, privacy-filtered record of its three selector keys and the resolved XML file's existence/hash), followed by the actual tree XML if present. Determine the literal selected `behavior_tree_path`, effective tree-library directory and the named main XML tree. Only then try to close the `StationWash` instantiation and Blackboard-sharing link. Do not publish the raw YAML/XML without reviewing it for private content. Do not infer a hardware rewash cycle or enable any CleanGenius writes from these static findings.

### Safe offline file discovery (Mac)

```bash
find "$HOME/Documents/X40-Firmware-Reference" -type f \
  \( -name setting.yaml -o -name RobotNode.xml -o -name Robot_Para.yaml \) -print
```

Also check **existing offline rootfs images/extraction directories** if the files are not directly visible; do not assume this ZIP was an entire firmware filesystem.

**Unproven:** runtime effective YAML values; `StationWash` selection; same Blackboard instance between the selected tree and `AvaNodeRoute`; an R2416-compatible producer of `special_push_clean_dish`; threshold-to-request causality; physical extra-wash actuation.

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, make no robot/MIOT/AVA writes and commit no private firmware or configuration.
