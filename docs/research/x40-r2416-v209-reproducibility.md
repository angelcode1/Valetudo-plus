# X40 R2416 v209 — reproducibility and safe next evidence

**27 October 2026. Offline only.** This branch descends from v208, not `master`. No robot access, firmware writes or live Valetudo+ changes.

The complete source-only kit is `X40-R2416-v209-sanitized-analysis-kit.zip`. SHA-256: **`26d3d4734ce41038718d0c16645a82069e43157230fdadb6b117dcec220b862b`**. It contains v197–v209 standard-library Python 3 verifiers, tests, the v208 targeted collector, sanitized findings, and checksum manifest. A clean extraction passed **40 per-file SHA-256 checks**, ZIP CRC and **15 v209 focused tests**, including all earlier firmware regressions, original five ELF hash pins, native tamper rejection, and create-only output. Proprietary firmware and PRIVATE collector archives are *not* included.

## Full offline replay

```sh
unzip X40-R2416-v209-sanitized-analysis-kit.zip
cd x40-r2416-v209-sanitized
shasum -a 256 -c SHA256SUMS.txt
export X40_V209_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V209_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V209_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
python3 -m unittest -v test_verify_x40_r2416_v209.py
python3 verify_x40_r2416_v209.py \
 --prior-zip "$X40_V209_PRIOR_ZIP" \
 --delta-zip "$X40_V209_DELTA_ZIP" \
 --resolver-zip "$X40_V209_RESOLVER_ZIP" \
 --out "$HOME/Downloads/X40-R2416-v209-new-SANITIZED.json"
# X40_R2416_V209_RESOLVER_DISPOSITION_PATH_STATIC_PASS 11 5
```

Output must be a new file; overwriting is refused. The separate bounded repository checker is `docs/research/x40-r2416-v209-tools/x40_r2416_v209_repo_check.py`:

```sh
python3 docs/research/x40-r2416-v209-tools/x40_r2416_v209_repo_check.py \
 --prior-zip "$HOME/Downloads/X40-R2416-live-PRIVATE.zip" \
 --resolver-zip "$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
# X40_R2416_V209_REPO_EMPTY_RESOLVER_REALPATH_PASS 11 5 6
```

## Optional owner-initiated read-only live inventory

The uploaded Mac-side collection contained **zero new plugin files**, and **zero remote inventory candidates** because no robot SSH scan occurred. Repeating the same Mac archive inputs will not advance this issue. If the owner chooses a read-only live inventory, the bundled collector supports:

```sh
python3 collect_x40_r2416_v208.py \
 --prior-zip "$X40_V209_PRIOR_ZIP" \
 --ssh root@ROBOT_IP --ssh-interactive \
 --output "$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE"
```

The robot IP and explicit SSH authorization are the owner's responsibility. This collector uses whitelisted tree-library/resource directories and read-only `find`/`cat`; its SSH mode has **not** been tested on the actual robot. Never commit PRIVATE ZIPs, original ELFs or raw configuration to public GitHub.

**Inference boundary:** v209 proves original `getcwd`, `make_absolute` and `realpath` call sites, but not the final opened `AiStainMop` pathname, runtime registration, AI stain-to-new-task edge or physical second cleaning pass. Keep experimental CleanGenius writes disabled.

See [v209 research](x40-r2416-v209-empty-resolver-path-normalization-2026-10-27.md) and [sanitized JSON](x40-r2416-v209-resolver-empty-path-SANITIZED.json).
