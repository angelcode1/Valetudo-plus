# Dreame X40 R2416 — v149 single-query recovery of missing v127 and v128 evidence

**25 October 2026. Offline owner-held source authentication and synthetic read-only SSH replay only.** No robot command was issued in this session.

## Problem and solution

The operator reported that neither of the two prerequisite ZIP files referenced in the v148 instructions existed in their macOS Downloads directory:

1. Original ten-ELF owner-private `X40-R2416-v62-readonly-20261023T051829Z.zip`.
2. Sanitized device-compiled-model site evidence `X40-R2416-v128-model-compare-site-<timestamp>.zip`.

**v62 recovered:** the original owner upload was recoverable directly from the prior conversation and its complete ZIP bytes were accessible in this execution. Original whole-archive SHA-256: `f996955745d07786d6290fd7afad4970f4d2cd182a493d61d329230c8038e6f6`. The v128 source verifier independently validated all **ten original firmware ELF pins**, **294** compiled native exact-name comparison call sites and **235** distinct compiled model identifiers. The private archive has been made available for the operator to download from the conversation; it is **not** in this public repository or the sanitized v149 utility kit.

**v128 regeneration simplified:** no prior v127 or v128 ZIP is required. The owner-side `x40_v149_one_pass_model_recovery.py` provided in the separately delivered v149 ZIP uses the verified v62 ELF model table, performs **one** operator-authorized read-only SSH query of **only** `/var/run/runava.conf`, and receives fixed two-key model categories and a compiled source-code site identifier, not raw MODEL/DEV_MODEL. From this *single actual observation*, it generates both correctly structured, independently validated sanitized v127 and v128 ZIPs.

The script refuses to proceed if the actual model categories differ from the earlier JSON-aware v127 observation (`MODEL=other_vendor_model`, `DEV_MODEL=absent`). It never infers a historical model site or reconstructs a missing live observation from a filename. It neither downloads raw remote configuration nor changes robot settings, the firmware, Blackboard, station state, MIOT, network service or Valetudo.

## Verification performed

- Original owner-held v62 ZIP SHA-256 and **10/10** original ELF source pins: PASS.
- **294** compiled model comparison calls and **235** compiled model names, using original `node_lethe.so`: PASS.
- v127 JSON-aware parser self-test: **13** synthetic configurations plus refusal tests: PASS.
- v128 native-site probe: **6** synthetic configurations, protocol mutation refusals and simulated SSH success/denial: PASS.
- v148 source-independent edge necessity: **11** fixtures; **192** independent correlated-state comparisons across **64** synthetic CFGs: PASS.
- v149 combined, single-SSH-response **synthetic** end-to-end test: generated both v127 and v128 expected ZIP members; v128 validator accepted the fresh source-derived site; no raw config or model was placed in ZIP: PASS.
- Clean extraction, all sanitized SHA256SUMS, ZIP integrity, and wrapper script end-to-end synthetic SSH run: PASS.

**Important timeout:** the optional four-edge v148 original-source analysis applied to a *synthetic model observation* exceeded the offline test execution limit. It is therefore **off by default** in the recovery helper. The initial task is just to recover the two missing evidence artifacts safely; users can upload the fresh sanitized v128 ZIP for independent subsequent analysis.

**No real device connection has occurred in v149.** The synthetic source-table-derived fixture is solely a code test; its model site cannot be reported as a newly observed runtime condition. Prior **ten** possible R2416 direct `SP+0xBC` flag writers remain possible. No executed instruction, live `enable_turbidity` Boolean, shared effective StationWash Blackboard object, or second physical mop wash is established.

## User instructions

Download original private v62 ZIP separately from the conversation, then download `X40-R2416-v149-one-pass-model-evidence-recovery.zip` (SHA-256 `6fbed310690fbcc81a6aee91275a7e84b493bf0c73af1648eb142a7a121851e7`). Save them both in `~/Downloads`. Run:

```sh
cd ~/Downloads
unzip X40-R2416-v149-one-pass-model-evidence-recovery.zip
cd x40-v149-sanitized
shasum -a 256 -c SHA256SUMS.txt
sh run-v149.sh root@YOUR_ROBOT_IP
```

The two sanitized ZIPs appear in `~/Downloads`. Share **only the new v128 ZIP**, not the original private v62 archive, raw robot configuration, device IDs, raw MODEL/DEV_MODEL strings, maps, logs or credentials.

**Safe baseline preserved:** last operator-confirmed Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher/rollbacks. GitHub `master` untouched; this commit contains sanitized documentation and aggregate verification records only.
