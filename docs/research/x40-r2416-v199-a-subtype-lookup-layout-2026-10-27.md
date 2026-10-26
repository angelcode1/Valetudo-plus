# Dreame X40 R2416 v199 — Native turbidity lookup layout and selected A-series index

**27 October 2026. Offline static analysis only.** Continues the v195 native RobotNode correction and v197–v198 turbidity Blackboard research. Owner's previously archived original native ELF binaries and collector ZIPs were inspected without executing vendor code or contacting the robot. No raw vendor ELF, raw YAML/JSON, maps, credentials, disassembly bodies, or model weights are committed.

## Verified lookup layouts

The exact SHA-256-pinned original `liblethe_tactics_tree.so` implements three 8-byte record lookups, all using midpoint/interval comparisons against a signed 32-bit key:

| Function / entry VA | Selected vector | Pair shape | Return |
| --- | --- | --- | --- |
| `FindA(int,int,int)` `0x24df50` | `this+0x5f8/+0x600` | `int32,int32` | signed integer `[record+4]` at `0x24dfa4` / `0x24dfd4` |
| `FindB(int,int,int)` `0x24e0f0` | `this+0x610/+0x618` | `int32,float32` | float `s0` at `0x24e144` / `0x24e174` |
| `FindC(int,int,int)` `0x24e020` | `this+0x628/+0x630` | `int32,int32` | signed integer `[record+4]` at `0x24e074` / `0x24e0a4` |

All three calculate record count from `(end-start)>>3`. The recovered saved JSON is structurally compatible: four A series with 63/35/60/60 records; one B with 20; one C with 63. Every series has strictly increasing integer lookup keys and two-field entries. This **does not** demonstrate runtime loading, numeric conversion fidelity, or a physical wash.

## Verified loaded-table A-series selection

A meaningful extension beyond v198 is the source of the selected A vector:

1. `SweepStationContorl::InitTable()` at `0x250730` has three distinct nested-vector deep-copy loops, roughly `0x250a30–0x250a9c`, `0x250ae8–0x250b58`, `0x250ba8–0x250c18`, each copying 8-byte inner records. Their outer vector fields reside at `this+0x5b0`, `+0x5c8`, `+0x5e0`, with 24-byte vector headers.
2. The `station_info_sub` Blackboard data provides a **16-bit subtype**, read into `w27` at `0x250850` (`ldrh [x0,#0x5e]`). This is compiled code, not an observed live value.
3. In the successful populated-table path, `0x251fa0–0x251fbc` calculates the number of outer A entries and compares it against the subtype; `0x251fc0` branches to `0x250d58` if the index is out of range.
4. For an in-range subtype, `0x251fe0–0x252004` calculates `outer_A_base + 24 * station_info_sub` and forwards that chosen inner vector into the active A destination at `this+0x5f8`. At `0x252004` control tail-branches to the array copying helper at `0x24cb90`.
5. B and C selected-vector copy paths are separate. The earlier `FindA` lookup is against the resulting active A vector, not a direct JSON ID.

**Reconciliation with v198:** The 0–3 `station_info_sub` fallback cases in `TurbidityMonitorGetAByTable` do not themselves prove a JSON A-table index. v199 now independently identifies another code path where the *same 16-bit subtype* **does** conditionally select an indexed element from a populated outer A vector. The live subtype value, active outer-vector population, and JSON-ID-to-native-vector ordering remain unobserved. In particular, **this is not proof that A[3] is active**.

## Verification and safety boundary

The offline v199 kit SHA-256 is `f441a20707261428a7796023edf787b09ff6482e32277f460225484c22437bcb`, containing the v197–v199 stdlib verifiers, focused tests, fixed instruction anchors, sanitized results and checksum manifest. Original R2416 ELF SHA-256 pins: five verified. The v199 verifier adds **152 exact AArch64 word anchors** and **17 decoded branch targets** to the full passing v197+v198 chain. **Ten tests passed**, including changed ELF, changed-instruction, malformed calibration, forged path and create-only output rejection. The 18 + 7 saved collector file checksums were independently verified, but the claimed original SSH session was not separately authenticated.

**Not established:** selected live `station_info_sub` value; JSON record ID-to-native outer-vector order; identity of runtime loader/consumer Blackboard objects; threshold crossing; AI stain detection causing a new floor task; R2416-reachable special-push rewash eligibility; or a physical second clean or dock rewash.

Next: statically map the host JSON parser's A record allocation and order into its Blackboard `turbidity_check_tables` publisher, then trace Blackboard forwarding to the station-control node. In parallel preserve the separate native generated `RobotNode` AI-stain-to-task-start question. `master` and working v74 Valetudo+ unchanged; do not enable `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS` or hardware writes.
