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
