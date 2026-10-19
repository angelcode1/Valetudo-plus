# Experimental X40 native CleanGenius research

This branch is derived from Valetudo+ and remains synced to its upstream Valetudo ancestor at the fork point. No automatic firmware flashing, native process replacement, cloud access, or device actions are added.

## Default behaviour

With no environment variable, the X40 continues to use Valetudo's normal CleanGenius auto-disable behavior. **Nothing in this feature is enabled by default.** Other Dreame models are unchanged.

For supervised hardware trials only, set `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1` **before** starting the Valetudo process, and restart it. The X40 quirks interface will then expose three experimental selectors:

- CleanGenius: off, routine, deep (SmartHost 0/1/2)
- Auto Reclean: off, deep_only, all_modes (SmartAutoMop 0/1/2)
- Auto Rewash: off, deep_only, all_modes (SmartAutoWash 0/1/2)

These fields are based on Tasshack's Dreame vacuum protocol reference and are **not proven to work on your individual X40 firmware**. Unknown or unsupported values fail closed: the selectors will not serialize successfully, and setters refuse to write. Setters also require a polled idle mode and idle task status. Writes use single-key MIOT 4:50 deltas and are not automatically retried.

**This is not a complete feature restoration.** CleanGenius may override the X40's manual fan, water, cleaning route, segment and mode settings. The Valetudo UI does not yet disable conflicting actions. Do not leave experimental mode enabled during unattended jobs; test the robot in a controlled environment. Do not assume `SmartHost=0` is a universal emergency-stop. Retain normal physical stop controls.

## Before a device trial

1. Record the as-received firmware/hardware identifiers and collect supported original flash samples before rooting.
2. Build and test the fork offline, with the experimental environment variable absent.
3. Verify the unchanged default behavior, existing multi-map, camera and MQTT features.
4. Verify the experimental controls using a fake MIOT helper; no hardware writes should happen in unit tests.
5. Read MIOT 4:50 first on the actual X40. Record the unmodified response, supported keys, current values and device idle-state fields.
6. Activate experimental mode only for supervised tests, with router-enforced WAN isolation, after confirming correct rollback procedures.
7. Record accepted writes **and** readback, mode/task transitions, mop-wash cycles and secondary passes. An accepted MIOT write alone does not prove CleanGenius works.
8. If native behavior is demonstrated, implement command conflict interlocks, event reporting, capability-specific MQTT/Home Assistant entities and optional Matter transport as separate reviewable changes.

## Upstream policy

Do not automatically open a PR against Hypfer/Valetudo. This is X40-specific experimental functionality, contradicts upstream's intentional CleanGenius disabling and has not been hardware-tested. Only submit a narrow upstream PR after device verification and discussion with maintainers. Do not claim hardware validation or official support.

## Sources

- https://github.com/Hypfer/Valetudo
- https://github.com/Algid/Valetudo-plus
- https://github.com/Tasshack/dreame-vacuum

## R2416 / 4.3.9_1782 device observation (2026-10-19)

A single supervised read-only MIOT `get_properties` query for SIID 4, PIID 50 succeeded on the user's X40 while docked and idle. The sanitized report contained 36 entries, 30 known numeric settings, and no factory credentials or map/camera data.

| Native key | Observed | Interpretation and safeguards |
| --- | ---: | --- |
| `SmartHost` | `0` | CleanGenius currently off; stock Valetudo may force it off, so capability is not disproved |
| `SmartAutoMop` | `-1` | Sentinel/unknown value; **do not infer disabled, supported, or writable** |
| `SmartAutoWash` | `0` | Auto rewash off at observation |
| `StainIdentify` | `1` | Native stain-related tunable enabled; not proof of observable inference results |
| `HotWash` | `1` | Native hot-wash setting enabled; dock temperatures not measured |
| `MeticulousTwist` | `-7` | Sentinel/unknown value; not a conventional 0/1 toggle |
| `BackWashType` | `1` | Mop wash cycle configuration; exact meaning not yet verified |
| `CleanRoute` | `1` | Native route configuration; model-specific range must be validated |

The active stock release is Valetudo 2026.10.0. Its Gen2 state parser normally writes `SmartHost=0` after observing `SmartHost>0`; therefore an observed zero cannot establish whether the feature is actually available. This experimental branch bypasses that policy *only when explicitly enabled*, which has **not** been tested on the hardware.

The independent X40 report https://github.com/Tasshack/dreame-vacuum/issues/982 also contains `SmartAutoMop=-1` and `MeticulousTwist=-7`; neither negative value is unique evidence of firmware corruption. That reference does not establish their precise semantics.

### Device-derived guardrail

Keep the existing strict decoding behavior: `SmartAutoMop=-1` causes the experimental Auto Reclean quirk's getter to reject (so Valetudo omits that quirk from the UI), and its setter must reject without issuing `set_properties`. Never coerce `-1` or `-7` into `0`, or overwrite the entire MIOT 4:50 settings blob.

No new cleaning commands, firmware writes, cloud dependencies or production behavior changes are authorized by this observation. Since map validation has been deferred, postpone hardware trials of CleanGenius and auto-reclean until reliable map/dock operation is established. Offline research and fake-helper tests can continue independently.

