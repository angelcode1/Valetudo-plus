# Dreame X40 R2416 v220 — production odometry tree tick versus debug TaskManager

**27 October 2026. Offline original-firmware static analysis.** Extends v219 on the research branch and preserves the v195 native-`RobotNode` correction. No robot contact, firmware writes, experimental CleanGenius activation or proprietary binaries, owner-private archives, maps, IPs, configuration or process data committed.

## Original host's real production behavior-tree execution path

In original SHA-256-pinned `node_lethe.so` (`b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`):

- The `AvaNodeRoute` constructor passes its route **Blackboard at `+0x30`**, together with the configured selector wrapper, into `BT::buildTreeFromText` at **`0x3552c8`**. The constructed root is retained at **`AvaNodeRoute+0xf48`** by `str x1,[x0,#0xf48]` at **`0x3552d8`**.
- Production `AvaNodeRoute::OdomProcessSUB` calls `PlanningFuncInOdomProcess` at **`0x3e1028`**. That routine calls `ProcessAiStrategy` at **`0x3e0260`**, `ProcessAiCleanBot` at **`0x3e0270`**, and other obstacle, summon and station processing. These are *handler calls*, not established cleaning-task starts.
- Later in the odometry callback's compiled sequence, **`0x3e1390`** loads the root from the identical **`AvaNodeRoute+0xf48`** field; `0x3e1394–0x3e1398` reads its vtable **`+0x18`** method; **`0x3e139c`** invokes the root by **`BLR`**; `0x3e13a0` retains the returned status low byte.
- Further compiled operations pass the retained tree to `SendMap` at **`0x3e1844`** and `PerfUpdataInfos` at **`0x3e1fcc`**. These are neither a stain→new-task scheduling edge nor proof that the root tick actually ran in a captured session.
- A separate `BtTask::Run` function at **`0x315ed0–0x315ee0`** uses virtual dispatch through an object's pointer and vtable slot **`+0x18`**. Similar virtual ABI structure does *not* establish object identity or show that a `DebugTask` triggers the retained production root.

A bounded direct-BL scan of original host executable VA **`0x2a0000–0x9c0000`** finds **exactly one direct call site each** for `PlanningFuncInOdomProcess` (`0x3e1028`), `ProcessAiStrategy` (`0x3e0260`), and `ProcessAiCleanBot` (`0x3e0270`). The same bounded scan separately rechecks **ten direct calls** to `TaskManager::TasksStackPush`, all previously attributed in v219 to DebugTask creation/reset flows inside carpet-signal or app-map-edit handlers. Their call sites do not coincide with the three planning/AI sites or the production root's indirect tick.

**Critical inference boundary:** This is compiled ordering and wiring. Guards and branches may skip the sequences. No live tick trace, proof of matching Blackboard object at separate node executions, AI-stain-changed state, production new-task enqueue or physical additional floor clean was captured. An exhaustive indirect-callback, cross-ELF, or other-scheduler exclusion has *not* been done. The two AI processing functions' names do not prove they dispatch a clean task.

## Reproducibility

Complete source-only `X40-R2416-v220-sanitized-analysis-kit.zip`, **SHA-256 `e88521a11729c88fbad956c55f15662674a4bc0e61345a016e8d9e3b6e9fdac2`**, **203,263 bytes**; **91 entries including SHA256SUMS**. A fresh extraction passed ZIP CRC, **90/90 SHA-256 file checks** and **all 12 focused v220 tests**, including full original-private **v197–v219 regression replay**. Python 3 stdlib-only. New verifier: **32 original AArch64 words, seven decoded direct BL targets, three single-site planning/AI direct-BL censuses, all ten inherited debug pushes**, and mutation tests for the retained-root store/load, virtual call, status, AI calls, target/census mismatch, private-output redaction and overwrite refusal. A smaller original-ELF checker independently passed **16 representative instruction anchors, three API singleton census checks and ten debug task pushes**.

**Next offline research:** analyze concrete Blackboard values/ports and gate behavior *inside* `ProcessAiStrategy` and `ProcessAiCleanBot`, and link a stain-caused state update to an actual production tree task-transition or command publisher. Neither the production tick alone nor a generic CleanList interface establishes CleanGenius recleaning or dock rewash.

Maintain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `writeGateOpen=false`. No change to `master`, robot or current Valetudo+ installation.
