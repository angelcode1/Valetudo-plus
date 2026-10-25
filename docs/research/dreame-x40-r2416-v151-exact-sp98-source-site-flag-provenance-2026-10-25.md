# Dreame X40 R2416 — v151 exact model-pruned SP+0x98 source-site to flag-writer provenance

**25 October 2026 · full offline run against the original owner-private ten-ELF v62 archive and authenticated sanitized v128 model evidence.** No robot/cloud/MIOT or native runtime activity.

## New evidence

v150 source-pinned 19 noncanonical native primary MODEL string comparisons and reduced possible *last direct* `SP+0xBC` flag writers to **five**, but v135's SP+0x98 analysis coalesced different store instructions into only three coarse value-source categories.

v151 tracks the **last direct instruction writing SP+0x98 at its actual load (0x470b40)**, together with the last direct SP+0x100 source *at its read* and the last SP+0xBC writer at the guarded flag consumer. This increases the precision of the bounded direct-AArch64 CFG audit without assuming a register or pointer value.

**Source-verified:** 10/10 original ELF SHA-256 pins, v150's 19 compiled comparison branches, seven possible last-direct SP+0x98 source sites (down from nine in the earlier unpruned source inventory), **100,132** correlated graph states and **30** distinct final (SP98-source, SP100-source, flag-writer) triples. The five possible final SP+0xBC writer sites remain unchanged.

The seven surviving possible *last* SP+0x98 source sites:

`0x4707e0, 0x47085c, 0x47130c, 0x4734a8, 0x475bbc, 0x4774d0, 0x478134`.

Previous possible SP98 sources `0x4775d8` and `0x477768` are excluded **only as last sources at the read** in the bounded model; not as executable instructions globally.

| Possible last direct SP+0xBC writer | Three common SP98 last sources | Distinguishing local SP98 last source |
|---|---|---|
| `0x475bc4` | `0x4707e0`, `0x47085c`, `0x47130c` | `0x475bbc` |
| `0x4774d8` | Same | `0x4774d0` |
| `0x4775a4` | Same | `0x4734a8` |
| `0x478160` | Same | `0x478134` |
| `0x47826c` | Same | `0x478134` |

The `0x4734a8` source writes the compiled zero result of a native regex_match and only pairs with `0x4775a4` as final flag writer in this bounded model. However **this source was not observed executing**, and `SP+0x98=0` has not been observed on the robot. Pointer-derived 64-bit source `0x47130c` overlapping SP98 has unknown low 32 bits, not an inferred Boolean. The two separate flag-writer paths `0x478160` and `0x47826c` can both inherit source `0x478134`; even a last-source address would not always identify the last flag writer.

### Tested counterexample to an overaggressive new prune

The original native primary-model compare `0x47813c` and CBNZ `0x478140` use ADRP/ADD x23 at `0x478124/0x478128`. The source-pinned compiled literal is not equal to the operator-authenticated primary model. **But source-correct pruning of the mismatched direct comparison edge leaves all five writer sites and all 30 source-site terminal combinations possible**: an alternate CFG path bypasses this exact branch. Therefore it would be unsound to eliminate `0x478160` based on that literal mismatch alone.

### Verification

- Original ten vendor ELF SHA256 source pins pass, plus v150 19 source-pinned noncanonical comparison windows and existing model identity validation.
- Native SP98/SP100 source load/store opcodes and native register, compare and branch instruction corridor verified.
- **29** independent native instruction/literal byte mutations rejected by source-specific opcode/digest checks without using full original ELF SHA mismatch as mutation oracle.
- Source-independent tests for overwritten stores, alternate writer paths and unassigned/never-read source cases pass.
- A clean-extraction replay from `X40-R2416-v151-sanitized-stack-source-site-provenance.zip` repeated all source checks and compared identical output JSON bytes. ZIP CRC, SHA256SUMS pass.

**Not proved:** any one writer actually executed for the R2416, the real live SP98 value, native effective enable_turbidity Boolean, actual StationWash Blackboard identity, or a dirt-triggered *additional physical mop wash*.

Full owner-side Python-only verifier, complete v112–v150 sanitized dependencies, report and aggregate JSON are separately downloadable in `X40-R2416-v151-sanitized-stack-source-site-provenance.zip` (SHA256 `c73e34f013a3acc00734abb84064aa5297465bc51993a608095bb071e115816f`). Only sanitized documentation and numeric/PC aggregate data are committed. No original vendor ELF binaries, raw model string, APK, device logs/config/maps/secrets/serials or hardware command payloads.

**Preserved:** last operator-confirmed Valetudo+ v74, SmartHost=0, writeGateOpen=false, original launcher/recovery copies and GitHub master. No runtime change.
