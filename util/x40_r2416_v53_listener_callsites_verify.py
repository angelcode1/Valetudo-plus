#!/usr/bin/env python3
"""v53 offline audit: whole-.text direct listener insertion calls and invoker input guards.

Usage: python3 x40_r2416_v53_listener_callsites_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Requires sibling v48-v52 verifiers. No network, robot connection or write operations.
"""
import argparse
import struct
import sys
from x40_r2416_v52_dispatcher_registration_verify import verify as verify_v52, EDGE_CTORS, CTOR, MAP_OP
from x40_r2416_v48_globalhook_callback_verify import original_and_runtime, check


def calls_to(elf, section_name, target):
    sec = elf.sec(section_name)
    data = elf.secdata(sec)
    check(sec['addr'] % 4 == 0 and len(data) % 4 == 0, 'unaligned executable code')
    hits=[]
    for i in range(0,len(data),4):
        word=struct.unpack_from('<I',data,i)[0]
        if word & 0xFC000000 != 0x94000000:
            continue
        imm=word & 0x03FFFFFF
        if imm & (1 << 25): imm -= 1 << 26
        address=sec['addr']+i
        if address+4*imm == target:
            hits.append(address)
    return hits


def verify(original_zip, runtime_zip):
    verify_v52(original_zip, runtime_zip)
    elfs=original_and_runtime(original_zip,runtime_zip)
    route=elfs['liblethe_route_nodes.so']
    ctor_start,ctor_size=route.symbol(CTOR)
    expected=[entry[4] for entry in EDGE_CTORS]
    hits=calls_to(route,'.text',MAP_OP)
    check(hits==expected, f'whole-.text listener-map direct calls changed: {[hex(x) for x in hits]}')
    check(all(ctor_start <= a < ctor_start+ctor_size for a in hits), 'call site outside constructor')
    print('PASS whole .text direct BL -> std::map::operator[] census:',len(hits), 'all inside GlobalDispatcher constructor')

    # Check first stage of all seven std::function invokers rather than
    # inferring listener semantics exclusively from type names.
    for key,_,_,_,_,_,_,invoker,_ in EDGE_CTORS:
        for offset,ins in {
            0x18:0xF9400003, # ldr x3, [x0] -- captured edge detector holder
            0x34:0xF9400020, # ldr x0, [x1] -- incoming numeric odometry value
            0x3C:0xEB01001F, # cmp x0,x1 -- incoming vs stored prior value
            0x40:0x54000089, # b.ls  -- route for <= previous
            0x4C:0x54000300, # b.eq  -- unit-delta special branch
        }.items():
            route.instruction(invoker+offset,ins)
        check(route.word(invoker+0x38) in (0xF9404701,0xF94046E1),
              f'{key!r}: stored-value load changed')
        check(route.word(invoker+0x44) in (0xCB010006,0xCB010002),
              f'{key!r}: incoming-minus-stored arithmetic changed')
        check(route.word(invoker+0x48) in (0xF10004DF,0xF100045F),
              f'{key!r}: delta==1 comparison changed')
        print(f'PASS {key.decode()}: invoker={invoker:#x}, stored-value compare and unit-delta branch')

    print('X40_V53_WHOLE_TEXT_DIRECT_REGISTRATION_AND_EDGE_GUARDS_STATIC_PASS')
    print('LIMIT: direct BL calls to one PLT map operator only, not indirect insertions,')
    print('      other mutation APIs/modules or live callback/event behaviour. No physical rewash proven.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    args=p.parse_args()
    try:verify(args.original_zip,args.runtime_zip)
    except Exception as e:
        print('X40_V53_STATIC_FAIL:',e,file=sys.stderr)
        sys.exit(1)