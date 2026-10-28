# X40 R2416 v234 — typed AVA topic registry and bounded SENSORS publisher search

**27 October 2026.** Original SHA-256-pinned R2416 firmware; read-only, offline. Descended from v233 at `41609dc5cdcae79d0999b91b5dcd72bd91749925`. No robot connection or runtime execution, no AVA/MIOT/MCU commands, no cleaning activation, no `master` change and no vendor binaries/private diagnostics in Git.

## Newly verified AVA framework boundary

Original recovered `ava` ELF SHA-256: `30c0302537c1ae5b1b95d5debeb654ebbb9cb3ad8760fcfb31f2acb81836d826` (235,680 bytes). Original `node_health_lethe.so` SHA-256: `5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5`.

- `ava::AvaNode::SubscribeImpl` (`0x25810`) sets role flag `w1=0` at `0x2585c` and calls `ava::AvaTopics::CheckTopicType` at `0x25870 → 0x2ecd0`.
- `ava::AvaNode::AdvertiseImpl` (`0x26410`) sets role flag `w1=1` at `0x26448` and calls the same typed registry at `0x26454 → 0x2ecd0`. This is a **general API**, not a verified publisher of `SENSORS`.
- `CheckTopicType` looks up topic names and compares `type_info` identity and names; its name fallback invokes `strcmp@plt` at `0x2ed50 → 0xe590`. The role flag also selects a branch within mismatch handling (`0x2ed68 → 0x2f0c8` for zero). These are compiled control paths, not observed live registrations.
- `ava::GetTopicPublisherCount` (`0x23780`) returns zero on a missing topic entry (`0x237a0 → 0x238b0`) and loads the retained publisher count at `0x2387c` if present. **No live count was measured.**

## Bounded original native file census

All **35** stored v230 PRIVATE ZIP payload SHA-256 hashes and CRC pass; exactly **eight native components** were examined. The exact byte literal `SENSORS\0` occurs once across those eight components, in `node_health_lethe.so`, where v233 verified the typed subscriber. No publisher was identified in that bounded inventory. This **does not exclude** dynamic topic construction or a publisher in an uncollected native module, and does not prove any topic lacks a publisher.

## Proof boundary

The original health module uses the AVA named-topic `SENSORS` subscription and copies a 264-byte `AvaSensorsMsg`. Original route host v229 has a distinct `AsyncDeque::MultAsyncSubscribe<AvaSensorsMsg>` registration and mop-stain checker byte `+0xfa` retention. No bridging transport or same runtime Blackboard/pointer identity has been established. Likewise, no OEM byte meaning, physical mop rewash, or stain-induced second floor task has been observed.

## Reproducibility

The separate source-only v234 package includes the full Python 3 stdlib verifier, inherited v233 checker, **17/17** passed regression tests, a compact repo checker, sanitised report and SHA-256 manifest. Original private evidence is **not** redistributed. New native checks: **17 exact AVA instruction words, three decoded `BL` targets, three conditional/guard branch edges**, original ELF function identities, and negative tests that change subscriber role, advertiser role, subscription call, type mismatch comparison and count read.

Repo checker: `python3 docs/research/x40-r2416-v234-tools/x40_r2416_v234_repo_check.py --v230-private /path/to/X40-R2416-v230-gap-PRIVATE.zip`. It checks exact original bytes and prints `X40_R2416_V234_REPO_AVA_TOPIC_CONTRACT_PASS 17 3 35`.

## Next steps

Find an original publisher or authoritative schema for `SENSORS` in previously collected firmware *not* among the eight examined modules; resolve the route `AsyncDeque` provenance independently; separately trace `stain_area_for_logic` → `SetExtraCleanArea` → **new production cleaning task start**. No broad recollection or test MCU commands.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`; leave `master`, original v233, robot and active Valetudo+ unchanged.
