# X40 R2416 v77 — SmartWash enum 24 is distinct from CleanGenius Auto Wash

**2026-10-24 · SHA-pinned original AArch64 firmware, offline static analysis only.** No device access, MIOT write, firmware install or vendor ELF redistribution.

## New finding

The v76 candidate producer `MsgClean::SetSmartWashSwitch()` in `node_msg_cvt.so` is **not evidence** of a `SmartAutoWash` (MIOT 4:50) ingress. It sends `enum_write_prop_int=24`; the corresponding native `node_lethe.so` receiver **does not write** `smart_auto_wash_switch`. Instead, it uses `smart_wash_switch` and calls `BT::Blackboard::set<std::string>` with `"true"` or `"false"` according to whether its input integer is nonzero. The v76 `SyncStateChange()` `SmartAutoWash` branch separately writes `smart_auto_wash_switch` through a typed **integer** Blackboard setter. The keys, value types and call targets differ.

Pinned ELF SHA-256:
- `node_msg_cvt.so`: `71c55d905e8e68c4d97d6cc108b251b879cf007ce8515d6f90767dd53d7d0da8`
- `node_lethe.so`: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`

## Verified native instructions

| Source | ELF VA | Fact |
|---|---|---|
| `node_msg_cvt.so` | `0x10a298`, `0x10a2b4`, `0x10a2b8` | `GetJsonValueInt`; load enum **24**; call `AvaNodeMsgCvt::WritePropInt` |
| `node_msg_cvt.so` | `0xbdfc4` | Resolved call to `Publisher<ava_msg_write_prop_int>::publishWithLine` |
| `node_lethe.so` | `0x582278`, `0x582294` | Read incoming message integer and copy to scratch |
| `node_lethe.so` | `0x5824b0`, `0x5824b4` | Compare enum **24**, branch to `0x5858a8` |
| `node_lethe.so` | `0x5858bc`, `0x5858c4` | Read copied integer; choose nonzero vs zero branch |
| `node_lethe.so` | `0x5858c8–0x5858cc`, `0x586af4–0x586af8` | Resolve `"true"` at `0x9cdf20` / `"false"` at `0x9cdf28` |
| `node_lethe.so` | `0x5858e0–0x5858e4`, `0x585900` | Resolve `smart_wash_switch` at `0xa05380`; resolved `Blackboard::set<std::string>` |
| `node_lethe.so` | `0x891724–0x891780` | Separately compares `SmartAutoWash`, selects `smart_auto_wash_switch` at `0xa05080`, calls `Blackboard::set<int&>` |

The `smart_wash_switch` pointer lands inside the longer null-terminated `dynamic_smart_wash_switch` literal (after `dynamic_`), but the passed key is the shorter substring. All names and addresses were verified in the pinned ELF, not guessed from symbol similarity.

## Repeatable bounded verification

A separately provided sanitized, Python-stdlib-only verifier `x40_r2416_v77_smartwash_enum_boundary_verify.py` parses original ELF sections, program headers, `.rela.plt`, `.dynsym` and `.dynstr`; decodes actual AArch64 branch and ADRP+ADD targets; validates pin hashes, instructions, literals, resolved function-call types, and 30 tamper-rejection checks *with the SHA check skipped only for the mutation tests*. Results:

```text
X40_V77_SMARTWASH_ENUM24_PUBLISHER_RECEIVER_STATIC_PASS
X40_V77_BOOLEAN_TO_STRING_BLACKBOARD_STATIC_PASS
X40_V77_SMARTWASH_NOT_AUTO_WASH_TYPE_KEY_STATIC_PASS
X40_V77_GOT_PLT_SYMBOL_RESOLUTION_STATIC_PASS count=5
X40_V77_MUTATIONS_REJECTED count=30
LIMIT: publication/receiver runtime pairing, MIOT 4:50 mapping, auto-rewash and actual washing remain unproved
```

The verifier is included in the user-delivered `X40-R2416-v77-sanitized-smartwash-boundary-20261024.zip`. The original proprietary v62 evidence archive **is not** distributed and must not be committed.

## Boundaries and next work

These are pinned compiled producer/receiver message-type and branch observations; the *runtime* publisher→subscriber pairing and real MIOT `4:50` translation remain unverified. This is a **negative-control result**: do not infer `SmartAutoWash=0` can safely be changed to 1/2 or that it activates a physical second wash. Also do not coerce observed MIOT `SmartAutoMop=-1` to off.

Next offline targets: locate the real MIOT 4:50 `SmartAutoMop`/`SmartAutoWash` handler and callback receiver, prove common live Blackboard identity between native sender and station consumer, and connect `r2343_start_rewash`/turbidity to actual outbound station wash. No new firmware action is warranted.

**Installed state remains verified v74:** native `SmartHost=0`, restored launcher, test `writeGateOpen=false`, baseline unchanged after successful 1→0 native write/readback experiment. Preserve working binary and rollback assets.
