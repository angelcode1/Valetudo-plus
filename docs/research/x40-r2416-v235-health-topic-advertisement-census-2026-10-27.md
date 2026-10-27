# X40 R2416 v235 — original AVA health advertisement and subscription census

**27 October 2026.** Offline static verification of owner-private original firmware, descended from [v234](x40-r2416-v234-ava-topic-contract-2026-10-27.md), commit `9306bf93104fc59e01de732cdcb596943c772b8e`. No robot access, MCU/AVA commands, vendor binary execution, firmware changes, or `master` modifications. No proprietary ELF, raw configuration, maps, identifiers or owner-private ZIPs committed.

## New verifiable direct-call census

Original SHA-256-pinned `node_health_lethe.so` SHA-256 `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`; original executable `.text` VA range **`0x4b800–0xbac20`**.

A complete original `.text` AArch64 **direct `BL`** census finds exactly **18 direct call sites** to `ava::AvaNode::AdvertiseImpl@plt` at `0x4a510`, and exactly **40** to `ava::AvaNode::SubscribeImpl@plt` at `0x4b540`. This does **not** enumerate indirect/virtual calls, uncollected modules or observed runtime registrations.

All 18 advertisement sites reside in two symbol-grounded functions:
- `AvaNodeHealth::InitRobotCheckPub` at `0x61110` supplies 5.
- `AvaNodeHealth::InitRobotCheckPlanningPub` at `0xaf290` supplies 13.

Each named source was recovered from the **original adjacent same-register `ADRP + ADD`** pointer construction preceding its direct advertisement call, followed by checking the original read-only literal bytes. Thus the evidence is **instruction-linked advertisement registrations**, not an arbitrary string list.

| Original producer initializer | Original advertised topics |
| --- | --- |
| `InitRobotCheckPub` | `HEALTH`, `NEW_HEALTH_ERROR_INFO`, `LINELASERCAMERAERR`, `STATIONSTATUSTYPE`, `HEALTH_MSG_EVENT_RECALL_CMD` |
| `InitRobotCheckPlanningPub` | `SKID_DATA`, `SIGNAL_STATISTICS`, `HEALTH_MOTOR_CTRL`, `HEALTH_BIG_DATA`, `HEALTH_CONFIG`, `OBSTACLERECORD`, `DROPTOBLACKBOARD`, `LOWSPEEDFLAG`, `WEAKESCAPE`, `HBACKOFFBUMP`, `HEALTH_TO_ROUTE`, `HEALTH_CLIFF`, `CLIFF_TOF_POWER_STATE` |

## New lead and boundary

**`HEALTH_TO_ROUTE`** advertisement is at **`0xb0254 → 0x4a510@plt`**, bound to original literal **`0xc01c0`** through adjacent `ADRP+ADD` at **`0xb021c/0xb0220`**. An exact `HEALTH_TO_ROUTE\0` literal scan across the eight previously verified v230 native components yields **one occurrence**, inside this health module. The topic name suggests a route-facing interface; **no consuming route implementation, message schema, or live message delivery was demonstrated**.

The previously verified **`SENSORS`** named topic instead uses `AvaNodeHealth::InitRobotCheckSub`, whose direct subscription is at **`0x5f36c → 0x4b540@plt`**, with original string literal `0xbc270`. `SENSORS` is not among the 18 direct health-module advertisement registrations. It remains unknown **which original module publishes `SENSORS`**. This bounded negative result is not a global exclusion of alternative/indirect advertisements or another module.

## Reproducibility and regression testing

The external **source-only** `X40-R2416-v235-health-topic-census.zip` includes complete inherited v233/v234 verifiers plus v235 full verifier and 16 v235 regression tests. All **35** original owner-private v230 ZIP payload checksums, ZIP CRC, pinned health and AVA binaries, inherited instruction and relocation anchors, full direct-call censuses, 18 literal bindings and exact eight-module `HEALTH_TO_ROUTE` literal count passed. **16/16 tests passed**. Negative mutations inject an otherwise unanchored advertisement call, delete an advertisement or sensor subscription and redirect the first advertised source pointer from `HEALTH` to `SENSORS`; all are detected. No original binaries included in public GitHub or source-only kit.

Run original-verification source-only package on Mac:

```sh
export X40_V235_PRIVATE="$HOME/Downloads/X40-R2416-v230-gap-20261027T094248Z-PRIVATE.zip"
python3 -m unittest -v test_v235.py
python3 verify_v235_health_topic_census.py --v230-private "$X40_V235_PRIVATE" --out "$HOME/Downloads/X40-R2416-v235-new-SANITIZED.json"
# X40_R2416_V235_HEALTH_TOPIC_CENSUS_PASS 18 40 35
```

## Next causal gaps

1. Locate an original **consumer and payload schema** for advertised `HEALTH_TO_ROUTE`, and the **original advertiser/publisher of `SENSORS`**. Seek existing offline firmware evidence before further collection.
2. Resolve separately whether `SENSORS`/health messages are received by route's independent `AsyncDeque<AvaSensorsMsg>` and the **specific** runtime Blackboard object read by `SendMopStainCheckCmd`; naming and type agreement alone do not prove this.
3. Independently establish `stain_area_for_logic` → `SetExtraCleanArea` → **production task dispatch** and observed additional physical floor pass. Do not conflate station dirty-mop checks or MCU code paths with extra floor cleaning.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Original v229–v234, `master`, robot, firmware and active Valetudo+ remain unchanged.
