# X40 R2416 v208 — complete offline replay and focused private collector

**27 October 2026.** Research branch extends v207 and preserves v195's native-`RobotNode` correction. All native verification is offline and read-only; the working Valetudo+ and GitHub `master` remain unchanged.

## Self-contained source-only ZIP

Artifact: `X40-R2416-v208-sanitized-analysis-kit.zip`  
SHA-256: **`e2835c8ef397c835808b0e8c66a8011d8eac001616f3f76daf9f78f80bdc2bf4`**

The archive has **37 entries including `SHA256SUMS.txt`**, and a clean extraction passed all **36 file SHA-256 checks**, ZIP integrity and **13 focused v208 tests**. The full Python 3 standard-library v197–v208 verifier chain and inherited unit tests are inside the ZIP, together with `collect_x40_r2416_v208.py`, v208 sanitized findings and usage instructions. There are no original proprietary ELF files, unredacted robot settings, maps, recordings, device credentials or user-private collector ZIPs.

```sh
unzip X40-R2416-v208-sanitized-analysis-kit.zip
cd x40-r2416-v208-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V208_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V208_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
python3 -m unittest -v test_verify_x40_r2416_v208.py
python3 verify_x40_r2416_v208.py \
  --prior-zip "$X40_V208_PRIOR_ZIP" \
  --delta-zip "$X40_V208_DELTA_ZIP" \
  --out "$HOME/Downloads/X40-R2416-v208-replay-SANITIZED.json"
# X40_R2416_V208_FILE_FALLBACK_BOUNDARY_STATIC_PASS
```

The output file must not already exist; the verifier intentionally refuses to overwrite it.

## Targeted private collector supplied inside ZIP

First inspect existing firmware archives on the Mac:

```sh
python3 collect_x40_r2416_v208.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip" \
  --offline "$HOME/Documents/X40-Firmware-Reference" \
  --archive "$HOME/Downloads/X40-Firmware-Reference.zip" \
  --output "$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE"
```

Omit nonexistent archives and repeat `--offline` or `--archive` as needed. Result: `X40-R2416-v208-resolver-PRIVATE.zip`. It checks the prior collection, looks specifically for installed tree-library ELF candidates and named `AiStainMop` resources (including extensionless `reuse/AiStainMop`), limits data volume and excludes private maps, logs, camera files and AI model weights. It saves original proprietary data **only into a clearly marked PRIVATE output** and reports sanitized counts separately.

If the Mac archive search does not resolve the resource, the owner can **optionally and explicitly** run a read-only SSH inventory:

```sh
python3 collect_x40_r2416_v208.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip" \
  --ssh root@ROBOT_IP --ssh-interactive \
  --output "$HOME/Downloads/X40-R2416-v208-live-PRIVATE"
```

This reads only whitelisted plugin/config directories using `find` and `cat`; no root filesystem modifications, firmware patching, commands to clean, AVA/MIOT publish or experimental Valetudo+ writes. **SSH mode has not been tested on the actual robot**, and the bounded directory search is not an exhaustive installed-resource proof.

## Smaller executable in this GitHub branch

`docs/research/x40-r2416-v208-tools/x40_r2416_v208_repo_check.py` extends the previously checked v206 and v207 repository-side tools. It verifies the exact original six-ELF SHA pins, **19 native instructions, six call targets**, and the exported factory-name census. The bounded checker was independently tested against the owner-private original ZIP.

```sh
python3 docs/research/x40-r2416-v208-tools/x40_r2416_v208_repo_check.py \
  --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
# X40_R2416_V208_REPO_ORIGINAL_FILE_FALLBACK_PASS 6 19 6
```

**Privacy and inference boundary:** Do **not** upload private collector ZIPs or original ELF binaries to public GitHub. `AiStainMop` may still be resolved by another loaded plugin, hidden/aliased factory, or external file. The file-loader interface passes the original string, but downstream path transformations are unverified. No successful live subtree resolution, new physical cleaning task, or actual second floor pass has been observed. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and working `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [sanitized report](x40-r2416-v208-aistain-file-fallback-2026-10-27.md) and [structured findings](x40-r2416-v208-aistain-file-fallback-SANITIZED.json).
