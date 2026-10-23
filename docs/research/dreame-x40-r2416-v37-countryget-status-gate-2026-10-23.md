# Dreame X40 R2416 — v37 pre-Loop `CountryGet` and `AlwaysSuccess` status audit

**Date:** 2026-10-23  
**Scope:** Offline-only, independent check against SHA-256-pinned original ARM64 libraries and the owner's existing v27 matching runtime tree collection. No robot access, MIOT/AVA writes, process instrumentation, firmware changes or Valetudo+ modifications.

## Why this matters

v36 identified 15 direct root attachments before the `Loop` containing the compiled `StationWash.xml` subtree. The last two, `AlwaysSuccess.xml` (slot 14) and `CountryGet.xml` (slot 15), were unresolved as potential blockers. This audit traces their registered native builder identities, the compiled child construction for `CountryGet`, and the relevant *actual* decorator/leaf tick status handling. It does **not** infer observed ticks from static instructions.

## Finding A — `AlwaysSuccess` ordinary tick returns status 2

The original `liblethe_tree.so` exports `buildAlwaysSuccess` at `0x383420`. Its generated code has exactly one direct call to `child_node_factory_instantiateTreeNode()` at `0x383474`, with the native node label `AlwaysSuccess`, followed by `nodes_push_back_child_node()` at `0x383480`. The matching base `libbehaviortree_cpp.so` exports `BT::AlwaysSuccess::tick()` at `0x63cf0`. Its two-instruction implementation returns numeric `2` directly.

**Narrow conclusion:** if this compiled leaf is created and ticked normally, it reports status 2 (success). This alone does not demonstrate that the parent actually reaches it during a live cleaning session or exclude initialization exceptions.

## Finding B — `CountryGet` is wrapped in `ForceSuccess`

The original `liblethe_tree.so` exports `buildCountryGet` at `0x232a88`. The bounded generated subtree constructor has **seven** direct node-factory instantiations (all seven callsites checked) with the following structural arrangement:

```text
ForceSuccess
  └─ SequenceStar
       ├─ SetBlackboard(key=Get_Country_Event, value="")
       ├─ RetryUntilSuccesful(num_attempts=10)
       │    └─ BlackboardContains(key=country)
       ├─ SaySomething(message="BT  -> Country:", ...)
       └─ SaySomething(message="${country}", ...)
```

The parent/child edges are based on compiled `decorator_parent_setChild`, `control_parent_addChild`, `increase_depth` and `decrease_depth` callsites, not just contiguous strings. The generated `ConstStr` table stores a **zero-length textual value** for `Get_Country_Event`; it is not evidence of a Boolean false value. The two `SaySomething` children have compilation-time message/line parameters and do not demonstrate transmission of speech or actual country values.

The exact `RetryUntilSuccesful` parameter is `num_attempts="10"`, and its child has a literal `key=country`. The base `BT::RetryNode::tick()` at `0x8b140` contains separate numeric-status branches and a completed-failure attempt counter; no runtime attempt count is known.

## Finding C — terminal failure is converted to success, but running is not

The compiled `BT::ForceSuccessDecorator::tick()` at `0x63d10`:

- Calls the child via its virtual tick entry.
- When the child reports numeric **1**, returns **1** (running).
- When the child reports numeric **2** or **3**, returns **2** (success).
- Has a separate fallback for other/invalid states; this audit does not assign them application semantics.

**Conditional conclusion:** `CountryGet` does not propagate an ordinary child failure (status 3) as a root-sequence failure; its `ForceSuccess` wrapper maps it to success. A running (status 1) `CountryGet` *can* still hold the enclosing `SequenceStarRoF` at slot 15. Whether the `country` key is present, how often the node ticks, or which status it produces on this X40 is **not observed**.

These findings narrow the plausible pre-Loop gating candidates to the earlier setup and initialization operations, especially `MapLoad`, `RobotSysInit`, `StationSysInit` and `RobotmodeInit`. No claim is made that any of these actually fails, runs continuously, or blocks `StationWash`.

## Verification contract

- The bundled v37 verifier runs the complete bundled v36 verifier first, checking five original-library SHA-256 pins, three original/runtime library byte comparisons, the configured `RobotNode` selector and the v36 pre-Loop node census.
- It then checks exported function addresses, node literals, seven direct node-factory callsites, generated parent/child helper calls, five exact `CountryGet` parameter tables, the single `AlwaysSuccess` constructor site, and instruction anchors for `AlwaysSuccess::tick`, `ForceSuccessDecorator::tick` and `RetryNode::tick`.
- The original archives passed with final marker `X40_V37_COUNTRYGET_STATUS_STATIC_PASS`.
- A deliberately modified private runtime tree archive was rejected with nonzero exit status, reporting `original/runtime differs: liblethe_tree.so`.

```bash
python3 x40_r2416_v37_countryget_gate_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Run it in the directory containing **both** `x40_r2416_v37_countryget_gate_verify.py` and `x40_r2416_v36_preloop_nodes_verify.py`. Python standard library only. It does not execute ELF code, issue network requests, access the robot or mutate files.

## Rewash evidence boundary and next audit

This is a compiled *tree-entry* finding, not a detection or actuation result. The following remain independent and unproven on the R2416: progress and statuses of preceding initialization subtrees, normal turbidity values causing `TurbidityResultFail`, an R2416-compatible producer of `special_push_clean_dish`, the effective Blackboard state required by `WashDonePrecess()`, and an actual additional physical dock wash. Do not conflate `TubidityRecleanFlag`, lowercase `turbidity_reclean_flag`, numeric `TubidityState`, `TurbidityResultFail` and `r2343_start_rewash`.

**Next:** inspect the generated `MapLoad`, `RobotSysInit`, `StationSysInit` and `RobotmodeInit` child structure and identify concrete control/status predicates offline; separately continue the R2416 special-push producer census. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No firmware or private configuration files should be committed to the public repository.