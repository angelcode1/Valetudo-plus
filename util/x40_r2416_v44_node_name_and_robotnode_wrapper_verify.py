#!/usr/bin/env python3
"""R2416 v44 static verification: auxiliary node name and configured root wrapper.

Usage: python3 x40_r2416_v44_node_name_and_robotnode_wrapper_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Dependencies: v36-v43 Python verifiers from the complete audit bundle.
Offline/read-only. Never executes an ELF or contacts a device.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect,require
from x40_r2416_v43_factory_blackboard_verify import verify_v43


def verify_v44(reference, runtime):
    verify_v43(reference,runtime)
    n = collect(reference,runtime)['node_lethe.so']

    # The AArch64 ADRP/ADD pair for the two string ctor calls is explicit.
    # Each creates a std::string with the literal FollowWallModeDeal; not
    # the YAML-selected RobotNode registration.
    require(n.va(0x9d64b8,19)==b'FollowWallModeDeal\0',
            'factory registration/instance literal changed')
    for a,w in {
        0x354fbc:0xd0003413, # adrp x19,0x9d6000
        0x354fc0:0x9112e261, # add x1,x19,#0x4b8 -> FollowWallModeDeal
        0x354fc8:0xf9403be0, # ldr x0,[sp,#0x70] (second string destination)
        0x354fcc:0x9112e261, # add x1,x19,#0x4b8
        0x355010:0xa9468be1, # ldp x1,x2,[sp,#0x68] (prepares instance)
        0x355028:0xf9401824, # ldr x4,[x1,#0x30]
        0x355050:0xf9404be1, # ldr x1,[sp,#0x90] registration ID
        0x355054:0xf9408be0, # ldr x0,[sp,#0x110] factory receiver
    }.items(): n.ins(a,w)
    n.call(0x354fc4,0x31cdc0)  # std::string construction helper
    n.call(0x354fd0,0x31cdc0)
    n.call(0x355058,0x2778d0) # instantiateTreeNode
    print('PASS direct instantiateTreeNode registration and instance names: FollowWallModeDeal')

    # The OTHER, later buildTreeFromText is a dynamically synthesized wrapper.
    prefix=b'<root main_tree_to_execute="BehaviorTree">\n        <BehaviorTree ID="BehaviorTree"><SubtreeCondition subtree_file_path="'
    suffix=b'"/></BehaviorTree></root>'
    require(n.va(0x9d3380,len(prefix))==prefix,'configured tree wrapper prefix changed')
    require(n.va(0x9d3400,len(suffix))==suffix,'configured tree wrapper suffix changed')
    # Input Parameter::GetInstance returns Parameter*. Its +0x8 member holds
    # the std::string data pointer and +0x10 holds its length.
    for a,w in {
        0x3551e8:0x911c43fc, # add x28,sp,#0x710 wrapper destination
        0x3551ec:0xd00033e1, # adrp x1,0x9d3000
        0x3551f0:0xaa1c03e0, # mov x0,x28
        0x3551f4:0x910e0021, # add x1,x1,#0x380 -> prefix
        0x355214:0xf9403be1, # ldr x1,[sp,#0x70] temp string
        0x355218:0xaa0003e2, # mov x2,x0 -> Parameter*
        0x35521c:0xf9403be0, # ldr x0,[sp,#0x70]
        0x355228:0xa9408841, # ldp x1,x2,[x2,#8] field+length
        0x35522c:0x8b020022, # add x2,x1,x2 -> end
        0x35525c:0xaa1c03e0, # mov x0,x28 -> wrapper
        0x355264:0x97fc8e6f, # BL append (also checked below)
        0x3552a0:0xd00033e0, # adrp x0,0x9d3000
        0x3552a4:0xd2800322, # mov x2,#25 -> suffix size
        0x3552a8:0x91100001, # add x1,x0,#0x400 -> suffix
        0x3552b4:0xf94037e0, # ldr x0,[sp,#0x68] route receiver
        0x3552bc:0xaa1c03e1, # mov x1,x28 -> wrapper
        0x3552c0:0xf9401802, # ldr x2,[x0,#0x30] shared Blackboard holder
        0x3552c4:0xf9408be0, # ldr x0,[sp,#0x110] factory
    }.items():n.ins(a,w)
    n.call(0x3551f8,0x31cdc0)  # std::string prefix constructor
    n.call(0x355210,0x2785d0) # Parameter::GetInstance
    n.call(0x355230,0x31aa40) # std::string range construction from Parameter member
    n.call(0x355264,0x278c20) # append configured tree name
    n.call(0x3552b0,0x278c20) # append XML suffix
    n.call(0x3552c8,0x2753c0) # BT::buildTreeFromText
    # The first output-tree word is moved into an AvaNodeRoute member. Other
    # adjacent words are assigned at +0xf50 / +0xf58 / +0xf60.
    for a,w in {
        0x3552cc:0xf94037e0, # ldr x0,[sp,#0x68], AvaNodeRoute
        0x3552d4:0xf941ebe1, # ldr x1,[sp,#0x3d0], buildTree result
        0x3552d8:0xf907a401, # str x1,[x0,#0xf48], store tree
        0x3552e8:0xf907a801, # str x1,[x0,#0xf50]
        0x3552f8:0xf907ac01, # str x1,[x0,#0xf58]
        0x355308:0xf907b003, # str x3,[x0,#0xf60]
    }.items():n.ins(a,w)
    print('PASS built RobotNode-wrapper tree moved into AvaNodeRoute+0xf48 and adjacent members')
    print('PASS configured RobotNode selector appended from Parameter+0x8 to SubtreeCondition XML wrapper')
    print('PASS direct configured-wrapper buildTreeFromText passes AvaNodeRoute+0x30 Blackboard holder')

    # Two additional fixed XML wrappers on the same holder + the preceding
    # ReuseTree.xml wrapper are explicitly identified, not called RobotNode.
    for addr,label in [
        (0x9d64d0,b'<SubtreeCondition subtree_file_path=\n        "ReuseTree.xml"'),
        (0x9d6578,b'<Condition ID="GridmapInit"'),
        (0x9d6600,b'<Condition ID="TypeInterfaceInit"'),
    ]:
        require(label in n.va(addr,240).split(b'\0',1)[0],
                'auxiliary wrapper literal changed at %#x'%addr)
    for a,w in {
        0x3550f8:0xb0003401, # adrp x1,0x9d6000
        0x3550fc:0x91134021, # add x1,x1,#0x4d0 ReuseTree.xml
        0x3553d0:0xb0003401, # adrp x1,0x9d6000
        0x3553d4:0x9115e021, # add x1,x1,#0x578 GridmapInit
        0x3554c4:0xb0003401, # adrp x1,0x9d6000
        0x3554c8:0x91180021, # add x1,x1,#0x600 TypeInterfaceInit
    }.items():n.ins(a,w)
    for a in (0x35511c,0x3553f4,0x3554e8):n.call(a,0x2753c0)
    print('PASS other buildTreeFromText wrappers: ReuseTree.xml, GridmapInit, TypeInterfaceInit')
    print('X40_V44_CONFIGURED_ROOT_WRAPPER_STATIC_PASS')
    print('BOUNDARY: call execution, effective descendants, live Blackboard identity,')
    print('R2416 special_push_clean_dish producer and physical rewash remain unproven')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    args=p.parse_args()
    try:verify_v44(args.original_zip,args.runtime_zip)
    except Exception as exc:
        print('X40_V44_STATIC_FAIL: '+str(exc),file=sys.stderr)
        sys.exit(1)