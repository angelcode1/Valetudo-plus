#!/usr/bin/env python3
"""Offline X40 R2416 v36 pre-Loop census using the repository's pinned v32 ELF loader."""
import argparse
import struct
import sys
import x40_r2416_v32_local_parent_verify as old

# root attachment VA, factory call VA, type, instance, parameter table,
# ADRP instruction address, tuple of exact constant-string parameters
ROWS = (
 (0x30d940,0x30d934,'LDS_Switch','LDS_Switch',0x6e3a90,0x30d918,(('state','false'),)),
 (0x30d978,0x30d96c,'EraseBlackboard','EraseBlackboard',0x6e5c30,0x30d950,(('key','playspeech_pause'),)),
 (0x30d9b0,0x30d9a4,'SetBlackboardWithType','SetBlackboardWithType',0x6ecd30,0x30d988,(('key','config_tick_frequency'),('type','int'),('value','25'))),
 (0x30d9e8,0x30d9dc,'SetMusicPlayPara','SetMusicPlayPara',0x6f6ef0,0x30d9c0,(('Interrupt_En','false'),('MusicNumber','0'),('MusicPlayPerSecond','10'),('MusicPlayTimes','0'),('Output','RobotMusic'))),
 (0x30da20,0x30da14,'SetBlackboard','SetBlackboard',0x6f9770,0x30d9f8,(('key','Start_Map_Load'),('value','true'))),
 (0x30da54,0x30da48,'SetBlackboard','SetBlackboard',0x6f1b90,0x30da30,(('key','robot_status'),('value','normal'))),
 (0x30da88,0x30da7c,'SetBlackboard','SetBlackboard',0x6fa530,0x30da64,(('key','robot_power_on'),('value',''))),
 (0x30dabc,0x30dab0,'SetBlackboard','SetBlackboard',0x6fb010,0x30da98,(('key','reset_wheel_before_clean'),('value','1'))),
 (0x30daec,0x30dadc,'GetSegmentMapFuncRunning','GetSegmentMapFuncRunning',None,None,()),
 (0x30db24,0x30db18,'SubTree','MapLoad',0x6eeed0,0x30dafc,(('display_name','SubTree'),)),
 (0x30db60,0x30db54,'SubTree','RobotSysInit',0x6eeed0,0x30db38,(('display_name','SubTree'),)),
 (0x30e03c,0x30ded8,'SubTree','StationSysInit',0x6eeed0,0x30debc,(('display_name','SubTree'),)),
 (0x30e078,0x30e06c,'SubTree','RobotmodeInit',0x6eeed0,0x30e050,(('display_name','SubTree'),)),
 (0x30e0b0,0x30e0a4,'SubtreeCondition','SubtreeCondition',0x6f7ff0,0x30e08c,(('expand_in_logger','true'),('subtree_file_path','AlwaysSuccess.xml'))),
 (0x30e0e4,0x30e0d8,'SubtreeCondition','SubtreeCondition',0x6e5c90,0x30e0c0,(('expand_in_logger','true'),('subtree_file_path','CountryGet.xml'))),
)
NAMES = {
 'LDS_Switch':0x578394,'EraseBlackboard':0x5ae6c2,
 'SetBlackboardWithType':0x569398,'SetMusicPlayPara':0x5699a7,
 'SetBlackboard':0x5692fc,'GetSegmentMapFuncRunning':0x585ddf,
 'SubTree':0x58fcdc,'MapLoad':0x585df8,'RobotSysInit':0x585e00,
 'StationSysInit':0x585e79,'RobotmodeInit':0x585e88,
 'SubtreeCondition':0x56832e,
}
def name_at(elf, address):
    raw=elf.va(address,128)
    return raw[:raw.index(b'\x00')].decode('ascii')
def params(elf, address, count):
    result=[]
    for i in range(count):
        pair=[]
        for j in range(2):
            ptr,length=struct.unpack('<QQ',elf.va(address+32*i+16*j,16))
            old.require(length<=128,'ConstStr length outside bound')
            pair.append(elf.va(ptr,length).decode('ascii') if length else '')
        old.require(bool(pair[0]),'empty ConstStr key')
        result.append(tuple(pair))
    return tuple(result)
def run(firmware_zip, runtime_zip):
    old.verify_v32(firmware_zip,runtime_zip)
    elf=old.collect(firmware_zip,runtime_zip)['liblethe_tree.so']
    old.require(name_at(elf,0x5692ec)=='SequenceStarRoF','root kind differs')
    depth=[];children=[]
    for addr in range(0x30d8c0,0x30e124,4):
        w=elf.word(addr)
        if w & 0xfc000000 != 0x94000000:
            continue
        imm=w & 0x3ffffff
        if imm & (1<<25): imm-=1<<26
        target=addr+imm*4
        if target==0x1c6730:depth.append(addr)
        elif target==0x1c6810:
            old.require(bool(depth),'invalid construction depth')
            depth.pop()
        elif target==0x1c6900 and depth==[0x30d90c]:children.append(addr)
    old.require(children==[row[0] for row in ROWS]+[0x30e11c],
                'pre-Loop direct attachment sequence changed')
    for idx,(attach, factory, kind, instance, table, adrp, expected) in enumerate(ROWS,1):
        elf.call(factory,0x1c6620)
        elf.call(attach,0x1c6900)
        old.require(name_at(elf,NAMES[kind])==kind, f'type {idx} differs')
        old.require(name_at(elf,NAMES[instance])==instance, f'instance {idx} differs')
        if table is None:
            old.require(elf.word(factory-4)==0xf90047ff,'empty param vector differs')
        else:
            old.require(old.table_address(elf,adrp,adrp+4)==table,
                        f'param table {idx} changed')
            old.require(elf.word(adrp-4)==(0xd2800002 | (len(expected)<<5)),
                        f'parameter count {idx} changed')
            old.require(params(elf,table,len(expected))==expected,
                        f'parameter values {idx} changed')
        print(f'{idx:02d} {attach:#x} {kind} {instance}')
    old.require(elf.word(0x30dedc)==0x14000056,'StationSysInit branch changed')
    print('X40_V36_PRE_LOOP_DIRECT_NODES_STATIC_PASS')
    print('BOUNDARY: static construction only; not actual tick or physical rewash.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:run(a.firmware_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V36_STATIC_FAIL: '+str(exc),file=sys.stderr)
        sys.exit(1)
