# X40 R2416 v78 — MIOT 4:50 native string transport

**2026-10-24, offline static research only.** No device connection, firmware modification, MIOT write or vendor binary redistribution. Evidence from the owner's original pinned `node_msg_cvt.so`, SHA-256 `71c55d905e8e68c4d97d6cc108b251b879cf007ce8515d6f90767dd53d7d0da8`.

## Verified native bridge

`MsgClean::MsgClean(...)` loads service ID **4** (`0x10ebbc`) and calls the `MsgHandler` constructor (`0x10ebc0`). Its getter registration loads `MsgClean::GetSwitchSet` from a symbol-resolved GOT relocation (`0x10f260`), passes property **50** (`0x10f274`) and invokes `MsgHandler::AddGetHandler` (`0x10f278`). Its setter registration loads `MsgClean::SetSwitchSet` (`0x10f54c`), passes property **50** (`0x10f560`) and invokes `MsgHandler::AddSetHandler` (`0x10f564`). The runtime launch registration is **statically present**; it has not been observed executing.

`MsgClean::GetSwitchSet()` (`0x10a130`) serializes its `this+0x2e8` cached string via `AddJsonValueString`. `MsgClean::SetSwitchSet()` (`0x10b0c0`) calls `GetJsonValueString` (`0x10b100`) and directly forwards the resulting string to `AvaNodeMsgCvt::SetSwitchMsg` (`0x10b114`). That routine (`0xbe270`) calls **`ava::Publisher<std::string>::publishWithLine`** (`0xbe41c`) using the publisher at `this+0x440`. This is NOT the `ava_msg_write_prop_int` message type used in v77's unrelated SmartWash enum-24 path.

`MsgClean::SetCleanSwitchSet(std::string&)` (`0x10db60`) compares the new string to the cached switch string, updates on change, and calls `AvaNodeMsgCvt::AddReportMsg` for property **50** (`0x10dbc0`) and the current handler's service ID (`this+0x8` at `0x10dbbc`). The getter, setter, and report form a native *string-valued service-4/property-50 transport*.

## Boundaries that are NOT established

- No verified subscriber/topic for the `std::string` publisher, nor a proven conversion of individual JSON `k` / `v` fields to `SyncStateChange`.
- v76 independently proved name-specific typed `BT::Blackboard::set<int>` writes for `SmartHost`, `SmartAutoMop`, and `SmartAutoWash`, but this study does **not** prove that the property-50 string flows into those setters, or that native station eligibility sees the same live Blackboard.
- The `SmartAutoMop=-1` MIOT readback remains an *unknown signed native state*, not a safe instruction to replace it with 0, 1 or 2.
- No observation yet proves dirt-triggered recleaning, real turbidity-triggered extra mop wash, or any physical rewash.

**Negative control:** v77's `SetSmartWashSwitch` publishes enum 24 to the separate `smart_wash_switch` *string* Blackboard key, not `smart_auto_wash_switch` *integer*.

## Reproducible bounded check

The user-delivered `X40-R2416-v78-sanitized-miot-string-bridge-20261024.zip` includes `x40_r2416_v78_miot_4_50_string_bridge_verify.py`, this analysis and a README, **not** the original ELF. The Python-stdlib-only verifier reads the owner's private `X40-R2416-v62-readonly-20261023T051829Z.zip`; pins the ELF SHA, handler-registration instruction sites, symbol-resolved GOT entries, real PLT call targets and changed-value report; and rejects 15 one-byte instruction mutations.

Verified output:

```text
X40_V78_MIOT_SERVICE4_PROPERTY50_GET_SET_REGISTRATION_PASS
X40_V78_PROPERTY50_STRING_PUBLISHER_NOT_INT_MESSAGE_PASS
X40_V78_PROPERTY50_UPDATE_REPORT_ANCHOR_PASS
X40_V78_STATIC_MUTATIONS_REJECTED count=15
LIMIT: string subscriber topic, MIOT 4:50 individual k/v parsing, Blackboard recipient, physical reclean/rewash unproven
```

**Next:** recover the native string-publisher topic/subscriber registration and the actual `k`/`v` receiver; establish shared Blackboard identity; then connect the native dirt/turbidity decision to a real second-clean or station-wash command.

The live X40 remains on verified v74 with its original launcher restored and `writeGateOpen=false`, `SmartHost=0`, `baselineMatch=true` following the earlier operator-confirmed 1→0 test and disarm. Do not enable the writer, send guessed native values or remove working rollback files.
