# X40 R2416 v182 — Native stain-ID writer, subscriber and handled-stain state

**2026-10-26** · Offline native research using two privately collected, user-supplied AArch64 modules. Neither ELF is included in GitHub, and no robot access, firmware updates, task control or CleanGenius activation was performed by the assistant.

## Conclusion

v182 resolves the two static native-code boundaries previously missing after v178–v181:

- **Blackboard writer:** `pointcloud::PointCloudProcess::FluidSlowDown(...)` in `liblethe_route_nodes.so` conditionally writes an integer from a classified candidate record to the exact key `now_stain_cleaning_id`. The key string and retained register reach the virtual typed setter at `0xc26bfc`. The integer comes from `LDRSW x2, [x19,#0x78]` at `0xc26bec`. The virtual vtable slot `+0x20` and integer boxing correspond to `BT::Blackboard::set<int>` compiled at `0x58dcb0` (equivalent virtual call at `0x58dcfc`).
- **Topic subscriber:** `ava_line_laser::MapAccumulatorNode::NodeSubscribe()` in `node_laser_transfer.so` constructs the exact `AI_STAIN_CLEANING` topic string at `0x12b338`–`0x12b33c`, constructs a typed `int*` callback, and calls `AvaNode::SubscribeImpl` at `0x12b3e0`. Three ELF GOT relocations identify the typed callback manager/invoke and the exact bound method `MapAccumulatorNode::ProcessStainCleanInfo(int*)` at `0x112390`.
- **Received value storage:** `ProcessStainCleanInfo` atomically stores its received integer with AArch64 `STLR` at `0x1123a4`.
- **Compatible stain-state consumer:** `ava_line_laser::SemanticFuser::UpdateCleanedStainId()` at `0x1db720` performs `LDAR` of a pending ID at member offset `+0xfd0`, matches a stain record's ID at `+0x3a0`, sets a byte flag at `+0x2ae`, conditionally changes the record's integer state `3 → 2`, and clears the pending ID by `STLR wzr` at `0x1db788`. The receiver callback stores to a nested object's `+0xfd0` field, but the exact runtime **object identity** of this nested pointer and the `SemanticFuser` instance is not independently established.

The earlier `node_lethe.so` v176–v178 research identified changed `now_stain_cleaning_id` readout and an `AI_STAIN_CLEANING` publisher stored at `route+0x28b0`. These findings now provide the necessary **compiled producer/consumer components** for an integer stain-handling event. However, same-instance Blackboard sharing, runtime execution, message delivery and any decision to schedule an **additional cleaning pass** remain unproven.

**Interpretation:** the receiver-side state change is consistent with marking a stain as handled, **not** a direct floor-reclean command. Neither of the two v165 floor revisits is causally linked.

## Source binary fingerprints

| Module | SHA-256 | Length |
|---|---|---:|
| `node_laser_transfer.so` | `16b487f486fb34d8fe85fb6e383243100657e0769d6df823aa13c34643644856` | 4,905,056 bytes |
| `liblethe_route_nodes.so` | `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e` | 19,160,912 bytes |

Matches the user-collected v181b private manifest. The exact topic string is at `0x41ac58` in the laser module, the key at `0x1011ff0` in the route module.

## Static native proof table

| Native VA | Meaning |
|---|---|
| Laser `0x12b338` | `ADRP` for `AI_STAIN_CLEANING` string |
| Laser `0x12b364` | load callback method GOT entry `0x4bca20` → `ProcessStainCleanInfo(int*)` |
| Laser `0x12b374` | load `int*` callback manager via GOT `0x4bc6b0` |
| Laser `0x12b36c` | load `int*` callback invoke via GOT `0x4bce20` |
| Laser `0x12b3e0` | call typed topic `SubscribeImpl` |
| Laser `0x11239c`, `0x1123a4` | read incoming int and atomically store it |
| Laser `0x1db764`, `0x1db788` | compare handled stain ID then atomically clear pending ID |
| Route `0xc267e0` | literal address for `now_stain_cleaning_id` |
| Route `0xc26ab0`, `0xc26ab8` | conditional classification and FP-threshold checks; precise semantic meaning not established |
| Route `0xc26bb4`, `0xc26bec` | reuse Blackboard key, retrieve record's signed integer ID |
| Route `0xc26be4`, `0xc26bfc` | virtual typed setter slot `+0x20` invoked with boxed integer |
| Route `0x58dce4`, `0x58dcfc` | independent typed `BT::Blackboard::set<int>` implementation showing same boxing and virtual slot |

## Testable evidence and boundaries

The private ZIP `X40-R2416-v182-sanitized-native-stain-id-writer-subscriber.zip` (SHA-256 `c6704587b63f39031b32ac85b42ae204e4705644d0005272210ec641c4983745`) contains `x40_r2416_v182_cross_module_native_verify.py`, `test_x40_r2416_v182.py`, the sanitized result JSON, report, README and checksums. **30 offline tests pass with the two original binaries**, including 17 private-ELF and mutation tests; without originals 13 pass and 17 skip. Fresh ZIP extraction, ZIP contents and SHA256SUMS passed. The verifier uses only the Python standard library and checks AArch64 instruction sites, literal addresses, direct BL targets and ELF relocation symbols in addition to SHA-256.

This Git commit includes **no original firmware bytes**. The standalone full verifier and tests were supplied separately as the ZIP and are referenced here by immutable checksum.

## Safety and next action

Do **not** enable CleanGenius, SmartHost or experimental writes on the basis of this result. Keep working v74: `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. The next essential proof is a task-planner transition that actually requests a second area pass in response to an AI dirt decision. The static stain-ID handling pipeline does **not** demonstrate that transition.
