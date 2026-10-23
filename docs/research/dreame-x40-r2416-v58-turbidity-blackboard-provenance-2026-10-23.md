# Dreame X40 R2416 — v58 turbidity Blackboard provenance and consumption audit

**Date:** 2026-10-23  
**Method:** Read-only offline AArch64 ELF instruction and exact direct-reference analysis of the user's five SHA-256-pinned firmware libraries, independently checked against three runtime tree-library copies. No robot access, MIOT operations, flashing, hooks, native patching, or Valetudo+ modifications.

## Executive findings

**The optional dynamic B-table index in `StationHandle::SweepStationContorl::CheckIfNeedReClean()` comes from the float-typed Blackboard key `turbidity_clean_area`, whose literal address in `liblethe_tactics_tree.so` is `0x340ba0`.** When the key is unavailable or a typed Blackboard lookup cannot furnish the value on the checked path, the code selects a default float value of `20.0`, which v57 showed translates to the B-helper's `>19` `1.0` fallback. When available, the value is loaded from the Blackboard result as `s8`, clamped to `0..20`, converted to an integer, and passed to `TurbidityMonitorGetBByTable(int)`.

**The same function also attempts to erase `turbidity_clean_area` after the value-retrieval/default branch.** In particular the code reconstructs the same key at `0x253968..0x2539b4` and calls the virtual Blackboard erase slot `+0x30` at `0x2539c8..0x2539cc` when the handle exists. This makes the code a *consume-on-check* path. It does not establish that the erase always succeeds or that the key was previously populated.

A second, independent decision input is also resolved: the `GetAByTable(..., false)` path reads Blackboard key **`station_info_sub`**, accesses a 16-bit value at offset `+0x5e` from the returned typed data, and selects table/fallback branches accordingly. Its `true` path instead uses the C-table route documented in v57.

## Verified instruction and key evidence

| ELF/function | Instruction(s) | Meaning supported by the binary |
|---|---|---|
| Tactics `CheckIfNeedReClean()` | `0x252f68/0x252f6c` | Loads `turbidity_clean_area` literal (`0x340ba0`) |
| Tactics `CheckIfNeedReClean()` | `0x252fa8..0x252fb0` | Virtual `contains` check for that key |
| Tactics `CheckIfNeedReClean()` | `0x253038`, `0x253044..0x253050` | Null storage/entry fallbacks and virtual `get` |
| Tactics `CheckIfNeedReClean()` | `0x2530c8` | Loads a float value into `s8` from the returned result |
| Tactics `CheckIfNeedReClean()` | `0x253940` | Explicit `20.0` float fallback |
| Tactics `CheckIfNeedReClean()` | `0x2539e8..0x253a14` | Clamps index to `0..20`, rejoins B-table call at `0x2530ec` |
| Tactics `CheckIfNeedReClean()` | `0x2539c8..0x2539cc` | Attempts virtual Blackboard erase of the same key |
| Tactics `WashErrorLogicRun()` | `0x254af0/0x254af4`, `0x254b14..0x254b18` | References and attempts to erase the same key |
| Tactics `WashFloorTubidityCheck()` | `0x25653c/0x256540`, `0x256560..0x256564` | References and attempts to erase the same key |
| Tactics `GetAByTable(int,bool)` | `0x252b10/0x252b14` | Builds `station_info_sub` key |
| Tactics `GetAByTable(int,bool)` | `0x252b48..0x252b4c`, `0x252bd0` | Reads typed Blackboard entry, then `ldrh [value+0x5e]` |
| Route `CalTurbidArea::tick()` | `0xaf3204/0xaf3208`, `0xaf3244` | Reads `turbidity_clean_area` with `Blackboard::get<float>` |
| Route `CalTurbidArea::tick()` | `0xaf3294/0xaf3298`, `0xaf32d4` | Reads `clean_area_bkwash` with `get<float>` when needed |
| Route `CalTurbidArea::tick()` | `0xaf3324/0xaf3328`, `0xaf335c` | Reads `last_turbid_area` with `get<float>` |
| Route `CalTurbidArea::tick()` | `0xaf3378..0xaf338c`, `0xaf33c0` | Compares a float difference with `5.0`; returns status 3 or status 2 by branch |
| Route `PresetBlackboard::tick()` | `0xb0f45c/0xb0f460`, `0xb0f4a0..0xb0f4a4` | References and erases `turbidity_clean_area` on this code path |
| Route `MopDirtyAccumulator::tick()` | `0xb478b4/0xb478bc`, `0xb47958` | Forms key and performs Blackboard internal hash/map lookup; this is *not* a verified setter |
| `node_lethe.so` `AvaNodeRoute::SendMap()` | `0x52232c/0x522330`, `0x52234c` | Another `get<float>` of `turbidity_clean_area` |

