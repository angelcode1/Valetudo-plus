# Dreame X40 R2416 — v48 GlobalHook pre-tick callback audit

**Date:** 2026-10-23  
**Scope:** Read-only offline static code and ELF-relocation analysis of the original SHA-256-pinned R2416 `node_lethe.so`, `liblethe_route_nodes.so`, and the three matching runtime tree libraries. No robot commands, MIOT writes, runtime injection, firmware modification, personal data or proprietary binaries published.

## Executive result

The indirect callback invoked by `AvaNodeRoute::OdomProcessSUB()` immediately before the retained `RobotNode` tree's virtual `executeTick()` is the `route_nodes::GlobalHook` instance's `std::function` callback. **Both inspected original native libraries install a default GlobalHook callback whose invocation handler is exactly one AArch64 `ret` instruction.** This resolves the default callback *implementation*, but not whether a plugin or runtime code can replace it before an odometry callback executes.

There is no evidence here that a normal turbidity threshold triggers rewash or that a second physical dock wash takes place.

## 1. Native callback implementation and initialization

| SHA-pinned ELF | `GlobalHook` default invoke symbol | Compiled body | Singleton initialisation |
| --- | --- | --- | --- |
| `node_lethe.so` | `0x3ec460` | `ret` (`0xd65f03c0`) | `0x3ee780`; installs manager `0x3ee2f0` and invoker `0x3ec460` |
| `liblethe_route_nodes.so` | `0x48ce00` | `ret` (`0xd65f03c0`) | `0x4a2000`; installs manager `0x48d500` and invoker `0x48ce00` |

In both singleton initializer functions, the `std::function` manager and invoker pointers are loaded via symbol-resolved GOT entries and installed into the newly allocated `GlobalHook` object with an `STP` pair. The independent verifier checks **four exact GOT relocations**, the full-byte SHA-256 pins, the invoke/manager symbol sizes, the two `ret` instructions, and the initializer store instructions. This is not merely a string search or an assumption based on the function name.

The existence of two compiled implementations does not prove whether ELF symbol interposition chooses one or the other in a particular process. Both checked defaults have the same no-op semantics.

## 2. Connection to odometry-driven tree dispatch

The verified original `node_lethe.so` `OdomProcessSUB()` code has:

| Address | Compiled operation |
| --- | --- |
| `0x3e1360–0x3e1370` | Read/test singleton `GlobalHook` pointer (lazy initialization detour if null) |
| `0x3e1374` | Read the `std::function` non-null invoker field |
| `0x3e1378` | Form a pointer to the stored callable payload |
| `0x3e137c` | Read `AvaNodeRoute+0x30` Blackboard holder for callback arguments |
| `0x3e1380` | If no callback is installed, branch to a `std::__throw_bad_function_call` path |
| `0x3e1384–0x3e138c` | Load and invoke current callback's function pointer (`blr x3`) |
| `0x3e1390–0x3e139c` | Load retained `AvaNodeRoute+0xf48` root and invoke virtual `executeTick()` |
| `0x3e13a0` | Preserve returned status byte in `w25` |

Thus, **when the singleton retains the compiled default invoker**, this callback does not add a separate operation before the retained tree tick. A missing callback enters the verified exception path; a runtime override could instead perform work, throw, block, or change Blackboard state.

## 3. Verification and strict limits

The standalone `util/x40_r2416_v48_globalhook_callback_verify.py` verifier uses only the Python standard library. It loads the original native files as inert bytes from the user's offline archive, validates all five full SHA-256 pins, checks all three byte-identical runtime tree libraries, and checks that the private `setting.yaml` selects `RobotNode` and `/tmp/lib/tree_lib//` without copying private configuration into the report.

It then verifies dynamic ELF symbols, four GOT relocations, singleton initializer instruction anchors and the odometry callback/`executeTick` instruction sequence. All checks are anchored to the specified R2416 build; they are not applicable to arbitrary firmware revisions. A deliberately altered runtime library is rejected before the instruction checks by the SHA/byte-identity gate.

Expected output marker: `X40_V48_GLOBALHOOK_DEFAULT_CALLBACK_STATIC_PASS`.

**Not proven:** runtime callback identity or assignment history, actual frequency/success of odometry events, the root tree's runtime Blackboard object identity at every descendant, any R2416-compatible alternative producer for `special_push_clean_dish`, normal turbidity-to-rewash marker causality, a physical dock-wash actuation, or functional automatic CleanGenius rewash under Valetudo+.

## 4. Next priority

The next static work should locate direct or indirect writers of `GlobalHook`'s stored callback and bound their potential effects. Then follow the `w25` root-tick status and revisit the model-gated `special_push_clean_dish` producer rather than assuming the default no-op callback establishes end-to-end rewash behavior.

Continue with `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, without live testing or firmware writes. Keep native ELFs and full private configurations out of GitHub.