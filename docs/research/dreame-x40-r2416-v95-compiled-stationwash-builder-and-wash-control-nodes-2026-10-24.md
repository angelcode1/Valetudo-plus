# Dreame X40 R2416 — v95 compiled StationWash builder and wash-control node inventory

**2026-10-24. Offline original-ELF research only.** No robot shell, MIOT/native writes, reboot, firmware change, XML export, vendor binary publication or disclosure of device secrets.

## New finding: an actual native StationWash tree builder is registered

The original pinned `liblethe_tree.so`, SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`, exports both `BT_RegisterNodesFromPlugin()` and `buildStationWash(const BT::BehaviorTreeFactory&, const shared_ptr<BT::Blackboard>&)`.

The native plugin associates the exact factory name **`StationWash`** with the compiled **`buildStationWash`** entry, through `BT::BehaviorTreeFactory::registerTreeBuilder()`. This is proven by matching the factory name, AArch64 ADRP+ADD, imported registration call, and GOT relocation resolving to the **specific** buildStationWash symbol. The entry calls a much larger generated station-tree construction helper.

| Original virtual address | Observed instruction/relocation |
|---|---|
| `0x562b4c` | Exported `BT_RegisterNodesFromPlugin`; length `0x4f2c` |
| `0x578590` | Exact NUL-terminated factory name `StationWash`, distinct from `StationWash.xml` |
| `0x566240–0x566244` | ADRP+ADD loads that exact factory-name literal |
| `0x56624c` | Native registration string constructor call |
| `0x566250, 0x56625c` | ADRP+LDR resolves the GOT slot `0x7b1c50` |
| `0x7b1c50` | `R_AARCH64_GLOB_DAT` for `_Z16buildStationWashRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE` |
| `0x566278` | BL `BehaviorTreeFactory::registerTreeBuilder` PLT `0x1c6930` |
| `0x358540` | Exported `buildStationWash`, length `0xc4` |
| `0x358574`, `0x358578`, `0x35857c` | Calls `init_fac`, native station-tree constructor **`0x34c898`**, then `clear_fac` |

Control: GOT `0x7b1c48` is separately linked to `buildRobotNode()`, not `buildStationWash()`. The distinction is anchored by original relocation names, not guesses about adjacent registration slots.

## Generated native layout contains wash-control node construction sites

The same original library directly prepares the names **`ControlMachineState`** (literal VA `0x574459`) and **`StartMachineCtrl_ELECT`** (literal VA `0x584e1b`) for `child_node_factory_instantiateTreeNode` (PLT `0x1c6620`):

- **21** verified `ControlMachineState` creation sites: `0x226e44`, `0x22f580`, `0x241078`, `0x25e574`, `0x25ece4`, `0x25f47c`, `0x265efc`, `0x266e50`, `0x26788c`, `0x2b4628`, `0x2b5244`, `0x2dbebc`, `0x2dcd48`, `0x2de2d8`, `0x2deddc`, `0x2df838`, `0x2dffa0`, `0x2e0cd4`, `0x2e1674`, `0x31f3cc`, `0x347768`. The instantiated-node call is 16 bytes after each reference, except `0x2e0cd4` (+20).
- **2** verified `StartMachineCtrl_ELECT` creation sites, at `0x2b5e00` and `0x323588`, both with child node factory BL at +20.

The name-reference census is bounded to direct same-register ADRP+ADD within six instruction slots of `.text`; it is not a comprehensive semantic call graph. No direct site for these two names occurs *inside* the primary native `StationWash` helper's own address interval `0x34c898–0x358540`, but that helper calls **other native helper blocks**. Thus we **cannot conclude that the instantiated station tree lacks those nodes**, nor can we say which of these named creation sites executes when station washing actually starts. Distinguish compiled builder/node availability from active-tree placement and execution.

## Implication for the absent XML

v84 proved a `SubtreeCondition` parameter `subtree_file_path=StationWash.xml` and a fresh XML file-loader call path. The operator's subsequent bounded read-only v85–v88 filesystem searches did not find the authentic XML in their searched locations. **v95 adds a separate, positive native compiled StationWash builder.** This means searching for XML cannot be our only reverse-engineering route. It does **not** prove that the native builder transparently replaces a missing file, or that it was selected on this R2416; the registry selection and runtime behaviour require separate evidence.

V93–v94 already established that `WashStationManag::ControlMachineState::tick()` can retrieve the typed `SetWashMchineControl` callback and construct a `WashMachineControl` value. V95 proves there are generated tree layouts that create nodes by this exact name, but not their runtime Blackboard scope. The `WASH_CONTROL` receiver and physical actuation are still not identified.

Crucially, the **`TurbidityResultFail` / `special_push_clean_dish` / `r2343_start_rewash`** chain has not been connected to a **second physical mop wash**. `r2343_start_rewash` may feed `wash_times` bookkeeping without causing station wash commands. Do not report the feature as operational.

## Private reproduction and verified results

A sanitized, user-delivered package named `X40-R2416-v95-sanitized-native-tree-builder-20261024.zip` contains the standalone **Python 3 stdlib-only** verifier `x40_r2416_v95_native_stationwash_builder_verify.py`, detailed analysis and README, **without** original vendor binaries, XML, credentials, maps or device IDs. Original SHA-256-pinned v62 ZIP is required privately.

```sh
python3 x40_r2416_v95_native_stationwash_builder_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V95_PINNED_TREE_PLUGIN_STATIONWASH_REGISTERED_BUILDER_PASS
X40_V95_STATIONWASH_COMPILED_BUILDER_HELPER_STATIC_PASS
X40_V95_COMPILED_CONTROLMACHINESTATE_INSTANTIATIONS_PASS count=21
X40_V95_COMPILED_STARTMACHINECTRL_ELECT_INSTANTIATIONS_PASS count=2
X40_V95_DIRECT_SITE_CENSUS_NOT_ACTIVE_TREE_EXECUTION_PASS
X40_V95_INDEPENDENT_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=27
LIMIT: registered compiled builders and nodes do not prove active StationWash selection, shared runtime Blackboard, WASH_CONTROL delivery, or extra physical wash
```

The baseline checks exact original symbols, source hash, GOT relocations, branch targets, and all 23 compiled name/reference/child factory call sites. The 27 mutation checks deliberately alter one instruction or literal each, and detect those changes by exact anchor comparison (rather than rerunning the full `.text` reference census after each mutation).

Sanitized archive SHA-256: `97e761c6d4f8b6c982dfc77e0a65c78fa479c15d5d34f77d2b4e6f542baaafdc`. Verifier SHA-256: `d5e42fdf0b1681dff31d204b27929ad66df616d5d98c4beb18f5e7bcf215c2e2`.

## Next targeted tasks

1. Trace actual tree-plugin registration and `SubtreeCondition` factory resolution for `StationWash` vs `StationWash.xml`.
2. Reconstruct native-helper reachability from `buildStationWash → 0x34c898` into the identified wash-control node instantiation sites, preserving cache and conditional branch boundaries.
3. Independently verify a genuine turbidity failure → `special_push_clean_dish` eligibility → `r2343_start_rewash` → `WashControlMsg` → physical *additional* mop wash. No guessed command payloads, forced contamination, or native switch writes.

**Robot untouched:** last user-verified stable Valetudo+ v74; native `SmartHost=0`, experimental `writeGateOpen=false`, launcher restored, native baseline and v70/v73/parent/original recovery artifacts preserved. No reboot, MIOT setting write or install is required.
