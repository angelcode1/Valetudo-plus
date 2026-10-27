# Dreame X40 R2416 v215 — reuse cache placeholder and native-builder/file fallback

**27 October 2026. Offline, read-only original-firmware analysis.** Extends v214, preserving v195's corrected native `RobotNode` construction and the full v197–v214 original evidence replay. No robot command, patch, firmware write, experimental CleanGenius enablement, source proprietary ELF, private owner diagnostic archive, process ID or private configuration in this commit.

## Key finding: first reuse cache miss may return without resolving the subtree

Original SHA-pinned `libbehaviortree_cpp.so` (`665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`) `BT::SubtreeConditionNode::onInit()` recognizes a literal `reuse` prefix (VA `0xad908`, comparison `0x75cfc`, flag `0x75d08`). The original `liblethe_tree.so` (`9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`) generates `subtree_file_path=reuse/AiStainMop` at parameter table `0x68a770`. The normalized cache and native-builder key is `AiStainMop`.

On **an initially absent key in the function-static cache**, the compiled prefix-enabled path `0x759d0 → 0x759e8 → 0x759f8 → 0x763f0 → 0x764b0 → 0x764b8 → 0x764bc → 0x75ad4` creates a null `BT::Tree*` placeholder (`str xzr,[x23,#0x40]`) and returns from initialization. **That route does not call a native tree builder or open a subtree file before the return.** This is a conditional static path, not a recorded runtime event.

On a later encounter with an **existing null entry**, `0x75ac4–0x75ac8 → 0x75b78` sets the post-build cache flag and construction may be attempted. Cache contents, actual hit order, initialization flags and tree owner lifetime are unmeasured.

## Explicit native builder lookup and fallback

The earlier interpretation of `0x75b84 cbnz x0` as a "registered native builder versus file" choice was imprecise: `0x75b80` loads **normalized-string length from `[sp,#0xe8]`**, and `0x75b84` tests its nonzero value. The actual `BehaviorTreeFactory::tree_builders()` search follows at `0x75de8`. Native builder lookup misses branch `0x75dfc` or `0x75e5c` to `0x76198`, which builds a diagnostic with the literal ` is not a registered tree` at VA `0xad930` (length 25 at `0x761f4`), and flows to the **file builder** at `0x76244/0x7624c → 0x75b88`. The original path parameter is passed via `x24` at `0x75ba4` to `buildTreeFromFile` at `0x75bb0`. When the native builder is present, the registered callback path eventually invokes `BLR` at `0x75f9c`.

This is important for interpreting the live evidence: **absence of the four candidate names relative to the observed process cwd does not establish that the file fallback was ever invoked.** Likewise, the compiled missing-builder message is not evidence of a live log, exception, crash or failed cleaning task.

## Cross-version native evidence and open question

The verifier rechecks **199 direct registration name→GOT callback pairs** from v213; no matching `AiStainMop` registration exists in that identified plugin, whereas `StationWash` is registered. The exact `AiStainMop` substring occurs once in the original compiled tree ELF, as part of `reuse/AiStainMop`. v214's separate plugin-loader ABI audit and v211–v212 bounded filesystem/cwd negative evidence remain valid. None excludes a dynamically registered alias, external resource, another effective loader location, or additional runtime-built names.

**Not demonstrated:** execution of `AiStainMop::onInit` on the robot, cache placeholder creation at runtime, actual populated cache, effective live factory map, native builder callback or file fallback taking place, any stain→new-cleaning-task scheduler edge, extra physical floor pass or turbidity-triggered dock rewash.

## Verification and source-only kit

Complete package: **`X40-R2416-v215-sanitized-analysis-kit.zip`**, SHA-256 **`a2a3fa4580a1a1011d64c5b698df00e1a34ecef2958928787e0d9beb18d0edd7`**, 63 entries including checksum manifest. **62/62 internal hashes** and ZIP CRC passed from a fresh extraction, together with **all 12 v215 focused tests** and full v197–v214 replay against the owner-private original evidence. v215 independently verifies **46 exact AArch64 instruction words, 19 decoded control-flow edges, the reuse and missing-builder literal strings, one generated AiStainMop path and all 199 native registered name/callback pairs**. Negative tests catch tampered native data/branches/literals, missing registrations and attempt to overwrite a sanitized report.

**Next priority:** trace whether any compiled consumer actually references the `AiStainMop` subtree beyond its ReuseTree placeholder, then focus on the separate real stain→task-dispatch edge. Do not continue broad directory rescans or enable experimental features without runtime causal evidence. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Leave robot, Valetudo+ and `master` unchanged.
