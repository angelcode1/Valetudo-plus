# Dreame X40 R2416 — v135 correlated stack-state analysis and direct flag-store obligation

**24 October 2026. Offline verification only against owner-private original ten SHA-256-pinned AArch64 ELFs and privacy-preserving actual model-site evidence.** No device I/O, writes, cloud access or hardware commands.

## New verified result

The v134 CFG left ten possible direct stores to `SP+0xBC` in native `node_lethe.so:ProcessModelInfo()`. v135 uses a **forward product-state graph** which tracks last-direct-write classes for `SP+0x98`, `SP+0x100`, and the identity of the last direct `SP+0xBC` store. The graph starts at original function entry and stops at the actual flag read `0x470be4`. Its edges include the source-pinned actual primary model site `site_0x473540`, normal missing-`DEV_MODEL` empty-string path and audited exact-name/regex conditions from v119–v134.

### Correlated source-class outcomes

| Read/test in original native code | Possible last direct source value | Treatment |
|---|---|---|
| `0x470b40` / `0x470b44` (`SP+0x98` / CBNZ) | `ZERO`, `ONE`, **`UNKNOWN_X64`** | Known zero follows fallthrough `0x470b48`, known one branches `0x47170c`; unknown pointer-derived low word permits **both** |
| `0x4710bc` / `0x4710c0` (`SP+0x100` / CBZ) | `ZERO` only | Only the zero branch `0x471108` is followed, subject to inventoried direct writes |
| `0x470be4` / `0x470be8` (`SP+0xBC` / CBNZ) | Ten remaining possible last direct flag stores | Do not claim live result or unique executed writer |

The unknown class comes from the original **overlapping 64-bit pointer-derived** source at `0x47130c`. It is not an integer Boolean. Removing that **source solely as a sensitivity check** leaves only `ZERO` and `ONE` at the `SP+0x98` test, confirming its role. It is retained in the actual model.

Under this bounded direct-CFG model, **every entry-to-flag-read path crosses at least one of the ten inventoried direct flag stores**: cutting traversal beyond all ten makes the read unreachable. A separate reverse reaching-last-direct-store walk gives exactly these ten, with no `ENTRY_UNDEFINED` state and no reachable inventoried zero store. Earlier v124/v125 source-corridor checks provided **locally positive register source coverage** for each of the ten. In this *conditional* model the flag therefore has a positive **direct-store source** on all modeled paths to the read.

**Critical limitation:** this is *not* whole-program alias-aware memory SSA. It does not model all indirect writes, register and pointer aliases, exceptions, cross-function memory effects, other runtime setting changes or dynamic instruction execution. The v124/v125 source-positive coverage is a prior dependency, not a new proof of whole-program register values. **There is no basis for asserting that the running R2416's effective `enable_turbidity` value is true**, selecting one instruction as actually executed, or claiming a dirt-triggered *second physical mop wash*.

The path-sensitive walk enumerates 68,924 abstract node states and 25 distinct abstract source-class combinations at the guard; these are implementation-defined static states, **not hardware events**. **All ten potential last direct writers remain**:

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

## Verifier and repeatability

The separately delivered **sanitized owner-side** ZIP `X40-R2416-v135-sanitized-correlated-flag-paths.zip`, SHA-256 `ff74f02f9f9fc46d92b4e5b49b0de4ded54279310f4ca8117dc3d4f1f5608191`, contains `x40_r2416_v135_correlated_store_reachability_verify.py`, all v112–v134 sanitized Python scripts, complete technical report, aggregate JSON, README, and SHA256SUMS. It contains **no** original vendor ELF, APK, native disassembly, private model string, configuration, secret, map, or hardware-command data.

Run the owner-held private ELF ZIP and prior owner-produced *sanitized* model evidence locally:

```sh
unzip ~/Downloads/X40-R2416-v135-sanitized-correlated-flag-paths.zip -d ~/Downloads
cd ~/Downloads/x40-v135-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v135_correlated_store_reachability_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

**Verified from a clean ZIP extraction:** archive CRC/manifest integrity; all ten original private ELF SHA-256 pins; v134 source-corridor, overlapping-width stack-source and model-pruned-graph checks; ten direct flag-store source pins; SP98/SP100 symbolic branch classes; all-path direct-store obligation; no unsupported writer exclusion; **27 independent original source-instruction single-byte mutations** refused by opcode-specific checks, independently of full-file hashes.

```text
X40_V135_TEN_ORIGINAL_ELF_PINS_AND_V134_REGRESSION_PASS sites=10
X40_V135_OVERLAPPING_SP98_PATH_CLASSES_PASS zero=1 one=1 unknown_pointer=1
X40_V135_SP100_PATH_VALUE_PASS zero_only=true
X40_V135_DIRECT_FLAG_STORE_OBLIGATION_PASS all_modelled_paths=true
X40_V135_TEN_POSITIVE_SOURCE_CANDIDATES_REMAIN_PASS last_writers=10
X40_V135_INDEPENDENT_NATIVE_SOURCE_MUTATIONS_REJECTED count=27
LIMIT: no unique executed writer, live turbidity value, or physical rewash proven
```

**Next evidence gap:** no uniquely executed native writer can be deduced from those graph states. A low-impact authorized **read-only effective native Blackboard state** could determine actual `enable_turbidity`, though it would still not identify the last executed instruction or prove extra physical washing. No collector or live instrumentation is performed or included in this run.

**Safety preserved:** last operator-confirmed working Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher and rollback backups intact. Robot, executable Valetudo code and GitHub `master` unchanged.
