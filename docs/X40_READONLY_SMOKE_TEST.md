# X40 Ultra CleanGenius read-only smoke test

**Status:** This is a read-only candidate validation procedure for the draft research branch, **not** a recommendation to deploy experimental controls.

## Development-machine test (no X40 connection)

Run on a Mac with Python 3:

```sh
python3 x40_readonly_smoke.py --self-test
```

The packaged `x40_readonly_smoke.py` script is distributed separately as an attachment in the research conversation; it uses only stdlib, performs GET-only requests and accepts only local/private IP addresses or `*.local` hosts. No tokens, credentials, maps, raw MIOT properties or camera data are collected.

## Repository CI release gate

Existing `.github/workflows/nodejs.yml` covers `npm ci`, OpenAPI generation, code generation, frontend/backend TypeScript, lint, frontend/backend builds and Node tests using Node 22. When enabled, a **new commit** to the research branch should generate a push run; enabling workflows does not itself create historical runs. Do not call this code release-ready until the full run succeeds and the AArch64 binary can be independently verified.

## Optional developer tests without changing the robot

```sh
git clone https://github.com/angelcode1/Valetudo-plus.git
cd Valetudo-plus
git checkout feature/x40-cleangenius-research
npm ci
npm run build_openapi_schema
npm run generate_code --workspace=backend
npm run ts-check --workspace=frontend
npm run ts-check --workspace=backend
npm run lint --workspace=frontend
npm run lint --workspace=backend
npm test --workspace=backend
```

## LAN read-only observation AFTER a validated branch build is safely deployed

```sh
python3 x40_readonly_smoke.py --host 192.168.8.XX
python3 x40_readonly_smoke.py --host 192.168.8.XX --samples 12 --interval 15 --output x40-readonly-observations.json
```

Replace `192.168.8.XX` with the robot's private LAN IP. The original Valetudo 2026.10.0 will report HTTP 404 for the new endpoint until replaced with a validated build. The optional JSON contains strictly allowlisted settings and dock-state transitions; review before uploading.

**Safety:** no write tests, no synthetic AVA messages, no firmware replacement, no manipulation of `SmartHost`, no inferred turbidity or rewash cause, and do not enable `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS`. Retain the original working Valetudo binary and configuration for rollback.