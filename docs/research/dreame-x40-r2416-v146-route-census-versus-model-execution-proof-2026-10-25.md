# Dreame X40 R2416 — v146: separating route-pointer census from model-writer execution

**25 October 2026. Offline-only validation of sanitized v137–v145 research and a new fail-closed evidence gate.** The owner-private original ten-ELF v62 archive was *identified* in conversation attachments, but the bytes were **not accessible to the executing analysis container**. No original ELF was scanned in v146. No robot or network operations were performed.

## Fundamental distinction now made explicit

Two different native objects/functions were conflated in the previous suggested next steps:

| Research question | Proven native scope | What the corrected store census can establish |
|---|---|---|
| Which store executed on the native `enable_turbidity` model-group eligibility flag? | `node_lethe.so:ProcessModelInfo`, flag **`SP+0xBC`**; 10 surviving v137 possible direct writer sites | **Nothing about unique execution:** constructor writes do not identify branch outcomes in this different routine. |
| Did a caller mutate the route object's Blackboard shared-pointer field between model processing and tree construction? | `ancp::AvaNodeRoute` constructor, field **`route+0x30`**, audited 3,194-instruction corridor | Source-pinned candidate *base-relative* store forms. Without register alias/reaching-definition analysis, even a fixed `+0x30` opcode is **not proof** its base is the route object. |

v140 source-pinned one `ProcessModelInfo` call and four tree-builder calls reading the same route field; v139 pinned the conditional station node's build-time Blackboard forwarding. Neither proves the object was unchanged or that the StationWash subtree was selected at runtime. v138's station branch tests **key lookup availability**, not typed `bool` truth directly.

v136/v137 preserved the owner's actual model evidence and confirmed the ten possible locally positive-sourced **direct** writers:

`0x474cd0, 0x475bc4, 0x476798, 0x4773dc, 0x4774d8, 0x4775a4, 0x4776b4, 0x47776c, 0x478160, 0x47826c`.

Their proof is **ten possible native store locations**, not ten real executions. v136 had **35 distinct abstract terminal source/writer combinations**, not an event count. Local positive source-preservation does not establish which branch runs.

## v146 reproducibility and fail-closed model

The new, self-contained `x40_r2416_v146_execution_evidence_gate.py` accepts **only** a v145 result marked `RAN_SOURCE_PINNED` that passed the original ten SHA256 ELF pins and earlier native-constructor regression. It validates the exact `0x352304..0x3554e8` constructor interval and 3,194 native instruction count, checks fixed-offset site bounds, code-site alignment, width/offset overlap, register number, collection-count consistency, and that LSE atomic entries have **no fabricated fixed-offset claim**. It deliberately strips any unknown or private fields from its output and reports only sanitized counts and bounded addresses.

Alternatively it can invoke the local v145 verifier directly with an owner-held original v62 ZIP. **This source-dependent mode was not run in this execution environment.** It is a convenience for the operator to produce the next genuine source result.

The self-test uses purely **synthetic v145-shaped JSON**, passes both one-hit and zero-hit cases, and rejects **21 deliberately mutated cases** (false source pins, malformed sites, overlaps, register bounds, count mismatches, missing original evidence, LSE false-claims, malformed form labels). Importantly the zero-overlap case still carries all ten independent model writers and expressly marks unique execution as unproven.

```sh
cd ~/Downloads
unzip X40-R2416-v146-sanitized-evidence-gate.zip
cd x40-v146-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v146_execution_evidence_gate.py --self-test

# Real native census, only on the owner's local original v62 archive:
python3 x40_r2416_v146_execution_evidence_gate.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --self-test \
  --out ~/Downloads/x40-v146-validated-native-constructor-census.json

# Or validate previously produced v145 source result:
python3 x40_r2416_v146_execution_evidence_gate.py \
  --v145-source-json ~/Downloads/x40-v145-native-store-census.json \
  --out ~/Downloads/x40-v146-validated-native-constructor-census.json
```

The script refuses missing sources or unsigned/unverified results, refuses to overwrite output, and does **not** export vendor code, device config, accounts, maps, log messages, control instructions, model literals or arbitrary JSON fields.

## What must happen to answer the original question

- To narrow the ten **model-gate** candidates further: model all still-unresolved native branch/alias dependencies in `ProcessModelInfo`; a separate route-field census is not a substitute.
- To identify the instruction **actually executed** rather than a possible static instruction: either a complete proof of all relevant runtime-dependent predicates, or an independently authorized, sufficiently scoped runtime instruction trace is needed. Neither is currently held. Do **not** attach risky production instrumentation or initiate a wash merely to force a trace.
- To establish functional CleanGenius rewash, additionally show effective Blackboard scope, native dirt result, marker/selector linkage and a **second physical mop wash**. A key literal or app status label is insufficient.

**Status:** no v146 original-firmware measurement; ten direct possible writers unchanged; no unique instruction or automatic physical rewash proven. Preserved last known Valetudo+ v74, SmartHost=0, `writeGateOpen=false`, original launcher/backups, and GitHub `master` untouched.