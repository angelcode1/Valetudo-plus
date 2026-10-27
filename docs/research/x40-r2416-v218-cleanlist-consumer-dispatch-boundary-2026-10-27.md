# X40 R2416 v218 — CleanList direct consumers and the unproven task-dispatch edge

**27 October 2026. Offline, original SHA-pinned firmware analysis only.** Continues v195 native `RobotNode` correction and v197–v217 research. No robot command, firmware write, CleanGenius enablement, private ELF, settings, map data, PID, diagnostics or PRIVATE collector archive committed. `master` is unchanged.

## New verified bounded direct-call topology

Scanning the original **`liblethe_route_nodes.so`**, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`, across executable **`.text` VA `0x4526f0–0xf9c0b0`**, for AArch64 **direct `BL` calls into four exact PLT stubs**, gives *exactly one* direct call to each:

| Native callee | PLT | Direct original call | Enclosing named function |
|---|---|---|---|
| `Cleanbot::preprocess(BT::TreeNode&)` | `0x449140` | `0xdf4eac` | `Cleanbot::edge_cleaning` |
| `Cleanbot::edge_cleaning(BT::TreeNode&)` | `0x4416a0` | `0xcd0cd8` | `FollowWallModeDeal::FollowWallModeDealFunc` |
| `types::SendCLeanListToCleanbot(...)` | `0x43d950` | `0x52f3c0` | `utility::GridmapInit::SetReuseTrans` |
| `Cleanbot::post_process()` | `0x447ac0` | `0xdf4f2c` | `Cleanbot::edge_cleaning` |

The PLT targets, original whole-ELF hash, 57 instruction anchors and 21 decoded call/branch edges are pinned in the verifier. The bounded census enumerates *all* direct BL instructions in this original .text and rejects an inserted extra direct call at an unanchored location.

The **direct** chain is `FollowWallModeDealFunc → Cleanbot::edge_cleaning → Cleanbot::preprocess`, with `Cleanbot::post_process` also called from `edge_cleaning`. The distinct `GridmapInit::SetReuseTrans → SendCLeanListToCleanbot` call goes through a separately named route: `SetReuseTrans` calls `BT::TreeNode::blackboard()` at `0x52f3b8` then calls the helper at `0x52f3c0`. Its string-return ABI/name is **not** evidence of transport actuation or new task scheduling.

**Census scope:** This is not an exhaustive callable-API census: indirect calls, virtual dispatch, other shared objects, alias stubs and dynamic registration are outside the narrow direct-BL scope. A one-site count does not imply runtime exclusivity.

## New concrete Cleanbot typed-list processing

Inside `Cleanbot::preprocess`:
- `0xdf2f48` obtains the `BT::TreeNode` Blackboard; `0xdf2f50/54` builds the **`Areas_Clean_List`** key, with the exact literal at `0xfce5e0`.
- `0xdf2f78` invokes a guarded virtual lookup, with an absence branch at `0xdf2f80`.
- `0xdf2fa0` calls `std::type_info::operator==` and `0xdf2fa8` checks its result. Further validation/absence tests appear at `0xdf2fb4/0xdf2fbc` and `0xdf2fc4`.
- If the typed payload is present, **`0xdf2fd4` calls the copy constructor of `std::deque<std::vector<types::Area>>`**. Additional source-area copying begins at `0xdf300c`, guarded by empty/range checks.

This is **stronger than shared string-key occurrence**: the area list can be copied into concrete motion-related preprocessing data. The route is not AI-dirt-specific and does not by itself issue a new cleaning task.

## Relation to stain/extra-clean state

v217 established generated `AiStainCheck` once in `buildNavigateTree` and two `SetExtraCleanArea` instances in `buildCleanSelectedAreas` and `buildFindNearbyMovablePoint`, plus guarded `stain_area_for_logic` and `Areas_Clean_List` accesses. The native calls in v218 are *separate* compiled consumers. Nothing here proves that these generated-tree nodes executed in the required order on the same live Blackboard or that an AI-stain event caused follow-wall/edge-cleaning or `GridmapInit` to dispatch another cleaning task.

**Unproven:** Same-instance Blackboard identity, live calls, autonomous second task dispatch, a physical second floor pass or automatic dock rewash. The old `need_extra_clean` flag is not a unique AI-stain trigger. v215–v216 ReuseTree placeholders and short-circuited ticks remain independent of these call chains.

## Complete source-only reproduction

`X40-R2416-v218-sanitized-analysis-kit.zip` SHA-256 **`2081da24c4ce84b9e05a7ee930b2721bdae3cd170d4d69d5ab98edad68b26f4c`**, **180,375 bytes**, **79 ZIP entries including manifest**, **78/78 per-file SHA-256 hashes**, ZIP CRC and **12/12 focused v218 tests passed on fresh extraction** with the complete v197–v217 native/evidence replay. Includes stdlib-only v197–v218 Python verifier chain, 57 exact new native words, 21 decoded control edges, all four direct caller censuses, mutation tests, source-only report and JSON, and a smaller independent 21-word, four-caller standalone checker. The tests reject altered original ELF, direct call sites, type guards, copy operation, key literal, an additional unanchored direct BL, and existing output overwrite.

**Next:** continue the generated node/Blackboard ownership path into an actual clean task manager or scheduler start API. Do not equate `Cleanbot::preprocess` or an area-data copy with dispatch. Keep experimental CleanGenius gates off: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.
