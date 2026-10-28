# Dreame X40 R2416 — v84: StationWash fresh file subtree Blackboard forwarding

**2026-10-24. Offline static research only.** Original owner-private firmware remains private. No robot connection, firmware modification, MIOT setting write, reboot, or deployment.

## Verified finding

The native `liblethe_tree.so` StationWash child is constructed with exactly two `ConstStr` parameters: `expand_in_logger=true` and **`subtree_file_path=StationWash.xml`**. The path is ordinary, without a `reuse/` prefix. This is a compiled reference, **not evidence that the actual StationWash.xml content was collected or its subtree ran**.

The fresh file-subtree branch in `libbehaviortree_cpp.so:BT::SubtreeConditionNode::onInit()` obtains the wrapper's `TreeNode::blackboard()` handle and forwards it as argument `x2` to `BT::buildTreeFromFile()`. In the callee, the received third argument is captured and passed unchanged as argument `x2` to **`XMLParser::instantiateTree()`**, after loading the XML file.

### Native ELF anchors

| ELF | Virtual address | Verified role |
|---|---|---|
| `liblethe_tree.so` | `0x30ee38–0x30ee58` | Two native parameter pairs, `SubtreeCondition` child construction and `child_node_factory_instantiateTreeNode` |
| `liblethe_tree.so` | `0x6f8350` | Exact `ConstStr` values `expand_in_logger=true`, `subtree_file_path=StationWash.xml` |
| `libbehaviortree_cpp.so` | `0x759d0`, `0x75a10–0x75a18`, `0x75dd8–0x75ddc` | Ordinary path skip of pre-registration, and unregistered cache miss clears post-build cache-insertion flag |
| `libbehaviortree_cpp.so` | `0x75b74–0x75b78` | An already registered but empty tree-cache entry may still fall through to fresh build |
| `libbehaviortree_cpp.so` | `0x75b88–0x75b90` | Gets the wrapper `TreeNode::blackboard()` |
| `libbehaviortree_cpp.so` | `0x75ba0–0x75bb0` | Forwards wrapper Blackboard as `x2` to `buildTreeFromFile()` |
| `libbehaviortree_cpp.so` | `0x7025c`, `0x70284`, `0x7028c–0x702a4` | Captures argument `x2`, loads XML, forwards the same Blackboard to `XMLParser::instantiateTree()` |
| `libbehaviortree_cpp.so` | `0x75bb8–0x75bc0` | Fresh owner/root stored; cache population separately conditional |

Original SHA-256:
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

This confirms the **fresh wrapper-to-file-instantiator root Blackboard argument connection**, not the effective NodeConfig or Blackboard identity of each instantiated `StationHandle` child. As v65/v66 found, reuse cache behaviour depends on a separate registration step; cache hits may reuse a previous root without this fresh forwarding. No runtime cache hit is proven.

## Evidence gap: actual StationWash.xml missing

The two existing owner-private evidence archives (`X40-R2416-v62-readonly-20261023T051829Z.zip`, `X40-R2416-v63-runtime-gap-20261023T053118Z.zip`) have **no file named StationWash.xml**. Embedded ELF strings mentioning `StationWash.xml` are not the XML contents. Do not invent the NodeConfig scope, remapping, subtree dependencies or active station-node Blackboard identity.

## Repeatable pinned validation

The separately delivered **sanitized** archive `X40-R2416-v84-sanitized-stationwash-blackboard-20261024.zip` includes `x40_r2416_v84_stationwash_file_blackboard_verify.py`, a detailed report and README, but no proprietary binaries. The standalone Python 3 script loads the private original v62 ZIP in memory, checks both SHA-256 pins, AArch64 instructions, PLT symbol destinations, native parameters, and root forwarding, and rejects 38 one-byte mutations.

```text
X40_V84_COMPILED_STATIONWASH_SUBTREE_FILE_PATH_STATIC_PASS
X40_V84_NONCACHE_MISS_TO_WRAPPER_BLACKBOARD_PASS
X40_V84_STATIONWASH_BUILD_FILE_ROOT_TO_XML_PARSER_STATIC_PASS
X40_V84_CONDITIONAL_REUSE_CACHE_NOT_IMPLIED_PASS
X40_V84_INSTRUCTION_PARAMETER_MUTATIONS_REJECTED count=38
LIMIT: XML NodeConfig scopes/remappings, runtime StationWash identity and extra physical wash NOT observed
```

No vendor ELF, original XML, private YAML, maps, identifiers, tokens or full disassembly are included.

## Next

Inspect **authentic StationWash.xml**, if an existing authorized offline copy becomes available, to resolve child Blackboard scopes and remappings. Then revisit whether R2416 provides `special_push_clean_dish` by a different writer, whether `r2343_start_rewash` causes a real extra station command, and whether genuine dirt/turbidity triggers the physical behaviour. No guessed switch writes or synthetic contamination.

**Operational state unchanged:** tested Valetudo+ **v74**, native SmartHost restored to 0 after the validated 1→0 test, launcher reverted, `writeGateOpen=false`, native baseline unchanged on final reboot. Preserve v70/v73 fallbacks and all original backups; nothing in v84 should be installed on the vacuum.
