# Dreame X40 R2416 — v79: MIOT 4:50 named string topic and subscriber

**2026-10-24. Offline-only pinned firmware research. No live device access or changes.** The operator's working v74 remains installed with `SmartHost=0`, `writeGateOpen=false` after the verified 1 → 0 setting test, launcher restoration and reboot.

## Original firmware provenance

- Original `node_msg_cvt.so` SHA-256: `71c55d905e8e68c4d97d6cc108b251b879cf007ce8515d6f90767dd53d7d0da8`
- Original `node_lethe.so` SHA-256: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`

The original binaries are owner-private and were **not** committed.

## New static evidence

The v78 MIOT service-4 property-50 `MsgClean::SetSwitchSet` extracts the string at `0x10b100`, and calls `AvaNodeMsgCvt::SetSwitchMsg` at `0x10b114`.

In `node_msg_cvt.so`, source topic reference `0xa1a08` ADRP + `0xa1a0c` ADD resolves to literal **`STATE_TO_LOGIC`** at VA `0x164888`. `AvaNode::AdvertiseImpl` is called at `0xa1a2c`; its publisher result is stored at `this+0x440` at `0xa1ab8`. The same publisher member is used by `SetSwitchMsg` at `0xbe404` immediately before the `Publisher<std::string>::publishWithLine` call at `0xbe41c`.

In `node_lethe.so`, source reference `0x363668` ADRP + `0x36366c` ADD resolves to the *same exact topic* at VA `0x9d7848`. GOT relocation `0xb79660` resolves to `AvaNodeRoute::ReceiveStateListProcess(std::string*)`. `std::function<void(std::string*)>` binding occurs at `0x363698`, followed by a typed `AvaNode::Subscribe<std::string>` at `0x3636a8`. That receiver calls `AsyncDeque::MultAsyncSubscribe<std::string,...>` at `0x56b208`; another pinned GOT relocation `0xb7d1c0` identifies the eventual `ReceiveStateListProcessSUB(std::string*)` callback. At `0x593624`, `ReceiveStateListProcessSUB` calls RapidJSON `GenericDocument::ParseStream`, followed by member/key-value processing.

### Bounded compiled route

```text
MIOT 4:50 set (registered in v78)
 → MsgClean::SetSwitchSet → AvaNodeMsgCvt::SetSwitchMsg
 → Publisher<std::string> topic STATE_TO_LOGIC
 → AvaNodeRoute::ReceiveStateListProcess(std::string*)
 → AsyncDeque::MultAsyncSubscribe<std::string>
 → ReceiveStateListProcessSUB(std::string*)
 → RapidJSON ParseStream
 → [individual k/v dispatch NOT YET PROVEN]
```

This is a **matching type-and-topic static producer/subscriber pair**, rather than live delivery evidence. The parser's treatment of individual keys and the eventual setter must be established separately. v76 independently established `StateShowAndSave::SyncStateChange` typed Blackboard writes for the three named switches, but **no direct connecting call** from this JSON receiver has been proven. Similarly, shared live Blackboard identity with the station controller and physical reclean/rewash remain unknown.

**Negative control:** the v77 enum-24 `SetSmartWashSwitch()` handler uses a distinct string `smart_wash_switch` key; it must not be substituted for integer `smart_auto_wash_switch`.

## Reproduction

The user-delivered sanitized archive `X40-R2416-v79-sanitized-state-to-logic-20261024.zip` contains a standalone Python 3 verifier and a longer report. It loads the user's *local original private* `X40-R2416-v62-readonly-20261023T051829Z.zip`; pins two source SHA-256 hashes, exact AArch64 opcode anchors, ELF file-backed topic references, PLT call symbols, dynamic GOT callback relocation names, and 17 one-byte mutation refusals. It contains **no vendor ELF or private settings**.

```text
X40_V79_MIOT_4_50_STATE_TO_LOGIC_PUBLISHER_STATIC_PASS
X40_V79_STATE_TO_LOGIC_TYPED_SUBSCRIBER_STATIC_PASS
X40_V79_CALLBACK_TO_ASYNC_JSON_PROCESSOR_STATIC_PASS
X40_V79_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=17
LIMIT: per-key k/v dispatch into SyncStateChange, shared live Blackboard, and physical reclean/rewash unproven
```

## Next technical gates

Resolve `ReceiveStateListProcessSUB` JSON key-dispatch and any transition to `StateShowAndSave::SyncStateChange`, including signed value semantics; then prove station Blackboard writer/reader object identity and the real turbidity-to-extra-wash execution path. Do not send guessed MIOT auto-switch values, force any dirt sensor or run active scripts merely to satisfy a software gate.

Preserve verified v74 with gate closed and all working rollback binaries, original launcher and configuration. No installation, reboot or settings write required.
