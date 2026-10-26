# X40 R2416 v204 — reproducibility and safety boundaries

**27 October 2026.** Continues v203 and preserves the corrected native `RobotNode` selection from v195. Offline original-ELF verification only, no robot access, no MIOT/AVA writes, no firmware changes and no change to `master`.

## Complete source-only offline analysis kit

`X40-R2416-v204-sanitized-analysis-kit.zip`

SHA-256: **`ee9718094c87e4b8a46c3074acc898a3e49125f7b94d5980a85cd092112d0b90`**

The ZIP contains **24 files including the checksum manifest**. Clean-extraction validation checked all **23 per-file SHA-256 hashes** and ZIP integrity; **all ten focused v204 tests passed**. The package includes the complete stdlib Python v197–v204 verifier chain and regression tests, v204 sanitized JSON and report, and no raw owner ELF, original private configuration, maps or credentials.

```sh
unzip X40-R2416-v204-sanitized-analysis-kit.zip
cd x40-r2416-v204-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V204_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V204_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v204.py
python3 verify_x40_r2416_v204.py \
  --prior-zip "$X40_V204_PRIOR_ZIP" \
  --delta-zip "$X40_V204_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v204-new-SANITIZED.json"
# X40_R2416_V204_CACHE_MISS_FLAG_STATIC_PASS
```

Choose a fresh report filename; the verifier refuses overwrite. This invokes v197–v203 checks, including five original whole-ELF SHA-256 pins, checksums for **18+7** stored collector files, and the new v204 **50 exact native instruction checks and 16 branch/call target checks**. No vendor code is executed.

## Small independent repository-side native checker

The branch also contains `docs/research/x40-r2416-v204-tools/x40_r2416_v204_repo_check.py`. It has no external dependencies and verifies the original `libbehaviortree_cpp.so` SHA pin and a bounded subset of **20 original instruction words and 10 branch targets**, without extracting firmware or importing earlier versions.

```sh
python3 docs/research/x40-r2416-v204-tools/x40_r2416_v204_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V204_REPO_CACHE_FLAG_STATIC_PASS 20 10
```

The bounded checker was run successfully on the original owner-private archive. Use the offline ZIP for the full v197–v204 regression replay.

**Evidence limits:** A missing cache key sets the local post-build insertion flag to zero and thus can bypass storing a fresh subtree. A null tree pointer in an existing cache entry sets the flag to one and allows a successful new tree pointer to be saved. Key-creation's zero-pointer write does not by itself prove owner-destruction invalidation. Cache hits attach a non-owning root. Actual live `StationWash` cache occupancy, producer/consumer Blackboard equality, dangling pointers, turbidity-triggered physical dock wash, and AI-stain-triggered extra floor cleaning are **unobserved**. Keep experimental CleanGenius writes disabled.

See [v204 sanitized research](x40-r2416-v204-cache-miss-null-entry-2026-10-27.md) and [v204 machine-readable findings](x40-r2416-v204-cache-miss-SANITIZED.json).
