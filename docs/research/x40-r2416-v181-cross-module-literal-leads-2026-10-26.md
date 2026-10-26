# X40 R2416 v181 — verified live native-module leads

**Date:** 26 October 2026. **Scope:** source-grounded analysis of the user's successful v180c read-only loaded-module topic report. This is an additive research checkpoint, not a runtime patch, firmware module, or CleanGenius activation.

## Grounded v180c observation

The user-run v180c collector probed 105 distinct mapped files in one selected native process with one SSH session. It reported 105 scanned files, no read errors, all three exact topic-string probes readable, and a complete probe. Input SHA-256: `a8e5e6bc8df39af518f3523c0818462cd26df7838b95989c24772ab5f444c0f9`.

| Literal | Native modules where exact bytes occur |
|---|---|
| `AI_STAIN_CLEANING` | `node_laser_transfer.so`, `node_lethe.so` |
| `now_stain_cleaning_id` | `liblethe_route_nodes.so`, `node_lethe.so` |
| `WR_PROPI` | `node_health_lethe.so`, `node_lethe.so`, `node_msg_cvt.so`, `node_signal.so`, `node_speech_control.so` |

**Priority 1:** `node_laser_transfer.so` contains `AI_STAIN_CLEANING`, making it a candidate receiver/forwarder of the typed stain-ID topic proved in `node_lethe.so` (v178). It is **not** yet a verified subscriber.

**Priority 2:** `liblethe_route_nodes.so` contains `now_stain_cleaning_id` and may hold code that reads or writes the Blackboard entry. It is **not** yet a verified writer.

**Independent bridge lead:** Other modules contain `WR_PROPI`, especially `node_msg_cvt.so`; no actual publisher or MIOT bridging edge has been demonstrated.

## Deliverable: safe two-module follow-up

Offline ZIP: `X40-R2416-v181-sanitized-two-module-native-followup.zip`, SHA-256 `8dc779c778a8d2335d01637d2dd946728fb025a8a52ef6602014358fa7a19290` (distributed privately in the ChatGPT research conversation). The self-contained kit includes a read-only, one-SSH-session collector for the **two** allowlisted mapped original ELFs, a local-only AArch64 literal/adjacent `ADRP+ADD` analyser, separate synthetic tests, this evidence interpretation, and file checksums. Its **25 offline tests passed** and clean extraction/checksum replay passed. Those tests do not establish real native subscriber or Blackboard-write behavior.

The collector saves any user-run original ELFs in a restricted local folder on the user's Mac; original native binaries are **not included in this commit or distributed in the ZIP**. It optionally creates a sanitized metadata-only xref JSON. Direct adjacent address references—even if subsequently found—are **not** proof of a typed Subscribe callback, Blackboard Set, or initiated second pass.

## Gate for further investigation

After a user-run v181 collection: trace the `AI_STAIN_CLEANING` reference(s) in `node_laser_transfer.so` to any actual typed subscriber and callback; independently trace `now_stain_cleaning_id` references in `liblethe_route_nodes.so` to a real Blackboard setter. Only then look for an output path to the cleaning-task planner and passive corroboration in the v165 floor telemetry.

No direct native reclean decision was recorded in v165 and no sensor-triggered extra floor pass is proven. Literal absence outside the selected mapped process or through nonliteral dynamic topic construction is not excluded.

## Safety/release

Keep last working v74 baseline, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No device changes, feature activation or robot access were performed by the assistant during v181. The v180c input was collected by the user.
