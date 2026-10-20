# X40 Stage 20 — offline wash-property reporter investigation

Status: **offline analyzer prepared and tested on synthetic ARM64 ELF only; actual R2416 SIID remains unverified.** No user-device action or firmware write has been performed.

## Evidence chain

1. User-provided prior private R2416 native study recovered a compiled `avanodemsgcvt::MsgClean::RptStationAutoWashState` routine producing MIOT **PIID 61**. The SIID is selected from a `MsgClean` instance, not established by those findings. `SetStationAutoWashState(int,bool)` provides a change/report path; `GetStationAutoWashState(AvaJson&,AvaJson&)` provides a getter for a stored integer. Compiled support does not demonstrate a supported public property, live values, or compatibility with `4:61`.
2. Separate AVA pipeline: `node_signal.so` defines typed `AI_MOP_DIRTY_INFO` publishing and `node_lethe.so` corresponding handlers; `node_camera_ai.so` defines stain-classification handlers. These are separate private message paths, **not demonstrated MIOT properties**.
3. Existing **device-confirmed** `4:50` values are setting snapshots only; `SmartHost=0`, `SmartAutoMop=-1` (unknown, not “off”), `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`. The running `master` fork already exposes these through a cached read-only endpoint, with experimental controls disabled.

## Stage 20 deliverable

A separate Mac-side `x40-stage20-offline-siid.zip` kit was generated containing `stage20_offline_siid.py`, a README and test notes. The user-facing artifact is independent of any firmware or on-robot deployment and is not embedded as a raw proprietary output in Git.

The Python analyzer reads **only** a privately stored, local AArch64 ELF `node_msg_cvt.so`. It uses local `llvm-readelf`/GNU readelf, `c++filt`/llvm-cxxfilt, and `llvm-objdump --disassemble-symbols=<exact mangled symbol>` without `--demangle`. It explicitly verifies that a disassembly header and instructions exist (the LLVM 17 false-zero diagnostic previously identified in Stage 9), tracks only these function families:

- `MsgClean::RptStationAutoWashState`
- `MsgClean::GetStationAutoWashState`
- `MsgClean::SetStationAutoWashState`
- `MsgClean::MsgClean` constructor

It exports **only** an allowlisted JSON summary with bounded member-offset hints and instruction counts. No full disassembly, raw proprietary symbols, paths, runtime values, vendor property payloads, camera imagery, maps or credentials leave the local machine. Tool failures are explicit, rather than interpreted as absence of calls.

### Test evidence

- Standalone parser synthetic tests: **PASS** (symbol matching, exact disassembly header, literal PIID 61 and bounded offset counting, invalid-disassembly rejection).
- An intentionally synthetic **AArch64** C++ shared library was built using clang++ and lld and successfully analyzed: all four function categories were recovered; the synthetic reporter's literal PIID 61 was detected. It is *not* the Dreame firmware.
- Python compilation and generated ZIP integrity: **PASS**.
- **No R2416 firmware has been analyzed in this new Stage 20 run** because the user-local native ELF/archive is not available in the active working directory/session.

### Next gates

1. Owner runs `python3 stage20_offline_siid.py --self-test`, then the offline analyzer on their saved private `node_msg_cvt.so`; share **only** `x40-stage20-sanitized.json`.
2. If the reporter's caller/constructor path can be established through private, verified static analysis, derive the *actual* SIID from the instance initializer rather than guessing an `SIID` from a memory operand or assigning `4:61` from similarity to `4:50`.
3. Only after identity verification can naturally emitted candidate notifications be evaluated for harmless, high-level presence. Stage 19's passive `piid=61` observer is still an **unmerged, undeployed research-only prototype**.
4. Do not enable experimental SmartHost/SmartAutoWash writes, emit AVA messages, add unreviewed MIOT polling ranges, or alter the running `/data/valetudo` installation. Physical cleaning/docking validation is explicitly deferred by the owner.

The companion Stage 19 branch doc remains [Stage 19 passive MIOT candidate research](X40_STAGE19_PASSIVE_MIOT61_RESEARCH.md). No firmware, private measurements, or sensor values have been committed.

## Stage 22 update — resolved compiled service ID; not live verification (2026-10-20)

The user uploaded the corrected collector archive and its sanitized manifest. The private ZIP contains **106 firmware files; all 106 match the archive's SHA-256 manifest and size declarations**, with ZIP CRC integrity verified. Binary source code and raw configuration remain private.

Static AArch64 disassembly establishes **MIOT service 4, property 61** for `MsgClean::StationAutoWashState`:

1. `MsgClean::MsgClean` puts the immediate SIID **4** in the constructor argument and calls `MsgHandler::MsgHandler(int,...)`.
2. `MsgHandler::MsgHandler` stores that argument at the instance's service-ID field.
3. `MsgClean::RptStationAutoWashState` reloads the stored service ID and uses the immediate PIID **61** for the MIOT report.
4. The `MsgClean` constructor registers **get** and **report** handlers for PIID **61**. `SetStationAutoWashState` is an internal stored-value setter that schedules a report on change; it is *not* evidence of an externally writable API.

This proves the firmware's **compiled 4:61 identity**, superseding the earlier unknown-SIID state. It does **not** establish that local MIOT clients can read this property or which numerical values correspond to wash, extra rewash or dirtiness.

