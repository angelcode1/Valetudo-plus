# Dreame X40 R2416 — v25 selector-loader provenance and remaining evidence boundary

**Date:** 2026-10-22  
**Scope:** Offline-only follow-up to the v19–v24 CleanGenius/rewash audits. This document contains no vendor binaries, private configuration values, maps, credentials, disassembly dumps, or device identifiers.

## New v25 finding

The SHA-pinned `node_lethe.so` provides an instruction-level chain between its incoming configuration path and three selector loaders:

1. `Parameter::Parameter(std::string const&)` saves its constructor path argument in `x23` (`0x2bde74`). At `0x2be18c`, it moves `x23` to `x0` and calls the imported **`YAML::LoadFile`** at `0x2be198` (PLT target `0x279840`). Thus the parameter loader reads a YAML file selected by its input path, rather than using only compiled defaults.
2. The constructor then calls, in sequence, `Parameter::LOAD_behavior_tree_path` at `0x2be310`, `Parameter::LOAD_tree_lib_path` at `0x2be31c`, and `Parameter::LOAD_robot_para_path` at `0x2be328`. Each call receives the same YAML subnode argument (`x20`) and the same `Parameter` object (`x19`).
3. `Parameter::GetInstance(std::string const&)` invokes the constructor via `0x3901cc` in its singleton-initialization path. This is evidence of a guarded, first-initialization configuration object, **not** evidence about what was loaded on the X40 at runtime.
4. The model's `AvaNodeLethe` entry in the supplied `/ava/conf/r2416.conf` specifies `config_file_path: /ava/conf/setting.yaml`. The actual `setting.yaml` is still absent from the provided ZIP; the original TAR contains native ELF libraries only. Neither `RobotNode.xml` nor `Robot_Para.yaml` is present in the provided ZIP.

The previously identified compiled fallbacks remain `cleanbot_pro/RobotNode.xml`, `/usr/lib/tree_lib`, and `/data/Robot_Para.yaml` for the three loader keys. **Fallback strings do not establish the effective file paths, tree selection, or presence of those files.**

## What was checked

The accompanying offline v25 verifier accepts the saved `X40-Firmware-Reference.zip`; it checks **all five whole-file SHA-256 pins** for `node_lethe.so`, `liblethe_tactics_tree.so`, `liblethe_tree.so`, `liblethe_route_nodes.so`, and `libbehaviortree_cpp.so` (the same pins in the v24 report), verifies R2416's config-file reference, verifies fixed AArch64 instruction anchors and decoded direct-call destinations, and checks literal loader-key/fallback locations. It does not execute any firmware.

Validation result: `X40_V25_SELECTOR_PROVENANCE_PASS`.

Negative tests: a modified `node_lethe.so` was rejected by the whole-file SHA gate; an optional offline directory inventory refused to follow a `setting.yaml` symlink. Neither test involved the robot.

## Updated research dependency chain

The historical v19–v24 audits established a model-gated producer for `special_push_clean_dish`, a shared holder within `AvaNodeRoute`, four `BT::buildTreeFromText` constructor calls using that holder, registration of `StationWash` by `liblethe_tree.so`, and the selector-config path. v25 adds the actual `YAML::LoadFile` argument/call chain and sequential selector parsing.

**Still unproven:** that X40 R2416 selects `StationWash`; that the selected tree's Blackboard is the `AvaNodeRoute` holder; that any alternative producer initializes `special_push_clean_dish` on R2416; that positive turbidity evidence meets the conditional rewash prerequisites; and that a rewash request leads to a physical second mop-wash cycle. No new claim of working CleanGenius or automatic rewash is warranted.

## Minimal next collection — archived files first

On the operator's Mac, search **existing offline archives/extracted rootfs** before touching the running vacuum:

```bash
find "$HOME/Documents/X40-Firmware-Reference" -type f \
  \( -name setting.yaml -o -name RobotNode.xml -o -name Robot_Para.yaml \) -print
```

If the owner has a *previously extracted* rootfs, the verifier supports `--rootfs /path/to/rootfs` and reports only existence, size and SHA-256 for a fixed shortlist of config/tree path candidates; it neither prints nor packages private file contents. Candidate absence is **not** proof that no such XML exists under a different path or in an uncollected image.

Once `/ava/conf/setting.yaml` is located, inspect it **privately** to resolve only `behavior_tree_path`, `tree_lib_path`, and `robot_para_path`; use the effective `behavior_tree_path` to identify the exact tree definition and its `StationWash` remapping, if any. Do not publish the raw YAML or proprietary XML. If absent from all offline sources, stop at this evidence boundary; an independently authorized read-only collection would be a separate action.

## Reproduce

```bash
python3 util/x40_r2416_v25_selector_provenance_verify.py \
  "$HOME/Downloads/X40-Firmware-Reference.zip"

# Optional, only if an offline extracted rootfs already exists:
python3 util/x40_r2416_v25_selector_provenance_verify.py \
  "$HOME/Downloads/X40-Firmware-Reference.zip" \
  --rootfs "$HOME/Documents/X40-Firmware-Reference/extracted-rootfs"
```

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No robot access, AVA/MIOT writes, live hooks, firmware modification, or Valetudo+ behavior changes occurred in v25. All proprietary firmware and complete disassemblies remain private.
