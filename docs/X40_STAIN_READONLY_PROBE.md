# Bounded native stain-prerequisite read profile

The explicit `--readonly-x40-stain-prerequisites` argument selects a separate
fixed profile in the standalone probe: the existing fresh safety and settings
requests, followed by one read of MIOT 4:22. It permits at most three
get_properties requests. The default `--readonly-x40-probe` retains its original
two-request budget. Neither profile accepts an arbitrary property argument or
exposes a write/action API.

The added profile uses the shared stain-prerequisite reader and exports only
the reference obstacle/fluid flags, their fixed blocked reason and observation
timestamp. It never exports the complete AI settings bitmask. Identity and
transport guards, loopback-only scope, consumed-on-failure budget and 20-second
deadline are unchanged. A failed third read returns
`stain_prerequisites_unavailable`, exits 3 and cannot retry. A successful read
with absent flags or unsupported format is a blocked configuration observation,
not an activation permission or model-capability proof.

The probe performs no HTTP service startup, normal state parsing, configuration
edit, process switch, reboot, cleaning action or native setting write. A
Powersave reading can still be a valid read-only observation; it must not be
interpreted as authorization for a subsequent setting change.

The real-CLI encrypted peer tests exercise both profiles and a failed third
read. These remain synthetic firmware tests. A deployment runner must verify
the actually running service before and after, validate the executable hash,
use its own one-attempt record, and remove only its unique temporary helper.
It must not assume the original process is running when another explicitly
accepted profile has been installed. Preserve earlier attempt records.

From a checkout with dependencies installed, under Node.js 22:

```bash
node --test backend/test/lib/robots/dreame/DreameX40ReadOnlyProbe_test.js
npm run build_x40_readonly_probe --workspace=backend
```

This document describes public source behavior only. It records no owner device
identities, executable digests, private runner paths or hardware-run outcomes,
and does not itself authorize a robot connection or setting change.