## Offline R2416 native stain pipeline evidence (2026-10-19)

Static analysis of a user-supplied, limited extraction of the DustBuilder `r2416` rootfs identified the following **compiled capabilities**; this is not proof that the features are enabled or invoked at runtime:

- `/ava/lib/node_camera_ai.so` dynamically exports `camera_ai::StainDetectionJob::Inference`, `camera_ai::CameraAINode::ConvertIntoAIStainResult`, `camera_ai::CameraAINode::ProcessWashStainClassificationRequest(ava_msg_wash_stain_classification*)`, and `camera_ai::StainClassificationJob` classifiers.
- The binary contains the internal AVA bus/service name `AI_WASH_STAIN_CLASSIFICATION_SERVICE` and other distinct topic names including `AI_CLASSIFICATION_RESULT`. Do **not** equate these internal AVA messages with the external MIOT 4:50 AutoSwitch settings.
- ARM64 disassembly of the wash-stain request handler shows branch values 1, 2, and 3 selecting the Dreame202404, Maibo202502Series50, and Maibo202502Series40 logistic-regression classifiers respectively; unsupported selector values return a default response. The C++ method consumes numeric inputs and writes a result through a pointer. The message ABI is **not documented or independently validated**; do not send synthetic requests.
- `/ava/conf/ai_models/MR813/dreame_stain1_v1.3.0.json` specifies a single `stain` category, detection threshold `0.7`, and an image shape `672 x 300`. This is a model configuration, not an observed classification event. The underlying `.mnn` model file was **not** included in this extraction.
- `/ava/lib/node_map_divide.so` contains `stain`, `STAIN_NEED_FILTER`, and `stubborn_stain` strings, plus AI room/furniture/material handlers. The relationship between these strings and camera stain output is not yet established.
- `/usr/bin/dreameiot` did not yield stain or SmartHost-related strings in the supplied string scan; absence of strings in this one binary does not imply the local MIOT property is absent. A separate on-device read of MIOT 4:50 has already succeeded.
- A secondary finding: `/usr/bin/dreame-rvc-app-1.4` contains compiled Matter RVC mode, service-area, commissioning, and operational-state code and refers to `/data/matter/chip_kvs`. Earlier inspection of `/etc/rc.d/matter.sh` found an inert stub, so compiled capability does not demonstrate an active native Matter server. Keep that investigation separate from CleanGenius.

### Next evidence required before enabling controls

1. Inspect the as-built `/ava/conf/r2416.conf` and relevant camera-AI mission configuration **offline**, reporting only service enablement and model references, never secret values or camera imagery.
2. Identify the intended **producer, consumer and message schema** of the internal wash-stain classification service from benign static analysis. No `LD_PRELOAD` hooks, arbitrary AVA bus publications, or library injection against the running robot at this stage.
3. Determine whether native AI results (labels/confidences, not images) reach existing local MIOT events or a permitted Valetudo polling path. A service name in a binary alone is not sufficient.
4. Preserve currently running upstream Valetudo 2026.10.0. Do not merge or deploy the experimental controls while the map is incomplete or the MIOT `SmartAutoMop=-1` sentinel semantics remain unknown.
5. Keep firmware binaries, model weights, factory credentials, MACs, personal maps and live video **out of this public repository**.


## R2416 camera-AI configuration references (2026-10-19)

A user-supplied file listing and **filtered `r2416.conf` lines** from the DustBuilder rootfs confirm the firmware config explicitly references the stain model, rather than merely bundling its binary:

- `/ava/conf/r2416.conf:146` sets `sysModelType` to `dreame.vacuum.r2416`.
- `/ava/conf/r2416.conf:390` identifies a `camera_ai` configuration block.
- `/ava/conf/r2416.conf:411-413` references `/ava/conf/ai_models/MR813/dreame_stain1_v1.3.0.mnn` and `dreame_stain1_v1.3.0.json`.
- The same model configuration references furniture, fused-obstacle, carpet, human, material, room segmentation, and LiDAR furniture AI models.
- The firmware inventory also includes `/ava/conf/auto_water_ctrl_config.json` and `/ava/conf/turbidity_check_config.json`, plus `node_cmd.so`, `node_iot.so`, `node_msg_cvt.so`, `node_camera_ai.so` and `node_map_divide.so`.

This corroborates **configured model references**, not runtime activation or a demonstrated path from AI inference to CleanGenius/MIOT. A string reference to `AI_WASH_STAIN_CLASSIFICATION_SERVICE` does not establish the request schema or identify its producer/consumer. Follow up by performing a private **offline** key-shape inventory of the water/turbidity configuration and a module-by-module *presence-only* service string cross-reference. Do not transmit internal messages, install hooks, or issue model/cleaning commands on the robot. No raw firmware, credentials, images or maps should be included in Git.


## R2416 Stage 4 — candidate native CleanGenius decision boundary (2026-10-19)

A privacy-filtered, **offline** SquashFS report (`x40-offline-stain-stage4-v1`) scanned 12 selected AVA native libraries. Important string-occurrence results:

