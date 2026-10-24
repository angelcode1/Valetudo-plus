# X40 R2416 — v90 typed station-control producer and publisher

**2026-10-24 · Offline pinned original ELF analysis. No robot access or state change.** This corrects and deepens the v89 station-control finding. All original vendor binaries, private XML, settings, map data, credentials and identifiers remain outside GitHub.

## Verified compiled producer and type

`RobotCollectDust::DustStrategy::SetStationFan(StationFanState, unsigned char)` in original `liblethe_tactics_tree.so` constructs key **`Ava_Station_Ctrl`**, stages a five-byte **`ava_msg_station_set`** value, and invokes an indirect setter-style Blackboard method. The v89 report had correctly found the literal and indirect call but could not yet identify the payload type.

- Key literal `0x33f1f0`, direct ADRP/ADD at `0x22b300–0x22b304`; exact reference census over the two pinned original ELFs remains one per binary
- Blackboard-like holder loaded from the fan object `+0x38` (`0x22b2c4`), then virtual receiver at `0x22b32c`
- Fan state bytes staged at `0x22b338–0x22b344`; message bytes at `0x22b35c` and `0x22b364`; an exact 1 is placed in message byte four
- `0x22b34c` ADRP and `0x22b360` LDR resolve **GOT `0x3c3268`**, whose `R_AARCH64_GLOB_DAT` relocation explicitly identifies `linb::any::vtable_for_type<ava_msg_station_set>::table`
- At `0x22b358` a `+0x20` virtual slot is read; `0x22b36c`, `0x22b374`, `0x22b378` pass typed payload `x2`, key `x1`, then `blr x3`. The exact same slot/calling convention is independently visible in the library's typed `BT::Blackboard::set<WashControlMsg&>` at `0x21d894`, `0x21d8a4`, `0x21d8bc`.

**Conclusion:** the compiled fan path inserts a typed station message into a Blackboard. It is not an inferred dock wash or an identified rewash producer. The object's actual dynamic identity remains unobserved.

## Verified compatible reader and publisher

`ancp::AvaNodeRoute::SendStationParamCmd()` in original `node_lethe.so`:

- Reads route root Blackboard from `AvaNodeRoute+0x30` at `0x7c9cd0–0x7c9cf4`, constructs literal **`Ava_Station_Ctrl`** at `0x7c9d1c–0x7c9d20` (VA `0xa24f70`), and looks up entry through virtual slot `+0x10` at `0x7c9d44–0x7c9d58`
- Checks the `SafeAny` type at `0x7c9d74–0x7c9d98`: its GOT `0xb7a050` has `R_AARCH64_GLOB_DAT` for the explicit type-name `_ZTS19ava_msg_station_set`. The type check can also take an exception branch on mismatch; do not assume arbitrary keys/types are accepted
- Copies the typed 32-bit field and adjacent byte at `0x7c9dd0–0x7c9de0`
- Erases the keyed entry on the verified successful path through virtual slot `+0x30` (`0x7c9e5c–0x7c9e70`)
- Calls PLT `0x275580` at `0x7c9e9c`, symbol `ancp::AsyncDeque::MultAsyncPublish<ava_msg_station_set,ava_msg_station_set&>`

The two modules therefore share a **compiled key + type contract**, stronger than simply finding the same string. However, `SetStationFan` uses its own object-held Blackboard; `SendStationParamCmd` uses route-root `+0x30`. **Runtime shared-object identity and actual message delivery are not proven.**

## Rewash boundary remains intact

The earlier v67 `WashDonePrecess()` path checks `TurbidityResultFail`, a wash eligibility flag, and `special_push_clean_dish` before writing `r2343_start_rewash`. `SendStationTaskTip()` consumes that marker, updates `wash_times` and clears the marker; it has **no direct station-set publisher call** in the checked body. The newly identified typed station-fan writer does not bridge those rewash conditions to a physical second wash. The fan state must not be relabelled as a rewash opcode.

## Repeatable offline verifier

The owner-side sanitized ZIP `X40-R2416-v90-sanitized-station-set-bridge-20261024.zip` contains standalone `x40_r2416_v90_station_set_any_bridge_verify.py`, the full detailed report and README. It reads the owner-private v62 evidence ZIP **only in memory**, checks exact original ELF SHA-256, AArch64 instructions, bounded literal reference inventories, GOT `GLOB_DAT` symbol names and PLT branch target, and rejects **39** independent instruction/literal byte mutations. No native binaries are included.

Original SHA-256 pins:
- `node_lethe.so` `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so` `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`

```sh
python3 x40_r2416_v90_station_set_any_bridge_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V90_TYPED_STATION_FAN_BLACKBOARD_SET_STATIC_PASS type=ava_msg_station_set
X40_V90_STATION_CTRL_KEY_AND_TYPE_CONSUMER_STATIC_PASS
X40_V90_STATION_COMMAND_TYPE_CHECK_AND_PUBLISH_STATIC_PASS
X40_V90_MATCHING_COMPILED_KEY_TYPE_CONTRACT_STATIC_PASS
X40_V90_PINNED_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=39
LIMIT: matching type/key and virtual setter/getter are compiled evidence, not live Blackboard identity, rewash command, or physical actuation
```

### Next specific question

Identify the actual subscription/recipient of `MultAsyncPublish<ava_msg_station_set>`, its station payload-field semantics, and whether there is a *separate, R2416-reachable* rewash producer into this command channel. Also establish the station subtree's live Blackboard inheritance, and any R2416-compatible writer for `special_push_clean_dish`. No guessed auto-switch writes, synthetic soil, forced wash cycles or firmware modification.

**Safety:** Keep the verified native v74 state: `SmartHost=0`, `writeGateOpen=false`, original launcher restored, native baseline unchanged on reboot, and v70/v73/parent/original backups retained. No device action warranted for v90.
