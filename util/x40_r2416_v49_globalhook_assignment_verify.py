#!/usr/bin/env python3
"""R2416 v49: verify GlobalHook replacement and pre-tick dispatcher (offline).

Usage:
    python3 x40_r2416_v49_globalhook_assignment_verify.py ORIGINAL_ZIP RUNTIME_ZIP

Requires sibling x40_r2416_v48_globalhook_callback_verify.py. Verifies SHA-pinned
native code as inert bytes. Does NOT contact, modify or instrument the robot.
"""
import argparse
import sys
from x40_r2416_v48_globalhook_callback_verify import (
    original_and_runtime, verify as v48_verify, check,
)

HOOK = b'_ZN11route_nodes15odomProcessHookERKmRSt10shared_ptrIN2BT10BlackboardEE'
REG = b'_ZN21route_bt_nodes_plugin13RegisterNodesERN2BT19BehaviorTreeFactoryE'
DISPATCH = b'_ZN17global_dispatcher16GlobalDispatcher8dispatchERSt10shared_ptrIN2BT10BlackboardEEm'
INV = b'_ZNSt17_Function_handlerIFvRKmRSt10shared_ptrIN2BT10BlackboardEEEPS7_E9_M_invokeERKSt9_Any_dataS1_S6_'
MGR = b'_ZNSt17_Function_handlerIFvRKmRSt10shared_ptrIN2BT10BlackboardEEEPS7_E10_M_managerERSt9_Any_dataRKSA_St18_Manager_operation'


def branch_target(el, addr):
    """Decode AArch64 unconditional immediate branch, NOT arbitrary branch."""
    ins = el.word(addr)
    check((ins & 0xfc000000) == 0x14000000,
          f'not unconditional B at {addr:#x}')
    val = ins & 0x3ffffff
    if val >= 1 << 25:
        val -= 1 << 26
    return addr + (val << 2)


def verify(original_zip, runtime_zip):
    # The previously released v48 integrity, symbol and call-site checks are
    # regression dependencies. Its verification includes all five full ELF
    # pins and byte equality of the three active runtime library copies.
    v48_verify(original_zip, runtime_zip)
    elf = original_and_runtime(original_zip, runtime_zip)['liblethe_route_nodes.so']

    check(elf.symbol(REG)[0] == 0x48bad0, 'unexpected route node registration implementation')
    check(elf.symbol(HOOK) == (0x4a24e0, 248), 'odomProcessHook symbol or size changed')
    check(elf.symbol(DISPATCH) == (0xcf4220, 592), 'GlobalDispatcher::dispatch changed')
    check(elf.symbol(INV)[0] == 0x48ce10, 'function pointer handler invoker changed')
    check(elf.symbol(MGR)[0] == 0x48d530, 'function pointer handler manager changed')
    print('PASS concrete registration, hook, dispatcher and std::function wrapper symbols')

    # These are actual GOT relocations, not guesses based on nearby names.
    elf.relocation(0x124ed40,
                   b'_ZZN11route_nodes10GlobalHook8InstanceEbE8instance', 0x1255b60)
    elf.relocation(0x124fab8, HOOK, 0x4a24e0)
    elf.relocation(0x1249db0, INV, 0x48ce10)
    elf.relocation(0x1249e60, MGR, 0x48d530)
    print('PASS GOT relocations identify the singleton, odomProcessHook, manager and invoker')

    # Validate singleton -> concrete callback replacement. In the AArch64
    # layout, x20 points at the GlobalHook instance; [x20,#8..#20] contains
    # the std::function object, replaced via the copy/move operations below.
    expected = {
        0x48c0d8:0xf946a2f7,  # singleton GOT pointer
        0x48c0dc:0xf94002f4,  # instance
        0x48c0e0:0xb4003af4,  # if null, lazy initialization branch
        0x48c0fc:0xf9455ca5,  # odomProcessHook pointer via GOT
        0x48c10c:0xf90073e5,  # copy function address to staged payload
        0x48c110:0xa90f0fe4,  # stage manager+invoker
        0x48c128:0xa9408e82,  # load previous callback storage
        0x48c12c:0xa9100fe2,  # stage callback storage
        0x48c130:0xa9008680,  # replace singleton payload
        0x48c140:0xf9000e80,  # replace singleton invocation pointer
        0x48c150:0xf9001280,  # replace singleton manager pointer
        0x48c154:0xb40000a3,  # skip old manager invocation if empty
        0x48c164:0xd63f0060,  # call old callback manager
        0x48c17c:0xd63f0060,  # clean staged callback manager
        0x48c8b0:0x17fffe0d,  # lazy singleton init rejoins install
    }
    for addr, opcode in expected.items():
        elf.instruction(addr, opcode)
    check(branch_target(elf, 0x48c8b0) == 0x48c0e4,
          'singleton initializer does not rejoin callback assignment')
    print('PASS RegisterNodes replaces std::function; null instance detour can rejoin installation')

    for addr, opcode in {
        0x48ce1c:0xf9400062,  # load registered function pointer
        0x48ce24:0xd61f0200,  # function-pointer wrapper tail dispatch
        0x4a2518:0xb40001c0,  # GlobalDispatcher singleton check
        0x4a2538:0xaa1403e1,  # Blackboard argument
        0x4a253c:0xf94002a2,  # odometry value
        0x4a254c:0x17fe9d41,  # tail dispatch to GlobalDispatcher::dispatch PLT
        0xcf4254:0xf9000e80,  # retain Blackboard raw pointer
        0xcf429c:0xf9000683,  # retain odometry number
        0xcf42f4:0xd63f0040,  # invoke one registered dispatcher callback
    }.items():
        elf.instruction(addr, opcode)
    check(branch_target(elf,0x4a254c)==0x449a50,
          'odomProcessHook no longer tail-dispatches via GlobalDispatcher PLT')
    elf.call(0xcf42b4,0x447ee0)  # StopPauser::update PLT
    print('PASS installed hook routes into dispatcher with Blackboard reference and odometry value')
    print('PASS dispatcher retains input state, updates StopPauser and invokes callbacks on eligible path')

    print('X40_V49_GLOBALHOOK_REPLACEMENT_STATIC_PASS')
    print('LIMITS: successful runtime registration, ELF singleton coalescing, callback state,')
    print('  execution frequency, Blackboard effects, special_push_clean_dish and physical rewash unproven.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip')
    p.add_argument('runtime_zip')
    args=p.parse_args()
    try:
        verify(args.original_zip, args.runtime_zip)
    except Exception as exc:
        print('X40_V49_STATIC_FAIL:',str(exc),file=sys.stderr)
        sys.exit(1)