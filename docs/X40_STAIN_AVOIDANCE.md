# X40 stain handling: separate reference protocol

Status: **code complete / fake-helper and UI/API tested / hardware unverified**.
This source change does not authorize a deployment, process restart, native
write, new firmware collection or change to the guarded launcher.

## The missing distinction

The native key `StainIdentify` was displayed as a boolean identification setting,
with value 1 labelled On. The reference integration instead associates that key
with **stain avoidance**, and uses 1 for disabled and 2 for enabled. Treating 1
as identification On can misrepresent the user's setting and suggests an
incorrect 0/1 setter.

Evidence is pinned to `Tasshack/dreame-vacuum` commit
`f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585`:

- [types.py](https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/dreame/types.py)
  maps STAIN_AVOIDANCE to StainIdentify and checks AI fluid detection for availability.
- [switch.py](https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/switch.py)
  writes 2 for enabled and 1 for disabled; the entity additionally requires the
  fluid-detection capability.

This is primary source evidence for that integration's protocol. It does not
establish the X40's model feature gate, current AI fluid-detection configuration,
firmware acceptance, obstacle behavior, stain detection or automatic reclean.
No private robot file is needed to reproduce the source comparison.

## Implementation

- Keep the API field name `stainIdentification` for compatibility, but report
  raw 1/2 as mode_1_unverified/mode_2_unverified. Zero, negative and other values
  are unknown. The status page now says Stain handling setting and explains the
  reference mapping without calling either value a verified detection state.
- Register **EXPERIMENTAL Stain Avoidance** only when the main CleanGenius opt-in
  and `VALETUDO_X40_EXPERIMENTAL_STAIN_AVOIDANCE` are both exactly `1`.
  Main, advanced and signed flags alone never register it. The new flag is absent
  from the clean environment supplied by the generic UI launcher.
- Offer `disabled` / `enabled`, mapped to 1/2. Require a current recognized 1/2
  value, eligible cached state and the existing complete fresh idle/charging/
  clear-error/idle-dock read for either direction. Disabling avoidance does not
  use the SmartHost Off recovery exception.
- Reuse the existing controller and its shared write lock. Write only the
  requested StainIdentify key in MIOT 4:50, verify exact readback, and never retry
  or issue a blind rollback write. Reclean/Rewash signed transforms do not apply
  to this setting. No main mode, temperature, map or auto-mode setting is written.
- Unknown values and failed reads keep the control visible and disabled. The
  existing Quirks refresh behavior applies after both successful and failed
  mutations. This change does not add a polling loop.

The explicit new opt-in isolates an unverified reference protocol; it does not
replace model capability validation. Leave it absent in a normal installation.

## Reproducible code checks

From a checkout with dependencies installed, under Node.js 22:

```bash
node --test backend/test/lib/robots/dreame/DreameX40StainAvoidance_test.js \
  backend/test/lib/robots/dreame/DreameX40QuirkUiFlow_test.js
npm test --workspace=backend
npm run ts-check_all
npm run lint_all
```

The dedicated tests cover independent opt-ins, 1/2 deltas in both directions,
preservation of other settings, unsupported/current/missing values, duplicate
keys, both-direction guards, readback mismatch/failure, no retries and the lock
shared with CleanGenius. The UI/API tests execute the production mutation hook
with real Query Core observers and the capability/router/controller over loopback
HTTP with synthetic native replies. They cover applied-write/readback failure,
unavailable native/HTTP refresh, blocked writes and pending-until-refresh behavior
for both main mode and stain avoidance. They do not render a browser or operate
a robot.

## Bounded decision and rollback boundary

**GO for source review:** fix the inaccurate boolean display and retain a
separately disabled reference-protocol implementation. No new collector is
needed for this decision. Existing signed Reclean/Rewash restrictions remain.

**NO-GO for enabling this control on a robot:** no X40-specific fluid-detection
eligibility or 1/2 round-trip evidence is established by these tests. Do not edit
an accepted service environment merely because the build passes.

If a later owner-approved validation establishes those prerequisites, its one
bounded attended procedure must pin a fresh starting value, require the complete
fresh safety gate for each direction, select the other value once, capture exact
readback and unchanged other settings, then restore the starting value with
another complete gate and exact readback. No cleaning task is needed to test
setting acceptance; it would not establish avoidance behavior. On rejection,
unknown value, mismatch or unexpected state, stop and park without retries.

Removing the new opt-in and restarting via a separately reviewed deployment
recovery path hides the control; it does not itself restore the native setting.
A failed readback may follow an applied write. Any future deployment proposal
must include its verified baseline and recovery path before seeking approval.
