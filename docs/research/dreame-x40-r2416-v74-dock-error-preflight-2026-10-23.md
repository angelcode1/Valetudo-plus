# R2416 X40 CleanGenius — v74 docked/drying/error interpretation

**Date:** 2026-10-23 · **Scope:** experimental source branch, no live writes or deployment.

## Verified live v73 result

The owner installed source ref `research/x40-cleangenius-v73-single-key-gate-20261023`. The read-only v73 host probe reported:

```json
{
  "activation_test_authorized": false,
  "matches_recorded_baseline": true,
  "no_write_requests_sent": true,
  "preflight": {
    "mode": 6,
    "taskStatus": 0,
    "chargeCode": 1,
    "dockWashCode": 2,
    "errorClear": false,
    "idleAndDocked": false,
    "baselineMatch": true,
    "writeGateOpen": false,
    "canTestMode1": false
  }
}
```

Native settings still `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`. The live write-gate flag is disabled.

## Source-grounded interpretation

- `DreameValetudoRobot.STATUS_MAP[6]` maps to **DOCKED**; v73 incorrectly assumed every safe idle/docked unit must have `mode=0`. The v74 mode check allows 0 (idle) or 6 (docked), but *only with* independently checked charger code 1, task 0, no reported error and idle mop dock.
- `DreameValetudoRobot.MOP_DOCK_STATUS_MAP[2]` maps to **DRYING**. It is not evidence of a second physical wash. v74 deliberately keeps **`dockWashCode=0`** a strict activation gate; active drying 2 remains blocked.
- The existing `DreameGen2ValetudoRobot` parser treats `""` and `"0"` as no error, whereas v73's stricter check missed the empty string. v74 accepts 0, `"0"` and `""` as clear and exposes a sanitized decimal or comma-separated numeric code (max 48 chars) in read-only preflight. Non-numeric/oversized payloads map to `null` with `errorCodeFormatRecognized=false`, not raw vendor data.
- Upstream Gen2 specifically interprets 68 (dock with mop attached), 114 (dock maintenance reminder) and 122 (water-hookup information) as dock/reminder conditions. **v74 does not automatically treat these as safe for a native SmartHost experiment**. Their concrete presence still blocks activation pending deliberate case-specific analysis.
- The v74 preflight remains a GET-only MIOT read of precisely six properties: mode (4:1), task (4:7), charging (3:2), error (4:18), dock activity (4:25), settings (4:50). No call to regular `pollState()` and no settings writes from preflight.

## Next operator-side read-only checkpoint

**Only after a separately verified v74 AArch64 build and reversible install:**

```sh
curl -fsS http://192.168.8.149/api/v2/robot/clean-genius/smart-host-test/preflight |
  python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ("mode","taskStatus","chargeCode","errorCode","errorCodeFormatRecognized","errorClear","dockWashCode","idleAndDocked","baselineMatch","writeGateOpen","canTestMode1")},indent=2))'
```

Do not set `VALETUDO_X40_NATIVE_SMARTHOST_TEST=1`, do not call the POST writer, and do not send a physical dock or wash command to make the gate pass. Wait for normal drying to finish. If the native error code is a reminder, study its effect first.

Successful native setting readback or mode eligibility does not demonstrate actual dirt recognition, native auto reclean or second mop wash. Those are separate later experiments with observation and physical confirmation.

Keep existing v70/v73 binary rollback copies, launcher, configuration and original binaries untouched. Nothing proprietary is committed.