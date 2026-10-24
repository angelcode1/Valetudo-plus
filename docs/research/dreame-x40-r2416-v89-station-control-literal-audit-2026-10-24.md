# Dreame X40 R2416 — v89 scoped station-control literal audit

**2026-10-24 · Offline SHA-pinned ELF analysis and operator-provided read-only v88 result.** No X40 settings write, firmware modification, process restart, or vendor binary redistribution.

## Observed v88 resource layout

The operator ran the exact-name/extension-only v88 resource locator against native PID `1736`, with CWD `/data`. Reported mount destinations were `/data`, `/tmp`, and a single-file `/usr/bin/ogg123` mount. The inspected resource roots `/tmp/ava`, `/tmp/lib/tree_lib`, `/ava`, `/usr/lib/tree_lib` yielded no matching `StationWash.xml`, `RobotNode.xml`, symlink, or resource package. The only candidate XML printed was **`/ava/conf/camera_prior_info.xml` (997 bytes)**. It is unrelated to station-tree remapping; do not collect it. Previous v87 showed the native process and SSH session have the **same mount namespace**, root `/`, and mapped library paths in `/tmp/ava/lib`, `/tmp/lib/tree_lib`, `/usr/lib`.

This remains a bounded negative inventory, not proof that `StationWash.xml` is absent globally. The v84 compiled `subtree_file_path=StationWash.xml` and v85 `getcwd()/make_absolute()` evidence do **not** show that the file was opened or that the subtree executed.

## New offline station-control reference finding

The original pinned ELF archives yield **two direct same-register ADRP+ADD references to the exact `Ava_Station_Ctrl\0` literal across the two examined libraries**, one in each:

| Original ELF | Literal VA | Direct reference VA | Function / interpretation |
|---|---|---|---|
| `node_lethe.so` | `0xa24f70` | `0x7c9d1c–0x7c9d20` | `AvaNodeRoute::SendStationParamCmd()`: previously identified station message publisher path |
| `liblethe_tactics_tree.so` | `0x33f1f0` | `0x22b300–0x22b304` | `RobotCollectDust::DustStrategy::SetStationFan()`: constructs station-control message and invokes an indirect interface |

In `SetStationFan`, a conditional null branch at `0x22b330` protects dispatch; `0x22b358` loads a vtable slot and `0x22b378` is an AArch64 `blr x3`. This is a new compiled **station-control message path**, not a proven Blackboard setter, automatic mop rewash trigger, or causal producer for `SendStationParamCmd()`. In particular, **literal matching is not equivalent to dataflow**. The station fan call must not be presented as proof of native rewash.

Original SHA-256 pins:
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`

## Repeatable offline verifier

The **separately delivered sanitized** `X40-R2416-v89-sanitized-station-control-audit-20261024.zip` contains standalone standard-library Python `x40_r2416_v89_station_ctrl_string_boundary_verify.py`, longer report and README. It reads only the owner's *private* `X40-R2416-v62-readonly-20261023T051829Z.zip` in memory, checks both SHA-256 hashes, literal VAs, exact AArch64 ADRP+ADD references, five further pinned instruction sites including `blr`, and rejects nine one-byte mutations.

```text
X40_V89_PINNED_STATION_CTRL_LITERAL_CENSUS_PASS files=2 refs=2
X40_V89_NODE_ROUTE_STATION_CTRL_LITERAL_REFERENCE_PASS
X40_V89_DUST_STATION_FAN_INDIRECT_CALL_STATIC_PASS
X40_V89_INDEPENDENT_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=9
LIMIT: reference census excludes computed accesses; station fan indirect dispatch is not a proven rewash command
```

Limit: reference scanning only covers `.text` direct ADRP+ADD pairs within six instructions in the two original ELFs; other libraries, computed identifiers, data references, indirect registrations, runtime values and log observations are outside its scope.

## Next priorities

1. Determine the indirect station-control recipient in `DustStrategy::SetStationFan()`, and compare its control payload/receiver with `AvaNodeRoute::SendStationParamCmd()`, without conflating an ordinary fan command with a second wash.
2. Trace `TurbidityResultFail`, `special_push_clean_dish` and `r2343_start_rewash` through real station control to a specific **additional mop wash command**, not just marker bookkeeping.
3. Treat `StationWash.xml` location/remapping as unresolved. Repeated wide scans would not add much; rely on authentic private XML or passive evidence from naturally occurring, unforced station activity.

**Live robot remains unchanged:** last operator-verified Valetudo+ v74, `SmartHost=0`, writer gate `writeGateOpen=false` after launcher restoration and reboot, native baseline preserved, rollback artifacts intact. No native setting write, forced wash or reboot is recommended.

No vendor binaries, XML contents, maps, credentials or device identifiers committed.