| Native module | Evidence |
| --- | --- |
| `node_camera_ai.so` | `AI_WASH_STAIN_CLASSIFICATION_SERVICE` (1), `AI_CLASSIFICATION_RESULT` (1), `StainDetectionJob` (10), `StainClassificationJob` (5), `ProcessWashStainClassificationRequest` (1) |
| `node_lethe.so` | `AI_WASH_STAIN_CLASSIFICATION_SERVICE` (1), `AI_CLASSIFICATION_RESULT` (1), `SmartHost` (6), `SmartAutoMop` (3), `SmartAutoWash` (3), `StainIdentify` (1), `BackWashType` (9), `Turbidity` (20), `turbidity` (21) |
| `node_map_divide.so` | `AI_CLASSIFICATION_RESULT` (1), `STAIN_NEED_FILTER` (1), `stubborn_stain` (1) |
| `node_iot.so`, `node_cmd.so`, `node_msg_cvt.so` | No **matching allowlisted strings** in this scan; this is not proof those nodes never carry associated messages. |

**Inference, not established runtime behavior:** `node_camera_ai.so` likely offers stain inference/classification while `node_lethe.so` is the best candidate for *consuming* an AVA result and making cleaning or rewash decisions, because service and MIOT-key references coexist. A literal string match does not prove publisher/subscriber direction, that a handler is enabled, that a request is issued, or that an external Valetudo API exists. We must not patch/inject AVA messages based on this evidence alone.

The report also confirms that `r2416.conf` has key paths `nodes.[].auto_water_config_file_path`, `nodes.[].turbidity_check_config_file_path`, and `nodes.[].stain.model`; the configuration files `auto_water_ctrl_config.json` and `turbidity_check_config.json` parse as JSON. It reports R2416-specific `RUNTIME_TURBIDITY_DETECTION` and other wash/tank-water key **names** in `dconf_runtime.json`, but not their values. The same file carries hundreds of entries from other Dreame models: never mistake mere cross-model key presence for enabled R2416 hardware.

**Next investigation:** read-only, offline extraction of **only the R2416** runtime flag values (safe Boolean/0/1), the water/turbidity config *key shapes* (no numeric thresholds), and dynamic symbol/relationship hints for `node_lethe.so` vs `node_camera_ai.so`. Then trace AVA service producer/consumer references using offline reverse engineering. No robot commands or privileged injection are needed.

Separate third-party code (`malard/node-dreame`, `src/spec/feature-config.ts`) describes `-1` as a disabled-state sentinel for some multi-mode keys including `SmartAutoMop`. Treat this as an **unverified external interpretation**, not license to coerce the X40's observed `SmartAutoMop=-1` to `0` or enable experimental setters; keep the current fail-closed behavior until model-specific readback/behavior evidence exists.


## Stage 5 R2416 firmware results — turbidity flags and native CleanGenius (2026-10-19)

The user's `stage5-r2416-sanitized-summary.json` comes from an **offline** SquashFS extraction. It confirms the following facts for `dreame.vacuum.r2416`:

- `dconf_runtime.json` contains `RUNTIME_TURBIDITY_DETECTION`, `RUNTIME_SELF_CLEANING_WASH_PLATE`, `RUNTIME_AUTO_WATER_FILLING_MACHINE`, tank-position/level checks and drainage entries. The report marks their values `kind: str`, `redacted_or_uninterpreted`. **Presence is not proof of enabled state**. They may require interpreting literal string booleans.
- `turbidity_check_config.json` parses and exposes a top-level `turbidity_check_config` entry whose **type is Boolean**. Its actual value was not included. Even `true` in the saved image would be a configuration clue, not evidence of live turbidity measurements.
- `auto_water_ctrl_config.json` includes a `default` branch and several *other-model* `wash_id` entries, but the sanitized results do not establish any R2416-specific entry. Do not infer a missing capability; the firmware may fall back to a default.
- `r2416.conf` contains 30 nodes, with `bsp`, `camera_ai`, `cmd`, `iot`, and `msg_cvt` recognized in the privacy-filtered scan.
- `node_lethe.so` static strings include `AI_WASH_STAIN_CLASSIFICATION_SERVICE`, `AI_CLASSIFICATION_RESULT`, `SmartHost`, `SmartAutoMop`, `SmartAutoWash`, `StainIdentify`, `BackWashType` and turbidity names. `node_camera_ai.so` contains the same named classification service plus a `ProcessWashStainClassificationRequest` reference.
- The optional dynamic ELF-symbol analysis was **unavailable** in this run. This is a tooling gap, **not** evidence that the ELF exports/imports are absent.

**Working hypothesis:** `node_lethe.so` likely participates in cleaning decisions and may consume results from `node_camera_ai.so`, but no cross-reference or runtime message trace establishes producer/consumer direction yet. The AVA service does not automatically expose a Valetudo MIOT status property.

**Next fully offline checks:** (1) read only allowlisted 0/1/true/false/on/off model-specific flag literals and the turbidity config Boolean, (2) recover `greadelf`/LLVM dynamic symbol metadata from `node_lethe.so` and `node_camera_ai.so`, and (3) investigate service-message direction in a standalone disassembler if necessary. Keep the robot's installed Valetudo 2026.10.0 intact. No AVA messages, firmware writes, runtime hooks or synthetic cleaning requests.


