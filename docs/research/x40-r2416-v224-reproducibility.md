# X40 R2416 v224 — full offline replay and next causal boundary

**27 October 2026.** Research branch extends v223; robot, firmware, running Valetudo+ and GitHub `master` unchanged. No proprietary vendor ELF, PRIVATE device archives, raw configuration, process identifiers, IP addresses or user maps in this commit or ZIP.

## Complete self-contained source-only verification ZIP

**`X40-R2416-v224-sanitized-analysis-kit.zip`**

- SHA-256 **`ec8bad8c1875a6ef21681b445dc0343cdfc0bc81968c7acdfca59901d54b2fa3`**
- Size **247,502 bytes**; **115 ZIP entries** including `SHA256SUMS.txt`
- ZIP CRC, **114/114 payload SHA-256 checks** and **11/11 tests passed** from **fresh extraction** (clean suite 57.413 seconds)
- Earlier source-directory run also passed **11/11 tests** (69.447 seconds), including complete historical **v197–v223** owner-private native/evidence replay
- Python 3 standard-library scripts, native instruction anchors, sanitized research reports, independent checker and mutation tests. **Original owner PRIVATE inputs are not bundled.**

```sh
cd ~/Downloads
unzip X40-R2416-v224-sanitized-analysis-kit.zip
cd x40-r2416-v224-sanitized
shasum -a 256 -c SHA256SUMS.txt

export X40_V224_PRIOR_ZIP="$HOME/Downloads/X40-R2416-live-PRIVATE.zip"
export X40_V224_DELTA_ZIP="$HOME/Downloads/X40-R2416-delta-PRIVATE(1).zip"
export X40_V224_OFFLINE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v208-resolver-PRIVATE.zip"
export X40_V224_LIVE_RESOLVER_ZIP="$HOME/Downloads/X40-R2416-v209-live-resolver-PRIVATE.zip"
export X40_V224_SCOPE_SANITIZED="$HOME/Downloads/X40-R2416-v210-scope-SANITIZED.json"
export X40_V224_SCOPE_PRIVATE="$HOME/Downloads/X40-R2416-v210-scope-PRIVATE.json"
export X40_V224_PROCESS_SANITIZED="$HOME/Downloads/X40-R2416-v211-process-SANITIZED.json"
export X40_V224_PROCESS_PRIVATE="$HOME/Downloads/X40-R2416-v211-process-PRIVATE.json"

python3 -m unittest -v test_verify_x40_r2416_v224.py
python3 verify_x40_r2416_v224.py \
 --prior-zip "$X40_V224_PRIOR_ZIP" \
 --delta-zip "$X40_V224_DELTA_ZIP" \
 --offline-resolver-zip "$X40_V224_OFFLINE_RESOLVER_ZIP" \
 --live-resolver-zip "$X40_V224_LIVE_RESOLVER_ZIP" \
 --scope-sanitized "$X40_V224_SCOPE_SANITIZED" \
 --scope-private "$X40_V224_SCOPE_PRIVATE" \
 --process-sanitized "$X40_V224_PROCESS_SANITIZED" \
 --process-private "$X40_V224_PROCESS_PRIVATE" \
 --out "$HOME/Downloads/X40-R2416-v224-new-SANITIZED.json"
# X40_R2416_V224_DIRTY_MOP_MCU_BOUNDARY_STATIC_PASS 37 11 3 1 2
```

The output path must be **new**; overwriting is refused. Generated output contains only sanitized evidence summary, not private data. The full verifier checks **37 original AArch64 instruction words, 11 decoded direct/conditional branches, three exact dirty-mop key references, exact host `UpdateOutput` direct-caller census and two guarded MCU publication calls**, with mutation tests for extra/unanchored callers and altered guards. Complete v223 inbound AI subscriber and both GOT callback relocations are replayed.

## Independent fast GitHub checker

The smaller standalone `docs/research/x40-r2416-v224-tools/x40_r2416_v224_repo_check.py` checks **15 pinned original native words, the exact dirty-mop literal, three selected host caller PLTs and two MCU-publication call sites inside the known consumer body**; source-equivalent script in the ZIP passed against the original owner firmware:

```sh
python3 docs/research/x40-r2416-v224-tools/x40_r2416_v224_repo_check.py \
 --prior-zip "$X40_V224_PRIOR_ZIP"
# X40_R2416_V224_REPO_DIRTY_MOP_MCU_PASS 15 3 2
```

This is bounded static proof, not a live event trace. `AiDetectResultSUB` conditionally sets `ai_set_mop_is_dirty_data`; `SendMopStainCheckCmd` references that exact key and may attempt one of two guarded `_CtrlMcuCMD` publications; `UpdateOutput` calls the consumer and separately calls turbidity/new-command functions. **Neither code-15→MCU publication causality nor an actual station rewash or second floor pass has been established.**

**Next:** reverse-engineer the two conditional `_CtrlMcuCMD` payload constructions and subscriber/MCU interpretation; separately trace `stain_area_for_logic`/extra-area changes to an actual production cleaning-task launch. Do not enable CleanGenius experimentally to substitute for missing proof.

Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`.

See [v224 technical report](x40-r2416-v224-mop-dirty-consumer-mcu-2026-10-27.md) and [sanitized result JSON](x40-r2416-v224-mop-dirty-consumer-SANITIZED.json).
