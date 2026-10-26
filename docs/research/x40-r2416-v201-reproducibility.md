# X40 R2416 v201 — offline reproducibility and evidence limits

Research branch based on v200. No robot commands, runtime changes, `master` modifications, unredacted configs or raw proprietary binaries.

## Small standalone repository-side checker

The repo includes `x40-r2416-v201-tools/x40_r2416_v201_repo_check.py`. The checker consumes the owner-private initial collector ZIP held **outside GitHub**, reads the two original native libraries in memory, verifies their SHA-256 pins, 24 selected exact AArch64 instructions, and four decoded branches/calls.

```sh
python3 docs/research/x40-r2416-v201-tools/x40_r2416_v201_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V201_REPO_NATIVE_STATION_INFO_PASS
```

This is only a bounded subset; the complete verifier and its tests are in the ZIP below.

## Full offline v197–v201 verifier chain

Local offline ZIP: `X40-R2416-v201-sanitized-analysis-kit.zip`
SHA-256: `f1cc6de32fef95587af0ce1110759b9d6e3dc9ab695d2f70a723a90d9e5eae74`.

16 files, including one checksum manifest; 15 SHA-256 file checks passed and ZIP CRC integrity passed. Includes complete v197, v198, v199, v200 and v201 source-only verifiers; test suites for v198–v201; 71 fixed original instruction anchors and v201 sanitized findings. Raw collector ZIPs and ELF payloads are not distributed.

```sh
unzip X40-R2416-v201-sanitized-analysis-kit.zip
cd x40-r2416-v201-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V201_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V201_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v201.py

python3 verify_x40_r2416_v201.py \
  --prior-zip "$X40_V201_PRIOR_ZIP" \
  --delta-zip "$X40_V201_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v201-new-SANITIZED.json"
# X40_R2416_V201_STATION_SUBTYPE_PRODUCER_STATIC_PASS
```

Use a fresh report filename: overwrite is intentionally refused. On the owner-provided ZIPs, 10 focused tests passed; whole-file original SHA pins, earlier regression chain, 71 new word anchors, 11 decoded edges, altered binary/opcode/key construction rejection, wrong branch polarity refusal and create-only report checks passed.

**Interpretation boundary:** We have a compiled producer for `station_info_sub` under the route's Blackboard and a compatible station-control consumer, but have **not** proven equality of live Blackboard instances, measured subtype, loaded A series, stain-triggered new floor task, or physical rewash. Additional **static** analysis can use the same original collected firmware. Experimental CleanGenius write gates remain off.

See [sanitized finding](x40-r2416-v201-station-subtype-blackboard-2026-10-27.md) and [machine-readable result](x40-r2416-v201-station-subtype-SANITIZED.json).
