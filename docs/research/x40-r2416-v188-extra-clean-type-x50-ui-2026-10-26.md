# X40 R2416 v188 — Extra-clean type callers and user-supplied X50 CleanGenius screen evidence

Date: 26 October 2026. Offline-only analysis. Based on original private `liblethe_route_nodes.so` and 12 user-provided screenshots taken from https://www.youtube.com/watch?v=cWB9SBORkQg. Neither original firmware nor screenshots are committed here.

## Native direct-call finding
The native R2416 function `switch_mode::CleanedAreaCheckTool::GetExtraCleanType(std::shared_ptr<BT::Blackboard> const&)` is implemented at `0xb75e00`; its relocatable PLT stub is `0x4510c0`. A scan of all executable sections of the pinned native ELF finds exactly **five direct AArch64 BL calls to this PLT stub**, from:
1. `BlockGridsAnalyzer::GetSegmentMap` — `0xb5caf8`, result saved in `w20` at `0xb5cb00`.
2. `CleanedAreaCheckTool::FloodFillGetCleanedEdge` — `0xb6720c`, `w26` at `0xb67210`.
3. `CleanedAreaCheckTool::GetSeed` — `0xb7776c`, `w23` at `0xb77774`.
4. `CleanedAreaCheckTool::CheckAreaUnreachable` — `0xb7fda8`, `w22` at `0xb7fdb0`.
5. `CleanedAreaCheckTool::GetUnreachableArea` — `0xb812f0`, `w19` at `0xb812f4`.

Original ELF SHA-256: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`.

All five direct callers process area-map geometry, edges, seeds or reachability. This supports extra-clean *type* being considered in area treatment, but identifies **no direct task-start command** in these five edges. This is a bounded direct-BL/PLT call census in one ELF, **not** a complete indirect/cross-module call graph and **not** proof no automated re-cleaning exists.

## User-supplied app screens: X50 Ultra (not user's X40 R2416)
The 12 screenshot frames explicitly show `X50 Ultra` in the mobile app title.

**Top-level selector:** CleanGenius | Custom.

**CleanGenius tab:** explanatory labels `Free your hands`, `Intelligently Recommend Cleaning Parameters` and `Re-clean Dirty Areas (Optional)`; cleaning mode choices `Vac & Mop` / `Mop after Vac` (Vac & Mop selected in shown screens); separate `Deep Cleaning` switch, shown off. **The phrase Re-clean Dirty Areas (Optional) is not itself a visible separate toggle in the supplied frames**. Daily and Ultimate switches are not visibly shown.

**Custom tab:** Vacuum, Mop, Vac & Mop, Mop after Vac and a further partially clipped choice; suction Quiet/Standard/Intense/Max; wetness 16 at Standard; mop washing frequency `By Area 15 m²`; route Quick, Standard, Intensive, Deep; per-room customization includes an Intelligent Recommendation label.

**Model and feature boundary:** the video screenshots are direct evidence for the X50 app UI, **not** proof of the exact X40 R2416 settings, MIOT property values, native implementation, or a separable automatic reclean switch. Keep CleanGenius Deep Cleaning, Custom Route Deep, dock mop-washing frequency and dirty-area reclean conceptually separate. The sample screenshot map has segmented rooms; the user's X40 floor map currently does not.

## Reproducibility and safe handling
Verified offline ZIP: `X40-R2416-v188-sanitized-extra-clean-type-x50-ui.zip`.
SHA-256 `39198cb2487bd5f0a01d9cf22eeee9c21dc302deee6513ffa499e01daad36e5c`.

The full ZIP includes Python 3 standard-library v184–v188 verifiers, tests, sanitized native results, screenshots-only metadata including all 12 SHA-256 image fingerprints, README and SHA256SUMS. Against the exact original route ELF **145 tests passed**; after clean ZIP extraction without firmware **73 passed and 30 skipped** (103 total). The v188 suite checks every callsite, post-call instruction, PLT gadget and independent mutated instructions with strict hash disabled only for adversarial checks.

No robot SSH, native writes, MIOT commands, changed configuration, firmware patches, proprietary module redistribution or screenshots redistribution occurred. Preserve working v74 `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. The missing proof remains an AI dirt-driven state-machine action that actually enqueues a new cleaning pass, not the existence of an extra-clean type or a UI description.
