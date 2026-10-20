# X40 Stage 10 result and Stage 11 polling correction

**2026-10-20.** The official Valetudo+ 0.5.0 parent resumed successfully after maintenance: the user's post-reboot fingerprint showed `PARENT_SHA256_PASS`, `CANDIDATE_SHA256_PASS`, `RUNNING_PARENT_PATH_PASS`, `PORT_80_LISTENING`, `HTTP_STATUS=200` and `X40_STAGE9_BASELINE_FINGERPRINT_PASS`. Baseline configuration checksum `eca068eef7dfc1e1b6dd26a82aa25b7680a4586f63c892e5a29ab4805548fcb6`; preserved original config checksum `f594fc798706c538d0d2c89f4be022af6ae8905f3c78d0e06f867e843d422018`.

The supervised Stage 10 maintenance A/B also succeeded at startup: fork reached HTTP 200 at ~80 seconds and returned six `GET /api/v2/robot/clean-genius/status` HTTP 200 responses. The fork was stopped and the unchanged parent was successfully verified after reboot.

## Crucial observation: all six status samples contain no live data

The operator uploaded six 794-byte private JSON responses and a sanitized aggregate, `X40_STAGE10_READONLY_CONTRACT_V1`. All six have `state="unavailable"`, `observedAt=null`, `ageMs=null`, `stale=true`, unavailable values for all five allowlisted settings, `dockWashActivity.state="unavailable"` and zero transitions. Their `valetudoPolicy` is `auto_disable_smart_host_when_positive`, consistent with experimental controls disabled. The sanitizer's `contract_pass=true` checks **schema and safety posture only**, not whether a real observation occurred. The native dirtiness field explicitly reports unavailable.

## Root of diagnostic gap found in the call chain

* `GET /api/v2/robot/clean-genius/status` merely invokes `robot.getCleanGeniusReadOnlyStatus()`, which builds JSON from `x40CleanGeniusObservation` and `x40DockWashObservation`. It makes **no MIOT poll**.
* The Stage 10 script queried this cached endpoint, without first querying `GET /api/v2/robot/state`. Therefore it could return valid JSON with null observations indefinitely.
* `RobotRouter.js` `GET /state` invokes `robot.pollState()`; `DreameGen2ValetudoRobot.pollState()` reads its state property list and calls `parseAndUpdateState`.
* **Inheritance matters:** `DreameX40UltraValetudoRobot extends DreameGen4ValetudoRobot`. While Gen2's base poll list omits `MISC_TUNABLES`, Gen4's override **adds MIOT 4:50** specifically for the stock SmartHost safety policy. The X40 override inherits that request and **adds MOP_DOCK_STATUS**. The X40 parser already observes both returned properties, on successful valid responses.
* Thus no added code or new MIOT property is yet justified. What remains **unverified** is whether the X40 firmware will provide valid readings in the normal state response under the known-good parent-fork configuration.

## Stage 11 — corrected observational gate

A separate operator-side `x40-stage11-poll-cache.zip` has been created and its shell syntax/Python sanitizer self-test verified offline. It is **not deployed**. Before maintenance it requires the healthy official 0.5.0 parent, SHA-pinned preserved fork and original backup and unchanged launcher; it uses a disposable config, leaves the production binary/script untouched, and restores the parent via reboot. The new script explicitly requests ordinary `GET /api/v2/robot/state` before each cached status GET (six pairs). It discards raw `/state` bodies and keeps status/log files private. The Mac-side sanitizer sends out only allowlisted state labels/counts; it declares `live_data_pass` only when both settings and dock have at least one `observed` sample. Running that sanitizer against all six actual Stage 10 files produces `contract_pass=true`, `settings_observed_samples=0`, `dock_observed_samples=0`, `live_data_pass=false` (process exit status 3), as intended.

**Hardware safety:** `GET /state` triggers the existing MIOT state poll and may result in the built-in automatic `SmartHost=0` write if SmartHost is positive, or a water-hookup-test acknowledgement; therefore this is **not** strictly side-effect-free even though the diagnostic sends only GET requests. Experimental writable CleanGenius remains disabled. Run only when idle/docked and with an independent reboot/recovery path. Raw logs may contain `CloudSecret` and `LocalSecret`: never publish them.

**Release gate remains closed:** We have verified startup, endpoint HTTP and JSON shape, but **not actual CleanGenius setting observations, native stain inference, measured turbidity or automatic rewash decisions**. Do not permanently promote the fork until Stage 11 evidence and ordinary maps, dock, UI and controls are validated.

## Stage 11 actual observations (verified 2026-10-20)

The owner provided `x40-stage11-sanitized.json` plus six source JSON samples. The sanitizer output reports `X40_STAGE11_POLL_CACHE_CONTRACT_V1` with `contract_pass=true`, `live_data_pass=true`, `sample_count=6`, `settings_observed_samples=6`, `dock_observed_samples=6`. All six source samples independently agree: both caches were **observed**, fresh, with no stale readings. Values were `SmartHost=0`, `SmartAutoMop=-1` (unknown sentinel), `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`, and `MOP_DOCK_STATUS=0` (idle). Only one initial idle transition was recorded; there is no demonstrated dock wash or rewash transition. Experimental controls remained disabled. This proves cache population via the normal state polling path, not native dirtiness, stain inference, or a CleanGenius decision. The raw user-uploaded snapshots remain private and were **not** published.

**Revised engineering decision:** The Gen4/X40 poll list and parser already work for the current read-only settings. Do not add duplicate MIOT 4:50 polling or loosen sentinel decoding. Investigate the frontend's cache refresh expectations separately: its 15-second query refetches the read-only status endpoint but does not itself call the normal state poll. Before permanent fork promotion, confirm the official parent baseline is restored, verify ordinary map/robot/dock features in a supervised fork test, and retain one-command rollback and default-off experimental control policy. No executable production code was changed by Stage 11.
