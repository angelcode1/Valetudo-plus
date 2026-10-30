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

## Source references

- [X40 constructor and registration](../backend/lib/robots/dreame/DreameX40UltraValetudoRobot.js)
- [Opt-ins, single-key setter and readback](../backend/lib/robots/dreame/DreameX40CleanGeniusResearch.js)
- [Fresh activation and settings readers](../backend/lib/robots/dreame/DreameX40CleanGeniusPreflight.js)
- [Quirks mutation refresh](../frontend/src/api/hooks.ts)
- [Quirks menu route](../frontend/src/options/RobotOptionsRouter.tsx)

This document describes public source behavior. It contains no device trial
record or deployment authorization and changes no executable code or default.
