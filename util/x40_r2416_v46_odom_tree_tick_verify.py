#!/usr/bin/env python3
"""Read-only SHA-pinned offline R2416 v46 odometry-to-tree executeTick audit.

Run alongside the v36-v45 verifiers:
  python3 x40_r2416_v46_odom_tree_tick_verify.py ORIGINAL_ZIP RUNTIME_ZIP

Performs no execution of device ELF code; no robot, network, or state changes.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v45_tree_lifecycle_verify import verify_v45


def relocation(elf, slot, symbol_name, expected_type, expected_value):
    matches = []
    symsec = elf.section('.dynsym')
    symblob = elf.secbytes(symsec)
    names = elf.secbytes(elf.sec[symsec['link']])
    raw = elf.secbytes(elf.section('.rela.dyn'))
    for i in range(0, len(raw), 24):
        offset, info, addend = struct.unpack_from('<QQq', raw, i)
        if offset != slot:
            continue
        index, typ = info >> 32, info & 0xffffffff
        require(index * 24 + 24 <= len(symblob), 'symbol index outside dynsym')
        stridx, _, _, _, address, size = struct.unpack_from('<IBBHQQ', symblob, index * 24)
        require(stridx < len(names), 'symbol name offset out of bounds')
        end = names.find(b'\0', stridx)
        require(end >= 0, 'unterminated ELF symbol name')
        matches.append((typ, names[stridx:end], address, size, addend))
    require(len(matches) == 1, f'expected exactly one relocation at {slot:#x}, got {len(matches)}')
    typ, name, address, size, addend = matches[0]
    require(typ == expected_type and name == symbol_name and address == expected_value and addend == 0,
            f'unexpected relocation at {slot:#x}: {matches[0]}')
    return size


def verify_v46(reference, runtime):
    verify_v45(reference, runtime)
    files = collect(reference, runtime)
    n = files['node_lethe.so']
    bt = files['libbehaviortree_cpp.so']

    require(n.symbol(b'_ZN4ancp12AvaNodeRoute11OdomProcessEP11OdometryMsg') == 0x3cff50,
            'Odometry callback entry differs')
    require(n.symbol(b'_ZN4ancp12AvaNodeRoute14OdomProcessSUBEP11OdometryMsg') == 0x3e02c0,
            'Odometry worker entry differs')
    # OdomProcess binds a pointer to OdomProcessSUB via the GOT and submits
    # the binder into an AsyncDeque OdometryMsg subscription; does not prove
    # runtime messages are received.
    n.ins(0x3cff88, 0x90003d64)  # adrp x4, page of GOT
    n.ins(0x3cff98, 0xf9438884)  # ldr x4, [x4, #0x710]
    require(relocation(n, 0xb7b710,
                       b'_ZN4ancp12AvaNodeRoute14OdomProcessSUBEP11OdometryMsg',
                       1025, 0x3e02c0) >= 0,
            'OdomProcessSUB relocation invalid')
    n.call(0x3cffe8, 0x27c740)  # MultAsyncSubscribe<OdometryMsg...>@plt
    print('PASS OdomProcess binds OdomProcessSUB and calls MultAsyncSubscribe<OdometryMsg>')

    # x20 saves this at worker entry; on the compiled reachable path after
    # preceding status/data guards, root+0xf48 is loaded and virtual slot used.
    n.ins(0x3e02d8, 0xaa0003f4)  # mov x20, x0
    for addr, instruction in {
        0x3e1390: 0xf947a680,  # ldr x0, [x20, #0xf48]
        0x3e1394: 0xf9400001,  # ldr x1, [x0]
        0x3e1398: 0xf9400c21,  # ldr x1, [x1, #0x18]
        0x3e139c: 0xd63f0020,  # blr x1
        0x3e13a0: 0x12001c19,  # and w25, w0, #0xff
    }.items():
        n.ins(addr, instruction)
    require(n.word(0x3e12c8) & 0x7f000000 == 0x36000000,
            'expected conditional TBZ/TBNZ upstream of tick region')
    print('PASS OdomProcessSUB dispatches root+0xf48 vtable slot +0x18 and captures status')

    # Match actual class implementation of the configured XML wrapper type.
    # Standard Itanium layout: vtable symbol +0x10 is the address point;
    # +0x18 from that address point is the executeTick virtual entry.
    vtable = bt.symbol(b'_ZTVN2BT20SubtreeConditionNodeE')
    require(vtable == 0xd65d0, 'SubtreeConditionNode vtable moved')
    ap = vtable + 0x10
    length = relocation(bt, ap + 0x18,
                        b'_ZN2BT20SubtreeConditionNode11executeTickEv',
                        257, 0x74a80)
    require(length == 60, 'SubtreeConditionNode executeTick implementation size changed')
    print('PASS SubtreeConditionNode vtable +0x18 resolves to executeTick (60-byte implementation)')

    print('X40_V46_ODOMETRY_ROOT_EXECUTETICK_STATIC_PASS')
    print('LIMITS: compiled dispatch is not observed runtime tick frequency or successful odometry delivery;')
    print('        StationWash eligibility, rewash-marker causality and physical dock-wash restart are unproven.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_zip')
    parser.add_argument('runtime_zip')
    args = parser.parse_args()
    try:
        verify_v46(args.original_zip, args.runtime_zip)
    except Exception as e:
        print(f'X40_V46_STATIC_FAIL: {e}', file=sys.stderr)
        sys.exit(1)