New private firmware modules `liblethe_route_nodes.so`, `liblethe_tactics_tree.so`, and `liblethe_tree.so` were recovered. Verified exact direct PLT branches show that `ChooseWashType` invokes both `ChooseSmartHostWashType` and `ChooseAICheckWashType`; `InitTurbidityCheckInfo` invokes `TurbidityRecleanAndRewashSet`; `WashFloorTubidityCheck` invokes `TurbidityMonitorLogicRunEx`; and `WashStateLogic` has a direct tail branch to `WashRunningPrecess`. The route-nodes module contains `MopDirtyAccumulator::tick` and `StateCurrent::WriteAiMopDirtyData`. These support **compiled wash-decision mechanisms**, not observed live operation.

The exact saved `dreame.vacuum.r2416` runtime configuration contains `RUNTIME_TURBIDITY_DETECTION="Single_Channel"`, `RUNTIME_SELF_CLEANING_WASH_PLATE="Y"`, and the independent `turbidity_check_config=true`. These are **static configured capabilities**, not sensor readings or proof of operation.

The undeployed research-only PIID61 passive observer was subsequently restricted to **SIID 4 / PIID 61**; it still never reads a vendor notification `value`, transmits a MIOT query or enables the experimental CleanGenius modes. CI/full robot testing is outstanding. No changes to the installed X40 fork, Valetudo parent binary, original backups, MIOT state, or AVA services. A sanitized audit is available as a conversation artifact outside Git; do not commit proprietary binaries, model weights or raw runtime data.

## Stage 23 — Verified compiled internal update dispatcher (2026-10-20)

The previously supplied private X40 firmware ZIP was reused *offline*. Narrow ELF symbol extent and AArch64 disassembly checks of the actual `node_msg_cvt.so` establish these additional compiled instructions, supplementing Stage 22's `MsgClean` constructor SIID=4 / PIID=61 proof:

- `AvaNodeMsgCvt::SetPropIntMsg(int,int,bool)` has **one exact branch to the PLT entry** for `MsgClean::SetStationAutoWashState(int,bool)`; this is a branch within that dispatch function's declared ELF extent, not an unsafe nearest-symbol annotation. It is a **tail branch**, not an ordinary returning `bl` call.
- The `SetStationAutoWashState` routine checks the existing **stored 32-bit status at object offset 0x2d4**, updates the field if different, and transfers to `AvaNodeMsgCvt::AddReportMsg` with literal property ID **61** and the instance's service ID. This establishes an **internal value-update and report-scheduling path**, not an externally writable property.
- `GetStationAutoWashState` reads the same object field; `RptStationAutoWashState` reads the same field and the service ID stored at object offset 0x8. The three compiled functions share a single state member and are consistent with the Stage 22 verified `4:61` getter/reporter registrations.

The private-archive audit script validates *all four* declared ELF function extents and exact disassembly headers; the real archive returned `COMPILED_DISPATCH_TO_4_61_STORED_STATUS`. Its synthetic, no-network parser self-test passed. The output report contains only Boolean instruction-pattern markers, sanitized function counts and a short binary SHA prefix, with no proprietary ELF/disassembly, native runtime values or credentials. The local script and sanitized report are provided separately in `x40-stage23-native-wash-audit.zip`; no proprietary code is committed to GitHub.

**Still unverified:** the source of the dispatcher's incoming runtime values; whether this X40 answers local MIOT `get_properties(4,61)`; whether actual `properties_changed` events are emitted; numeric status meanings; native mop dirtiness, turbidity measurements or automatic rewash decisions. Do not infer numeric enums from the status member offset or dispatch branch. The branch's passive probe remains undeployed and accepts only a naturally incoming **4:61** notification while ignoring its value. The probe now reports `livePropertySupported=null` (unknown), not `false` (absent).

The narrowly modified pure passive-probe source and its updated tests were replicated in a local offline Node 22 test harness: **7/7 pass**, with syntax check. This does *not* replace a full repository CI build and real X40 integration. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, parent rollback backups and the deferral of the physical cleaning/docking test.

## Stage 24 — typed AVA property update chain, offline verification (2026-10-20)

The owner requested continued offline CleanGenius research. The same privately collected and archived **R2416** libraries were analyzed without network/robot access. An independent analyzer `stage24_offline_prop_path.py` checked the exact ELF symbol sizes, instruction ranges and branch-to-PLT labels in `node_msg_cvt.so`; its output is sanitized as `X40_STAGE24_OFFLINE_AVA_PROPERTY_CHAIN_V1`.

**Compiled converter chain now directly established:**

1. `AvaMsgCvtPropIntProcess(ava_msg_device_prop_int*)` (12-byte ELF function, 3 decoded instructions) uses **one exact tail branch** to `PropIntMsgProcess(ava_msg_device_prop_int&)`.
2. `PropIntMsgProcess` (756-byte function, 188 instructions) uses **two exact PLT branches** (one tail `b`, one `bl`) to `AvaNodeMsgCvt::SetPropIntMsg(int,int,bool)`.
3. `SetPropIntMsg` (4,248-byte function, 1,060 instructions) uses **one exact PLT tail branch** to `MsgClean::SetStationAutoWashState(int,bool)`.
4. The short station setter reads/writes the same private instance member at `0x2d4` and uses literal **PIID 61**, as established independently in Stage 23. Stage 22 established the instance's **SIID 4** and reporter/getter registration.

