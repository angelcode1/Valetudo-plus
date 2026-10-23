#!/usr/bin/env python3
"""Offline v42: bounded Start_Map_Load writer and Blackboard-holder lineage.

Inputs: original owner-provided firmware ZIP and v27 runtime collection ZIP.
Requires the v36-v41 verifiers packaged alongside this file. Uses only the
Python standard library; does not execute ELF data or access a network/device.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v41_mapload_charger_verify import verify_v41

# These AppEditMap subpaths load the same AvaNodeRoute holder field before
# dispatching the typed Blackboard::set<bool> call checked by v41.
APP_EDIT_FIELD_LOADS = {
    0x6c8458: 0x6c8484,
    0x6d3f54: 0x6d3f80,
    0x6d4cdc: 0x6d4d08,
    0x6d7bc0: 0x6d7bec,
    0x6d80a4: 0x6d80d0,
}
# Class-specific member offset, not evidence of cross-class pointer equality.
SLAM_FIELD_LOADS = {0x842ad0: 0x842afc, 0x842f28: 0x842f58}
TACTICS_BLACKBOARD_ACCESSORS = {
    0x270fbc: 0x270ff0,
    0x2ba5ac: 0x2ba5dc,
    0x2e6bc4: 0x2e6bf4,
}

def verify_v42(original_zip, runtime_zip):
    verify_v41(original_zip, runtime_zip)
    libraries = collect(original_zip, runtime_zip)
    node = libraries['node_lethe.so']
    tactics = libraries['liblethe_tactics_tree.so']

    # Prior v22/v23 constructor and tree build lineage, reproduced here.
    node.ins(0x34c088, 0x913ea001)  # add x1,x0,#0xfa8
    node.ins(0x34c098, 0xf9001841)  # str x1,[x2,#0x30]
    node.ins(0x355108, 0xf94037e0)  # reload constructor receiver
    node.ins(0x355114, 0xf9401802)  # ldr x2,[x0,#0x30]
    node.call(0x35511c, 0x2753c0) # BT::buildTreeFromText

    # Class-member provenance of the five AppEditMap typed set<bool> sites:
    # the value in x2 is the pointer to the AvaNodeRoute+0x30 holder.
    for source, target in APP_EDIT_FIELD_LOADS.items():
        node.ins(source, 0xf9401802)  # ldr x2,[x0,#0x30]
        node.ins(source+0x10, 0xf9400053 if source != 0x6c8458 else 0xf9400054)
        node.call(target, 0x2795c0)
    print('PASS five AppEditMap setters load AvaNodeRoute member +0x30')

    # MT_ChangeMap read and previously unclassified Matter run-mode setter
    # both use the same AvaNodeRoute member. The latter's slot +0x20 is the
    # concrete BlackboardRobinMap / StaticBlackboardRobinMap virtual set slot
    # (as separately established in v18). Do not infer payload type or runtime use.
    node.ins(0x440d98, 0xf9401a62) # ldr x2,[x19,#0x30]
    node.ins(0x440de0, 0xf9401442) # vtable contains +0x28
    node.ins(0x440de4, 0xd63f0040)
    expected = {
        0x447e1c: 0xf9401a62, # ldr x2,[x19,#0x30]
        0x447e2c: 0xf9400053, # ldr x19,[x2]
        0x447e34: 0xf9400660, # ldr x0,[x19,#8]
        0x447e38: 0xb4fff760, # skip on null pointer
        0x447e3c: 0xf9400003, # ldr x3,[x0]
        0x447e44: 0xd2800024, # mov x4,#1 (not decoded type)
        0x447e50: 0xaa1703e1, # key argument from x23
        0x447e54: 0xf9401063, # vtable set +0x20
        0x447e60: 0xaa1603e2, # payload pointer x22
        0x447e64: 0xd63f0060, # blr x3
    }
    for address, word in expected.items(): node.ins(address, word)
    require((0x447e20,0x447e24) in node.adrp_add_references(0x9f7c88),
            'MT_SetRunModeProcessSUB literal reference changed')
    print('PASS previously unclassified MT_SetRunModeProcessSUB site: virtual set +0x20 via AvaNodeRoute+0x30')

    # SlamControl uses a separate class receiver (also offset +0x30).
    # Numeric field offset reuse does not demonstrate pointer aliasing.
    for addr, call in SLAM_FIELD_LOADS.items():
        node.ins(addr, 0xf9401a62)
        node.call(call, 0x2795c0 if call==0x842afc else 0x279900)
    print('PASS separate SlamControl+0x30 holder for one set<bool> and one get<bool> site')

    # The tactics-library writers use BT::TreeNode::blackboard(), a different
    # accessor from the class-member loads above. Do not assume shared pointee.
    for accessor, setter in TACTICS_BLACKBOARD_ACCESSORS.items():
        tactics.call(accessor, 0xc60b0)
        tactics.ins(accessor+4, 0xaa0003e2) # mov x2,x0
        tactics.call(setter, 0xc79b0)
    print('PASS three tactics writers obtain Blackboard via TreeNode::blackboard()')
    print('PASS original SHA pins; active/original library byte identity; v36-v41 regression checks')
    print('X40_V42_MAPLOAD_BLACKBOARD_HOLDER_STATIC_PASS')
    print('BOUNDARY: concrete pointer equality, startup ordering, R2416 special-push eligibility and physical rewash are NOT proven')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_zip')
    parser.add_argument('runtime_zip')
    args=parser.parse_args()
    try:
        verify_v42(args.original_zip,args.runtime_zip)
    except Exception as exc:
        print('X40_V42_STATIC_FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)