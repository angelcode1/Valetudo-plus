#!/usr/bin/env python3
"""Dreame X40 R2416 v51 offline-only GlobalDispatcher callback-ABI verifier.

Usage: python3 x40_r2416_v51_dispatcher_callback_abi_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Requires sibling v48, v49, v50 verifier modules. No network, robot interaction,
firmware modification, image extraction or write-back. Uses inert ELF bytes.
"""
import argparse
import sys
from x40_r2416_v50_dispatcher_listener_gate_verify import verify as verify_v50
from x40_r2416_v48_globalhook_callback_verify import original_and_runtime, check

SYMBOL=b'_ZN17global_dispatcher16GlobalDispatcher8dispatchERSt10shared_ptrIN2BT10BlackboardEEm'

# Fixed words in the full-SHA-pinned original liblethe_route_nodes.so. Each
# corresponds to the ARM64 register/field flow described in the report.
WORDS={
  0xcf4234:0xaa0003f4,  # mov x20,x0 (dispatcher)
  0xcf423c:0xaa0103f6,  # mov x22,x1 (incoming shared_ptr reference)
  0xcf4240:0xf9001fe2,  # str x2,[sp,#0x38] (numeric argument)
  0xcf4244:0xf9400020,  # ldr x0,[x1] (shared_ptr raw pointer)
  0xcf4254:0xf9000e80,  # str x0,[x20,#0x18]
  0xcf4258:0xf9401280,  # ldr x0,[x20,#0x20] (old owner)
  0xcf425c:0xf94006d3,  # ldr x19,[x22,#0x8] (incoming owner)
  0xcf4260:0xeb00027f,  # cmp x19,x0
  0xcf4264:0x54000180,  # b.eq owner retained
  0xcf4268:0xb4000113,  # cbz x19, skip count increment
  0xcf4278:0xb9400a60,  # ldr w0,[x19,#8]
  0xcf427c:0x11000400,  # add w0,w0,#1
  0xcf4280:0xb9000a60,  # str w0,[x19,#8]
  0xcf4284:0xf9401280,  # ldr x0,[x20,#0x20]
  0xcf4288:0xb4000040,  # cbz x0, no old owner release
  0xcf4290:0xf9001293,  # str x19,[x20,#0x20]
  0xcf4298:0xf9401fe3,  # ldr x3,[sp,#0x38]
  0xcf429c:0xf9000683,  # str x3,[x20,#0x8] (numeric value)
  0xcf42cc:0xf9403a93,  # ldr x19,[x20,#0x70] (first RB tree node)
  0xcf42d0:0x91018294,  # add x20,x20,#0x60 (registry header)
  0xcf42d4:0xeb13029f,  # cmp x20,x19
  0xcf42dc:0x9100e3f5,  # add x21,sp,#0x38 (callback arg)
  0xcf42e0:0xf9402a62,  # ldr x2,[x19,#0x50] (invoker)
  0xcf42e4:0x91010260,  # add x0,x19,#0x40 (callback payload)
  0xcf42e8:0xb4000c02,  # null callback exception path
  0xcf42ec:0xf9400c02,  # ldr x2,[x0,#0x18] (invoker)
  0xcf42f0:0xaa1503e1,  # mov x1,x21 (= address of numeric argument)
  0xcf42f4:0xd63f0040,  # blr x2
  0xcf42f8:0xaa1303e0,  # mov x0,x19
  0xcf42fc:0x97dd6405,  # RB-tree increment@plt
  0xcf4300:0xaa0003f3,  # mov x19,x0
  0xcf4304:0xeb00029f,  # cmp x20,x0
  0xcf4308:0x54fffec1,  # next listener if not at end
}

def verify(original_zip,runtime_zip):
    # v50 transitively checks full hashes, runtime equality, and the upstream
    # hook replacement/odometry gates before this local ABI/ownership check.
    verify_v50(original_zip,runtime_zip)
    route=original_and_runtime(original_zip,runtime_zip)['liblethe_route_nodes.so']
    check(route.symbol(SYMBOL)==(0xcf4220,592), 'unexpected dispatcher function extent')
    for addr, opcode in WORDS.items():
        route.instruction(addr,opcode)
    route.call(0xcf428c,0x440f80)   # std::_Sp_counted_base::_M_release@plt
    route.call(0xcf42fc,0x44d310)   # RB tree increment@plt
    # Relocation for singleton pointer means the caller can discover dispatcher,
    # but it does NOT prove any particular listener registry entry exists.
    route.relocation(0x124e498,b'_ZZN17global_dispatcher16GlobalDispatcher8InstanceEbE8instance',0x1256770)
    print(f'PASS exact dispatcher ABI/ownership anchors={len(WORDS)} (original ELF SHA-pinned)')
    print('PASS Blackboard raw/owner fields +0x18/+0x20 and odometry field +0x08')
    print('PASS listener callback receives x0=entry+0x40, x1=&odometry stack argument')
    print('PASS listener tree iteration, release of previous owner and singleton relocation')
    print('X40_V51_DISPATCHER_CALLBACK_ABI_STATIC_PASS')
    print('LIMITS: no concrete listener identity or insertion proven; callbacks may use')
    print(' retained dispatcher Blackboard indirectly. R2416 rewash remains unproven.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V51_STATIC_FAIL:',str(exc),file=sys.stderr)
        sys.exit(1)