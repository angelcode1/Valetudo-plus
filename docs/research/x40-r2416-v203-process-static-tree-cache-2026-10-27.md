# Dreame X40 R2416 v203 — process-static subtree-cache lifetime and owner-release boundary

**27 October 2026 | offline owner-private native analysis.** Continues the v195 correction (the configured `RobotNode` root is native) and v197–v202 turbidity/subtree research. This report contains no original firmware bytes, full disassembly, private robot configuration, credentials, maps or model weights. No robot access or running-Valetudo+ modification.

## New native evidence

In the original, whole-file SHA-pinned `libbehaviortree_cpp.so` (**SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`**), built-in `BT::SubtreeConditionNode::onInit()` uses a function-static, string-keyed `std::_Rb_tree<std::string, BT::Tree*>`. The symbol identifies a **raw `BT::Tree*`** value, not a shared ownership wrapper. The static map is created under a one-time guard (`0x759c4–0x759c8 → 0x75fc8`) and its destructor is registered with `__cxa_atexit` at `0x75ff8`; the guard is released at `0x76000`. This establishes a process/static initialization-and-teardown mechanism, not a per-cleaning-job cache reset.

**Cache lookup and attachment:** On the relevant path, the map lookup occurs at `0x759e8` and `0x75a10` via `std::_Rb_tree::find`. A present entry's raw tree pointer is loaded from the map-entry `+0x40` at `0x75ac4`, checked at `0x75ac8`, dereferenced at `0x75acc` for its root, and the root is attached at the current node's `+0x20` via `0x75ad0`. v202 established that this cached attachment branch makes no **direct** new `setBlackboard` call. Native filename normalization for the generated `StationWash.xml` subtree to registered `StationWash` is documented in v30.

**Fresh construction and cache write:** The relevant fresh file/native builder branches are entered on a cache miss (`0x75ac8 → 0x75b78`). They obtain the node's Blackboard and forward it into tree construction. At `0x75bb8`, the new root pointer and heap `BT::Tree*` are stored on the node at offsets `+0x20/+0x28`. When caching is enabled, `0x75c90` obtains a filename-keyed map entry and `0x75c98` stores the **same raw tree pointer** into entry offset `+0x40`. A subsequent lookup can reuse the cached root instead of rebuilding.

**Owner release:** `BT::SubtreeConditionNode::~SubtreeConditionNode()` loads its owned tree pointer from node offset `+0x28` at `0x74e94`; it has a guarded halt path and calls `operator delete` for the tree pointer at `0x74f48–0x74f4c`. A complete scoped census of all **352 bytes of this destructor** finds **five direct `BL` sites**, none to the inspected map-find or map-insertion helper, and includes the tree release at `0x74f4c`. This is a bounded negative result, **not** an exhaustive proof that no other code invalidates or transfers the cache entry.

## Significance and limits

The compiled code exposes a **conditional dangling-pointer hazard**: if a cache entry survives destruction of the node that owns its raw `BT::Tree*`, a later lookup could use a no-longer-valid pointer. No live entry lifetime, cache hit after destruction, stale station Blackboard, use-after-free, crash, exploitability, or R2416 physical mop-rewash has been demonstrated. Runtime ownership coordination, other cleanup paths and effective plugin-registration choices remain to be examined. The destructor and cache code are not themselves proof of an actual defect.

This remains separate from the unresolved AI-stain-to-new-floor-cleaning-task path and the R2416-specific `special_push_clean_dish` eligibility question. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; never enable experimental writes as a diagnostic shortcut.

## Reproducibility

Full offline source-only release: `X40-R2416-v203-sanitized-analysis-kit.zip`, SHA-256 **`66c767868bd1ba63da6569bbd1a62ba5dbcf64d61667384622c4f23d78145d0f`**.

The complete v197–v203 Python 3 standard-library chain passed against the same two private collected ZIPs: **five original ELF whole-file pins**, **18 + 7** saved-payload SHA-256 checks, **63 additional original AArch64 instruction anchors**, **20 decoded native branch/call edges**, a complete scoped destructor direct-call census, and **11 focused v203 tests**, including changed input/instruction/branch rejection and create-only output enforcement. The ZIP has **22 entries, with 21 included payload checksums**, and passed clean-extraction replay.

**Next offline work:** identify global cache invalidation/erase sites and the effective `SubtreeCondition` registration; determine whether the native `StationWash` node can be destroyed and reconstructed while a keyed cache entry survives; distinguish static possibility from actually exercised lifetime. `master` and the live robot remain unchanged.