`node_lethe.so` **also defines** typed `ancp::AsyncDeque::_ProcessAsyncPub<ava_msg_device_prop_int>` and related type machinery. This is a **compiled potential producer**, not a verified concrete caller producing StationAutoWashState 4:61. Symbol presence and the converter's generic dispatcher do not prove that any matching AVA messages were delivered on the running X40 or reveal integer meanings.

The offline Python script self-test, syntax check, real private ZIP CRC and compiled ARM64 audit passed, returning `COMPILED_AVA_INTEGER_TO_STATION_STATUS`. The code and sanitized report were packaged separately in `x40-stage24-offline-prop-path.zip`; the firmware was **not** packaged or committed. The installed `master` fork and backup copies are **unchanged**. The research-only passive notification prototype is still undeployed. **Next gate:** identify a trustworthy, consented local method to read only MIOT 4:61 (or a naturally emitted passive notification), without querying arbitrary properties, altering AVA, enabling experimental SmartHost controls, or interpreting undocumented values as dirtiness/rewash.

## Stage 25 — wash-state blackboard inputs, offline-only (2026-10-20)

An independent **no-network** investigation of the owner's same verified 106-file R2416 archive identified a precise, further compiled wash-state path inside `liblethe_tactics_tree.so`, which was not available in the early native archive:

- `RobotWIFI_Deal::WIFIState_Send::tick()` has a verified **direct PLT call** to `RobotWIFI_Deal::WIFIState_Send::updateStationAutoWashState()` at +780 bytes into the caller.
- The station auto-wash updater makes a verified **direct PLT call** to `BT::Blackboard::get<WashStatus>` at +2232 bytes and a separate direct PLT call to `BT::Blackboard::get<ava_mop_station_msg>` at +2704 bytes.
- Both disassembled functions were checked against their **exact** mangled ELF entry, declared extent and complete AArch64 instruction count: tick **2988 bytes / 747 instructions**; updater **7836 bytes / 1959 instructions**. Only exact `@plt` labels were accepted, to avoid the earlier Stage 9b nearest-symbol annotation problem.

The new `x40-stage25-offline-wash-state.zip` source kit contains a read-only offline Python3 analyzer, synthetic parser/negative tests, README and sanitized result `X40_STAGE25_WASH_STATE_BLACKBOARD_OFFLINE_V1`. Its local `--self-test`, Python compilation, ZIP CRC integrity and real *private* R2416 audit **passed**; no ELF, proprietary code, firmware, maps or raw disassembly was included in the distributed report or Git repository. The tooling includes a regression test for `nop` between decoded instructions, which previously caused an over-strict instruction-count failure and was repaired before publishing the kit.

**Critical boundary:** These exact branches establish **compiled state acquisition** from two internal behaviour-tree data types, *not* that the updater necessarily emits the same numeric value as compiled MIOT `4:61`. Stage 22–24 separately establish the converter-side 4:61 property and generic AVA integer dispatcher. Do **not** assert a verified connection between the two from similarly named functions. The meaning of any numeric station wash status, native turbidity, dirtiness, and rewash decisions remains unknown. No live robot command was made.

The source review of the existing production fork establishes that `DreameMiotHelper.readProperty(4,61)` implements an exact **single `get_properties` request** internally, but no reviewed, publicly exposed or authenticated endpoint on the current installed fork permits calling it as an external arbitrary-property diagnostic. Do not guess vendor CLI flags, demand secrets or deploy the experimental branch to force the read. A live single read can be designed only after establishing a trusted, narrowly scoped local transport with explicit user action. Maintain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and preserve official parent rollback.

## Stage 26 — carefully scoped local read candidate, not executed (2026-10-20)

The completed Stages 22–25 verify **compiled** MIOT `4:61`, a converter-side internal update/report chain, and separate behaviour-tree wash state inputs; they do not establish live accessibility, numeric meanings, or a complete link from behaviour-tree update to reported property.

**Source review:** current `master` implements `DreameMiotHelper.readProperties()` as `get_properties` with precisely `[{did: robot.deviceId, siid, piid}]`. It reads its local auth token from `/data/config/miio/device.token` and `did` + `model` from `/data/config/miio/device.conf`. Independently, python-miio documents a standard `Device.send("get_properties", ...)` and `MiotDevice.get_property_by(siid, piid)` interface.

**Mac-only prototype delivered separately:** `x40-stage26-single-property-read.zip` contains `x40_stage26_read_4_61.py` and instructions. The script's *default invocation is no-network*. Only an explicit `--confirm-one-read` path reads the two **fixed** configuration files via SSH `cat` in memory, checks the exact R2416 model, then uses authenticated local UDP MIIO to invoke `get_properties` for `(4,61)` once at the library API level. It creates a 0600 JSON report exclusively, omitting token, DID, raw exception, raw property payload and (by default) numeric status value. The operator may opt into collecting one small integer state code with a separate flag, but the code remains **semantically unverified**. Network handshake/retry may cause multiple UDP datagrams. No files are installed on the robot, no settings or firmware writes, and no arbitrary property enumeration is possible by modifying CLI arguments.

