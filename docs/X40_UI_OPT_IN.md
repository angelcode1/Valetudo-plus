# X40 experimental CleanGenius UI opt-in

The X40 registers its experimental CleanGenius control when the Valetudo process
starts with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1`. The constructor makes this
decision before registering QuirksCapability. Changing a browser setting or
opening a status page does not change the process environment.

The control is at **Options → Robot → Quirks → EXPERIMENTAL CleanGenius**.
The CleanGenius Status page supplies observations; it does not register controls.

## Process policy and UI visibility

| Process environment | Effect |
| --- | --- |
| Main opt-in absent or not exactly `1` | Does not register the experimental SmartHost selector |
| `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1` | Registers the guarded SmartHost selector |
| `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` without the main opt-in | Preserves positive SmartHost observations without registering writable experimental controls |
| Main opt-in plus `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED=1` | Registers additional experimental Reclean/Rewash controls |
| Advanced controls without `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED=1` | Keeps their writes disabled |

Default behavior remains off. The main opt-in is a code-level permission to show
manual controls, not a command to select a native mode or start cleaning.
Advanced controls remain a separate scope with additional protocol checks.

If a service manager or boot script starts Valetudo without the main opt-in,
the selector is hidden after that start. A flag set for a temporary process is
not automatically saved into application configuration or inherited by the next
boot. Restoring another launch configuration can therefore hide the selector.

## Settings and displayed values

The SmartHost selector offers `off`, `routine` and `deep`, mapped to native
values 0, 1 and 2. UI availability does not prove firmware acceptance or automatic
cleaning behavior. A successful mutation requires the controller's exact native
readback. Unsupported settings remain visible as a disabled control with a
bounded raw value and a fixed reason.

Activation requires both eligible cached state and a complete fresh native
safety read. Powersave mode 14 remains blocked. Off recovery instead requires
a recognized fresh SmartHost value; it does not depend on activation eligibility.
Operations are serialized, single-key and never automatically retried. Unknown
or negative advanced values do not authorize a write.

The frontend refreshes Quirks after successful and failed mutations and keeps
the changed control pending until refresh settles. A failed command may follow
an applied native write, so its old cached display cannot prove that the setting
stayed unchanged. A later Off observation also cannot reconstruct an earlier
Routine observation; capture each required outcome at the time it occurs.

## Scope of app-style settings

The mode selector does not provide every setting offered by a vendor app.
The following table describes the X40 source implementation, not device
acceptance or a recommendation to enable additional protocol flags.

| Setting | UI and implementation | Remaining boundary |
| --- | --- | --- |
| CleanGenius Off / Routine / Deep | Guarded SmartHost selector under Options → Robot → Quirks | Main opt-in required; exact readback confirms only the requested setting |
| Auto Reclean / Auto Rewash | Additional experimental quirks | Advanced opt-in required for registration, signed opt-in for writes; unknown or negative current values remain blocked |
| Stain Identification | Read-only CleanGenius Status field | No setter is implemented |
| Mop wash temperature | Existing Options → Robot → Mop Wash Temperature control | X40's V2 capability exposes Cold, Warm, Hot and Scalding; setting it does not prove a wash occurred |
| HotWash flag | Read-only CleanGenius Status field from MIOT 4:50 | Separate from the V2 heater temperature property; it cannot establish the selected temperature |

X40 already registers
[MopDockMopWashTemperatureControlCapabilityV2](../backend/lib/robots/dreame/capabilities/DreameMopDockMopWashTemperatureControlCapabilityV2.js).
It reads and writes `HIGH_RES_MOP_DOCK_HEATER`, while the observed `HotWash`
flag is decoded by the read-only settings parser. Do not add a duplicate
temperature control by assuming these two properties are interchangeable.

**Decision:** the existing controlled UI path covers manual native mode
selection. Broader app parity remains incomplete. Exposing advanced selectors
or normalizing unsupported values would not establish their firmware semantics;
keep those writes blocked until a separately justified validation decision.
No firmware/app collection or repeat hardware trial is required to reach this
source-level scope decision.

## Source references

- [X40 constructor and registration](../backend/lib/robots/dreame/DreameX40UltraValetudoRobot.js)
- [Opt-ins, single-key setter and readback](../backend/lib/robots/dreame/DreameX40CleanGeniusResearch.js)
- [Fresh activation and settings readers](../backend/lib/robots/dreame/DreameX40CleanGeniusPreflight.js)
- [Quirks mutation refresh](../frontend/src/api/hooks.ts)
- [Quirks menu route](../frontend/src/options/RobotOptionsRouter.tsx)

## Optional guarded launcher

[util/x40/ui-launch.sh](../util/x40/ui-launch.sh) provides a generic launch-time
selection policy. It does not install itself, edit a boot script, send native
messages, select a cleaning mode or start a cleaning task. Its caller supplies
an original launch environment, a private state directory, the original binary,
both binary hashes and a release identifier:

```text
sh ui-launch.sh launch STATE_DIR ORIGINAL_BINARY CANDIDATE_SHA ORIGINAL_SHA RELEASE_ID
```

The state directory must contain a matching `release` marker. A matching
`enabled` marker permits candidate selection; `rollback` always selects the
original. Candidate files are `valetudo`, `config.json` and `data` inside that
directory. Config/data are deployment inputs, not generated or modified by the
launcher. The candidate runs in a clean environment with the main UI opt-in,
observe-only preservation and explicit zero advanced/signed/test flags. Fallback
uses the original config/data environment with the main opt-in disabled.

Without a matching `accepted` marker, the candidate gets one boot attempt. A
detached watchdog must report readiness before the candidate starts. At 900
seconds, absence of acceptance makes it record rollback before requesting a
normal reboot. The following boot selects the original. An additional boot
before acceptance also selects the original rather than retrying the candidate.
Acceptance never overrides rollback. After explicit acceptance, later boots can
select the candidate without the initial timed fallback.

The launcher validates binary hashes and rejects linked candidate profile
files. Invalid candidate inputs fall back to the pinned original. An invalid
original binary is not executed. Required host tools include `sha256sum`,
`nohup`, `setsid`, `sleep`, `sync` and `reboot`. Actual boot integration,
acceptance authorization, original startup backup and rollback installation
remain the caller's responsibility. Do not point an isolated test profile at a
normal service without reviewing its settings.

[Launcher tests](../backend/test/lib/utils/X40UiLauncher_test.js) execute the
shell selection logic with fake applications and fake detached-process/reboot
tools. They cover policy, hashes, fallback, single-attempt behavior and watchdog
acceptance/expiry; they do not establish device boot or SSH-detachment behavior.

This document describes public source behavior. It contains no device trial
record or deployment authorization and changes no executable code or default.
