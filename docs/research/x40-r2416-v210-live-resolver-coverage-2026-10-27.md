# X40 R2416 v210 — live resolver collection and coverage limitation

**27 October 2026 | read-only offline analysis of the owner's uploaded live-collection ZIP.** Based on v209 with the v195 native `RobotNode` correction preserved. No robot command or firmware/Valetudo+ modification; no private ELF, config, logs, maps or PRIVATE ZIP committed.

## Exact uploaded live evidence

Uploaded artifact `X40-R2416-v209-live-resolver-PRIVATE.zip` has SHA-256 **`b5439e44d7286d9f7007f55fd26d326eb68d8dae1f29b62e275795a7255b8a7b`** and **933 bytes**. Its two JSON metadata members pass ZIP CRC/schema/path-safety checks and both record **six remote candidate paths**, **zero newly saved ELF files**, **zero named subtree resources** and **six skipped byte-identical copies of prior collected libraries**. Each of the three names `liblethe_tree.so`, `liblethe_tactics_tree.so` and `liblethe_route_nodes.so` appears exactly **twice** in skipped records. This is **three known binaries encountered as six candidate paths**, not six new libraries.

The manifest reports earlier source-archive checksum checks over 18 entries. Those reported counts and metadata are internally consistent; the **remote SSH session is not independently authenticated** by this ZIP, which contains neither remote path list nor scan transcript. The ZIP excludes all candidate file payloads, so it does not permit independent recalculation of their live-byte digests, although the collector states they were identical to the archived originals.

**Key limit:** Absence of a retained `AiStainMop` file does not establish its absence on the running X40 or failure of the runtime behavior tree. The previous v208 collector filtered plugin files by the `tree_lib` path, matched resources by a strict `AiStainMop` basename and suffix set, scanned to depth five and did not follow symlinks. It did not persist which configured roots existed, per-root scan totals, errors or symlink counts, or the effective native process's working directory. It thus cannot establish complete search coverage.

## Connection to existing native findings

v206 proved `ReuseTree` generates `reuse/AiStainMop`; v207 showed no matching exported native `buildAiStainMop` in the original `liblethe_tree.so`; v208 checked all six originally collected ELFs and the original file-fallback argument; v209 verified `getcwd`, `make_absolute` and `realpath` call sites. **None of these static facts establishes successful/failed live factory registration, final file opened, or AI-stain-caused task dispatch.**

The uploaded v209 live inventory adds a useful *duplicate check*, but **does not close the resource-resolution gap**.

## v210 offline verification and source-only handoff

The v210 source ZIP is **`X40-R2416-v210-sanitized-analysis-kit.zip`**, SHA-256 **`dd7b298a98761f54201317b1d2032dc02cef90a06374356c74bc976091c70d83`**. It contains all v197–v209 stdlib-only verifiers/test sources, plus v210 uploaded-artifact validator, **13 v210 focused tests** and a more informative *opt-in* read-only coverage collector. The 46-entry archive passed clean extraction, ZIP CRC and **45 internal SHA-256 checksum checks**. With the owner's four private input ZIPs available, 13/13 v210 tests pass, including complete v197–v209 replay, mutated live ZIP/metadata rejection, incomplete/unsafe scope rejection, symlink/root reporting and refusal to overwrite an existing report.

The new `collect_x40_r2416_v210_scope.py` is a **metadata-only coverage probe**, not another firmware collector. It scans four fixed tree/plugin directories at maximum depth eight, records root presence and symbolic-link counts (never follows symlink targets), and captures only matching `AiStainMop` path names and tree-plugin ELF path names in a separate local **PRIVATE** JSON. Its **SANITIZED** JSON contains only per-root counts and scan failure flags. It **does not download any ELF, XML, config, camera, map or model contents**. It makes no SSH connection unless `--ssh` is explicitly requested. SSH mode was **not** run in this analysis; tests exercised fixture input only.

Even a zero-result full four-root coverage probe would not prove absence from other roots, deeper directories, symlink targets, dynamic factory registration, or cwd-dependent path resolution.

## Next boundary

If the owner wants more evidence, use the v210 kit's optional scope collector and inspect the PRIVATE matching-path JSON in this private conversation. Do not publish PRIVATE output to GitHub. No hardware controls, MIOT/AVA messages, task scheduling, root filesystem writes or experimental CleanGenius activation are required. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. Neither an AI-stain-triggered physical second pass nor dock rewash has been demonstrated.
