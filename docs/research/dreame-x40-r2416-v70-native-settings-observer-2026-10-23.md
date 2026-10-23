# X40 R2416 v70: direct MIOT observation and explicit SmartHost preservation

Research-only, 2026-10-23. Native firmware CleanGenius automatic reclean and physical turbidity-based rewash remain unverified. This commit neither enables them nor deploys to the robot.

## Confirmed software obstacle

The inherited Gen2 state parser writes MIOT 4:50 `SmartHost:0` when SmartHost is positive without a prior opt-in. An ordinary Valetudo state poll can therefore disable CleanGenius. The existing `/clean-genius/status` endpoint returns cached settings that may be stale.

## v70 implementation

- New X40-only `GET /api/v2/robot/clean-genius/native-settings` makes one direct `miotHelper.readProperty(4, 50)` request, without `pollState` or `parseAndUpdateState`. It uses the existing bounded, allowlisted settings parser; unknown values such as -1/-2 stay unknown. No raw settings, device secrets or vendor configuration are returned. Errors produce a fixed HTTP 502 response, not a firmware error dump.
- `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` explicitly opts the X40 out of **only** the inherited automatic `SmartHost:0` write. Default behavior remains unchanged. This flag does **not** set SmartHost to a positive value, reveal experimental setters, or suppress unrelated writes. Native SmartHost may interfere with other Valetudo controls, so test only with a deliberate rollback plan.
- The cached status endpoint additionally reports the observe-only policy when opted in.
- Unit tests exercise one direct 4:50 read, no parser or write method, allowlisting, unknown negative values, opt-in gate, malformed payloads, and transport error propagation. No real robot testing has occurred.

For a future test build, keeping both experimental flags unset, read:
```sh
curl -fsS http://ROBOT_IP/api/v2/robot/clean-genius/native-settings | python3 -m json.tool
```
Do not use GET `/api/v2/robot/state` as a read-only comparison: it invokes the state parser, which can write SmartHost 0. Do not activate observe-only mode or experimental CleanGenius on a production robot without a reversible test plan.

## Remaining native evidence

R2416 `node_lethe.so` has explicit, referenced `SmartAutoMop`/`SmartAutoWash` -1/-2 native messages. Their protocol meanings remain unknown. R2416's model-specific native path differs from the known direct `special_push_clean_dish` setter. The link from `r2343_start_rewash` through `wash_times` to physical dock actuation is still not established.

Startup-performance suggestions (Dreame-only build profile and precompiled OpenAPI validators) remain separate: reported mock x86 startup gains must not be taken as ARM/X40 measurements. Preserve OpenAPI validation, frozen `Object.prototype`, and full rollback coverage.

**Privacy:** no original firmware, binaries, raw YAML, maps, tokens, credentials or private device dumps are included.
