# X40 experimental Fluid Detection

Set both `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1` and
`VALETUDO_X40_EXPERIMENTAL_FLUID_DETECTION=1` in the Valetudo process environment
to register **Options → Robot → Quirks → EXPERIMENTAL Fluid Detection**.
The guarded launcher does not set the fluid opt-in. Registration sends no
write. The control offers **Disabled** and **Enabled**.

## Model and property mapping

The pinned Dreame reference integration's [device table][table] and
[capability decoder][types] list fluid detection for the following models.
The capability numbers come from decoding the literal table data without
executing the reference integration.

| Model | Reference capability | Minimum reference capability version |
| --- | --- | --- |
| `dreame.vacuum.r2416` | Fluid detection (27) | 1 |
| `dreame.vacuum.r2416a` | Fluid detection (27) | 1 |
| `dreame.vacuum.r2416c` | Fluid detection (27) | 1 |

The reference [switch][switch] requires AI obstacle detection. Its
[setter][device] changes mask `0x08` in the integer AI settings property
(MIOT 4:22). The prerequisite uses mask `0x02` in that same value.
Valetudo permits only the three listed model identifiers. This mapping
comes from reference source. Firmware write acceptance remains unverified.

## Request and readback

- Both selections require confirmed cached idle state and a single fresh batch
  containing the five native safety observations and the AI settings property.
  The response must contain every requested property exactly once with a
  successful code. The robot must be awake, idle and charging without a task,
  an error or dock activity. Obstacle detection must be enabled.
- The control changes only the fluid flag in the freshly read unsigned
  32-bit value. A selection that already matches sends no write. Otherwise
  it sends one write to 4:22 and requires exact readback of the complete
  target. The UI reports the fluid state and any fixed refusal reason.
- The operation shares the experimental X40 settings lock and the local
  AI settings lock used by camera, pet and image controls. External firmware
  writers do not share the locks. The native read and write are separate
  requests.
- The fluid operation leaves MIOT 4:50 alone. Stain Avoidance and its write
  prerequisites remain separate.

The manual X40 experimental reads and writes select the local transport
with a three-second timeout per transmission. This path refuses an invalid
timestamp and does not recover the handshake to replay the request. A lost
acknowledgement can follow an applied write. An error leaves the setting
unverified, and the UI refresh makes a separate read. Normal miIO callers
retain their retry policy.

Earlier controller-only tests verified one helper invocation. The production
transport could still resend it after a timeout. Encrypted loopback tests for
CleanGenius mode and Fluid Detection now simulate a lost acknowledgement,
count exactly one write transmission and confirm the applied value through a
separate read.

## Verification

Run with Node.js 22 from the repository root after installing dependencies
with `npm ci`.

```sh
npm run build_openapi_schema
npm run generate_code --workspace=backend
npm run ts-check_all
npm run lint_all
npm test --workspace=backend
npm run build:aarch64
```

The suite exercises the Quirks UI/API contract with a fake robot and the
production transport with a loopback peer. Live acceptance requires a
separate supervised trial.

1. Review the exact build and confirm a working recovery path to the prior
   Valetudo service and profile. Enable only the main and fluid experimental
   controls. Keep CleanGenius Off and confirm a fresh supported model,
   awake idle state, obstacle detection enabled and fluid detection disabled.
2. Select **Enabled** once and confirm a successful write with exact readback.
   While still eligible, select **Disabled** once and confirm the same checks
   and the original fluid state. Leave cleaning tasks idle throughout.
3. Stop on a refusal, unavailable observation or mismatch. Establish fresh
   state before any explicit recovery selection. If the service needs
   recovery, restore the prior launch profile. Restarting Valetudo does not
   reverse a firmware setting that was already applied.

[table]: https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/dreame/const.py
[types]: https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/dreame/types.py
[switch]: https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/switch.py
[device]: https://github.com/Tasshack/dreame-vacuum/blob/f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585/custom_components/dreame_vacuum/dreame/device.py
