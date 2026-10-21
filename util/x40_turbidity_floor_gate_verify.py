#!/usr/bin/env python3
"""Check a limited R2416 WashFloorTubidityCheck branch (offline, read-only)."""
import argparse
from x40_turbidity_bt_verify import ELF, PIN

# Fixed opcode anchors for the identified conditional path; no gadget execution.
WORDS = {
    0x255a94: 0xb90077ff,  # local smart_hosting_switch result zero-init
    0x255ce4: 0xf9401442,  # Blackboard contains vtable slot +0x28
    0x255ce8: 0xd63f0040,  # virtual contains call
    0x255cec: 0x72001c1b,  # mask contains result into w27
    0x255cf0: 0x54000480,  # no marker -> alternative path
    0x255d0c: 0xb9467661,  # load this+0x674
    0x255d10: 0x51000421,  # decrement counter by 1
    0x255d14: 0xb9067661,  # store this+0x674
    0x255d18: 0x7100003f,  # compare countdown with 0
    0x255d1c: 0x540000cc,  # positive -> skip block
    0x255d20: 0xb9467a60,  # load this+0x678
    0x255d24: 0x7100001f,  # compare with 0
    0x255d28: 0x5400006d,  # nonpositive -> skip block
    0x255d2c: 0xeb1a02df,  # compare x22 and x26
    0x255d30: 0x540003c0,  # equal -> downstream tests
    0x255da8: 0xb94077e0,  # load smart_hosting_switch result
    0x255dac: 0x7100001f,  # compare result with 0
    0x255db0: 0x7a40cb60,  # conditional compare marker w27 with 0
    0x255db4: 0x54fffc01,  # nonzero condition -> skip block
    0x255de4: 0xf0000741,  # robot_oversea_avoid_turbidity string page
    0x255de8: 0x91304021,  # corresponding string offset
    0x255e30: 0xf9401442,  # another Blackboard contains slot +0x28
    0x255e34: 0xd63f0040,  # virtual contains call
    0x255e38: 0x72001c1f,  # test contains result
    0x255e3c: 0x54000220,  # absent -> further handling
}
LITERALS={
    0x32a968: b'smart_hosting_switch',
    0x340bf8: b'turbidity_reclean_flag',
    0x340c10: b'robot_oversea_avoid_turbidity',
}

def verify(path):
    elf=ELF(path,PIN['tactics'])
    for addr,expected in WORDS.items():
        if elf.w(addr)!=expected:
            raise ValueError('instruction mismatch at '+hex(addr))
    for addr,key in LITERALS.items():
        if elf.at(addr,len(key)+1)!=key+b'\0':
            raise ValueError('key mismatch at '+hex(addr))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tactics',help='private, unmodified liblethe_tactics_tree.so')
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        assert len(WORDS)>=20 and len(LITERALS)==3
        print('X40_TURBIDITY_FLOOR_SELFTEST_PASS synthetic_only=true')
        return
    if not args.tactics:
        parser.error('provide --tactics or --self-test')
    try:
        verify(args.tactics)
    except (OSError,ValueError) as exc:
        parser.exit(1,'X40_TURBIDITY_FLOOR_REFUSED '+str(exc)+'\n')
    print('X40_TURBIDITY_FLOOR_ELF_PASS sha256=true opcodes=25 keys=3 no_device_access=true')

if __name__=='__main__':
    main()
