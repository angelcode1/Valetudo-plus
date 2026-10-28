# X40 R2416 v138 — native Blackboard producer/consumer scope boundary

**24 October 2026 · offline SHA-256-pinned original vendor ARM64 firmware audit.** No robot, cloud, station, Valetudo runtime or `master` modification.

## Source-verified finding

The original `node_lethe.so:ProcessModelInfo(std::shared_ptr<BT::Blackboard>&)` saves its *input* shared-pointer address in `x27` at `0x46fd74`. It loads the Blackboard object via `[x27]` at `0x471840`, moves that object into the typed setter target register at `0x47184c`, and calls **`BT::Blackboard::set<bool>` for `enable_turbidity` at `0x47185c`**, guarded by a separate `SP+0xBC` model-group test at `0x47182c–0x471830`. Prior v117 exact-key and named typed-setter checks are replayed.

The original, separate `liblethe_tactics_tree.so:StationHandle::SweepStationContorl::InitTurbidityCheckInfo()` obtains its lookup context by calling **`BT::TreeNode::blackboard()` at `0x24e8c8`**. Its original independent `enable_turbidity` key literal is at `0x33b2f8`, versus `0x9fd2e0` in the producer library. The station code checks the lookup context at `0x24e920`, invokes an indirect Blackboard entry lookup at `0x24e930`, tests the *lookup result* low byte at `0x24e934`, and branches when false at `0x24e938`.

Source-pinned absent-entry route:

```text
0x24e938 (no entry) -> 0x24eb9c (cleanup)
  -> 0x24eba4 / 0x24ebb4 -> 0x24e95c (common continuation)
```

That route **bypasses** the separately named `TurbidityRecleanAndRewashSet()` call at `0x24e958`. When entry lookup succeeds, the compiled path goes through optional string cleanup at `0x24e944`, into `0x24e954`, and *can* execute the helper at `0x24e958` before both paths join at `0x24e95c`. The v116 named helper relocation, native flag and key-regression checks are replayed.

### Essential distinction

**Blackboard entry availability is not a direct typed Boolean read of that entry.** The compiled station-side branch acts on the result of a virtual lookup. Even if the producer's compiled `set<bool>` guard is true, **identical native key spelling does not establish identical Blackboard object identity**. The producer uses a caller-supplied Blackboard shared pointer; the station reader calls `TreeNode::blackboard()` and may see a different/remapped subtree, timing, or value.

No active `StationWash.xml`/Blackboard remapping is available from the existing captured firmware. Consequently neither live `enable_turbidity` presence/value nor a native StationWash gate value is established. v116 already showed that the station's configuration-derived completion byte `+0x688` starts at one and can be recomputed from `smart_hosting_switch`, `smart_auto_wash_switch`, and `smart_auto_mop_switch` only on its guarded path; skipped recomputation can leave initial/stale values.

v137's actual-model bounded source graph still permits **ten positive-sourced direct `SP+0xBC` writers**: `0x474cd0`, `0x475bc4`, `0x476798`, `0x4773dc`, `0x4774d8`, `0x4775a4`, `0x4776b4`, `0x47776c`, `0x478160`, `0x47826c`. v138 does **not** exclude any of them, observe an executed instruction, prove the live flag is true, or establish a genuine dirt-triggered **second physical mop wash**.

## Reproducibility

The owner-side sanitized `X40-R2416-v138-sanitized-blackboard-scope-boundary.zip`, SHA-256 **`7aab034bcf7325476840996c76b537cb0b044fd9b99050649b5c0169ec6f7e39`**, contains `x40_r2416_v138_blackboard_handoff_verify.py`, its v112–v137 sanitized Python dependencies, complete detailed report, aggregate JSON, README and SHA256SUMS. The original ten vendor ELFs and original model literal **are not included**.

```sh
unzip ~/Downloads/X40-R2416-v138-sanitized-blackboard-scope-boundary.zip -d ~/Downloads
cd ~/Downloads/x40-v138-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v138_blackboard_handoff_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Original tested output:

```text
X40_V138_ORIGINAL_SHA256_ELF_PINS_PASS count=10
X40_V138_V137_TEN_POSITIVE_SOURCE_REGRESSION_PASS candidates=10
X40_V138_INPUT_BLACKBOARD_TYPED_BOOL_SET_BOUNDARY_PASS
X40_V138_TREENODE_BLACKBOARD_LOOKUP_AND_GUARDED_HELPER_PASS
X40_V138_ABSENT_KEY_BYPASSES_RECALCULATION_PASS
X40_V138_DIFFERENT_BLACKBOARD_PROVENANCE_PASS shared_object_identity=NOT_PROVEN
X40_V138_SOURCE_MUTATIONS_REJECTED count=23
LIMIT: key presence is not key Boolean value; no active shared scope or physical rewash demonstrated
```

Four complete original native instruction corridors, named PLT identities, key literals, branch destinations, 21 local instruction anchors, and **23 independently mutated original source opcodes/key bytes** are checked without relying on full-ELF checksum mismatch as the mutation oracle. Separately, all ten original source hashes, prior v116/v117 checks and the v137 candidate-source regression pass. ZIP CRC, SHA256SUMS and a clean-extraction replay pass.

**Next proof gate:** an authenticated native station tree registration/remapping or an explicitly authorized passive, read-only observation of effective station Blackboard key availability and naturally occurring wash transitions. Do not force Blackboard switches, fake dirt, issue guessed station commands, install risky instrumentation, or relax the experimental write gate.

**Safety preserved:** last operator-confirmed Valetudo+ v74, SmartHost=0, `writeGateOpen=false`, original launcher and rollbacks. Only sanitized research files added; no private ELF, APK, model literals, raw configuration, maps, logs, credentials, or command bytes were committed.
