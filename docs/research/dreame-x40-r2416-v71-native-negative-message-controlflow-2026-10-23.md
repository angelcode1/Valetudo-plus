# X40 R2416 v71 — SmartAutoMop / SmartAutoWash negative-message control flow

**Date:** 2026-10-23. **Scope:** read-only, offline verification against the owner's SHA-pinned R2416 `node_lethe.so`. The original ELF is intentionally excluded from GitHub.

## Objective

Restore native firmware CleanGenius dirt-based area reclean and extra mop rewash, preserving original decisions. Manual washing endpoints do not prove automatic CleanGenius functionality.

## New verified fact

In `ancp::StateShowAndSave::SyncStateChange(...)`, native `BT::Blackboard::get<int>` supplies a state that is compared with 1 or 2. The respective branch selects a fixed negative JSON message, processes it, then calls an **indirect callback** through `blr x3`:

| State | Referenced message | Compare / conditional branch | Callback |
|---|---|---|---|
| SmartAutoMop 1 | `{"SmartAutoMop":-1}` | `0x8905fc / 0x890600 -> 0x891cb4` | `0x891cf8` |
| SmartAutoMop 2 | `{"SmartAutoMop":-2}` | `0x890604 / 0x890608 -> 0x891c20` | `0x891c64` |
| SmartAutoWash 1 | `{"SmartAutoWash":-1}` | `0x891808 / 0x89180c -> 0x891afc` | `0x891b40` |
| SmartAutoWash 2 | `{"SmartAutoWash":-2}` | `0x891810 / 0x891814 -> 0x891a68` | `0x891aac` |

The typed Blackboard readers are at `0x8905cc` and `0x8917d8`. The four branches, their ADRP/ADD string references and callback invocations passed instruction-level checks. Eight independent instruction mutations were rejected.

**Crucial limit:** Those messages are state-dependent *callback inputs*, **not proof of persistent MIOT 4:50 configuration values**. The callback target and transport have not been established. The user's earlier cached `SmartAutoMop=-1` reading must remain labeled unknown; this analysis does not resolve why it was returned or authorize writing guessed values.

Earlier v69 evidence of local zero-normalization remains valid. R2416's `special_push_clean_dish` producer and the causal route from turbidity to a second physical dock wash are unresolved.

## Safe next field observation

The v70 branch implements `GET /api/v2/robot/clean-genius/native-settings`: one on-demand MIOT `get_properties(4,50)` which bypasses `parseAndUpdateState()`, avoiding a **direct** SmartHost auto-disable action. Unlike it, `GET /api/v2/robot/state` invokes the legacy parser and may write `SmartHost:0`. Concurrent routine polls can still do so with default policy.

After deployment of a separately tested, reversible v70+ build, the downloadable v71 host probe performs **only GET** on `/clean-genius/native-settings` and `/clean-genius/status`, and emits only allowlisted observations. No v71 robot probing or deployment was performed.

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, and keep the separate observe-only SmartHost-preservation flag off by default until a controlled test with rollback. Do not normalize `-1/-2` into `0`, or conflate native message state with verified automatic wash/reclean.

## Reproduction

The downloadable sanitized v71 verifier accepts the private `X40-R2416-v62-readonly-20261023T051829Z.zip` and `--self-test`. It validates the full `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, native comparisons, branch targets, referenced literals and four indirect callbacks. It contains no vendor library bytes, credentials, device addresses or private configuration.

**Source status:** v71 static research and offline tests only. No activation, firmware edits, robot commands, or startup-optimization changes.