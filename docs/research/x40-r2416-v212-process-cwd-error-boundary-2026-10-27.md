# X40 R2416 v212 — observed process cwd versus compiled realpath failure branch

**27 October 2026. Read-only owner-private evidence analysis.** The corrected v195 native-`RobotNode` baseline and complete v197–v211 regression replay are preserved. No new robot command, running Valetudo+ modification, experimental writes, private ELF, original configuration or uploaded process report committed to GitHub.

## Owner process evidence, scope and limits

The owner uploaded v211 **SANITIZED** and **PRIVATE** process-cwd JSON outputs. Exact input SHA-256s were checked offline:
- SANITIZED: `c35bc6085b78875256c0e985227e0d34c1a670e301f9c5e1c79d3b8159e2f255`
- PRIVATE: `b1f2a6cf2dc75342af77e022331837078aea39d1a867af8949ad3696defc9767`

The matching reports record **one process mapping `liblethe_tree.so`**, one readable cwd, no unreadable cwd, and **zero file/symlink hits** for each of four relative names:
`reuse/AiStainMop`, `AiStainMop`, `AiStainMop.xml`, `reuse/AiStainMop.xml`.

The concrete **cwd and process identifier are redacted** in this public report and the output JSON; their values remain only in the owner's private upload. The reports indicate no SSH stderr warning, file-content collection or robot modification. They are user-provided metadata, not an independently authenticated SSH transcript. The v210 four-root scan and prior six-ELF export census remain separate bounded negative evidence, not a global proof that no native builder or XML exists.

## New static original-ELF evidence

The original SHA-pinned `libbehaviortree_cpp.so` (SHA-256 `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`) has an explicit **conditional error path** for `filesystem::path::make_absolute()`. v209 already proved `realpath()` at `0x733bc`, its result retention at `0x733c0`, and the null branch at `0x733dc→0x73874`.

v212 additionally pins **ten exact AArch64 instructions** and **six decoded edges** covering, if that null branch is reached:
- `0x73878` → `__cxa_allocate_exception`
- `0x73880` → `__errno_location`
- `0x73888` → `strerror`
- `0x738b4` → `std::runtime_error` constructor
- `0x738f4` → `__cxa_throw`
- `0x733dc` → conditional branch target `0x73874`

This verifies that a failing `realpath()` can construct and throw a `std::runtime_error`. **No failure, exception, `AiStainMop` file fallback, cache reuse or cleaning-task start was observed on the running robot.** The final pathname actually passed to `realpath` in a real run has not been reconstructed conclusively. An absent relative candidate is not equivalent to a runtime exception.

## Offline replay, privacy and next work

Complete source-only kit `X40-R2416-v212-sanitized-analysis-kit.zip`, SHA-256 **`4801282109f0fda28b81e5ad09d96741cd6f874913a0b25a60458b8d0b9a12bc`**, 55 ZIP entries including SHA256SUMS, **54 internal file hash checks**. A clean extraction passed ZIP CRC, all **12 v212 focused tests** and full v197–v211 native/evidence replay. Tests cover the exact new native words, BL targets, four absent process-relative path results, user-input digest and schema tampering, inconsistent public/private counters, missing process/candidate records, no-private-field output and create-only report refusal. Full zip contains all versioned Python stdlib-only verifier/test sources; private inputs are external.

**Next research:** inspect actual native `AiStainMop` factory registration, aliases or runtime resolver behavior. Do not repeat broad filename searches, or enable experimental CleanGenius writes merely because the candidate paths are absent. The stain→new-cleaning-task edge and independent turbidity→physical dock rewash remain unproven. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. `master` and the robot were not changed.
