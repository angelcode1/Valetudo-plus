#!/usr/bin/env python3
"""R2416 v39: SHA-pinned offline SubTree decorator callback and child wiring audit.

Run with X40-Firmware-Reference.zip and X40-R2416-v27.zip. Never
executes vendor code, accesses devices or sends network requests.
Requires adjacent v36/v37/v38 offline verifiers (included in v39 package).
"""
import argparse
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v38_subtree_instance_verify import verify_v38


def reloc_info(elf, address):
    """Resolve GOT relocation to its named, defined dynsym (no binary execution)."""
    rels = elf.secbytes(elf.section('.rela.dyn'))
    symtab = elf.section('.dynsym')
    syms = elf.secbytes(symtab)
    strs = elf.secbytes(elf.sec[symtab['link']])
    out = []
    for pos in range(0, len(rels), 24):
        off, rinfo, addend = struct.unpack_from('<QQq', rels, pos)
        if off != address: continue
        idx = rinfo >> 32
        kind = rinfo & 0xffffffff
        nameoff, _, _, _, value, _ = struct.unpack_from('<IBBHQQ', syms, idx * 24)
        name = strs[nameoff:strs.index(b'\0', nameoff)].decode('ascii')
        out.append((kind, value, addend, name))
    require(len(out) == 1, f'expected one relocation at {address:#x}')
    return out[0]


def verify_v39(original, runtime):
    verify_v38(original, runtime)
    e = collect(original, runtime)
    b = e['libbehaviortree_cpp.so']
    t = e['liblethe_tree.so']
    # Factory registration: "SubTree" is a DecoratorSubtreeNode builder,
    # not a dynamic lookup by the instance-name strings MapLoad etc.
    require(b.va(0xa9ae8, 8) == b'SubTree\0', 'SubTree registration literal changed')
    require((0x62c0c, 0x62c10) in b.adrp_add_references(0xa9ae8),
            'SubTree registration literal cross-reference changed')
    b.call(0x62c74, 0x3a8c0)
    m = reloc_info(b, 0xd8a90)
    f = reloc_info(b, 0xd8ae8)
    require(m[:3] == (1025, 0x64790, 0) and 'DecoratorSubtreeNode' in m[3] and '_M_manager' in m[3],
            'SubTree builder manager relocation no longer maps to decorator')
    require(f[:3] == (1025, 0x64890, 0) and 'DecoratorSubtreeNode' in f[3] and '_M_invoke' in f[3],
            'SubTree builder invoke relocation no longer maps to decorator')
    # Constructor of the factory's decorated SubTree wrapper.
    b.call(0x648b4, 0x394b0)  # DecoratorSubtreeNode::DecoratorSubtreeNode PLT
    require(b.symbol(b'_ZN2BT20DecoratorSubtreeNode4tickEv') == 0x8f430,
            'DecoratorSubtreeNode::tick address changed')
    for addr, word in {
        0x8f430: 0x39406401, # ldrb w1,[x0,#0x19]
        0x8f434: 0x35000061, # cbnz w1, +0xc
        0x8f438: 0x52800021, # mov w1,#1
        0x8f43c: 0x39006401, # strb w1,[x0,#0x19]
        0x8f440: 0xf9401000, # ldr x0,[x0,#0x20] child
        0x8f444: 0xf9400001, # ldr x1,[x0] child vptr
        0x8f448: 0xf9400c21, # ldr x1,[x1,#0x18]
        0x8f44c: 0xaa0103f0, # mov x16,x1
        0x8f450: 0xd61f0200, # br x16 ; tail dispatch, no status conversion
    }.items(): b.ins(addr, word)
    require(b.symbol(b'_ZNK2BT13DecoratorNode5childEv') == 0x4e090,
            'DecoratorNode::child accessor changed')
    b.ins(0x4e090, 0xf9401000)  # child pointer at +0x20

    # The four RobotNode SubTree wrappers all have native child-building paths.
    chains = (
        ('MapLoad', 0x30db18, 0x30db24, 0x30db28, 0x30db2c, 0x2eeaf8,
         0x2eeb20, 0x2eeb38, 0x2eeb44),
        ('RobotSysInit', 0x30db54, 0x30db60, 0x30db64, None, None,
         0x30db68, 0x30db80, 0x30db8c),
        ('StationSysInit', 0x30ded8, 0x30e03c, 0x30e040, 0x30e044, 0x2ccaf4,
         0x2ccb10, 0x2ccb30, 0x2ccb3c),
        ('RobotmodeInit', 0x30e06c, 0x30e078, 0x30e07c, 0x30e080, 0x2c7694,
         0x2c76a8, 0x2c76c8, 0x2c76d4),
    )
    for name, construct, attach, push, helper_call, helper_entry, inc, child_construct, child_attach in chains:
        t.call(construct, 0x1c6620)
        t.call(attach, 0x1c6900)
        t.call(push, 0x1c6640)
        if helper_call is not None:
            t.call(helper_call, helper_entry)
        t.call(inc, 0x1c6730)
        t.call(child_construct, 0x1c6620)
        t.call(child_attach, 0x1c6800)
        print(f'PASS {name}: SubTree wrapper -> generated direct child via decorator_parent_setChild')

    # First children: three init wrappers select SequenceStarRoF, while
    # RobotmodeInit selects IfThenElseStarRoF. These names describe compiled
    # node construction, not observed execution or successful initialization.
    expected_names = {
        0x5692df: 'SequenceStar',
        0x5692ec: 'SequenceStarRoF',
        0x5692be: 'IfThenElseStar',
        0x5692cd: 'IfThenElseStarRoF',
    }
    for addr, name in expected_names.items():
        require(t.va(addr, len(name)+1) == name.encode()+b'\0',
                f'generated first-child literal changed: {name}')
    for addr, word in {
        0x2eeb28: 0x910b7f21, 0x2eeb2c: 0x910bb300,   # MapLoad first child
        0x30db74: 0x910b7f41, 0x30db78: 0x910bb2a0,   # RobotSysInit first child
        0x2ccb18: 0x910b7c21, 0x2ccb20: 0x910bb000,   # StationSysInit first child
        0x2c76b0: 0x910af821, 0x2c76b8: 0x910b3400,   # RobotmodeInit first child
    }.items(): t.ins(addr, word)
    print('PASS SubTree registration invokes DecoratorSubtreeNode builder via independently resolved relocation entries')
    print('PASS DecoratorSubtreeNode::tick only forwards to its child virtual method after RUNNING-state bookkeeping')
    print('PASS first-child constructor literals: SequenceStarRoF for three init wrappers, IfThenElseStarRoF for RobotmodeInit')
    print('X40_V39_SUBTREE_DECORATOR_STATIC_PASS')
    print('BOUNDARY: no compiled first-child status is a measured R2416 tick result;')
    print('          special_push_clean_dish and physical automatic rewash remain unproven.')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip'); p.add_argument('runtime_zip')
    args=p.parse_args()
    try: verify_v39(args.original_zip, args.runtime_zip)
    except Exception as exc:
        print('X40_V39_STATIC_FAIL: '+str(exc), file=sys.stderr)
        raise SystemExit(1)