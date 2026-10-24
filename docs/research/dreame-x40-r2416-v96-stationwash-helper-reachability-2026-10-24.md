# Dreame X40 R2416 — v96 StationWash helper-call reachability

**2026-10-24. Pinned original firmware analysed offline.** No robot connection, firmware writes, native setting changes, restart, executable loading, or proprietary firmware publication.

## Main verified finding

The original AArch64 `liblethe_tree.so` contains the factory-registered native `StationWash` builder at VA `0x358540` (v95). At `0x358578`, this wrapper calls its generated station constructor `0x34c898`. **v96 proves three specific helper functions called directly by that constructor create typed wash-control nodes**, closing the construction-path reachability gap from v95.

| Root helper BL callsite | Direct helper function bounds from DWARF FDE | Native node creation site | Node | Native child-factory BL |
|---|---|---|---|---|
| `0x3583a0 → 0x31f224` | `0x31f224..0x31fa98` | `0x31f3cc` | `ControlMachineState` | `0x31f3dc → 0x1c6620` |
| `0x357e14 → 0x345bb8` | `0x345bb8..0x34c898` | `0x347768` | `ControlMachineState` | `0x347778 → 0x1c6620` |
| `0x350264 → 0x3231a8` | `0x3231a8..0x32412c` | `0x323588` | `StartMachineCtrl_ELECT` | `0x32359c → 0x1c6620` |

All three branch targets are **function starts** according to the original binary's DWARF unwind index and each node-reference site is **inside** the corresponding helper's explicit FDE range. The node names resolve to the original, pinned `ControlMachineState` (VA `0x574459`) and `StartMachineCtrl_ELECT` (VA `0x584e1b`) literals; `0x1c6620` is `child_node_factory_instantiateTreeNode`.

The full pinned `liblethe_tree.so` `.eh_frame_hdr` index contains exactly **1,071** valid FDE function bounds. The direct AArch64 `BL` graph rooted at `0x34c898` reaches **27** FDE-delimited functions. Of v95's whole-library 21 `ControlMachineState` creation sites, **2** are in that 27-function closure, and **19** outside. Of v95's two `StartMachineCtrl_ELECT` sites, **1** is in that direct closure and **1** outside. This is explicitly a **direct-call graph**; tail branches, virtual calls, callbacks and dynamically selected tree builders are not represented.

**Bounded conclusion:** the compiled native StationWash constructor really does call helpers containing both kinds of wash-control node creations. This does **not** prove the station-tree builder is selected by the running R2416, that those nodes are ticked, which branch statuses they return, what their parameters are at runtime, or whether a physical additional mop wash occurs.

## Reproduction

SHA-256 pinned original owner-private `liblethe_tree.so`:

`9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`

The separately supplied sanitized ZIP, `X40-R2416-v96-sanitized-stationwash-helpers-20261024.zip`, contains a Python-standard-library-only verifier `x40_r2416_v96_stationwash_helper_reachability_verify.py`, detailed report, and README. It does **not** contain source vendor ELF, robot settings, private XML, serials, maps, passwords or tokens. The verifier reads the owner's original evidence ZIP in memory; it pins the binary hash, exported builder symbol, builder GOT registration, all previous direct name/reference sites and factory calls. It decodes the original `.eh_frame_hdr` pcrel/datarel format and matching `.eh_frame` FDE start/range, reconstructs the direct-call graph, and checks the three explicit constructor calls and node placements. It performs **23 one-byte mutation trials**, each rerunning full verification of an altered image.

```bash
python3 x40_r2416_v96_stationwash_helper_reachability_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V96_PINNED_STATIONWASH_UNWIND_FDE_BOUNDARIES_PASS entries=1071
X40_V96_STATIONWASH_DIRECT_BL_HELPER_CLOSURE_PASS functions=27
X40_V96_STATIONWASH_REACHABLE_CONTROLMACHINESTATE_HELPERS_PASS count=2
X40_V96_STATIONWASH_REACHABLE_STARTMACHINECTRL_ELECT_HELPER_PASS count=1
X40_V96_OTHER_DIRECT_NODE_SITES_OUTSIDE_BUILDER_GRAPH_PASS control=19 elect=1
X40_V96_INDEPENDENT_ANCHOR_AND_UNWIND_MUTATIONS_REJECTED count=23
LIMIT: direct compiled constructor helper reachability is NOT dynamic factory selection, live tree tick, callback scope, rewash marker forwarding or physical washing
```

Sanitized verifier SHA-256: `0d7edaef0da7c62d50bbb59191d0b7a3a89356f7c8c9e599ea3b6ceb117cff11`; sanitized ZIP SHA-256: `6d06fbd02843de107588f1b7daf3918e4b64cf0c1ffc10a172ea83d28208a057`.

## Important remaining distinctions

- **v84/v95:** the compiled relative `subtree_file_path=StationWash.xml` and registered native `StationWash` builder are *different* observations. The live resolver's selection or fallback from the XML name to the native builder has not been proven; the authentic XML is still missing from bounded evidence.
- **v93/v94:** typed `SetWashMchineControl` callback paths, route-root `wash_machine_control` map, and `WashControlMsg` / `WASH_CONTROL` publisher are statically identified. A child node's effective Blackboard inheritance, callback presence, actual `tick()` and hardware receiver remain unobserved.
- **v67/v75–v82:** `special_push_clean_dish` has no established R2416-compatible writer, and the `r2343_start_rewash` marker-to-`wash_times` bookkeeping is not a causal proof of `WASH_CONTROL` or a physical second mop wash. Genuine turbidity-triggered rewash remains **unproven**.

**Next:** resolve native builder vs XML-file resolver selection and effective child Blackboard assignment, then trace the real wash-command receiver. Do not force dirt tests, guess station opcodes, toggle auto-switches or patch the native runtime.

**Live X40 remains untouched:** last verified Valetudo+ v74, native `SmartHost=0`, experimental `writeGateOpen=false`, original launcher restored, and v70/v73/parent/vendor rollback files intact. No device action required for v96.
