# X40 R2416 v236 — verified typed route/health interface and retained health state

**27 October 2026.** Read-only offline static analysis of owner-private original R2416 firmware. Branch descends from v235 commit `49472799a7f852dbc7db56e7c2e6e704cfe41cae`. No robot connection, MCU/AVA/MIOT commands, runtime Valetudo+ changes or original vendor binary execution. No original ELF, PRIVATE ZIP, device-specific configuration, IDs or maps committed.

The SHA-256-pinned original `node_health_lethe.so` is `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`.

## Incoming `ROUTE_NODE_HEALTH`: named topic, callback and original type

Original `AvaNodeHealth::InitRobotCheckPlanningSub` (`0xad150`) builds **`ROUTE_NODE_HEALTH`** via adjacent `ADRP+ADD` at `0xae574/0xae578`, referring to literal `0xc00e0`. Its typed AVA subscription is at **`0xae61c → SubscribeImpl@plt 0x4b540`**.

The callback and argument type are independently grounded in original `R_AARCH64_GLOB_DAT` relocations:

| Original GOT | Exact symbol | Value |
| --- | --- | --- |
| `0xe8438` | `AvaNodeHealth::RouteNodeHealthMsgProcess(AvaRouteNodeHealthMsg*)` | `0x9bf00` |
| `0xe7dc8` | `typeinfo for AvaRouteNodeHealthMsg` | `0xe64d0` |

The subscription initialiser loads the callback through the GOT at `0xae5a0` and the type-info pointer at `0xae60c`, prior to its `SubscribeImpl` call. These links are compiled code and relocation evidence, **not** evidence of actual live message delivery or source identity.

The original `RouteNodeHealthMsgProcess` body at `0x9bf00` performs actual **compiled** input-to-retained-state copies: `0x9bf14/0x9bf20` load/store two 8-byte words and `0x9bf28/0x9bf2c` load/store another 8 bytes from input offset `+0xe` to retained offset `+0xe`. Conditional byte comparisons follow. Branch `0x9bf4c → 0x9c000` reaches a direct call to `ClimbEntryClear@plt 0x4b460`. The original OEM field meanings and observed runtime effects remain unknown.

## Outgoing `HEALTH_TO_ROUTE`: different type

The independently verified v235 `AvaNodeHealth::InitRobotCheckPlanningPub` advertisement at **`0xb0254 → AdvertiseImpl@plt 0x4a510`** uses literal **`HEALTH_TO_ROUTE`** at `0xc01c0`, constructed at `0xb021c/0xb0220`. Original GOT **`0xe8620`** loads `typeinfo for AvaHealthToRouteMsg` at `0xe63a0` (`0xb0234`).

**`ROUTE_NODE_HEALTH` / `AvaRouteNodeHealthMsg` and `HEALTH_TO_ROUTE` / `AvaHealthToRouteMsg` are two different compiled interfaces.** The names suggest directions, but this analysis neither identifies the route-side peer nor proves exchanged messages.

A bounded eight-native-component original v230 ZIP literal census shows exactly one `ROUTE_NODE_HEALTH\0` and one `HEALTH_TO_ROUTE\0` literal. This is not a global firmware exclusion.

## Original-private reproducibility

The source-only v236 package `X40-R2416-v236-route-health-interface.zip` verifies **all 35 owner-private v230 saved SHA-256 payload hashes and archive CRC**, the pinned original ELF, the inherited v233–v235 checks, **25 exact AArch64 instruction words**, three decoded direct calls, three original callback/type-info GOT relocations, and the original conditional control-flow edge. **19/19** tests passed against the real original-private evidence. Mutations of the subscription or advertisement calls, topic pointer, callback and type relocations, retained-state copy, and control-flow edge are all rejected. The independent compact repo checker also passed.

Local Python 3 stdlib usage:

```sh
python3 verify_v236_route_health_interface.py \
  --v230-private "$HOME/Downloads/X40-R2416-v230-gap-20261027T094248Z-PRIVATE.zip" \
  --out "$HOME/Downloads/X40-R2416-v236-new-SANITIZED.json"
# X40_R2416_V236_ROUTE_HEALTH_STATIC_PASS 25 3 35
```

The complete v236 verification scripts and 19-test suite are distributed separately as a source-only ZIP; the repo-local checker is at `docs/research/x40-r2416-v236-tools/x40_r2416_v236_repo_check.py`, requires only the original owner-private v230 ZIP and invokes the existing v235 checker.

## Still open

1. Original publisher of AVA topic `SENSORS` and authoritative OEM `AvaSensorsMsg` field/enum descriptions.
2. Actual route-side producer/consumer and runtime object lineage for the distinct route/health messages; **do not conflate** named AVA subscriptions with v229 route-host `AsyncDeque<AvaSensorsMsg>`.
3. The separate production causal chain `stain_area_for_logic` → `SetExtraCleanArea` → **new cleaning-task start** and a physical second floor pass. Health messaging and dock rewash do not prove it.

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `writeGateOpen=false`. Leave firmware, robot, active Valetudo+, `master` and earlier research branches unchanged.
