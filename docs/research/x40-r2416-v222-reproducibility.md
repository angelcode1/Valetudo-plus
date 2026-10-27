# X40 R2416 v222 — reproducibility and exact proof boundary

**27 October 2026.** Branch based on v221 research, not `master`. The robot and working Valetudo+ were not accessed or modified. The original ELF, PRIVATE firmware collector ZIP and other personal/device data remain outside GitHub and the source-only release.

## Complete offline source-only archive

`X40-R2416-v222-sanitized-analysis-kit.zip`  
SHA-256 **`c2ef9698a800c77c734a803556adaaf6e5bda91b649e1f45a95c056a559f30ff`**; **224,482 bytes**, **103 entries**, **102 internal file hashes verified**, ZIP CRC passed. Includes Python 3 standard-library-only verifiers and tests spanning v197–v222, source-only sanitized reports, v222 native instruction/call anchors, and the separate 21-word/seven-edge checker. **No proprietary original ELF files or uploaded PRIVATE JSON/ZIP payloads included.**

Verification scopes are reported separately to avoid overstating them:
- Full 11-test **source-directory** v222 suite passed, including the complete v197–v221 original-native and user-private evidence replay and sanitized create-only output.
- The clean-extraction full replay **did not complete within the execution limit**; its pass is unconfirmed.
- From that exact clean extraction, **all 10 isolated native/mutation tests passed**, and the standalone checker against the SHA-pinned original host ELF passed **21 words and seven decoded calls**.

```sh
cd ~/Downloads
unzip X40-R2416-v222-sanitized-analysis-kit.zip
cd x40-r2416-v222-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V222_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V222_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V222_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V222_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V222_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V222_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V222_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V222_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v222.py
python3 verify_x40_r2416_v222.py \
 --prior-zip "$X40_V222_PRIOR_ZIP" \
 --delta-zip "$X40_V222_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V222_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V222_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V222_SCOPE_SANITIZED" \
 --scope-private "$X40_V222_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V222_PROCESS_SANITIZED" \
 --process-private "$X40_V222_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v222-new-SANITIZED.json"
# X40_R2416_V222_ASYNC_BOUNDARY_STATIC_PASS 36 9 3 2
```

The full output destination is **create-only**, so choose a new path. Alternatively run the smaller, independently tested checker with the original collector ZIP alone:

```sh
python3 x40_r2416_v222_repo_check.py --prior-zip "$X40_V222_PRIOR_ZIP"
# X40_R2416_V222_REPO_ASYNC_BOUNDARY_PASS 21 7
```

The corresponding GitHub checker lives at `docs/research/x40-r2416-v222-tools/x40_r2416_v222_repo_check.py` on this branch.

## What has and has not been demonstrated

The original host contains a conditional descriptor wake-byte `n` → `AsyncDeque::MultPublishProcess` route, two indirect deque callable invocations, a typed `ava_ai_new_cmd` publisher helper with a separate callback path, and an AI CleanBot condition-variable queue with its own wait/notify/write. The latter has zero **direct BL** calls to the two selected other queue/typed publisher entry points. This does **not** prove distinct runtime queue objects, actual callback identity, an AI-stain command publication, a physical reclean or a dock rewash.

**Next offline priority:** identify the actual callback registration and production AI new-command publisher consumers, then look for causally linked stain-area/extra-clean task-state transitions. Keep all safety gates disabled and `master` untouched.

See [technical findings](x40-r2416-v222-async-callback-boundary-2026-10-27.md) and [sanitized JSON](x40-r2416-v222-async-callback-SANITIZED.json).
