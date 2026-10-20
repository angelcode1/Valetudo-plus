# X40 Stage 19 — passive native wash-status candidate

**Research branch only; not installed or validated on the robot.** Do not use this branch as a firmware or executable update.

## Evidence

The user's private offline R2416 native study found `avanodemsgcvt::MsgClean::RptStationAutoWashState` compiling a MIOT property report with **PIID 61** while its **SIID is read from the MsgClean instance**. The identity, SIID and semantics of any live MIOT property remain unverified. A separate compiled AVA `AI_MOP_DIRTY_INFO` path links Signal typed publishing to Lethe handlers; this is not a supported, externally readable interface and is distinct from PIID 61.

Device-tested MIOT `4:50` settings, including `SmartHost=0`, `SmartAutoMop=-1` (unknown), `SmartAutoWash=0`, `StainIdentify=1` and `HotWash=1` **do not demonstrate native stain measurements or rewash decisions**.

## Research-only implementation

`DreameX40PassiveWashNotificationProbe.js` accepts only incoming `properties_changed` messages and checks `piid===61` with bounded integer `siid`. It records a maximum of eight distinct SIIDs, occurrence counts capped at 65,535, and timestamps. It **does not access, store or echo the `value` field**; a test uses a `value` getter that throws if accessed. Incoming notifications are handed straight to the inherited handler after counting, preserving the original ACK and handling path. It adds no new MIOT polling, writes, subscriptions, native hooks or cloud calls.

The existing GET-only X40 `/api/v2/robot/clean-genius/status` returns an additional **`nativeWashNotificationCandidate`** field, with hardcoded `candidateIdentityVerified=false`, `semanticMeaningVerified=false`, `valuesCollected=false`, and `notDirtinessOrRewashEvidence=true`. The lack of a candidate notification is not interpreted as an absence of native firmware capability; notifications on a different service ID may be unrelated. Existing `nativeMopDirtiness` remains **unavailable**.

This is a source prototype for review; it is *not* merged into production `master` and has not been packaged or installed on the X40. No change is made to the running `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` setting, native writable experimental quirks, or SmartHost safety policy.

## Testing and next gates

Offline Node.js tests verify value redaction, bounded observations, unknown-state handling, disallowed identifiers, out-of-order timestamps and no robot command capability. The standalone module's seven tests passed locally; **the full backend test suite and deployed integration are not yet verified**. Execute from the clone:

```sh
node --test backend/test/lib/robots/dreame/DreameX40PassiveWashNotificationProbe_test.js
node --check backend/lib/robots/dreame/DreameX40UltraValetudoRobot.js
```

Before considering any deployment, complete a source review and normal CI/build validation, and separately verify a *naturally emitted* MIOT report with a trusted SIID or recover that SIID from private offline disassembly. No new device probing now: the operator deferred the supervised physical cycle.

Do **not** enable CleanGenius writes, send synthetic AVA messages, collect camera imagery or firmware logs, change rootfs, or equate `AI_MOP_DIRTY_INFO` with an externally accessible MIOT value. Proprietary firmware, map data, credentials and raw notifications must remain private.
