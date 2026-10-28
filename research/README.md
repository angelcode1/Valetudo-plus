# Valetudo+ consolidated research — authoritative index
**Status:** 2026-10-29 · **Research branch:** `research/consolidated` · **Code base:** `master`

> **Purpose:** one durable entry point for the complete research record. This branch was forked directly from `master` at `ef49d2e558e4c190d5c4a0f9d7e985d356d0a0f4`, after the 2026-10-28 preservation and branch cleanup. It contains the same guarded implementation and **all research documents, scripts, and reachable legacy Git history** already preserved on `master`. Only the guide/branch metadata added here are new. It does **not** activate CleanGenius or alter a robot.

## Branch and source-of-truth policy

- **`master` = canonical working code and CI/release workflows.** Do not rewrite it or sync upstream blindly.
- **`research/consolidated` = single active research branch and future sanitized findings/experiments.** New research notes belong here; do not create `research/v###`, feature-sprawl or collector branches. Promote any safe, independently tested code to `master` only after review.
- Historic documents written before this branch was created may say “master is the only active branch” or mention PR #2 or a now-deleted branch. Those statements describe **2026-10-28 history**, not the current branch layout; current navigation/decisions are governed by this file plus the unchanged safety rules of [AGENTS.md](../AGENTS.md).
- Branch naming and archive consolidation are **organizational**. Do not assume all divergent legacy experimental implementations are present as active source files; many were intentionally preserved as merge-parent ancestry instead of being reactivated.

## Preservation audit / no-stale-ref decision