## R2416 Stage 6: runtime configuration literals (2026-10-19)

The user supplied a **read-only offline** JSON report from the saved `4.3.9_1782` SquashFS image. It contains one `dreame.vacuum.r2416` dconf block and confirms:

| Configuration | Offline parsed literal | Scope of claim |
| --- | --- | --- |
| `RUNTIME_AUTO_WATER_FILLING_MACHINE` | string `"true"` (interpreted true) | Saved configuration enables this flag |
| `RUNTIME_AUTO_WATER_SUPPLY_DRAINAGE` | string `"true"` (interpreted true) | Saved configuration enables this flag |
| `RUNTIME_CLEANING_TRAY_FULL_WATER_DETECTION` | string `"true"` (interpreted true) | Saved configuration enables this flag |
| top-level `turbidity_check_config` | Boolean `true` | Saved check configuration enabled |
| `RUNTIME_TURBIDITY_DETECTION` | `unrecognized_redacted` | **Unknown**, not proven enabled or disabled |
| `RUNTIME_SELF_CLEANING_WASH_PLATE` | `unrecognized_redacted` | **Unknown**, not proven enabled or disabled |

Other water/tank flags are similarly redacted and uninterpreted. `auto_water_ctrl_config.json` has a default branch but no exact `dreame.vacuum.r2416` branch; this does not establish which fallback the running device selects.

The module string matches corroborate the Stage 4 candidate topology: `node_lethe.so` references `AI_WASH_STAIN_CLASSIFICATION_SERVICE`, `SmartHost`, `SmartAutoMop`, `SmartAutoWash`, `StainIdentify`, and turbidity terms; `node_camera_ai.so` references that service and `ProcessWashStainClassificationRequest`. Dynamic symbol inspection still **did not execute**, because the macOS analysis utility was unavailable. That is a host tool gap, not an ELF finding.

**Engineering decision:** next inspect both libraries' ELF exports/imports offline using a real cross-platform ELF reader, and examine AVA service call sites to establish direction. Do not infer an accessible Valetudo API, active turbidity sensor, measured thresholds or automatic rewash decision from configuration flags alone. Preserve the existing `SmartAutoMop=-1` fail-closed semantics and leave the running Valetudo installation untouched. The map check remains deferred.


## Stage 7 ARM64 dynamic ELF evidence — native classification and mop dirtiness (2026-10-19)

The user's sanitized report `x40-r2416-stage7-elf-v1` successfully used `llvm-readelf` and a demangler on the saved `dreame.vacuum.r2416` SquashFS image; unlike previous stages, dynamic symbol analysis is available. The report deliberately lists **only the first 80 filtered matches per module** (matching counts: camera AI 145, Lethe 2833, map divide 223), so absence of an individual symbol from the list is **not** evidence of absence from the binary.

**Named exported functions and types observed:**

| Component | ELF evidence | Limited conclusion |
| --- | --- | --- |
| `node_camera_ai.so` | `camera_ai::CameraAINode::ProcessWashStainClassificationRequest(ava_msg_wash_stain_classification*)` | A compiled handler for the wash-stain classification request exists |
| `node_camera_ai.so` | `camera_ai::CameraAINode::Publish(const camera_ai::ImageWithClassification&)`, `ava::Publisher<ava_ai_result_with_classification_msg>` | Compiled AI result publishing implementation exists |
| `node_lethe.so` | `ancp::AvaNodeRoute::SignalClassfyProcess(ava_ai_result_with_classification_msg*)` | Compiled route handler for AI classification results exists |
| `node_lethe.so` | `ava_msg_mop_dirty_info`, `WashStatus`, `WashControlMsg`, `WashData` | Native mop-dirtiness and wash-control message/data types exist |
| `node_map_divide.so` | `std::function<void(ava_ai_result_with_classification_msg*)>`, `lds_perception::NodeMapDivide` callback types | A map component also has AI result callback support |

**Evidence boundary:** the apparent camera -> AVA classification result -> Lethe route flow is plausible but not proven. The exported types may support different consumers, and wash-stain classification via `ava_msg_wash_stain_classification` is **not necessarily identical** to visual stain detection through `ava_ai_result_with_classification_msg`. The request ABI, mop-dirty payload layout, publisher/subscriber registration and runtime feature enablement remain unknown. Do not send AVA messages or interpose native code.

Stage 7 also contains native Matter-related AVA symbols in `node_lethe.so`, but a published C++ symbol does not establish a running Matter service. Matter research remains a separate workstream.

**Focused next steps (offline only):** enumerate the *untruncated* dynamic symbols using `llvm-nm -D --defined-only --demangle`, identify exact `AvaNodeRoute` and `AsyncDeque` wash/stain/turbidity callbacks, and inspect the specific publisher/subscriber registrations and argument use with Ghidra if appropriate. Favor a read-only existing MIOT/status observation over any custom AVA instrumentation. Keep working Valetudo 2026.10.0 unchanged and experimental CleanGenius PR as draft.


## Stage 8 R2416 targeted ELF symbols — distinct stain paths (2026-10-19)

