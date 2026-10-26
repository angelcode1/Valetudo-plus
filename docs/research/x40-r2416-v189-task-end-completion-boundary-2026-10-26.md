# Dreame X40 R2416 v189 — extra-clean "end" transition and task-completion guard

**26 October 2026 · Offline, read-only AArch64 evidence.** Original private native `liblethe_route_nodes.so` SHA-256: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. No robot connection, firmware modification, cleaning action or repository runtime patch was made.

## 1. End-of-extra-clean input branch

Inside `subregion::SetExtraCleanArea::tick()`:
- `0xad9fb8`–`0xad9fbc`: `ADRP+ADD` forms the exact string `"end"` at `.rodata` VA `0xfe3f88`.
- `0xad9fc0`: direct call to `std::string::compare(char const*)` PLT `0x44bbc0`.
- `0xad9fc4`: `CBNZ w0` sends a *nonmatching* input back to `0xad837c`.
- `0xad9fcc`: obtains `BT::TreeNode::blackboard()`.
- `0xad9fd0`: matching branch directly invokes `SetExtraCleanArea::EndExtraCleanArea` via PLT `0x4435b0`.
- `0xad9fd4`: branches back into the containing behavior-tree state logic.

Inside `EndExtraCleanArea()`, independently established in v184 and rechecked in v189:
- `0xad4964`: `Blackboard::get<bool>(is_extra_clean_area)`.
- `0xad4970` and `0xad4978`: successful lookup and value guard.
- `0xad49a8`, `0xad49b8`, `0xad49bc`: conditionally stage and write `need_extra_clean=true` through `Blackboard::set<bool>`.

The complete direct `BL` census in this ELF gives **two callers of the EndExtraCleanArea PLT**: `types::ResetPlanningCleanTaskBB` at `0x5d2ec4` and the new `"end"` branch at `0xad9fd0`. The counterintuitive *true* update does **not** prove a new cleaning task is scheduled; its later interpretation remains unknown.

## 2. A "task complete" helper is actually keyed to a high-level-break flag

`switch_mode::CleanedAreaCheckTool::IsCleanTaskComplete()` builds the literal `auto_mode_break_by_high_level_event_flag` (VA `0x100c5f0`) at `0xb606e0`–`0xb606e4`. Its compiled paths include `EOR w19,w19,#1` at `0xb607f8` and `0xb60890` to invert the retrieved value, together with explicit context-dependent 0/1 fallback returns. This is a predicate used by area processing—not proof of a task-start or task-end event on the robot.

Three direct callers of its PLT `0x4468b0` (GOT `0x1242cd8`) are:
- `GetAreaEdgesAndDoAnalyse()` at `0xb6c60c`, followed by `TST` at `0xb6c610` and conditional branch `0xb6c614`.
- `GetUnreachableArea()` at `0xb81e30`, followed by test/conditional comparison and branch `0xb81e34`–`0xb81e40`.
- `UpdateReuseLdsHeightMap()` at `0xb86700`, followed by bit masking at `0xb86708`.

## 3. A separate ordinary CleanList maintenance route

`CleanedAreaCheckTool::UpdateCleanAreas(blackboard, vector<int>)` (PLT `0x44e910`, GOT `0x1246d08`) has one direct caller in this ELF: `RemoveNoCleanFromList::RemoveNoCleanAreaFromList()` at `0xab2770`, following `types::CleanList::RemoveAreas` at `0xab2760`. The no-argument `UpdateCleanAreas()` PLT `0x448350` has zero direct calls in this bounded scan. No inference about indirect dispatch follows from this count.

## Decision boundary

**Established:** a string-guarded extra-clean end handler with conditional typed flag update; a high-level interruption/completion predicate read by three map-geometry functions; a distinct list-maintenance caller. PLT/GOT identities, instruction words, 6 direct call sites, and literal addresses are verified against the pinned original ELF.

**Not established:** runtime reachability of the `"end"` branch; shared live Blackboard instance; dirt-classification data causing this path; any dispatch that actually starts another vacuum/mop pass; automatic CleanGenius reclean; or the two v165 coarse-area revisit candidates being caused by AI dirt detection. The X50 UI screenshots documented in v188 are not direct R2416 configuration evidence.

## Verified offline kit

`X40-R2416-v189-sanitized-task-end-completion-boundary.zip`

SHA-256: `5e458ed0eb62ccf42dd551687178be55295e6eeadfa85c075741f06bcb5e4269`.

Contains the full, self-contained v184–v189 standard-library verifier chain and tests, sanitized results, detailed report and SHA256SUMS. **165 tests passed against the exact private route ELF**; fresh ZIP extraction without it yielded **83 pass, 40 skip**; all checksums passed. No proprietary .so or screenshot source is inside the ZIP. See the reproducibility manifest in this commit.

The GitHub-side `v189_repo_check.py` and `test_v189_repo_check.py` provide an additional stand-alone verifier for selected compiled sites and the direct-call census. They are narrower than the ZIP's full native mutation and all-previous-version tests.

**Safety:** keep working Valetudo+ v74 with `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. This is documentation and offline code, not a firmware deployment or CleanGenius enablement.
