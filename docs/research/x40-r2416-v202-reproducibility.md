# X40 R2416 v202 — offline replay and provenance

**27 October 2026.** This research branch descends from v201 and preserves the native-`RobotNode` correction and all earlier X40 research. No robot command, firmware change or `master` update. Raw original firmware and unredacted configurations remain owner-private.

## Downloadable complete v197–v202 kit

`X40-R2416-v202-sanitized-analysis-kit.zip`  
SHA-256: `7e5995b503a0c48a45c0dc6810fa5a631fb767989374c96f31d9647cf57205d3`

This source-only ZIP contains the complete, standard-library Python 3 verifiers for v197–v202, all inherited focused test sources, the v202 88-instruction anchor table, v202 ten-test suite, sanitized findings/JSON and the per-file checksum manifest. The ZIP has 19 entries including the checksum manifest. Its CRCs and all **18 internal payload SHA-256 hashes passed**. With the two owner-private ZIPs, all **10 focused v202 tests passed**, including ELF tamper, altered fixed instruction, altered expected branch, bounded call-census and create-only overwrite refusal. The complete v197–v201 replay passed with five native ELF whole-file SHA pins and 18+7 earlier collection payload checksums.

```sh
unzip X40-R2416-v202-sanitized-analysis-kit.zip
cd x40-r2416-v202-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V202_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V202_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v202.py
python3 verify_x40_r2416_v202.py \
  --prior-zip "$X40_V202_PRIOR_ZIP" \
  --delta-zip "$X40_V202_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v202-new-SANITIZED.json"
# X40_R2416_V202_SUBTREE_BLACKBOARD_BINDING_STATIC_PASS
```

The report path must be unused. This does not extract native firmware or send commands to the robot.

## Smaller GitHub-side checker

`x40-r2416-v202-tools/x40_r2416_v202_repo_check.py` is a compact bounded independent checker. It reuses the v201 repository ELF reader and verifies the original `libbehaviortree_cpp.so` hash, **20 exact word anchors**, **11 decoded branches/calls**, and the scoped onInit direct-branch-link census. This **is not** the full 88-word, 20-edge v202 replay; use the downloaded ZIP for that.

```sh
python3 docs/research/x40-r2416-v202-tools/x40_r2416_v202_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V202_REPO_FRESH_CACHE_STATIC_PASS 20 words 11 edges
```

## Evidence limits

Compiler evidence proves that fresh child-factory construction binds a supplied Blackboard before initialization and that cached-root attach in the inspected `SubtreeConditionNode::onInit` has no *direct* `setBlackboard` call. It cannot prove the presence or absence of indirect rebinding, cache reuse in a real cleaning job, equality of producer/consumer pointers, stale data, R2416 active calibration subtype, or physical extra washing. Avoid uploading owner-private ZIPs to public GitHub; keep experimental CleanGenius controls disabled.

See [v202 research](x40-r2416-v202-subtree-blackboard-cache-2026-10-27.md) and [machine-readable sanitized result](x40-r2416-v202-subtree-blackboard-SANITIZED.json).