The user's offline report `x40-r2416-stage8-native-symbols-v1` scanned **all dynamic symbols** with `llvm-nm` (camera AI: 1,583 defined, Lethe: 15,906 defined, map divide: 3,852 defined), then filtered for function names. Some grouped output lists remain truncated, but the following named symbols are explicitly present:

1. **Wash-stain service request path (likely Lethe -> Camera AI):** `node_lethe.so` defines `ancp::AsyncDeque::_ProcessPub<ava_msg_wash_stain_classification>(...)` and `ava::Publisher<ava_msg_wash_stain_classification>` types. `node_camera_ai.so` defines `camera_ai::CameraAINode::ProcessWashStainClassificationRequest(ava_msg_wash_stain_classification*)` and typed callback-holder functions. This is strong static evidence of matching sender/handler *capabilities*, not direct proof of published runtime messages or their payload ABI.
2. **Visual classification result path (likely Camera AI -> Lethe/map):** `node_camera_ai.so` defines `CameraAINode::Publish(ImageWithClassification const&)`, `ConvertIntoAIStainResult(...)` and `ava::Publisher<ava_ai_result_with_classification_msg>` types. `node_lethe.so` defines `ancp::AvaNodeRoute::SignalClassfyProcess(ava_ai_result_with_classification_msg*)` and `SignalClassfyProcessSUB(AvaAIResultWithClassificationMsgSafe*)`. `node_map_divide.so` separately defines `NodeMapDivide::OnAIFloorMaterial(ava_ai_result_with_classification_msg*)`. These are **different** AVA message types from the wash-stain service request; do not collapse the flows.
3. **Cleaning and wash-decision implementation:** `node_lethe.so` defines `CheckSmartHostClean(std::shared_ptr<BT::Blackboard>&)`, `CloseSmartHostClean(std::shared_ptr<BT::Blackboard>&, bool)`, `ancp::AvaNodeRoute::AiMopDirtyInfoProcess(ava_msg_mop_dirty_info*)`, `AiMopDirtyInfoProcessSub(...)`, `LoadTurbidityCheckConfig(...)`, `SendAITurbidityValue()`, `publish_wash_info(WashControlMsg)`, `CleaningStainIdMsgPub()`, `FilterStain(...)`, and `FilterStainClean(...)`. This gives high-confidence native symbol entry points to examine next, but **not** their data values or decision rules.

**Important limitation:** the filtered report describes most Lethe methods as `defined` dynamic symbols, which does **not** establish how a node registers, publishes or consumes an AVA topic; actual call graph and subscription sites require standalone disassembly. `SmartAutoMop=-1` remains a device-observed sentinel/unknown state. No reason to modify the robot, inject native libraries, send synthetic messages, or enable CleanGenius yet.

**Next offline step:** disassemble *only* selected named functions and their static direct-call edges (Lethe wash/mop/turbidity/smart-host controls and Camera AI request handler), explicitly distinguish indirect calls, and map any accessible read-only MIOT status fields. Do not commit proprietary firmware, symbol dumps containing sensitive paths, model weights, camera captures or runtime credentials. Keep mapping deferred.

## Stage 9 call-site audit: false-zero parser failure and offline verification (2026-10-19)

The supplied `stage9-r2416-sanitized-callsite.json` found all 14 named functions but reported `direct_bl_count=0` and `indirect_blr_count=0` for *all* of them. **The zero-call results are invalid, not negative evidence.** We reproduced the tool defect against a user-provided `node_camera_ai.so` binary from an earlier limited firmware extraction.

**Root cause:** Stage 9 invoked `llvm-objdump --demangle --disassemble --disassemble-symbols=<mangled C++ symbol>`. With the tested LLVM 17, passing a mangled selector while enabling `--demangle` prints `failed to disassemble missing symbol` on stderr, but returns exit status **0**. Stage 9 checked only the exit status, then interpreted the header-only/empty disassembly as zero calls.

A corrected **offline-only** call-site parser removes `--demangle` when using the mangled symbol selector, checks stderr for missing-symbol warnings, requires a matching function header and real ARM64 instruction lines before counting, and reports analysis failures explicitly instead of `0`. Its synthetic test passed.

**Grounded positive confirmation:** running the corrected parser directly against the separately supplied `node_camera_ai.so` file decoded 2,468 ARM64 instructions inside `camera_ai::CameraAINode::ProcessWashStainClassificationRequest(ava_msg_wash_stain_classification*)`. It found 233 direct `bl` call instructions and 29 indirect `blr` call instructions, including **direct calls to all three** named `camera_ai::StainClassificationJob` logistic regression functions: `Dreame202404(float,float,float,float,float)`, `Maibo202502Series40(float,float)`, and `Maibo202502Series50(float,float)`. Raw instructions, offsets and firmware binaries were **not** added to Git.

This verifies that the *compiled camera handler* calls the three classifiers. It does **not** show that `node_lethe.so` publishes actual runtime requests, identify the message ABI or meaning of model input/output, or prove that CleanGenius is active. Do not send AVA messages or enable `SmartHost` from this finding. The corrected audit has not yet been run on the user's locally saved **Lethe** binary, because that binary was not part of the prior limited ZIP; the script must be run privately against the saved `rootfs.img` on the Mac.

Status: working robot Valetudo 2026.10.0 unchanged; experimental PR remains draft; map investigation deferred.

