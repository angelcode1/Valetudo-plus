# Dreame X40 R2416 — v117 native switch initialization and turbidity-key provenance

**24 October 2026 · owner-private original ELF static evidence · sanitized report.** No robot I/O, firmware modification or device action.

## Result

v116 showed that the StationHandle bytes at `+0x688` and `+0x689` are derived from the native Blackboard integer inputs `smart_hosting_switch`, `smart_auto_wash_switch` and `smart_auto_mop_switch`. Constructor defaults and optional recalculation mean the separately observed app-level `SmartHost=0` cannot establish the live Blackboard gate value.

v117 verifies upstream compiled initializers and guards in original `node_lethe.so`:

| Key | Direct compiled evidence | Limitation |
|---|---|---|
| `smart_hosting_switch` | `AvaNodeRoute` constructor loads this exact key at `0x354630`, stages its integer initializer at `0x354644–0x354648` and invokes typed `BT::Blackboard::set<int>` at `0x354658` | Does not establish final live value |
| `smart_auto_mop_switch` | Same constructor's separate key site `0x354688` and typed `set<int>` at `0x3546b0` | Does not establish any current device switch |
| `enable_turbidity` | `ProcessModelInfo()` exact-key load `0x471834–0x471838`, preceding branch guard `0x47182c–0x471830`, typed `set<bool>` at `0x47185c` | Not proved reachable through the R2416 model branch |
| `enable_turbidity` | `StateShowAndSave::StateInit()` key-presence test at `0x8958ac–0x8958dc` | Presence is not true/false and is not evidence that guarded initialization ran |
| `smart_auto_wash_switch` | `StateInit()` `0x895d9c–0x895da0`, zero-initialized typed `set<int>` at `0x895dbc–0x895dc0` | Compiled initialization, not a measured live effective value |

The same `ProcessModelInfo()` contains a branch for the R2416 model comparison (`0x470940` → `0x470958`). **Co-location with the guarded `enable_turbidity` writer does not prove that R2416 reaches that writer.** The exact intervening control-flow/data-flow condition is still unresolved.

## Exact native literal reference census

Counts below are direct AArch64 ADRP+ADD references to *exact standalone NUL-terminated keys* across ten SHA-256-pinned original vendor ELF libraries. They are **not** counts of unique setters, active runtime writes, or all dynamically assembled references.

| Key | `node_lethe.so` | `liblethe_tactics_tree.so` | `liblethe_route_nodes.so` |
|---|---:|---:|---:|
| `smart_hosting_switch` | 31 | 10 | 4 |
| `enable_turbidity` | 3 | 6 | 5 |
| `smart_auto_wash_switch` | 2 | 1 | — |
| `smart_auto_mop_switch` | 4 | 1 | — |

These references include getters, checks and initializers; no all-writers completeness claim is made.

## Reproducibility

The separately delivered sanitized v117 archive `X40-R2416-v117-sanitized-native-switch-provenance.zip` contains a Python-stdlib verifier, the v112–v116 regression verifier dependencies, a more detailed report, JSON results and checksums. It requires the owner's private `X40-R2416-v62-readonly-20261023T051829Z.zip` input; **never commit, publish or distribute the original vendor binaries**.

Run from the extracted `x40-v117-sanitized` directory:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v117_native_switch_provenance_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Actual verified results:

```text
X40_V117_TEN_ORIGINAL_SHA256_PINS_PASS count=10
X40_V117_V116_COMPLETION_GATE_REGRESSION_PASS
X40_V117_NATIVE_EXACT_KEY_REFERENCES_PASS keys=4
X40_V117_CONSTRUCTOR_SMART_HOST_SWITCH_SET_INT_STATIC_PASS
X40_V117_GUARDED_MODEL_ENABLE_TURBIDITY_SET_BOOL_STATIC_PASS
X40_V117_STATEINIT_ENABLE_KEY_PRESENCE_AND_AUTO_WASH_SET_STATIC_PASS
X40_V117_INDEPENDENT_INSTRUCTION_AND_KEY_MUTATIONS_REJECTED count=37
LIMIT: R2416 reachability, live Blackboard values, and physical second wash NOT proven
```

The independent mutation tests alter 37 pinned native instruction/key sites in memory and check the verifier rejects them without relying on a whole-file hash mismatch.

## Next evidence gate

Prove or disprove **R2416-specific control-flow reachability** from the model compare to the `enable_turbidity` setter, then establish the actual StationWash subtree's Blackboard remapping and initialization order. An authentic `StationWash.xml` was not present in the v62/v63 private captures. Even if the gate proves eligible, a real turbidity result → `special_push_clean_dish` → `r2343_start_rewash` → **additional physical mop wash** remains unproven. No guessed settings, synthetic contamination, MIOT writes or station opcodes should be used to bypass these gaps.

**Preserved operator baseline:** last-confirmed working Valetudo+ v74, native SmartHost=0, `writeGateOpen=false`, original launcher/backups intact. No robot actions, runtime source changes or proprietary data published in this research commit.
