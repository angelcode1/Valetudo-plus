# X40 R2416 — numeric turbidity-state dispatch and retry bookkeeping

**Source:** offline, SHA-256-pinned `liblethe_tactics_tree.so` (`da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`); no robot access. Supplements [post-decision findings](./X40_TURBIDITY_POSTDECISION_R2416.md).

## Verified native dispatch

In `StationHandle::SweepStationContorl::WashErrorLogicRun(int,int&,int)`, a Blackboard-associated lookup of `TubidityState` prepares an integer at stack offset `0x98`; the function branches on that value at `0x2549bc`–`0x2549cc`. Key evidence:

| Value/path | Observed compiled operations |
| --- | --- |
| `0` | Branch at `0x2549cc` enters `TurbidityMonitorLogicRun()` at `0x254d44`. The latter has a separate path that prepares numeric state `1` through a Blackboard-associated setter. |
| `2` | Branch at `0x2549c4` reaches `0x254dc8`: typed `set<TubidityState&>` prepares `0`; `this+0x674` is set to `100`; `this+0x678` is decremented and published to a Blackboard integer; `this+0x648` increments. |
| `>2` | Dispatches via `0x254c48`; state `4` has its own comparison path. Do not infer handling of arbitrary integers. |
| `4` | A-table calculation at `0x254fa0`, counter test at `0x254fac`–`0x254fb0`; the `<=9` path can call `CheckIfNeedReClean()` at `0x254ff4`. The `>9` arm writes state `4` and continues separate bookkeeping. |

The `2` arm additionally writes `turbidity_check_failed_times` using the incremented field at `this+0x648`. If that field exceeds `9`, the compiled code prepares the string `"true"` for `TurbidityNeedCheck` before writing the count.

These code paths are not all executed sequentially; they are **distinct branches** selected by the current state and other checks. The `this+0x678` value has the appearance of remaining-count bookkeeping, but its initialization, units, allowed range and device-specific policy were not decoded. The value 100 is a compiled counter initialization, **not** a proven wash duration or number of allowed rewashes.

## Relation to other findings

`WashFloorTubidityCheck()` can independently write `TubidityState=2` with `TubidityResult="fail"` or `TubidityState=3` with `TubidityResult="success"` after an A-table comparison. The consumer of state `2` above therefore forms a **compiled feedback/retry-related loop for turbidity checking**.

`CheckIfNeedReClean()` produces a different mixed-case string value, `TubidityRecleanFlag`; `r2343_start_rewash` is a separate marker consumed by AVA to update `wash_times`. **No demonstrated instruction-level path ties the state-2 bookkeeping loop directly to that marker or to a physical mop-wash restart.**

The lowercase `turbidity_reclean_flag` is independently set/erased by conditional behaviour-tree nodes. It must not be equated to the numeric `TubidityState` or the mixed-case `TubidityRecleanFlag`.

## Validation and safety

An offline verifier was run against the unmodified private ELF, checking its complete SHA-256, **44 instruction anchors, four literal keys and eight branch targets**. It passed; a deliberately modified copy was rejected at the hash gate. The standalone verified script and sanitized JSON are available in the accompanying offline research ZIP, without any proprietary binaries.

No MIOT or AVA writes, firmware changes, network/device access, or Valetudo+ production changes were performed. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`. No physical rewash causation has been established.
