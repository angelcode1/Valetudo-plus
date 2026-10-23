# Dreame X40 R2416 — v39 native `SubTree` decorator and initialization-root audit

**Date:** 2026-10-23  
**Method:** private, read-only AArch64 disassembly of the SHA-256-pinned original firmware with existing runtime library comparisons. This report contains no proprietary ELF bytes, full disassemblies, passwords, device identifiers, original YAML files, or maps. **No robot commands or Valetudo+ changes.**

## Research question

v38 confirmed that the four initialization nodes preceding the enclosing `StationWash` loop are instances of the same native node type `SubTree`. It did **not** determine the concrete `SubTree` factory callback, whether the node translates child statuses, or which generated nodes are immediately underneath the four wrappers.

## Finding 1: `SubTree` is `BT::DecoratorSubtreeNode`, not a file-selector node

The built-in `BehaviorTreeFactory` registration for `SubTree` uses a function handler for `BT::DecoratorSubtreeNode`. The `SubTree` literal and `registerBuilder` call at `0x62c0c–0x62c74` are connected to the concrete builder through the following GOT relocations in pinned `libbehaviortree_cpp.so`:

| Relocation offset | Expected relocated symbol | Symbol VA |
|---|---|---|
| `0xd8a90` | `getBuilderImpl<BT::DecoratorSubtreeNode>` handler `_M_manager` | `0x64790` |
| `0xd8ae8` | `getBuilderImpl<BT::DecoratorSubtreeNode>` handler `_M_invoke` | `0x64890` |

The latter constructs `BT::DecoratorSubtreeNode` through its constructor PLT and returns that object to the factory. This is an exact, concrete callback resolution, not an inference from the name `SubTree`.

At `DecoratorSubtreeNode::tick()` (`0x8f430–0x8f450`), the code updates its running-state bookkeeping if necessary, retrieves the child pointer from `this+0x20`, and tail-dispatches through the child's vtable `+0x18` using `br x16`. No extra status comparison or conversion occurs **in that wrapper tick routine**. A child can still return running, success or failure according to *its* logic; no runtime statuses have been observed.

This node is distinct from the `SubtreeCondition` / `SubtreeConditionOpt` selector mechanisms studied in v28–v31. Do not attribute their `.xml` basename resolution semantics to the four `SubTree` initialization wrappers.

## Finding 2: all four instances have an attached generated child

The SHA-pinned `liblethe_tree.so` constructs each wrapper with the same `SubTree` node type, attaches it under the generated root sequence, and then builds its first child through `decorator_parent_setChild` (`0x1c6800`).

| Pre-Loop instance | Wrapper attach | Generated child builder | First child attach | First child *type* |
|---|---:|---:|---:|---|
| `MapLoad` | `0x30db24` | helper `0x2eeaf8` | `0x2eeb44` | `SequenceStarRoF` |
| `RobotSysInit` | `0x30db60` | inline at `0x30db68` | `0x30db8c` | `SequenceStarRoF` |
| `StationSysInit` | `0x30e03c` | helper `0x2ccaf4` | `0x2ccb3c` | `SequenceStarRoF` |
| `RobotmodeInit` | `0x30e078` | helper `0x2c7694` | `0x2c76d4` | `IfThenElseStarRoF` |

The first three type/name literal pairs are `SequenceStarRoF` / `SequenceStar`; the fourth is `IfThenElseStarRoF` / `IfThenElseStar`. The verifier checks the literal bytes and the generated AArch64 argument-preparation instructions, rather than guessing from neighbouring string matches.

For three nodes, `RobotNode` makes a direct `BL` call into the helper after the wrapper has been constructed and pushed onto the construction stack. The helper increases construction depth, creates the first child, and calls `decorator_parent_setChild`. `RobotSysInit` performs the same operations inline. This resolves the earlier ambiguity about whether instance names such as `MapLoad` imply separate exported builder functions: the corresponding generated child trees are constructed **inside the pinned native tree library**.

## Important refinement to v38

v38 correctly reported that names like `MapLoad` were **instance names**, not independently demonstrated exported functions. v39 identifies the actual runtime node type and its first child without inventing any `buildMapLoad` symbol.

**The `SubTree` decorator does not, by itself, determine an initialization outcome.** Its child control nodes are now the bounded next targets for status analysis:

- `SequenceStarRoF` beneath `MapLoad`, `RobotSysInit` and `StationSysInit`.
- `IfThenElseStarRoF` beneath `RobotmodeInit`.

A wrapper's forwarded status is only one part of the pre-Loop `SequenceStarRoF` prerequisite chain. We have not proven which of these children succeeds on the running R2416 or whether a particular one delays entry to `StationWash`.

## Verification and limitations

The standalone v39 verifier first replays v38 → v37 → v36 checks against the private archives, including five original-library full-file SHA-256 pins, the three active/original byte comparisons, and the effective `RobotNode` selector. It then verifies:

1. Both concrete decorated-`SubTree` factory handler relocations.
2. The builder's constructor call, decorator child-pointer accessor, and tick tail-dispatch instructions.
3. All four wrapper constructor/attachment and generated-first-child construction/attachment paths.
4. The distinct first-child type/name literal pairs.

Expected marker: `X40_V39_SUBTREE_DECORATOR_STATIC_PASS`. It does not connect to the X40, execute vendor code, publish AVA messages, or set MIOT properties. An altered runtime tree library must fail the original/runtime comparison check.

**Unproven and unchanged:** actual runtime child statuses, completed initialization, actual `StationWash` tick execution, R2416-specific creation of `special_push_clean_dish`, normal turbidity causing `TurbidityResultFail` then `r2343_start_rewash`, and an additional physical dock-wash operation. Continue distinguishing `TubidityRecleanFlag`, lowercase `turbidity_reclean_flag`, `TurbidityResultFail`, and `r2343_start_rewash`.

## Reproduce

Extract the offline package, retaining the v36/v37/v38 verifier dependency scripts alongside v39, then run:

```bash
python3 x40_r2416_v39_subtree_decorator_verify.py \
  ~/Downloads/X40-Firmware-Reference.zip \
  ~/Downloads/X40-R2416-v27.zip
```

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. Preserve the running robot and do not commit proprietary native libraries, private configuration, personal maps or device credentials to Git.

## Next narrowly bounded task

Decode the immediate control-child conditions inside the first-child `SequenceStarRoF` and `IfThenElseStarRoF` generated regions; identify which branch statuses can actually reach the enclosing Loop. Separately maintain the bounded search for `special_push_clean_dish` producers. Do not infer physical rewash from tree control structure alone.