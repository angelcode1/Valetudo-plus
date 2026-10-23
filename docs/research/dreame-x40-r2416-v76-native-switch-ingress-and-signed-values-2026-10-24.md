# X40 R2416 v76 — native AVA state sync → Blackboard switch writers

**2026-10-24, offline-only; no robot access or firmware changes.** Original pinned `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.

## New direct native bridge

Within `ancp::AvaNodeRoute::WritePropIntProcessSUB(ava_msg_write_prop_int*)`, calls at ELF VAs `0x5842a4`, `0x584348`, `0x584698`, and `0x58473c` target the named PLT entry for `ancp::StateShowAndSave::SyncStateChange(std::string const&,std::string const&,std::string const&)`. Nearby branches also invoke `DeviceMsgFromAppDeal::SyncDeviceMsgChange`. This is direct native AVA write-property → state synchronizer evidence, **not proof of MIOT 4:50 → AVA ingress**.

`SyncStateChange()` (VA `0x88dab0`) compares three setting-name literals and invokes typed `BT::Blackboard::set<int>` for the corresponding native keys:

| Setting | Native Blackboard key | Typed setter VA |
|---|---|---|
| `SmartHost` (literal `0xa2f7a0`) | `smart_hosting_switch` (`0x9d3f60`) | `0x890360` |
| `SmartAutoMop` (`0xa2f7b0`) | `smart_auto_mop_switch` (`0x9d62a0`) | `0x890508` |
| `SmartAutoWash` (`0xa2f858`) | `smart_auto_wash_switch` (`0xa05080`) | `0x891780` |

The SmartHost branch performs unsigned `cmp w0,#2; b.hi` at `0x89032c–0x890330`: only 0, 1, and 2 reach its typed setter on this path. The *nonzero* Auto Mop and Auto Wash paths use `cmn w0,#2; b.lo; str wzr,[sp,#0x98]` (`0x8904d4–0x8904dc` and `0x89174c–0x891754`). For signed -1 or -2, unsigned carry is set and the value is normalized to zero **before** the setter. This is not a generic negative-value clamp: -3 takes a different branch.

For **incoming zero**, `Blackboard::get<int>` reads the *old* value (mop `0x8905cc`, wash `0x8917d8`). Old value 1 branches to native generated `{"SmartAutoMop":-1}` at `0x891cb4` or `{"SmartAutoWash":-1}` at `0x891afc`; old value 2 similarly branches to `-2` messages at `0x891c20` and `0x891a68`. Four PC-relative branches were verified against original instruction encodings.

**Crucial limit:** this establishes deliberately generated **outgoing negative state notifications** on this function's zero-value transitions; it does **not** explain the source/persistence of the owner's MIOT `SmartAutoMop=-1` setting or establish that the native callback reaches MIOT. Neither MIOT 4:50 ingress equivalence nor live writer/reader Blackboard identity across `node_lethe.so` and `liblethe_tactics_tree.so` is proven. Native eligibility is still distinct from real dirty-floor sensing and an extra physical wash.

## Repeatable verification

A separately packaged sanitized Python verifier (`x40_r2416_v76_state_switch_ingress_verify.py`) checks the SHA-pinned original ELF's file-backed addresses, source/callback instruction words, named literals, signed-value cases and 53 deliberate tamper rejections. Tested result:

```text
X40_V76_AVA_WRITE_PROP_TO_SWITCH_SYNC_STATIC_PASS calls=4
X40_V76_PINNED_SMART_SWITCH_BLACKBOARD_SET_STATIC_PASS keys=3
X40_V76_SIGNED_NEGATIVE_NORMALIZATION_STATIC_PASS cases=7
X40_V76_PRIOR_VALUE_NEGATIVE_CALLBACK_BRANCHES_PASS branches=4
X40_V76_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=53
LIMIT: MIOT 4:50 ingress, shared runtime Blackboard, callback transport and physical rewash not verified
```

## Current operational status

The user's tested Valetudo+ v74 remains unchanged: prior `SmartHost: 0 → 1 → 0` readbacks succeeded; after launcher restoration and reboot, `writeGateOpen=false`, `SmartHost=0`, `baselineMatch=true` were confirmed. Auto Mop is still `-1` (unknown), Auto Wash `0`. No new settings write, firmware, launcher edit or reboot is required.

Next trace: identify MIOT 4:50 → `ava_msg_write_prop_int` producer; callback receiver/persistence; station writer/reader Blackboard identity; and `special_push_clean_dish`/turbidity → rewash marker → real dock wash. No vendor binary, map, secret or full disassembly is committed.
