# Dreame X40 R2416 — v140 upstream route/model/tree Blackboard provenance

**25 October 2026 · SHA-256-pinned original ARM64 ELF static audit, fully offline.** No robot access, executable code changes, original firmware publication, MIOT writes, cloud sessions or station actions.

## New finding: common route-level Blackboard reference source

v138 established `node_lethe.so:ProcessModelInfo()` calls the guarded typed `BT::Blackboard::set<bool>("enable_turbidity")`, while the native station node uses a `TreeNode::blackboard()` entry-availability test. v139 verified compiled `buildStationWash()` passes its own input Blackboard through factory construction to `TreeNode::setBlackboard()`. v140 connects these through the original `ancp::AvaNodeRoute` constructor.

The SHA-pinned native constructor at `0x34c020` contains the **only direct BL** to `ProcessModelInfo()` via its PLT within `node_lethe.so` `.text`, at **`0x352308`**. Its first argument register `x0` loads a Blackboard reference from the route object's **`+0x30` field** (`0x3522f8`, `0x352304`).

In the **same constructor, after the model call**, four direct invocations of `BT::buildTreeFromText()` each use **the same route field `+0x30`** as the native Blackboard argument source (ABI `x2`):

| Tree build BL | Route +0x30 load | Proven argument |
|---|---|---|
| `0x35511c` | `0x355114` | `[route+0x30] → x2` |
| `0x3552c8` | `0x3552c0` | `[route+0x30] → x2` |
| `0x3553f4` | `0x3553e8` | `[route+0x30] → x2` |
| `0x3554e8` | `0x3554dc` | `[route+0x30] → x2` |

The only **fifth** direct `buildTreeFromText()` invocation in this ELF is at `0x316600`, in a separate `BtTask` constructor. It is **not** included in the four route-constructor calls.

In the original `libbehaviortree_cpp.so`:

- `BT::buildTreeFromText()` begins at `0x70a10`, retains the incoming Blackboard `x2` in `x19` at `0x70a3c`, and forwards it as `x2` at `0x70a6c`;
- It calls `XMLParser::instantiateTree()` at `0x70a84`, which saves its received Blackboard argument at `0x6e244`;
- The v139 compiled StationWash/factory source evidence independently confirms the node builder-to-`TreeNode::setBlackboard()` forwarding path when that builder is selected.

**Proved:** the compiled model-key producer and four tree-building calls source their Blackboard *reference arguments* from the **identical route-object field**, connecting the previously isolated producer and consumer factory handoffs.

## Crucial remaining limitations

**Same field is not a runtime object-identity trace.** An intervening call could replace the field, a tree may be instantiated in an alternate context, and subtree remapping may alter effective lookup scope. The captured root preference is `RobotNode`, but actual native tree/subtree selection and tick state have not been observed. The station key guard checks *entry lookup success*, not the typed Boolean value.

The exact owner model's static CFG still contains **ten possible locally positive-sourced direct writes** to the model eligibility flag at `SP+0xBC`, not a uniquely executed instruction. Neither the effective live `enable_turbidity` value nor a dirt-triggered **second physical mop wash** has been established. No new device-side wash commands should be tried.

## Repeatable offline verifier

The separately delivered **sanitized** `X40-R2416-v140-sanitized-route-tree-blackboard.zip` (SHA-256 `54238940e0e4e9c36dbabb9f86a0040935ade94e6bb41d60384a4e27a411ca72`) contains `x40_r2416_v140_route_tree_blackboard_verify.py`, all sanitized v112–v139 Python dependencies, full report, aggregate JSON, README and SHA256SUMS. Original proprietary ELFs, complete disassembly, raw model value/configuration and credentials are **not** included.

```sh
unzip ~/Downloads/X40-R2416-v140-sanitized-route-tree-blackboard.zip -d ~/Downloads
cd ~/Downloads/x40-v140-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v140_route_tree_blackboard_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

A **fresh extraction** passed archive integrity, every SHA256SUMS check, all ten original ELF SHA-256 checks, the v139 station-factory handoff and earlier ten-writer regressions, source-pinned call and corridor inspections, and **28 independent native original-instruction mutations** rejected without using whole-ELF SHA mismatch as the mutation oracle.

**Next:** source-audit the dynamic XML subtree factory/remap path, and test possible `AvaNodeRoute+0x30` field replacements across the caller interval. If those cannot close live shared-scope identity, only expressly authorized, low-impact passive runtime evidence—not invented path choice—could identify an executed writer or effective station key.

**Safety unchanged:** last owner-confirmed Valetudo+ v74; SmartHost=0, `writeGateOpen=false`, original launcher and rollback assets intact. GitHub `master`, unrelated branches, executable runtime and robot unchanged.
