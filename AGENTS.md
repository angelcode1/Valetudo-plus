# X40 CleanGenius: engineering contract for future work

**Repository source of truth:** `master` only. Read [Branch Consolidation and Research Preservation](docs/BRANCH_CONSOLIDATION_20261028.md) before changing X40 research. All 90 other branch refs have been removed after preservation of their historical commit tips. Do not recreate numbered version branches or duplicate the research archive.

**Current handoff (2026-10-28):** [X40 CleanGenius implementation handoff](docs/X40_CLEANGENIUS_HANDOFF_20261028.md). Read it before proposing new work. **Two bounded candidate trials already happened**: `ccaa64d` displayed the experimental quirk but its mode change was blocked by the idle guard; `20377ec` displayed unavailable cached MIOT readings. The original Valetudo is confirmed restored after the second trial (`STATE=ORIGINAL ORIGINAL_PID=1752`, `WATCHDOG=NOT_RUNNING`). No `SmartHost=1` acceptance or automated cleaning behaviour was demonstrated. **Do not repeat the hardware trials by default.**

**This file is a binding project instruction, not an optional research suggestion.**
The owner has repeatedly asked for an actually working X40 CleanGenius feature and has explicitly objected to the same firmware-decoding rabbit hole occurring four times. Do not waste their time by repeating it.

## Goal, in order

1. Expose a **controlled, testable opt-in path** for the firmware's existing native CleanGenius mode on X40 R2416.
2. Verify on a supervised device that an explicit mode selection is accepted, persists on readback, does not interfere with essential normal controls, and can be reversed.
3. Only if evidence supports it, confirm automatic stain-triggered re-clean and mop rewash **as separate outcomes**. A setting update, Blackboard write, or CleanList mutation does not establish these outcomes.

## Mandatory stop rules

- **No v291 or any more successive incremental offline ELF-instruction analysers.** Freeze the v249–v290 static reverse-engineering trail. Do not propose “just one more register / relocation / callsite” as progress toward enabling the feature.
- Every new task must produce one of: executable Valetudo+ code, automated tests of that code, a reproducible *bounded* supervised verification/rollback procedure, or a clear go/no-go decision. No analysis-only work without a named decision it will settle.
- Reuse existing implementation before writing new code: `DreameX40CleanGeniusResearch.js`, X40 `QuirksCapability`, the read-only MIOT 4:50 snapshot, and Gen2 `allowExperimentalCleanGenius` bypass.
- Maximum **one** bounded test of a hypothesis before deciding implement / reject / park. If evidence is missing, mark the feature blocked; do not ask the owner to run another chain of collector kits.
- Report clearly what works in automated fake-helper tests, what still needs supervised robot verification, and what is not implemented. Never claim a second physical pass or dock rewash from static evidence.
- Do not automatically deploy, restart, root, patch, flash, send native AVA messages, or alter the user's robot. Do not touch `master` or the original working Valetudo installation without explicit user approval.
- Keep default policy: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`; observed `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`; no coercion of unknown/sentinel values, no bulk MIOT 4:50 writes. Respect existing mode/task idle guards.
- Restore the stock Gen2 auto-disable policy by removing the opt-in environment variable and restarting Valetudo in any rollback plan. **Do not imply this replaces a physical emergency stop or guarantees device state.**
- Keep private firmware libraries, binary dumps, credentials, maps, and camera images out of Git.

## Known implementation status at 2026-10-28

- The feature branch based on `research/x40-cleangenius-v229-sensor-retention-20261027` already contains three opt-in X40 quirks for `SmartHost`, `SmartAutoMop`, and `SmartAutoWash`. The normal Gen2 parser intentionally writes `SmartHost=0` unless the X40 opt-in bypass is active.
- `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `StainIdentify=1` were observed in a prior read-only X40 MIOT 4:50 response. The auto-reclean sentinel `-1` is unsupported by the existing setter; **never use this as evidence to turn it on**.
- v290 establishes neither production scheduler enqueue, physical second floor pass, nor dock rewash. No X40 hardware activation was performed in this work.
- The guarded **single-key SmartHost manual opt-in**, fresh idle check, verified readback, separate advanced-control gating, and explicit config-path compatibility are implemented and were CI-tested at `ccaa64d`. The experimental quirk appeared on a supervised robot, but no SmartHost activation was accepted. A later read-only `20377ec` trial produced unavailable cached observations; original recovery was confirmed. Subsequent source-only work must distinguish normal polling lifecycle from missing/invalid observations without weakening write safeguards, and receive CI verification before any deployment decision. Do not install older staged `99c984c` build.

## Acceptance criteria for next change

- A code change + regression tests that keeps default-off, requires intentional opt-in and confirmed idle state, writes at most one requested MIOT 4:50 key, performs strict post-write readback, and explicitly reports mismatch/unknown instead of claiming success.
- A brief controlled verification and rollback checklist; no more iterative offline kit requests unless the owner specifically requests one.
- Clear label: **code complete / fake-helper tested / hardware unverified** until the owner supplies a hardware result.
