# Dreame X40 R2416 v217 — generated stain-check ownership and guarded CleanList handoff

**27 October 2026. Original firmware offline, SHA-256 pinned.** Continues the v195 native RobotNode correction and v197–v216 research. Private ELF binaries, configuration, map data, process metadata and owner collector archives remain outside GitHub. No robot commands, firmware writes, experimental activation or `master` changes.

## New generated-tree ownership evidence

In original `liblethe_tree.so` (SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`), all immediately adjacent same-register AArch64 ADRP/ADD references to exact node type names were counted and native child factory/attachment calls decoded:

| Native generated child | Name address | Reference | Factory call (to `0x1c6620`) | Parent builder |
| --- | --- | --- | --- | --- |
| `AiStainCheck` | `0x5b5631` | `0x45e6c8` | `0x45e6d8` | `buildNavigateTree` |
| `SetExtraCleanArea` | `0x5a0b8d` | `0x3c1ec8` | `0x3c1ed8` | `buildCleanSelectedAreas` |
| `SetExtraCleanArea` | `0x5a0b8d` | `0x4176b4` | `0x4176c4` | `buildFindNearbyMovablePoint` |

The three nodes also have direct `control_parent_addChild` calls at `0x45e6e4`, `0x3c1ee4`, `0x4176d0`. Native exported-builder code ranges, exact literal-pointer construction, instructions and target calls are pinned. **The AiStainCheck child and two SetExtraCleanArea children are in different generated builders**, and this code placement does not establish live traversal order.

## Static Blackboard chain into generic cleaning

In SHA-pinned original `liblethe_route_nodes.so` (`fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`):

1. `cleanbot::MapSensor::CleanedAreaBuild` conditionally writes compatible `stain_area_for_logic` data: exact key at `0xf8b528`; typed box cast `0xf8b508`, setter-compatible virtual slot `0xf8b560` and BLR `0xf8b57c`.
2. `utility::AiStainCheck::tick` has a typed `AlignedBox` getter `0x51916c` and guards; reads the exact shared key at `0x5191c0` and `std::Hashtable::find` at `0x51921c`.
3. `subregion::SetExtraCleanArea::tick` has parameter and stain-type guards; tests the exact shared `stain_area_for_logic` key at `0xad944c` through `BLR` `0xad9474`, skipping the list append on branch `0xad947c`. On the surviving branch it calls `CleanList::append` at `0xad94bc` and typed `Blackboard::set<types::CleanList&>` with `Areas_Clean_List` at `0xad94ec`.
4. `system_motion::Cleanbot::preprocess` obtains its node Blackboard, constructs `Areas_Clean_List` at `0xdf2f50` and performs a guarded virtual lookup at `0xdf2f78`. `types::SendCLeanListToCleanbot` separately calls typed `Blackboard::get<types::CleanList>` at `0x5d05fc` and guards failed/empty lists. Its name is **not** proof that it sends a task command.

The new v217 scanner's **restricted adjacent same-register ADRP+ADD reference form** yields **11 direct references** to `stain_area_for_logic` and **62 to one `Areas_Clean_List` literal at `0xfce5e0`**; another exact list literal is present at `0x1007b9c` but has no references of *this restricted form*. Earlier v186 reported 77 references under its own census. **Do not silently replace or equate those two counts**: the scope and scanner definitions matter, and neither implies all indirect/runtime uses.

**Proof limit:** This is a compiled **producer → named data interface → guarded CleanList update → generic Cleanbot consumer**, not a proven execution chain. No same-instance live Blackboard identity, order of the three separate generated builders, dirt-caused actual new task-dispatch call, second floor pass or dock rewash has been established. The generic CleanList and `need_extra_clean` are not unique AI-dirt event identifiers.

## Validation and next action

The source-only offline kit `X40-R2416-v217-sanitized-analysis-kit.zip` has SHA-256 **`6ed558fc279fa41b148f6c52b2ec8197685fb39f619543dc43524a0fef399704`**, **73 entries including manifest**, and **72/72 extracted file hashes** verified. It passed **13 focused v217 tests**, all inherited v197–v216 regressions, **53 new original instruction checks**, **21 decoded branch/call targets**, the **1+2 node placements**, and the **11/62 narrow xref censuses**. Mutations deliberately breaking generated node creation, key write/read and branch guards are rejected. The small independent repo-side check confirms **22 representative instruction anchors and six factory/helper calls** against the private original ZIP.

**Next:** reconstruct calls from the actual generated owner builders to area-selection/task-start logic; identify an actual cleaning-task dispatch and timing/same-Blackboard link before enabling or attributing CleanGenius. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No additional robot collection needed for the next offline pass.
