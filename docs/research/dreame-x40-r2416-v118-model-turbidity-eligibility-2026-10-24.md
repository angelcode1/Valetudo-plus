# Dreame X40 R2416 — v118 exact-model and native turbidity flag boundary

**24 October 2026 · SHA-256-pinned original firmware static analysis, offline only.**

## Discovery

The exact native string `dreame.vacuum.r2416` is compared in `node_lethe.so:ProcessModelInfo()` at `0x470930–0x470940`. The successful equality branch at `0x470940` reaches `0x470958`. This comparison **does not by itself write** the model-group feature flag later checked before `enable_turbidity`.

The guarded native `BT::Blackboard::set<bool>` of the exact `enable_turbidity` key is at `0x47185c`. Its prior condition loads a different, SP-relative flag at `SP+0xBC`: observed checks at `0x470be4/0x470be8` and `0x47182c/0x471830`. The 0-valued branch at `0x471830` skips the setter to `0x470bec`, while a positive flag permits the setter. This is a **separate eligibility gate**, not a direct consequence of merely matching the R2416 literal.

The original native function contains several alternative model-specific initialization groups. Two verified examples of flag-zero staging are `0x4703fc` and `0x471a90`; two positive group examples are `0x47227c` and `0x47373c`. Crucially, scanning the **entire** `ProcessModelInfo()` symbol for directly SP-relative 32-bit `STP`/`STR` stores overlapping `SP+0xBC` yields **61 instruction sites**. This is *not* 61 models, a complete semantic setter inventory, or a unique-producer count. Indirect accesses/aliases and other encodings are out of scope. The earlier limited examples are **not exhaustive**.

## Proven / unresolved

| Question | Finding |
|---|---|
| Exact R2416 model comparison | Compiled and verified, branch `0x470940 → 0x470958` |
| Independent flag guard on `enable_turbidity` write | Verified at `SP+0xBC` |
| Typed Boolean setter | Verified at `0x47185c` |
| Full symbol's directly decoded 32-bit pair/word stores overlapping source stack slot | 61 |
| Whether R2416 reaches a positive model-group setter | **Not proved** |
| Whether R2416 is excluded from every positive setter | **Not proved** |
| Live `enable_turbidity` value and active StationWash Blackboard scope | **Unobserved** |
| Genuine dirt-triggered extra physical mop wash | **Unproven** |

This evidence refines v117's initialization findings; it **does not** establish or deny R2416-specific eligibility in the face of alternate model-group branches. The original R2416 name can coexist with broader regex or alias conditions that still need complete control-flow resolution.

## Reproduction

The operator-side sanitized `X40-R2416-v118-sanitized-model-eligibility.zip` includes `x40_r2416_v118_model_turbidity_flag_verify.py` together with its v112–v117 Python-only regression dependencies, README, detailed research report, JSON and checksums. The original owner-private v62 firmware ZIP is **never committed**.

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v118_model_turbidity_flag_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Observed, verified results:

```text
X40_V118_TEN_ORIGINAL_SHA256_PINS_PASS count=10
X40_V118_V117_NATIVE_KEY_PROVENANCE_REGRESSION_PASS
X40_V118_EXACT_R2416_MODEL_COMPARE_BRANCH_PASS
X40_V118_INDEPENDENT_MODEL_GROUP_FLAG_INIT_AND_GUARDS_PASS
X40_V118_ENABLE_TURBIDITY_TYPED_WRITER_GUARDED_PASS
X40_V118_PINNED_INSTRUCTION_AND_LITERAL_MUTATIONS_REJECTED count=44
LIMIT: model-group reachability, live turbidity enablement, and second physical wash NOT proven
```

The independent mutation checks reject 44 single native instruction/literal modifications without relying on whole-file SHA rejection; the loader separately SHA-pins all ten originals. The companion ZIP contains no native firmware, original vendor configs, maps, logs or personal identifiers.

## v119

Complete symbolic CFG / model-string and regex-match provenance for exactly `dreame.vacuum.r2416`, traversing all model-group initializers that may feed `SP+0xBC`, and prove exact setter reachability **before** treating the feature as eligible or impossible. Do not infer effective runtime tree scope from static root Blackboard construction alone; authentic `StationWash.xml` remains absent.

**Device unchanged:** last-confirmed working Valetudo+ v74, `SmartHost=0`, experimental `writeGateOpen=false`, launcher/recovery files preserved. No robot I/O, firmware patch, actuator test, MIOT write or runtime fork modification in v118.
