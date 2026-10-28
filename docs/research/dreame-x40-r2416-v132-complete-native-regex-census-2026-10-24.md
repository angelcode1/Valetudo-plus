# Dreame X40 R2416 — v132 complete native regex census and turbidity gate reduction

**24 October 2026. Offline-only original firmware/static CFG verification, no robot interaction.**

## Source-derived result

The original SHA-256-pinned `node_lethe.so:ProcessModelInfo()` contains **31** direct native typed `std::regex_match()` calls. v131 audited **27**. v132 establishes source-backed handling for **all four remaining calls** and completes the census.

| Native call | Proven source and outcome | CFG treatment |
|---|---|---|
| `0x47038c` | A lower-level `std::__detail::_Compiler` generates an ECMAScript regex from the original literal byte range `0x9fb1b0…0x9fb1c6`; it does **not** match the separately verified actual private R2416-family primary model | The `TST w0,#0xff` and `B.eq 0x4721cc` at `0x470394` take the no-match branch. Remove impossible successor `0x470398` |
| `0x472b3c` | Normal regex constructor, primary `MODEL`, foreign-name no-match; low-byte result stored at `SP+0x100` | Local no-match zero spill confirmed; shared downstream consumer **not** globally constrained |
| `0x47349c` | Normal regex constructor, primary `MODEL`, foreign-name no-match; low-byte result stored at `SP+0x98` | Local no-match zero spill confirmed; shared downstream consumer **not** globally constrained |
| `0x478404` | Normal regex constructor, primary `MODEL`, foreign-name no-match; low-byte result stored at `SP+0x80` | Local no-match zero spill confirmed; shared downstream consumer **not** globally constrained |

The manual-compiler site is distinct from the conventional regex constructor pattern previously recognized by v122–v131; it has its compiler inputs, ECMA syntax option transfer, source begin/end literal addresses, regex-object transport, typed `regex_match`, actual input register and immediate branch verified against the **original** native instructions and an exact SHA-256-pinned instruction corridor. All three other calls have their native constructor-to-join corridors independently source-hashed.

**New conservative bounded result: 12 → 11 possible direct writes to `[SP+0xBC]`**. The eliminated site is **`0x4703fc`**, whose value source is architectural zero. The surviving possible direct writer sites, each having bounded locally positive source coverage from v124/v125, are:

`0x474cd0`, `0x475bc4`, `0x476598`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

**Critical limit:** this is a possible direct-instruction **static CFG source analysis**. The fact that the only inventoried possible zero source was excluded does **not** prove that a positive writer executes, that no indirect write resets the flag, that the active native `enable_turbidity` Blackboard key is true, or that a dirt-triggered **second physical mop wash** occurs.

The three stored regex results must not be used for whole-graph pruning without proving which of several stack-slot definitions reaches each later shared consumer. The next logical task is source-verified path-sensitive stack/reaching-definition propagation.

## Reproduction and verified tests

The separately delivered owner-side package `X40-R2416-v132-sanitized-complete-native-regex-census.zip` (SHA-256 **`30604c805c52188572009103f5c03ab0ad60855f4cde7e923bf932c0d1e07aa3`**) contains full Python-standard-library verifier `x40_r2416_v132_complete_regex_inventory_verify.py`, its v112–v131 sanitized dependencies, detailed report, aggregate-only JSON, README and SHA256SUMS. No original firmware ELF, APK, private runtime config, credentials or source disassembly is included.

```sh
unzip ~/Downloads/X40-R2416-v132-sanitized-complete-native-regex-census.zip -d ~/Downloads
cd ~/Downloads/x40-v132-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v132_complete_regex_inventory_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

The ZIP passed integrity and SHA-256 checks, **and was freshly unpacked and re-executed from its contents** against the original source evidence:

```text
X40_V132_ORIGINAL_SOURCE_PINS_PASS elfs=10
X40_V132_NATIVE_REGEX_CENSUS_COMPLETE calls=31 old=27 new=4
X40_V132_COMPILER_CONSTRUCTED_REGEX_BRANCH_PASS excluded=0x4703fc
X40_V132_SPILLED_REGEX_ZERO_RESULTS_PASS count=3 no_unsafe_global_prune=true
X40_V132_POSSIBLE_DIRECT_FLAG_WRITERS_PASS before=12 after=11
X40_V132_INDEPENDENT_NATIVE_MUTATIONS_REJECTED count=37
LIMIT: no one executed flag writer, live turbidity value or second physical wash proven
```

**Preserved last confirmed state:** Valetudo+ v74, SmartHost=0, writeGateOpen=false, original launcher/recovery backups intact. No robot, Valetudo executable code, `master` or other branch changes.
