#!/usr/bin/env python3
"""Compact original-private X40 R2416 v236 route/health checker, stdlib only.

In repository, import sibling v235 verifier from ../x40-r2416-v235-tools.
In source-only ZIP, import it from the same extracted directory.
"""
import argparse, hashlib, json, struct, sys, zipfile
from pathlib import Path
here=Path(__file__).resolve().parent
prev=here.parent/'x40-r2416-v235-tools'
sys.path.insert(0,str(prev if prev.is_dir() else here))
from x40_r2416_v235_repo_check import verify as verify_v235

HEALTH_SHA='5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5'
WORDS={
  0xae574:0xd0000081,0xae578:0x91038021,
  0xae590:0xd00001c2,0xae5a0:0xf9421c42,
  0xae600:0xb00001c4,0xae60c:0xf946e484,
  0xae608:0xaa1303e1,0xae610:0xaa1403e0,0xae614:0x52800123,
  0xae61c:0x97fe73c9,
  0xb021c:0x90000080,0xb0220:0x91070000,
  0xb0224:0x900001c2,0xb0234:0xf9431042,
  0xb0248:0xaa1303e0,0xb024c:0xaa1703e1,0xb0254:0x97fe68af,
  0x9bf0c:0xb0000273,0x9bf10:0xf940a662,0x9bf14:0xa9401c26,
  0x9bf20:0xa9001c46,0x9bf28:0xf840e021,0x9bf2c:0xf800e041,
  0x9bf4c:0x540005a1,0x9c000:0x97febd18,
}

def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def u64(b,p):return struct.unpack_from('<Q',b,p)[0]
def signed(x,n):return x-(1<<n) if x&(1<<(n-1)) else x

def verify(path):
    verify_v235(path)
    with zipfile.ZipFile(path) as z:
        rows=[r for r in json.loads(z.read('manifest.PRIVATE.json'))['records'] if r.get('status')=='saved']
        matches=[z.read(r['stored_as']) for r in rows if r.get('category')=='native' and r.get('original_sha256')==HEALTH_SHA]
    if len(rows)!=35 or len(matches)!=1:raise ValueError('Missing original SHA-pinned health component')
    b=matches[0]
    if hashlib.sha256(b).hexdigest()!=HEALTH_SHA:raise ValueError('Original health SHA mismatch')
    if b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',b,18)[0]!=183:raise ValueError('Wrong ELF')
    # Verify original VAs map directly to file offsets in pinned ELF .text & .rodata.
    header=u64(b,40);stride=struct.unpack_from('<H',b,58)[0];number=struct.unpack_from('<H',b,60)[0]
    if stride<64 or number<1 or number>200 or header+stride*number>len(b):raise ValueError('Bad section headers')
    mapped=set()
    for i in range(number):
        p=header+stride*i;addr=u64(b,p+16);off=u64(b,p+24);size=u64(b,p+32)
        if addr==off and off+size<=len(b):mapped.update(a for a in WORDS if addr<=a<a+4<=addr+size)
    if mapped!=set(WORDS):raise ValueError('Expected original VA/file map differs')
    for a,expected in WORDS.items():
        if u32(b,a)!=expected:raise ValueError('Original v236 AArch64 word mismatch')
    if b[0xc00e0:0xc00f2]!=b'ROUTE_NODE_HEALTH\0' or b[0xc01c0:0xc01d0]!=b'HEALTH_TO_ROUTE\0':
        raise ValueError('Original named topic missing')
    for a,target in [(0xae61c,0x4b540),(0xb0254,0x4a510),(0x9c000,0x4b460)]:
        ins=u32(b,a)
        if ins>>26!=0b100101 or a+(signed(ins&0x3ffffff,26)<<2)!=target:
            raise ValueError('v236 original direct call changed')
    # Fixed original .rela.dyn (also checked via v235 whole-ELF digest).
    rels={}
    for p in range(0x3a628,0x3a628+0xd188,24):
        where,info,add=struct.unpack_from('<QQq',b,p)
        if where in (0xe8438,0xe7dc8,0xe8620):rels[where]=(info>>32, info&0xffffffff,add)
    if rels!={0xe8438:(1779,1025,0),0xe7dc8:(415,1025,0),0xe8620:(1600,1025,0)}:
        raise ValueError('v236 original callback/type-information relocations changed')
    print('X40_R2416_V236_REPO_ROUTE_HEALTH_PASS',len(WORDS),3,len(rows))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v230-private',required=True)
    verify(p.parse_args().v230_private)
