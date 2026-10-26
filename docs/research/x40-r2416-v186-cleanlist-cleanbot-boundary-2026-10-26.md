# Dreame X40 R2416 — v186 CleanList fan-out and generic Cleanbot preprocessing

Date: 2026-10-26. Original R2416 `liblethe_route_nodes.so` SHA-256: `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. Offline native-only research using the user's private source ELF; no robot, firmware or Valetudo+ runtime changes.

## Verified compiled interface

Following v185's shared `stain_area_for_logic` key and conditional extra-clean branch, v186 establishes that `Areas_Clean_List` is not merely an internal `SetExtraCleanArea` output but is **also referenced and read by the generic Cleanbot preprocessing code**.

- `subregion::SetExtraCleanArea::tick()`: presence-dependent branch at `0xad9474–0xad947c`; `types::CleanList::append` at `0xad94bc`; literal construction `0xad94cc–0xad94d0`; typed `Blackboard::set<types::CleanList&>` at `0xad94ec`.
- `system_motion::Cleanbot::preprocess(BT::TreeNode&)`: `BT::TreeNode::blackboard` at `0xdf2f48`; literal `0xdf2f50–0xdf2f54`; internal key-handling branch/call `0xdf2f60`; guarded virtual lookup and value handling `0xdf2f64–0xdf2f80`. This **is not itself proof of dispatching a new cleaning task**.
- `types::SendCLeanListToCleanbot(...)` (ABI string return): constructs key at `0x5d05d8–0x5d05dc`, calls **typed `Blackboard::get<types::CleanList>`** at `0x5d05fc`, checks failed/empty states at `0x5d0624/0x5d0634`, and assembles a textual list. **Despite its name, this function alone is not a verified transport-send or cleaning command**.
- `types::ResetPlanningCleanTaskBB(...)` touches the same key at `0x5d2788`; `segmentation::MakeSmartCleanList::ModifyCleanList` at `0xa66308`; `switch_mode::RemovableMopCleaningPreprocess::UpdateCleanList` at `0xb1e2bc`.

## Complete bounded key reference census

The exact `Areas_Clean_List\0` literal is at `0xfce5e0` in the supplied ELF. A strict scan of **adjacent executable AArch64 ADRP+ADD** resolved 77 direct sites. Mapping them to original ELF `FUNC` symbol ranges gave **63 named functions plus one unmapped reference in 64 distinct regions**. See companion sanitized JSON for all 77 exact sites. Representative other uses include carpet processing, zone/segment search, mop preprocessing, route planning, multi-layer area expansion, and map/segment updates.

The key is **not exclusive to extra-clean, CleanGenius or a re-clean task**. Nearby named functions and their occurrence counts are a symbol inventory, *not* a dynamic call graph, read/write direction census, runtime observation, or proof that a sensor event updates a task.

The compiled program now shows a named-key boundary from stain-area-conditioned extra-clean `CleanList` construction into **generic cleaning preprocessing**. The exact Blackboard instance and timing, AI dirt classification payload, activation branch, new scheduler command, and physical second floor pass remain unverified. The v165 coarse-area revisit candidates are not attributable to CleanGenius.

## Reproduction / provenance

Self-contained offline release: `X40-R2416-v186-sanitized-cleanlist-cleanbot-boundary.zip` SHA-256 `89550ed8e990e76157a5979cb9d0be544a4fb9f2254574678efc054eb2f1f9d1`. Distributed privately in the user's research conversation; this GitHub commit contains sanitized research and the ZIP checksum, not native proprietary ELF bytes.

The ZIP contains original-bin-aware Python 3 stdlib-only v184, v185 and v186 verification scripts, all three test suites, detailed report, exhaustive per-function xref JSON, README, and checked `SHA256SUMS.txt`. The original ELF ran **107 passing offline unit tests**, including full 77-site reference validation and isolated opcode mutation tests. Clean ZIP extraction, checksum verification and tests ran **50 pass, 15 native tests skipped** without the original private ELF. Tests verify compiled static semantics only.

```sh
cd ~/Downloads
unzip X40-R2416-v186-sanitized-cleanlist-cleanbot-boundary.zip
cd x40-v186-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py
export X40_R2416_V184_ROUTE_ELF="/private/path/liblethe_route_nodes.so"
export X40_R2416_V185_ROUTE_ELF="$X40_R2416_V184_ROUTE_ELF"
export X40_R2416_V186_ROUTE_ELF="$X40_R2416_V184_ROUTE_ELF"
python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py
python3 x40_r2416_v186_cleanlist_fanout_verify.py --route-elf "$X40_R2416_V186_ROUTE_ELF" --out "$HOME/Downloads/X40-R2416-v186-cleanlist-SANITIZED.json"
```

Safety: maintain last working v74 (`SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`). This is research-only; no deployment, feature activation, robot writes, or changes to `master`. Future work must identify **an actual task scheduler entry and command** correlated with a native dirt event, not infer autonomous reclean from key sharing.
