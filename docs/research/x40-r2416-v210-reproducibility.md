# X40 R2416 v210 — reproducibility and source-only handoff

**27 October 2026.** v210 analyzes the newly uploaded owner-private *live* resolver ZIP; the robot was not contacted by the assistant and `master` remains unchanged.

## Complete standalone offline kit

`X40-R2416-v210-sanitized-analysis-kit.zip`

**SHA-256:** `dd7b298a98761f54201317b1d2032dc02cef90a06374356c74bc976091c70d83`

The ZIP contains **46 files including a checksum manifest**, the complete Python 3 standard-library-only v197–v210 verifier source chain, the previous regressions, v210 13-test suite, the original private evidence metadata auditor, and the new *optional* metadata-only scope collector. The archive includes **no private firmware or collector ZIPs**. Clean-extraction validation passed ZIP CRC, **45 file SHA-256 checks**, all **13 focused v210 tests**, and full v197–v209 native replay against the previously provided private ZIPs.

```sh
unzip X40-R2416-v210-sanitized-analysis-kit.zip
cd x40-r2416-v210-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V210_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V210_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V210_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V210_LIVE_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"

python3 -m unittest -v test_verify_x40_r2416_v210.py
python3 verify_x40_r2416_v210.py \
 --prior-zip "$X40_V210_PRIOR_ZIP" \
 --delta-zip "$X40_V210_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V210_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V210_LIVE_ZIP" \
 --out "$HOME/Downloads/X40-R2416-v210-new-SANITIZED.json"
# X40_R2416_V210_LIVE_RESOLVER_ZERO_NEW_STATIC_PASS 6 6 0
```

The `--out` filename must not exist: report overwrite is refused.

## Small repository-side audit

`docs/research/x40-r2416-v210-tools/x40_r2416_v210_repo_check.py` performs a hash-pinned audit of the new 933-byte live resolver ZIP only, not the full native replay:

```sh
python3 docs/research/x40-r2416-v210-tools/x40_r2416_v210_repo_check.py \
 --live-resolver-zip "$X40_V210_LIVE_ZIP"
# X40_R2416_V210_REPO_LIVE_RESOLVER_PASS 6 3 0
```

It verifies archive integrity, metadata schemas, zero new files, and exact 2× duplication of three known tree libraries.

## Optional metadata-only tree-plugin coverage probe

The ZIP's `collect_x40_r2416_v210_scope.py` records directory coverage without copying firmware file contents:

```sh
python3 collect_x40_r2416_v210_scope.py \
 --ssh root@ROBOT_IP \
 --out-prefix "$HOME/Downloads/X40-R2416-v210-scope"
```

**Only run this if you decide to authorize a read-only live inventory.** Substitute your robot's address; it requires your Mac's normal SSH authentication. It inspects only the fixed roots `/tmp/lib/tree_lib`, `/usr/lib/tree_lib`, `/ava/lib`, `/tmp/ava/lib` to depth eight and records root presence, regular-file counts, symlink counts, error indicators and matching `AiStainMop`/tree-plugin path names. It never follows symbolic link targets or downloads any ELF/XML/config contents. **SSH mode was not tested on the actual robot**; the 13 v210 tests exercise synthetic listings and offline originals only.

Output is two create-only JSON files: `X40-R2416-v210-scope-PRIVATE.json` (matching paths; keep off public GitHub) and `X40-R2416-v210-scope-SANITIZED.json` (coverage counts only). A zero-match result still does not prove absence from other roots, dynamic registration, symlink targets, deeper trees, or cwd-dependent paths.

**Evidence boundary:** This uploaded live resolver records six paths of three already collected libraries and zero new file payloads, but no independently verified live runtime registration, cleaning task start or physical reclean/rewash. Preserve the disabled experimental CleanGenius write gates and the working v74 baseline.

See [v210 research](x40-r2416-v210-live-resolver-coverage-2026-10-27.md) and [sanitized findings](x40-r2416-v210-live-resolver-SANITIZED.json).
