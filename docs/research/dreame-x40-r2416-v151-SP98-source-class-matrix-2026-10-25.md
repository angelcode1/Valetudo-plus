# X40 R2416 v151 — source-verified SP+0x98 class matrix

25 October 2026. Offline SHA-pinned original ten-ELF firmware plus actual sanitized v128 model comparison site `0x473540`. No robot access.

Replayed v150 native graph with 19 additional authenticated primary-model comparison exclusions, yielding **52,713 correlated states**, **16 terminal classes**, and five candidate *last direct* stores to model eligibility flag `SP+0xBC`.

Source-backed per-writer reaching `SP+0x98` **classes**:

| Last direct store | REGEX_ZERO | LOCAL_POSITIVE_SOURCE_UNRESOLVED_REG_CLOBBERS | WIDE_POINTER_LOW32_UNKNOWN |
|---|---|---|---|
| `0x475bc4` | no | yes | yes |
| `0x4774d8` | no | yes | yes |
| `0x4775a4` | **yes** | yes | yes |
| `0x478160` | no | yes | yes |
| `0x47826c` | no | yes | yes |

**Conclusion:** a *proved* zero source at `SP+0x98` would leave only `0x4775a4` within this bounded static last-direct-write model. However, **no live zero or nonzero reading is established**. In the positive or pointer-unknown classes, five writer alternatives remain; simply assuming nonzero does not identify execution.

The companion offline v151 Python-stdlib verifier intercepts/rechecks v150's actual native state graph, asserts exact class matrix and static graph state counts, and passes source-free tamper/consistency checks. Original firmware and sanitized v128 evidence are private *inputs* and are not bundled. Companion ZIP `X40-R2416-v151-sanitized-SP98-writer-classes.zip` SHA-256 `0189d5eeae6dff88d4f07dd65a6769d7c1f57bc46625c9299c5ecd16dd5317d7`.

**Not proven:** one actually executed writer, whole-program indirect/alias effects, live `enable_turbidity`, StationWash shared Blackboard object, or dirt-triggered extra physical mop wash. No native settings, Valetudo runtime or GitHub master changed.
