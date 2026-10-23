# Reproduce v83 without distributing proprietary firmware

The separate sanitized v83 ZIP distributed to the operator contains `x40_r2416_v83_special_key_consumers_verify.py`, `x40_r2416_v82_root_blackboard_bridge_verify.py`, the full technical report, and README. The **owner-private** `X40-R2416-v62-readonly-20261023T051829Z.zip` is **not** included or committed.

With both sanitized verifier scripts adjacent:

```sh
python3 x40_r2416_v83_special_key_consumers_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test

python3 x40_r2416_v82_root_blackboard_bridge_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Verify 16 new mutation refusals, and 29 root-bridge mutation refusals. Both scripts read the ELF bytes in memory directly from ZIP, validate three SHA-256 pins and exact instruction/callee boundaries, and make no network or device calls.

**Scope limit:** the direct key-reference census checks ADRP+ADD pairings within six instructions of one another in `node_lethe.so` `.text`; it is not a complete all-module, all-runtime key-writer proof. A compiled root argument passed to behaviour-tree construction is not proof of the active StationWash subtree's Blackboard object identity. No evidence of an extra physical rewash is established here.
