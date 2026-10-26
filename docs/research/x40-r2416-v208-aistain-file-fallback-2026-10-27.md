# Dreame X40 R2416 v208 — exact AiStainMop file-fallback argument and collected-plugin boundary

**27 October 2026. Owner-private original R2416 firmware, read-only offline analysis.** Extends the v195 native-`RobotNode` correction and the v197–v207 exact native audits. No robot access, firmware change, Valetudo+ change or public `master` change. Proprietary ELF files and raw robot settings are **not** in this repository.

## New result: the file-loader input is `reuse/AiStainMop`

The generated native `ReuseTree` provides `subtree_file_path=reuse/AiStainMop` via verified original `liblethe_tree.so` parameter table **VA `0x68a770`**. On the **file** fallback branch in original `libbehaviortree_cpp.so`, `BT::SubtreeConditionNode::onInit()` retains the original parameter string at `sp+0xc0` / `x24` (`0x757dc`, passed to `getParamImpl` at `0x75800`). It passes `x1=x24` to **`BT::buildTreeFromFile`** at `0x75ba4–0x75bb0` alongside the node Blackboard in `x2`. The callee saves `x1` in `x20` at `0x70244` and forwards `x1=x20` to **`XMLParser::loadFromFile`** at `0x7027c–0x70284`.

**Verified at the API boundary:** the original parameter string is passed unchanged through these two function calls. The complete internal file search/path transformations of `XMLParser::loadFromFile` were **not** reconstructed. `reuse/AiStainMop` (extensionless, prefixed) is thus an essential candidate in addition to `AiStainMop.xml` and any external resource root. Do **not** claim the parser necessarily opens the literal original pathname or automatically appends `.xml`. The distinct native registered-builder path calls `BehaviorTreeFactory::tree_builders` (`0x75de8`) and a callback (`0x75f9c`).

## Second result: all **six collected** original ELF modules checked

The first owner-private collector ZIP contains six ELFs. Five match the established complete original SHA-256 pins; `node_health_lethe.so` independently matches its saved digest **`5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`**. A bounds-checked ELF64LE `.dynsym` audit across all six gives:

| ELF | Defined exported `build<Name>` functions | `AiStainMop` byte-substrings |
|---|---:|---:|
| `liblethe_tree.so` | **199** | 1, in `reuse/AiStainMop` |
| `liblethe_route_nodes.so` | 0 | 21, related `AiStainMopRegion` classes |
| `liblethe_tactics_tree.so` | 0 | 0 |
| `libbehaviortree_cpp.so` | 0 | 0 |
| `node_lethe.so` | 0 | 0 |
| `node_health_lethe.so` | 0 | 0 |

There is **no matching defined exported `buildAiStainMop` in any of these six**, but this is explicitly a collected-binaries/export census, **not** a census of all installed plugins, private/hidden/aliased builders, factory registrations or file-backed subtrees. The `AiStainMopRegion` class is a separate node type, not proof of a complete registered `AiStainMop` tree.

The privately collected `setting.yaml` sets `tree_lib_path: /tmp/lib/tree_lib//`; the model's `r2416.conf` names a separate `nodes_dir: /tmp/ava/lib/`. Neither existing collector ZIP is an exhaustive inventory of the first directory. The source-only v208 collection kit therefore limits further discovery to named `AiStainMop` resources and tree-library plugin binaries; it never collects maps, camera data, logs or model weights.

## Tests and source-only handoff

Complete offline package: **`X40-R2416-v208-sanitized-analysis-kit.zip`**. SHA-256 **`e2835c8ef397c835808b0e8c66a8011d8eac001616f3f76daf9f78f80bdc2bf4`**. Contains complete v197–v208 Python 3 stdlib-only verifier chain and regression test sources, targeted v208 private collector, this research narrative and sanitized JSON. It has **37 entries**, including a checksum manifest; **36 internal SHA-256 checks** and ZIP integrity passed. A separate clean extraction replayed all **13** v208 tests: 19 exact native instruction anchors, 6 direct BL targets, full inherited v197–v207 regression, five original ELF pins, sixth collected saved-byte pin and both prior evidence ZIP checksum inventories (18+7). Negative tests reject altered native ELF bytes, altered opcode, changed branch target, unsafe archive paths and existing output overwrite. The v208 collector's read-only SSH mode has **not** been exercised on the robot.

**Next:** use already held Mac firmware archives first, then (only if needed) explicitly opt into read-only remote plugin/resource inventory. A matching file or registry entry would advance resolution; **neither** proves the AI-stain event starts another cleaning task, or a physical second floor pass. Keep experimental CleanGenius writes off: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. `master` and robot remain unchanged.
