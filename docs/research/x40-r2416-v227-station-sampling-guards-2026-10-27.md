# X40 R2416 v227 — mop-stain station guard / sampling-state analysis

**27 October 2026.** Offline read-only analysis of original owner-provided `node_lethe.so`, SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`. Continues v226 and the complete v197–v226 verifier chain. Robot, firmware, running Valetudo+, experimental gates and GitHub `master` untouched. Proprietary ELFs, owner-private diagnostic archives, maps, credentials and device identifiers remain off GitHub.

## Exact typed Blackboard inputs

Original `AvaNodeRoute::SendMopStainCheckCmd` at `0x7b8360–0x7b977c` constructs six exact strings through original adjacent same-register ADRP+ADD pairs. Addresses below are **native VAs**:

| Exact name | Key VA | ADRP+ADD | Native operation |
|---|---|---|---|
| `AvaSensors` | `0x9d3b00` | `0x7b83d0/0x7b83d4` | `Blackboard::get<AvaSensorsMsg*>` at `0x7b840c`; null pointer skips at `0x7b842c` |
| `open_stain_identify` | `0x9d6270` | `0x7b8584/0x7b8588` | `Blackboard::get<bool>` at `0x7b85a4`; lookup result guard `0x7b85e0` |
| `RobotMode` | `0x9d3fc8` | `0x7b85e8/0x7b85ec` | `Blackboard::get<_RobotMode>` at `0x7b8618` |
| `wash_status` | `0xa33250` | `0x7b8638/0x7b863c` | `Blackboard::get<WashStatus>` at `0x7b8668` |
| `mop_stain_check_time` | `0xa16168` | `0x7b8acc/0x7b8ad0` | `Blackboard::get<int>` at `0x7b8af0` |
| `ai_set_mop_is_dirty_data` | `0xa13488` | `0x7b8b10/0x7b8b14` | Guarded virtual lookup at `0x7b8b38` (v224/v225) |

**Typed-get success is not necessarily the retrieved Boolean's value**, so compiled lookup and result guard do not prove that stain identification is enabled in a live session.

## Native station-mode and numerical guards

- The returned `_RobotMode` code is compared against **16** at `0x7b8688`, equal branch `0x7b868c → 0x7b8a80`. The `WashStatus` code is compared against **2** at `0x7b8694`, equal branch `0x7b8698 → 0x7b8a80`. No original vendor enum description has been proven for these numeric values.
- A byte at `AvaSensorsMsg+0xfa` is read at `0x7b872c`, compared to **4** at `0x7b8730`, and conditionally branches to `0x7b8d7c`. Neither its calibrated sensor meaning nor value 4's interpretation is established.
- `mop_stain_check_time` has an initialized local **60** at `0x7b8ac8` before the typed integer lookup. The code compares a deque count against **4499** at `0x7b8b60/0x7b8b94`, then applies a native floating-point multiplier of **25.0** at `0x7b8bd0–0x7b8bd8` before an additional counter comparison. The user-facing time unit is **not known**.
- A separate retained countdown is tested with branch **`0x7b871c → 0x7b8bf4`** when nonpositive, where value **750** is staged at `0x7b8bf8` and written to the retained field at `0x7b8c0c` before constructing MCU numeric **33/1**. The positive branch decrements the retained value at `0x7b8720–0x7b8724`; the actual call cadence and real-time duration are unknown.
- The previously proven alternative retained-state branch constructs MCU numeric **32/0** at `0x7b88c4–0x7b88d8`. Both direct command-publication routes can bypass the dirty-mop named-key lookup on their local paths; previous state might still influence eligibility.

**Important:** These are exact compiled sampling and state-machine operations, not decoded OEM MCU commands, verified publication, station-wash start/stop events, a real second mop wash, or evidence of an AI-stain-triggered extra floor-cleaning task. Numeric 16/2/4/60/25/4499/750 must not be silently relabeled as particular times, modes, or motor actions.

## Verification and reproducibility

Complete source-only `X40-R2416-v227-sanitized-analysis-kit.zip`, SHA-256 **`86cd852599e59a5406ed4cddf36122eb1e16d1d734759e9b654085334d145907`**; **280,507 bytes**, **133 ZIP entries including checksum manifest**, **132/132 SHA-256 file checks** and ZIP CRC passed after fresh extraction. **All 11 v227 focused tests passed from the working source and again from the clean extraction**, including the full v197–v226 original PRIVATE evidence replay. New verifier checks **75 exact native instruction words, six key pointers, seven direct typed-call/MCU publication edges and 14 decoded branch edges**, with deliberate negative mutations of keys, guards, time multiplier and original ELF hash. An independent repo-local Python 3 stdlib checker passed **28 original words and six exact key pointers**. The ZIP contains no proprietary original ELF/PRIVATE input archives.

**Next research:** decode actual firmware enum/type descriptions for `RobotMode=16`, `WashStatus=2`, the sensor byte `+0xfa == 4`, and the consumer of numeric 32/33 if independently available. Separately pursue the still-unproven `stain_area_for_logic`→`SetExtraCleanArea`→new production cleaning-task launch. Never send experimental raw MCU commands.

Safety: `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`, unchanged `master`, robot and live Valetudo+.