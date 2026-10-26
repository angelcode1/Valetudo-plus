# Dreame X40 R2416 v187 — follow-wall entry into generic Cleanbot and CleanGenius app evidence limits

Date: 26 October 2026. Private original route ELF SHA-256: fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e.

## Verified compiled route
1. FollowWallModeDeal::FollowWallModeDealFunc at 0xcd0cd8 directly calls Cleanbot::edge_cleaning PLT 0x4416a0 (implementation 0xdf4e50).
2. Cleanbot::edge_cleaning at 0xdf4eac directly calls Cleanbot::preprocess PLT 0x449140 (implementation 0xdf22b0).
3. After that call edge_cleaning invokes VelocityProcess::SetActiveSmoothFlag at 0xdf4ec8 and edge_cleaning_type_switch at 0xdf4ed0.

The verifier audited ALL executable-section direct AArch64 BL calls to these two exact PLT destinations. Each has one direct caller in this ELF. This is NOT a census of virtual, indirect, cross-module, or inlined entry paths.

The v186 Cleanbot::preprocess code accesses the shared Areas_Clean_List Blackboard key at 0xdf2f50. Its use by a follow-wall/edge-cleaning path demonstrates that its mere presence does not imply a CleanGenius automatic reclean task. Previously v185 showed a conditional stain-area extra-clean list producer; the actual condition causing a NEW scheduling event remains unproven.

## Video and app documentation
User-supplied link: https://www.youtube.com/watch?v=cWB9SBORkQg

The specific linked YouTube video frames, captions and transcript could not be accessed. No specific screenshots, UI labels, tap sequences or video timestamps have been claimed from it.

INDEPENDENT Dreame references (context, not a substitute transcript):
- https://support.dreametech.com/hc/en-us/articles/11495198440847-What-is-the-difference-between-daily-mode-and-ultimate-mode-in-CleanGenius — Daily can include secondary cleaning after global cleaning; Ultimate can include denser/slower coverage and mop washing.
- https://dreameservice.zendesk.com/hc/en-us/articles/11640725021199-Setting-Up-a-Scheduled-Cleanup-A-Simple-Guide-with-X40-Ultra-as-example — CleanGenius All and Room ordering differ.
- https://dreametech.zendesk.com/hc/en-us/articles/55534904939673-Robot-Vacuum-and-Mop-Poor-Cleaning-Performance — Deep Cleaning intensity distinguished from custom mode and mop washing frequency.
- https://forum.dreametech.com/forum.php?mod=viewthread&tid=1882 — Dreame support discusses an Auto-recleaning toggle on Matrix10, which does not prove identical controls on R2416.

Crucial feature boundaries: CleanGenius mode selection, deep-clean route density, mop rewash at dock, user-selected cleaning, and genuinely automatic dirty-area floor reclean are NOT interchangeable. No native MIOT or Blackboard mapping to particular video/app switches was identified.

## Verification and release boundary
Full self-contained offline package: X40-R2416-v187-sanitized-cleanbot-entry-app-control-evidence.zip
SHA-256: 129411855989633a255ec972849d98b84192318193d2e31cd4b53ba7f66c567d

The ZIP contains executable v184-v187 Python stdlib verifiers and tests, this research report, sanitized evidence and SHA256SUMS.txt. Against the original ELF 127 tests passed; clean ZIP replay without ELF gave 60 pass, 25 skip. Native instruction mutation checks reject changed compiled callsites. No private ELF binaries included. The full executable verifier/test files are in this ZIP, not individually in this GitHub commit.

Safety: preserve the working v74 baseline, SmartHost=0, SmartAutoMop=-1, SmartAutoWash=0, writeGateOpen=false. No robot access, feature activation, cleaning commands or runtime patches.

Next: identify a genuine task-planner state transition that requests another area pass following a native dirt decision. Do not mistake generic Cleanbot preprocessing or Deep Cleaning app controls for that event.
