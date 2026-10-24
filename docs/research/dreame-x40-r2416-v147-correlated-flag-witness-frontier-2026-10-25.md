# Dreame X40 R2416 — v147 correlated native flag-writer witness frontier

**25 October 2026. Offline, sanitized, non-device research.** The goal remains finding the uniquely **executed** source instruction writing the native model-group eligibility flag `SP+0xBC` inside `ProcessModelInfo()`. That instruction is **not identified** in this run.

## Conditional constraint already proved by v135

The earlier source-pinned v135 analyzer jointly tracks the last direct writer at `SP+0xBC` and two model-group condition variables, `SP+0x98` and `SP+0x100`. It reported 118,989 possible direct-CFG/product states and 35 terminal combinations for the owner-recorded model-class evidence (v128 source site `site_0x473540`). The v137 source-register corridor work confirms positive-value inputs to the ten remaining *possible* last-direct-writer sites. **Static candidates are not runtime executions.**

If the native `SP+0x98` branch input at `0x470b44` is proven to be **zero**, only these five direct-writer sites survive that category within the v135 bounded graph:

`0x474cd0`, `0x476798`, `0x4773dc`, `0x4775a4`, `0x4776b4`.

With a pointer-derived **unknown** low-32-bit `SP+0x98` source or a locally positive/unproven input, the original static set still permits all ten:

`0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`.

These are **prior source-verified conditional classes**, not a v147 re-scan or a claim that zero was measured on the robot. The previous `SP+0x100` zero-source pruning alone excludes no writer.

## New v147 reproducible witness extractor

The operator-downloadable, Python 3 standard-library-only `X40-R2416-v147-sanitized-correlated-flag-witnesses.zip` contains `x40_r2416_v147_flag_writer_witness_verify.py` and the complete sanitized v112–v146 verifier dependencies. The code requires **both** original ten-ELF owner-private v62 ZIP and the sanitized owner-collected v128 comparison-site ZIP. It refuses to invent either missing input.

When those inputs are available, it validates ten original SHA256 ELF pins; v135 native branch and stack-source evidence; v137 source-register corridors; the exact source-model/regex-pruned CFG; the original ten-writer bound; and v135's 118,989 / 35 state/terminal regressions. It then independently records a *representative feasible path* for each final writer and the branch decisions on that path, emitting only bounded code addresses and category labels, never original vendor bytes or the raw model literal. It compares witness branch alternatives only as **examples**; a branch taken by one example is not proved necessary for that writer.

**Actually tested in this run:** seven synthetic source-independent witness/state fixtures and prior five-of-ten category invariants; an explicit missing-source rejection; Python compilation; checksum verification; archive integrity; and successful clean-extraction replay. **The v147 owner-source witness extraction was NOT RUN:** original v62 and v128 bytes were not available together to this container. The private v62 attachment was visible as metadata and a file-service materialization returned a nominal path, but it was absent from the execution filesystem. Original source results are **not** inferred from synthetic tests.

## Replay

SHA256 of tested ZIP: `274dd4518f6b94195e384f904c1a2bb18b9b399f61318aa4dae63de18ac02269`.

```sh
cd ~/Downloads
unzip X40-R2416-v147-sanitized-correlated-flag-witnesses.zip
cd x40-v147-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v147_flag_writer_witness_verify.py --self-test
python3 x40_r2416_v147_flag_writer_witness_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test --out ~/Downloads/x40-v147-flag-writer-witnesses.json
```

Only the last command needs the private inputs; it was not run in the assistant's environment. Do not reconstruct missing v128 evidence from a guessed model string and report it as an authentic live capture. Upload **only** the generated sanitized JSON, not original ELF or raw robot config.

## Next proof gate

Inspect the source-verified witness divergence addresses and trace complete predicates/necessary outcomes rather than treating feasible example paths as observed. No actual last-writer instruction, native `enable_turbidity` value, shared live StationWash Blackboard or genuine extra physical mop wash has been proven.

**Safe baseline:** last operator-confirmed Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher/backups. No robot/cloud network I/O, MIOT writes, native tracing hooks, firmware patches, public proprietary binaries or `master` modification.
