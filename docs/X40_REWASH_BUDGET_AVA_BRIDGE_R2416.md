# X40 R2416 — rewash-count lifecycle and AVA turbidity gate

**Scope:** Offline disassembly of the owner's unmodified, SHA-256-pinned R2416 `liblethe_tactics_tree.so` and `node_lethe.so`. No X40 connection, vendor binaries, MIOT writes, runtime hooks, firmware changes, or Valetudo+ production edits.

## Confirmed `max_rewash_cnt` code references

The *exact* Blackboard key has **five** tactics-library ADRP+ADD code references and **two** AVA references (not just string matches). The tactics library uses a shared internal field at `this+0x678`:

| Tactics routine | Verified compiled handling |
| --- | --- |
| `WashIdleProcess()` | When byte `this+0x19` is zero, writes integer **1** at `this+0x678` and calls typed `BT::Blackboard::set<int>(max_rewash_cnt)`. Exact meaning of the mode byte is unknown. |
| `InitTurbidityCheckInfo()` | On a conditional path (a previously retrieved integer is positive), passes `this+0x678` to a Blackboard-associated helper, alongside the exact key. That helper's read/write direction and the source of the value are not resolved. |
| `WashDonePrecess()` | Reads current `this+0x678` and performs a virtual Blackboard-associated setter on `max_rewash_cnt`. |
| `WashErrorLogicRun()` | In the state-2 path, sets countdown `this+0x674` to **100**, decrements `this+0x678`, and calls typed `set<int>(max_rewash_cnt)`. |
| `WashFloorTubidityCheck()` | In a separate conditional path, also sets countdown to **100**, decrements `this+0x678`, and calls typed `set<int>(max_rewash_cnt)`. |

The wash initialization route is compiled as `WashIdleProcess() → InitWashParam() → InitTurbidityCheckInfo()` (direct BL calls at `0x23d7e4` and `0x23d040`). The two decrements are distinct compiled branches, **not** evidence that both happen during one real wash.

## Cross-library AVA consumption

`ancp::AvaNodeRoute::SendAITurbidityValue()` constructs the same `max_rewash_cnt` key (`0x5cdbb8`) and calls typed `BT::Blackboard::get<int>` at `0x5cdbe8` with output address `sp+0xd4`. The same function has another exact key reference at `0x5cd8cc`.

**After separate status/data checks**, the path at `0x5cdd14` loads the 32-bit stack value and `0x5cdd18` branches away from further numeric/AI-turbidity processing when the value is **nonzero**. A zero value allows that particular processing path to continue. The earlier guards include a separate enable/data flag and a wash-status comparison. The function's compiled gate is **not** an actuator call, not a complete publication trace, and does not establish the validity of a failed Blackboard getter.

This makes a precise **compiled cross-library key relationship**. Whether these exact library components share a Blackboard instance at runtime remains unproven. The name and decrements resemble a rewash budget, but no saturation/lower bound, actual configured limit, or physical rewash restart policy has been demonstrated.

## Reproducible evidence

Pinned binaries (SHA-256):

- `liblethe_tactics_tree.so`: `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`

The offline-only standalone verifier checked **51 fixed AArch64 instructions**, **seven exact key references**, **ten branch destinations**, **both full ELF SHA-256 hashes** and refused a modified ELF at the SHA gate. Synthetic self-test and original-file verification passed. The archived private ELF files remain private; no proprietary binary is in this repo.

Supplementary research: [numeric turbidity-state consumers](./X40_TUBIDITY_STATE_CONSUMERS_R2416.md), [post-decision states](./X40_TURBIDITY_POSTDECISION_R2416.md), [floor-to-threshold call path](./X40_FLOOR_TO_THRESHOLD_R2416.md).

## Hard boundary

**Not proven:** whether the cross-library key is the same runtime state, whether an AVA read leads to a successfully delivered message, whether a positive turbidity comparison sets `r2343_start_rewash`, or whether any such action starts a physical second mop wash.

Keep running Valetudo+ unchanged and `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No new robot testing is required for this finding.
