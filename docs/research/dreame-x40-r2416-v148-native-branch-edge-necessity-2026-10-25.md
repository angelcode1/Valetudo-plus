# Dreame X40 R2416 — v148 source-gated necessary branch edges

**25 October 2026 — sanitized offline research, no robot interaction.**

## What v148 adds

The previous v147 analysis selects **one example native CFG path per possible last direct `SP+0xBC` writer**. Divergent choices on example paths are not evidence that those branches are *necessary*. Other feasible paths can reach the same writer.

v148 adds a separate bounded **edge-deletion necessity check**. For a selected source-verified conditional edge (`branch PC -> successor PC`), it deletes that single edge and re-explores the correlated state graph. A writer is reported dependent on that edge **only if no feasible bounded path still reaches the original flag read with that writer as the last direct store**. It independently tracks the last direct `SP+0xBC` writer; direct `SP+0x98` 32-/64-bit value-source classes; and the source-verified `SP+0x100` zero-result branch. Pointer-low-bits and unresolved local register values remain unknown, never coerced to true or false.

The default source-backed audit checks up to **16 conditional edges**, prioritising `0x470b44` (`SP+0x98`) and `0x4710c0` (`SP+0x100`), then divergence sites from prior witness samples. The **selection** is heuristic and finite; the test of each selected edge explores all bounded reachable correlated states. It is not a proof for untested branches, indirect control transfers, aliased stores, runtime model metadata or actual hardware behaviour. An edge *necessary for a writer* is still **not an observed execution** of that edge.

## Verified in this run

- **11** source-free behavioural fixtures pass: alternative paths, truly required edge, overwrite of a prior writer, bypass, no guard-reachable writer, native known-zero SP98 restriction, unknown pointer source, state budget refusal and sampled edge-selection cases.
- Independently generate **64** synthetic DAGs with a deterministic seed. Under baseline and two single-edge deletion settings, compare the new edge-cut worklist against the independently authored v135 `joint_product`: **192 comparisons passed**, preserving both total possible writers and SP98 source subclasses.
- Prior v147 source-free regressions, Python compilation, original `SHA256SUMS` manifest, ZIP CRC and a *clean-extraction* replay passed.
- An intentionally missing original private v62/v128 input pair was **refused without creating an output artifact**.

## IMPORTANT: actual firmware result was not generated here

The original ten-ELF v62 archive was listed by the conversation file service, but its supposedly materialized path was not accessible in the current execution container. The owner-side sanitized v128 model-compare-site ZIP was likewise unavailable. **The actual v148 original-firmware edge-cut computation was NOT RUN.** No actual candidate is eliminated by the v148 synthetic results; the earlier source-pinned **ten possible direct last-writer sites remain unchanged**:

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

Only if `SP+0x98` is independently known **zero**, the earlier v135 bounded path graph permits five sites: `0x474cd0`, `0x476798`, `0x4773dc`, `0x4775a4`, `0x4776b4`. **The actual runtime value was not observed.** No one writer, `enable_turbidity` state or additional physical mop wash is proved.

## Reproducible operator kit

`X40-R2416-v148-sanitized-necessary-branch-edges.zip` SHA-256 **`4633b7490b82a3637449b507e3cee58e2c510d47b6a6fe40465a6fbffdffedb9`** contains the complete standalone Python-standard-library `x40_r2416_v148_necessary_edge_cut_verify.py`, v112–v147 sanitized dependencies, detailed report, sanitized JSON, README and SHA256SUMS. It **does not include** original firmware, APKs, raw model literals, runtime config, account material or private hardware values.

```sh
unzip ~/Downloads/X40-R2416-v148-sanitized-necessary-branch-edges.zip -d ~/Downloads
cd ~/Downloads/x40-v148-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v148_necessary_edge_cut_verify.py --self-test

# Source-backed analysis for the owner's private input archives only;
# NOT run by the assistant in this turn:
python3 x40_r2416_v148_necessary_edge_cut_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
 --max-cut-edges 16 --self-test \
 --out ~/Downloads/x40-v148-necessary-branch-edges.json
```

The last command source-validates ten original SHA pins, exact model evidence and the v135/v147 correlated **118,989** states and **35** terminal classes before producing bounded proof of checked-edge necessity. It refuses source absence, state cap overflow and output overwriting. The resulting sanitized JSON is a *static edge-dependence report*, never a live branch observation.

No robot setting changes, MIOT writes, station commands, runtime instrumentation, binary redistribution, executable Valetudo code changes or changes to `master`. Last operator-confirmed working Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false` and original launcher/recovery preserved.
