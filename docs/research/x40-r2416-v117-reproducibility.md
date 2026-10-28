# X40 R2416 v117 — research provenance and verifier

The repository files are **sanitized research output**, not a robot-side patch. The complete validated offline verifier and its v112–v116 imported modules were delivered to the operator in `X40-R2416-v117-sanitized-native-switch-provenance.zip`.

The verifier consumes the operator-owned `X40-R2416-v62-readonly-20261023T051829Z.zip` privately, checks 10 SHA-256-pinned original ELFs and v116 regression anchors, and rejects 37 independently modified native instruction/key sites. See the v117 report for the exact invocation.

Do not commit private vendor ELF, original device settings/logs/maps, or any secrets to this public fork. The research branch intentionally changes **no** Valetudo runtime files. The last working device configuration is not changed or inferred from the static checks.

The main unresolved gate is whether the R2416 model's branch actually reaches the guarded `enable_turbidity` writer and whether that key participates in an active shared/remapped StationWash Blackboard. No second physical mop wash is proven.
