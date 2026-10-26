# X40 R2416 v206 — reproducibility, privacy and proof limits

**27 October 2026.** Research branch follows v205 and retains v195's corrected native `RobotNode` model. No robot collection, AVA/MIOT publish, firmware changes, running Valetudo+ modifications, or `master` changes.

## Complete source-only v197–v206 replay

Artifact: `X40-R2416-v206-sanitized-analysis-kit.zip`  
SHA-256: **`0ca4cb7a41dd6c2ea9186d2b01032fd0f3a6f2403ff05521814cddc0aa0d1c53`**

The ZIP has **32 entries including a checksum manifest**, and its **31 per-file SHA-256 hashes** and archive CRCs passed clean-extraction verification. It includes all stdlib Python 3 verifiers from v197 through v206, prior regression tests, v206 fixed instruction anchors, a full 158-child generated-tree census, vtable-onInit relocation verification, sanitized research report and JSON, and a smaller bounded repo-side verifier. The original native binaries, unredacted device files and the two private collector archives are not included.

```sh
unzip X40-R2416-v206-sanitized-analysis-kit.zip
cd x40-r2416-v206-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V206_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V206_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v206.py

python3 verify_x40_r2416_v206.py \
  --prior-zip "$X40_V206_PRIOR_ZIP" \
  --delta-zip "$X40_V206_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v206-new-SANITIZED.json"
# X40_R2416_V206_REUSETREE_AISTAIN_CHILD_STATIC_PASS
```

The report output must not already exist; overwrite is refused. This repeats all earlier original ELF whole-file SHA256 pins and **18+7 saved payload hashes**, and performs **45 new original AArch64 word checks, 11 branch/call checks, two decoded native parameter-table verifications, 158 separate generated `reuse/` subtree positions, and original `SubtreeConditionNode::onInit` vtable relocation lookup**. All **10** v206 focused tests passed, including changed original ELF, changed instruction, wrong branch target and create-only negative tests.

## Smaller checker retained on the research branch

The repository contains `docs/research/x40-r2416-v206-tools/x40_r2416_v206_repo_check.py`, a dependency-free, bounded checker reading only the initial owner-private collector ZIP:

```sh
python3 docs/research/x40-r2416-v206-tools/x40_r2416_v206_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V206_REPO_REUSETREE_STATIC_PASS 158 distinct reuse children
```

The independent checker SHA-pins the original host, tree, and BT core ELF files; checks selected instructions and factory calls; checks the precise AiStainMop and CleanSelectedAreas generated parameter vectors; and reconstructs the 158-child ReuseTree census. It is a **subset**, not a replacement for the full historical verifier chain.

**Interpretation boundary:** ReuseTree construction is compiled to precede RobotNode and receives the same route Blackboard holder. Child instantiation has a **conditional** pre-tick `onInit` path, not an observed live cache entry. Neither this evidence nor any previous static ELF finding demonstrates live effective cache contents, the AI-stain-to-new-task dispatch chain, or actual physical extra cleaning. Keep experimental CleanGenius writes off and all raw firmware and private robot information out of public GitHub.

See [sanitized findings](x40-r2416-v206-reusetree-aistain-2026-10-27.md) and [machine-readable result](x40-r2416-v206-reusetree-SANITIZED.json).
