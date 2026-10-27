# X40 R2416 v214 — native plugin discovery and registration ABI

**2026-10-27. Offline, read-only, SHA-pinned R2416 native research.** Extends corrected v195 native `RobotNode` and the full v197–v213 regression chain. No robot activity, firmware write, experimental feature enablement, private ELF/ZIP/config/map or personal process metadata committed.

## Primary verified finding: exact compiled loader route

The original `node_lethe.so` (`b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`) in `AvaNodeRoute`:

- Calls `opendir` at `0x350e14`, branches on failure at `0x350e1c`, calls `readdir` at `0x350e5c` and `closedir` at `0x350e6c`.
- Uses `dirent.d_name` at `0x350e30`, `strlen` at `0x350e38`, substring start `strlen−3` at `0x350e44–0x350e48`, and `strcmp` at `0x350e4c` to filter **`.so`** filenames (exact literal `0x9d5a78`); matching branch `0x350e50→0x351d84`. This is a filename filter, not an exhaustive recursive scan.
- Builds a path through `GetFilePath` at `0x350ed8` and passes it to `BT::BehaviorTreeFactory::registerFromPlugin` at **`0x350f00`**. The subsequent `builders()` count comparison at `0x350f20–0x350f2c` concerns the **ordinary node-builder** map and must not be interpreted as the tree-builder count or as proof of live success.

The original `libbehaviortree_cpp.so` (`665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`) implements `registerFromPlugin` at `0x5cc00`. It constructs a `BT::SharedLibrary` (`0x5cc40`), calls `load` (`0x5cc50`), constructs exact literal **`BT_RegisterNodesFromPlugin`** (`0xaca80`), checks `hasSymbol` (`0x5cc7c`), conditionally branches if missing (`0x5cc98→0x5cd44`), otherwise calls `getSymbol` (`0x5ccb8`) and invokes the resolved callback with the factory at **`0x5ccd4–0x5ccd8`**.

These are statically compiled control-flow paths; actual runtime plugin loading and invocation were not independently observed.

## Plugin API audit: all three identified native tree plugins

Three distinct native plugin basenames were observed in the owner-supplied v210 scoped inventory; the user-private original firmware archive preserves exact SHA-pinned binaries for each. Each exports `BT_RegisterNodesFromPlugin`. Bounded ELF64 `.dynsym` function import/export and relocation checks show:

| Original plugin | Export entry point | Import `registerTreeBuilder` | Import ordinary `registerBuilder` |
|---|---|---|---|
| `liblethe_tree.so` | Yes | **Yes** | No |
| `liblethe_route_nodes.so` | Yes | **No** | Yes |
| `liblethe_tactics_tree.so` | Yes | **No** | Yes |

The one tree-builder import and two node-builder imports are accompanied by actual imported-function relocation entries. The inherited v213 verifier again checks **199/199 direct name→relocated callback registrations** in `liblethe_tree.so`; none is named `AiStainMop`. Thus **neither of the other two identified plugins directly imports the same tree-builder API**. A direct `registerTreeBuilder` registration in those two through a normal imported C++ call is unsupported.

**Proof limit:** This does not exclude `dlsym`/other indirect invocation, factory aliasing, other plugin libraries, runtime changes to the factory map, or XML file fallback for `reuse/AiStainMop`. The live loader result has not been authenticated with a runtime factory dump. No AI-stain-triggered second cleaning task, physical reclean or dock rewash is established.

## Reproducibility

Complete **source-only** ZIP: `X40-R2416-v214-sanitized-analysis-kit.zip` — SHA-256 **`cecec623d89b38324c654eeeaaeb14678e0830885311a2343997c191fb75eaee`**. It has **58 entries including SHA256SUMS**, **57 per-file hashes** verified after fresh extraction, complete v197–v214 stdlib Python verifier chain, sanitized report/JSON, and focused tests. **All 11 v214 focused tests passed**, including complete inherited regression, five ELF SHA-256 pins, **45 exact new native instruction words**, **17 decoded branch/call edges**, three ABI exports/imports, altered ELF/opcode/edge tests, simulated missing export and alternate imported tree-builder API, and create-only output. The independent smaller repo checker passed original evidence (three plugins, 14 representative instructions). No original proprietary binaries or PRIVATE ZIPs included.

**Next:** inspect alias/dynamic registration and specifically the native builder-versus-file-fallback decision in `SubtreeConditionNode::onInit`. When static analysis reaches a limit, a minimal passive runtime factory result would be more meaningful than repeated directories/filename searches. Preserve disabled CleanGenius gates: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. `master` unchanged.
