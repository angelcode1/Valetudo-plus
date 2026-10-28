# X40 R2416 v143 — source-independent STTR fixed-offset decoder correction

**25 October 2026. Offline and read-only.** No robot access, firmware modification, MIOT writes, configuration changes or actuator commands.

## Verified decoder omission

The sanitized v142 ARM64 decoder does not recognize scalar AArch64 **STTR / STTRB / STTRH** (unprivileged, signed 9-bit fixed offset) because it omits the mode-2 / bit21=0 branch in its GPR memory classifier. These are potential *statically addressable* memory stores; their omission means v142's fixed-offset census may miss relevant instructions.

v143 adds only that opcode class, checks the bit22 store/load discriminator, sign-extends imm9, derives the width, and keeps dynamically register-indexed or atomic-family instructions unresolved rather than fabricating a fixed offset. All initial opcode samples were independently assembled with clang targeting AArch64 and disassembled using llvm-objdump.

| Synthetic opcode | AArch64 instruction | Grounded interpretation |
|---|---|---|
| `f8030823` | `sttr x3,[x1,#48]` | +48, width 8 bytes |
| `b8030823` | `sttr w3,[x1,#48]` | +48, width 4 |
| `38030823` | `sttrb w3,[x1,#48]` | +48, width 1 |
| `78030823` | `sttrh w3,[x1,#48]` | +48, width 2 |
| `f8430823` | `ldtr x3,[x1,#48]` | **load, not store** |

**Tests performed:** 26 v142 baseline assertions plus 30 additional v143 assertions, **56 passed**. New checks cover four STTR forms, four corresponding LDTR negative cases, signed immediate and byte-range overlap boundaries, indexed-store uncertainty, five prior nonstore negatives, load-bit mutations, and a bounded synthetic instruction-corridor scan.

## Reduced dependency for native-source rerun

The v143 downloadable full Python-standard-library verifier can perform this **route constructor store-form census using only the operator-held original ten-ELF v62 ZIP**. It no longer requires the separate sanitized v128 model-comparison evidence: that input was used to regress **which R2416 model-flag paths are possible**, not to decode AArch64 stores within the route constructor.

Its original-source code path SHA-pins the ten vendor ELFs, checks the v140 exact route-to-model/four-tree argument handoffs, reproduces the v141 101 (all base registers) / 98 (`x0`) `+0x30` field-load census, and examines 3,194 original instructions for expanded direct base-relative store forms.

**Important status:** the source-dependent scan was **not run here**. The earlier owner-private v62 conversation attachment was located through conversation file metadata, but a requested materialization was not accessible in the container runtime. No actual STTR site or changed firmware overlap count is asserted. The existing **ten possible native model flag writers** are not further pruned.

## Replay

Download `X40-R2416-v143-sanitized-sttr-coverage.zip`, SHA-256 `bf5ecd2e7894838ddea3d3382c70e45b139506bdab1649eab0c049a7b830861c`, which includes v143 verifier and v112–v142 sanitized regression modules, synthetic AArch64 assembly, report, README, sanitized JSON and SHA256SUMS.

```sh
unzip ~/Downloads/X40-R2416-v143-sanitized-sttr-coverage.zip -d ~/Downloads
cd ~/Downloads/x40-v143-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v143_unprivileged_store_coverage_verify.py --self-test
python3 x40_r2416_v143_unprivileged_store_coverage_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --self-test --out ~/Downloads/x40-v143-native-route-store-audit.json
```

The last command is prepared but **was not executed on the private vendor source in this turn**. A fixed offset is relative to *its own base register*, which is not proved to alias the route's `+0x30` Blackboard shared-pointer field. Caller effects, indirect writes, runtime node alias/remap, actual native `enable_turbidity` value, uniquely executed flag writer and physical second mop wash all remain unverified.

No original vendor firmware, app binaries, raw model identities, account material, maps, private configuration or actuator values are committed. Working v74 Valetudo+, `SmartHost=0`, `writeGateOpen=false`, original launcher/recovery copies and GitHub `master` remain unchanged.
