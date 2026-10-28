# Dreame X40 R2416 — v135b conservative correlated stack-path cross-check

**24 October 2026. Offline original ten-ELF SHA-256-pinned AArch64 source + owner-sanitized exact model-comparison evidence. No device I/O.**

## Why this is an addendum

The existing research branch's v135 source-correlated analysis represents 68,924 abstract CFG node states and 25 terminal combinations. It follows the prior locally positive-source register reasoning to treat source-class `ONE` as nonzero at the `SP+0x98` branch.

The separately validated **v135b conservative replay does not force that branch for a locally positive-sourced register unless whole-path register SSA is established.** It retains *both* successors, just as it retains both possible outcomes for the overlapping pointer-derived 64-bit `SP+0x98` store at `0x47130c`. This deliberately broadens the abstract graph without implying any additional physical device behavior. It also tracks whether the separate `SP+0x100` Boolean read was actually reached rather than assigning a value to unread paths.

The original direct CFG and evidence are unchanged: actual private native model identity `site_0x473540`, normal missing-`DEV_MODEL` empty-result constraints, 297 pinned direct primary comparisons, native regex gates, v133 spill producer sites, v134 overlapping 32-/64-bit stores and the ten v134 flag-writer candidates.

## Conservative product-state results

Each forward source-path state tracks current direct-source class at `SP+0x98`, at `SP+0x100`, last inventoried direct `SP+0xBC` store, and the two separate values/classes at their **actual** consumer instructions.

| Bounded offline measurement | Result |
|---|---:|
| Augmented reachable static states | **118,989** |
| Distinct terminal source-class / flag-writer combinations | **35** |
| Terminal combinations where `SP+0x100` consumer reads inventoried regex zero | **20** |
| Terminal combinations where `SP+0x100` consumer was never reached | **15** |
| Possible final direct flag writers overall | **10** |
| Possible flag writers conditioned on inventoried zero source at `SP+0x98` read | **5** |
| Possible flag writers with locally positive source class at `SP+0x98` read | **10** |
| Possible flag writers with pointer-derived X64 unknown-low-word source | **10** |

On paths where the `SP+0x98` consumer reads the source-verified regex zero, the bounded last flag-writer sites are:

`0x474cd0`, `0x476798`, `0x4773dc`, `0x4775a4`, `0x4776b4`.

This five-site conditional subset is **not** a device-global exclusion. All ten previously known possible sites remain reachable under the other source classes:

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

The source-pinned 64-bit store writes a pointer-derived value, **not** a known Boolean. At that branch it is treated as an unknown low 32-bit value. The v133 direct regex zero at `SP+0x100` constrains the CBZ to its zero successor **only on paths that pass through that load**; unread paths remain explicitly unclassified.

These cardinalities are implementation-defined *finite static abstract-path classes*, not actual execution counts, confidence estimates, observed memory, or evidence of automatic washing. The widening of abstract states between v135 and v135b arises from a more conservative branch treatment and explicit consumer-visited state; it is not an inconsistent measurement of robot execution.

## Verification

The separately delivered sanitized owner-side `X40-R2416-v135-sanitized-correlated-stack-state.zip` (SHA-256 `4d26106003da13242207d2fb6d7a27eae52ad4a084f9bde0eecbebcd02bb6176`) contains the Python standard-library `x40_r2416_v135_joint_stack_last_writer_verify.py`, v112–v134 sanitized regression modules, detailed report, aggregate JSON, README and SHA256SUMS.

From a **fresh ZIP extraction**, the full current verifier and checksum manifest passed using only the owner's private original v62 firmware ZIP plus the separately sanitized model comparison-site evidence as read-only inputs. **10/10 original ELF SHA-256 pins**; scoped v124/v133/v134 native instruction/stack-source and ten-writer CFG checks; **27 independent native-source instruction mutations rejected**; **6 synthetic product-state tests passed** (zero, locally positive, wide unknown, consumer skipped and truly uninitialized flag). This is a targeted original-source and scoped regression, not a claim to have re-run every expensive historical whole-ELF reference census.

```sh
unzip ~/Downloads/X40-R2416-v135-sanitized-correlated-stack-state.zip -d ~/Downloads
cd ~/Downloads/x40-v135-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v135_joint_stack_last_writer_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

**Limits:** original intra-procedural **direct** AArch64 branches and inventoried direct W32/X64 stack stores, not complete register SSA, pointer-alias-aware memory modelling, all exception paths, actual dynamic instruction trace, or active Blackboard `enable_turbidity`. **No unique executed writer or real dirt-triggered second physical mop wash has been proved.**

**Safety:** no original proprietary ELF/disassembly, APK, private MODEL value, configuration, map, log, secret, or station-command value committed. Original Valetudo+ v74, SmartHost=0, experimental writeGateOpen=false, launcher, recovery backups, robot, executable code and GitHub `master` remain unchanged.
