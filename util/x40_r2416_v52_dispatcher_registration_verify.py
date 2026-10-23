#!/usr/bin/env python3
"""v52: Offline SHA-pinned R2416 GlobalDispatcher constructor listener census.

Usage: python3 x40_r2416_v52_dispatcher_registration_verify.py ORIGINAL_ZIP RUNTIME_ZIP

Requires sibling v48-v51 verification scripts (all standard library). Reads
ELF bytes only; never communicates with or modifies the vacuum.
"""
import argparse
import sys
from x40_r2416_v51_dispatcher_callback_abi_verify import verify as verify_v51
from x40_r2416_v48_globalhook_callback_verify import original_and_runtime, check

CTOR=b'_ZN17global_dispatcher16GlobalDispatcherC2Ev'
MAP_OP=0x44f640  # std::map<string,std::function<void(unsigned long const&)>>::operator[]@plt
EDGE_CTORS=[
    (b'awesome_search',       0xfd65d0,0xcf5228,0x4427b0,0xcf5324,0xcf535c,0xcf3a20,0xcf2310,0xcf5368),
    (b'follow_wall',          0xfcde40,0xcf542c,0x44c770,0xcf5500,0xcf5538,0xcf3920,0xcf2820,0xcf5544),
    (b'follow_with_chain',    0xfde090,0xcf5604,0x43df80,0xcf56d8,0xcf5710,0xcf3820,0xcf0d00,0xcf571c),
    (b'carpet_follow',        0x101a0b0,0xcf5824,0x443d60,0xcf58fc,0xcf5934,0xcf3720,0xcf1e70,None),
    (b'maybe_carpet_follow',  0xf9c870,0xcf5a04,0x44d360,0xcf5adc,0xcf5b14,0xcf3620,0xcf19e0,None),
    (b'carpet_back_done',     0x101a0c0,0xcf5be4,0x44f190,0xcf5cbc,0xcf5cf4,0xcf3520,0xcf1540,None),
    (b'confirm_carpet',       0xfd9d88,0xcf5dc8,0x449810,0xcf5eac,0xcf5ee4,0xcf3420,0xcf1120,0xcf5ef0),
]

# Earlier v51 verifies that the dispatcher listener registry is the RB tree
# whose header is at +0x60 and first pointer at +0x70; the ctor's map base is
# +0x58. These are separately typed maps from the edge-detector registry at +0x28.
def verify(original_zip,runtime_zip):
    verify_v51(original_zip,runtime_zip)
    route=original_and_runtime(original_zip,runtime_zip)['liblethe_route_nodes.so']
    start,size=route.symbol(CTOR)
    check((start,size)==(0xcf4e90,6596),'GlobalDispatcher ctor changed')
    check(start<=EDGE_CTORS[0][4]<EDGE_CTORS[-1][4]<start+size,'listener sites outside ctor')
    route.instruction(0xcf4ec4,0x91016058) # add x24,x2,#0x58 (listener map base)
    route.instruction(0xcf4ef8,0xb900605f) # str wzr,[x2,#0x60] (empty listener registry)
    route.instruction(0xcf4efc,0xa900801f) # init RB sentinel
    route.instruction(0xcf4f00,0xa901fc00) # init RB links/count
    sites=[]
    for addr in range(start,start+size,4):
        ins=route.word(addr)
        if (ins&0xfc000000)!=0x94000000:continue
        imm=ins&0x3ffffff
        if imm&(1<<25):imm-=1<<26
        if addr+4*imm==MAP_OP:sites.append(addr)
    expected=[e[4] for e in EDGE_CTORS]
    check(sites==expected, f'listener-map operator[] constructor call census changed {sites!r}')

    # Each edge-detector creation is followed by a same-key callback registration
    # in map<string,std::function<void(const unsigned long&)>>. The callback's
    # staging pair contains std::function manager then invoker function pointer.
    for key,src,edgect,edgeplt,insert,stage,manager,invoker,capture in EDGE_CTORS:
        check(route.va(src,len(key))==key,f'mismatched allowlisted key {key!r}')
        route.call(edgect,edgeplt)
        route.call(insert,MAP_OP)
        route.instruction(stage,0xa91187e2) # stp x2,x1,[sp,#0x118]
        # AArch64 ADRP x1 and ADD x1,... after map insertion prepare invoker.
        # Decode the exact static immediates rather than trusting symbol labels.
        a1=route.word(stage-16); b1=route.word(stage-12)
        a2=route.word(stage-8);b2=route.word(stage-4)
        check((a1&0x9f00001f)==0x90000001 and (b1&0xffc003ff)==0x91000021,
              f'invoker address calculation invalid at {stage:#x}')
        check((a2&0x9f00001f)==0x90000002 and (b2&0xffc003ff)==0x91000042,
              f'manager address calculation invalid at {stage:#x}')
        def adr_addr(at,ad,add):
            immlo=(ad>>29)&3
            immhi=(ad>>5)&0x7ffff
            imm=(immhi<<2)|immlo
            if imm&(1<<20):imm-=1<<21
            return (at&~0xfff)+(imm<<12)+((add>>10)&0xfff)
        # x1 is invoker, x2 is manager, stored as (manager,invoker)
        check(adr_addr(stage-16,a1,b1)==invoker,f'invoker target changed for {key!r}')
        check(adr_addr(stage-8,a2,b2)==manager,f'manager target changed for {key!r}')
        if capture is not None:route.instruction(capture,0xa900581c if capture!=0xcf5ef0 else 0xa900581b)
    # The constructor registrations provide only a bounded inventory: other
    # modules or post-construction insertion may exist, and callbacks can capture
    # objects that themselves read the Blackboard indirectly.
    print('PASS full SHA-256 pins and runtime copy equality inherited from v51')
    print(f'PASS bounded ctor census exactly {len(sites)} std::map<string,function> insertion calls')
    for entry in EDGE_CTORS:
        print(f'PASS listener key={entry[0].decode()} ctor_call={entry[4]:#x} manager={entry[6]:#x} invoker={entry[7]:#x}')
    print('X40_V52_DISPATCHER_CONSTRUCTOR_LISTENERS_STATIC_PASS')
    print('LIMITS: registration execution, later insertions/removals, listener side effects,')
    print('Blackboard aliasing and R2416 automatic physical rewash are not proven.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V52_STATIC_FAIL:',exc,file=sys.stderr)
        sys.exit(1)