Offline no-network self-test, Python compilation, dry-run/no-network default and ZIP CRC verification **passed**. The code is **not run against the user's X40**, and therefore neither direct MIIO UDP availability nor `get_properties(4,61)` result support is established. Even a successful code-zero read would prove a protocol response only, not native dirtiness/turbidity/automatic rewash activity. An unreachable port or nonzero response does not disprove compiled firmware capability. The normal Valetudo SmartHost safety routine is **not invoked** by this external standalone local read, though possible native firmware read-handler side effects cannot be guaranteed absent.

The deployed fork, research branch code, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, and official parent rollback assets are unchanged. The owner has deferred physical cleaning and docking tests. Future device execution requires the owner to explicitly run the opt-in command on their Mac.

## Stage 26 — first code-zero live R2416 4:61 read (2026-10-20)

The operator successfully ran the separate Stage26 v3, authenticated, read-only, **single-property** Mac diagnostic after a prior Python virtualenv import failure. Uploaded sanitized report `X40_STAGE26_DIAGNOSTIC_V3` at 2026-10-20T09:53:25Z states: `client_command_attempted=true`, `model_family=r2416_family`, `target_siid=4`, `target_piid=61`, `response_shape_valid=true`, `firmware_code=0`, `code_zero=true`, `value_type=integer`, `live_property_supported=true`, `conclusion=LIVE_4_61_CODE_ZERO`, and `firmware_writes_or_actions=false`. No raw MIOT payload, DID or credentials were persisted. This **closes the live-local-read accessibility gate** for the owner's current X40 hardware, **not** for every X40 firmware variant or every operating state.

The current Stage26 diagnostic defaults to redacting vendor property numbers, so `numeric_state_code=null` is a **redaction placeholder**; it is not a firmware numeric result. There is no known mapping from integer codes to idle/wash/dry/dirtiness/rewash, and no evidence that the station-auto-wash status represents AI dirtiness or a decision to rewash. One successful code-zero GET under unknown physical conditions cannot establish state transitions or passive notifications.

The research-only 4:61 passive notification observer remains **undeployed and never reads vendor value**; its `livePropertySupported=null` field refers to its *own lack of observed notification data*, not to the now independently proven reachability of the local authenticated read. Avoid conflating these two evidence paths. No installed-fork changes, AVA messages or control actions occurred. The next optional, explicitly user-run data point is a single bounded numeric capture using the existing `x40_stage26_diagnostic_v3.py --confirm-one-read --include-numeric-state` and a new private/sanitized report path. A code cannot be assigned semantics until firmware or state-context evidence exists.

## Stage 27 — live zero and constructor-zero evidence (2026-10-20)

The operator's second, narrowly allowlisted local MIOT `get_properties` captured the one integer value of the **verified live R2416 property 4:61**: `numeric_state_code=0` with `firmware_code=0` and `code_zero=true`. The sanitized `X40_STAGE26_DIAGNOSTIC_V3` JSON also shows `allowlisted_numeric_state_persisted=true`, matching SIID/PIID, no firmware actions or writes and no raw vendor payload or credential capture. Numeric zero is a device-returned state value; firmware response code zero is the protocol's separate success indicator.

To interpret the value conservatively, the existing private `node_msg_cvt.so` archive was **reexamined offline** with exact-symbol checks and complete AArch64 function disassembly. Its `MsgClean` constructor copies the instance pointer to a preserved register before zeroing eight bytes at member offset `0x2d0`. The `GetStationAutoWashState`, `SetStationAutoWashState` and `RptStationAutoWashState` functions independently access the same 32-bit `0x2d4` member within the zeroed 8-byte range. This directly verifies **constructor-default station status 0**, not that the particular runtime zero is unchanged.

The separately supplied `x40-stage27-default-zero.zip` contains only a Python3 offline AArch64 ELF analyzer, README, synthetic positive/negative self-tests and sanitized output `X40_STAGE27_DEFAULT_ZERO_OFFLINE_V1`. It passed `py_compile`, synthetic tests, exact four-function size/header/instruction-coverage and matching-memory-offset checks against the actual private archived firmware, and ZIP CRC verification. No raw binary or disassembly was published.

**Limitations:** 0 remains a **numeric value with unknown semantics**. No proof that 0 means idle, no auto wash, no dirtiness or disabled; no proof that the live status was never modified since construction; no observed state transition, forced wash, detected turbidity, AI mop dirtiness or automatic rewash. The branch remains undeployed. The native positive runtime read result applies to this owner device, not universally to all model variants. A future natural, independently corroborated state transition or offline code-path mapping is required before surfacing named statuses in Valetudo. Leave the production fork, experimental write disablement and rollback backups untouched.

## Stage 28 — exact native wash-blackboard key cross-references (2026-10-20)

Using only the owner's earlier validated 106-file **private R2416 firmware archive** (no robot connection), a new strict offline analyzer verified the entire `RobotWIFI_Deal::WIFIState_Send::updateStationAutoWashState()` function from `liblethe_tactics_tree.so`: **7,836 bytes, 1,959 consecutive AArch64 instructions** and the exact ELF symbol/header. It found six unique `.rodata` keys referenced by exact **adjacent `ADRP` + `ADD`** address materializations from inside the function (not a mere `strings` hit):

