#!/usr/bin/env python3
"""v50 R2416 offline audit: GlobalDispatcher listener iteration and StopPauser gate.

Only reads two operator-supplied ZIPs as inert data. Standard library only.
Run next to x40_r2416_v48_globalhook_callback_verify.py and
x40_r2416_v49_globalhook_assignment_verify.py.
"""
import argparse
import struct
import sys
from x40_r2416_v49_globalhook_assignment_verify import verify as verify_v49
from x40_r2416_v48_globalhook_callback_verify import original_and_runtime, check


def imm19_target(elf, at):
    """Decode imm19 for AArch64 conditional branches or compare-and-branch."""
    instruction = elf.word(at)
    # Accept only B.cond, CBZ or CBNZ (32/64-bit variants).
    is_bcond = instruction & 0xff000010 == 0x54000000
    is_cb = instruction & 0x7e000000 == 0x34000000
    check(is_bcond or is_cb, f'no conditional branch at {at:#x}')
    imm19 = (instruction >> 5) & 0x7ffff
    if imm19 & 0x40000:
        imm19 -= 0x80000
    return at + imm19 * 4


def verify(original_zip, runtime_zip):
    verify_v49(original_zip, runtime_zip)  # authentic ELFs + earlier checks
    route = original_and_runtime(original_zip, runtime_zip)['liblethe_route_nodes.so']
    name = b'_ZN17global_dispatcher16GlobalDispatcher8dispatchERSt10shared_ptrIN2BT10BlackboardEEm'
    check(route.symbol(name) == (0xcf4220, 592), 'dispatcher symbol size or address changed')
    check(route.symbol(b'_ZN17global_dispatcher16GlobalDispatcherC2Ev')[0] == 0xcf4e90,
          'dispatcher constructor address changed')

    expected = {
        # Dispatcher initializes std::map-like listener registry to empty.
        0xcf4eb4:0x91018000,  # add x0,x0,#0x60  (verify via actual instruction)
        0xcf4ef8:0xb900605f,  # str wzr,[x2,#0x60]
        0xcf4efc:0xa900801f,
        # Obtain StopPauser SM, initialize/wait if missing, then call update.
        0xcf42a4:0xf94002a0,
        0xcf42a8:0xb4000480,
        0xcf42b4:0x97dd4f0b,
        0xcf42bc:0xf9400260,
        0xcf42c0:0xb4000860,
        0xcf42c4:0x39406000,
        0xcf42c8:0x35000220,
        # Listener iteration: RB tree root and end sentinel, std::function call.
        0xcf42cc:0xf9403a93,
        0xcf42d0:0x91018294,
        0xcf42d8:0x540001a0,
        0xcf42e0:0xf9402a62,
        0xcf42e8:0xb4000c02,
        0xcf42ec:0xf9400c02,
        0xcf42f4:0xd63f0040,
        0xcf42fc:0x97dd6405,
        0xcf4308:0x54fffec1,
        # Retry wait for missing state-machine instance, then resume update.
        0xcf43a0:0x52800020,
        0xcf43a4:0x97dd749f,
        0xcf43a8:0xf94002a0,
        0xcf43ac:0xb4ffffa0,
        0xcf43bc:0x97dd4ec9,
        0xcf43c8:0xb5fff7e0,
        # Pauser can reset +0x18; test of that same state byte later.
        0xd0d680:0x3900607f,
        0xd0d6ec:0x39406020,
        0xd0d6f4:0x340000a0,
    }
    for addr,word in expected.items():route.instruction(addr,word)
    check(imm19_target(route,0xcf42a8)==0xcf4338, 'missing singleton detour changed')
    check(imm19_target(route,0xcf42c8)==0xcf430c, 'listener bypass target changed')
    check(imm19_target(route,0xcf42d8)==0xcf430c, 'empty listener map skip changed')
    check(imm19_target(route,0xcf4308)==0xcf42e0, 'listener iteration loop changed')
    check(imm19_target(route,0xcf43ac)==0xcf43a0, 'singleton wait loop changed')
    check(imm19_target(route,0xcf43c8)==0xcf42c4, 'initialized singleton rejoin changed')
    check(imm19_target(route,0xd0d6f4)==0xd0d708, 'StopPauser state branch changed')
    route.call(0xcf42b4,0x447ee0)   # StopPauser::update plt
    route.call(0xcf43bc,0x447ee0)   # StopPauser::update plt after wait
    route.call(0xcf42fc,0x44d310)   # RB tree increment plt
    route.call(0xcf43a4,0x451620)   # usleep plt

    # Preserve independently visible and intentionally narrow literal finding.
    # Full ELF bytes (not the dynamic string table alone) are checked here.
    for key in (b'special_push_clean_dish',b'r2343_start_rewash',b'TurbidityResultFail'):
        check(route.blob.count(key)==0, f'new direct literal in route library: {key!r}')

    print('PASS dispatcher status-byte branch bypasses the listener loop, not the later root tick')
    print('PASS nonempty listener map iterates registered std::function callbacks through BLR')
    print('PASS null-SM detour can poll with usleep() until singleton appears')
    print('PASS StopPauser::update writes and reads its +0x18 state byte')
    print('PASS no direct literal for three rewash-related keys in route-node ELF')
    print('X40_V50_DISPATCHER_LISTENER_GATE_STATIC_PASS')
    print('LIMITS: live listener registrations, dispatch exit, callback side effects,')
    print('  Blackboard aliasing, R2416 special_push_clean_dish producer and physical rewash unproven')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V50_STATIC_FAIL:',exc,file=sys.stderr)
        sys.exit(1)