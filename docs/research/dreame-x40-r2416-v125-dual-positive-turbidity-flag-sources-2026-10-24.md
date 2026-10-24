# Dreame X40 R2416 — v125 paired positive flag-value sources

**24 October 2026 · offline owner-private SHA-256-pinned AArch64 ELF research.** No robot actions, firmware writes, account access, station commands, or proprietary binary distribution.

## New result

v124 retained thirteen possible direct source sites writing the `SP+0xBC` model-group eligibility flag in `node_lethe.so:ProcessModelInfo()`, after exact R2416 name and source-verified regex pruning. One site writes zero; twelve use locally staged register values of one. Eight of the twelve nearby `MOVZ #1` sites dominated their stores in the bounded CFG. Four did not.

**v125 resolves all four previously nondominated source paths.** Each alternate incoming path executes another original `MOVZ W24,#1`, then branches directly into a shared store block. Original native source and branch-target instruction corridors are separately SHA-256 pinned. At the fourth site a typed `std::string::compare` call leaves callee-saved W24 intact by AArch64 ABI, with the exact local bytes pinned.

| Store site | Original nearby MOVZ W24,#1 | Alternate MOVZ W24,#1 | Alternate jump into shared block | First MOVZ reachable in model-pruned graph |
|---|---|---|---|---|
| `0x474cd0` | `0x474cb4` | `0x474df8` | `0x474e04 → 0x474cc4` | No |
| `0x4761c4` | `0x476190` | `0x476298` | `0x4762a8 → 0x47619c` | Yes |
| `0x4773dc` | `0x4773b4` | `0x4775d0` | `0x4775e0 → 0x4773c0` | Yes |
| `0x4775a4` | `0x47758c` | `0x4774b4` | `0x4774bc → 0x477590` | No |

For each store: (a) a path bypassing just the nearby initializer still reaches it; (b) cutting *both* source initializers makes it unreachable from native function entry under the v123/v124 model-pruned direct AArch64 CFG; and (c) cutting the verified alternate branch destination prevents that alternate source from reaching the store. The two initially assumed reachable first initializers that were actually unreachable are now recorded explicitly, not silently treated as live paths.

**Interpretation:** all twelve locally positive-value candidate store sites now have positive-source coverage within the verified bounded graph (eight by a single dominating source, four by alternative positive sources). This is not proof that any positive branch is selected by the real R2416 model. The initial zero-valued source `0x4703fc` remains a possible last direct writer, and there are still **13** bounded candidate last-writer sites.

## Limits

This is direct intraprocedural graph and pinned local-corridor evidence, **not** complete register SSA / dynamic execution. Other writes/aliases, indirect branches, nonlocal effects, runtime model metadata and the effective Blackboard key are outside proof scope. The compiled `enable_turbidity` setter's downstream guard, the actual `+0x688` StationWash gate value, genuine mop-dirt observation, and a **second physical mop wash** remain unverified.

## Reproduction

The separately delivered owner-downloadable `X40-R2416-v125-sanitized-dual-positive-sources.zip`, SHA-256 `49ce508127c63bf571330a155021a590f990877520e69f425e3d60e6c38bdfad`, contains a complete Python-standard-library script `x40_r2416_v125_dual_initializer_paths_verify.py`, v112–v124 regression modules, research report, sanitized JSON, README and a checksum manifest. The owner-private `X40-R2416-v62-readonly-20261023T051829Z.zip` is required *locally* and is **never** included or committed.

```sh
cd ~/Downloads
unzip X40-R2416-v125-sanitized-dual-positive-sources.zip
cd x40-v125-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v125_dual_initializer_paths_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verified output:

```text
X40_V125_TEN_ORIGINAL_ELF_SHA256_PINS_PASS count=10
X40_V125_V124_FLAG_VALUE_PROVENANCE_REGRESSION_PASS sites=13
X40_V125_FOUR_ALTERNATE_MOVZ_ONE_SOURCES_PASS count=4
X40_V125_TWO_SOURCE_COVERAGE_ON_ALL_FOUR_PREVIOUS_NONDOMINATORS_PASS
X40_V125_ALT_BRANCH_CORRIDORS_PINNED_PASS count=4
X40_V125_INDEPENDENT_NATIVE_SOURCE_MUTATIONS_REJECTED count=28
LIMIT: bounded positive source coverage is not live R2416 gate enablement or a second physical wash
```

28 single-location source byte changes were rejected by source-specific checks without relying on an original ELF-wide SHA mismatch. Ten original ELF SHA-256 pins are separately checked.

## Next — v126

Analyse consistent model-group predicates and the actual *last* writer to `SP+0xBC`, instead of considering source sites individually. The next proof must distinguish the zero initializer from mutually exclusive positive-model routes for the same exact R2416 input. Do not try device-side MIOT writes, guessed station opcodes or synthetic dirt.

**Preserved safety:** last operator-confirmed Valetudo+ v74, SmartHost=0, experimental `writeGateOpen=false`, original launcher/rollback files intact. GitHub `master` and runtime Valetudo code unchanged.
