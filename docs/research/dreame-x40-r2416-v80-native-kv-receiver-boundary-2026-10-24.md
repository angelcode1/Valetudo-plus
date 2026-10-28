# X40 R2416 — v80: native MIOT 4:50 JSON k/v extraction and downstream boundary

**2026-10-24 · Offline static verification on owner-private SHA-pinned original `node_lethe.so`** (`b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`). No live MIOT request or firmware change. Original proprietary libraries, maps and device secrets are not committed.

## Why this matters

v78 confirmed MIOT service **4**, property **50** registers a string-valued get/set/report handler, which calls `SetSwitchMsg`. v79 matched `Publisher<std::string>` and `Subscribe<std::string>` on the exact `STATE_TO_LOGIC` topic, ending at `ReceiveStateListProcessSUB(std::string*)` and RapidJSON `ParseStream`.

**v80 confirms the receiver knows the compact `k` / `v` payload shape and conditionally extracts an integer**. The proof uses original AArch64 opcodes, branch targets and literal VAs rather than keyword similarity.

| Observation | Verified ELF VA |
|---|---|
| Native RapidJSON `ParseStream` | `0x593624` |
| `k` literal resolved via ADRP+ADD → `0xa2f770`; single-character key compare; RapidJSON operator[] | `0x5939c8–0x5939cc`; `0x5939fc`; `0x593a20`; `0x593a40` |
| `v` literal resolved via ADRP+ADD → `0xa059d0`; single-character key compare; RapidJSON operator[] | `0x593a64–0x593a68`; `0x593a88`; `0x593aac`; `0x593acc` |
| Checks RapidJSON numeric integer flag, reads the 32-bit `v`, stores local value | `0x593ad0–0x593ae8` |
| A branch sets local value to zero if extraction is not performed | `0x593b1c` |
| Later sign-extends that value and appends a RapidJSON member to a new document | `0x593c34`, call `0x593c54 → 0x552670` |
| Indirect downstream call; static target unresolved | `blr x2` at `0x5937a4` |

This proves the parser is not *merely* a generic JSON routine. It specifically handles the same one-character keys used in native `{"k":"SmartHost","v":1}` settings messages. **It does not establish which runtime consumer receives the decoded/reformatted pair, or that it reaches the three integer Blackboard setters.** A malformed/missing value branch assigning zero does not justify sending altered native payloads.

## Important negative direct-call inventory

The original `node_lethe.so` has a single PLT target for `ancp::StateShowAndSave::SyncStateChange(...)` at `0x275420`. Scanning **all direct BL instructions** in the pinned ELF's `.text` finds exactly four callers: `0x5842a4`, `0x584348`, `0x584698`, and `0x58473c`. All four are inside the separate `AvaNodeRoute::WritePropIntProcessSUB(ava_msg_write_prop_int*)` handler identified in v76. There is **no direct call** to this PLT from `ReceiveStateListProcessSUB`.

This is *not* a proof of unreachable code: a dynamic callback or further message may still invoke the synchronizer. In particular, the local `0x552670` helper from `0x593c54` is a RapidJSON member append routine, **not** the missing direct call to `SyncStateChange`. The callback or other recipient and station-side live Blackboard instance remain unproven.

## Offline verifier

The sanitized user-provided `X40-R2416-v80-sanitized-kv-receiver-20261024.zip` contains a Python-stdlib-only verifier, this report and a README, **not** the owner's original firmware evidence ZIP. Against the SHA-pinned private source `X40-R2416-v62-readonly-20261023T051829Z.zip`, it checks exact instruction anchors, key strings, resolved AArch64 ADRP/ADD and PLT targets, a direct-call inventory over the full ELF text, and rejection of 22 deliberate instruction/string mutations.

```text
X40_V80_MIOT_STATE_TO_LOGIC_KV_KEYS_STATIC_PASS
X40_V80_SIGNED_INT_VALUE_EXTRACTION_STATIC_PASS
X40_V80_JSON_REWRITE_HELPER_BOUNDARY_STATIC_PASS
X40_V80_DIRECT_SYNCSTATECHANGE_CALLS_ONLY_INT_PROP_STATIC_PASS count=4
X40_V80_PINNED_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=22
LIMIT: indirect destination of rewritten k/v, shared runtime Blackboard and physical reclean/rewash still unproven
```

**Next research task:** identify the indirect call/receiver and its owner after `ReceiveStateListProcessSUB`, determine if and when the corresponding key/value modifies the same Blackboard read by `SweepStationContorl::TurbidityRecleanAndRewashSet()`, and trace genuine turbidity → physical extra wash separately. Treat `SmartAutoMop=-1` as unknown. Preserve live working v74, `SmartHost=0`, closed `writeGateOpen=false`, launcher and all validated rollback binaries. No device activity or newly guessed MIOT writes needed.
