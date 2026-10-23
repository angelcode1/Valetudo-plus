#!/usr/bin/env python3
"""v41: offline R2416 Start_Map_Load keyflow and charger predicate audit.

Depends on adjacent v36-v40 scripts packaged in v41 ZIP.
Does not execute vendor code, contact robot, or write firmware.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v40_init_branch_verify import verify_v40

REFS={
'node_lethe.so': (
 0x440d9c,0x447e20,0x6c845c,0x6d3f58,0x6d4ce0,0x6d7bc4,
 0x6d80a8,0x72ece8,0x744bbc,0x744de0,0x842ad4,0x842f34),
'liblethe_tactics_tree.so':(0x270fc4,0x2ba5b4,0x2e6bcc),
}
LOCATIONS={'node_lethe.so':0x9f7c88,'liblethe_tactics_tree.so':0x343650}
# Directly observed typed Blackboard::set<bool> destinations in node_lethe
NODE_SETS={
 0x6c8484:0x2795c0,0x6d3f80:0x2795c0,0x6d4d08:0x2795c0,
 0x6d7bec:0x2795c0,0x6d80d0:0x2795c0,0x72ed10:0x2795c0,
 0x744be4:0x2795c0,0x744e08:0x2795c0,0x842afc:0x2795c0,
}
TACTICS_SETS={0x270ff0:0xc79b0,0x2ba5dc:0xc79b0,0x2e6bf4:0xc79b0}

def check_refs(e,target,expected):
    found=e.adrp_add_references(target,max_gap=4)
    places=tuple(a for a,b in found)
    require(places==expected, f'key ADRP+ADD references changed: {places!r}')
    require(all(b==a+4 for a,b in found),'nonadjacent ADRP+ADD')
    return places

def verify_v41(reference,runtime):
    verify_v40(reference,runtime)
    all_elf=collect(reference,runtime)
    for name, sites in REFS.items():
        elf=all_elf[name];addr=LOCATIONS[name]
        require(elf.va(addr,len(b'Start_Map_Load')+1)==b'Start_Map_Load\x00',f'{name}: key differs')
        found=check_refs(elf,addr,sites)
        print(f'PASS {name}: exact Start_Map_Load literal; {len(found)} adjacent direct ADRP+ADD sites')
    node=all_elf['node_lethe.so'];tactics=all_elf['liblethe_tactics_tree.so']
    for site,target in NODE_SETS.items(): node.call(site,target)
    for site,target in TACTICS_SETS.items(): tactics.call(site,target)
    node.call(0x842f58,0x279900) # bool get
    # One direct virtual Blackboard contains call in MT_ChangeMap
    node.ins(0x440de0,0xf9401442) # vtable contains +0x28
    node.ins(0x440de4,0xd63f0040) # BLR x2
    print('PASS 9 node_lethe and 3 tactics typed set<bool> callsites; 1 node_lethe get<bool> callsite')
    print('PASS MT_ChangeMap contains-slot (+0x28) load and indirect dispatch')
    # RobotmodeInit's condition implementation: look up AvaSensorsMsg*,
    # return failure when missing and on the other arm check a byte.
    cond=b'_ZN17RobotSignalDetect19DoesRobotGetChargerERN2BT8TreeNodeE'
    require(tactics.symbol(cond)==0x11fff0,'charger condition symbol changed')
    tactics.call(0x120054,0xc9370) # get<AvaSensorsMsg*>
    for site,word in {
        0x120078:0x52800074, # mov w20,#3 (failure on absent lookup)
        0x12007c:0x34000155, # cbz w21 to failure path
        0x12008c:0x39416000, # ldrb w0,[x0,#0x58]
        0x120090:0x7100001f, # cmp w0,#0
        0x120094:0x1a9f17f4, # cset w20,eq
        0x120098:0x11000a94, # add w20,w20,#2
    }.items(): tactics.ins(site,word)
    print('PASS DoesRobotGetCharger: sensor-pointer lookup, absent-lookup status 3, byte+0x58 comparison and 2/3 status construction')
    print('X40_V41_MAPLOAD_CHARGER_STATIC_PASS')
    print('BOUNDARY: paths are compiled, not observed; no demonstrated producer timing, shared instance, R2416 special-push eligibility or extra dock wash')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify_v41(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V41_STATIC_FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)