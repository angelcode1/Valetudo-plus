# X40 R2416 v183 — Compiled stain-perception object and processing chain
Date: 2026-10-26. Offline-only analysis on the two original user-provided AArch64 native ELFs.

## New proof beyond v182
1. `MapAccumulatorNode::InitNode` allocates `MapAccumulator` (allocation 0x1306c8, constructor call 0x1306dc), then assigns its pointer to `node+0x1380` at 0x1306e4.
2. The `MapAccumulator` constructor invokes `SetSemanticConfig()` at 0x3b8384.
3. The semantic setup allocates a `SemanticFuser` at 0x3ac928, calls its constructor at 0x3ac93c, and stores it in `MapAccumulator+0x8000+0x9a0 = +0x89a0` at 0x3ac948.
4. The independently verified `AI_STAIN_CLEANING` subscriber callback `ProcessStainCleanInfo(int*)` follows these *same pointer fields*: node+0x1380 → accumulator+0x89a0 → fuser+0xfd0, then uses an atomic AArch64 STLR at 0x1123a4.
5. `MapAccumulator::UpdateSemanticInfo()` also reads accumulator+0x89a0 at 0x3a5268.
6. `SemanticFuser::ProcessSemanticData()` calls `UpdateObstaclesWithThirdPartyInfo()` at 0x1e9ab4. That routine calls `UpdateCleanedStainId()` at 0x1e300c. The latter acquires the pending +0xfd0 ID, compares it to stain-record identifiers, changes a matching record's flags/state as appropriate, and clears +0xfd0. Combined semantic update conditions can set a changed-data flag +0x5e9 (0x1e9b18).

This establishes the **compiled object-identity link** left open by v182 and supports a *stain-marked-handled / semantic state refresh* interpretation. It does **not** identify a robot cleaning-task planner request. The constructor can replace previously allocated objects; same physical runtime instance, message delivery, shared Blackboard instance and concurrency lifetime are not established.

## Verification and availability
The self-contained validated offline ZIP is `X40-R2416-v183-sanitized-stain-perception-object-link.zip`, SHA-256 `302185d902c82ddfad8ad99eaf6920d5e0ac16d3dba2bf1957cbc6e4889cbc2d`. It includes the complete v182/v183 original-ELF verifier chain, 48 offline tests, sanitized evidence and checksums; 48 passed against exact original ELFs; without private binaries, 19 pass and 29 skip. No binaries are distributed.

The accompanying standalone *GitHub-side* Python check is an additional compact hash/instruction/BL-path checker; for complete v182–v183 ELF, relocation and mutation checks use the ZIP. No native proprietary ELF content is in this commit.

Keep original working v74: `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No robot access, task command, firmware change or CleanGenius activation occurred. The two observed v165 coarse-area revisits are **not** proved to be dirt-triggered.
