# X40 R2416 v73 — dormant native SmartHost single-key test gate

**2026-10-23. Experimental source branch only. Nothing deployed.**

## Established live evidence

With installed Valetudo+ v70, the operator confirmed the *running* process environment:
- `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1`
- `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`

A fresh direct MIOT 4:50 reading agreed with the normal poll cache: `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`; both reported `observe_only_preserve_smart_host`. This proves read transport and policy configuration only. Native dirt sensing, AI reclean and physical rewash are **not demonstrated**.

## Why a separate test path

The existing opt-in `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1` exposes *three* experimental writable quirks. That is too broad for investigating only `SmartHost`, especially while `SmartAutoMop=-1` remains semantically unresolved. v73 keeps the three writers disabled.

The new component `DreameX40NativeSmartHostTest` is **off by default**, and the installed v70 has none of its routes. The v73-only opt-in flag is `VALETUDO_X40_NATIVE_SMARTHOST_TEST=1`; it is **not set or staged by this source change**.

### Read-only preflight (v73 only)

`GET /api/v2/robot/clean-genius/smart-host-test/preflight` reads the firmware properties `4:1` (mode), `4:7` (task), `3:2` (dock/charging state), `4:18` (error), `4:25` (mop dock activity) and `4:50` (native settings), with **no call** to `pollState` or `parseAndUpdateState` and no writes. It returns allowlisted values and booleans, not the raw settings payload.

For this specific R2416 baseline, enabling mode 1 refuses unless all of the following hold on a fresh preflight:

- Firmware mode `0`, task `0`, charger `1`, error `0` (integer or string), and mop-dock activity `0` (idle, no active task, docked/charging, no reported error or dock wash).
- Native settings `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`, exactly matching the operator's observed baseline.
- Observe-only suppression enabled, broad experimental writers disabled, and the **new separate v73 gate** explicitly enabled.

An unexpected, missing or malformed property is an error. A stale Valetudo cache never authorizes activation.

### Explicit single-key write (v73 only)

`POST /api/v2/robot/clean-genius/smart-host-test` requires all of:
- `X-X40-Native-Test: one-key-only` request header.
- Exact two-key JSON body `{"target":1,"confirm":"I_ACCEPT_UNVERIFIED_X40_SMARTHOST_1"}` for mode 1; `{"target":0,"confirm":"RESTORE_X40_SMARTHOST_0"}` for off.
- The separate v73 environment gate and the preserved v70 observe-only safety policy.
- A fresh preflight satisfying the mode-1 eligibility gates.

The backend then writes **only** `{"k":"SmartHost","v":1}` (or `v:0` for restore) to MIOT `4:50`, and reads back `4:50` without changing other native settings deliberately. No native AVA signals or artificial turbidity data are sent. A process-scoped busy guard refuses concurrent test requests. A readback failure means the write's outcome may be uncertain; **never automatically retry**.

A restore to `SmartHost=0` is available through the same explicit opt-in route even if the robot is no longer idle or docked, provided fresh 4:50 and the other preflight reads succeed. This improves recovery capability, but it is not a guarantee of successful rollback after lost connectivity or firmware failure. The original launcher and executable backups remain essential.

### Safety and verification gate

**Do not deploy/enable this v73 write route solely because CI passes.** Before any operator-initiated native setting test: inspect the fully successful CI, validate real-device *read-only* preflight using a separate reversible build, verify the robot is safely docked and physically accessible, retain the present original/parent/v70 backup binaries and launcher; have physical stop/return-to-dock options available.

Then request a separate, deliberate decision to send the single-key MIOT command. A positive SmartHost readback is only a settings confirmation; it does **not** prove AI features, reclean or rewash. Continue to investigate the R2416 `special_push_clean_dish` rewash eligibility gate and the native callback destination.

No vendor binaries, credentials, maps or original launcher content are committed.
