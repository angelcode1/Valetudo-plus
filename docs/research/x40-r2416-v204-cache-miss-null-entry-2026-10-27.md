# Dreame X40 R2416 v204 — subtree cache-miss versus null-entry branch

**27 October 2026. Offline, read-only analysis of the original owner-private R2416 AArch64 ELF.** Builds on v195 native-`RobotNode` correction and v197–v203 research. No robot communication or firmware/Valetudo+ changes. Keep raw vendor ELF and private configuration outside the public repository.

## New branch-sensitive result

In original `libbehaviortree_cpp.so` (SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`), `BT::SubtreeConditionNode::onInit()` has **two distinct conditions** that v203 did not separate:

- **An absent keyed cache entry:** the `std::_Rb_tree::find` call at `0x75a10` reaches the not-found branch at `0x75a18→0x75dd8`. The instruction at `0x75ddc` sets local `[sp,#0x84]` to **zero**. The subsequent `0x75de0` tests whether a registered native-builder route is available or the file-builder route is needed. After successful construction, `0x75bbc` reads the same local flag, and `0x75bc0→0x75ad4` **skips cache insertion when the flag is zero**. Thus an ordinary missing-key fresh build need not create a populated cache entry, even though caching code exists.
- **An existing cache entry whose tree-pointer value is null:** `0x75ac4–0x75ac8` detects a zero pointer at entry offset `+0x40`. This path sets the local flag to **one** at `0x75b78–0x75b7c`. Successful fresh construction can then reach `0x75c90` and store the resulting `BT::Tree*` into the cache slot at `0x75c98`.

A **separate key-creation path** (`0x759f8→0x763f0`) inserts a new filename-keyed tree-map entry with helper call `0x764b0`, and `0x764b8` sets the entry's pointer slot to null. This is **placeholder initialization**, not verified deletion-time invalidation of a previously populated cache entry.

On a **non-null cache hit**, `0x75acc` retrieves the cached root and `0x75ad0` writes both the root pointer and an explicitly null owning-tree pointer at the consumer node's `+0x20/+0x28` offsets. The cached consumer thus does **not** acquire ownership via the `+0x28` destructor field; the original owner still has the delete path `0x74e94→0x74f4c` (v203). This is an important ownership distinction. The conditional dangling-pointer hazard described in v203 **requires an actually populated cache entry and owner destruction in the wrong lifetime order**. Neither has been observed on a live X40.

The original native `StationWash` builder and simple-filename resolution have been verified previously, but **which cache-key/flag branch it takes during a real station wash is still unobserved**. No conclusion that it always caches or never caches is justified. No stale live Blackboard, use-after-free, crash, special-push mop rewash, AI-stain-triggered new task, or physical extra floor-cleaning pass is established.

## Evidence and reproducibility

The complete locally packaged `X40-R2416-v204-sanitized-analysis-kit.zip`, SHA-256 **`ee9718094c87e4b8a46c3074acc898a3e49125f7b94d5980a85cd092112d0b90`**, carries all source-only v197–v204 offline verifiers and tests plus sanitized research/JSON. Against the owner's two private ZIPs, it passes all earlier v197–v203 regressions and **50** additional exact native instruction-word checks, **16** decoded branch/call edges, and **10 v204 focused tests** (including tampered ELF, changed expected instruction/edge, and create-only report refusal). All five original native ELF whole-file SHA pins and 18+7 previously collected saved-file hashes are checked by the regression chain. A clean extraction passed its **23 internal SHA-256 checks** and all ten v204 tests. No copyrighted proprietary ELF, personal map, sensor data or unredacted robot configuration is included.

**Next:** identify the exact key-parsing conditions for entry placeholder creation and the effective `SubtreeCondition` registration; trace ownership transitions through root teardown. Do not turn a conditional stale-pointer pattern into a confirmed defect. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Keep all future tests offline until static gates are resolved.
