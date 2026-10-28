#!/usr/bin/env python3
"""Compact original v237 retained route-health state checker, Python 3 stdlib.

Requires local owner PRIVATE v230 ZIP, never executes vendor firmware or contacts robot.
In GitHub imports the existing v236 checker from its adjacent versioned directory.
"""
import argparse, hashlib, json, struct, sys, zipfile
from pathlib import Path
here=Path(__file__).resolve().parent
old=here.parent/'x40-r2416-v236-tools'
sys.path.insert(0,str(old if old.is_dir() else here))
from x40_r2416_v236_repo_check import verify as verify_v236
PIN='5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5'
WORDS={
0x9bf18:0x39400444,0x9bf1c:0x39401443,0x9bf24:0x39405454,
0x9bf40:0x52000061,0x9bf44:0x39401442,0x9bf48:0x6a02003f,
0x9bf70:0x39405660,0x9bf74:0x6b14001f,0x9bf78:0x540002a0,
0x9bf8c:0xf9433863,0x9bf90:0xf944cc42,0x9bf94:0xf9457421,
0x9bf98:0x7900007f,0x9bf9c:0xf946bc00,0x9bfa0:0x7900005f,
0x9bfa4:0x7900003f,0x9bfa8:0xb900203f,0x9bfac:0x7900001f,
0x9bfb0:0xb900201f,0x9bfb4:0xb900205f,0x9bfb8:0xb900207f,
0x9bfbc:0x7900487f,0x9bfc0:0x7900485f,0x9bfc4:0x7900483f,
0x9bfc8:0x7900481f,0x9bffc:0x54fffaa0,
}
GLOBALS={0xe8670:1707,0xe8998:2071,0xe8ae8:2155,0xe7d78:1193}
def u32(b,a):return struct.unpack_from('<I',b,a)[0]
def verify(path):
    verify_v236(path)
    with zipfile.ZipFile(path) as z:
        saved=[r for r in json.loads(z.read('manifest.PRIVATE.json'))['records'] if r.get('status')=='saved']
        matches=[z.read(r['stored_as']) for r in saved if r.get('original_sha256')==PIN and r.get('category')=='native']
    if len(saved)!=35 or len(matches)!=1 or hashlib.sha256(matches[0]).hexdigest()!=PIN:
        raise ValueError('Original private v230 SHA-pinned health ELF missing')
    b=matches[0]
    for a,expected in WORDS.items():
        if u32(b,a)!=expected:raise ValueError('v237 original reset instruction mismatch '+hex(a))
    for a,target in [(0x9bf78,0x9bfcc),(0x9bffc,0x9bf50)]:
        inst=u32(b,a)
        imm=(inst>>5)&0x7ffff
        if imm&0x40000:imm-=0x80000
        if (inst&0xff000010)!=0x54000000 or a+imm*4!=target:
            raise ValueError('v237 original branch destination mismatch')
    got={}
    for p in range(0x3a628,0x3a628+0xd188,24):
        where,info,add=struct.unpack_from('<QQq',b,p)
        if where in GLOBALS:got[where]=(info>>32,info&0xffffffff,add)
    if got!={a:(num,1025,0) for a,num in GLOBALS.items()}:
        raise ValueError('Original four retained-state global relocations changed')
    calls=[]
    for a in range(0x9bf00,0x9c008,4):
        inst=u32(b,a)
        if inst>>26==0b100101:
            imm=inst&0x3ffffff
            if imm&0x2000000:imm-=0x4000000
            calls.append((a,a+imm*4))
    if calls!=[(0x9c000,0x4b460)]:
        raise ValueError('v237 unexpected direct callback call site')
    print('X40_R2416_V237_REPO_STUCK_STATE_RESET_PASS',len(WORDS),len(GLOBALS),len(saved))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v230-private',required=True)
    verify(p.parse_args().v230_private)
