# Dreame X40 R2416 — v124 flag-store value provenance and CFG dominance

**24 October 2026 · offline study of SHA-256-pinned original R2416 AArch64 ELF files; sanitized public documentation.** No robot, app/cloud account, firmware, station, MIOT or Valetudo runtime action.

## New verified finding

v123 narrowed the native `ProcessModelInfo()` direct SP-relative stores overlapping its model-group feature flag at `SP+0xBC` from 61 to **13** potential writer sites under the exact `dreame.vacuum.r2416` model's verified name/regex branch constraints.

v124 verifies the actual `STP` destination register for `SP+0xBC` and a nearby local code window that sources each register:

- **One** store (`0x4703fc`) writes the architectural zero register `WZR`.
- **Twelve** store sites use a register which a preceding, source-pinned local instruction sets with `MOVZ #1`.
- But a conservative CFG dominator test shows the local positive initializer dominates its store at only **eight** sites. At the other **four** sites, the CFG permits a route to the store that bypasses that initializer. It would be unsound to claim those registers are necessarily one on all paths.
- A bounded potential-last-direct-store check finds all **13** sites still admit a route to the R2416 comparison without another *inventoried direct* `SP+0xBC` store. Thus v124 does not eliminate another candidate; it provides more precise value-source evidence.

| Store | Compiled local source | Positive initializer dominates in bounded CFG? |
|---|---|---|
| `0x4703fc` | `WZR` zero | Not applicable |
| `0x474cd0` | Nearby `MOVZ #1` | No |
| `0x475bc4` | Nearby `MOVZ #1` | Yes |
| `0x4761c4` | Nearby `MOVZ #1` | No |
| `0x476598` | Nearby `MOVZ #1` | Yes |
| `0x476798` | Nearby `MOVZ #1` | Yes |
| `0x4773dc` | Nearby `MOVZ #1` | No |
| `0x4774d8` | Nearby `MOVZ #1` | Yes |
| `0x4775a4` | Nearby `MOVZ #1` | No |
| `0x4776b4` | Nearby `MOVZ #1` | Yes |
| `0x47776c` | Nearby `MOVZ #1` | Yes |
| `0x478160` | Nearby `MOVZ #1` | Yes |
| `0x47826c` | Nearby `MOVZ #1` | Yes |

The original native `STP` destination register is independently checked at every site, and each positive source is checked against the original `MOVZ` register and a SHA-256 digest of the complete local intervening instruction window (short *source check*, not redistribution of binary code).

### Scope and caution

The dominator graph models direct AArch64 branch/fallthrough instructions with the v119/v122/v123 pinned exact-model and regex decisions. **Even an eight-site dominance result is not whole-program SSA proof:** alternate register redefinitions, stack aliases, exceptions, indirect branches and runtime model state remain unmodelled. The 13 candidates are potential sites, not 13 observed executions.

It remains unknown which final value reaches the native guarded `enable_turbidity` setter for the actual X40 R2416. A real dirt/turbidity result → `r2343_start_rewash` → an additional **physical mop wash** has also not been proven. The generic Dreamehome app package studied in v120/v121 contained no obtained R2416-specific plugin to settle this.

## Repeatable offline verifier

The separately delivered owner-side **sanitized** `X40-R2416-v124-sanitized-flag-value-provenance.zip` (SHA-256 `3927900acc2e0a3ef07e4906098b5b432c3a36c7ab066bcf39e5be23e765d88d`) includes the Python-stdlib `x40_r2416_v124_flag_value_sources_verify.py`, its v112–v123 sanitized regression dependencies, report, aggregate JSON, README and SHA256SUMS. The original owner-private v62 archive is **not** included, committed or redistributed.

```sh
cd ~/Downloads
unzip X40-R2416-v124-sanitized-flag-value-provenance.zip
cd x40-v124-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v124_flag_value_sources_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Original test output (verified):

```text
X40_V124_TEN_ORIGINAL_ELF_SHA256_PINS_PASS count=10
X40_V124_V123_REGEX_CFG_REGRESSION_PASS candidates=13
X40_V124_DIRECT_STORE_SOURCE_VALUE_CENSUS_PASS zero=1 local_one=12
X40_V124_SOURCE_DOMINANCE_AUDIT_PASS one_dominated=8 one_not_dominated=4
X40_V124_ALL_13_REMAIN_POTENTIAL_LAST_DIRECT_WRITER_PASS scoped=bounded_cfg
X40_V124_INDEPENDENT_NATIVE_SOURCE_MUTATIONS_REJECTED count=49
LIMIT: 8 locally initialized paths dominate stores, 4 do not; no live R2416 turbidity eligibility or second wash established
```

The 49 mutation tests modify distinct original store, initializer and local instruction-window bytes independently without relying on an ELF-wide hash mismatch. Ten original firmware SHA-256 source pins are separately validated.

## v125 investigation

Trace alternate incoming edges and reaching register definitions for the four nondominated sources, and account for indirect memory/exception paths before attempting a final R2416 feature-eligibility verdict. Do **not** send guessed station commands or change live native switches.

**Safe baseline preserved:** last operator-confirmed Valetudo+ v74, native SmartHost=0, experimental `writeGateOpen=false`, original launcher and rollback files intact. No live device or executable Valetudo code modifications.
