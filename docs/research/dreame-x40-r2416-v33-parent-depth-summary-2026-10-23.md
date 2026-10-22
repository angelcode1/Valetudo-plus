# X40 R2416 v33 — compiled StationWash parent-depth summary

Date: 2026-10-23. Offline native-code research only; no device operations or firmware changes.

SHA-pinned liblethe_tree.so includes a generated helper called from RobotNode at 0x30ee30. That helper starts at 0x2edb70 and ends with a tail branch to decrease_depth at 0x2ee9c8. The bounded instruction census found 27 depth increases and 27 decreases in the helper. The examined outer RobotNode builder region had 76 increases and 76 decreases.

Immediately before constructing StationWash.xml, the directly emitted ancestor depth stack corresponds to SequenceStarRoF → Loop → DoWhile. This is a static construction ledger, not an execution trace. The Loop has a literal num_cycles parameter of -1, but no conclusion about unlimited cleaning or physical washing follows.

The full private offline verifier checked original ELF SHA-256 pins and the generated instruction anchors. Its companion v33 research package is retained outside the public repository. Native ELF files, private configuration and device identifiers are intentionally excluded.

Unresolved: runtime subtree ticks, effective Blackboard identity, production of special_push_clean_dish on R2416, and a second physical mop wash.
