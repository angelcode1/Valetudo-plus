# X40 R2416 v198 — A-table fallback branches and live-file provenance

**26 October 2026. Offline-only analysis of owner-provided, SHA-pinned native R2416 ELF files and two owner-private collector ZIPs.** This extends the v195 native-`RobotNode` correction and the v197 compiled turbidity config → Blackboard bridge. No robot commands were sent, no firmware was executed or modified, and `master` remains untouched.

## New native finding — 0–3 are fallback cases, not proven JSON A-table IDs

In the exact original `liblethe_tactics_tree.so`, `SweepStationContorl::TurbidityMonitorGetAByTable(int,bool)` at `0x252a10` calls `InitTable()` at `0x252a40`, then its **false** branch at `0x252a44` reads Blackboard key `station_info_sub`. The 16-bit member read at `0x252bd0` feeds explicit cases 0 (`0x252be8`), 1 (`0x252bf0`), 2 (`0x252bf8`) and 3 (`0x252c00`), each of which computes a possible native fallback value before converging on the A-vector check.

- **Nonempty A vector:** the code loads vector start/end from `this+0x5f8/+0x600`, compares them at `0x252c10` and, if nonempty, overwrites x0 with the instance address at `0x252c38`, forwards the original lookup input in w1 and tail-calls `FindA` at `0x252c5c`. The provisional case-dependent w0 is **not an explicit JSON A-series index** forwarded into that call.
- **Empty A vector:** `0x252c14` branches to `0x252c98` then directly to the shared return path `0x252a60`. This returns the case-dependent compiled fallback, without calling `FindA`.

Independently, `InitTable()` checks `turbidity_check_tables` on its Blackboard. If missing, `0x2508e0` branches to compiled fallback-table construction at `0x250d90`, with another `station_info_sub` case check at `0x250df0`. The successful copied-table path has a distinct return at `0x250d8c`. These distinct branches explain why a case label 3 must **not** be conflated with the recovered JSON's `table_a[3]` 40-series label. The selector used to populate the actual live vectors remains unverified; other code may still use `station_info_sub` differently.

## Collection provenance — matching deployed files, not proven runtime use

The first private collector's redacted `r2416.conf` names `/ava/conf/turbidity_check_config.json`, and its manifest records matching original SHA-256 from the archived `r2416.conf` and a read-only SSH duplicate. An unredacted `setting.yaml` was collected over SSH and SHA-verified; it selects the native `RobotNode` factory.

The second private collector manifest records the archived original turbidity JSON and a read-only **SSH duplicate with the same original pre-redaction SHA-256**. The saved JSON is privacy-filtered, so its original SHA cannot be reconstructed from the saved redacted bytes. This independent analysis verifies the collector manifests and saved-byte digests but cannot independently authenticate the historical SSH session. Presence of a matching file at collection time does not demonstrate that the native loader ran or that the station node used it.

## Verification

Standalone **Python 3 standard-library-only** `X40-R2416-v198-sanitized-analysis-kit.zip`; SHA-256 **`b4d688bef97e5c817fb366854bf4e98f7a58c7120d3d82ae30111ebdca622042`**. It includes complete v197 verifier source plus v198 verifier/tests, sanitized JSON/report, and internal SHA-256 manifest. Replay of the two private ZIPs passed: **18 + 7** stored payload checksums, **five** original ELF SHA pins, **54 v197 + 32 new = 86** exact native AArch64 instruction-word anchors, **13** decoded AArch64 branch edges, six focused tests including an altered-instruction rejection, and package integrity. The repository contains this sanitized research and a standalone bounded v198 branch checker; full v197+v198 replay source is included in the kit.

**Not verified:** successful live `LoadTurbidityCheckConfig` execution, producer/consumer Blackboard instance identity, chosen live A-series index, stain-to-task dispatch, `special_push_clean_dish` eligibility, physical additional floor cleaning or dock rewash. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and existing Valetudo+ gates unchanged.

**Next:** characterize `InitTable()`'s populated-table copying, native `FindA` data shape and the generated `RobotNode`/station subtree Blackboard forwarding before proposing any active robot observations.