- `station_auto_wash_stage`: **1** exact instruction reference
- `station_auto_wash_working`: **2**
- `station_auto_wash_pause`: **3**
- `station_auto_wash_out_time`: **1**
- `station_auto_wash_happen_error`: **1**
- `station_auto_wash_back_home`: **1**

The same function's exact named PLT branches include `BT::Blackboard::get<WashStatus>` **1**, `get<ava_mop_station_msg>` **1**, `get<int>` **3**, `set<bool>` **6**, `set<int>` **1** and `set<int&>` **1**. Counts were verified against the user's actual archive; they establish compiled wash-related **read/write behaviour-tree processing**. They do *not* establish the concrete value flow from those keys to the separate `MsgClean::SetStationAutoWashState` path or live MIOT `4:61`.

Standalone no-SSH/no-network script `stage28_offline_blackboard_audit.py`, synthetic negative parser tests (including truncated disassembly rejection), README and sanitized JSON `X40_STAGE28_BLACKBOARD_KEY_XREF_V1` were packaged into **`x40-stage28-wash-blackboard.zip`** as a private-workstation audit utility. The script and real R2416 firmware audit passed, ZIP CRC verified. The ZIP **contains no** proprietary firmware, disassembly, vendor payloads, maps, raw camera imagery, or secrets. A short binary SHA prefix is included only for local provenance.

**Status semantics boundary:** separately observed `MIOT 4:61=0` is still only a known live integer; Stage 27 proved that zero is also constructor-default but not whether the live value was never changed. The named working/pause/error/timeout/return-stage blackboard fields are *not* a verified numeric mapping for 4:61, nor proof that AI dirtiness/turbidity triggers a rewash. Neither this stage nor its script connected to the robot, queried MIOT, enabled CleanGenius, or changed Valetudo. The research-only passive 4:61 prototype remains unmerged and undeployed; the production fork and parent backups are preserved. Next offline investigation should trace the **specific producer** of `ava_msg_device_prop_int` for the station-auto-wash property, or use independently corroborated natural wash-state transitions to discover semantics (not an induced cleaning cycle).

## Stage 29 — cross-library station wash blackboard key references (2026-10-20)

The user's existing private, integrity-validated 106-file R2416 firmware archive was audited further **offline** with no on-robot or network operations.

A full streamed AArch64 disassembly scan of `node_lethe.so` covered **1,929,367 instructions**, checking exact adjacent `ADRP`+`ADD` address materializations against individually unique ELF `.rodata` keys and attributing the call sites to declared named ELF function extents. Verified matches:

- `station_auto_wash_working`: **7** within `node_lethe.so`; associated contexts include `CheckRobotSelfClean`, `AvaNodeRoute::SendWashLogicOTA`, `SendGyroCalibrateCmd`, `SendDrainMotorCloseProcect`, `PropStringControl::EnableOrderClean`, `GetStandbyRobotState`, and `GetChargerRobotState` (each one exact xref).
- `station_auto_wash_happen_error`: **1** within `node_lethe.so`, in `DeviceMsgFromAppDeal::ChangeDeviceMsg`.

The same precise key strings were independently verified in `liblethe_tactics_tree.so`'s exact **7,836-byte** `WIFIState_Send::updateStationAutoWashState()`: **2** `station_auto_wash_working` and **1** `station_auto_wash_happen_error` references. These cross-library matching key names strengthen the compiled state-processing context but **do not** prove a shared runtime `BT::Blackboard` instance or property-value flow between components.

Inside the exact **3,104-byte** `AvaNodeRoute::SendWashLogicOTA()`, direct `@plt` branch analysis also confirms calls to `BT::Blackboard::get<WashStatus>` **1**, `get<int>` **1**, `set<int>` **3**, and `AsyncDeque::MultAsyncPublish<_CtrlMcuCMD...>` **2**. This verifies one compiled path for **MCU-control publishing** in a station-wash context. **The target message type is not the converter-side `ava_msg_device_prop_int`**, and this evidence does *not* identify a specific producer of the MIOT `4:61` station-auto-wash integer.

A no-network standalone Python source kit `x40-stage29-native-bridge-audit.zip` (script, sanitized JSON, README and tests, no firmware) was assembled and passed Python compilation, parser self-tests, real archive CRC / AArch64 exact-symbol audit and output ZIP CRC. The sanitized report marker is `X40_STAGE29_NATIVE_CROSS_LIBRARY_WASH_KEYS_V1` and the conclusion is `NATIVE_WASH_KEY_CROSS_LIBRARY_XREFS_VERIFIED`; flags for `same_runtime_blackboard_object_proven`, `native_station_state_to_miot_4_61_producer_proven`, and `numeric_miot_4_61_value_0_interpreted` all remain **false**.

The device's previously live-observed `4:61=0` remains unclassified, and zero is a compiled constructor default. This investigation does not demonstrate a cleaning, turbidity, AI dirtiness or rewash event. No robot access, MiOT request, firmware mutation, deployed fork change or experimental writes occurred. Preserve the current stable `master` installation, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and rollback assets; physical wash retest remains deferred.

## Stage 30 — exact typed device-property blackboard callers (2026-10-20)

