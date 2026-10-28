#!/usr/bin/env python3
"""Original pinned AVA topic-contract checker, Python 3 stdlib only.
Requires owner-private v230 evidence ZIP. No network, robot or vendor code execution.
"""
import argparse
import hashlib
import json
import re
import struct
import zipfile

AVA_SHA='30c0302537c1ae5b1b95d5debeb654ebbb9cb3ad8760fcfb31f2acb81836d826'
HEALTH_SHA='5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5'
WORDS={0x2585c:0x52800001,0x2586c:0x9100c260,0x25870:0x94002518,
0x26448:0x52800021,0x26450:0x9100c000,0x26454:0x9400221f,
0x2ed14:0xaa0303e1,0x2ed1c:0x910022e1,0x2ed34:0xf9400661,
0x2ed38:0xf9400400,0x2ed40:0x54001440,0x2ed50:0x97ff7e10,
0x2ed68:0x34001b18,0x23780:0xa9bb7bfd,0x237a0:0xb4000894,
0x2387c:0xb94072c0,0x238b0:0x52800000}
CALLS={0x25870:0x2ecd0,0x26454:0x2ecd0,0x2ed50:0xe590}

def sha(b):return hashlib.sha256(b).hexdigest()
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def u64(b,p):return struct.unpack_from('<Q',b,p)[0]
def signed(v,n):return v-(1<<n) if v&(1<<(n-1)) else v

def locate(b,va):
    if b[:6]!=b'\x7fELF\x02\x01' or u16(b,18)!=183:
        raise ValueError('Wrong ELF architecture')
    base=u64(b,40);stride=u16(b,58);count=u16(b,60)
    if stride<64 or not (1<=count<=200) or base+stride*count>len(b):
        raise ValueError('Bad ELF section headers')
    for i in range(count):
        h=base+i*stride;addr=u64(b,h+16);off=u64(b,h+24);size=u64(b,h+32)
        if addr<=va and va+4<=addr+size and off+size<=len(b):
            return off+va-addr
    raise ValueError('Unmapped ELF instruction '+hex(va))

def check(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        rows=json.loads(z.read('manifest.PRIVATE.json'))['records']
        rows=[r for r in rows if r.get('status')=='saved']
        checks={p:h for h,p in [s.split('  ',1) for s in
                z.read('SHA256SUMS.PRIVATE.txt').decode().splitlines()]}
        if len(rows)!=35 or len(checks)!=35:raise ValueError('Archive manifest mismatch')
        saved={}
        topic_count=0
        for r in rows:
            member=r['stored_as']
            if not re.fullmatch(r'files/[a-f0-9]{20}-[A-Za-z0-9._-]+',member):
                raise ValueError('Unsafe ZIP member')
            b=z.read(member);h=sha(b)
            if h!=r['original_sha256'] or h!=checks.get(member) or len(b)!=r['size']:
                raise ValueError('Evidence hash/size mismatch')
            if r['category']=='native':
                topic_count+=b.count(b'SENSORS\x00')
            if h in (AVA_SHA,HEALTH_SHA):saved[h]=b
        if topic_count!=1 or set(saved)!={AVA_SHA,HEALTH_SHA}:
            raise ValueError('Native literal census or pinned ELF missing')
    ava=saved[AVA_SHA]
    for addr,expected in WORDS.items():
        w=u32(ava,locate(ava,addr))
        if w!=expected:raise ValueError('Original instruction mismatch '+hex(addr))
    for addr,target in CALLS.items():
        w=WORDS[addr];imm=signed(w&0x3ffffff,26)
        if (w>>26)!=0b100101 or addr+imm*4!=target:
            raise ValueError('Original BL destination mismatch')
    for addr,w,mask,form,target in [
        (0x2ed40,WORDS[0x2ed40],0xff000010,0x54000000,0x2efc8),
        (0x2ed68,WORDS[0x2ed68],0x7f000000,0x34000000,0x2f0c8),
        (0x237a0,WORDS[0x237a0],0x7f000000,0x34000000,0x238b0)]:
        if w&mask!=form or addr+signed((w>>5)&0x7ffff,19)*4!=target:
            raise ValueError('Original conditional branch mismatch')
    print('X40_R2416_V234_REPO_AVA_TOPIC_CONTRACT_PASS',len(WORDS),len(CALLS),len(rows))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v230-private',required=True)
    check(p.parse_args().v230_private)
