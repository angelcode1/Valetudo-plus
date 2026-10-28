# Dreame X40 R2416 — v82 model-specific special rewash key and Blackboard boundary

**2026-10-24 · Offline-only, original SHA-pinned AArch64 firmware.** No MIOT actions, device shell, firmware installation, process instrumentation, or publication of vendor binaries. Full sanitized offline report and stdlib verifier are supplied in `X40-R2416-v82-sanitized-model-special-key-20261024.zip` to the operator, not in this repository.

## Verified model branch difference

The original `node_lethe.so` `ProcessModelInfo()` (ELF VA `0x46fd40`, symbol length 45,380 bytes) contains a model-gated initialization segment at `0x4704e8`. This block first writes `clean_dish_times`, then at `0x47052c–0x470554` constructs `special_push_clean_dish`, loads integer 1 and calls typed `BT::Blackboard::set<int>`.

| Native compiled model comparison | Conditional/fallthrough site | Next block |
|---|---|---|
| `dreame.vacuum.r2432` | `0x4704d0` equal | `0x4704e8` special-key segment |
| `mova.vacuum.r2432b` | `0x4704e4` equal fallthrough | `0x4704e8` special-key segment |
| `dreame.vacuum.r9420` | `0x4731e8` equal | `0x4704e8` special-key segment |
| **`dreame.vacuum.r2416`** | **`0x470940` equal** | **`0x470958` — different segment** |

A bounded inventory of all directly encoded AArch64 B/BL, B.cond, CBZ/CBNZ and TBZ/TBNZ transfers inside the complete `ProcessModelInfo` function shows **two** direct branches targeting `0x4704e8`: `0x4704d0` and `0x4731e8`. The r2432b case is a fallthrough, not a third direct branch. Original model names and key literals were pinned through their real ADRP+ADD target addresses.

This strengthens previous v65–v68 work: the **known** direct model-gated `special_push_clean_dish` setter is not supported as an R2416 source by the explicitly checked branch. **It does not prove this key is absent at runtime or impossible on R2416.** Other code paths, indirect callbacks, computed keys, configuration, or libraries can still populate it. No full control-flow exhaustiveness or global no-writer claim is made.

This distinction matters because v67 verified `StationHandle::SweepStationContorl::WashDonePrecess()` checks `special_push_clean_dish` before staging `r2343_start_rewash`. The marker's consumption updates `wash_times`, but a direct causal route to an additional physical dock wash remains unverified.

## Blackboard reader context, not yet identity

In the other original pinned library, `liblethe_tactics_tree.so`, `StationHandle::SweepStationContorl::TurbidityRecleanAndRewashSet()` calls `BT::TreeNode::blackboard()` separately at `0x24e61c`, `0x24e6a4`, `0x24e72c` before reading `smart_hosting_switch`, `smart_auto_wash_switch`, `smart_auto_mop_switch`. Each key read uses the native helper at `0x24d4b0`; calls at `0x24e680`, `0x24e708`, and `0x24e790`. Internal eligibility bytes are written to `+0x688` and `+0x689` (v75).

V81 separately established a compiled app-status callback and three `BT::Blackboard::set<int&>` switches in `node_lethe.so`. The station controller is a **different ELF and obtains its Blackboard through a behaviour-tree node**. No live shared_ptr managed-object equality or compatible parent/child remapping has yet been demonstrated. Exact name and type matches do not prove same instance.

## Repeatable static verification

Original private SHA-256 pins:
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`

The separately delivered standalone Python 3 script `x40_r2416_v82_model_special_key_boundary_verify.py` validates these original ZIP entries without extracting or publishing native code. It checks the SHA pins, model/key literals, actual ADRP+ADD resolution, conditional targets, the complete bounded direct-branch inventory in the named function, and station Blackboard read calls. **44 independent one-byte instruction/literal modifications were rejected** in self-test.

```text
X40_V82_R2416_BRANCH_SEPARATE_FROM_KNOWN_SPECIAL_KEY_WRITER_STATIC_PASS
X40_V82_KNOWN_SPECIAL_WRITER_MODEL_BRANCH_TARGETS_PASS count=3_models
X40_V82_DIRECT_BRANCH_INVENTORY_TO_SPECIAL_SEGMENT_PASS count=2
X40_V82_STATION_TREE_NODE_BLACKBOARD_READS_STATIC_PASS count=3
X40_V82_PINNED_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=44
LIMIT: other/indirect model key writers, live Blackboard identity, runtime AutoMop=-1 semantics and physical rewash unproven
```

### Next research gates

1. Determine whether R2416 ever populates `special_push_clean_dish` via **other** native/configured producers. No generated key or conditional fallthrough is automatically a missing feature.
2. Establish the actual Blackboard reference relationship between the app-status writer in `node_lethe.so` and the station tree reader, accounting for v64 factory shared_ptr forwarding and optional subtree reuse (v65–v66).
3. Trace a genuine turbidity failure to `r2343_start_rewash`, `Ava_Station_Ctrl` and a concrete second station-wash command. Marker != actuation.
4. Do not rewrite `SmartAutoMop=-1` or toggle unproven auto-switches.

**Installed X40 remains unchanged:** verified working Valetudo+ v74, `SmartHost=0`, launcher restored, baseline preserved, `writeGateOpen=false` after the operator-confirmed mode 1→0 native transport experiment and disarm. Keep v70/v73 fallback binaries and original backups; no reboot, firmware or setting write warranted.