**All analysis offline; no additional device action.** A new standalone, no-network Python/LLVM audit reused the owner's previously uploaded, SHA/CRC-verified private 106-file R2416 archive. It scanned the **entire** `node_lethe.so` disassembly (**1,929,367 decoded AArch64 instructions**) for **exact** direct `b` or `bl` calls to two specifically identified ELF PLT entries:

- `BT::Blackboard::get<ava_msg_device_prop_int>`: **12 direct call sites**; **10 function-owner groups, one of which is unnamed/unattributable** because the instruction address does not fall inside a trustworthy named ELF function extent.
- `BT::Blackboard::set<ava_msg_device_prop_int&>`: **2 direct call sites**, both with verified named function owners: `AvaNodeRoute::ExtrStrAdd` and `AvaNodeRoute::CleanLogAndSetLastAppMap`.
- Named typed message **getter** callers include `AvaNodeRoute::SendRobotStatueToWIFI` (**1**), `SendRobotMapStateToWIFI` (**1**), `CleanAreaControlAndSend` (**2**), `ExtrStrAdd` (**1**), `CleanLogAndSetLastAppMap` (**1**), plus other map/statistics/state routines. These are not evidence that the corresponding message carries StationAutoWashState.
- In particular, `AvaNodeRoute::SendWashLogicOTA` and `CheckRobotSelfClean` have **zero exact direct calls to those specific typed getter/setter PLT entries**.
- The exact, independently verified `RobotWIFI_Deal::WIFIState_Send::updateStationAutoWashState()` from `liblethe_tactics_tree.so` has **7,836 bytes / 1,959 consecutive decoded instructions** and **zero exact direct calls to the same typed getter/setter entries**.
- `ancp::AsyncDeque::_ProcessAsyncPub<ava_msg_device_prop_int>` is compiled in `node_lethe.so`. A generic typed publisher implementation is **not evidence identifying the concrete property value producer**, and an inlined or indirect producer could evade these direct-call checks.

These are deliberately **narrow, positively established ELF call-site results**, not a whole-program data-flow proof of non-communication. Stage 24 independently confirmed the incoming `ava_msg_device_prop_int → MsgClean::SetStationAutoWashState` **consumer** path, and Stage 26 independently demonstrated a valid live `get_properties(4,61)` response with numeric value **0**. Stage 27 confirmed constructor-default zero. Neither investigation has yet linked a particular upstream native event or blackboard value to the consumer path, decoded integer enums, measured dirtiness or verified an automatic rewash decision.

**Reproducibility:** `x40-stage30-typed-property-xrefs.zip` contains standalone `stage30_typed_xrefs.py`, synthetic exact-PLT self-test, README and sanitized `X40_STAGE30_TYPED_DEVICE_PROPERTY_CALLSITE_V1` report. Python compilation, parser tests, real firmware archive scan and output ZIP integrity passed. One failed intermediate audit correctly exposed an unnamed ELF function-owner interval and a leading-zero LLVM header mismatch; both were corrected before publishing, and that uncertain attribution is explicitly reported rather than guessed. No proprietary binary/config/disassembly, map/camera content or private keys were added to this repository. No MIOT requests, firmware writes, new installation or cleaning/dock cycle occurred.

**Next useful evidence:** a local, narrowly scoped static data-flow/cross-reference review of the **unknown function-owner getter site**, the two typed blackboard setter call sites, and the specific typed AVA publisher's message creation. Avoid inferring a direct bridge from similarly named wash functions. Leave the stable production fork, the disabled experimental write policy and rollback backups untouched.

## Stage 31 — keyed typed-writer provenance and source-register ambiguity (2026-10-20)

The original, CRC/SHA-verified **private R2416** archive was re-examined without robot/network access to follow the two `BT::Blackboard::set<ava_msg_device_prop_int&>` call sites found in Stage 30.

A bounded, exact-function ELF/ARM64 analyzer checked both writer functions: `AvaNodeRoute::CleanLogAndSetLastAppMap` **29,824 bytes** and `AvaNodeRoute::ExtrStrAdd` **64,180 bytes**. Both functions' complete, consecutive instructions and single **exact** `set<ava_msg_device_prop_int&>@plt` calls were verified. The `node_lethe.so` SHA-256 prefix matches prior audited provenance `b34eb5c71bccd903`.

**New positive evidence:** `CleanLogAndSetLastAppMap` materializes the **literal** `WIFI_Robot_State` using an exact, adjacent `ADRP`+offset-`ADD` sequence whose resulting address was verified against the actual `.rodata` bytes. It sets up a temporary string near a direct typed-message blackboard setter call. This is a **verified nearby key setup**, not whole-program proof that this literal is used as the setter key on every possible runtime path.

**Important corrective constraint:** `ExtrStrAdd` also has the typed setter and a nearby `#0x598` offset in an `ADD`, but the instruction's **base register cannot be proven to still carry the literal page**: it has other assignments elsewhere in the large function. Therefore **do not attribute `WIFI_Robot_State` to that setter from the offset alone**, despite matching superficial assembly. An updated parser rejects unproven register provenance and source clobbering. The Stage 30 single typed getter call site beyond the named ELF function extent also remains deliberately unattributed.

