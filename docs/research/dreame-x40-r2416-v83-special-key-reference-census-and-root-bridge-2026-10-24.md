# Dreame X40 R2416 — v83: special-key reference census and shared root Blackboard

**2026-10-24 · Offline-only, owner-private, SHA-256-pinned original AArch64 ELF evidence.** The original vendor binaries, maps, tokens and raw native MIOT payloads are not committed. The installed X40 and its verified v74 safety configuration are unchanged.

## Executive finding

A bounded full-.text direct ADRP+ADD reference census of the exact literal `special_push_clean_dish` in the original `node_lethe.so` identifies exactly **two** references within the audited six-instruction pairing window:

- `ProcessModelInfo()`, reference at `0x47052c/0x470530`. It stages integer `1` at `0x470540` and invokes **typed Blackboard::set<int>** at `0x470554`. The `dreame.vacuum.r2416` equality branch at `0x470940` goes to **`0x470958`**, not the known special-key initialization segment `0x4704e8` (v82). The known model matches feeding that segment are different models.
- `AvaNodeRoute::SendStationTaskTip()`, reference at **`0x7ca20c/0x7ca210`**. It gets the native root Blackboard through a route member at `0x7ca1dc`, zero-initializes a local integer result at `0x7ca2b0`, and invokes **typed Blackboard::get<int>** at **`0x7ca2b4`**. This is a *reader*, not a new R2416 writer.

A third consumer is in original `liblethe_tactics_tree.so`: `SweepStationContorl::WashDonePrecess()` resolves the same literal at `0x23526c/0x235270`, using the station tree's Blackboard (`0x235244`) and a virtual contains operation (`0x2352b4`); the absent-key branch bypasses the rewash request (v67).

A fourth textual occurrence resides in original `liblethe_tree.so` beside station-wash diagnostic strings (`StationWash.xml,DryingSubtree`, `StationWash.xml,HandleMopAgain`). This is *contextual diagnostic text*, not a verified writer, XML instance or execution path.

**Interpretation:** finding the station-tip getter strengthens the distinction between using and initializing this prerequisite. No additional direct-key writer for R2416 was established. The bounded direct ADRP+ADD census is **not** a global absence proof: computed identifiers, string tables, indirect branches, alternative writers and runtime configuration remain possible.

## Compiled shared-root bridge reverified

The separately generated v82 root-Blackboard verifier was rerun in this research pass. Original `AvaNodeRoute` stores a root Blackboard at `this+0x30` (`0x34c088/0x34c098`), and `StateShowAndSave` copies that pointer/reference into its callback state (`0x88d130/0x88d13c`). All **four** `BT::buildTreeFromText` calls in `AvaNodeRoute` load that same root into argument `x2` (source sites `0x355114`, `0x3552c0`, `0x3553e8`, `0x3554dc`). `libbehaviortree_cpp.so` forwards the root to `XMLParser::instantiateTree` (`0x70a3c` through `0x70a84`).

The tactics plugin registers `RobotTree` and `StationHandle` nodes. The station eligibility function itself obtains three Blackboards through `BT::TreeNode::blackboard()` (tactics `0x24e61c`, `0x24e6a4`, `0x24e72c`). The static bridge establishes a **common root supplied at tree creation**, not that the active station subtree has an identical live Blackboard instance. Remapping, inherited scopes and conditional cached subtrees remain material unknowns.

## Pins and reproducible regression

- `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so` SHA-256 `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`
- `libbehaviortree_cpp.so` SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

The operator-side sanitized package `X40-R2416-v83-sanitized-special-key-audit-20261024.zip` contains two standalone Python standard-library scripts (`x40_r2416_v83_special_key_consumers_verify.py`, companion `x40_r2416_v82_root_blackboard_bridge_verify.py`), technical report and README; **no source ELF**. Both were exercised against the owner's private `X40-R2416-v62-readonly-20261023T051829Z.zip`. The new verifier rejected **16** single-instruction/key-literal mutations, while the root verifier rejected **29** independent mutations.

```text
X40_V83_SPECIAL_KEY_MODEL_WRITER_AND_STATION_TIP_READER_STATIC_PASS
X40_V83_NODE_LETHE_EXACT_DIRECT_KEY_REFERENCE_CENSUS_PASS count=2
X40_V83_R2416_BRANCH_TO_DIFFERENT_MODEL_SEGMENT_STATIC_PASS
X40_V83_ROOT_BLACKBOARD_TO_BT_TREE_INSTANTIATION_STATIC_PASS trees=4
X40_V83_STATION_WASH_KEY_CONSUMER_STATIC_PASS
X40_V83_INDEPENDENT_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=16
LIMIT: direct literal census is not all runtime key writers; live subtree identity and physical extra wash unverified
```

This audit establishes **compiled sites**, not runtime key population, a real turbidity failure, the `r2343_start_rewash` marker being acted upon, or a second physical wash. The marker's separate `wash_times` bookkeeping path and `Ava_Station_Ctrl` publisher remain unlinked to physical execution (v67).

## Next research steps

1. Examine the active station XML/NodeConfig Blackboard inheritance/remapping and conditional reuse, without inferring that plugin registration guarantees live node placement.
2. Continue searching for any R2416-compatible non-model-gated or indirect `special_push_clean_dish` producer before proposing any passive device observation.
3. Close the separate real turbidity → rewash request → actual station-set payload → physical additional wash chain; similarly distinguish eligibility from dirt-triggered extra area cleaning.
4. Do not inject simulated contamination, force Blackboard switches, or write guessed MIOT AutoMop/AutoWash values. Preserve the current tested robot state.

**Live robot status (last operator-confirmed):** Valetudo+ v74, SmartHost restored to `0`, original launcher restored and rebooted, native baseline preserved, experimental `writeGateOpen=false`, existing v70/v73 and parent/original recovery artifacts intact. No new install, reboot or robot command is needed for this research.
