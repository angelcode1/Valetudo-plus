# Dreame X40 R2416 — v92: output-call order and separate typed wash control

**24 October 2026. Pinned original ELF static evidence, offline.** No robot connection, write, restart, instrumentation or proprietary source redistribution.

## Sender order is now resolved

The original **`node_lethe.so`**, SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, contains `AvaNodeRoute::UpdateOutput()` at VA `0x3daf20` (length `0x9e4`). In a single sequential compiled segment using the same route receiver, its direct BLs are:

| Site | PLT target | Sender |
|---|---|---|
| `0x3db49c` | `0x27de30` | `SendStationParamCmd()` — sends typed `ava_msg_station_set` on `STATION_UI` (v90–v91) |
| `0x3db4b4` | `0x278e20` | `SendCleanDockMsg()` |
| `0x3db4bc` | `0x273700` | `SendRobotMopMsg()` |
| `0x3db4c4` | `0x276390` | `SendStationTaskTip()` — previously shown in v67 to consume `r2343_start_rewash` and advance `wash_times` when its guards pass |
| `0x3db4dc` | `0x27d090` | `SendWashContrlInfo()` — separate wash-control path described below |

The full `.text` direct BL inventory finds **one caller each** of the PLT entries for `SendStationParamCmd`, `SendStationTaskTip` and `SendWashContrlInfo`: the sites above. PLT GOT addresses and `R_AARCH64_JUMP_SLOT` symbol identities are validated independently. In this straight-line sequence, **the STATION_UI send precedes marker consumption**. Consequently a marker *first consumed by the later call* cannot retroactively cause the earlier send in that invocation. The order does **not** exclude previously staged commands, other writer paths, repeated cycles, or asynchronous events, and it does not prove any output actually occurred.

## A distinct `wash_machine_control` → `WashControlMsg` route

`SendWashContrlInfo()` at `0x7d73f0` reads the route root Blackboard at `+0x30`, resolves the exact key **`wash_machine_control`** (literal `0x9d3c78`), and looks up its value using virtual Blackboard calls. Its type-handling code refers to RTTI **`std::map<int,WashMachineControl>`** via `R_AARCH64_GLOB_DAT` at `0xb7f958`.

Three verified direct BLs in that function publish typed **`WashControlMsg`** through `AsyncDeque::MultAsyncPublish`: `0x7d77f8`, `0x7d80c8`, `0x7d8170`, all to PLT `0x274ee0`, JUMP_SLOT GOT `0xb72e80`. The `WashControlMsg` name relocation at `0xb7e6c0` provides an additional type anchor. **This is a separate message class and key from `STATION_UI`'s `ava_msg_station_set` / `Ava_Station_Ctrl`.**

An exact direct ADRP+ADD reference census of `wash_machine_control` in `node_lethe.so` finds four pairs: `0x32734c/0x327350` in another, **not yet fully analysed** code region; and `0x7d746c/0x7d7470`, `0x7d74d0/0x7d74d4`, `0x7d781c/0x7d7820` in `SendWashContrlInfo`. The earlier code region is a **candidate** producer to trace, not a verified writer based on matching literal alone.

The only direct reference to literal `r2343_start_rewash` in `node_lethe.so` is `0x7ca34c/0x7ca350` in `SendStationTaskTip`. The bounded wash-control sender has **no direct ADRP+ADD references** to either `r2343_start_rewash` or `wash_times`. This is a direct-literal boundary, not an all-access negative proof.

## Reproducible verifier

The separately delivered sanitized ZIP **`X40-R2416-v92-sanitized-output-order-washcontrol-20261024.zip`** contains `x40_r2416_v92_output_order_washcontrol_verify.py`, the detailed report and README. No original binaries, XML, settings, user data or credentials are included. To reproduce, use the operator-owned private `X40-R2416-v62-readonly-20261023T051829Z.zip`:

```sh
python3 x40_r2416_v92_output_order_washcontrol_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verified local output:

```text
X40_V92_OUTPUT_STATION_SEND_BEFORE_REWASH_MARKER_CONSUME_PASS
X40_V92_WASH_MACHINE_CONTROL_AFTER_MARKER_SEPARATE_TYPED_BUS_PASS
X40_V92_WASH_CONTROL_MAP_AND_TYPED_MESSAGE_STATIC_PASS
X40_V92_DIRECT_SENDER_CALLSITE_INVENTORY_STATIC_PASS station=1 marker=1 wash=1
X40_V92_NO_DIRECT_MARKER_OR_WASH_TIMES_LITERAL_IN_WASH_CONTROL_SENDER_PASS
X40_V92_PINNED_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=35
LIMIT: compiled sequential call order is not runtime delivery; no proven marker->wash_machine_control writer, R2416 wash gate or physical extra wash
```

The Python-standard-library-only self-test rejects 35 separately altered original ELF instructions, literals, and PLT anchors, in memory. The script itself has SHA-256 `3bee72588bae7248035102cc27c556457de6287625a5620fd14935b239285d60`.

## Next technical gates

1. Disassemble the additional `wash_machine_control` reference at `0x3272c0`; determine whether it actually writes the map and which input drives it.
2. Identify the topic and subscriber of `WashControlMsg` and decode only verified control semantics, rather than guessing station command codes.
3. Independently establish an R2416-compatible `special_push_clean_dish` producer, effective active-subtree Blackboard scope, genuine turbidity triggering, and a **second physical mop wash**. The current code does **not** prove automatic rewash.

**Operational safety unchanged:** last verified working Valetudo+ v74, native `SmartHost=0`, `writeGateOpen=false`, original launcher restored, recovery/rollback binaries preserved. No X40 connection, MIOT write or firmware update is needed for v92.
