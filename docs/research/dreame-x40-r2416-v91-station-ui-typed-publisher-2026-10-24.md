# Dreame X40 R2416 — v91: typed STATION_UI native publisher

**2026-10-24 · Pinned original ELF static research, offline only.** No device commands, MIOT writes, reboot, native binary publication, or changes to working Valetudo+ v74.

## New sender-side proof

The `AvaNodeRoute` constructor advertises topic **`STATION_UI`** with the native RTTI **`ava_msg_station_set`**, and stores the publisher shared holder at route object offset **`+0x21e8`**. The separate `AvaNodeRoute::SendStationParamCmd()` routine loads that **same +0x21e8 member** and passes it to `AsyncDeque::MultAsyncPublish<ava_msg_station_set>`. Unlike the v90 report, which established a matching Blackboard key and typed message, v91 proves the *concrete output topic* and constructor-publisher-member relationship.

Original `node_lethe.so` SHA-256: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.

| ELF VA | Pinned operation |
|---|---|
| `0x9d7098` | NUL-terminated **`STATION_UI`** literal |
| `0x35c1e4–0x35c1e8` | Direct ADRP+ADD loads that exact topic |
| `0x35c1f0` | Constructs advertised topic string |
| `0x35c1f4`, `0x35c1fc` | Load exact GOT slot `0xb7d208` |
| `0xb7d208` | `R_AARCH64_GLOB_DAT` relocation to `_ZTI19ava_msg_station_set` |
| `0x35c204` | BL `AvaNode::AdvertiseImpl` PLT `0x274f20` |
| `0x35af88–0x35af94` | Builds `x23=route+0x2200`, retained through publisher store |
| `0x35c270–0x35c274` | Releases old control holder then `stur q0,[x23,#-0x18]` to **route+0x21e8** |
| `0x7c9e8c–0x7c9e90` | Reads same constant `0x21e8`; `x1=route+0x21e8` |
| `0x7c9e9c` | BL `MultAsyncPublish<ava_msg_station_set,ava_msg_station_set&>` PLT `0x275580` |

This positively distinguishes the typed station-set publisher from the similarly named `STATION_LED` or `STATION_CLEANSET` topics also present in the constructor.

## Bounded receiver census

The ten original library files in the owner's v62 evidence archive were checked with **ten individual SHA-256 pins** and a byte-level census: exactly **one** `STATION_UI\0` occurrence, in `node_lethe.so`; and **zero** occurrences of the particular mangled template spelling `MultAsyncSubscribeI19ava_msg_station_set`. This is **not a device-wide subscriber absence proof**: the receiver can live in a separate process, binary or library not collected, use type-erased/topic-configured subscription, or construct the topic name dynamically. No actual message delivery was observed.

The v90 compiled `DustStrategy::SetStationFan` producer and `SendStationParamCmd` consumer share the Blackboard name `Ava_Station_Ctrl` and type `ava_msg_station_set`, but their live Blackboard instance identity remains unproven. Nor is the fan example a mop-rewash command.

## Verification and private provenance

The separate operator-delivered **sanitized** `X40-R2416-v91-sanitized-station-ui-20261024.zip` contains standalone Python-stdlib verifier `x40_r2416_v91_station_ui_publisher_topic_verify.py`, full technical report and README. The original private source ZIP `X40-R2416-v62-readonly-20261023T051829Z.zip` is an *input*, not included. The verifier validates ten source hashes, exact topic reference, GOT relocation, constructor storage, same publish member, direct PLT targets and bounded absent-symbol census. With `--self-test` it rejects **19** byte-level instruction/literal/relocation mutations.

```sh
python3 x40_r2416_v91_station_ui_publisher_topic_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

```text
X40_V91_STATION_UI_EXACT_TOPIC_ADVERTISE_STATIC_PASS
X40_V91_STATION_UI_RTTI_IS_AVA_MSG_STATION_SET_PASS
X40_V91_ADVERTISE_STORE_ROUTE_OFFSET_0X21E8_STATIC_PASS
X40_V91_SEND_STATION_USES_SAME_PUBLISHER_MEMBER_PASS
X40_V91_TEN_PINNED_ELF_TOPIC_LITERAL_CENSUS_PASS topic_occurrences=1 typed_subscriber_symbols=0
X40_V91_INSTRUCTION_LITERAL_RELOCATION_MUTATIONS_REJECTED count=19
LIMIT: topic and publisher are statically proven; physical receiver, delivery, Blackboard instance and rewash command NOT proven
```

**Next evidence gate:** identify a real `STATION_UI` subscriber and decoding of the 5-byte `ava_msg_station_set` payload, preferably with a new *read-only, owner-reviewed* firmware evidence snapshot or existing passive logs. Do not probe guessed station opcodes. Independently show an R2416-supported `special_push_clean_dish` writer and bridge real turbidity failure through `r2343_start_rewash` to physical additional mop-wash actuation before calling the feature operational.

**Safety:** The operator's last-confirmed working X40 remains on Valetudo+ **v74**, native `SmartHost=0`, experimental `writeGateOpen=false`, launcher restored and rebooted, old verified v70/v73/parent/vendor recovery files retained. No live changes or deployment are needed for v91.