### Cross-ELF direct-reference census

For the exact ASCII `turbidity_clean_area` literal and the bounded ADRP+ADD instruction pattern, v58 confirms these complete per-ELF lists:

- `liblethe_tactics_tree.so`: 3 direct pairs, at `0x252f68`, `0x254af0`, `0x25653c`.
- `liblethe_route_nodes.so`: 3 direct pairs, at `0xaf3204`, `0xb0f45c`, `0xb478b4`.
- `node_lethe.so`: 1 direct pair, at `0x52232c`.

`liblethe_tree.so` also contains the textual key in two places but no matching direct ADRP+ADD reference to the first occurrence. This is **not an exhaustive cross-library producer proof**: inline strings, alternative code-generation patterns, aliases, indirect virtual setters, or callbacks can escape the bounded direct-reference method.

### Interpreting the route node

`CalTurbidArea::tick()` first tries `turbidity_clean_area`, then can try `clean_area_bkwash` if the first getter fails, and separately reads `last_turbid_area`. The compiled comparison (`fsub` followed by comparison with `5.0`) yields different native BT return codes. These read and compare operations establish a route-side consumer of the same named area data; **they do not show this node computing or publishing the value**.

`MopDirtyAccumulator::tick()` uses a lower-level Blackboard hash-map lookup for the key, but its full handling must be traced before assigning writer/reader semantics. The checked instruction block does not establish a write to `turbidity_clean_area`.

### Relation to the rewash failure

The v54–v57 chain remains intact: a measured turbidity difference may produce numeric `TubidityState=2`; later producers can write `TurbidityResultFail`, which `WashDonePrecess()` may erase before checking its wash-enable flag and the `special_push_clean_dish` eligibility key. The direct literal-based `ProcessModelInfo` producer identified so far is model-gated to models other than R2416. **v58 identifies a new input dependency, not an alternate producer of `special_push_clean_dish` and not proof of a physical second dock wash.**

## Verification and limits

The standalone verifier embeds all checks from v54–v57, checks original hashes and runtime equality, validates the additional literal origins and instruction/branch words in v58, rejects a modified route-library instruction, and rejects a separately modified tactics-library SHA-256 pin. It contains no proprietary library data, customer configuration or robot credentials. It does not query the robot.

**Still unknown:** Who writes `turbidity_clean_area` on a normal R2416 run; whether the same concrete Blackboard instance flows through the route and tactics consumers; whether the key is present when the recheck occurs; what the `station_info_sub+0x5e` value is at runtime; whether the failure marker is re-armed; and whether a physical second wash occurs.

## Reproduce

```bash
python3 x40_r2416_v58_turbidity_blackboard_provenance_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip --self-test
```

Expected ending:

```text
X40_V58_TURBIDITY_BLACKBOARD_PROVENANCE_STATIC_PASS
X40_V58_INSTRUCTION_TAMPER_REJECTION_PASS
X40_V58_SHA_TAMPER_REJECTION_PASS
```

**Safety:** Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not push native firmware payloads or tamper with the robot to reproduce this report.

## Next research focus (v59)

Trace the `MopDirtyAccumulator` hash-map path and the route-side native float setter sites for an actual `turbidity_clean_area` producer. Verify Blackboard instance provenance between `CalTurbidArea`, `SendMap`, and `CheckIfNeedReClean()` before inferring cross-tree value propagation. Continue separately searching for an R2416-reachable alternate `special_push_clean_dish` producer.