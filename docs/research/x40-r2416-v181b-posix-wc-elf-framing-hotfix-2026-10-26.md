# X40 R2416 v181b — portable byte-count framing hotfix

**Research maintenance date:** 26 October 2026. **Parent finding:** [v181 cross-module topic leads](x40-r2416-v181-cross-module-literal-leads-2026-10-26.md). This is a *collector portability correction*, not a native firmware discovery, robot-side patch, or permission to enable CleanGenius.

## Real failure and cause

On the user's macOS host, the v181 test `test_executable_shell_two_fixture_maps` failed in `parse_framed_stream()` with `noncanonical module size`. The shell sent the raw text produced by `wc -c < file` into a strict `__X40_V181_FILE__|name|size` framing header. BSD/macOS `wc` may left-pad the decimal count, whereas the Python parser correctly demands the canonical ASCII form `[1-9][0-9]*`. Linux-side test fixtures did not reproduce this difference.

## Narrow fix (no parser weakening)

Apply the following changes to the remote read-only POSIX shell template for **both** allowlisted private ELF files:

```diff
-x40n1=$(wc -c < "$x40laser") || exit 25
-x40n2=$(wc -c < "$x40route") || exit 25
+x40n1=$(wc -c < "$x40laser" | tr -d '[:space:]') || exit 25
+x40n2=$(wc -c < "$x40route" | tr -d '[:space:]') || exit 25
```

The collector then still requires sizes between 64 and 33,554,432 bytes; each length-delimited payload must match its declared size and be ELF64 little-endian AArch64. The resulting package was independently versioned to `x40-v181b-sanitized`; it does not overwrite the user's earlier v181 folder. All other boundaries (two exact native module names, one user-run SSH session, user-only local binary copies, no robot writes) remain intact.

## Regression and deliverable

New test `test_shell_size_fields_canonical_with_bsd_padded_wc` executes the actual remote `/bin/sh` command with two synthetic AArch64 ELF files and a fixture `wc` wrapper intentionally emitting a left-padded count. It asserts the canonical `|96` header and parses both complete ELF payloads. Along with all prior tests, **26 unit tests passed**. A clean extraction of the ZIP passed its SHA256SUMS and reran all tests successfully. **These are offline fixture tests, not a successful live two-module collection.**

Private self-contained ZIP distributed in the research conversation:
`X40-R2416-v181b-sanitized-two-module-wc-portability-hotfix.zip`
SHA-256: `9b89b48caa974c6e741d8adb72091f83377bb6c88b60ffb5683d0b814957b02f`.

After downloading to the Mac:

```sh
cd ~/Downloads
unzip X40-R2416-v181b-sanitized-two-module-wc-portability-hotfix.zip
cd x40-v181b-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v181b.py test_x40_r2416_v181b_xref.py
python3 x40_r2416_v181b_private_two_module_collector.py --ssh root@192.168.8.149 --ssh-auth password --output-dir ~/Downloads
```

The final command is explicitly **user-run**, read-only, and saves original native modules only in a private local directory. No proprietary ELF file is included in GitHub or the ZIP. When collection succeeds, inspect the `v181b-two-module-xrefs-...-SANITIZED.json` output before making any claims about actual subscription, Blackboard writes, or floor reclean.

## Evidence boundary and release safety

The v180c 105-file probe showed `AI_STAIN_CLEANING` in `node_laser_transfer.so` and `now_stain_cleaning_id` in `liblethe_route_nodes.so`. These are literal matches only; the receiver, writer and any autonomous second pass are not yet verified. Preserve working v74, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0` and `writeGateOpen=false`. No robot access or firmware changes were performed by the assistant during this hotfix.
