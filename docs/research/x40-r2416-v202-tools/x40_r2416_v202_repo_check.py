#!/usr/bin/env python3
"""Offline v202 bounded fresh/cache subtree Blackboard proof (stdlib only).

Uses the original owner-private collector ZIP. Reads but never writes vendor ELF.
The full verified v197-v202 regression chain is in the separate v202 ZIP kit.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import sys
from zipfile import ZipFile, BadZipFile

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'x40-r2416-v201-tools'))
from x40_r2416_v201_repo_check import va_bytes, word, need

PIN="665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94"
WORDS={
  0x75ac4:0xf94022c0,0x75ac8:0xb4000580,0x75acc:0xf9400000,
  0x75ad0:0xa9027ea0,0x75b74:0xb5fffac0,0x75b84:0xb5001300,
  0x75b8c:0x97ff0cdd,0x75ba0:0xaa1703e2,0x75bb0:0x97ff0dac,
  0x75de0:0xb4ffed40,0x75de8:0x97ff0ce6,0x75f68:0x97ff0be6,
  0x75f8c:0xaa1703e2,0x75f9c:0xd63f0060,
  0x5f634:0xf94057e1,0x5f638:0x97ff68a6,0x5f650:0x97ff689c,
  0x505f8:0xf94002a3,0x50610:0xeb03003f,0x50614:0x540004c0,
}
EDGES={
 (0x75ac8,'cbz'):0x75b78,(0x75b74,'cbnz'):0x75acc,
 (0x75b84,'cbnz'):0x75de4,(0x75de0,'cbz'):0x75b88,
 (0x75b8c,'bl'):0x38f00,(0x75bb0,'bl'):0x39260,
 (0x75de8,'bl'):0x39180,(0x75f68,'bl'):0x38f00,
 (0x5f638,'bl'):0x398d0,(0x5f650,'bl'):0x398c0,
 (0x50614,'cond'):0x506ac,
}

def target(va, insn, kind):
    if kind=='bl':
        need(insn&0xfc000000==0x94000000,'BL opcode changed')
        val=insn&0x3ffffff; bits=26
    elif kind=='cond':
        need(insn&0xff000010==0x54000000,'B.cond opcode changed')
        val=(insn>>5)&0x7ffff; bits=19
    else:
        need((insn&0x7e000000)==0x34000000,'CBZ family changed')
        need(((insn>>24)&1)==(kind=='cbnz'),'CBZ polarity changed')
        val=(insn>>5)&0x7ffff; bits=19
    if val&(1<<(bits-1)):val-=1<<bits
    return va+val*4

def verify(blob):
    need(hashlib.sha256(blob).hexdigest()==PIN,'Original libbehaviortree_cpp SHA mismatch')
    for addr,expected in WORDS.items():
        need(word(blob,addr)==expected,f'Native word mismatch {addr:#x}')
    for (addr,kind),expected in EDGES.items():
        need(target(addr,word(blob,addr),kind)==expected,f'Branch mismatch {addr:#x}')
    start=0x757b0; length=4112
    body=va_bytes(blob,start,length)
    matches=[]
    for offset in range(0,len(body),4):
        insn=struct.unpack_from('<I',body,offset)[0]
        if insn&0xfc000000==0x94000000:
            destination=target(start+offset,insn,'bl')
            if destination in (0x398d0,0x505b0):
                matches.append(start+offset)
    need(not matches,'New direct setBlackboard call within bounded onInit function')
    return len(WORDS),len(EDGES)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    args=p.parse_args()
    with ZipFile(args.prior_zip) as z:
        members=[n for n in z.namelist()
                 if '/files/libbehaviortree_cpp.so/' in n]
        need(len(members)==1,'Missing or ambiguous native input')
        body=z.read(members[0])
    words,edges=verify(body)
    print(f'X40_R2416_V202_REPO_FRESH_CACHE_STATIC_PASS {words} words {edges} edges')
    print('Scoped direct-call absence is not a claim about indirect or live binding')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,IndexError,struct.error,BadZipFile) as exc:
        raise SystemExit('X40_R2416_V202_REPO_FAIL: '+str(exc))
