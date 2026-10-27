# Dreame X40 R2416 — v216 native ReuseTree tick short-circuit

**27 October 2026. Read-only, SHA-pinned original firmware analysis.** Continues v215, the v195 corrected native `RobotNode` model and the complete v197–v215 verifier chain. No robot access, firmware writes, CleanGenius activation or change to `master`. No proprietary ELF, private configuration, private collector archive or user process identifiers in GitHub.

## Verified generated order, not just literal names

Original `liblethe_tree.so`, SHA-256 `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`, builds `ReuseTree` at `0x1c9be4–0x1cc8f4`:
- First generated instantiation, `0x1c9c0c`: `Fallback` root, string literal `0x568325`. Root pushed and depth increased (`0x1c9c18–0x1c9c1c`).
- Next generated instantiation, `0x1c9c38`: `AlwaysSuccess`, literal `0x569211`; **first child attached** by `control_parent_addChild` at **`0x1c9c44`**, then pushed.
- Next, `0x1c9c70`: `SubtreeCondition` using `reuse/ActiveRelocalize_Crossline`; **second child attached** at **`0x1c9c7c`**.
- The bounded generated body contains **160 direct `child_node_factory_instantiateTreeNode` calls, 160 `nodes_push_back_child_node` calls, and 159 `control_parent_addChild` calls**. A separate exact native parameter-table census verifies **158 distinct generated `reuse/` children**. They include `reuse/AiStainMop` at parameter VA `0x68a770` and node factory call `0x1cb400`. The exact `AiStainMop` substring appears once in this original tree ELF, in the generated reuse name.

## Verified compiled Fallback execution

Original `libbehaviortree_cpp.so`, SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`:
- `BT::AlwaysSuccess::tick` at **`0x63cf0`** returns constant status **2**: `mov w0,#2; ret`.
- `BT::FallbackNode::tick` at **`0x92960`** invokes the first child through virtual call `0x929f0`, then compares its result with **2** at **`0x92a14`**.
- The equal/success edge **`0x92a18 → 0x92a48`** calls `ControlNode::haltChildren(0)` at **`0x92a50`** and returns success; it does not advance to the next child.
- The separate advance-to-next-child route is **`0x92a1c → 0x92a74`**; child index increments at `0x92a74–0x92a78`.

**Bounded static conclusion:** Assuming normal factory mapping to the inspected built-in Fallback and AlwaysSuccess classes and the generated child attachment order, a tick of the `ReuseTree` root **short-circuits after AlwaysSuccess**. The subsequent 158 reused SubtreeCondition children, including `reuse/AiStainMop`, do **not** receive root-driven normal ticks. This is consistent with `ReuseTree` being a **construction-time cache/placeholder preparation wrapper**, not a tick-time executor of those 158 subtrees. The proposed design purpose is an inference, not a demonstrated runtime event.

**Crucial distinction:** v206/v215 showed that child creation may call `initializeOnce`/`onInit`, and an initial opt-in `reuse/` cache miss can create a null placeholder and return *before subtree resolution*. Therefore the tick short-circuit does **not** imply child constructor/initialization has no effects. Actual live root tick, cache use, native/file resolver activity and Blackboard object identity remain unverified. A different runtime builder, altered child vector, other subtree resource or dynamically constructed path is not ruled out.

## Implication for the CleanGenius goal

The original `liblethe_route_nodes.so` contains other `AiStainMopRegion` node-class names and `AiStainCheck`, but those are not a second generated `AiStainMop` native subtree. The compiled **`stain_area_for_logic` → `AiStainCheck` / `SetExtraCleanArea` → `Areas_Clean_List`** route described by v185 is more promising for actual scheduling. v190 showed `need_extra_clean` also participates in dynamic obstacles and other workflows, so it is not sufficient alone as a dirt-caused extra-pass indicator.

No evidence here proves a runtime stain-triggered task start, physical second floor-clean pass or dock rewash; those remain unverified.

## Offline replay and provenance

Complete self-contained source-only archive **`X40-R2416-v216-sanitized-analysis-kit.zip`**, SHA-256 **`839547a633bc18afe19f26f7659470a91d8ddca6dddceb4f6d9f2fac116aa85e`**, size **156,681 bytes**. It contains **68 entries including a checksum manifest**, with **67 file SHA-256 hashes** verified after fresh extraction, ZIP CRC, **12 focused v216 tests**, all v197–v215 private-evidence regressions, **42 new exact AArch64 words, 18 decoded call/branch targets, 160/160/159 construction census and 158 decoded `reuse/` parameter tables**. Tests reject mutations in the AlwaysSuccess return, Fallback success edge, root type, first/last child attachments, and `reuse/AiStainMop` table. A separate stdlib-only smaller repo checker passed on the original archive: **22 representative exact native words** and **160/160/159** generated calls.

**Next:** follow the **non-ReuseTree** compiled stain→extra-clean planner task transition to the actual task dispatch boundary. No new robot collection required now. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; preserve current Valetudo+ and `master`.
