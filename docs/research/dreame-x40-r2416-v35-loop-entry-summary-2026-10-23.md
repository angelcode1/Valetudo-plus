# X40 R2416 v35 — SequenceStarRoF / Loop gate summary

Date: 2026-10-23. Offline, SHA-pinned instruction-level evidence; no robot access.

The examined SequenceStarRoFNode::tick implementation retains its current child index for numeric status 1, advances on 2, and resets/halts on 3. Later siblings are therefore not unconditionally reached. The examined LoopNode::tick increments its completed-cycle counter on numeric status 2 or 3; status 1 does not advance the counter. A signed nonnegative bound check skips its fixed-count exit when num_cycles=-1.

In RobotNode's generated direct-root construction scope, the v35 checker found 15 direct child attachments before the Loop (16th attachment at 0x30e11c). The Loop's decorator child is DoWhile, which contains the compiled StationWash subtree.

These are compiled instruction/control-flow relationships, not actual status observations. Nested generated-helper children are excluded from the 15-site direct census. See the following v36 census for their compiled identities.

The full v35 verifier and report were separately packaged offline and passed hash- and tamper-guarded tests. No proprietary native library, unfiltered configuration or credentials were committed.

Unresolved: which preceding node statuses occur on R2416 and whether the eligibility marker or physical rewash is ever triggered.
