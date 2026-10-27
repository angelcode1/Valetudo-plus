# Dreame X40 R2416 v222 — asynchronous callback pump and typed AI publisher

**27 October 2026.** Read-only static study of the original SHA-pinned `node_lethe.so` (SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`). Extends v221 and its full v197–v221 verification chain; no robot commands, firmware write, running Valetudo+ modification, private ELF or diagnostics, or `master` changes.

## Verified conditional compiled paths

1. **Descriptor-driven async pump:** `ancp::AsyncDeque::SpinCallback(int)` at VA `0x3179b0` calls `read@plt` at `0x3179f4`, looks for byte `0x6e` (ASCII `n`) at `0x317a24–0x317a30`, and conditionally invokes `AsyncDeque::MultPublishProcess@plt` at `0x317a44 → 0x271fa0`.
2. **Deque callback drain:** `ancp::AsyncDeque::MultPublishProcess` at `0x3190b0` has guarded mutex/deque processing and invokes dynamically stored callable objects through `BLR` at `0x3191e0` and `0x319354`. Callback identity and live execution were not measured.
3. **Typed AI new-command publisher helper:** `ancp::AsyncDeque::_ProcessPub<ava_ai_new_cmd>` at `0x5d7e30` contains an indirect publisher callback `BLR` at `0x5d7f58` and calls `std::condition_variable::notify_one@plt` at `0x5d8074 → 0x2773a0`. The compiled template is not proof that a new command was published or that any subscriber initiated cleaning.
4. **AI handler's local queue:** `AvaNodeRoute::ProcessAiCleanBot` at `0x5cebc0–0x5cfa80` contains a local `std::condition_variable::wait()` at `0x5cf3d8`, `notify_one()` at `0x5cf148`, `write()` at `0x5cf15c` and `deque<function<void()>>` push-helper at `0x5cf5b0`. Its complete bounded direct `BL` scan contains **zero direct calls** to the selected separate `MultPublishProcess@plt` or `_ProcessPub<ava_ai_new_cmd>` bodies.

**Critical scope:** The original binary contains at least two different asynchronous *compiled processing paths*. This does **not** prove they are different runtime queue objects, nor a specific connection among them. Indirect calls, callbacks, object aliasing, other libraries and runtime scheduler changes are not excluded. The existence of `ava_ai_new_cmd` publication support must not be equated to an AI stain-caused new cleaning task.

## Verification and provenance

Complete **source-only** archive `X40-R2416-v222-sanitized-analysis-kit.zip`, SHA-256 **`c2ef9698a800c77c734a803556adaaf6e5bda91b649e1f45a95c056a559f30ff`**, **224,482 bytes**, **103 entries including checksum manifest**, **102/102 internal file SHA-256 checks**, ZIP CRC passed.

- Original source-directory full test suite: **11/11 passed**, including v197–v221 original private evidence replay and create-only redacted output validation.
- Clean-extraction focused static/mutation test subset: **10/10 passed**; independently checked the standalone 21-word/seven-edge repo checker against the original firmware.
- A separate clean-extraction **full historical replay exceeded its run limit**; it is not reported as clean-extraction passed. The source-directory full replay passed.
- New full verifier checks **36 exact AArch64 instruction words, nine decoded BL edges, three indirect callback BLR sites**, and absence of two selected direct calls from the AI handler. Tamper tests cover wake-up read, queue dispatch, indirect callbacks, publisher notification, local wait and SHA protection.

**Open proof gap:** locate the actual callback registration/object identity from production stain classification through `stain_area_for_logic`, `SetExtraCleanArea` and command publication to new production cleaning-task dispatch. Neither a physical floor second pass nor automatic dock rewash is observed.

Safety defaults remain `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No robot access, raw private input upload or `master` mutation.
