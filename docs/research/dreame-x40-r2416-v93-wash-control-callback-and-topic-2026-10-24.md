# Dreame X40 R2416 — v93 typed wash-control callback and WASH_CONTROL publisher

**2026-10-24 · Offline instruction-level verification, owner-private original firmware.** No robot connection, MIOT write, process restart, firmware replacement or proprietary vendor content committed.

## New static wash-control route

v92 established two separate native senders in `AvaNodeRoute::UpdateOutput()`: station-set control on `STATION_UI` before the rewash-marker consumer, and `SendWashContrlInfo()` after it. v92 identified an additional but unclassified `wash_machine_control` reference at VA `0x32734c`. **v93 resolves that reference into a registered function callback and typed Blackboard map writer, with a cross-library wash-station node that retrieves and invokes that callback.**

1. The `node_lethe.so` `AvaNodeRoute` constructor accesses the route root Blackboard at **`+0x30`** at `0x356924–0x35693c`, creates a callable wrapper bound to its **local code entry `0x3272c0`** (`0x35692c–0x356950`), and registers the callable under the exact key **`SetWashMchineControl`** (vendor misspelling intentional; literal VA `0x9d69a0`). The registration is through an indirect Blackboard set-style dispatch at `0x356974`/`0x3569b4`, using the explicit RTTI `std::function<void(int, WashMachineControl)>` at GOT `0xb78998` and function `linb::any` vtable GOT `0xb7e788`.

2. The callback body at `0x3272c0` takes the captured route, accesses its **root Blackboard `+0x30`** (`0x3272e0`, `0x327300`), constructs **`wash_machine_control`** (literal `0x9d3c78` at `0x32734c–0x327350`), gets the current entry through an indirect lookup (`0x327380–0x327394`), and handles **`std::map<int,WashMachineControl>`** by typed `SafeAny` comparison and per-key map insert/update. It finally stages the typed map under the same key with an indirect setter-style call (`0x327660–0x327668`, `0x3276bc–0x3276c4`, `0x327730–0x327734`). Map RTTI and `linb::any` vtable are pinned to original GOT relocations `0xb7f948`, `0xb783c8`.

3. In the **different** original `liblethe_tactics_tree.so`, `WashStationManag::StartMachineCtrl_ELECT(BT::TreeNode&)` starts at VA `0x1f3670`. It calls `BT::TreeNode::blackboard()` at `0x1f36a0`, resolves the same **`SetWashMchineControl`** key at `0x1f36d4–0x1f36d8` (literal `0x32ed00`), calls the exact typed `BT::Blackboard::get<std::function<void(int,WashMachineControl)>>` PLT at **`0x1f3718`**, and conditionally invokes the retrieved function at `0x1f37c8` / `0x1f385c`. These are compiled machine-control parameters, **not validated external device opcodes**.

4. In `node_lethe.so` the constructor also advertises topic **`WASH_CONTROL`** (literal `0x9d7140`, reference `0x35cd40–0x35cd44`) with **`WashControlMsg`** RTTI (GOT `0xb7aff0`) through `AvaNode::AdvertiseImpl` at `0x35cd60`. The publisher holder is stored at **`AvaNodeRoute+0x2a70`** at `0x35cdd8`. As established in v92, `SendWashContrlInfo()` reads `wash_machine_control` through the same route root `+0x30`, and the typed publish call at `0x7d77f8` reads **the same publisher member `+0x2a70`** (`0x7d77e8–0x7d77f4`).

## Evidence levels and remaining gate

This establishes a coherent **compiled callback-registration → station-node typed getter/invocation → route-root map update → typed WASH_CONTROL publisher** model. It is materially stronger than merely matching names across libraries. The constructor callback and sender both refer to the same **route-object member offset +0x30**; however the station node's independently obtained `TreeNode::blackboard()` handle is not shown to resolve to that root at runtime. Authentic `StationWash.xml` has not been collected in earlier bounded searches and its key remapping, child scope and actual execution are unknown.

Also unproven: whether `WASH_CONTROL` has a receiving consumer in the evidence set or firmware external to it; whether the `WashControlMsg` payload is accepted or physically actuated; whether `special_push_clean_dish` becomes available on R2416; and whether a **genuine turbidity failure** causes a **second mop wash** rather than routine wash-station control. **The v67 `r2343_start_rewash` marker-to-`wash_times` bookkeeping is still not connected to this callback or wash-control map**. Do not conflate these independent compiled flows.

## Reproducible offline verification

Original ELF SHA-256 pins:
- `node_lethe.so` `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`
- `liblethe_tactics_tree.so` `da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c`

The operator-only sanitized ZIP `X40-R2416-v93-sanitized-wash-control-callback-20261024.zip` includes a **standalone Python 3 standard-library verifier**, a detailed report and README, and **no original ELF, XML, firmware archive, private settings, maps or credentials**. Re-run with private original `X40-R2416-v62-readonly-20261023T051829Z.zip`:

```sh
python3 x40_r2416_v93_wash_control_callback_bridge_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
```

Successful run, observed on original private evidence in this research pass:

```text
X40_V93_WASH_CONTROL_TOPIC_WASHCONTROLMSG_PUBLISHER_STATIC_PASS
X40_V93_ROUTE_REGISTERED_TYPED_WASH_FUNCTION_STATIC_PASS
X40_V93_STATION_NODE_GETS_AND_INVOKES_WASH_FUNCTION_STATIC_PASS
X40_V93_WASH_FUNCTION_TO_ROOT_MAP_AND_SENDER_STATIC_PASS
X40_V93_V92_OUTPUT_ORDER_REGRESSION_PASS
X40_V93_INSTRUCTION_LITERAL_MUTATIONS_REJECTED count=56
LIMIT: static callback type/key/map and publisher; active tree Blackboard identity, marker-to-wash mapping and physical extra wash UNPROVEN
```

The original source receives **full** exact-symbol/relocation, callsite and ADRP+ADD verification (including v92 regressions); each of **56 separate one-byte mutations** is screened against the exact pinned instruction/literal anchor set to keep the offline self-test bounded. These are **not** 56 live device scenarios. SHA-256 of the Python verifier `7efe73b87b4ca2608392f4996a04d7805e61597bea17889d98aaeb772b041440`, sanitized ZIP `b831885a7089e0e489ac9b80a1ae7df417ecbc06730173128e00965502df19d2`.

## Follow-up

Confirm active `WashStationManag` node placement and `SetWashMchineControl` effective Blackboard inheritance; locate the `WASH_CONTROL` subscriber and interpret only verified command semantics; find a causal route from native turbidity/reclean decisions through an actual extra wash actuation. Do not send guessed `WashControlMsg` values, trigger artificial dirt or mutate `SmartAutoMop=-1`.

**Preserve safe live state**: last user-confirmed working Valetudo+ **v74**, `SmartHost=0`, experimental `writeGateOpen=false`, original launcher restored and rebooted, settings baseline and v70/v73/parent/vendor backups retained. No on-robot action warranted.
