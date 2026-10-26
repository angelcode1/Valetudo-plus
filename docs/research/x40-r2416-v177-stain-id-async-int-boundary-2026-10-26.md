# Dreame X40 R2416 — v177 stain-ID async integer publication boundary

**2026-10-26. Offline native research.** Original private R2416 `node_lethe.so` SHA-256: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`. No original native binaries, personal maps or credentials are committed.

## Principal finding

Earlier v176 work verified `AvaNodeRoute::CleaningStainIdMsgPub()` reads Blackboard `now_stain_cleaning_id`, skips failed lookup or unchanged values, and queues an asynchronous callback when the ID changes. v177 resolves **the queued callback's type** as `ancp::AsyncDeque::_ProcessAsyncPub<int>(ava::Publisher<int>*,std::shared_ptr<int>)`. This is a typed integer publication path, **not** a demonstrated automatic reclean command.

The compiled store at `0x4b8b9c` places a 32-bit ID into the shared integer payload. AArch64 GOT/relocation evidence:
- `0x4b8bbc` ADRP / `0x4b8bd0` LDR → GOT `0xb79d70` → `AsyncDeque::_ProcessAsyncPub<int>`.
- `0x4b8bc0` ADRP / `0x4b8bd8` LDR → GOT `0xb7f720` → matching bound `std::_Function_handler` invoke.
- `0x4b8bc4` ADRP / `0x4b8be0` LDR → GOT `0xb7c858` → matching bound `std::_Function_handler` manager.
- v176 previously verified `std::deque<std::function<void()>>::push_back` at `0x4b8c14` and a worker wakeup `write` at `0x4b8c48`.

The exact `now_stain_cleaning_id\0` string occurs once in the available ELF; its only **adjacent ADRP+ADD reference** in `.text` is `0x4b8a64`–`0x4b8a68`. This is a **bounded reference form**, not a census of all setters or a claim that no other writer exists.

The constructor separately constructs the `AI_STAIN_CLEANING` literal address at `0x35ec94`–`0x35ec98` and calls `ava::AvaNode::Advertise<int>` at `0x35ecac`. **It has not been established that this advertised topic is the same publisher object used by `CleaningStainIdMsgPub()`.** Its subscriber and any task-planner action also remain unverified.

## Evidence decisions

| Claim | Decision |
|---|---|
| Changed Blackboard stain ID can queue a typed integer publish callback | Verified compiled binding |
| One exact key literal and one adjacent text ADRP+ADD reference | Verified within the stated bounds |
| A separate `AI_STAIN_CLEANING` integer advertisement exists | Verified |
| Writer of `now_stain_cleaning_id` | Not identified |
| Specific topic/object identity between the two publisher sites | Not proven |
| Subscriber that schedules an extra floor-cleaning pass | Not identified |
| Either v165 coarse-area revisit caused by sensor-detected dirt | Not proven |
| CleanGenius safe to enable with manual Valetudo control | Not established |

## Validation and safety

The original-ELF replay passes **19 offline unit tests**, including independently corrupted opcodes/key/relocation sites checked with full-file SHA validation disabled for the specific mutation. Clean ZIP extraction, included-file checksums and replay also pass. The complete standalone offline package and detailed report were delivered in the user's ChatGPT conversation as `X40-R2416-v177-sanitized-stain-id-async-boundary.zip`. ZIP SHA-256: `88a35350a5892dea45048d8e3ddb5930336aaa109e31fdc403a9f9c8359a7b4a`.

Keep the working v74 baseline intact: `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No live native observation, SSH, robot command, feature activation or firmware modification was made in v177. Do not infer physical reclean from queued integer publication.

## Follow-up

Trace the exact publisher object initialized in the native constructor into its stored route field and named topic, then trace a genuine subscriber; separately identify the **writer** of the Blackboard integer before correlating any native decision with floor movement. Do not collect more normal dock observations or enable CleanGenius based on this audit alone.
