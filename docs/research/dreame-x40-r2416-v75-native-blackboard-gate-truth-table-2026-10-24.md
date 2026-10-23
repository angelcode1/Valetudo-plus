# X40 R2416 — v75 native reclean/rewash Blackboard gate truth table

**2026-10-24. Offline static evidence only; no live robot change.** Recovered from the owner-collected SHA-256-pinned original AArch64 ELF `liblethe_tactics_tree.so` (`da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`) and `node_lethe.so` (`b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`).

## Real-device state and boundary

The operator's installed v74 successfully wrote `SmartHost=1` through the *separately authorised single-key* MIOT 4:50 route and immediately read back 1, then restored `SmartHost=0` with immediate readback. The other four firmware settings remained `SmartAutoMop=-1` (unknown), `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`. Subsequently the original launcher was restored, the user rebooted, and the read-only preflight confirmed `writeGateOpen=false`, `SmartHost=0`, and `baselineMatch=true`. **The native writer is closed and need not be reopened for this investigation.**

## Exact native gate function

`StationHandle::SweepStationContorl::TurbidityRecleanAndRewashSet()` begins at `liblethe_tactics_tree.so:0x24e5e0`. It reads separate Blackboard integers:

| Native key | Original ELF literal VA | Native local |
|---|---|---|
| `smart_hosting_switch` | `0x32a968` | host (stack `0x44`) |
| `smart_auto_wash_switch` | `0x340b10` | wash (stack `0x48`) |
| `smart_auto_mop_switch` | `0x340b28` | mop (stack `0x4c`) |

The load at `0x24e7ac–0x24e7b0`, comparisons/branches at `0x24e7b4–0x24e858`, and stores to receiver `+0x688` (`0x24e7d8`, `0x24e820`, `0x24e838`) and `+0x689` (`0x24e7ec`) produce the following **internal eligibility flags**.

| Blackboard host | Rewash eligibility +0x688 | Reclean eligibility +0x689 |
|---|---|---|
| 0 or values other than 1/2 | false | false |
| 1 | `wash === 2` | `mop === 2` |
| 2 | `wash > 0` | `mop > 0` |

Thus, **if and only if the currently observed MIOT settings were mapped unchanged** into these native Blackboard integers, a triplet `host=1, wash=0, mop=-1` would leave **both flags false**. But there is **no proof of unchanged MIOT-to-Blackboard mapping or the effective runtime values**. Do not treat `SmartAutoMop=-1` as off, erase it, or write a guessed replacement.

These two bytes establish **permission to proceed with a native decision**, not that a stain/turbidity event occurred, nor that an extra cleaning pass or physical rewash happened. The earlier v67 proof shows `WashDonePrecess()` also gates `r2343_start_rewash` on `TurbidityResultFail` and `special_push_clean_dish`; marker consumption increments `wash_times` but a complete link to an extra station command has not been established.

## Native negative-value callback provenance

The `node_lethe.so` routine `ancp::StateShowAndSave::SyncStateChange()` loads the `if_need_save_app_state` string (`0x9f78b0`) around `0x88f574–0x88f578`. Near `0x88f624–0x88f684`, the code obtains and copies a **dynamic callable** into function-object storage; `0x891a8c–0x891aac` checks and invokes that local callable on the `SmartAutoWash:-2` message branch, consistent with the earlier v72 callback ABI tracing.

This constrains the origin of the negative-value **message dispatch**, but **does not establish the callable's producer, its receiver, MIOT persistence, or the relationship to native user settings**. The same `if_need_save_app_state` literal occurs in `liblethe_tactics_tree.so`, but this bounded literal occurrence alone does not prove callback registration.

## Repeatable bounded verification

A sanitized standalone stdlib verifier (distributed separately, not a firmware library) loads only the owner's private `X40-R2416-v62-readonly-20261023T051829Z.zip`, pins original ELF hashes, translates file-backed ELF VAs, asserts native literals and bounded instruction word signatures, checks 125 branch truth-table combinations, and rejects 55 deliberate one-byte alterations. It reports:

```text
X40_V75_PINNED_NATIVE_GATE_TRUTH_TABLE_STATIC_PASS cases=125
X40_V75_CALLBACK_LOOKUP_BOUNDARY_STATIC_PASS
X40_V75_SIGNATURE_MUTATIONS_REJECTED count=55
LIMIT: MIOT-to-Blackboard equivalence, callback target, and physical rewash remain unproven
```

No vendor ELF, full native disassembly, private maps, secrets, device identifiers or raw vendor settings are committed.

## Next research gates

1. Trace the firmware-side translation of MIOT `SmartHost`, `SmartAutoMop` and `SmartAutoWash` to native `smart_hosting_switch`, `smart_auto_mop_switch` and `smart_auto_wash_switch` using *signed* value handling.
2. Resolve the `if_need_save_app_state` callback producer/receiver before attributing `SmartAutoMop:-1/-2` message dispatch to persistent settings.
3. Confirm an R2416-reachable source for `special_push_clean_dish`, then the causal link from actual turbidity to `r2343_start_rewash` to a second physical station wash.
4. Retain the **working v74 with its gate closed** and existing v70/v73 executable, launcher and configuration rollback backups. No additional native write is recommended yet.
