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
