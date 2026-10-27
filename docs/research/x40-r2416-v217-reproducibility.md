# X40 R2416 v217 — reproducible offline source-only handoff

**27 October 2026.** Research branch extends v216. The robot, firmware, Valetudo+ runtime, experimental feature gates and GitHub `master` remain unchanged. PRIVATE owner firmware, path lists, process metadata and diagnostic ZIPs remain external.

## Complete clean-tested v197–v217 kit

File: `X40-R2416-v217-sanitized-analysis-kit.zip`  
**SHA-256: `6ed558fc279fa41b148f6c52b2ec8197685fb39f619543dc43524a0fef399704`**.  
**73 ZIP entries including `SHA256SUMS.txt`; 72/72 payload SHA-256 hashes verified** after fresh extraction; ZIP CRC clean. **All 13 v217 focused tests passed**, including full v197–v216 inherited private-original native replay, original five whole-ELF SHA pins and all prior collected evidence checks. No original ELF or private configuration is inside the kit.

v217's new verifier pins **53 exact AArch64 instructions and 21 direct call/branch targets**, 1 generated `AiStainCheck` and 2 generated `SetExtraCleanArea` placements in distinct builders, and the expressly **restricted immediately adjacent same-register ADRP/ADD reference form**: 11 `stain_area_for_logic` and 62 `Areas_Clean_List` sites. Mutation tests reject changed ELF bytes, node-creation opcodes, source key writes, list append, guarded branch, generic consumer key lookup, and even an unanchored direct-key reference in the limited census. The full tester rejects report overwrites and redacts all original user-private fields.

```sh
cd ~/Downloads
unzip X40-R2416-v217-sanitized-analysis-kit.zip
cd x40-r2416-v217-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V217_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V217_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V217_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V217_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V217_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V217_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V217_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V217_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v217.py
python3 verify_x40_r2416_v217.py \
 --prior-zip "$X40_V217_PRIOR_ZIP" \
 --delta-zip "$X40_V217_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V217_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V217_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V217_SCOPE_SANITIZED" \
 --scope-private "$X40_V217_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V217_PROCESS_SANITIZED" \
 --process-private "$X40_V217_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v217-new-SANITIZED.json"
# X40_R2416_V217_GENERATED_STAIN_CLEANLIST_STATIC_PASS 53 21 1 2 11 62
```

The `--out` destination must be a **new** sanitized filename. Use `sha256sum -c` on Linux.

## Smaller bounded checker in GitHub

`docs/research/x40-r2416-v217-tools/x40_r2416_v217_repo_check.py` reads only the original owner PRIVATE collector ZIP. It SHA-pins the exact tree and route-node ELFs and checks **22 representative original AArch64 words, six direct call targets and the complete bounded one-plus-two generated-node name census**. It is **not** the 53-word/21-edge full verifier and does not replay all historical tests. The matching bounded check shipped inside the v217 ZIP was independently executed on the original archive and passed.

```sh
python3 docs/research/x40-r2416-v217-tools/x40_r2416_v217_repo_check.py \
  --prior-zip "$X40_V217_PRIOR_ZIP"
# X40_R2416_V217_REPO_STAIN_NODE_OWNERS_PASS 22 6 1 2
```

## Evidence limits and follow-up

Generated `AiStainCheck` and `SetExtraCleanArea` node placements are in **different native builder functions**. The route module has compatible guarded `stain_area_for_logic` and `Areas_Clean_List` getter/setter/append/consumer operations, but no proven live same-Blackboard identity, execution order or actual dirt-caused cleaning-task start. Neither `SendCLeanListToCleanbot`'s name nor `need_extra_clean` alone establishes a second pass. No physical floor reclean or dock rewash was observed. The v217 restricted reference count of 62 must not be equated to v186's differently derived 77-site bound.

The next offline target is **actual task dispatch after Cleanbot/area selection** and generated caller topology. No new robot collection is needed; keep original binaries, raw settings, maps and PRIVATE ZIPs off GitHub. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [v217 report](x40-r2416-v217-generated-stain-cleanlist-2026-10-27.md) and [sanitized machine evidence](x40-r2416-v217-stain-cleanlist-SANITIZED.json).
