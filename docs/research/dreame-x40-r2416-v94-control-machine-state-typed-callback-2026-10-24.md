# Dreame X40 R2416 — v94 registered ControlMachineState callback

**24 October 2026. Original SHA-256-pinned native ELF, offline only.** No robot connection, MIOT write, native process restart, vendor XML collection, firmware update or device-modifying test.

## New result: second compiled wash-control callback caller

v93 established the native `SetWashMchineControl` registration in `AvaNodeRoute`, its typed `std::function<void(int, WashMachineControl)>` callback, its map update under `wash_machine_control`, and `SendWashContrlInfo()` publishing `WashControlMsg` on `WASH_CONTROL`. Its `WashStationManag::StartMachineCtrl_ELECT()` path already used the typed callback.

**v94 proves a second, distinctly registered behaviour-tree node calls that same typed callback:** `WashStationManag::ControlMachineState::tick()`. In original `liblethe_tactics_tree.so`, `RegisterNodes()` constructs the exact name `ControlMachineState` at `0x2125d8–0x2125e0` (original literal `0x33bde0`) and passes its manifest and builder to `BT::BehaviorTreeFactory::registerBuilder()` at `0x212678`. The registered node's exported tick function is at `0x2179b0` (length 1024 bytes).

The tick routine reads three **integer** NodeParameters via `BT::TreeNode::getParamImpl<int>`:

| Name in original ELF | Literal VA | Getter BL site | Role established |
|---|---|---|---|
| `MachineType` | `0x33bcb0` | `0x2179fc` | Integer, must be positive to reach callback |
| `ContrlTime` | `0x33bfe0` | `0x217a58` | Integer control input; preserve vendor spelling |
| `InputV` | `0x33bdf8` | `0x217a80` | Integer control input in structured value |

The instruction sequence `0x217a88–0x217a94` checks `MachineType>0`; the callback lookup is downstream. At `0x217aa4` the node retrieves its `TreeNode::blackboard()`; at `0x217ab0–0x217ad4` it loads `SetWashMchineControl` (literal `0x32ed00`) and performs a typed `BT::Blackboard::get<std::function<void(int, WashMachineControl)>>`. The same tick has another Blackboard lookup for `is_wifi_station` (literal `0x32eea0`) at `0x217af8–0x217b28`; when that lookup fails, the corresponding prepared field defaults to zero. At `0x217b70–0x217b9c` it assembles a `WashMachineControl` value and indirectly invokes the callback. A missing invoke target is routed to `std::__throw_bad_function_call` at `0x217bcc`, **not** treated as proof that the callback always exists at runtime.

This is a second compiled entry into the **same named, typed callback contract** proven in v93, and includes an explicit factory registration. It is **not** proof that the `ControlMachineState` node is present or ticked in the owner's active station subtree, that the child Blackboard actually resolves to `AvaNodeRoute+0x30`, or that any specific wash hardware command is safe/issued.

## Offline verification

Original private AArch64 binaries are pinned:

- `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so` SHA-256 `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`

The separately delivered **sanitized** `X40-R2416-v94-sanitized-control-machine-state-20261024.zip` contains a standalone Python 3 verifier `x40_r2416_v94_control_machine_state_node_verify.py`, detailed report and README, **not** the source ELFs. It reads the operator-private `X40-R2416-v62-readonly-20261023T051829Z.zip` in memory, pins original two SHA-256 values, checks v92 and v93 regressions, original function symbols, exact ADRP+ADD literals, AArch64 branch targets, typed PLT relocation symbols, three parameter getter callsites, and 34 independent byte-flip refusal tests:

```sh
python3 x40_r2416_v94_control_machine_state_node_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V94_COMPILED_CONTROL_MACHINE_STATE_REGISTERED_BUILDER_PASS
X40_V94_BT_NODE_THREE_NAMED_INPUTS_STATIC_PASS
X40_V94_BT_NODE_TYPED_WASH_CALLBACK_GET_AND_INVOKE_PASS
X40_V94_WIFI_STATION_CONDITION_AND_BAD_CALLBACK_GUARD_PASS
X40_V94_V93_TYPED_WASH_CONTROL_REGRESSION_PASS
X40_V94_INSTRUCTION_LITERAL_CALL_MUTATIONS_REJECTED count=34
LIMIT: builder registration and compiled callback call are not active XML placement, shared live Blackboard, WASH_CONTROL receiver, or physical dirt-triggered second wash
```

The SHA-256 of this verifier is `6a073eaf58ab73a0f94ec1456c9b79dd0d8c79c383fc0077aac1a40f331c4397`. The sanitized ZIP SHA-256 is `08c4b36d987498e801eab7311bc02ececd734ba3488baf29203f28d66c9d6a86`. The private original ELFs, settings, camera data, XML and serials have **not** been committed.

## Receiver and rewash remain unproved

In a separate bounded search across the **ten collected original ELFs**, `WASH_CONTROL\0` appears in `node_lethe.so`, and no demangled dynamic `Subscribe<WashControlMsg>` or `MultAsyncSubscribe<WashControlMsg>` method was identified in those ten ELFs. This is **not** evidence that the device lacks the consumer; the real receiving executable/library or a type-erased subscription may be absent from the collection.

Most importantly, v67's `r2343_start_rewash` marker is only proven to reach `wash_times` bookkeeping in `SendStationTaskTip()`. Neither the newly registered node nor the typed callback has been shown to translate that marker, genuine turbidity failure or `special_push_clean_dish` into a **second physical mop wash on R2416**. Model-specific prerequisite and active StationWash.xml NodeConfig/Blackboard remapping also remain unverified.

**Next:** inspect authorised passive evidence or additional private native components for the real `WASH_CONTROL` consumer and actual active `StationWash` node execution. Do not fabricate station command IDs, force dirt sensors or enable untested MIOT auto switches.

**Robot preserved:** last operator-confirmed Valetudo+ v74, native `SmartHost=0`, `writeGateOpen=false`, original launcher restored after the controlled 1→0 write/readback and reboot, and existing v70/v73/parent/vendor rollback assets retained. No robot-side changes required for v94.
