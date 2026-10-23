#!/usr/bin/env python3
"""Offline-only, SHA-pinned X40 R2416 v47 odometry tree-tick branch audit.

Usage: python3 x40_r2416_v47_odometry_guard_paths_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Place next to v36-v46 verifiers from the v46 audit package.
Never connects to a device, executes firmware, or writes device state.
"""
import argparse
from collections import deque
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import collect, require
from x40_r2416_v46_odom_tree_tick_verify import verify_v46, relocation

START = 0x3e02c0
END = 0x3e5530
TICK = 0x3e1390


def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def succ(addr, w):
    """Conservative intraprocedural AArch64 direct-control-flow graph.

    All calls other than a specifically verified noreturn throw are assumed
    to return; no register/flag feasibility or indirect branch modeling.
    """
    if addr == 0x3e443c:  # BL __throw_bad_function_call@plt, verified below
        return []
    if (w & 0xfc000000) == 0x14000000:  # B imm26
        return [addr + signed(w & 0x03ffffff, 26) * 4]
    if (w & 0xff000010) == 0x54000000:  # B.cond imm19
        return [addr + 4, addr + signed((w >> 5) & 0x7ffff, 19) * 4]
    if (w & 0x7e000000) == 0x34000000:  # CBZ/CBNZ imm19
        return [addr + 4, addr + signed((w >> 5) & 0x7ffff, 19) * 4]
    if (w & 0x7e000000) == 0x36000000:  # TBZ/TBNZ imm14
        return [addr + 4, addr + signed((w >> 5) & 0x3fff, 14) * 4]
    if (w & 0xfffffc1f) in (0xd65f0000, 0xd61f0000):  # RET or BR
        return []
    return [addr + 4]


def graph_reaches(elf, start, target):
    seen = {start}
    q = deque([start])
    while q:
        a = q.popleft()
        if a == target:
            return True
        for dst in succ(a, elf.word(a)):
            if START <= dst < END and (dst % 4) == 0 and dst not in seen:
                seen.add(dst)
                q.append(dst)
    return False


def branch(elf, address, word, jump):
    elf.ins(address, word)
    paths = succ(address, word)
    require(paths == [address + 4, jump],
            f'branch at {address:#x} unexpectedly goes {paths}')


def verify_v47(reference, runtime):
    verify_v46(reference, runtime)
    elfs = collect(reference, runtime)
    n = elfs['node_lethe.so']
    require(n.symbol(b'_ZN4ancp12AvaNodeRoute14OdomProcessSUBEP11OdometryMsg') == START,
            'worker start changed')
    for address, word in {
        0x3e1234: 0xb0003ce0,  # adrp x0, GOT page
        0x3e1238: 0xf9411c00,  # ldr x0, [x0, #0x238]
        0x3e123c: 0x39400000,  # ldrb w0, [x0]
        0x3e3210: 0x395b8001,  # ldrb w1, [x0,#0x6e0]
        0x3e3214: 0x35ff01e1,  # cbnz w1, rejoin
        0x3e12bc: 0x90003cd8,  # adrp x24, guard GOT
        0x3e12c0: 0xf9465b18,  # ldr x24, [x24, #0xcb0]
        0x3e12c4: 0x08dfff00,  # ldarb w0,[x24]
        0x3e303c: 0xaa1803e0,  # mov x0,x24
        0x3e3040: 0x97fa47ec,  # __cxa_guard_acquire
        0x3e3044: 0x34ff1440,  # cbz w0 -> rejoin
        0x3e306c: 0xaa1803e0,  # mov x0,x24
        0x3e3070: 0x97fa4f64,  # __cxa_guard_release
        0x3e3074: 0x17fff896,  # b rejoin
        0x3e1360: 0xf944ef03,  # ldr x3, [x24,#0x9d8]
        0x3e1368: 0xf9400060,  # ldr x0, [x3]
        0x3e136c: 0x39006022,  # strb w2,[x1,#0x18]
        0x3e1374: 0xf9400c01,  # ldr x1,[x0,#0x18]
        0x3e137c: 0xf9401a82,  # ldr x2,[x20,#0x30]
        0x3e1384: 0xf9400c03,  # ldr x3,[x0,#0x18]
        0x3e1388: 0xaa1703e1,  # mov x1,x23
        0x3e138c: 0xd63f0060,  # blr x3
        0x3e3650: 0x90003ca0,  # singleton lazy initialization
        0x3e36cc: 0x17fff72a,  # b 0x3e1374
        0x3e443c: 0x97fa62b9,  # BL __throw_bad_function_call
        0x3e1390: 0xf947a680,  # retained root load
        0x3e139c: 0xd63f0020,  # virtual executeTick dispatch
    }.items():
        n.ins(address, word)
    branch(n, 0x3e1240, 0x3500fe60, 0x3e320c)
    branch(n, 0x3e12c8, 0x3600eba0, 0x3e303c)
    branch(n, 0x3e1370, 0xb4011700, 0x3e3650)
    branch(n, 0x3e1380, 0xb40185e1, 0x3e443c)
    n.call(0x3e443c, 0x27cf20)  # C++ std::__throw_bad_function_call
    require(relocation(n, 0xb7e238,
                       b'_ZN6dreame5route31SuspendableRegister_suspend_allE',
                       1025, 0xb836d8) == 1, 'suspend_all symbol mismatch')
    require(relocation(n, 0xb79cb0,
                       b'_ZGVZN13basic_actions10StateStackB5cxx11EvE3ins',
                       1025, 0xb85688) == 8, 'StateStack lazy guard mismatch')
    require(relocation(n, 0xb7c9d8,
                       b'_ZZN11route_nodes10GlobalHook8InstanceEbE8instance',
                       1025, 0xb85620) == 8, 'GlobalHook singleton mismatch')
    print('PASS three named GOT relocation identities: suspend_all, StateStack guard, GlobalHook instance')
    for branch_addr in (0x3e1240, 0x3e12c8, 0x3e1370):
        e = succ(branch_addr, n.word(branch_addr))
        reach = tuple(graph_reaches(n, dst, TICK) for dst in e)
        require(reach == (True, True),
                f'guard at {branch_addr:#x}: one syntactic arm cannot reach tick: {reach}')
        print(f'PASS branch at {branch_addr:#x}: both successor arms have intra-worker route to executeTick')
    e = succ(0x3e1380, n.word(0x3e1380))
    require(tuple(graph_reaches(n,dst,TICK) for dst in e) == (True,False),
            'function-call target-null branch no longer terminates in throw')
    print('PASS 0x3e1380: nonnull callback route reaches tick; null callback enters noreturn bad_function_call')
    require(graph_reaches(n,0x3e303c,0x3e12cc), 'StateStack guard fails to return to common path')
    require(graph_reaches(n,0x3e3650,0x3e1374), 'GlobalHook lazy-init fails to return to common path')
    print('X40_V47_ODOMETRY_TICK_BRANCH_REJOIN_STATIC_PASS')
    print('LIMITS: CFG reachability ignores feasibility, exception side effects, scheduling, and runtime state;')
    print('        no observed tick, special_push_clean_dish producer on R2416, or dock rewash actuation.')


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original_zip')
    ap.add_argument('runtime_zip')
    args=ap.parse_args()
    try:verify_v47(args.original_zip, args.runtime_zip)
    except Exception as e:
        print('X40_V47_STATIC_FAIL:',str(e),file=sys.stderr)
        sys.exit(1)