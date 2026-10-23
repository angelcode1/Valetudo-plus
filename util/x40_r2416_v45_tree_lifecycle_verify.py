#!/usr/bin/env python3
"""R2416 v45: pinned static audit of retained RobotNode tree lifecycle and tick boundary.

Run: python3 x40_r2416_v45_tree_lifecycle_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Dependencies: bundled v36–v44 verifier scripts. Offline-only; no device or ELF execution.
"""
import argparse
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect,require
from x40_r2416_v44_node_name_and_robotnode_wrapper_verify import verify_v44


def verify_v45(original_zip,runtime_zip):
    verify_v44(original_zip,runtime_zip)
    elf=collect(original_zip,runtime_zip)['node_lethe.so']

    # v44 stored the configured wrapper's BT::Tree root word in route+0xf48.
    require(elf.word(0x3552d8)==0xf907a401,'retained wrapper root store differs')

    # At dtor entry, x21 contains `this`; conditional cleanup halts the tree root.
    require(elf.symbol(b'_ZN4ancp12AvaNodeRouteD2Ev')==0x323c70,
            'AvaNodeRoute destructor symbol differs')
    for a,w in {
        0x323c8c:0xaa0003f5, # mov x21,x0 (`this`)
        0x325cb4:0xf947a6a0, # ldr x0,[x21,#0xf48]
        0x325cb8:0xb4000040, # cbz x0,skip halt
        0x325cc0:0xf947aab3, # ldr x19,[x21,#0xf50]
    }.items():elf.ins(a,w)
    elf.call(0x325cbc,0x27da20) # BT::haltAllActions@plt
    print('PASS retained RobotNode-wrapper root is checked and passed to BT::haltAllActions in route destructor')

    # An exact dynamic relocation ties the *AvaNodeRoute* virtual slot to a base no-op.
    address=elf.symbol(b'_ZTVN4ancp12AvaNodeRouteE')
    require(address==0xb60d58,'AvaNodeRoute vtable symbol moved')
    callback=elf.symbol(b'_ZN4ancp16AvaNodeRouteBase16ProcessEveryTickEv')
    require(callback==0x376d20,'ProcessEveryTick symbol moved')
    require(elf.word(callback)==0xd65f03c0,'ProcessEveryTick is no longer a one-instruction ret')
    raw=elf.secbytes(elf.section('.rela.dyn'))
    matches=[]
    for i in range(0,len(raw),24):
        off,info,addend=struct.unpack_from('<QQq',raw,i)
        if off==address+0x30:matches.append((info&0xffffffff,info>>32,addend))
    require(len(matches)==1,'expected one ProcessEveryTick vtable relocation')
    rtype,index,addend=matches[0]
    require(rtype==257 and addend==0,'unexpected AArch64 vtable relocation type/addend')
    dyn=elf.secbytes(elf.section('.dynsym'))
    strings=elf.secbytes(elf.sec[elf.section('.dynsym')['link']])
    nameoff,_,_,_,target,sz=struct.unpack_from('<IBBHQQ',dyn,index*24)
    end=strings.index(b'\0',nameoff)
    require(strings[nameoff:end]==b'_ZN4ancp16AvaNodeRouteBase16ProcessEveryTickEv'
            and target==callback and sz==4,
            'effective vtable slot is not inherited 4-byte ProcessEveryTick')
    print('PASS AvaNodeRoute vtable ProcessEveryTick slot (+0x20 from address point) resolves to inherited RET stub')

    # Related periodic update path, without interpreting this as evidence of tree tick.
    require(elf.symbol(b'_ZN4ancp12AvaNodeRoute12UpdateOutputEv')==0x3daf20,
            'UpdateOutput symbol moved')
    elf.ins(0x3daf34,0xaa0003f3)  # save this
    elf.ins(0x3daf64,0xaa1303e0)  # restore this for planning update
    elf.call(0x3daf68,0x2797c0) # PlanningFuncInUpdateOutput@plt
    elf.ins(0x3dafd4,0xf9401a62) # ldr x2,[x19,#0x30] Blackboard
    # The called planning routine has a bounded symbol extent and no BLR
    # (generic virtual tick) or directly encoded root +0xf48 load there.
    # This is a negative finding only within this one function.
    require(elf.symbol(b'_ZN4ancp12AvaNodeRoute26PlanningFuncInUpdateOutputEv')==0x3d3f90,
            'PlanningFuncInUpdateOutput symbol moved')
    dyn=elf.secbytes(elf.section('.dynsym'))
    found=[]
    for j in range(0,len(dyn),24):
        _,_,_,_,va,size=struct.unpack_from('<IBBHQQ',dyn,j)
        if va==0x3d3f90 and size:found.append(size)
    require(980 in found,'PlanningFuncInUpdateOutput bounded length differs')
    words=[elf.word(a) for a in range(0x3d3f90,0x3d3f90+980,4)]
    require(not any(w&0xfffffc1f==0xd63f0000 for w in words),
            'indirect BLR newly present inside planning routine')
    require(not any((w&0xffc00000)==0xf9400000 and ((w>>10)&4095)*8==0xf48
                    for w in words),'direct +0xf48 root load newly present in planning routine')
    print('PASS UpdateOutput calls PlanningFuncInUpdateOutput and accesses route+0x30 Blackboard')
    print('PASS bounded PlanningFuncInUpdateOutput body has no BLR or direct +0xf48 root load')
    print('X40_V45_TREE_LIFECYCLE_TICK_BOUNDARY_STATIC_PASS')
    print('LIMITS: retained root cleanup is not a runtime tick; inherited no-op is not proof')
    print('of absent tree ticks through other routines/schedulers. Physical rewash unproven.')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original_zip');ap.add_argument('runtime_zip')
    ns=ap.parse_args()
    try:verify_v45(ns.original_zip,ns.runtime_zip)
    except Exception as e:
        print('X40_V45_STATIC_FAIL: '+str(e),file=sys.stderr)
        sys.exit(1)