## R2416 Stage 9b — validated call counts, and nearest-symbol label correction (2026-10-19)

The user-supplied `stage9b-r2416-sanitized-callsite.json` correctly disassembles selected ARM64 functions after resolving the Stage 9 LLVM demangle-selector defect. Highlights:

- `camera_ai::CameraAINode::ProcessWashStainClassificationRequest(ava_msg_wash_stain_classification*)`: **2,468 decoded instructions**, 233 direct `bl` and 29 indirect `blr` calls. The binary includes actual **PLT calls** to all three `StainClassificationJob::ClassifyStainByLogisticRegression*` implementations (Dreame202404, Maibo202502Series40, Maibo202502Series50).
- `ancp::AvaNodeRoute::AiMopDirtyInfoProcess(ava_msg_mop_dirty_info*)`: 5 direct / 6 indirect branches in 96 instructions; Stage 9b prints a candidate `MultAsyncSubscribe<ava_msg_mop_dirty_info,...>` call label.
- `ancp::AvaNodeRoute::SignalClassfyProcess(ava_ai_result_with_classification_msg*)`: 32 direct / 9 indirect branches; prints a candidate classification subscriber helper.
- `ancp::AvaNodeRoute::SendAITurbidityValue()`: 125 direct / 40 indirect branches in 1,300 instructions; prints a candidate `WashStatus` cast. `CheckSmartHostClean` has 68 instructions and `CloseSmartHostClean` has 732.
- None of these compiled paths prove that the live X40 executes them, or reveal AVA payload layouts.

### Critical Stage 9b caveat: objdump's nearest-symbol annotations are not function-entry calls

Independent validation using the previously supplied **offline** `node_camera_ai.so` showed that Stage 9b's `CameraAINode::Publish(ImageWithClassification const&)` seemingly calling `ProcessWashStainClassificationRequest` is **NOT established**. The actual ARM64 branch resolves to the *annotated* label `ProcessWashStainClassificationRequest+0x3e0`, but the ELF dynamic symbol declares a function size of only `0xec`. The target is **outside that function's declared extent**, so the disassembler is attributing code to the nearest exported symbol rather than naming the true target function.

The Stage 9b report's label renderer stripped `+0x...` before exporting matches. Therefore **all Stage 9b named callee labels must be considered candidates until the numeric destination matches the exact symbol entry or its `@plt` stub**. The instruction counts are not invalidated, and the three classifier PLT calls from the wash-stain handler were independently confirmed.

A corrected private **Stage 10 offline inbound-call analysis** now validates target address and ELF function size, distinguishes `exact_entry`, `plt_entry`, `interior_within_function_not_entry`, `nearest_symbol_label_outside_extent`, and `address_mismatch_unverified`, and enumerates callers of the selected functions from streaming ARM64 `.text` disassembly. It passed synthetic unit tests and was validated against the supplied `node_camera_ai.so`. In that camera binary it found:

- one valid PLT call from the wash-stain handler to **each of the three classifiers**;
- one valid PLT call to `ConvertIntoAIStainResult` from `CameraAINode::Publish(ImageWithObjects const&)`;
- valid PLT call sites for `Publish(ImageWithClassification const&)` in `camera_ai::Running::Dispatch()` and `camera_ai::Paused::Dispatch()`;
- multiple disassembler `ProcessWashStainClassificationRequest+offset` labels **outside the symbol's size**; they must not be treated as calls to that handler.

The Stage 10 collector has **not yet** been run against the full user-local `node_lethe.so` because that proprietary binary was not in the limited shared archive. Await its sanitized JSON output before asserting Lethe call-site direction. Do not send AVA messages, patch native libraries, change MIOT 4:50, or enable experimental `SmartHost`. Keep the working Valetudo 2026.10.0 and defer mapping as requested.


## One-shot R2416 private firmware archive — completed native analysis (2026-10-19)

The user supplied a single screened offline archive containing **34 native ELF/executables** and **18 sanitized configuration records**. ZIP integrity passed, and **34/34** native SHA-256 and byte-length values matched the collector manifest. The archive's signature scanner found zero recognizable credential patterns; this **does not guarantee** an opaque binary has no secret, so the archive and binaries must remain private. No raw configuration files, binaries, weights, disassembly, images, credentials or personal maps have been committed to this repo.

**New static evidence from the broader module sweep:**

