#!/usr/bin/env python3
"""Offline X40 R2416 rewash-count / AVA turbidity-gate check; no device I/O."""
import argparse
from x40_turbidity_bt_verify import ELF, PIN

AVA_SHA = 'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
REFS = {
    'tactics': ([0x2354ac,0x23dee4,0x24ea00,0x254e7c,0x25640c],0x340600),
    'ava': ([0x5cd8cc,0x5cdbb8],0xa127c0),
}
WORDS = {
    'tactics':{0x23daac:0x34002120,0x23ded0:0x52800020,0x23ded4:0xb9067a60,
        0x254e5c:0xb9467a81,0x254e64:0xb9067680,0x254e6c:0x51000421,
        0x254e70:0xb9067a81,0x2563f0:0xb9467a61,0x2563f8:0xb9067660,
        0x256400:0x51000421,0x256404:0xb9067a61},
    'ava':{0x5cdbcc:0x910353e2,0x5cdbe0:0xaa1403e1,0x5cdc6c:0x340000b6,
        0x5cdc70:0x394162a0,0x5cdc74:0x7100041f,0x5cdd14:0xb940d7e0,
        0x5cdd18:0x35fffb40},
}
BRANCHES = {
    'tactics':[(0x23d040,'BL',0xc5fc0),(0x23d7e4,'BL',0xc86d0),
               (0x23daac,'CBZ',0x23ded0),(0x23df04,'BL',0xc7800),
               (0x254e9c,'BL',0xc7800),(0x25643c,'BL',0xc7800)],
    'ava':[(0x5cdbe8,'BL',0x2746d0),(0x5cdd18,'CBNZ',0x5cdc80)],
}
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def ref(e,a):
    w=e.w(a); w2=e.w(a+4)
    if w&0x9f000000!=0x90000000 or w2&0xffc00000!=0x91000000 or (w&31)!=((w2>>5)&31):
        raise ValueError('not ADRP+ADD '+hex(a))
    imm=((w>>29)&3)|(((w>>5)&0x7ffff)<<2)
    return (a&~4095)+(sx(imm,21)<<12)+((w2>>10)&4095)
def branch(e,a,kind):
    w=e.w(a)
    if kind=='BL':
        if w&0xfc000000!=0x94000000:raise ValueError('not BL '+hex(a))
        return a+4*sx(w&0x3ffffff,26)
    expected={'CBZ':0x34000000,'CBNZ':0x35000000}[kind]
    if w&0x7f000000!=expected:raise ValueError('not '+kind+' '+hex(a))
    return a+4*sx((w>>5)&0x7ffff,19)
def verify(tactics,ava):
    bins={'tactics':ELF(tactics,PIN['tactics']),'ava':ELF(ava,AVA_SHA)}
    for k,e in bins.items():
        refs,key=REFS[k]
        if e.at(key,15)!=b'max_rewash_cnt\0':raise ValueError('key missing '+k)
        for a in refs:
            if ref(e,a)!=key:raise ValueError('key ref mismatch '+k+' '+hex(a))
        for a,w in WORDS[k].items():
            if e.w(a)!=w:raise ValueError('opcode mismatch '+k+' '+hex(a))
        for a,kind,dst in BRANCHES[k]:
            if branch(e,a,kind)!=dst:raise ValueError('branch mismatch '+k+' '+hex(a))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tactics');p.add_argument('--ava');p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if args.self_test:
        assert len(REFS['tactics'][0])==5 and len(REFS['ava'][0])==2
        assert len(WORDS['tactics'])==11 and len(WORDS['ava'])==7
        print('X40_BUDGET_AVA_REPO_SELFTEST_PASS synthetic_only=true');return
    if not args.tactics or not args.ava:p.error('provide both pinned ELF paths')
    try:verify(args.tactics,args.ava)
    except (ValueError,OSError) as e:p.exit(1,'X40_BUDGET_AVA_REPO_REFUSED '+str(e)+'\n')
    print('X40_BUDGET_AVA_REPO_ELF_PASS sha256_both=true refs=7 anchors=18 branches=8 no_device_access=true')
if __name__=='__main__':main()
