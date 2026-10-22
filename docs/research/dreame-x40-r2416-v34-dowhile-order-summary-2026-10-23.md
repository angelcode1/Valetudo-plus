# X40 R2416 v34 — DoWhile direct-child-order summary

Date: 2026-10-23. SHA-pinned, offline-only static research.

In the verified RobotNode generated DoWhile construction scope, a bounded direct-call census counted 50 control-parent child-attachment sites, excluding those emitted by nested generated helpers. StationWash.xml is direct site 23 and RobotDropCharger is direct site 24, constructed in sequence.

The pinned libbehaviortree_cpp.so DoWhileNode::tick implementation advances through child slots on its examined normal path rather than short-circuiting simply on each child's returned status. The examined end-of-tick return/halt path is status-sensitive. This is not proof that the enclosing Loop or sequence ticks this DoWhile instance in a live washing session.

The separate private v34 verifier reproduced the original/runtime hash pins, the direct-site census, and selected tick/branch instructions; it rejected a modified runtime library. No vendor binaries are part of this repository.

Unresolved: the parent entry conditions, station wash runtime status, R2416 special-push key eligibility, and rewash actuation.
