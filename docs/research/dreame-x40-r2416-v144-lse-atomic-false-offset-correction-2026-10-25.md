# X40 R2416 v144 — correct false fixed offsets in AArch64 LSE atomic instructions

**25 October 2026 · static, source-independent opcode analysis. No robot I/O.**

## Result

v142/v143 mistakenly interpret some ARM64 LSE atomic read-modify-write instruction bits as a signed 9-bit **immediate store displacement**. AArch64 LSE `STADD`, `LDADD` and `SWP` instructions address `[base]` without an encoded displacement. The old decoder could claim a spurious `base+0x30` field write by decoding their register/operation bits as `imm9`.

An independently assembled ARM64 fixture (Clang + LLVM disassembly) establishes **12 LSE RMW opcodes**, nine non-LSE controls, and **eight synthetic false-positive fixed-overlap store reports** produced by v143. The v144 decoder intercepts the `bit21=1, mode00` LSE family before the unscaled-immediate classification, conservatively marks it `unknown_not_proved_store` with **no invented offset**, and preserves actual fixed `STUR`/`STTR` and indexed `STR` semantics.

**Verification:** 56 inherited v143 assertions + 77 new assertions = **133 PASS**. An independent compile/disassemble check confirmed **19** fixture instruction words. Clean ZIP extraction reran the 133 assertions and a standalone 21-opcode family/false-overlap test. SHA-256 manifest and ZIP integrity passed.

Example original opcodes from independently assembled fixture:

| Assembly | AArch64 word | v143 | v144 |
|---|---|---|---|
| `stadd x3,[x1]` | `f823003f` | false fixed `+0x30` | LSE; no literal displacement |
| `ldadd x3,x4,[x1]` | `f8230024` | false fixed `+0x30` | LSE; no literal displacement |
| `swp x3,x4,[x1]` | `f8238024` | false fixed `+0x38` | LSE; no literal displacement |
| `sttr x3,[x1,#48]` | `f8030823` | correct fixed `+0x30` | preserved |
| `stur x3,[x1,#48]` | `f8030023` | correct fixed `+0x30` | preserved |
| `str x3,[x1,x2]` | `f8226823` | variable indexed | preserved |

## Important source boundary

**The original vendor v62 ten-ELF archive was not accessible to the native analysis container**, despite being visible in the conversation's file records and a materialization request returning a nominal path. Consequently **the actual 3,194-instruction firmware route-constructor scan has NOT been run in v144**. Eight false positives are solely a synthetic-fixture count; they are **NOT** claimed to occur on the X40.

This correction does not prove whether any actual base register aliases `AvaNodeRoute+0x30`, whether a callee changes the Blackboard shared_ptr, whether StationWash uses the same live Blackboard, or whether one of the ten remaining candidate R2416 `SP+0xBC` flag stores executes. Neither live `enable_turbidity` nor a second physical mop wash is proven.

## Owner-side reproducibility

Sanitized verifier bundle `X40-R2416-v144-sanitized-lse-atomic-correction.zip`, SHA-256 `7dca82bb49859b1dd7eaae528601ce32f26a2a802416d8933cb84f2a1ff52f70`, includes Python-stdlib v144 source, v112–v143 dependencies, assembly fixture, research report, aggregate JSON, README and SHA256SUMS. No vendor ELF or APK is distributed.

```sh
unzip ~/Downloads/X40-R2416-v144-sanitized-lse-atomic-correction.zip -d ~/Downloads
cd ~/Downloads/x40-v144-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v144_lse_atomic_store_decode_verify.py --self-test
python3 x40_r2416_v144_lse_atomic_store_decode_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --self-test --out ~/Downloads/x40-v144-native-store-census.json
```

**Only the source-independent self-test and clean extraction were run here.** The final original-firmware command must run locally with the private v62 input. It source-pins ten ELFs and v140/v141/v143 regressions and compares the old and corrected census for the identical 3,194 original instructions. It outputs bounded sanitized counts/address categories and refuses to overwrite existing files.

No original binaries, device configurations, raw model identifiers, credentials, logs, maps or hardware commands committed. Preserve last operator-verified Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher, backups and untouched `master`.
