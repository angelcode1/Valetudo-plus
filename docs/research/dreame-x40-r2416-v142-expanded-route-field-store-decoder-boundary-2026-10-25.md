# Dreame X40 R2416 — v142: expanded AArch64 store-decoder boundary

**25 October 2026 · offline analysis of sanitized v141 verifier plus newly assembled synthetic AArch64 instructions.** **No owner-private v62 ELF archive or v128 model-site evidence ZIP was available in this execution environment**. Consequently **the expanded original-firmware census was NOT RUN** and the existing ten possible source-level flag writers are not reduced.

## Concrete v141 classifier gap (reproduced)

The v141 `immediate_store()` audit covered selected AArch64 scalar GPR fixed-base-immediate instructions; zero direct relative-offset-overlap sites was **only** a bounded result for those decoded forms. v142 verified the classifier against 18 **independently assembled** AArch64 store-form examples (`clang --target=aarch64-none-elf`, `llvm-objdump`):

- `stp x3, x4, [x1], #16` — **post-indexed STP** (writes at original `x1`, not at updated `x1+16`); v141 decoder returned None although its description said it included post-indexed pairs.
- `stnp x3, x4, [x1,#48]` — non-temporal pair store; v141 decoder returned None despite a statically resolvable `+0x30` address.
- `str q0, [x1,#48]`, `stp q0,q1,[x1,#48]`, and `stur q0,[x1,#48]` — fixed-offset SIMD/FP stores omitted by the GPR-only census.
- `str x3,[x1,x2]`, `str w3,[x1,w2,uxtw #2]`, `strb` and `strh` register-offset forms require register value propagation; their offsets must not be invented.
- Atomic/exclusive and AdvSIMD structure opcode **families** include potential stores and loads. Family membership is explicitly flagged `unknown_not_proved_store`; it is not equated to a confirmed store or a confirmed field target.

Tests: **18 synthetic memory-form examples**, **5 negative/non-store controls**, **3 load-bit mutation checks**, total **26 passed**. The two v141 STP/STNP misses were separately asserted as reproducible. These examples are **synthetic, not extracted from proprietary firmware**, and their occurrence inside the real `AvaNodeRoute` constructor is **not known**.

## Source-dependent v142 verifier, held for private operator rerun

The separately delivered sanitized `X40-R2416-v142-sanitized-extended-store-boundary.zip` includes `x40_r2416_v142_extended_store_boundary_verify.py`, the v112–v141 regression modules, AArch64 fixture *assembly source*, detailed report, JSON, README, and SHA256SUMS. ZIP SHA-256: `448c4ee519f9cb1f710d7146cd157ffdab5500835bacc95f8b0d65f516655df7`. Clean extracted checksums, archive integrity and 26-check self-test passed.

```sh
unzip ~/Downloads/X40-R2416-v142-sanitized-extended-store-boundary.zip -d ~/Downloads
cd ~/Downloads/x40-v142-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v142_extended_store_boundary_verify.py --self-test
python3 x40_r2416_v142_extended_store_boundary_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test --out ~/Downloads/x40-v142-native-audit-results.json
```

The **last command was not run in this environment** because the two original source inputs were missing. With both owner-side files, it rechecks original ten SHA-256 ELF pins, v140 shared route argument anchors, v141 same-interval regressions and the existing ten model-specific source candidates, then reports additional fixed GPR/SIMD site candidates and unresolved dynamic indexed/atomic families in the **3,194 instruction** constructor interval.

**Interpretation:** expanded fixed-offset overlap means only `[base+offset]` overlap relative to *that instruction's base register*. It does not prove the base aliases the actual route object or that any write executes. Register-indexed, callee-mediated, subtree, cached-root and concurrent writes remain outside the addressed semantics. No one `SP+0xBC` writer has been observed executing, no live `enable_turbidity` value is established, and no additional physical mop wash is proven.

## Working safety state

No robot I/O, native runtime instrumentation, MIOT writes, changes to Valetudo, firmware, `master`, original launcher or recovery copies. Last operator-confirmed v74 baseline has `SmartHost=0` and `writeGateOpen=false`. No original vendor ELF, app APK, configs, model strings, credentials, maps, serial or actuator command bytes were redistributed or committed.
