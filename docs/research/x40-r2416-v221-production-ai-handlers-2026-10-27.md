# Dreame X40 R2416 v221 — production AI mode inputs and asynchronous work queue

**27 October 2026. Offline, read-only SHA-pinned original firmware analysis.** This branch descends from v220, preserves corrected v195 native `RobotNode` and full v197–v220 regression history, and performs no robot access, firmware change, experimental CleanGenius activation, or `master` change. Original proprietary ELF, owner PRIVATE ZIPs, raw settings, paths, process identifiers, network information and maps are **not** committed.

## What the two host production handlers actually read

The original `node_lethe.so` (SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`) defines `AvaNodeRoute::ProcessAiCleanBot` at `0x5cebc0–0x5cfa80` and `AvaNodeRoute::ProcessAiStrategy` at `0x5cfa80–0x5d0050`. Both are called before the retained production behavior-tree tick in the original odometry path (v220); the compiled calls are not evidence of an observed live execution.

**ProcessAiStrategy** accesses its route Blackboard (`AvaNodeRoute+0x30`) and constructs the exact `RobotAiSwitch` key (literal `0x9d4d30), ADRP+ADD `0x5cfacc–0x5cfad0`). Typed `Blackboard::get<int>` is called at **`0x5cfb18 → 0x2746d0`**; subsequent branches and bit decoding inspect that result. It separately builds `current_motion_type` (`0x9edbf0), `0x5cfb98–0x5cfb9c`), performs a guarded virtual lookup and casts a SafeAny string, and compares motion-state data with exact `Followwall` literal `0x9edc28` via string compare calls at **`0x5cfc78`** and **`0x5cfc90`**. The function initializes a local static `Stop` state as well. The flags and string comparisons are native AI-mode/motion logic, not proof of AI stain-driven cleaning-task start.

**ProcessAiCleanBot** constructs `online_pqklfilename` (literal `0xa05e50`, ADRP+ADD `0x5cec20–0x5cec24`) and `ai_model_info` (`0xa05960`, ADRP+ADD `0x5cec78–0x5cec7c`). Guarded Blackboard virtual lookups occur at **`0x5cec68`** and **`0x5cecd0`**, and a typed `Blackboard::get<std::string>` at **`0x5ced94 → 0x27b040`**. On other guarded branches, the original function contains a `std::deque<std::function<void()>>` overflow push helper call **`0x5cf5b0 → 0x278340`**, `std::condition_variable::notify_one()` **`0x5cf148 → 0x2773a0`**, and a descriptor `write()` **`0x5cf15c → 0x278aa0`**. These are compiled asynchronous callback/queue-notification operations; neither execution nor the downstream callback effect is measured, and they are not, by themselves, proof of a motor command or floor-reclean task.

## Verified bounded negative — not a global exclusion

A direct AArch64 `BL` census of **both entire known handler bodies** identified **zero direct calls** to any of the following original targets:

| Queried target | Original target VA |
| --- | --- |
| `TaskManager::TasksStackPush` PLT | `0x27afd0` |
| `AvaNodeRoute::SendAINewCmd` native body | `0x5d1fd0` |
| `AvaNodeRoute::SendAITurbidityValue` native body | `0x5cd770` |
| `BtTask::Run` native body | `0x315ed0` |

The verifier deliberately inserts an **additional, unanchored direct `BL` to TasksStackPush** at a known `NOP` in the CleanBot body, and confirms that the exact negative census fails. The result only covers direct `BL` instructions in those two functions and these exact four targets. **It does not exclude `BLR`/virtual callbacks, other loaded libraries, aliases, eventfd work processing, deferred command publication, or another production scheduler.** Do not infer that AI handlers are inert or that a lack of direct calls means a new clean cannot occur elsewhere.

## Source-only reproducibility and result limit

Full `X40-R2416-v221-sanitized-analysis-kit.zip` SHA-256 **`28d2e493a30851e9baec88e4168576f646bfa530df7cdb78ff2406607d014636`**, **215,356 bytes**, **97 ZIP entries including SHA256SUMS**, **96/96 internal payload SHA-256 checks**, ZIP CRC and **13/13 focused v221 tests passed in a clean extraction**, including the complete v197–v220 original-private evidence replay. Python 3 standard library only, no proprietary original binaries in ZIP. New verification checks **52 exact AArch64 words**, **12 decoded direct `BL` targets**, **nine conditional branch edges**, **five exact key/motion-state strings**, positive queue calls and both negative direct-call censuses. Tests reject tampered keys, typed get, compare, queue notify, descriptor write, injected unanchored direct task push, private data leakage and output overwrite. Smaller standalone checker independently passes **24 representative original instructions, five literals and zero selected direct dispatch calls**.

**Not established:** effective live Blackboard identity and timing across `AiStainCheck`, `SetExtraCleanArea` and these handlers; stain-triggered command publication; new autonomous production cleaning task; second physical floor pass; dock turbidity-driven rewash. The `reuse/AiStainMop` placeholder and root tick short-circuit from v215–v216 remain independently valid bounds.

**Next research:** resolve the asynchronous callback consumers and the actual production clean-command/task-state publisher, rather than repeating filename/ELF exports scans or conflating the debug TaskManager queue with autonomous cleaning. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Robot, Valetudo+ and `master` unchanged.