# X40 R2416 v219 — original host TaskManager and route debug executor boundary

**27 October 2026. Original firmware SHA-pinned offline analysis only.** Continuing the corrected v195 native-`RobotNode` model and full v197–v218 replay. No robot commands, feature activation, firmware writes or public private-ELF/config uploads.

## Compiled task-stack producer

Original host `node_lethe.so`, SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, **defines** `TaskManager::TasksStackPush(BtTask&&)` at `0x316ee0`. Its non-reallocation native path constructs a task entry at `0x316f14`, moves/copies the queued task and advances the deque end at `0x316f90–0x316fa0`. Other allocation/refcount cases also exist. This is a genuine task-stack insertion implementation, unlike merely writing `Areas_Clean_List` to a Blackboard.

The bounded AArch64 direct-BL scan of host executable VA `0x2a0000–0x9c0000` found **10 calls** to `TasksStackPush` PLT `0x27afd0`, **10 calls** to `TasksStackReset` PLT `0x27e0f0`, and **10 calls** to `DebugTask` constructor PLT `0x275ba0`. At all ten observed push call sites, a `TaskStackReset` call appears **12 bytes before** and a `DebugTask` constructor call **48 bytes before** on that same compiled code path. The callers are five sites inside `AvaNodeRoute::SignalCarpetProcessSUB` and five inside `AvaNodeRoute::AppEditMap`.

| Host caller | DebugTask constructor | Reset | Push |
|---|---|---|---|
| SignalCarpetProcessSUB | 0x51ad38 | 0x51ad5c | 0x51ad68 |
| SignalCarpetProcessSUB | 0x51b448 | 0x51b46c | 0x51b478 |
| SignalCarpetProcessSUB | 0x51b9f8 | 0x51ba1c | 0x51ba28 |
| SignalCarpetProcessSUB | 0x51be24 | 0x51be48 | 0x51be54 |
| SignalCarpetProcessSUB | 0x51cc3c | 0x51cc60 | 0x51cc6c |
| AppEditMap | 0x6e2678 | 0x6e269c | 0x6e26a8 |
| AppEditMap | 0x6e2cb0 | 0x6e2cd4 | 0x6e2ce0 |
| AppEditMap | 0x6e3310 | 0x6e3334 | 0x6e3340 |
| AppEditMap | 0x6e4864 | 0x6e4888 | 0x6e4894 |
| AppEditMap | 0x6e5328 | 0x6e534c | 0x6e5358 |

These are **static direct callers only**; neither their names nor their count prove that no other indirect/cross-library task producer exists.

## Compiled task-stack consumer

Original route plugin `liblethe_route_nodes.so`, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`, imports the stack's `TasksStackEmpty`, `GetStackFrontTask` and `TasksStackPop`. Each has exactly **one direct BL site** inside `debug_mode::BtTaskExecutor::tick`, according to a bounded direct scan of executable VA `0x4526f0–0xf9c0b0`:

- `0x6a87b8` → `TasksStackEmpty()` PLT `0x44c390`, with test and branch `0x6a87bc–0x6a87c0`.
- `0x6a87f4` → `GetStackFrontTask()` PLT `0x449130`, followed by an indirect virtual task method call `BLR` at `0x6a8800`.
- `0x6a8814–0x6a8818` tests return status and conditionally loops; `0x6a8820` → `TasksStackPop()` PLT `0x449df0` on the other branch.

This identifies an **enqueue/execute/pop debug task mechanism**, not the main autonomous floor-cleaning scheduler. No on-robot stack activity, actual TaskManager push, live condition or task output was measured.

## Relationship to v217–v218 and remaining proof gap

v217 established `AiStainCheck` and `SetExtraCleanArea` are built in separate native tree builders, with a guarded stain-area/list interface; v218 established typed list copying in `Cleanbot::preprocess` and a direct follow-wall/edge-cleaning caller. No direct `TasksStackPush` site identified here belongs to those two stained-area/list functions. This is a **bounded negative**, not a proof that stain processing never reaches task dispatch indirectly, via a different scheduler or runtime alias.

Do **not** equate debug TaskManager stack operation with a second physical pass or AI-stain-triggered new cleaning task. Same-instance Blackboard identity, live execution ordering, stain→new-clean-task entry, actual second cleaning, and dock rewash all remain unverified.

## Reproduction and safety

Source-only package: **`X40-R2416-v219-sanitized-analysis-kit.zip`**, SHA-256 **`62b70968c651e9f14bf67191a0c7263692942c6a20bef31ba5ba00b3268ea6ab`**; **85 ZIP entries**, **84/84 verified per-file hashes**, ZIP CRC, **12 v219 focused tests** and the full v197–v218 original-native/private evidence regression replay passed from a fresh extraction. Includes **51 new exact native instruction words**, **33 bounded direct BL caller sites**, mutation tests for altered constructor/reset/push, virtual task run and an injected unanchored push; output redaction and create-only report refusal tested. Python 3 stdlib only. No owner-private ELF, ZIP, JSON or raw config redistributed.

**Next research** should distinguish the primary production cleaning-task state machine and root task transitions from this debug queue, then look for a causal stain-triggered task-start edge. Do not repeat already-closed directory scans or enable experimental CleanGenius. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; leave `master` and robot unchanged.
