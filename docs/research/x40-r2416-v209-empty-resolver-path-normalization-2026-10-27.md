# X40 R2416 v209 — resolver collection disposition and native path normalization

**27 October 2026. Offline, read-only static analysis.** Research descends from v208; the correction that configured `RobotNode` is native (v195) remains in force. No robot commands, firmware writes, runtime Valetudo+ modifications or `master` changes. No private archives, original vendor binaries, personal maps, logs, unredacted settings or credentials are published.

## Uploaded private v208 resolver archive: no new payloads

The owner-uploaded `X40-R2416-v208-resolver-PRIVATE.zip` is **910 bytes**, SHA-256 **`47905a5e9ed7e59a25ef6db1ae07ccb3f5641d439cf3e31a76f018bd7e3907ee`**. Archive CRC passes; it contains **two metadata JSON files and no original file payloads**. The private manifest and sanitized inventory agree:
- **18** original saved-file checksums checked.
- **0** newly collected plugin ELFs and **0** named subtree resources.
- **0** remote path candidates: this was an **offline comparison**, not a live SSH directory inventory.
- **6** byte-identical skip records for **3** already preserved libraries (`liblethe_tree.so`, `liblethe_tactics_tree.so`, `liblethe_route_nodes.so`). These are duplicate hits, not missing files or added implementations.
- `search_not_exhaustive=true` and `robot_changed=false`.

The archive therefore provides **no new AiStainMop implementation to disassemble**. The absence of a saved resource is **not evidence that the installed robot lacks that resource**.

## New original ELF path-normalization instructions

Re-examination of original SHA-256-pinned `libbehaviortree_cpp.so` `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94` identifies:
- `BT::XMLParser::loadFromFile` saves the incoming pathname at `0x6f9ac` and calls **`filesystem::path::getcwd`** from `0x6f9d8` (PLT `0x3a850`).
- Its path-component loop includes `find_first_of` at `0x6fb90` (PLT `0x3a230`).
- It calls **`filesystem::path::make_absolute`** at `0x6fe50` (PLT `0x391e0`).
- That helper calls **`realpath`** at `0x733bc` (PLT `0x3a7c0`), then saves and checks its returned pointer at `0x733c0/0x733dc`. The checked null-result branch goes to `0x73874`.

v208 established that the initial path supplied to the file fallback is the unaltered generated `reuse/AiStainMop` string. v209 now confirms **cwd-aware/path-canonicalization code in the downstream loader**. It does **not** establish the final path opened, an automatic `.xml` suffix, the actual process cwd, that the file fallback was exercised, or that a file exists. The `realpath` call cannot be simplified to an observed on-device resolution.

## Offline replay

Full source-only kit: `X40-R2416-v209-sanitized-analysis-kit.zip`, SHA-256 **`26d3d4734ce41038718d0c16645a82069e43157230fdadb6b117dcec220b862b`**. The kit contains v197–v209 stdlib Python verifiers and tests, the v208 read-only opt-in targeted collector, sanitized v209 research and JSON, instructions and checksums. A clean extraction verified **40 internal SHA-256 checksums**, ZIP CRC, **15 v209 focused tests**, all inherited v197–v208 regressions and original ELF hashes. v209 adds **11 exact original AArch64 word anchors and 5 decoded call/failure branch targets**, with changed-opcode/branch/digest and unsafe-path rejection, and create-only report enforcement.

**Next minimal evidence:** rather than rerunning the same Mac archive search, obtain an **explicitly owner-authorized read-only live inventory of tree plugins and named `AiStainMop` subtree files** from the v208 collector's whitelisted locations, particularly `/tmp/lib/tree_lib`. Its SSH mode is available in the source kit but has not been run here. No maps, cameras, logs, model weights, AVA/MIOT publishes or experiment activation are necessary. Effective native subtree resolution, task dispatch and physical reclean/dock-rewash remain unproven.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.
