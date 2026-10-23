#!/usr/bin/env python3
"""X40 R2416 v38: offline pre-Loop SubTree identity / duplicate MapLoad audit.

Requires adjacent x40_r2416_v36_preloop_nodes_verify.py and
x40_r2416_v37_countryget_gate_verify.py.  Python stdlib only.
Reads owner-supplied ZIPs, never executes ELF content or contacts the robot.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import (
    collect,require,decode_bl_or_b
)
from x40_r2416_v37_countryget_gate_verify import verify_v37


def verify_v38(original_zip, runtime_zip):
    verify_v37(original_zip,runtime_zip)
    src=collect(original_zip,runtime_zip)
    tree=src['liblethe_tree.so']
    bt=src['libbehaviortree_cpp.so']

    # The compiler reuses the tail "SubTree" of the longer rodata literal
    # ClearFluctuationSubTree as an exact NUL-terminated node-type string.
    node_type=0x58fcdc
    require(tree.va(node_type,8)==b'SubTree\0','SubTree node-type literal changed')
    # Verify the actual AArch64 ADRP source and type address using the known
    # builder register (x22) setup; remain explicitly within the bounded block.
    tree.ins(0x30dae8,0xd0001416)  # ADRP x22: 0x58f000 page
    for addr in (0x30db14,0x30db50,0x30ded4,0x30e068,0x30e620):
        tree.ins(addr,0x913372c0) # ADD x0, x22, #0xcdc

    # Two distinct MapLoad instantiations exist in the bounded RobotNode region;
    # the second is after the pre-Loop attachment and is NOT one of the 15 slots.
    named_nodes=(
        ('MapLoad',0x585df8,0x30db08,0x30db18,0x30db24),
        ('RobotSysInit',0x585e00,0x30db44,0x30db54,0x30db60),
        ('StationSysInit',0x585e79,0x30dec8,0x30ded8,0x30e03c),
        ('RobotmodeInit',0x585e88,0x30e05c,0x30e06c,0x30e078),
        ('MapLoad',0x585df8,0x30e614,0x30e624,0x30e630),
    )
    for name,addr,prep,instantiate,attach in named_nodes:
        require(tree.va(addr,len(name)+1)==name.encode()+b'\0',
                f'instance-name literal changed: {name}')
        require((prep,prep+4) in tree.adrp_add_references(addr),
                f'name preparation not checked direct ADRP/ADD: {name} {prep:#x}')
        tree.call(instantiate,0x1c6620) # node construction helper
        tree.call(attach,0x1c6900) # control parent attachment
    # Exact reference census for the four string literals in this ELF.
    expected={
        0x585df8:[(0x30db08,0x30db0c),(0x30e614,0x30e618)],
        0x585e00:[(0x30db44,0x30db48)],
        0x585e79:[(0x30dec8,0x30decc)],
        0x585e88:[(0x30e05c,0x30e060)],
    }
    for addr,sites in expected.items():
        require(tree.adrp_add_references(addr)==sites,
                f'instance-name direct-reference census differs: {addr:#x}')
    require(decode_bl_or_b(tree,0x30dedc)==('B',0x30e034),
            'StationSysInit path no longer jumps over exception cleanup')

    # child_node_factory_instantiateTreeNode passes type, instance name, params
    # and factory's Blackboard into instantiateTreeNode, but does not itself
    # execute any subtree's tick().
    require(tree.symbol(b'_Z38child_node_factory_instantiateTreeNodePKcS0_RKSt6vectorISt4pairIN2BT19BehaviorTreeFactory8ConstStrES5_ESaIS6_EE')==0x567e90,
            'generated node-construction helper moved')
    tree.call(0x567f00,0x1c6650)
    # The base factory has a built-in SubTree manifest/registration path.
    require(bt.va(0xa9ae8,8)==b'SubTree\0','BT SubTree manifest spelling changed')
    require((0x62c0c,0x62c10) in bt.adrp_add_references(0xa9ae8),
            'built-in SubTree manifest reference changed')
    bt.call(0x62c74,0x3a8c0)  # registerBuilder@plt
    require(bt.symbol(b'_ZNK2BT19BehaviorTreeFactory19instantiateTreeNodeERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_RKSt6vectorISt4pairINS0_8ConstStrESB_ESaISC_EERKSt10shared_ptrINS_10BlackboardEE')==0x5f4c0,
            'factory node-instantiation entry moved')
    # This ordinary factory callback is not a tick observation.
    bt.call(0x5f638,0x398d0) # TreeNode::setBlackboard@plt
    bt.call(0x5f650,0x398c0) # initializeOnce@plt

    # These names are instance strings, not declarations of exported functions;
    # no matching buildX symbol is present in the pinned tree library's dynstr.
    dyn=tree.secbytes(tree.section('.dynstr'))
    for name in ('MapLoad','RobotSysInit','StationSysInit','RobotmodeInit'):
        require(('build'+name).encode() not in dyn,
                'new matching exported buildX symbol: '+name)
    print('PASS 5 original SHA-256 pins and 3 active/original byte comparisons (via v37)')
    print('PASS four pre-Loop SubTree type+instance-name factory paths')
    print('PASS second distinct MapLoad constructor at 0x30e624 and parent attach at 0x30e630')
    print('PASS built-in SubTree manifest registration, node helper and Blackboard initialization calls')
    print('PASS bounded dynamic-symbol census; no buildMapLoad/buildRobotSysInit/buildStationSysInit/buildRobotmodeInit exports')
    print('X40_V38_SUBTREE_IDENTITY_STATIC_PASS')
    print('BOUNDARY: no concrete subtree return statuses or runtime tick outcomes were observed;')
    print('          the R2416 special_push_clean_dish eligibility and physical rewash remain unproven.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip')
    p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify_v38(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V38_STATIC_FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)