# X40 settings readiness patch — 30 October 2026

Status: source implementation and fake-helper/HTTP tests; hardware unverified. This patch is based on canonical source `ef49d2e558e4c190d5c4a0f9d7e985d356d0a0f4`. It does not authorize deployment or native setting changes. The original robot installation remains untouched.

## Behavior

- Restore fresh GET `/api/v2/robot/clean-genius/native-settings` and add GET `/api/v2/robot/clean-genius/preflight`. Preserve the old GET `/clean-genius/smart-host-test/preflight` URL as an alias, with the new documented response contract. There is no corresponding POST test writer. Unsupported robots return 404, direct read failures return a fixed 502, and every response uses no-store. Neither fresh method runs normal state parsing or modifies the passive cache.
- The CleanGenius Status page has an explicit **Read fresh safety status** button. It reads mode/task/charging/error/dock once per click; it does not run on page load, change a setting, or start cleaning. Cached and fresh readings are labelled separately. A visible result cannot authorize a later write; setters repeat their own reads.
- Activation requires a cached mode 0 or 6 with task 0, then a complete successful fresh response identifying mode 0 or 6, task 0, charging 1, clear error and idle dock. Correctly identified responses may arrive in a different order. Duplicates, missing properties, unexpected IDs, errors and invalid types fail closed. Mode 14 Powersave remains blocked with an explicit diagnostic. Unknown modes, active tasks, drying and washing remain blocked. The old cached 0/0 indicator is still informational and is not the complete activation gate.
- SmartHost Off recovery uses a fresh recognized settings read, one-key write if necessary, and strict readback. It does not depend on the unrelated activation-state prerequisites. It is available only where writable controls were deliberately opted in; it is not an emergency stop or guaranteed recovery after connectivity failure.
- Preserve the installed `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` policy. This suppresses only the inherited positive-SmartHost auto-disable, without registering writable controls. With no opt-ins, the inherited default auto-disable remains unchanged. Enabling experimental controls is still a distinct explicit choice.
- Experimental quirks remain visible if the settings value is unsupported or a settings read fails. The UI disables the selector and shows the bounded raw signed number and a fixed reason. Native/transport error text is not disclosed. The observed SmartAutoMop=-1 remains **unsupported/unverified**, not coerced to Off, and cannot be used to enable a setting.
- Advanced Reclean/Rewash writes now also require `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED=1`, in addition to the existing main and advanced opt-ins. With no signed opt-in, advanced controls are read-only. For a recognized positive current mode 1 or 2, an explicit Off selection writes its negative (-1/-2) and requires that exact signed readback. This implements the maintained reference integration's wire transformation behind a separate test gate; it is not X40 hardware acceptance. Negative or unknown current values still block all advanced writes.
- Settings operations remain serialized, strictly parsed and one-key only. Duplicate known 4:50 keys fail closed. There are no automatic retries or blind rollback writes.
- The Quirks UI refreshes settings after both successful and failed commands, and keeps the changed control pending until that refresh settles. A failed write response may follow an applied native setting, so the old display must not imply the setting stayed unchanged. The original command error is still reported; no PUT or native write is retried. A failed native refresh produces the existing disabled/unavailable selector, and a failed HTTP refresh uses the existing error view rather than displaying cached controls as current. This refresh behavior applies to all Quirks controls.

## Why the signed mapping is isolated

`Tasshack/dreame-vacuum` at `f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585`, `device.py` methods `set_auto_recleaning` and `set_auto_rewashing`, writes `-current_value` when disabling a positive setting. Its UI normalizes negative readings. The X40 byte-pinned archived v81 analysis also records signed -1/-2 branches, but the owner's collected X40 readings do not prove the full disabled/remembered-mode semantics. Therefore this patch keeps negative raw values unverified and prevents using the observed -1 as permission for a write.

## Local build and tests

With Node.js 22 and the repository dependencies installed, from the source root:

```bash
npm ci
npm run build_openapi_schema
npm run generate_code --workspace=backend
npm run ts-check_all
npm run lint_all
npm test --workspace=backend
npm run build:aarch64
```

The targeted regression files are `DreameX40CleanGeniusResearch_test.js`, `DreameX40SettingsReadiness_test.js`, `DreameX40FreshRoutes_test.js` and `DreameX40QuirkUiFlow_test.js`. They cover protocol gating, signed Off transformations, unknown values, duplicate keys, no-write rejection paths, recovery, concurrency, readback mismatch/failure, real router GET/POST behavior, error redaction, actual X40 direct-reader methods and the actual inherited SmartHost policy. The UI-flow tests execute the production mutation hook body with real TanStack Query Core observers and the actual Quirks capability/router/controller over loopback HTTP, replacing only React bindings, native MIOT, transport/error notifications and schema middleware. They reproduce an applied setting followed by failed readback, native/HTTP refresh failures, blocked activation and delayed refresh after success. All five failed before the UI refresh fix. This is an offline contract test, not a browser-rendered or robot acceptance result. Full repository CI remains required before treating a candidate as CI-validated. A local passing build is not a hardware acceptance result.

After the UI refresh correction, all 170 backend tests pass under Node 22.17.1, frontend/backend type and lint checks pass (six existing backend warnings), and the complete frontend plus ARM64 Valetudo build passes. The standalone probe is unchanged by this correction; building it again does not include or test the browser UI change.

## Bounded validation / rollback boundary

1. Validate code/build first. Do not overwrite `/data/valetudo`, the original config, data directory or postboot script. Existing physical trials are already closed; no restore/reboot is requested for them.
2. A future separately approved isolated diagnostic run should keep main experimental controls off, observe-only preservation as intended for the existing installation, and both advanced flags unset. Opening the page is cache-only. One explicit fresh safety read should report mode 14 as blocked if the robot remains in Powersave; it must not wake the robot or change settings.
3. Writable acceptance is a separate decision. If later authorized, use the existing independently verified backup, isolated config/data, original boot path and detached watchdog/recovery procedure. Do not infer hardware approval from this artifact. The full fresh preflight must pass before an activation write, and exact single-key readback must confirm the requested value. Stop after a rejection, mismatch or unexpected state; no repeated blind attempts.
4. Keep the signed/advanced flags unset for an initial SmartHost-only decision. The current observed Reclean=-1 remains blocked even if signed code is opted in. No request to enable Reclean/Rewash is part of this patch.
5. Recovery-to-Off still requires a recognized fresh SmartHost value and successful verified transport. If connectivity or safety is lost, use the robot's physical controls and the independently established original-service recovery process. Restoring the original default auto-disable policy is not a substitute for physical stop.

No robot file collection, app/ADB access, new ELF instruction-analysis chain, native AVA traffic, camera capture or settings change is needed for the local tests above.