- `node_signal.so` and `node_lethe.so` both contain the AVA topic literal **`AI_MOP_DIRTY_INFO`**. `node_signal.so` defines `ava::Publisher<ava_msg_mop_dirty_info>::publishWithLine(...)`, and `AvaNodeSignal::PubMsgThroughFilter(...)` contains a **direct PLT call** to the typed mop-dirty publisher. Lethe defines `AvaNodeRoute::AiMopDirtyInfoProcess(...)` and `AiMopDirtyInfoProcessSub(...)`. This provides strong compiled sender/consumer evidence, **not** proof of a live pub/sub exchange or a stable public API.
- `AvaNodeSignal::ComProcess(AvaComMsg*)` in `node_signal.so` contains direct PLT calls to `ProcessTurbidity(unsigned char*)` and `SignalTransWashInfoPac(unsigned char*)`. The signal library also defines `ProcessWifiStationTurbidity(...)`, `ProcessWifiStationWashStatus(...)`. This identifies a compiled packet-processing side of the turbidity/wash-state pipeline; it does not verify real sensor measurements.
- The whole-module Lethe call scan confirms `AvaNodeRoute::UpdateOutput()` makes direct PLT calls to **both** `SendAITurbidityValue()` and `SendMopStainCheckCmd()`. Stage 10 also independently confirmed a constructor -> `LoadTurbidityCheckConfig()` link.
- Offline read-only ARM64 inspection of `CheckSmartHostClean(...)` resolves its BehaviorTree blackboard key to **`smart_hosting_switch`**; the function reads an integer and checks `>0`. This is a compiled CleanGenius guard, not evidence that the native switch is active.
- `ancp::AIControl::CheckAIHeavyStainSwitch()` has directly encoded callers `AiHeavyStainCopyAfterWash()` and `GetStainSegId(...)`. Heavy-stain/post-wash integration is therefore a legitimate static research target, but the precise decision logic is not yet decoded or runtime-tested.
- Stage 10's validated PLT xrefs remain relevant: 18 calls to `CheckSmartHostClean` and 15 to `CloseSmartHostClean` from MIOT property, voice, work-mode and Matter cleaning-mode handlers. Camera AI's wash-stain handler has PLT calls to the three named logistic classifiers. These are **compiled call sites**, not observed events.
- The R2416 `camera_ai` stain model is explicitly configured; `turbidity_check_config` is Boolean `true`. Saved R2416 water-management flag values include `"true"`, but the **`RUNTIME_TURBIDITY_DETECTION` literal is still redacted/unknown** and no live measurement was supplied.

**Architecture hypothesis:** MCU/dock wash data -> Signal typed `AI_MOP_DIRTY_INFO` publisher -> Lethe mop-dirtiness handlers and wash policy; Lethe can separately publish wash-stain classification requests to Camera AI, whose handler calls three logistic classifiers. The independent visual AI result path must not be conflated with the wash-stain request path.

**Product boundary:** MIOT 4:50 can provide read-only *settings* (`SmartHost`, `SmartAutoMop`, `SmartAutoWash`, etc.), **not** proof of dirtiness observations. Keep the deployed upstream Valetudo intact and the experimental research branch unmerged/unenabled. Preserve `SmartAutoMop=-1` as unknown. A private AVA message is **not** an externally supported interface: do not inject libraries, fabricate packets, alter robot firmware or collect camera frames. Further collection is not needed for ordinary ELF/symbol audits; implementation needs a verified safe read-only status interface and eventually live runtime validation when the user elects to do so.


## First implementation: X40 cached read-only CleanGenius status API (2026-10-19)

**Status: committed to draft research branch, not built or deployed on the robot.** This avoids the experimental writable quirks entirely and makes **no change** to the existing upstream default rule that disables positive `SmartHost` values on a regular Gen4 state poll.

- **GET** `/api/v2/robot/clean-genius/status` on the X40 Ultra. Other robot implementations return HTTP `404`. There are **no POST/PUT/PATCH or setter methods** for this resource.
- The X40 driver caches a strict allowlist from its **existing**, periodic MIOT `4:50` poll; this implementation adds **zero extra device requests** and does **not** send native AVA traffic. It discards the vendor blob after parsing.
- Returned JSON contains `source=miot_4_50`, `readOnly=true`, `dataType=native_settings_not_sensor_measurements`, `state` (observed/stale/unavailable), `observedAt`, `ageMs`, `stale`, `valetudoPolicy`, five interpreted settings, and `nativeMopDirtiness=unavailable_no_verified_local_status_interface`.
- Settings are only `cleanGenius` (SmartHost), `autoReclean` (SmartAutoMop), `autoRewash` (SmartAutoWash), `stainIdentification` (StainIdentify) and `hotWash` (HotWash). Each setting has `value` (signed integer or null) and `state`. Values 1/2 for the multi-mode keys are intentionally exposed as `mode_1_unverified` / `mode_2_unverified` rather than claiming verified X40 behavior. The observed `SmartAutoMop=-1` yields `{value:-1,state:"unknown"}`, **never** `off`.
- No observation is `unavailable`; observations older than 120 seconds are `stale`. Malformed/missing/duplicate allowlisted keys do not fabricate a valid result, and arbitrary string values, keys, robot IDs, firmware paths and private config are never reflected.
- The `valetudoPolicy` explicitly distinguishes `auto_disable_smart_host_when_positive` (normal/default Valetudo) and `experimental_controls_opted_in`. An observed `SmartHost=1` during normal operation may be transient, because **generic Dreame state handling asynchronously writes SmartHost=0**. The API must not label an observed setting as the actual effective cleaning mode.
- `node_signal.so`, `node_lethe.so` and `node_camera_ai.so` evidence remains documentation-only. **No native mop dirtiness, rewash decisions, raw water turbidity readings or visual classifications are claimed to be exposed.**

Tests added in `backend/test/lib/robots/dreame/DreameX40CleanGeniusReadOnlyStatus_test.js` for observed X40 `-1` sentinel, invalid payloads, unknown/missing keys, redaction and stale status. Core pure-module checks passed in the tool harness; the full Valetudo backend test suite and integration on an actual X40 have **not** been run. No runtime deployment, public firmware upload or proprietary code commits.

