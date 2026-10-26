# Dreame X40 R2416 v200 — native JSON array-order mapping

**27 October 2026 | offline static analysis only.** Preserves the v195 native-`RobotNode` correction and all v197–v199 evidence. Owner-private original R2416 binaries and two collector ZIPs were inspected locally; neither the robot nor the working Valetudo+ installation was contacted or modified. No raw firmware or unredacted configuration is committed.

## New verified native path

Original `node_lethe.so` SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0` contains `AvaNodeRoute::LoadTurbidityCheckConfig` at `0x62aa40`. It dispatches on literal names `table_a` (`0xa16360`), `table_b` (`0xa16368`) and `table_c` (`0xa16370`), using string-compare branches `0x62b13c→0x62b214`, `0x62b150→0x62b35c` and `0x62b164` for the three cases.

The A branch reads the `value` arrays at `0x62b214–0x62b244`, iterates successive 24-byte RapidJSON pair elements at `0x62b270–0x62b2a0`, builds native `int32,int32` pairs, and appends each completed inner vector to the outer A collection at `0x62b2a4–0x62b358` through native helper `0x62b4ac`. The enclosing source array iteration advances by 24 bytes at `0x62b0e4`. In the inspected A loop, no `id` value is used as an index or sorting key; array order is preserved by sequential appends.

The B branch at `0x62b35c–0x62b3f8` reads a signed int32 lookup key, converts its other JSON value through RapidJSON `GetDouble` at `0x62b3c8` and `fcvt s0,d0` at `0x62b3cc`, and appends native `int32,float32` pairs. The C path builds `int32,int32` pairs. The resulting `TurbidityCheckConfig` is published through the route's Blackboard at `0x62ae48–0x62ae54`.

## Resolution of v199 ordering question

The saved, redacted R2416 calibration JSON has ordered `table_a` records with `id` labels `[0,1,2,3]` and lengths `[63,35,60,60]`. **Given successful parsing and unchanged delivery, the nth JSON A-array element becomes the nth outer native A-vector element.** This correspondence arises from array traversal and append order, *not* sorting by the `id` label.

v199 independently verified that `SweepStationContorl::InitTable()` conditionally selects the nth outer A vector using an unsigned 16-bit `station_info_sub` plus a bounds check and 24-byte outer-vector stride (`0x251fa0–0x252004`). Therefore **if** that original JSON was loaded, reached the same effective Blackboard and controller, and `station_info_sub=3`, the fourth array position would be chosen. The fourth saved JSON series describes a 40-series calibration. **We have not measured the live subtype or verified successful runtime loading and Blackboard identity.** Do not convert this conditional result into a claim that the R2416 actively selected A[3].

## Reproduction and boundaries

Standalone local kit `X40-R2416-v200-sanitized-analysis-kit.zip`, SHA-256 `959d8d77932e9632a1dc7c9002b57ae7809ba9fab904efaa0be25a031aa55b37`. Complete Python 3 stdlib-only v197–v200 replay passed against original private archives: 18 + 7 saved-payload checksum verifications, five whole-file ELF SHA pins, all previous regressions, **143 v200 host AArch64 instruction anchors, 18 decoded branch or call targets, ten passing focused tests**, mutation rejection and create-only output enforcement. The ZIP's 12 included payload checksums and ZIP CRCs also passed.

Unproven: successful live config parsing, runtime A-vector contents or subtype, route-to-station controller Blackboard instance equality, threshold crossings, any AI-stain-to-new-task edge, the model-eligible `special_push_clean_dish` rewash prerequisite, or physical second cleaning or washing. No experimental writes or runtime probes were attempted. Continue static Blackboard forwarding and subtype-writer analysis next. Preserve `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` and working v74 safety gates; do not modify `master`.

A separate smaller repository-side checker and full offline kit reproducibility instructions accompany this report.
