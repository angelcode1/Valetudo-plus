# Dreame X40 R2416 — v206 generated ReuseTree / AiStainMop prebuild boundary

**27 October 2026.** Read-only offline analysis of the owner's five SHA-256-pinned original R2416 native libraries and both previously collected private archives. Continues the corrected v195 native-`RobotNode` model and v197–v205 regressions. No robot access, firmware modification, vendor execution, experimental CleanGenius writes or changes to `master`. No proprietary native ELF, raw device settings, maps or credentials committed.

## New verified native generated-tree finding

The original `liblethe_tree.so` exports native `buildReuseTree` at `0x1cc8f4`. The builder calls `init_fac` at `0x1cc928` and its generated body at `0x1cc92c → 0x1c9be4`. That body builds a `Fallback` root, an `AlwaysSuccess` child, and **158 distinct generated `SubtreeCondition` children whose `subtree_file_path` values begin with `reuse/`**. This count is independently obtained by decoding each concrete ADRP/ADD/vector-copy site within `0x1c9be4–0x1cc8f4`, reading the two `ConstStr` parameter pairs through original ELF load segments, and verifying whole-ELF SHA-256. It is a compiled child count, **not an observed cache-entry count**.

The generated `reuse/AiStainMop` child's exact two-pair parameter vector starts at **VA `0x68a770`**, selected at **`0x1cb3e8–0x1cb400`**. The pairs are `expand_in_logger=true` and `subtree_file_path=reuse/AiStainMop`. The sequence calls the normal child-node factory, so this is an actual generated child placement, not merely a string in a constant pool. Another verified child has `subtree_file_path=reuse/CleanSelectedAreas`, table **`0x68b530`**, site **`0x1ca138–0x1ca150`**. **No `reuse/StationWash` child appears in the 158-item generated ReuseTree census**. That aligns with the v205 correction: normal generated `StationWash.xml` is unprefixed.

## Host construction order and incoming Blackboard

In original `node_lethe.so`, the auxiliary fixed wrapper literal at `0x9d64d0` selects `ReuseTree.xml`. The `AvaNodeRoute` constructor supplies the **route's `this+0x30` Blackboard** at `0x355114`, invokes `BT::buildTreeFromText` at **`0x35511c`**, then retains this auxiliary tree starting at route member **`+0xf28`** (`0x35512c`). *Later* in the same constructor, the configured native-`RobotNode` wrapper supplies the **same `this+0x30` field** at `0x3552c0`, invokes `buildTreeFromText` at **`0x3552c8`**, then retains the main root starting at **`+0xf48`** (`0x3552d8`). This verifies **static construction order and holder-field forwarding**, not actual descendant Blackboard object identity or successful live construction.

## Conditional pre-tick initialization mechanism

Original `libbehaviortree_cpp.so` factory creation calls `TreeNode::setBlackboard` at `0x5f638` before `TreeNode::initializeOnce` at `0x5f650`. The latter checks its node initialization flag and has conditional virtual dispatch at `0x4fb00–0x4fb34`. Independently, the `R_AARCH64_ABS64` relocation for the first virtual slot of `SubtreeConditionNode` at `0xd65e0` points to its `onInit` implementation at `0x757b0`. This supplies a compiled **possible construction-time path** into v205's `reuse/`-opt-in subtree resolver/cache handling. It is **not proof that this flag was set, that the effective node implementation is the inspected built-in type, or that any auxiliary child was successfully cached**.

An `AlwaysSuccess` child in the generated `Fallback` must not be confused with evidence of an actual cleaning task tick; construction-time initialization and runtime ticking are separate.

## What v206 settles / does not settle

**Verified statically:** native auxiliary `ReuseTree` owns the real generated `reuse/AiStainMop` child; its fixed route wrapper is constructed before configured `RobotNode`; both wrapper builds use the same route Blackboard holder field; the fresh node factory offers a conditional pre-tick `onInit` path; the generated reuse set has 158 distinct entries including `CleanSelectedAreas` and no `StationWash`.

**Unproven:** successful runtime resolution of `AiStainMop` to a native registered tree or external resource; live execution of `onInit`; populated cache, cache invalidation, owner lifetime or actual cache hit; equal runtime Blackboard instances across stain/tactics consumers; AI stain initiating an additional cleaning task; or physical floor reclean/dock rewash. `SetAiStainMopRegion`, `AiStainCheck`, and `SetExtraCleanArea` have separate native implementations, but their mere presence does not establish the missing task-start edge.

## Reproduce

The full source-only offline kit is **`X40-R2416-v206-sanitized-analysis-kit.zip`**, SHA-256 **`0ca4cb7a41dd6c2ea9186d2b01032fd0f3a6f2403ff05521814cddc0aa0d1c53`**. It contains complete v197–v206 Python 3 standard-library regression code, 10 focused v206 tests, sanitized report/JSON, 45 pinned new original AArch64 words, 11 new decoded call/branch checks, original vtable relocation inspection and the 158-child census. The private first/delta archives remain external inputs. Full regressions recheck five original ELF SHA pins and 18+7 collector saved-file SHA values. A clean extraction passed 10 v206 tests, all **31** internal file checksums and ZIP CRC validation. A separate smaller repo-side checker verifies the same 158-child census and targeted original binaries without dependencies.

**Next:** resolve actual `AiStainMop` tree-builder registration or proven external subtree and find its consumer in the effective native cleaning tree, then inspect auxiliary root `AvaNodeRoute+0xf28` lifetime/cache handoff. No new robot collection is required for these offline steps. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.