## Frontend read-only CleanGenius status page (2026-10-19)

An X40-only frontend page has been committed to the draft research branch:

- **UI:** `Robot Options → Misc → CleanGenius Status`, route `/options/robot/clean-genius`. The menu link is shown **only** if `/api/v2/robot` reports implementation `DreameX40UltraValetudoRobot`. Opening the route directly on an unsupported robot renders a non-actionable message and does not query the endpoint.
- **GET-only client:** typed request to `/api/v2/robot/clean-genius/status`. A TanStack Query hook is enabled only on the X40 and refreshes the **backend cache** every 15 seconds. This does not trigger more MIOT requests. A manual refresh button only refreshes the cached GET.
- **Read-only display:** SmartHost, SmartAutoMop, SmartAutoWash, StainIdentify and HotWash settings with their original allowlisted signed integer values and explanatory labels. Unknown sentinels like `SmartAutoMop=-1` appear as **Unknown (raw -1)**; numeric modes 1/2 are **unverified**, not interpreted as confirmed X40 behavior.
- **Freshness:** UI explicitly warns about stale or unavailable observations; network failure suppresses potentially outdated values. Notes normal Valetudo's automatic `SmartHost=0` policy, the effect of experimental opt-in and the distinction between native settings and live dirtiness/rewash events.
- **Safety:** no toggle/select/command UI, no PUT/POST, no AVA subscriptions, no pump/camera/cleaning interactions, no new raw settings or credentials exposed. The unmerged experimental writable quirks remain separately opt-in and are **not** rendered on the status page.

Frontend build dependencies were not installed in the analysis environment; therefore a full `npm run ts-check` or bundled frontend build has **not** run. The code was checked against the actual repository's type, React-query, router and MUI conventions; static integration assertions passed. Before shipping to the robot, run `npm --prefix frontend run ts-check` and `npm --prefix frontend run build` in a working repo clone, and run backend tests. Preserve the running stock Valetudo installation until local smoke tests succeed.

**Native status limitation unchanged:** firmware static evidence strongly suggests the Signal → Lethe `AI_MOP_DIRTY_INFO` path and the wash-stain request path, but no supported read-only external API or verified message schema has been identified. Do not hook native processes or fabricate AVA messages merely to populate this UI.


## Read-only dock-wash activity observations (2026-10-19)

**Motivation:** The one-shot firmware analysis established a private Signal → Lethe `AI_MOP_DIRTY_INFO` message path, but did **not** identify a verified external, safe, read-only source for measured dirtiness or for automatic rewash decisions. Rather than hook native processes or fabricate telemetry, the X40 already polls `VACUUM_2.MOP_DOCK_STATUS` as part of its normal state update.

**Added implementation on this draft branch (not deployed):**

- `DreameX40DockWashReadOnlyStatus.js` is a pure, side-effect-free decoder and immutable transition accumulator. It maps the codes using Valetudo's existing `DreameValetudoRobot.MOP_DOCK_STATUS_MAP`: `0=idle`, `1/5/6=cleaning`, `2=drying`, `4=paused`; `3=cleaning_unverified_variant` because upstream itself comments that the proper mapping may be idle. Other signed codes are **unknown**. The words describe a *dock status code*, not actual inferred cleaning actions.
- The X40 driver captures only the allowlisted status integer from the **already existing** MIOT state polling response. **No extra MIOT requests**; no changes to native AVA services, pump/motor controls, mapping or camera. A failed status read invalidates the cached observation. Identical repeated values update freshness but **do not** create fabricated transitions; out-of-order observations fail closed.
- An in-memory maximum of **12 transitions** is retained, with timestamps, and discarded on Valetudo restart. The status snapshot is marked `observed`, `stale` (older than 120 seconds) or `unavailable`. No maps, room IDs, locations, firmware strings or credentials are held in this history.
- The existing **GET-only** `/api/v2/robot/clean-genius/status` now includes `dockWashActivity` with the marker `dock_activity_not_dirtiness_or_rewash_reason`, a current status, and bounded transition history. The X40-specific UI shows these values alongside the five CleanGenius setting observations.
- Unknown states and current unavailability are explicit. **A cleaning code, a change of code, or repeated cleaning status cannot establish mop dirtiness, turbidity, an additional wash cycle, or a decision made by CleanGenius.** The existing `nativeMopDirtiness=unavailable_no_verified_local_status_interface` remains unchanged and honest.

A dedicated Node test file covers repeated codes, up to 30 code changes, unknown states, failed inputs, staleness and the absence of incidental/raw MIOT vendor data. The pure module passed focused JavaScript checks in the analysis tool harness; no full frontend/backend build, live robot test or CI run was performed. No firmware, raw image, symbols dumps, secrets or proprietary binaries were committed.

**Next evidence needed for true native mop dirtiness:** a proven, naturally occurring read-only public MIOT status or documented, permission-safe native diagnostic interface. Such an interface was **not** established by static ELF string/symbol/call-site findings; do not deploy a private AVA subscriber just to make the UI look complete.
