# Dreame X40 R2416 — v41 Start_Map_Load producer and charger-condition audit

**Date:** 2026-10-23  
**Scope:** Read-only, fully offline static analysis of the original SHA-256-pinned R2416 native ELFs and previously collected identical runtime tree libraries. No native binary execution, robot connection, MIOT/AVA writes, firmware modifications or Valetudo+ changes. This report omits all original vendor binaries, raw disassembly, credentials, maps, sensor data and private configuration.

## Executive result

The `MapLoad` initialization tree's first child (`BlackboardContains(key=Start_Map_Load)`, verified in v40) is **not the only native reference to that key**. The v41 exact-literal direct `ADRP+ADD` census finds **12** code-reference preparations in `node_lethe.so` and **3** in `liblethe_tactics_tree.so`. Across them, we verified **12 typed `BT::Blackboard::set<bool>` calls** along separate conditional code paths, **one `get<bool>`**, and a concrete virtual `contains` operation. This demonstrates compiled key production *capability*; it does not demonstrate that a producer executes before the first `MapLoad` tick or that all parties share one Blackboard instance.

The compiled `RobotSignalDetect::DoesRobotGetCharger(BT::TreeNode&)` predicate invoked by `RobotmodeInit` calls the typed `BT::Blackboard::get<AvaSensorsMsg*>` helper. The failed-lookup arm supplies numeric status **3**. A separate arm loads and compares a byte at offset `+0x58` to zero and constructs status **2** or **3**. The byte's exact hardware meaning and runtime values remain unknown. These statuses select the two `RobotmodeInit` branches already decoded in v40.

## Key-reference and operation census

| Original library | Exact-key direct ADRP+ADD sites | Verified operation boundaries |
|---|---:|---|
| `node_lethe.so` | 12 | 9 typed `set<bool>` calls, one typed `get<bool>` call, one vtable `contains` dispatch; one further reference not independently classified |
| `liblethe_tactics_tree.so` | 3 | 3 typed `set<bool>` calls |

### `node_lethe.so` references

The single exact `Start_Map_Load` literal is at VA `0x9f7c88`. The twelve directly paired reference sites are:

`0x440d9c`, `0x447e20`, `0x6c845c`, `0x6d3f58`, `0x6d4ce0`, `0x6d7bc4`, `0x6d80a8`, `0x72ece8`, `0x744bbc`, `0x744de0`, `0x842ad4`, `0x842f34`.

- `AvaNodeRoute::MT_ChangeMap()` uses the vtable slot `+0x28` (`contains`) at `0x440de0–0x440de4`.
- Five typed Boolean setters within `AvaNodeRoute::AppEditMap()` call `set<bool>` at `0x6c8484`, `0x6d3f80`, `0x6d4d08`, `0x6d7bec`, and `0x6d80d0`. These are distinct **conditional** code branches, not evidence of five calls in a single map action.
- `AvaNodeRoute::SaveMap()` has `set<bool>` at `0x72ed10`.
- `AvaNodeRoute::DeleteMap()` has two compiled `set<bool>` sites at `0x744be4` and `0x744e08`.
- `SlamControl::CheckRelocDeal()` has a `set<bool>` site at `0x842afc` and a separate `get<bool>` site at `0x842f58`.
- `MT_SetRunModeProcessSUB()` additionally references the exact key at `0x447e20`; its full write/read semantics were not established in this pass.

### `liblethe_tactics_tree.so` references

The single exact key literal is at `0x343650`; its direct `ADRP+ADD` sites are `0x270fc4`, `0x2ba5b4`, and `0x2e6bcc`:

- `multmap::MultMapRecover::StandbyAndReloadMap(int)` invokes `BT::Blackboard::set<bool>` at `0x270ff0`.
- `multmap::ChargingReloc::tick()` invokes `set<bool>` at `0x2ba5dc`.
- `interface::UpdateReuseAppMap(BT::TreeNode&)` invokes `set<bool>` at `0x2e6bf4`.

Several paths prepare a Boolean value 1, but the verifier **does not assert that every setter invariably stores `true`**. All sites are conditional code paths; there is no live execution observation.

## Charger condition: `RobotmodeInit`

The exported `RobotSignalDetect::DoesRobotGetCharger(BT::TreeNode&)` entry is `0x11fff0` in `liblethe_tactics_tree.so`. Relevant checked instructions:

| VA | Compiled role |
|---|---|
| `0x120054` | call `Blackboard::get<AvaSensorsMsg*>` |
| `0x120078–0x12007c` | initialize status `3`; failed getter branches directly to this return arm |
| `0x12008c–0x120098` | load a byte at a pointer-relative offset `0x58`, compare to 0, construct status `2` or `3` |

The exact provenance of the pointer used for the byte load and whether that byte corresponds to a specific physical charger sensor were **not established**. Do not infer power state from the offset. v40 demonstrated that status `2` selects the `SequenceStarRoF` arm and status `3` selects the `Sequence` arm of `RobotmodeInit`. An absent lookup does not, by itself, establish that the entire initialization subtree permanently blocks the outer sequence.

## What is new—and what is not proven

**Established:** exact `Start_Map_Load` literal, direct-code reference census, 12 typed setters, native contains/get boundaries, and the charger predicate's typed getter and status construction. This supports revising the earlier *possible orphan-key hypothesis*: the key has multiple compiled producers.

**Not established:** event-order precedence relative to the first `MapLoad` tick, producer/consumer Blackboard instance identity, actual values under R2416, return status of the full `MapLoad`/`RobotmodeInit` subtree, or a normal turbidity result causing a second wash. The `special_push_clean_dish` initializer previously identified remains model-gated away from R2416, and no alternative producer or physical wash causation was established by v41.

## Offline reproduction

Extract `X40_R2416_V41_OFFLINE_AUDIT.zip` next to the private owner-supplied inputs, then run:

```bash
python3 x40_r2416_v41_mapload_charger_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Expected marker: `X40_V41_MAPLOAD_CHARGER_STATIC_PASS`. The checker inherits the original five SHA-256 pins, three original/runtime comparisons and v36–v40 regression chain; checks original ELF exact literal/reference sites and typed calls; and checks the charger-condition AArch64 instructions. An altered original or runtime ELF must be rejected by the hash/byte comparison gate.

**Recommended next focus:** verify the effective Blackboard instance lineage and scheduling around the `Start_Map_Load` producer(s), then return to the high-priority R2416 `special_push_clean_dish` eligibility blocker. Do not enable experimental CleanGenius writes or alter a functioning robot. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`.