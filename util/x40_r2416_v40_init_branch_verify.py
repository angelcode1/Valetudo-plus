#!/usr/bin/env python3
"""Offline R2416 v40 first-branch verifier. Never executes firmware or contacts robot.

Requires adjacent v36-v39 verifier dependencies, supplied in v40 audit package.
Inputs: X40-Firmware-Reference.zip and X40-R2416-v27.zip.
"""
import argparse
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v39_subtree_decorator_verify import verify_v39


def param_pairs(tree, address, count):
    require(0 < count <= 5, 'unexpected parameter count')
    out=[]
    for i in range(count):
        entries=[]
        for j in (0,1):
            ptr,n=struct.unpack('<QQ',tree.va(address+32*i+16*j,16))
            require(0<n<=256, f'unreasonable parameter length at {address:#x}')
            txt=tree.va(ptr,n)
            require(b'\0' not in txt, 'non-string parameter value')
            entries.append(txt.decode('utf-8'))
        out.append(tuple(entries))
    return out


def check_params(tree,address, expected):
    actual=param_pairs(tree,address,len(expected))
    require(actual==expected, f'parameter table {address:#x} changed: {actual!r}')


def verify_v40(original, runtime):
    verify_v39(original,runtime)
    binaries=collect(original,runtime)
    t=binaries['liblethe_tree.so']
    b=binaries['libbehaviortree_cpp.so']

    # MapLoad: first child is a direct blackboard presence check, before
    # the diagnostic and cleanup operations. Presence != Boolean true.
    for addr,name in [(0x56932f,'BlackboardContains'),
                      (0x569342,'SaySomething'),
                      (0x5ae6c2,'EraseBlackboard'),
                      (0x5692ec,'SequenceStarRoF'),
                      (0x5692df,'SequenceStar')]:
        require(t.va(addr,len(name)+1)==name.encode()+b'\0',f'node type literal {name} changed')
    t.call(0x2eeb38,0x1c6620)
    t.call(0x2eeb44,0x1c6800)
    t.call(0x2eeb74,0x1c6620)
    t.call(0x2eeb80,0x1c6900)
    t.call(0x2eebac,0x1c6620)
    t.call(0x2eebb8,0x1c6900)
    t.call(0x2eebe4,0x1c6620)
    t.call(0x2eebf0,0x1c6900)
    check_params(t,0x6f97d0,[('key','Start_Map_Load')])
    check_params(t,0x6f97f0,[('message','MapLoad Start!'),('xml_line_num','4532'),('full_stack','RobotNode.xml,MapLoad,0 1')])
    check_params(t,0x6f9850,[('key','startup_clear_flag')])
    print('PASS MapLoad: SequenceStarRoF begins BlackboardContains(Start_Map_Load), then diagnostic and erase')

    # RobotSysInit: distinguish the diagnostic from subsequent named node.
    t.call(0x30db80,0x1c6620)
    t.call(0x30db8c,0x1c6800)
    t.call(0x30dbbc,0x1c6620)
    t.call(0x30dbc8,0x1c6900)
    t.call(0x30dbf4,0x1c6620)
    t.call(0x30dc00,0x1c6900)
    check_params(t,0x6fcd30,[('message','Robot Running'),('xml_line_num','5658'),('full_stack','RobotNode.xml,RobotSysInit,0 0')])
    for addr,name in [(0x585cdc,'setKey_LongPress_Process'),(0x585e0d,'RobotInitPara')]:
        require(t.va(addr,len(name)+1)==name.encode()+b'\0',f'RobotSysInit node literal changed: {name}')
    print('PASS RobotSysInit: leading diagnostic Robot Running, followed by setKey_LongPress_Process/RobotInitPara')

    # StationSysInit: early child writes are compiled init defaults,
    # and must not be misreported as observed runtime Blackboard state.
    t.call(0x2ccb30,0x1c6620)
    t.call(0x2ccb3c,0x1c6800)
    for pos in [0x2ccb6c,0x2ccba4,0x2ccbd8,0x2ccc0c]:
        t.call(pos,0x1c6620)
    for pos in [0x2ccb78,0x2ccbb0,0x2ccbe4,0x2ccc18]:
        t.call(pos,0x1c6900)
    check_params(t,0x6e4170,[('message','Station Sys Init'),('xml_line_num','6268'),('full_stack','RobotNode.xml,StationSysInit,0 0')])
    for address,key,val in [(0x6e42f0,'continue_work','clean_none'),
                            (0x6e43d0,'mode_dirty_record','none'),
                            (0x6e4550,'robot_in_station_flag','false')]:
        check_params(t,address,[('key',key),('value',val)])
    print('PASS StationSysInit: diagnostic then continue_work/mode_dirty_record/robot_in_station_flag defaults')

    # RobotmodeInit generated first-child IfThenElseStarRoF: three direct
    # attachments, with DoesRobotGetCharger at condition index 0.
    require(b.symbol(b'_ZN2BT21IfThenElseStarRoFNode4tickEv')==0x95520,
            'IfThenElseStarRoF tick symbol changed')
    for addr,name in [(0x569993,'DoesRobotGetCharger'),
                      (0x569378,'Sequence'),
                      (0x5692be,'IfThenElseStar'),
                      (0x5692cd,'IfThenElseStarRoF')]:
        require(t.va(addr,len(name)+1)==name.encode()+b'\0',f'RobotmodeInit node type changed: {name}')
    for pos in (0x2c76c8,0x2c76f8,0x2c7728,0x2c7844):
        t.call(pos,0x1c6620)
    t.call(0x2c76d4,0x1c6800)
    for pos in (0x2c7704,0x2c7734,0x2c7850):
        t.call(pos,0x1c6900)
    t.call(0x2c7764,0x1c6620)
    check_params(t,0x6e5950,[('key','chargemode_poweron'),('value','true')])
    # Signed dispatch from child(0) status2 -> index1, status3 -> index2,
    # running status1 returns. These are compiled transitions only.
    for addr,word in {
        0x955ac:0xf9400c21, # load child vfunc tick
        0x955b0:0xd63f0020, # BLR x1
        0x955d4:0x71000a7f, # CMP w19,#2
        0x955e0:0x340016f3, # CBZ w19 => exceptional/unrecognized
        0x95608:0x71000e7f, # CMP w19,#3
        0x95610:0xb9403a80, # current child index
        0x95620:0x52800040, # choose branch index 2
        0x95630:0xb9403a80, # current child index
        0x95640:0x52800020, # choose branch index 1
        0x95648:0xb9003a80, # store selected child index
    }.items():b.ins(addr,word)
    print('PASS RobotmodeInit: IfThenElseStarRoF begins DoesRobotGetCharger, then SequenceStarRoF / Sequence arms')
    print('PASS IfThenElseStarRoF tick: condition success/failure choose index1/index2; RUNNING remains a possible hold')
    print('PASS successful original pin checks and runtime comparisons inherited from v39')
    print('X40_V40_INITIALIZATION_BRANCHES_STATIC_PASS')
    print('BOUNDARY: no observed R2416 tick statuses, no validated R2416 special_push_clean_dish producer, no demonstrated physical rewash')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    args=p.parse_args()
    try:verify_v40(args.original_zip,args.runtime_zip)
    except Exception as exc:
        print('X40_V40_STATIC_FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)