No verified direct/indirect bridge has been found from the Stage 28 `station_auto_wash_*` blackboard keys to the generic typed message's concrete property payload or live `4:61`. The device's previously confirmed `4:61=0` remains an **unmapped integer**, and constructor default zero is not a status label. No AVA/MIOT/wash control was exercised.

The standalone privacy-filtered reproducible artifact **`x40-stage31-key-provenance.zip`** includes `stage31_key_provenance.py`, a synthetic exact-literal/negative-source-provenance self-test, README, TEST_NOTES and JSON `X40_STAGE31_TYPED_WRITER_KEY_PROVENANCE_V1`. Python compilation, self-tests, real archive structural audit, output ZIP CRC and integrity checks passed. The firmware, disassembly, credentials and raw config remain **outside GitHub**. Preserve working installed Valetudo+, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, original/parent rollback and the owner's deferred physical wash/dock test. Future work should follow verified **typed payload construction and publisher registration**, with explicit CFG/register checks; no named status should be exposed yet.

## Stage 32 — typed internal selector 57 resolves to StationAutoWashState (2026-10-20)

**Offline only:** Reused the user's privately preserved, previously verified R2416 native ZIP. A new strict ELF/AArch64 investigation of `node_msg_cvt.so` recovered an important precise **internal message selector** for the already firmware-proven and live-readable MIOT `4:61` property.

- In `AvaNodeMsgCvt::SetPropIntMsg(int,int,bool)` (exact **4248-byte** ELF extent, all **1062** AArch64 instructions verified), the unique adjacent instruction pair **`cmp w1,#0x39`** followed by `b.eq` enters a local dispatch block. That block reaches an **exact `b` tail call to `MsgClean::SetStationAutoWashState(int,bool)@plt`**. This proves **internal enum selector decimal 57**, which is **not** MIOT property ID 61.
- The typed `AvaMsgCvtPropIntProcess` callback (exact **12 bytes / 3 instructions**) directly branches into `PropIntMsgProcess` (exact **756 / 189**). The processor compares and copies **252 bytes** in a cached integer-message snapshot using `memcmp`/`memcpy`. It has both a one-index update path with the observed `[x22 + 4 + 4*index]` access and a full-delta scan path that reaches the same `SetPropIntMsg` routine. The indexed access for selector 57 corresponds to **byte offset 232** relative to the start of that typed message buffer. This is a **compiled layout fact, not a captured value**.
- The separately exact-checked setter (**48 bytes / 12 instructions**) compares and writes the 32-bit instance member `0x2d4` and schedules `AddReportMsg` with literal **PIID 61**, and its instance's **SIID 4** was established in Stage 22.
- **Boundary:** The audit identifies the converter-side **consumer selector** used for station auto wash, but does **not** trace the specific upstream Lethe producer that creates/sends selector 57, show a nonzero runtime event, establish status-code enums, or prove turbidity, AI dirtiness or rewash logic reaches the published property. The actual live reading `4:61=0` remains unmapped.

The independently reproducible `x40-stage32-typed-selector.zip` contains only `stage32_typed_selector.py`, README, synthetic exact-branch negative tests and privacy-filtered `X40_STAGE32_INTERNAL_SELECTOR_57_V1` JSON; **no proprietary firmware or disassembly**. Self-test, Python compilation, exact four-function real-archive audit and ZIP CRC **passed**. The sanitized report concludes `COMPILED_TYPED_SELECTOR_57_TO_MIOT_4_61_VERIFIED` with `specific_upstream_sender_of_selector_57_verified=false` and `numeric_miot_state_0_interpreted=false`. No X40 network/SSH/MIOT requests or changes to deployed Valetudo+ occurred. The experimental CleanGenius controls stay disabled and rollback backups remain intact.

Next worthwhile static task is to identify a *concrete producer that populates **index 57** of the typed device-property integer message*, with demonstrable register/address/CFG provenance. Do not equate numeric selector 57 with property 61 or guess based on grep/nearest symbols.

## Stage 33 — producer-side index-57 triage (2026-10-20)

A scoped, **completely offline** analysis of the owner's previously captured SHA/CRC-validated private 106-file R2416 archive followed Stage 32's internal converter selector **57** (distinct from MIOT **4:61**). No robot connection, new property reads, AVA injection, firmware writes or installed Valetudo+ modifications took place.

The reproducible `x40-stage33-producer-triage.zip` kit contains a standalone Python 3 / LLVM analyzer, synthetic exact-immediate/type-target tests, README and allowlisted `X40_STAGE33_SELECTOR57_PRODUCER_TRIAGE_V1` JSON; **no proprietary ELF or instruction dump**. Python compilation, self-test, private ZIP CRC, pinned AArch64 ELF SHA prefix `b34eb5c71bccd903`, complete exact-symbol disassembly and output ZIP integrity all passed.

**Direct facts from `node_lethe.so`:**

