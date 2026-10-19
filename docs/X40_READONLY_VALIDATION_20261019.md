# X40 Ultra read-only telemetry validation — 2026-10-19

- MIOT transport failure now invalidates both cached read-only snapshots immediately and preserves the inherited poll exception.
- Clock rollback and invalid observation timestamps now fail closed rather than converting negative age into a fresh observation.
- The existing settings and dock-state parsers use only allowlisted MIOT values. There are no new robot requests, native process hooks, or firmware changes.
- Focused, dependency-free execution in a JS sandbox: 11/11 tests passed for the two pure decoder test modules. Driver polling tests with a stub of the inherited Gen2 method: 2/2 passed.
- These checks are not the full backend test suite, frontend TypeScript check, or production build. The repository's existing Node.js CI workflow covers these; GitHub currently shows zero workflow runs for this research branch.
- Keep PR #1 as draft and do not deploy until complete build/test validation and a natural read-only dock-observation smoke test succeed. No secrets, keys or proprietary firmware files belong in this repository.
