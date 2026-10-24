# Dreame X40 R2416 — v136 direct stack flag overlap and alias-surface audit

**24 October 2026. Original SHA-256-pinned ARM64 vendor firmware, offline only.** This is a conservative addendum to v135b, not an executed instruction trace or a runtime firmware modification.

## Source and scope

The source-pinned `node_lethe.so:ProcessModelInfo()` spans 11,345 original 4-byte AArch64 instructions from `0x46fd40` through `0x47ae80`. The relevant model-group eligibility flag is read with a 32-bit load at `0x470be4` from `[SP,#0xBC]`, and the branch tests that value at `0x470be8`.

v136 independently scans original instruction opcodes for SP-based signed-offset paired integer stores, unsigned-offset GPR byte/halfword/word/X64 stores, and signed-unscaled GPR forms whose **byte footprints overlap `[SP+0xBC,SP+0xC0)`**.

- **61** direct integer store instruction sites overlap those four bytes.
- **All 61 are 32-bit paired `STP W` stores**, including instructions based at `SP+0xB8` whose *second* 32-bit element writes the flag.
- **No additional SP-based byte, halfword, single-W32 or X64 stores** overlap in the decoded forms.
- The 61 decoded store sites equal the independently established earlier original direct SP+0xBC writer census, and their full sorted address/opcode pairs are pinned by a feature-specific digest.

This is not proof of full opcode/alias completeness: SIMD/vector, atomic, arbitrary-register-addressed, indirect or called-function memory writes are outside this specific GPR SP-immediate census.

## Stack pointer materialization census

Independently scanning original `ADD (immediate, Xd,SP,#imm)` finds **64** instructions.

- **62** produce nonframe stack addresses; all point to `SP+0x110` or higher, clear of the local flag word.
- At `0x46fd4c`, **`MOV X29,SP`** establishes a frame-pointer alias. It is retained separately rather than falsely counted as above the protected flag region. In a separate complete native-disassembly inspection, X29 appears as the frame setup/restore register, with no observed memory dereference through `[X29,...]` in this function. The standalone verifier pins the frame-pointer creation opcode but does not claim global frame-pointer alias freedom.
- At `0x4716ec`, **`ADD SP,SP,#0x420`** restores the frame.

A second full site/opcode digest pins all 64 SP-add instructions. This narrows the **explicit in-function direct-address-taking** concern, but does not rule out pointer arithmetic after construction, implicit aliases, nonlocal writes, exception paths or runtime execution of callees.

## Conservative primary-model regression

The original owner-sanitized native model identifier `site_0x473540`, verified normal missing-`DEV_MODEL` case, original branch constraints, original 61-store inventory, v134 wide overlapping SP98 source and v135b conservative stack consumer handling were rerun.

- **Ten** possible last *direct* flag writer sites remain:
  `0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.
- Conservative bounded product model still has **118,989** abstract states and **35** terminal source/writer combinations.
- No unique **executed** writer, live `enable_turbidity` value, or genuine dirt-triggered **second physical mop wash** was established.

These abstract state counts are offline graph constructs, not physical events or execution frequencies. Source-register positivity is conditional on earlier local-corridor assumptions; it does not prove a running device's feature state.

## Reproducibility and privacy

The owner-side sanitized `X40-R2416-v136-sanitized-stack-alias-surface.zip` has SHA-256 **`172f238cecacbf36076865a0ce9a5f41d0d02c17558723bf52ea3e0b1546e2e7`**. It contains:

- `x40_r2416_v136_flag_alias_surface_verify.py`, standalone Python standard-library verifier;
- necessary v112–v135 sanitized Python regression dependencies;
- technical report, aggregate-only JSON, README, and SHA256SUMS.

The original v62 firmware ZIP and sanitized v128 model-site ZIP are used only as **private local inputs**:

```sh
unzip ~/Downloads/X40-R2416-v136-sanitized-stack-alias-surface.zip -d ~/Downloads
cd ~/Downloads/x40-v136-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v136_flag_alias_surface_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Checks **passed on original source and on a separate clean ZIP extraction**:

```text
X40_V136_ORIGINAL_ELF_PINS_PASS count=10
X40_V136_DIRECT_FLAG_OVERLAP_GPR_CENSUS_PASS all_paired_w32=61
X40_V136_SP_POINTER_MATERIALIZATION_BOUND_PASS constructors=62 minimum_offset=0x110
X40_V136_ACTUAL_MODEL_CORRELATED_LAST_DIRECT_WRITERS_PASS candidates=10 combos=35
X40_V136_SOURCE_MUTATIONS_REJECTED count=29
X40_V136_SYNTHETIC_INSTRUCTION_DECODER_TESTS_PASS count=10
LIMIT: no whole-program alias freedom, executed writer, effective turbidity setting, or physical rewash verified
```

29 independent original opcode mutations are rejected using feature-specific complete site/opcode digests, not the ten original whole-ELF checksums as the mutation oracle. Ten synthetic tests exercise GPR store-width overlap (including 64-bit, W32 and subword forms), near misses, and stack pointer address construction. ZIP CRC and SHA256SUMS passed.

No proprietary firmware, complete native disassembly, Dreamehome APK, raw MODEL, robot configuration, account secret, logs, maps or hardware command bytes are committed. No device access, runtime patches, branch deletion or modification of `master`, the working Valetudo+ v74 configuration, `SmartHost=0`, `writeGateOpen=false`, original launcher or recovery files occurred.

**Next:** use complete register/alias-aware reaching definitions across the remaining ten source-verified writer corridors. If source-only proof remains underdetermined, identifying a **specific actually executed** writer requires safe, expressly authorized bounded runtime observation.
