# Dreame X40 R2416 — v97 native StationWash resolver (2026-10-24)

**Scope:** SHA-256 pinned original AArch64 firmware; offline-only static verification. No live robot access, MIOT actions, original vendor ELFs, settings, maps or credentials published.

## Executive finding

The compiled `subtree_file_path=StationWash.xml` value **can resolve through the registered native `StationWash` tree builder**, without opening an XML file. The original `BT::SubtreeConditionNode::onInit()` first derives a basename from the file-shaped parameter, checks `BehaviorTreeFactory::tree_builders()`, invokes a matching builder with `TreeNode::blackboard()`, and retains a separate `BT::buildTreeFromFile()` **fallback** when no matching native builder is selected.

The native `liblethe_tree.so` `BT_RegisterNodesFromPlugin` registers **`StationWash` → `buildStationWash`** with `registerTreeBuilder`. v95 and v96 independently verified that its generated constructor reaches two `ControlMachineState` and one `StartMachineCtrl_ELECT` node factory sites.

This resolves the *compiled reason* that the user's repeated bounded v85–v88 searches found no `StationWash.xml`; **it does not prove that the running R2416 completed the plugin registration or selected/ticked that builder**. If no registered native entry exists, the original implementation does take the XML-file path. The XML is not proven globally absent.

## Original binary evidence

| Source | Pinned original SHA-256 |
|---|---|
| `liblethe_tree.so` | `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99` |
| `libbehaviortree_cpp.so` | `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` |

The original vendor ELFs are owner-private and were not committed.

| Source VA | Verified native instruction/semantic |
|---|---|
| Tree `0x30ee3c–0x30ee40` | Resolves ConstStr table `0x6f8350`, parsed as `expand_in_logger=true`, `subtree_file_path=StationWash.xml` |
| Tree `0x566240–0x566244` | `StationWash` builder name at `0x578590` |
| Tree `0x566278` | `registerTreeBuilder()`; `GLOB_DAT` at `0x7b1c50` resolves exact `buildStationWash` symbol |
| Tree `0x358578` | Compiled builder calls generated station constructor `0x34c898` |
| BT `0x75844–0x7584c` | Loads `.` and calls `std::string::find_last_of` |
| BT `0x75858–0x75870` | Loads `/` and calls `std::string::find_last_of` |
| BT `0x75894–0x758a0` | Slash/dot presence branches to basename-extraction path |
| BT `0x75dc8`, `0x75de0` | Extracted basename length and empty-key fallback guard |
| BT `0x75de8` | Looks up generated basename in native `BehaviorTreeFactory::tree_builders()` |
| BT `0x75e5c` | Missing registered builder branch |
| BT `0x75f68`, `0x75f8c–0x75f9c` | Retrieves wrapper `TreeNode::blackboard()` and invokes found native tree-builder function through `blr x3` |
| BT `0x76244 → 0x75b88`, `0x75bb0` | Missing-builder continuation calls imported `BT::buildTreeFromFile()` |

For the exact 15-byte path `StationWash.xml`, the dot is at index 11 and no slash exists, producing the 11-byte lookup key **`StationWash`**. A `reuse/` cache registration path exists separately; no cache hit is inferred.

## Repeatable regression

The separately delivered, sanitized user package `X40-R2416-v97-sanitized-native-resolver-20261024.zip` contains the tested, Python-stdlib-only `x40_r2416_v97_stationwash_native_resolver_verify.py`, full technical report and README. It consumes the private `X40-R2416-v62-readonly-20261023T051829Z.zip` as input and never executes vendor ELFs.

```bash
python3 x40_r2416_v97_stationwash_native_resolver_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V97_STATIONWASH_XML_CONSTSTR_AND_NATIVE_FACTORY_NAME_PASS
X40_V97_FILENAME_DOT_SLASH_BASENAME_EXTRACTION_PASS derived_name=StationWash
X40_V97_REGISTERED_TREE_BUILDERS_LOOKUP_BEFORE_FILE_PASS
X40_V97_NATIVE_BUILDER_BLACKBOARD_FORWARD_AND_DISPATCH_PASS
X40_V97_XML_FILE_FALLBACK_WHEN_NO_REGISTERED_BUILDER_PASS
X40_V97_NATIVE_ANCHOR_MUTATIONS_REJECTED count=44
LIMIT: code proves native builder preferred when registry contains StationWash; runtime registry state, node ticks, and physical rewash unverified
```

The 44 mutations deliberately alter distinct original instructions/literals/parameters in memory, each of which is rejected by the complete verifier. **These are offline tamper checks, not hardware test cases.** Script SHA-256 `fabc165cff0473a3a73de7401b1a9ee99d79a5d2c8c5a486529d996cf0bf0e4a`; sanitized ZIP SHA-256 `6c959981376cc215452b6570efd6faf7da3e23926db7d46c8dfd795c470e3ca2`.

## Remaining gates and next priority

1. Establish **runtime registration and selection** of the native StationWash factory, ideally through existing, passive native logs or permitted read-only instrumentation rather than changing settings.
2. Establish effective child Blackboard scope, availability and invocation of the compiled `SetWashMchineControl` callback at actual tick time.
3. Identify the receiving end of `WASH_CONTROL` / `WashControlMsg` and prove any physical dock actuation without guessing command opcodes.
4. Independently find an R2416-compatible `special_push_clean_dish` producer and demonstrate a real turbidity failure → `r2343_start_rewash` → physical **additional** mop wash, not mere `wash_times` bookkeeping.

**Preserve working Valetudo+ v74**: last operator-confirmed `SmartHost=0`, `writeGateOpen=false`, original launcher restored and v70/v73/parent/original rollback binaries intact. No robot action is required for v97.
