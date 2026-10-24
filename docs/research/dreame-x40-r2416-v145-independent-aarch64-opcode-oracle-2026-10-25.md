# Dreame X40 R2416 — v145 independently assembled AArch64 memory decoder oracle

**25 October 2026 · offline regression, no robot I/O.**

## Source-independent verified result

The v142/v143/v144 ARM64 memory decoder needed confidence beyond selected hand-written sample words. A new fixture contains **1,857 synthetic AArch64 memory instructions**, individually compiled by Clang's `--target=aarch64-none-elf -march=armv8.5-a+lse` and independently disassembled by LLVM objdump. Its complete `x40_v145_assembled_opcode_oracle.tsv` fixture has SHA-256 `77934d23a47c1dae5a6a146ebeadff415242d53259c93d47f60de40366bef925`.

Cases vary base `x0/x1/x19/sp`, scalar 8/16/32/64-bit and SIMD/FP store/load widths, immediate offsets (including edge crossing of `+0x30`), STUR/LDUR, STTR/LDTR, STP/STNP, pre/post-indexing, register-offset addressing and atomic/exclusive examples.

| Independent synthetic verification | Observed count |
|---|---:|
| Assembled opcode oracle rows | **1,857** |
| Definite fixed-offset store cases matching expected offset and width | **1,028** |
| Variable/atomic store cases not assigned fabricated fixed offsets | 23 |
| Load/non-store cases never called fixed stores | 806 |
| Semantic classifier mismatches in this finite corpus | **0** |
| v144 inherited decoder checks rerun | 133 |
| Individually changed fixture offset/width expectations rejected without whole-file hash shortcut | 24 |
| Independently reassembled machine words matching TSV | **1,857 / 1,857** |

This is **not** exhaustive coverage of AArch64 and gives no guarantee for untested opcodes, unmodelled pointer aliases or concurrent/callee writes. The fixture is **entirely synthetic**; no original vendor binary or assembly is included.

## Explicit original-firmware source boundary

The ten-ELF v62 ZIP was visible as a prior conversation file reference but unavailable as bytes to this execution container after an attempted materialization. **No original firmware opcode census was executed in v145.** Consequently v141's narrow original native facts (101 `+0x30` LDR X patterns, 98 x0-base, zero narrow-form direct stores) are not broadened by v145; v137's **10 possible direct model-gate writers remain unchanged**, and no uniquely executed site has been observed.

An owner-side v62-only source scan remains prepared in the downloadable verifier kit. It checks original SHA-256 source pins, v140/v141 route-Blackboard handoffs and reclassifies the 3,194 original AArch64 instructions with the v144 corrected decoder. It reports categorized sites and counts, not vendor code, and refuses output when source is missing or checks fail. v128 companion evidence is not needed for this *route memory-store* census.

## Reproduce

Operator package: `X40-R2416-v145-sanitized-assembled-opcode-oracle.zip` SHA-256 `18ae0072b8ae6833c8373bbc362c6a36c9a3479867c7f27e91ecd3643a3d68cd`.

```sh
unzip ~/Downloads/X40-R2416-v145-sanitized-assembled-opcode-oracle.zip -d ~/Downloads
cd ~/Downloads/x40-v145-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v145_assembled_oracle_and_source_gate_verify.py --self-test
python3 x40_v145_standalone_compiler_oracle_replay.py x40_v145_assembled_opcode_oracle.tsv

# Source-dependent, requires original owner-private v62 ZIP (NOT run in analysis environment):
python3 x40_r2416_v145_assembled_oracle_and_source_gate_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --self-test --out ~/Downloads/x40-v145-native-store-census.json
```

The standalone compiler replay needs a working AArch64-capable Clang and `llvm-objdump`. The repository also contains a corresponding pinned fixture replay tool in `util/x40_v145_standalone_compiler_oracle_replay.py` that accepts the TSV from the downloaded ZIP. The repo tool does not require native binary or original model string.

**Next:** inspect the actual source-census JSON and trace pointer/register definitions for any reported fixed-offset or unresolved store forms. Do not assert a route alias, real StationWash Blackboard identity, `enable_turbidity` value or dirt-triggered second physical mop wash from a synthetic opcode match alone.

No device, firmware, native runtime, MIOT, Valetudo `master`, SmartHost setting, write gate or recovery assets were altered.
