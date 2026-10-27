# X40 R2416 v224 — dirty-mop Blackboard consumer and guarded MCU-control publication

**27 October 2026. Offline original firmware analysis; no robot connection.** Based on the owner-private original `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`, extending the verified v223 AI command subscriber and v197–v223 static regression chain. No original ELF, raw configuration, private collector archives, maps or owner process data committed.

## Positive result: the exact key has a second host function consumer

The v223 `AiDetectResultSUB(ava_ai_new_cmd*)` code conditionally handles message code **15** by constructing the exact `ai_set_mop_is_dirty_data` key and calling typed `BT::Blackboard::set<bool>` with a true byte at **`0x5dd010`**.

In the original host, there is one exact key literal at `0xa13488`. A **bounded immediately adjacent, same-register ADRP+ADD** scan of original host executable `.text` identifies **three** direct key references:

- `0x5dcfec` — inside the v223 inbound `AiDetectResultSUB` handler
- `0x5dd024` — inside the same inbound handler, on a separate compiled branch
- **`0x7b8b10` — inside `AvaNodeRoute::SendMopStainCheckCmd()`**

At `0x7b8b0c`, the latter loads the route Blackboard from object offset `+0x30`; `0x7b8b10/14` constructs the exact dirty-mop key; `0x7b8b24–0x7b8b38` contains a guarded *virtual lookup*; and `0x7b8b3c–0x7b8b40` tests the result and branches away on failure to `0x7b8f84`.

This verifies a **compiled consumer of the named key**, not a live read or the key's typed Boolean value. The 3-site census is restricted to one exact ADRP+ADD encoding; dynamically produced names and indirect references remain outside its scope.

## Host dispatch boundary: UpdateOutput and conditional MCU publication

`AvaNodeRoute::UpdateOutput()` makes a direct call to `SendMopStainCheckCmd@plt` at **`0x3db484 → 0x27a720`**. The bounded original host direct-BL census finds **one** call site to this function. Two separately verified calls in the same `UpdateOutput` body are:

- **`0x3db47c → SendAITurbidityValue@plt`** (`0x27c9a0`)
- **`0x3db598 → SendAINewCmd@plt`** (`0x275de0`)

All three have exactly one direct host BL site under this census. Proximity in `UpdateOutput` is **not** evidence of a shared triggering event, or that either previous call caused a subsequent call.

Within the complete compiled `SendMopStainCheckCmd` body, `0x7b8360–0x7b977c`, there are exactly **two direct calls to `AsyncDeque::MultAsyncPublish<_CtrlMcuCMD>`** at `0x7b88d8` and `0x7b8c18`, both targeting PLT `0x275b10`. Additional compiled accesses include one `Blackboard::get<bool>`, two `Blackboard::get<int>`, two `Blackboard::get<std::string>`, and one `Blackboard::set<bool>` call, each with independently verified sites. Do **not** attribute these typed accesses to the dirty-mop key without reconstructing their individual parameters. The two MCU-publication paths are separately guarded, and their runtime payloads, actual subscriber/MCU effects and whether they correspond to a station-wash command are not established.

**Evidence boundary:** This is the first confirmed compiled inbound AI-command Boolean → named Blackboard consumer → guarded potential MCU-control publication interface. It is **not** a complete causal flow proving that inbound code 15 causes either `_CtrlMcuCMD` call. No live AI-stain-triggered new floor-cleaning task, extra physical pass or dock wash was observed.

## Reproducibility and privacy

Complete source-only research ZIP: **`X40-R2416-v224-sanitized-analysis-kit.zip`**, SHA-256 **`ec8bad8c1875a6ef21681b445dc0343cdfc0bc81968c7acdfca59901d54b2fa3`**, **247,502 bytes**, **115 entries including checksum manifest; 114/114 per-file hashes and ZIP CRC verified from a clean extraction**. `verify_x40_r2416_v224.py` checks **37 exact new AArch64 instruction anchors, 11 decoded branches/calls, all three dirty-key xrefs, one direct host consumer caller, two MCU publication sites** plus typed access call censuses, and replays the complete historical original-private native checks. The original source-directory v224 suite passed **11/11 focused tests**; separate clean-extraction full replay status is recorded in the reproducibility handoff. Mutation tests reject inserted otherwise-unanchored host calls or MCU calls as well as altered key, guards, original ELF bytes and output overwrite. Standalone 15-instruction checker independently passed against the original PRIVATE host archive.

**Next:** determine actual MCU command payload conditions and their station-wash/dirty-mop consumer semantics. Separately trace `stain_area_for_logic` and `SetExtraCleanArea` into a real production *new cleaning task* entry. Neither is proven by this study. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; robot, firmware, current Valetudo+ and `master` unchanged.
