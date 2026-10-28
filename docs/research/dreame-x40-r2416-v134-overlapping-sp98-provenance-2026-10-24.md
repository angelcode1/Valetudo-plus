# Dreame X40 R2416 — v134 overlapping SP+0x98 stack-slot provenance

**24 October 2026 · offline, ten SHA-256-pinned original native ARM64 libraries and owner-supplied sanitized exact model-site evidence.** No device actions or proprietary ELF redistribution.

## Finding

The v133 exact-model direct-CFG audit left **ten possible direct writers** to the separate turbidity model gate word at `SP+0xBC`. v134 audits another stack slot, `SP+0x98`, read at native instruction `0x470b40` and tested at `0x470b44`.

Original AArch64 direct `STR W` and `STR X` instructions targeting `SP+0x98` are inventoried with source opcode checks: **25 32-bit sites plus one 64-bit site**. Reverse reaching-last-direct-definition analysis under the combined v133 model-specific branch graph produces **eight 32-bit sites and one 64-bit site**.

| Possible last direct store | Width | Source-backed local kind |
|---|---|---|
| `0x4707e0` | W32 | shared block writes immediate one |
| `0x47085c` | W32 | immediate one |
| **`0x47130c`** | **X64** | X2 pointer-derived from original allocation address plus eight; **not a Boolean** |
| `0x4734a8` | W32 | zero from source-verified nonmatching model regex |
| `0x475bbc` | W32 | nearby immediate one |
| `0x4774d0` | W32 | W24 positive source, with earlier v125 alternative-path checks |
| `0x4775d8` | W32 | immediate W24 one |
| `0x477768` | W32 | immediate W24 one |
| `0x478134` | W32 | `CSET NE` on private actual primary model comparison, proven nonmatch against source-hashed literal, so locally one |

The original X64 store overlaps the bytes subsequently read as W32. It is therefore **unsound** to propagate the false result of the regex at `0x4734a8` as a globally known Boolean at `0x470b40`; one of the possible last stores writes a pointer-derived value to the same address.

The native empty-`DEV_MODEL` comparison at `0x4707d8` is nonmatching on the verified normal missing-key path, but pruning just its fallthrough **does not exclude** store `0x4707e0`: the shared block `0x4707dc` has **six additional compiled incoming branches** (`0x471980`, `0x471998`, `0x4719ac`, `0x4719c0`, `0x4719d4`, `0x4719ec`). Each instruction and branch target is individually source-pinned. The bounded graph independently confirms the stack last-definition set and ten flag-writer candidates remain unchanged after that one branch is pruned.

### Reproducibility

The **sanitized** owner-side archive `X40-R2416-v134-sanitized-overlapping-stack-provenance.zip` has SHA-256 `c4ffde39078a192802b8ef3f54191af9e58dc4145a9b94310ef4ae56dd59351e`. Contains standalone Python 3 standard-library verifier `x40_r2416_v134_overlapping_stack_provenance_verify.py`, all v112–v133 sanitized regression scripts, sanitized findings JSON, detailed report, README, and checksum manifest. Original firmware archives, disassembly, APK binaries, raw model values, private configs, secrets, station control parameters and logs are **not** included.

```sh
unzip ~/Downloads/X40-R2416-v134-sanitized-overlapping-stack-provenance.zip -d ~/Downloads
cd ~/Downloads/x40-v134-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v134_overlapping_stack_provenance_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

The original source/previous-research regression and the **32 independent native source instruction/literal/corridor mutations** pass their checks. ZIP CRC and the SHA256SUMS manifest pass.

**Limits:** the inventory covers direct `STR W/X` stores to one exact stack slot, and direct native-branch edges only. Do **not** treat it as full alias-aware SSA, complete memory-opcode coverage, concrete executed paths, observed native `enable_turbidity`, or evidence of a real dirt-triggered second physical mop wash. These nine stack-definition sites are not the ten possible `SP+0xBC` turbidity-gate writer sites.

**Safe baseline preserved:** last operator-confirmed Valetudo+ v74, native SmartHost=0, experimental `writeGateOpen=false`, original launcher and rollback assets. The robot, executable code, GitHub `master`, and other branches were not changed.
