# Dreame X40 R2416 v130 — Native DEV_MODEL missing-key fallback and secondary branch constraints

**24 October 2026. Owner-private SHA-256-pinned ARM64 firmware analysis, offline only.** No robot connection, MIOT writes, app/cloud login, firmware patch, debugger, synthetic dirt, actuator commands, or original private binary redistribution.

## Findings

The owner-uploaded v127 JSON model-class evidence reported valid JSON, with an absent top-level `DEV_MODEL`. The v128 model-site ZIP resolved the actual primary model to native strict comparison `site_0x473540`. v129 pinned that conditional model match route back to common model initialization, without flag writes. The model string itself stays private.

**v130 pins the original native normal missing-member code path in `node_lethe.so:ReadModleInfo()`:**

| Original address | Source-verified role |
|---|---|
| `0x46eee0` / `0x46eee4` | Requested key compare and branch |
| `0x46eefc` / `0x46ef44` | Member-search miss routed to `0x46e9f8` |
| `0x46f184`–`0x46f194` | Another search-exhaustion route to the same fallback |
| `0x46e9f8` | Cleanup path, pinned through the default result initializer |
| `0x46ea80`–`0x46ea88` | Empty C++ string initialization: length zero, NUL terminator |
| `0x46eb40` / `0x46eb60` | Return same result object on normal function exit |

For the **normal successful-parse, absent-member** route, this is an empty string fallback, **not a substitution of the primary `MODEL` value**. A bounded, source-hashed original instruction corridor checks the cleanup through empty-result initialization. This is **static conditional behaviour**, not a recorded native return or assertion about exceptions, malformed JSON, runtime changes or all possible parser states.

## Secondary comparisons

Using an empty secondary string (and the original nonempty compiled comparison operands):

- `0x478228` compare / `0x47822c` CBZ — not equal; branch not taken.
- `0x478238` compare / `0x47823c` CBZ — not equal; branch not taken.
- `0x47824c` compare / `0x478288` CBNZ — not equal; branch taken.

The third call-to-CBNZ instruction corridor `0x478250…0x478288` is separately hashed to exclude unreviewed W0 clobbers. In particular, potential flag writer `0x47826c` is **before** the last result-consumer branch and cannot be removed merely because equality failed.

With all **294** source-patterned primary-model comparisons, **23** anchored regex decisions, and the three secondary decisions, the bounded `ProcessModelInfo()` CFG still permits **13** potential direct `SP+0xBC` stores before the `enable_turbidity` guard: one zero source and twelve locally positive sources (as characterized by v124/v125). These are *possibilities*, not executed sites. No unique writer, actual Blackboard value, dirt-detection event or second physical mop wash is proven.

## Verified offline reproducibility

The operator-side ZIP `X40-R2416-v130-sanitized-missing-dev-model-fallback.zip`, SHA-256 `00b9100d7fc49346bb8009c1b07c5305d96fdfd0d348c797d061307b0e9ca236`, contains the full Python-standard-library `x40_r2416_v130_missing_dev_model_cfg_verify.py`, sanitized v112–v129 regression modules, detailed report, aggregate JSON, README and SHA256SUMS. It requires the **private** original firmware archive and **sanitized** v128 comparison-site ZIP only as local inputs.

```sh
unzip ~/Downloads/X40-R2416-v130-sanitized-missing-dev-model-fallback.zip -d ~/Downloads
cd ~/Downloads/x40-v130-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v130_missing_dev_model_cfg_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Observed:

```text
X40_V130_MUTATION_TEST_PASS pinned_native_sites=28 native_corridors=4 evidence=5
X40_V130_ORIGINAL_PINNED_ELFS_PASS count=10
X40_V130_NATIVE_READMODEL_MISSING_DEV_MODEL_EMPTY_RETURN_PASS
X40_V130_THREE_SECONDARY_MODEL_EQUALITY_FAILURES_PASS count=3
X40_V130_MODEL_PLUS_SECONDARY_CFG_PASS possible_direct_writers=13
LIMIT: no executed writer or physical second wash proven
```

Verification rejects **28** independent original instruction-anchor mutations, **four** original corridor mutations and **five** altered model-evidence cases without relying only on full original ELF SHA256 mismatch; separately validates all ten original ELF SHA256 pins.

## Next

Pursue correlation of the remaining native model-group predicates and the final reaching `SP+0xBC` store under the verified primary identity and the normal missing-secondary-model path. If a unique last writer remains nonderivable from immutable inputs, identifying one that **actually executed** requires an authorized low-impact runtime observation, not speculative static reachability.

**Preserved last-tested working state:** Valetudo+ v74, `SmartHost=0`, experimental `writeGateOpen=false`, original launcher and rollback files intact. No GitHub `master`, other research branches, device firmware, or executable Valetudo changes.
