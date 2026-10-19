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
