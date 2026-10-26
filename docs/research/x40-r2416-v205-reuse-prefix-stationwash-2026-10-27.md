# X40 R2416 v205 — native `reuse/` opt-in and StationWash cache boundary

**27 October 2026 — offline/read-only, exact original ELF SHA pins.** Continues v195's corrected native-`RobotNode` model and the full v197–v204 native turbidity/cache research. No robot interaction, unredacted configuration, original ELF, map or proprietary blob is committed.

## New result: cache opt-in is explicitly path-sensitive

The original `libbehaviortree_cpp.so` (`665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`) implements a literal **`reuse`** marker within `BT::SubtreeConditionNode::onInit()`. Its file-path parser invokes `std::string::find_last_of(".")` at `0x7584c` and `find_last_of("/")` at `0x75870`. For a path with a slash, `0x75894→0x75ca0` extracts the preceding component and `0x75cfc` compares it against literal `reuse` at `0xad908`; `0x75d00–0x75d08` sets reuse flag `w28` from that equality check. Path parsing after the slash continues separately.

For **plain `StationWash.xml`**, the no-slash path `0x75898–0x758a4→0x76008` computes `w28=0` for an ordinary nonnull filename buffer (`0x76020–0x7602c`). `0x759d0` then skips the pre-insert lookup. On an ordinary filename-key miss, `0x75a18→0x75dd8` clears the post-build insertion flag and `0x75bc0` bypasses storing a freshly built tree in the cache. Therefore **a plain-path miss does not by itself populate this static cache**.

An explicitly prefixed **`reuse/StationWash.xml`** path would match the marker and could create a null placeholder on a map miss (`0x759f8→0x763f0`, initialization `0x764b8`); its subsequent null-entry build sets the cache-result flag and can populate the tree pointer (`0x75b78–0x75b7c`, `0x75c98`). This is a compiler-path inference, not a recorded robot event.

**Important nuance:** The plain filename still looks up the normalized key and can **reuse an already populated entry** created by an earlier opt-in caller. Absence of its own cache opt-in is **not** a proof that a plain-path node can never take a cache-hit branch. Dynamic path construction and alternative runtime node registration are unexcluded.

## Generated native RobotNode specifies the unprefixed StationWash

The separately pinned original `liblethe_tree.so` (`9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`) builds a native `SubtreeCondition` child at `0x30ee3c–0x30ee58`. Its two-pair parameter vector at `0x6f8350` has **`expand_in_logger=true`** and **`subtree_file_path=StationWash.xml`**. Original C-string pointers/lengths, factory call and key literals were independently verified. The original tree binary includes other explicit `reuse/` child names, including `reuse/AiStainMop` and `reuse/CleanSelectedAreas`, but no contiguous `reuse/StationWash` or `reuse/StationWash.xml` string. This is a bounded static scan, not an exhaustive refutation of runtime-generated paths.

**Interpretation correction to v203/v204:** A generated unprefixed `StationWash.xml` child does not itself opt into creating the raw-pointer cache on an ordinary miss. The previously described use-after-free/stale-Blackboard hazard requires additional preconditions including a populated matching entry and an incompatible owner lifetime. Nothing proves a live stale cache, use-after-free, crash or second physical wash.

## Verification and next action

The owner-private ZIPs were used as read-only inputs to the complete v197–v205 Python 3 stdlib source-only verifier. v205 verifies **63 exact original AArch64 instruction anchors across two libraries** and **19 decoded branch/call edges**, exact `reuse`/separator literals, native `StationWash` parameter pairs, and the absence of a contiguous `reuse/StationWash` literal. **11 focused tests passed** (binary and instruction/edge tamper, changed parameter and create-only overwrite rejection), and all previous v197–v204 regressions passed, including five original native ELF SHA-256 pins and 18+7 collector payload checksums. Clean extraction passed all **26** ZIP per-file checksums. Full archive: `X40-R2416-v205-sanitized-analysis-kit.zip`, SHA-256 **`102f2965bf2f773230f7dfe429ee0f98f0811b1c8eb1191b9c9c933314ae32c1`**.

Next: inspect `reuse/AiStainMop` and other reused child placements, then trace cache lifetime in those **opt-in** subtrees. Separately, resolve route/station Blackboard instance equality and the native AI-stain-to-task-start chain. Neither physical reclean nor R2416 `special_push_clean_dish` eligibility is established. Leave experimental CleanGenius writes disabled, and keep the running robot and `master` unchanged.
