# Dreame X40 R2416 v201 — incoming station subtype producer and native tree bridge

**27 October 2026.** Offline, read-only SHA-pinned binary analysis. Extends the corrected v195 native-`RobotNode` model and v197–v200 turbidity-calibration research. The robot and `master` were not modified. No private ELF, raw configuration, maps, device identities, model weights or credentials are committed.

## Verified native producer

The original `node_lethe.so`, SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, contains exported `ancp::AvaNodeRoute::StationInfoProcessSUB(ava_mop_station_msg*)` at `0x8f9090`.

The callback copies the incoming `ava_mop_station_msg` data at `0x8f90c8–0x8f9104`. On one **guarded** path (`0x8f9108`, `0x8f916c`, `0x8f9178`) it obtains the route Blackboard through `AvaNodeRoute+0x30` at `0x8f9184`, constructs key `station_info_sub` from literal `0x9f7670` at `0x8f91ac–0x8f91b0`, copies the incoming struct representation into a 0x70-byte heap payload at `0x8f9204–0x8f9248`, and calls the selected virtual writer at `0x8f924c` (the method pointer at vtable `+0x20` was prepared at `0x8f91f0`). The prior v18 research established the Blackboard interface's `+0x20` set semantics for the inspected implementation vtables. v201 verifies this specific path's original opcode words and targets; runtime receiver class/dispatch was not measured.

This is a compiled station-message-to-route-Blackboard *publisher*, not an observed live sensor value or proof that the callback took the relevant branch.

## Verified bridge and independent consumer

The same `AvaNodeRoute+0x30` field is loaded into `x2` for `BT::buildTreeFromText` at `node_lethe.so:0x3552c0–0x3552c8`. The constructed root is retained at `AvaNodeRoute+0xf48` at `0x3552d8`. Earlier v195 work verified that the effective `setting.yaml` selected native `RobotNode` rather than fallback `RobotNode.xml`.

In the original tactics library (SHA-256 `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`), `SweepStationContorl::InitTable()` at `0x250730` calls `BT::TreeNode::blackboard()` at `0x250770`, constructs the same `station_info_sub` key at `0x250794–0x250798`, then on a conditional path reads `uint16` at offset `+0x5e` at `0x250850`. The in-range subtype selects a 24-byte A-series vector entry at `0x251fbc–0x252004` as confirmed in v199. The station callback copies the incoming message bytes covering that offset.

**Distinct boundary:** producer writes through the route Blackboard; consumer reads a station tree node's Blackboard. The native route constructor passes a Blackboard into the root builder. **Equality of the effective live parent/child Blackboard instances, including subtree cache reuse, has not been demonstrated.** No running `station_info_sub` value has been observed; A[3] selection remains a conditional inference, not a live finding.

## Reproduction

Offline local package `X40-R2416-v201-sanitized-analysis-kit.zip`, SHA-256 **`f1cc6de32fef95587af0ce1110759b9d6e3dc9ab695d2f70a723a90d9e5eae74`**, carries the complete v197–v201 source-only regression chain, focused unit tests, machine-readable findings and checksum manifest. Against the two owner-private collector ZIPs (kept outside the repository): all five original ELF SHA pins and the earlier 18 + 7 saved file digests pass, **71** new native instruction anchors (54 host/17 tactics) and **11** branch/call edges verify. **Ten** v201 focused tests pass, including native tamper detection, wrong key-construction, wrong conditional polarity and create-only report refusal. The 16-item ZIP contains 15 per-file SHA-256 checksums including source-only files and no proprietary payload.

This branch includes a separate small **repository-side** standalone verifier (not the full regression, which remains in the self-contained kit). No experimental commands, cleaning tasks, firmware patches or live robot interactions were performed.

Next: inspect actual native generated `StationWash` child creation, factory Blackboard forwarding, and cache attachment/rebind paths. No new collection is currently needed. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Neither physical reclean nor automatic dock rewash is proven.