| Check | Verified result |
| --- | --- |
| GitHub repository | [angelcode1/Valetudo-plus](https://github.com/angelcode1/Valetudo-plus) |
| Pre-cleanup inventory | 91 refs, including `master`; full **branch-to-SHA** list in [2026-10-28 manifest](../docs/BRANCH_CONSOLIDATION_20261028.md) |
| Prior cleanup | 90 stale branch refs deleted by [successful job 40656864797](https://github.com/angelcode1/Valetudo-plus/actions/runs/40656864797) after tip-hash and ancestry checks |
| Before this research branch | GitHub branch/heads endpoints returned exactly one live ref, `master` @ `ef49d2e` |
| Previous research recovery | 172 missing historical research documents/tools brought into the checked-out tree; legacy variants reachable through merged history |
| Current on-disk research | `docs/research/` contains many more historical reports/checkers than the 172 *recovered* items (340 file entries + 40 tool directories at its immediate top level as of 2026-10-29); **172 is not the total archive count** |
| Open pull requests | None; former draft PR [#2](https://github.com/angelcode1/Valetudo-plus/pull/2) was closed as superseded |
| Workflow files preserved | `nodejs.yml`, `manual_build.yml`, `release.yml`, `codeql-analysis.yml` |
| Code/CI checkpoint | `177aa2526a0144f584475862fe8f087012e68d75` passed [full Node.js CI 40657258670](https://github.com/angelcode1/Valetudo-plus/actions/runs/40657258670); parent `master` moved just one **documentation-only** commit to `ef49d2e` |

**No stale branches remain to delete from the pre-cleanup set.** Preserve `master` and this branch. An independent 2026-10-29 ancestry spot-check confirmed three former branch tips are exact merge bases (behind=0): `190aae591d90daa944eecce66bc0cd6fc1376829`, `661fd0184e728edc80d42d40e856c3e5f32e4dea`, and `49fa743d4bb9f54d84a2d2ea0ff0d779bd632f73`. If future stale branches appear, archive their complete tip SHAs and verify ancestry/unique files, CI and PR dependencies *before* deleting any ref; do not force-push either of these two retained branches.

## Current X40 CleanGenius verdict (highest-priority finding)

**Code guarded and CI-tested. Hardware CleanGenius activation NOT demonstrated. Do not enable or deploy from this branch.**

1. **Original X40 restored.** Following two supervised 2026-10-28 trials, the owner reported `STATE=ORIGINAL ORIGINAL_PID=1752`, `WATCHDOG=NOT_RUNNING`; the original robot installation was left unchanged by repository cleanup. This is the **last owner-confirmed** status, not continuous live monitoring.
2. **First supervised `ccaa64d` trial:** experimental Quirks selector appeared, but selecting `SmartHost=routine` was blocked by the strict native idle guard **before any MIOT write**. Read-only baseline: `SmartHost=0`, `SmartAutoMop=-1` (unknown sentinel), `SmartAutoWash=0`, `StainIdentify=1`. No successful mode transition.
3. **Second `20377ec` read-only trial:** status page lacked valid cached MIOT 4:50 and mode/task observations; this was *inconclusive*, not evidence of firmware rejection or an idle-gate error. Candidate stopped; original service restored.
4. **Subsequent source-only diagnostic fix:** normal MIOT poll lifecycle and stale/out-of-order poll protection added without introducing new MIOT calls. The status UI is *passive*; polling success alone does not imply valid values or safe idleness. The final consolidated source passed CI.
5. **Not demonstrated:** `SmartHost=1` acceptance and readback on hardware; native stain-triggered additional floor pass; planner/scheduler enqueue; automatic mop rewash; production-quality support. Native firmware reverse-engineering notes cannot substitute for these outcomes.

### Guarded implementation — preserve unchanged until separately justified

- `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` by default. Explicit `=1` only exposes the **SmartHost 0/1/2** selector; advanced `SmartAutoMop` / `SmartAutoWash` require a separate opt-in and are **not** approved for an initial hardware evaluation.
- Mutations require cached idle plus a *fresh* valid pair of MIOT `4:1 mode=0` and `4:7 taskStatus=0`, serialized single-key MIOT `4:50` change and exact post-write readback. No bulk writes, coercion of `-1`, blind retries or idle-guard bypass.
- `VALETUDO_CONFIG_PATH` must be absolute if provided; `VALETUDO_DATA_PATH` remains supported. Configuration migration can write to its chosen path, so trial configurations must be isolated and backed up.
- Never install old failed candidates (`99c984c` and the 2026-10-19 startup-regression build). CI tests compile/build contracts only; they do **not** certify a bootable/safe real-device binary.
- **Stop rule:** static-analysis iterations through v290 are archived. No v291+ collector chain, additional blind hardware trials, mode changes, reboot, flash, process replacement or original-data edits. Future work needs a specific implementation/test decision and, for any real device action, separate explicit authorization and tested rollback.

## How to find the complete findings

| Topic | Start here | Further archive |
| --- | --- | --- |
| Branch ancestry, 91 original refs and exact SHAs, 90 deletions | [Branch consolidation manifest](../docs/BRANCH_CONSOLIDATION_20261028.md) | `git log --all --graph`, and `git show <old-tip-sha>:<path>` using manifest values |
| Current experiment, CI, restoration, go/no-go | [2026-10-28 implementation handoff](../docs/X40_CLEANGENIUS_HANDOFF_20261028.md) | [Supervised runbook](../docs/X40_CLEANGENIUS_SUPERVISED_ENABLEMENT.md) (historic steps are **not** authorization to rerun) |
| Device MIOT baseline, read-only API, firmware hypotheses | [CleanGenius research](../docs/X40_CLEANGENIUS_RESEARCH.md) | [Research reports archive](../docs/research/) (historical v25-v290, distinct branches of evidence) |
| Failed executable/startup, recovery and pkg compatibility | [Runtime regression](../docs/X40_CANDIDATE_RUNTIME_REGRESSION.md) | `docs/research/` and `docs/X40_READONLY_VALIDATION_20261019.md` |
| Native stain / mop-wash behavior, turbidity, scheduler and thresholds | [Native wash status](../docs/X40_NATIVE_WASH_STATUS_PROTOCOL.md), [Turbidity state consumers](../docs/X40_TUBIDITY_STATE_CONSUMERS_R2416.md) | `docs/X40_TUBIDITY_*.md`, `docs/X40_REWASH_BUDGET_AVA_BRIDGE_R2416.md`, `docs/research/` |
| Read-only MIOT61, SIID inventories, stage9–20 | [Stage 19 MIOT61](../docs/X40_STAGE19_PASSIVE_MIOT61_RESEARCH.md), [Stage 20 audit](../docs/X40_STAGE20_OFFLINE_SIID_REPORTER_AUDIT.md) | `docs/X40_STAGE*.md` |
| Tool scripts, sanitized checkers and stage47 results | [Sanitized research tools](../scripts/research/) | `docs/research/x40-r2416-v*-tools/`, [stage47](x40/cleangenius/stage47/) |
| Latest guarded code and fake-helper tests | `backend/lib/robots/dreame/` | `backend/test/lib/robots/dreame/`, `.github/workflows/nodejs.yml` |
| General Valetudo+ fork features / upstream syncing | [Repository README](../README.md) | [2026-10-28 handoff: upstream fork-sync request](../docs/X40_CLEANGENIUS_HANDOFF_20261028.md#upstream-fork-sync-request-separate-from-this-trial) |

**Evidence classes:** `VERIFIED: repository/code/CI` ≠ `OBSERVED: user-supplied device output` ≠ `HYPOTHESIS: static analysis` ≠ `UNVERIFIED: runtime behaviour`. Retain raw observations, dates, commit IDs and explicit negative results; do not condense speculation into success claims.

## Reproducible Git audit (local read-only commands)

```sh
git fetch origin --prune
git branch -r
git merge-base --is-ancestor ef49d2e558e4c190d5c4a0f9d7e985d356d0a0f4 origin/research/consolidated
git diff --stat origin/master...origin/research/consolidated
git log --format='%h %s' --max-count=12 origin/research/consolidated
# Optional: set OLD_SHA to a captured hash from the preservation manifest
OLD_SHA=190aae591d90daa944eecce66bc0cd6fc1376829
git cat-file -t "$OLD_SHA"
git merge-base --is-ancestor "$OLD_SHA" origin/research/consolidated
```

Research commits belong on this branch; do not re-add superseded workflow files, branch proliferation, private firmware blobs, credentials, raw vacuum config, maps, cameras, or robot artifacts. Any future findings should update **this page first** with a dated decision and link to a sanitized, reproducible technical record.
