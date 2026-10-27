# X40 R2416 v237 — route-health byte transition and stuck-motion reset

**27 October 2026.** Read-only offline analysis of owner-private original R2416 health firmware. Descends from v236 (`49fa743d4bb9f54d84a2d2ea0ff0d779bd632f73`). No robot connection, firmware execution, control commands or Valetudo+ changes.

Original node_health_lethe.so SHA-256: `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`.

## New original-native result

v236 proved that `ROUTE_NODE_HEALTH` subscribes to `AvaNodeHealth::RouteNodeHealthMsgProcess(AvaRouteNodeHealthMsg*)` at VA `0x9bf00`. Before copying incoming data into retained route_node_health_msg, the callback loads the previous byte `+0x15` at `0x9bf24`. After copying, `0x9bf70` loads the current byte, `0x9bf74` compares them, and original branch `0x9bf78 → 0x9bfcc` skips reset logic when unchanged.

When previous control-flow guards permit the changed-byte path, the code in `0x9bf7c–0x9bfcc` clears three fields, at relative offsets `0x0` (16 bits), `0x20` (32 bits), and `0x24` (16 bits), in **each of four separately bound health-state objects**:

| Original global name | GOT relocation | Original static value |
|---|---|---|
| `gs_stuck_reciprocting_motion_check` | `0xe8670` | `0xebd68` |
| `gs_stuck_reciprocting_motion_quick_check` | `0xe8998` | `0xebd38` |
| `gs_stuck_reciprocting_motion_large_turn_check` | `0xe8ae8` | `0xebd08` |
| `gs_stuck_reciprocting_motion_precise_follow_wall_check` | `0xe7d78` | `0xebcd8` |

All four are grounded in exact original `R_AARCH64_GLOB_DAT` bindings and verified AArch64 page/GOT loads. The **only direct BL** in the callback body `0x9bf00–0x9c008` is the separately guarded `ClimbEntryClear` call at `0x9c000 → 0x4b460`. Additional guards exist; this does not imply every changed byte always causes resets.

**Not established:** actual runtime message delivery, OEM meaning of `AvaRouteNodeHealthMsg+0x15`, effect on cleaning, physical mop washing, new floor-cleaning task, or real extra pass. This typed message field is **not** v229's unrelated `AvaSensorsMsg+0xfa`; no shared live pointer/Blackboard identity has been established.

## Reproducibility

The separate v237 source-only offline kit reuses the owner's original v230 PRIVATE ZIP. All 35 saved-file SHA-256 checksums and archive CRC passed. Its full v237 verifier checks **49 new original AArch64 instruction words**, four named global relocations, four original GOT load computations, two decoded conditional branch edges, and the complete direct-call census of the callback. **20/20 regression tests passed**, including mutations to the byte comparison, resets, offset writes, relocation and injected direct call; the whole package also passed clean-extraction replay.

Repo-local compact checker verifies **26 representative words**, four relocation indexes, two branch targets and the callback direct-call census on top of inherited v236 original checks. No proprietary ELF, owner PRIVATE ZIP, raw robot configuration, maps or identifiers committed.

```sh
export X40_V237_PRIVATE="$HOME/Downloads/X40-R2416-v230-gap-20261027T094248Z-PRIVATE.zip"
python3 docs/research/x40-r2416-v237-tools/x40_r2416_v237_repo_check.py --v230-private "$X40_V237_PRIVATE"
# X40_R2416_V237_REPO_STUCK_STATE_RESET_PASS 26 4 35
```

## Open causal gaps

Identify the original **route-side publisher of ROUTE_NODE_HEALTH**, consumer of **HEALTH_TO_ROUTE**, and publisher of **SENSORS**. Separately establish `stain_area_for_logic → SetExtraCleanArea → production new-task launch → observed physical second pass`. The current v230 native archive contains the health module, but not the originally SHA-pinned route-host `node_lethe.so`; previously collected original private host evidence remains the preferred next offline source.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Robot, firmware, active Valetudo+, master and previous research branches unchanged.
