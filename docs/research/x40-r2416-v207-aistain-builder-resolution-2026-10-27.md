# X40 R2416 v207 — AiStainMop generated subtree and exported native builder coverage

**27 October 2026; offline, read-only static ELF analysis.** The owner's private R2416 collector ZIPs and SHA-pinned original AArch64 native libraries were inputs. This extends v195's corrected native RobotNode model and the v197–v206 verified research. No original binary, private robot settings, maps, videos or credentials are included in this public document. No robot access, writes or `master` change.

## New native builder coverage result

The original `liblethe_tree.so` contains a generated `SubtreeCondition(subtree_file_path="reuse/AiStainMop")` child in `buildReuseTree`. Its exact two-pair parameter table resides at VA **`0x68a770`** and is used at **`0x1cb3e8–0x1cb400`**. `reuse/CleanSelectedAreas` is a separate generated child at table `0x68b530`.

A bounded original-ELF `.dynsym` census decoded Itanium length-prefixed names for **199 distinct exported, defined `build<Name>` functions** in this one tree library. Comparison against all **158 distinct generated `reuse/` child path names** shows:

| Measure | Count |
|---|---:|
| Generated ReuseTree opt-in children | 158 |
| With a matching exported `build<Name>` function | **138** |
| Without a matching export | **20** |
| Defined exported native builder functions | 199 |

`reuse/AiStainMop` is **one of the 20 without a matching exported `buildAiStainMop`**. `reuse/CleanSelectedAreas`, in contrast, **does** have a matching exported `buildCleanSelectedAreas` native function. Exactly one `AiStainMop` substring occurs in the checked original tree ELF, as part of `reuse/AiStainMop`, and there is no `AiStainMop.xml` literal in that ELF. The route-node library separately contains `utility::AiStainCheck` and `subregion::SetAiStainMopRegion` **node-class** implementations, which are not equivalent to a complete `AiStainMop` tree builder.

The complete set of 20 unmatched generated paths is recorded in the downloadable kit's sanitized `v207-SANITIZED.json`. The count is **a precise string/name comparison to defined exported functions of this one ELF**—not a census of all loaded plugins, all hidden or inlined builders, dynamically generated registry names, or the robot's live factory map. Even a matching function export is not proof of runtime registration or execution.

## Two possible built-in resolution routes

In the exact original `libbehaviortree_cpp.so`, `SubtreeConditionNode::onInit` contains:
- A file-backed route: gets `TreeNode::blackboard()` at **`0x75b8c`**, forwards the Blackboard and calls `buildTreeFromFile()` at **`0x75bb0`**.
- A native tree-builder route: calls `BehaviorTreeFactory::tree_builders()` at **`0x75de8`**, obtains the Blackboard at **`0x75f68`**, and invokes a registered builder via **`BLR` at `0x75f9c`**.

Exact AArch64 instruction words and direct BL targets are checked against pinned whole-file hashes. These paths establish **compiled resolution mechanisms**, not successful `reuse/AiStainMop` resolution on the running robot. It could come from another native tree library, nonexported/aliased registration, an external XML/subtree resource, or another runtime route. The private collector ZIPs do not contain an identified `AiStainMop` subtree file, but they were **not exhaustive inventories of all installed plugins/XMLs**, so this is not proof of absence from the robot.

## Implications for automatic reclean

Earlier v185 identified shared `stain_area_for_logic` usage by `MapSensor::CleanedAreaBuild`, `AiStainCheck`, and `SetExtraCleanArea`; v182 established the separate stain-ID acknowledgement topic. Neither chain proves that a native AI stain event causes an **additional physical cleaning task**. v206 proves a compiled ReuseTree entry and possible initialization route, but v207 **does not** establish that `AiStainMop` is broken, fully implemented, reachable, initialized, cached or ticked in a real R2416 run. The R2416 `special_push_clean_dish` dock-rewash gate remains a separate open issue.

## Reproduce and next evidence

Source-only offline release: `X40-R2416-v207-sanitized-analysis-kit.zip`, SHA-256 **`c829c327d2c7807faa84cfc8b14c9ea1f3296894fd8c229d670c911fb33d43a2`**. It contains the complete v197–v207 standard-library-only replay chain, exact static `.dynsym` parser, generated subtree census, a research report, sanitized JSON and checksum manifest. It passed **all nine v207 focused tests**, all inherited v197–v206 checks, **22 new native instruction-word checks**, **nine decoded BL targets**, five whole-ELF SHA-256 pins and saved-file digest verification on the two owner-private archives; a clean extraction verified all **33 internal payload hashes**. Mutation/negative tests reject tampered original ELFs, changed opcode or call target, wrong coverage count and overwrite attempts.

**Next:** obtain only a bounded, read-only listing of installed tree plugins and a targeted `AiStainMop` subtree file search—on the owner's Mac firmware archives first, and on the robot only if needed. A normal file listing or missing exported symbol is not itself evidence of a failed live resolution. No maps, cameras, cleaning commands or experimental writes are needed. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; keep original binaries and raw configuration outside GitHub.
