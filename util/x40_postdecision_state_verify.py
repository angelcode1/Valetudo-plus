#!/usr/bin/env python3
"""Read-only X40 R2416 post-decision state-branch verification; no device access."""
import argparse
from x40_turbidity_bt_verify import ELF, PIN

def branch_target(pc, w, kind):
    if kind == 'BL':
        if w & 0xfc000000 != 0x94000000: raise ValueError('expected BL')
        imm=w & 0x3ffffff
        if imm & (1<<25): imm -= 1<<26
        return pc + imm*4
    if kind == 'B.cond':
        if w & 0xff000010 != 0x54000000: raise ValueError('expected B.cond')
        imm=(w>>5) & 0x7ffff
        if imm & (1<<18): imm -= 1<<19
        return pc + imm*4
    raise ValueError('unknown branch type')


WORDS={
 0x256660:0x97f9c4c4,  # separate B-table re-clean decision
 0x2568a0:0xb9458a62, 0x2568a4:0xb9468660,
 0x2568a8:0xb9458e61, 0x2568ac:0x4b020000,
 0x2568b0:0x6b00003f, 0x2568b4:0x54000aeb,
 0x2568b8:0x52800061, 0x2568c0:0xb9007fe1,
 0x2568e8:0x97f9c6ba, 0x256914:0x9130c021,
 0x256928:0x9131e042, 0x256934:0x97f9c94b,
 0x256950:0xb9064a7f, 0x25699c:0xb9458a61,
 0x2569a4:0xb9068661, 0x2569d0:0x97f9c38c,
 0x256a10:0x52800041, 0x256a18:0xb9007fe1,
 0x256a40:0x97f9c664, 0x256a80:0x911c4042,
 0x256a8c:0x97f9bffd, 0x256a90:0x17ffffbd,
}
STRINGS={0x340c30:b'TubidityResult\0',0x340c78:b'success\0',0x339710:b'fail\0'}
def check(path):
    elf=ELF(path,PIN['tactics'])  # requires pinned full-file SHA and AArch64 ELF from prior verifier
    for a,w in WORDS.items():
        if elf.w(a)!=w: raise ValueError('opcode mismatch '+hex(a))
    for a,s in STRINGS.items():
        if elf.at(a,len(s))!=s: raise ValueError('literal mismatch '+hex(a))
    for a,kind,dst in ((0x256660,'BL',0xc7970),(0x2568b4,'B.cond',0x256a10),
                        (0x2568e8,'BL',0xc83d0),(0x256a40,'BL',0xc83d0),
                        (0x256934,'BL',0xc8e60),(0x256a8c,'BL',0xc6a80)):
        if branch_target(a,elf.w(a),kind)!=dst: raise ValueError('branch mismatch '+hex(a))
    w=elf.w(0x256a90)
    if (w&0xfc000000)!=0x14000000:
        raise ValueError('expected B at 0x256a90')
    imm=w&0x3ffffff
    if imm&(1<<25): imm-=1<<26
    if 0x256a90+imm*4!=0x256984:
        raise ValueError('fail arm merge mismatch')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf')
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test:
        assert len(WORDS)==23 and len(STRINGS)==3
        assert branch_target(0x2568b4,0x54000aeb,'B.cond')==0x256a10
        print('X40_POSTDECISION_REPO_SELFTEST_PASS synthetic_only=true');return
    if not a.elf:p.error('provide --elf')
    try:check(a.elf)
    except (OSError,ValueError) as e:p.exit(1,'X40_POSTDECISION_REPO_REFUSED '+str(e)+'\n')
    print('X40_POSTDECISION_REPO_ELF_PASS sha256=true opcodes=23 branches=7 literals=3 no_device_access=true')
if __name__=='__main__':main()
