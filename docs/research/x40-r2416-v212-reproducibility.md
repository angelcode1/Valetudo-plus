# X40 R2416 v212 — source-only replay and process evidence validation

**27 October 2026.** Branch descends from v211 research. No robot communication, firmware changes, running Valetudo+ updates, proprietary library upload or `master` mutation.

## Complete, clean-tested offline kit

Artifact: `X40-R2416-v212-sanitized-analysis-kit.zip`  
SHA-256: **`4801282109f0fda28b81e5ad09d96741cd6f874913a0b25a60458b8d0b9a12bc`**  
**55 ZIP entries**, including the manifest; **54/54 internal SHA-256 checks passed** on clean extraction. All **12 focused v212 tests passed**, including complete v197–v211 original-native/evidence regression replay. The ZIP includes all previous stdlib Python verifier and test scripts, the v212 exact native exception-path checks, sanitized report and JSON. No original ELFs or owner-private process JSON contents appear in this release.

```sh
unzip X40-R2416-v212-sanitized-analysis-kit.zip
cd x40-r2416-v212-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V212_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V212_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V212_OFFLINE_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V212_LIVE_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V212_SCOPE_SAN="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V212_SCOPE_PRI="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V212_PROCESS_SAN="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V212_PROCESS_PRI="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v212.py
python3 verify_x40_r2416_v212.py \
  --prior-zip "$X40_V212_PRIOR_ZIP" \
  --delta-zip "$X40_V212_DELTA_ZIP" \
  --offline-resolver-zip "$X40_V212_OFFLINE_ZIP" \
  --live-resolver-zip "$X40_V212_LIVE_ZIP" \
  --scope-sanitized "$X40_V212_SCOPE_SAN" \
  --scope-private "$X40_V212_SCOPE_PRI" \
  --process-sanitized "$X40_V212_PROCESS_SAN" \
  --process-private "$X40_V212_PROCESS_PRI" \
  --out "$HOME/Downloads/X40-R2416-v212-new-SANITIZED.json"
# X40_R2416_V212_CWD_AND_REALPATH_ERROR_STATIC_PASS 10 6 4
```

A fresh output path is mandatory. It does not SSH to the robot or print the private PID/current working directory. The ten new original AArch64 word anchors and six branch/call edges cover the `realpath()` null-result exception path: `__cxa_allocate_exception`, `__errno_location`, `strerror`, `std::runtime_error`, `__cxa_throw`, and the inherited conditional branch. The actual runtime error path execution remains unobserved.

## Smaller tested GitHub checker

`docs/research/x40-r2416-v212-tools/x40_r2416_v212_repo_check.py` independently validates the uploaded process-private/sanitized JSON pair and original file hashes, **not** the complete native ELF regression:

```sh
python3 docs/research/x40-r2416-v212-tools/x40_r2416_v212_repo_check.py \
 --sanitized "$X40_V212_PROCESS_SAN" \
 --private "$X40_V212_PROCESS_PRI"
# X40_R2416_V212_REPO_PROCESS_CWD_PASS 1 4 0
```

It was separately run successfully on the actual uploaded JSONs and does not echo private fields.

**Limits:** One reported matching process, one readable cwd, four missing *tested* relative filename candidates. Neither a successful nor failed `AiStainMop` runtime resolver invocation is established. No autonomous second cleaning task, physical extra floor clean or dock rewash has been observed. Continue inspecting runtime registration/aliases offline and keep experimental CleanGenius gates disabled. Private evidence is not for publication to GitHub.

See [v212 research](x40-r2416-v212-process-cwd-error-boundary-2026-10-27.md) and [sanitized machine result](x40-r2416-v212-process-error-SANITIZED.json).
