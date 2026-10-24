# Dreame X40 R2416 — v98 native plugin loader and shared tree factory

**2026-10-24 · Offline SHA-256-pinned firmware research. No robot-side actions.**

## Verified compiled connection

v97 proved that the original `BT::SubtreeConditionNode::onInit()` resolves `subtree_file_path=StationWash.xml` to a registered native `StationWash` builder *before* falling back to XML loading. v95–v96 separately proved that original `liblethe_tree.so` exports `BT_RegisterNodesFromPlugin`, registers `StationWash → buildStationWash`, and that the native builder's direct helper closure contains two `ControlMachineState` and one `StartMachineCtrl_ELECT` construction sites.

**v98 connects plugin discovery to the factory used by the configured root tree.** In original `node_lethe.so`, the `AvaNodeRoute` constructor obtains a directory from `Parameter::GetInstance()+0x28`, guards `opendir()`, enumerates directory entries with `readdir()`, compares the exact `.so` suffix, builds each candidate path with `ancp::GetFilePath()`, and calls `BT::BehaviorTreeFactory::registerFromPlugin()` in a loop. It then passes the **same factory object held at `[sp,#0x110]`** to `BT::buildTreeFromText()` for the configured root `RobotNode` wrapper.

The implementation of `registerFromPlugin()` in original `libbehaviortree_cpp.so` constructs a `BT::SharedLibrary`, calls `load()`, checks for the literal **`BT_RegisterNodesFromPlugin`** with `hasSymbol()`, obtains its address with `getSymbol()`, and invokes that callback on the factory (indirect `blr x20`). The missing-symbol path does **not** call that export. The specific `liblethe_tree.so` exports the matching function and places its native `StationWash` builder registration within that export's verified extent.

### Source addresses

| Native file | ELF VA | Static evidence |
|---|---|---|
| `node_lethe.so` | `0x350db4–0x350ddc` | Parameter object, configured plugin-directory string from `+0x28` |
| `node_lethe.so` | `0x350e14,0x350e1c` | `opendir()`, null-result branch |
| `node_lethe.so` | `0x350e20–0x350e50` | Exact `.so` suffix literal VA `0x9d5a78`, `strlen()`, `strcmp()`, match branch |
| `node_lethe.so` | `0x350e5c,0x350e6c,0x350e80` | `readdir()`, `closedir()`, factory constructor |
| `node_lethe.so` | `0x350ed8,0x350efc–0x350f00` | Candidate filepath and call to `registerFromPlugin()` using `[sp,#0x110]` factory |
| `node_lethe.so` | `0x355114–0x35511c,0x3552c0–0x3552c8` | Same factory and route-root Blackboard used for auxiliary and configured root-tree `buildTreeFromText()` |
| `libbehaviortree_cpp.so` | `0x5cc40,0x5cc50` | `SharedLibrary` construction and `load()` |
| `libbehaviortree_cpp.so` | `0x5cc7c,0x5ccb8,0x5ccd8` | `hasSymbol()`, `getSymbol()`, conditional registration callback `blr x20` |
| `libbehaviortree_cpp.so` | `0xaca80` | Exact `BT_RegisterNodesFromPlugin\0` symbol name |
| `liblethe_tree.so` | `0x562b4c..0x567a78` | Exported `BT_RegisterNodesFromPlugin` range, containing `StationWash` registerTreeBuilder call at `0x566278` |

The operator's earlier **read-only** v87 device output showed `liblethe_tree.so` mapped at `/tmp/lib/tree_lib/liblethe_tree.so`, root `/`, process CWD `/data`, and the same process mount namespace as SSH. The previously collected configuration specified `tree_lib_path: /tmp/lib/tree_lib//` and `behavior_tree_path: RobotNode`. This supplies a real installed-file and configuration context for the compiled path, but the actual plugin registration outcome was **not observed**.

### Verification and provenance

Pinned original source SHA-256:
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`

The user-delivered **sanitized** package `X40-R2416-v98-sanitized-plugin-factory-20261024.zip` contains `x40_r2416_v98_plugin_loader_factory_bridge_verify.py`, a detailed standalone report and README. **It contains no vendor binaries, private XML, settings, maps, or secrets.** Python 3 standard-library verifier source SHA-256: `98f6b543f765646bd18affa59f43fd97f515d721c415fd94f5d491ff0162d051`. ZIP SHA-256: `1665a3e0bc7020478741707d88dde5e17966b2a61ce1d5047897b804ce8434c3`.

Reproduce with the owner's private `X40-R2416-v62-readonly-20261023T051829Z.zip`:

```sh
python3 x40_r2416_v98_plugin_loader_factory_bridge_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V98_PINNED_TREE_PLUGIN_DIRECTORY_AND_SO_DISCOVERY_STATIC_PASS
X40_V98_ROUTE_FACTORY_REGISTERFROMPLUGIN_IN_CONSTRUCTOR_PASS
X40_V98_SHAREDLIBRARY_LOAD_SYMBOL_LOOKUP_AND_PLUGIN_INVOKE_PASS
X40_V98_SAME_REGISTERED_FACTORY_USED_FOR_ROOT_TREE_BUILD_PASS
X40_V98_NATIVE_STATIONWASH_RESOLVER_V97_REGRESSION_PASS
X40_V98_NEW_ANCHOR_MUTATIONS_REJECTED count=31
LIMIT: compiled scan/load/register then root build, not a live registry snapshot, per-node tick, or physical reclean/rewash
```

The 31 checks independently alter pinned bytes in memory and verify rejection. All original-file checks are offline; **no robot connection or settings write was made**.

## Remaining proof gates

- Native library mapping and a compiled registration loop do not establish a successful **runtime** `StationWash` factory registration, a specific `SubtreeCondition` resolution event, or child ticks.
- v93–v96 confirm a typed `SetWashMchineControl` callback and compiled wash-control node construction, but active child Blackboard scope, `WASH_CONTROL` reception and physical actuation remain unknown.
- The `special_push_clean_dish` R2416-compatible writer and real turbidity → `r2343_start_rewash` → **second physical mop-wash** causality remain unproven. Bookkeeping `wash_times` alone is insufficient.

**Next:** prefer existing passive logs or safe, minimal read-only evidence of plugin registration/StationWash selection. Do not send guessed MIOT or wash-control payloads, fake contamination signals, or force mop rewash to close a software-only research gate.

**Preserve current device:** last verified stable Valetudo+ **v74**, native `SmartHost=0`, experimental `writeGateOpen=false`, original launcher restored, and existing v70/v73/parent/vendor rollback files intact.