- Full native disassembly covered **1,929,367 ARM64 instructions**. Exactly matching literal immediate `#0x39` and not false prefix `#0x390` yields mnemonic counts `cmp=8`, `mov=3`, `ror=3`, `ldrb=1`, `strb=1`. These appearances alone **do not identify the selector-57 producer**: other library/parser arithmetic and unrelated access patterns also use literal 57.
- The type-specific `ava_msg_device_prop_int` blackboard **reader** `AvaNodeRoute::SendRobotStatueToWIFI()` is verified at its exact **4,456-byte / 1,114-instruction** ELF extent: **one** exact direct call to `BT::Blackboard::get<ava_msg_device_prop_int>`, **two** exact direct calls to `AsyncDeque::MultAsyncPublish<ava_msg_device_status,...>` and **zero** direct typed `set<ava_msg_device_prop_int&>` calls. Its observed direct output message **type differs** from the typed property publisher sought. This is not a whole-program absence proof; it excludes treating these two direct calls as producer evidence.
- A restricted **32-bit `str wN,[xBase,#0xe8]`** scan found **five** candidates: **three** in `AvaNodeRoute::MopUpraiseMotorConvert`, **one** in `SaveBatteryInfoSUB`, and **one** in `ZSTDMT_compressStream_generic`. None is proven to target a buffer of type `ava_msg_device_prop_int`. The offset **232** is also used in unrelated memory objects; simple offset coincidence is not a provenance proof. Indexed stores, pair stores, bulk copies, aliases, and inlining remain unexcluded.
- A generic `AsyncDeque::_ProcessAsyncPub<ava_msg_device_prop_int>` implementation is compiled, but that templated machinery alone does not name a sender or specific index-57 source.

The sanitized conclusion is **`TYPE_SPECIFIC_READER_AND_OFFSET_CANDIDATES_FOUND_PRODUCER_UNVERIFIED`** with `actual_selector57_producer_identified=false`. Stage 32's exact consumer selector 57 → setter → compiled MIOT 4:61 remains valid, as does the earlier **live code-zero read of integer 0**. Its **numeric meaning remains unknown**. This stage does **not** establish native AI dirtiness/turbidity reporting or a rewash decision.

**Next source-only gate:** explicit register, buffer-type and data-flow provenance for *construction of the 252-byte typed property message*, followed by a concrete producer/publisher trace for word index 57. Do not infer a connection from names, offsets or co-occurring numbers. Preserve the installed stable fork, `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, original and parent rollback assets, and the owner's postponed physical wash/dock test.

## Stage 34 — concrete whole-message typed blackboard copy path (2026-10-20)

The operator asked to continue **offline** research using the previously collected, CRC/SHA-verified private 106-file R2416 firmware ZIP. A standalone no-network `stage34_bulk_message_audit.py` was created and **run against the actual private `node_lethe.so`**, pinned SHA-256 prefix `b34eb5c71bccd903`. The script verifies AArch64 ELF format, precise function extents and **all** decoded instructions of three exact native functions:

- `AvaNodeRoute::CleanLogAndSetLastAppMap`: **29,824 bytes / 7,456 consecutive instructions**.
- `BT::Blackboard::get<ava_msg_device_prop_int>`: **580 bytes / 145 instructions**.
- `BT::Blackboard::set<ava_msg_device_prop_int&>`: **248 bytes / 62 instructions**.

**New confirmed compiled structure:** The same `CleanLogAndSetLastAppMap` function has an exact direct typed **get** call early and exact typed **set** call later. It constructs the typed-buffer pointer `x28 = sp + 0x310`, then moves `x28` to the third argument `x2` at **both** call sites. The exact `WIFI_Robot_State` string bytes in `.rodata` and literal-page address setup near both sites are verified. The type-specialized blackboard getter contains **two** separate direct `memcpy` calls of **0xfc / 252 bytes**, transferring a complete typed record; the type-specialized setter requests a **252-byte allocation**, performs **one 252-byte `memcpy`**, then dispatches through a blackboard virtual method. This creates a concrete compiled **typed message read / bulk copy / write call-site pattern**, not merely name/offset similarity.

**Limits carefully retained:** Even though get and set use the same local stack *register*, this is **not a complete control-flow / alias analysis** establishing that both calls execute on all paths; other paths restore the callee-saved register. Crucially no checked instruction establishes **who assigns the selector-57 word at byte offset 232 of this typed record**. The copy operations offer a concrete reason that Stage 33's direct `str [xBase,#0xe8]` search could miss property updates; they do **not** prove this caller changes selector 57 or provides the live value of compiled/accessible MIOT **4:61**. The earlier device observation `4:61=0` remains an integer with unknown semantics and compiled constructor-default 0.

**Artifact/validation:** `x40-stage34-bulk-message.zip` holds only the standalone offline script, README, test notes and sanitized `X40_STAGE34_TYPED_252B_READ_COPY_WRITE_V1` JSON; no proprietary ELF, executable vendor code, full disassembly, map, raw config, device ID, token or camera data. Offline Python compilation, positive/negative synthetic tests, exact ELF function/call/key/constant checks on real saved R2416 binary and output ZIP CRC all **passed**. The self-test rejects mismatched call targets, buffer arguments and copy lengths. No robot connection, MIOT, AVA, firmware write, install or physical wash/dock cycle was performed. Working production Valetudo+ fork, experimental write disablement and original/parent rollback files remain unchanged.

**Next meaningful static gate:** establish one actual word-57 assignment inside a verified `ava_msg_device_prop_int` object (possibly via indexed writes, aliases, helper calls or whole-record copies) and the concrete publisher registration, not just typed blackboard transfer. Do not surface named states or auto-rewash claims.
