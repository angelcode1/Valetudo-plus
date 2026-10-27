# X40 R2416 v218 — complete source-only reproducibility and research boundary

**27 October 2026.** New research branch extends v217, not `master`. No robot contact, firmware write, running Valetudo+ change, experimental CleanGenius activation, or publication of PRIVATE firmware ELFs, owner configuration, maps, process identifiers or diagnostic archives.

## Clean-tested downloadable kit

**`X40-R2416-v218-sanitized-analysis-kit.zip`**  
SHA-256: **`2081da24c4ce84b9e05a7ee930b2721bdae3cd170d4d69d5ab98edad68b26f4c`**  
Size **180,375 bytes**, **79 ZIP entries including checksum manifest**, **78/78 internal file hashes verified** and ZIP CRC checked after fresh extraction. **All 12 v218 focused tests passed** (fresh extraction: 22.255 seconds) against the original owner-private inputs, with the complete **v197–v217 regression replay**. No original vendor binaries or raw PRIVATE input files are packaged; all Python scripts use the standard library only.

```sh
cd ~/Downloads
unzip X40-R2416-v218-sanitized-analysis-kit.zip
cd x40-r2416-v218-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V218_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V218_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V218_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V218_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V218_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V218_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V218_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V218_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v218.py

python3 verify_x40_r2416_v218.py \
 --prior-zip "$X40_V218_PRIOR_ZIP" \
 --delta-zip "$X40_V218_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V218_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V218_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V218_SCOPE_SANITIZED" \
 --scope-private "$X40_V218_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V218_PROCESS_SANITIZED" \
 --process-private "$X40_V218_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v218-new-SANITIZED.json"
# X40_R2416_V218_CLEANLIST_CONSUMER_CALL_BOUNDARY_PASS 57 21 4 4 1
```

The `--out` target must not already exist; overwriting the sanitized report is refused.

## Smaller, independent GitHub checkout audit

`docs/research/x40-r2416-v218-tools/x40_r2416_v218_repo_check.py` is a standalone Python 3 standard-library checker. It requires only the **original owner's private collector ZIP**; reads source evidence but publishes no private data. The corresponding kit-local checker ran successfully against original source and returned `21 4 4`. It validates **21 representative exact original AArch64 instructions**, the source ELF SHA-256, `Areas_Clean_List` literal and all four bounded direct-call BL target/site censuses in the original `.text`; the full kit is necessary for **all 57 words, 21 decoded edges, 12 mutation tests and v197–v217 replay**.

```sh
python3 docs/research/x40-r2416-v218-tools/x40_r2416_v218_repo_check.py \
 --prior-zip "$X40_V218_PRIOR_ZIP"
# X40_R2416_V218_REPO_DIRECT_CALL_CENSUS_PASS 21 4 4
```

## Verified native result and missing evidence

In the route-node module, `FollowWallModeDealFunc → Cleanbot::edge_cleaning → Cleanbot::preprocess` forms a bounded **direct-call** chain, and `GridmapInit::SetReuseTrans → SendCLeanListToCleanbot` is separate. The original `preprocess` reads `Areas_Clean_List` and, if the typed object survives its guards, copies `std::deque<std::vector<types::Area>>`. These statements are based on compiled code, not runtime observations.

There is **no proven same-Blackboard or runtime execution ordering** connecting `AiStainCheck`, `SetExtraCleanArea` and this consumer. No independent stain-triggered cleaning-task scheduler command, physical second pass or dock rewash has been observed. A direct-BL count does not exclude virtual/indirect/dynamic callbacks or code in other shared libraries.

**Next offline priority:** search the *actual native task-manager/scheduler handoff* and generated tree owners; do not infer a dispatch from a function name, CleanList, follow-wall preprocessing, `need_extra_clean` or a `reuse/` placeholder.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0` and `writeGateOpen=false`; `master` remains unchanged.

See [v218 technical findings](x40-r2416-v218-cleanlist-consumer-dispatch-boundary-2026-10-27.md) and [machine-readable sanitized evidence](x40-r2416-v218-cleanlist-consumers-SANITIZED.json).
