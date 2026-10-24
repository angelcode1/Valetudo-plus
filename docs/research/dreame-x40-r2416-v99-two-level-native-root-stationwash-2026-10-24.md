# Dreame X40 R2416 — v99: compiled RobotNode → StationWash two-level native builder chain

**24 October 2026 · Original SHA-256-pinned owner-private AArch64 firmware · offline only.** No robot shell, MIOT actions, native writes, restarts, firmware replacement, original vendor binaries or private settings committed.

## New evidence

v98 established the `AvaNodeRoute` plugin scan/`registerFromPlugin()` path, the exported `BT_RegisterNodesFromPlugin` callback and reuse of the same factory in configured root-tree construction. v97 showed that a `StationWash.xml` subtree can consult the `StationWash` native builder before XML-file fallback; v95–v96 proved the StationWash native builder reaches generated wash-control node constructors.

**v99 now pins the two-level native compiled graph:**

- The same original `liblethe_tree.so::BT_RegisterNodesFromPlugin` entry registers the exact `RobotNode` name to `buildRobotNode` **and** `StationWash` to `buildStationWash` via two separately typed GOT relocations and `BehaviorTreeFactory::registerTreeBuilder()` calls.
- The original, private `setting.yaml` selects `behavior_tree_path: RobotNode` and `tree_lib_path: /tmp/lib/tree_lib//`, checked as exact single entries by the offline verifier. The full private configuration is neither printed nor published.
- `buildRobotNode()` makes a direct AArch64 BL call into generated native helper `0x30d8c0`. Inside its original unwind-function boundary `0x30d8c0–0x312c6c`, native child factory call `0x30ee58` constructs a `SubtreeCondition` child with compiled ConstStr parameters `expand_in_logger=true` and `subtree_file_path=StationWash.xml`.
- All two-builder registration, generated root-helper, nested child and original FDE-boundary evidence matches pinned original `liblethe_tree.so` bytes.

### Exact original instructions and symbols

| Virtual address | Evidence |
|---|---|
| `0x568a74` | NUL-terminated `RobotNode` literal |
| `0x565bf8–0x565bfc` | Literal ADRP+ADD in the plugin-registration entry |
| `0x565c18`, GOT `0x7b1c48` | `R_AARCH64_GLOB_DAT` names `buildRobotNode` |
| `0x565c38` | Direct native `registerTreeBuilder` call for RobotNode |
| `0x578590` | NUL-terminated `StationWash` literal |
| `0x566240–0x566244`, GOT `0x7b1c50` | Name and relocation to distinct `buildStationWash` |
| `0x566278` | Direct native `registerTreeBuilder` call for StationWash |
| `0x562b4c–0x567a78` | FDE enclosing *both* registrations within `BT_RegisterNodesFromPlugin` |
| `0x312c6c–0x312d30` | Native `buildRobotNode` symbol/function FDE |
| `0x312ca0`, `0x312ca4`, `0x312ca8` | `init_fac`, BL `0x30d8c0`, `clear_fac` |
| `0x30d8c0–0x312c6c` | Original generated RobotNode helper FDE |
| `0x30ee3c–0x30ee40`, `0x6f8350` | Compiled `StationWash.xml` child parameter table |
| `0x30ee58` | Native child-node factory BL within generated RobotNode helper |

### Important qualification: differing path syntax

The owner-configured root selector **`RobotNode` has no extension**; the nested station selector is **`StationWash.xml`**. The original `SubtreeConditionNode::onInit()` sends the extensionless case through a **different parsing branch** at `0x758a0 → 0x760d0`. v97 proved the dotted `StationWash.xml` native-builder lookup. Neither the different root branch nor current v99 evidence permits a claim that *the live R2416 selected or ticked either builder*. Builder registration still requires a successful runtime plugin load. A source-level generated construction path is not an observed cleaning run.

The unresolved `special_push_clean_dish` R2416 writer, child Blackboard scope, `SetWashMchineControl` availability, `WASH_CONTROL` physical receiver, real turbidity signal and a **second physical mop wash** remain unproved. `r2343_start_rewash` → `wash_times` bookkeeping alone is not physical actuation.

## Reproducible offline test

Original private SHA-256 pins:
- `liblethe_tree.so` — `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`
- `node_lethe.so` — `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `libbehaviortree_cpp.so` — `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

The separately delivered sanitized package **`X40-R2416-v99-sanitized-two-level-native-tree-20261024.zip`** contains:
`x40_r2416_v99_two_level_native_tree_bridge_verify.py`, the full technical report and README. It does not contain source ELFs, XML, settings, maps, device IDs or credentials.

```sh
python3 x40_r2416_v99_two_level_native_tree_bridge_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verified test output:

```text
X40_V99_PINNED_PRIVATE_CONFIG_ROOT_AND_PLUGIN_PATH_PASS
X40_V99_REGISTERED_ROBOTNODE_AND_STATIONWASH_BUILDERS_STATIC_PASS count=2
X40_V99_NATIVE_ROBOTNODE_BUILD_HELPER_WITH_STATIONWASH_SUBTREE_STATIC_PASS
X40_V99_EXTENSIONLESS_ROOT_VS_DOT_XML_RESOLVER_BRANCH_DISTINCT_PASS
X40_V99_ROOT_BUILDER_AND_GENERATED_HELPER_FDE_SCOPE_PASS
X40_V99_V98_LOADER_AND_NATIVE_STATIONWASH_RESOLVER_REGRESSION_PASS
X40_V99_INSTRUCTION_LITERAL_RELOCATION_MUTATIONS_REJECTED count=18
LIMIT: compiled native RobotNode -> StationWash graph, not observed registration success, root/subtree tick or physical rewash
```

The 18 self-tests reject individual instruction, literal, table and **actual relocation record** alterations. They do not change the robot or establish live feature behavior.

Sanitized artifact hashes:
- Python verifier SHA-256 `3218cf6f6466ff65729b83e5f97255d3145f8af49e53422d9bfe1e7957a0ac16`
- Sanitized ZIP SHA-256 `4a4ae4ff40d865521a9d3e20cd522891500dc4d795bbe8eb1abee51cf94d62c9`

**Next:** inspect exact extensionless-root resolution and possible `SubtreeConditionOptNode` override, then pursue passive evidence of actual plugin registration and tree selection; do not inject guessed native control messages or synthetic dirt events.

**Preserve last verified working v74**: `SmartHost=0`, `writeGateOpen=false`, original launcher, native baseline and v70/v73/parent/vendor backups. No robot-side changes required.
