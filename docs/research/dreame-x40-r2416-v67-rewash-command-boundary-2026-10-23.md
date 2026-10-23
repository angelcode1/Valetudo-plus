# Dreame X40 R2416 — v67: rewash marker vs station-command publisher

**Date:** 2026-10-23. **Scope:** Offline read-only instruction-level verification of the owner-collected, SHA-pinned, byte-matched native R2416 ELF libraries. No robot connection, runtime instrumentation, flash or configuration changes. This report is sanitized; the underlying original binaries are not for publication.

## Executive result

The request marker and the identifiable station-set publishing interface are **distinct compiled paths**. `StationHandle::SweepStationContorl::WashDonePrecess()` conditionally writes integer 1 to Blackboard key `r2343_start_rewash` only after checking `TurbidityResultFail`, the configured wash gate, and `special_push_clean_dish`. `ancp::AvaNodeRoute::SendStationTaskTip()` checks that marker, increments `wash_times`, and erases the marker. A separate `ancp::AvaNodeRoute::SendStationParamCmd()` loads Blackboard key `Ava_Station_Ctrl` and has two direct calls to `MultAsyncPublish<ava_msg_station_set>`.

The static ELF trace **does not** connect the marker (or its bookkeeping update) causally to `Ava_Station_Ctrl`, the station-set message payload, or a specific physical mop wash. A station publish is not evidence that the requested extra wash took place.

## Addresses and direct evidence

| Pinned ELF / virtual address | Verified instruction-level property |
|---|---|
| `liblethe_tactics_tree.so:0x235134–0x235138` | Constructs `TurbidityResultFail` key; `0x23517c` tests presence and `0x235210` erases it |
| `liblethe_tactics_tree.so:0x23522c–0x235230` | Reads wash-enable state at receiver `+0x688`; false branches to `0x235644` |
| `liblethe_tactics_tree.so:0x23526c–0x235270` | Constructs `special_push_clean_dish`; missing-key branch at `0x2352bc` jumps to `0x235758` |
| `liblethe_tactics_tree.so:0x2352e4–0x2352e8` | Constructs `r2343_start_rewash`; `0x235318` stages integer 1 and `0x235328` invokes the virtual setter |
| `node_lethe.so:0x7ca34c–0x7ca350` | Constructs exactly the `r2343_start_rewash` key in `SendStationTaskTip()` |
| `node_lethe.so:0x7ca390–0x7ca39c` | Uses virtual contains slot `+0x28` and skips the update if absent |
| `node_lethe.so:0x7ca3c4,0x7ca3f0` | Increments integer `wash_times` and calls typed Blackboard `set<Ri>` |
| `node_lethe.so:0x7ca410–0x7ca434` | Reuses the marker key for virtual erase slot `+0x30` |
| `node_lethe.so:0x7c9d1c–0x7c9d20` | Constructs the separate `Ava_Station_Ctrl` key in `SendStationParamCmd()` |
| `node_lethe.so:0x7c9e8c–0x7c9e9c` | Retrieves station publisher handle and invokes `MultAsyncPublish<ava_msg_station_set>` at `0x275580` |
| `node_lethe.so:0x7c9f18` | Separate conditional branch to the same station-set publisher PLT |

The publisher PLT resolves through the AArch64 `R_AARCH64_JUMP_SLOT` relocation at `0xb731d0` to `ancp::AsyncDeque::MultAsyncPublish<ava_msg_station_set,...>`. The checked direct-call census finds exactly those two calls to the publisher in `SendStationParamCmd()` (`0x7c9cc0–0x7ca090`) and **none** in `SendStationTaskTip()` (`0x7ca090–0x7cacd0`). This does not exclude indirect calls, other publishers, or command dispatch in other modules.

A ten-original-ELF exact-byte literal census finds `r2343_start_rewash` once in `liblethe_tactics_tree.so` and once in `node_lethe.so` and nowhere else in those ten files. This bounded census cannot exclude computed identifiers, other libraries, event forwarding or inlined handling.

## Relation to v65–v66

v66 showed that ordinary `StationWash.xml` does **not** populate a previously nonexistent cache entry. A compatible `reuse/` registration is required first; no exact `reuse/StationWash` literal was found among the ten native libraries. Therefore v65's raw-pointer cached-tree lifetime concern remains conditional, not an observed StationWash defect. The current v67 trace makes no assertion of live producer–consumer Blackboard pointer equality.

The only previously verified literal `special_push_clean_dish` setter is gated for other compiled model names (`dreame.vacuum.r2432`, `mova.vacuum.r2432b`, `dreame.vacuum.r9420`). No R2416-reachable setter has been established by this static work; do not interpret the negative direct-literal census as global proof of absence.

## Reproduce (private inputs)

```bash
python3 x40_r2416_v67_rewash_command_boundary_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  ~/Downloads/X40-R2416-v63-runtime-gap-20261023T053118Z.zip \
  --self-test
```

Place `x40_r2416_v66_stationwash_cache_registration_verify.py` alongside the v67 verifier. Both use only the Python standard library. v67 runs v64–v66 regressions, checks exact branch/ADRP/string and GOT symbol anchors, performs the ten-library direct-marker census and executes 12 new mutated-instruction rejection tests. Expected new markers:

```text
X40_V67_REWASH_MARKER_CONSUME_AND_STATION_PUBLISHER_SEPARATE_PASS
X40_V67_TEN_ELF_DIRECT_MARKER_CENSUS_PASS
X40_V67_TWELVE_NEW_INSTRUCTION_MUTATIONS_REJECTED_PASS
```

## Remaining evidence boundary and next step

1. Identify who creates `Ava_Station_Ctrl`, and whether any path translates `r2343_start_rewash` or `wash_times` into that outbound message. A string match alone is not a causal dataflow proof.
2. Resolve the station-set payload's command/type mapping and the docking subsystem receiver before claiming physical actuation.
3. Continue bounded review of config-derived/indirect `special_push_clean_dish` producers compatible with R2416.
4. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Do not run MIOT writes, station command probes, or firmware patching.

**Privacy:** Neither report nor verifier includes firmware binaries, original private YAML, serial numbers, maps, tokens, credentials or full vendor disassembly.