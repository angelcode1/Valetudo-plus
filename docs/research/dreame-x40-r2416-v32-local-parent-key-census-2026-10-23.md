# Dreame X40 R2416 — v32 RobotNode local-parent and eligibility-key census

**Scope:** Offline inspection of the owner's original SHA-256-pinned R2416 libraries and the previously collected matching runtime tree-plugin inventory. This report extends v26–v31; it does not demonstrate robot-time tree ticks, a working automatic-rewash chain or dock actuation.

## Verified v32 result

The active `tree_lib_path` in the owner's locally collected `setting.yaml` is `/tmp/lib/tree_lib//`, and its observed directory inventory contained exactly `liblethe_tree.so`, `liblethe_tactics_tree.so`, and `liblethe_route_nodes.so`. All three active hashes match the separately preserved originals. Each original ELF exports `BT_RegisterNodesFromPlugin`. These facts make **the observed tree-plugin candidate set** explicit, rather than relying only on hypothetical additional tree libraries. They do **not** prove every candidate successfully registered in a live process or exclude plugins loaded from elsewhere.

In generated `RobotNode` code within the pinned `liblethe_tree.so`, the immediate compilation order at the relevant region is:

| Address | Statically verified operation |
|---|---|
| `0x30ee1c`, `0x30ee28` | Instantiate `StationKeyProcess`, attach as control-parent child |
| `0x30ee30` | Call another generated builder helper (`0x2edb70`) |
| `0x30ee58`, `0x30ee64`, `0x30ee68` | Instantiate `SubtreeCondition(subtree_file_path=StationWash.xml)`, attach and register child |
| `0x30ee8c`, `0x30ee98`, `0x30ee9c` | Instantiate `SubtreeCondition(subtree_file_path=RobotDropCharger)`, attach and register child |

The verifier checks the exact parameter pairs for the last two constructs, the constructor/callback calls, and the absence of **direct** `increase_depth`, `decrease_depth` or `decorator_parent_setChild` calls between their factory/attachment sites. This establishes **local generated attachment at the same apparent depth** for `StationWash` and `RobotDropCharger`. The intervening helper is not assumed to be depth-neutral, so `StationKeyProcess` is **not** claimed to be their sibling. The enclosing control-parent type, behavioural condition and tick sequence remain undecoded; static child instantiation is not a tick.

## `special_push_clean_dish` boundary

Across the five primary pinned native libraries, a bounded exact-literal census still finds that key only in `node_lethe.so`, `liblethe_tactics_tree.so`, and `liblethe_tree.so`; the route-nodes plugin and base behaviour-tree library have no such exact literal. The two direct `ADRP+ADD` references in `node_lethe.so` remain at `0x47052c` (the model-gated `ProcessModelInfo` setter) and `0x7ca20c` (downstream presence check). This repeats the v20/v21 negative evidence while explicitly matching the now-verified active tree-plugin set. The setter's compiled model allowlist includes `dreame.vacuum.r2432`, `mova.vacuum.r2432b` and `dreame.vacuum.r9420`, **not** `dreame.vacuum.r2416`.

This scan does **not** rule out a name built dynamically, Blackboard parent inheritance, external registration, uncollected modules, or a different runtime model identifier. Nor does it show that a positive normal turbidity-threshold result supplies `TurbidityResultFail`, a valid wash gate and `special_push_clean_dish` to `WashDonePrecess()` on the same effective Blackboard.

## Reproducibility

The accompanying standalone `x40_r2416_v32_local_parent_verify.py` uses only the Python standard library. It repeats v28–v31 checks, verifies the five original whole-file SHA-256 pins and exact equality for the three preserved original/runtime tree libraries, checks `setting.yaml` selectors, then validates the v32 fixed instruction and literal anchors. A modified input ELF is rejected at its hash check. Run:

```bash
python3 x40_r2416_v32_local_parent_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected final marker: `X40_V32_LOCAL_PARENT_AND_KEY_CENSUS_PASS`.

### Proven versus unresolved

- **Proven in the compiled build:** effective tree selector (`RobotNode`), observed tree-plugin candidates and hashes, distinct built-in `SubtreeCondition` versus plugin `SubtreeConditionOpt` registrations, conditional native `StationWash` name resolution, local child-attachment sequence, and bounded special-push direct-reference census.
- **Unresolved:** identity and conditions of the enclosing station-wash control node; successful plugin registration at runtime; active Blackboard instance lineage; any R2416-reachable alternative eligibility-key producer; normal turbidity leading to the `r2343_start_rewash` request; and a physical additional mop wash.

Keep `TubidityRecleanFlag`, `turbidity_reclean_flag`, `TubidityState`, `TurbidityResultFail`, `special_push_clean_dish` and `r2343_start_rewash` distinct.

## Suggested next offline investigation

Identify the control-parent/decorator ancestor governing the two children by recovering the generated depth stack across the `0x2edb70` helper and its caller, then trace its tick guards. Separately, consider the actual Blackboard scope/ownership and dynamic producer possibilities for `special_push_clean_dish`. Do not infer X40 support merely from code existing for other model IDs.

**Safety and repository policy:** No SSH, MIOT/AVA writes, firmware edits, Valetudo+ configuration changes or robot tests were performed. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; keep proprietary ELFs, unredacted device configuration, MAC/device identifiers, maps, credentials and disassemblies outside the public repository. Commit only this sanitized report and verifier.
