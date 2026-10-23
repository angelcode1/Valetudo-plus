#!/usr/bin/env python3
"""X40 R2416 v43: offline AvaNodeRoute factory Blackboard-argument lineage.

Usage: python3 x40_r2416_v43_factory_blackboard_verify.py ORIGINAL_ZIP RUNTIME_ZIP

Requires v36-v42 dependency verifiers alongside this script. Reads only local
firmware archives; never executes any vendor binary or connects to the robot.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v42_mapload_holder_lineage_verify import verify_v42


def verify_v43(original_zip, runtime_zip):
    # Includes five full original SHA-256 pins, three original/runtime byte
    # comparisons, effective RobotNode setting, and all v36-v42 regression gates.
    verify_v42(original_zip, runtime_zip)
    n = collect(original_zip, runtime_zip)['node_lethe.so']

    # AArch64 receiver identity: ctor saves x0 (this) at sp+0x68; +0x30 is
    # initialized to address of the embedded shared_ptr holder at this+0xfa8.
    for addr, word in {
        0x34c054: 0xf90037e0,  # str x0,[sp,#0x68]
        0x34c088: 0x913ea001,  # add x1,x0,#0xfa8
        0x34c098: 0xf9001841,  # str x1,[x2,#0x30]
    }.items():
        n.ins(addr, word)

    # NEW: Direct instantiateTreeNode(factory, name, instance, params, bb)
    # x1 is the ctor receiver restored from sp+0x68 at 0x355010, and x4 is
    # loaded from receiver+0x30 at 0x355028. The call is the unique direct BL
    # to the imported factory instantiateTreeNode stub in this ELF.
    for addr, word in {
        0x355010: 0xa9468be1,  # ldp x1,x2,[sp,#0x68]
        0x355028: 0xf9401824,  # ldr x4,[x1,#0x30]
        0x355050: 0xf9404be1,  # ldr x1,[sp,#0x90]
        0x355054: 0xf9408be0,  # ldr x0,[sp,#0x110]
    }.items():
        n.ins(addr, word)
    n.call(0x355058, 0x2778d0)
    require(n.bl_sites(0x2778d0) == [0x355058],
            'direct instantiateTreeNode call census changed')
    print('PASS AvaNodeRoute ctor uses receiver+0x30 as x4 Blackboard argument to direct instantiateTreeNode')

    # Four extra constructor buildTreeFromText calls use the same holder.
    for field, call, word in (
        (0x355114, 0x35511c, 0xf9401802),
        (0x3552c0, 0x3552c8, 0xf9401802),
        (0x3553e8, 0x3553f4, 0xf9401802),
        (0x3554dc, 0x3554e8, 0xf9401822),
    ):
        n.ins(field, word)
        n.call(call, 0x2753c0)
    require(n.bl_sites(0x2753c0)==[0x316600,0x35511c,0x3552c8,0x3553f4,0x3554e8],
            'direct buildTreeFromText call census changed')
    print('PASS four auxiliary AvaNodeRoute tree-text builds use the same +0x30 holder')

    # CORRECTION: BtTask constructor direct PLT call only occurs inside
    # DebugTask ctor; this separately takes its Blackboard as x1 and forwards
    # it to BtTask's third argument x2. Not evidence of main RobotNode creation.
    for addr, word in {
        0x316968: 0xaa0203e1,  # mov x1,x2 (name)
        0x31696c: 0xaa1303e2,  # mov x2,x19 (DebugTask supplied Blackboard holder)
    }.items():
        n.ins(addr, word)
    n.call(0x31697c, 0x27d220)
    require(n.bl_sites(0x27d220)==[0x31697c],
            'direct BtTask constructor PLT-call census changed')
    print('PASS BtTask constructor: sole direct PLT caller at DebugTask::DebugTask')

    print('X40_V43_FACTORY_BLACKBOARD_STATIC_PASS')
    print('BOUNDARY: selected instance name at direct factory call, initial MapLoad timing,')
    print('station-wash runtime Blackboard sharing, R2416 special-push producer and physical rewash remain unproven')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip')
    p.add_argument('runtime_zip')
    args=p.parse_args()
    try:
        verify_v43(args.original_zip,args.runtime_zip)
    except Exception as exc:
        print('X40_V43_STATIC_FAIL: '+str(exc),file=sys.stderr)
        sys.exit(1)