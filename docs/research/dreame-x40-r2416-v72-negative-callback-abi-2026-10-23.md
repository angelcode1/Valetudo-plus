# Dreame X40 R2416 — v72 native negative-message callback ABI

**2026-10-23 | Offline static evidence, no device commands or proprietary binaries.**

## Objective and live checkpoint

Restore Dreame's native CleanGenius dirt-based reclean and turbidity-based rewash under Valetudo+, rather than substituting manual mop-wash commands.

The operator has successfully deployed the v70 read-only direct MIOT 4:50 observer. Their fresh response reported `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1` and the default `auto_disable_smart_host_when_positive` policy. Older cached status can remain unavailable because the direct reader intentionally bypasses the state-poll parser.

## New validated R2416 callback calling convention

Pinned ELF: `ava/lib/node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.

Within `ancp::StateShowAndSave::SyncStateChange(...)`, all four state-dependent negative-message paths use the same code shape: construct a message from an exact literal; store the one-byte value `1` in a stack slot; load/check the callback-presence pointer at `[sp+0xd0]`; load the function entry into `x3` from `[sp+0xd8]`; and invoke `blr x3` with `x0=sp+0xc0` (callable object), `x1=x28` (constructed message string object), `x2=&one-byte-true`.

| Fixed string | Literal VA | Path entry | Flag | Indirect invoke |
|---|---:|---:|---:|---:|
| `{"SmartAutoMop":-1}` | `0xa2f7c0` | `0x891cb4` | `[sp+0x94]` | `0x891cf8` |
| `{"SmartAutoMop":-2}` | `0xa2f7d8` | `0x891c20` | `[sp+0x95]` | `0x891c64` |
| `{"SmartAutoWash":-1}` | `0xa2f868` | `0x891afc` | `[sp+0x96]` | `0x891b40` |
| `{"SmartAutoWash":-2}` | `0xa2f880` | `0x891a68` | `[sp+0x97]` | `0x891aac` |

**What this establishes:** a guarded indirect native callback accepts a constructed message and a true-valued byte. It is **not** proof of the callback's registration, transport, MIOT 4:50 persistence semantics, a dirtiness measurement, or a physical second wash. The live `SmartAutoMop=-1` remains semantically unresolved.

## Verification and next gate

The companion sanitized downloadable v72 ZIP includes a standard-library Python verifier (no vendor bytes). With the owner's private v62 archived ELF it reports:
```
X40_V72_PINNED_NATIVE_FOUR_CALLBACK_ABI_STATIC_PASS
X40_V72_EIGHT_INSTRUCTION_TAMPER_REJECTIONS_PASS
LIMIT: callback target, delivered MIOT state, native dirt event and physical rewash unproven
```
It checks archive CRC, ELF SHA, load segments, literal construction, guard, true-flag stores, argument registers, and indirect calls. Eight mutated instructions are rejected independently of the full SHA guard.

Next: identify the callback object/handler registration and its downstream transport; separately resolve the R2416 eligibility producer `special_push_clean_dish` and the turbidity-to-second-dock-wash causality. Observe-only `VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1` remains an explicit, off-by-default test flag; it does not enable SmartHost. Keep experimental firmware writers disabled (`VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`). Do not modify installed Valetudo, native firmware, existing rollback binaries or launcher merely for this offline evidence.

**Scope:** documented static research only. Cleanup of obsolete /data test directories is distributed as a separate dry-run-first user-side script, never automatically invoked.