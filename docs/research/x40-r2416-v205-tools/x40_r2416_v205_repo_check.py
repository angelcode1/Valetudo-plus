#!/usr/bin/env python3
"""Bounded native R2416 v205 reuse-prefix/StationWash check (stdlib, offline)."""
import argparse
import hashlib
import struct
import zipfile

PINS = {
    'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
    'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
}
WORDS = {
    'libbehaviortree_cpp.so':{
        0x7584c:0x97ff1449,0x75870:0x97ff1440,0x75894:0x54002061,
        0x758a4:0xb5003b34,0x759d0:0x3400017c,0x75a18:0x54001e00,
        0x75bbc:0xb94087e0,0x75bc0:0x34fff8a0,0x75c98:0xf90022b6,
        0x75cfc:0x97ff0cc1,0x75d00:0x7100001f,0x75d08:0x1a9f17fc,
        0x75ddc:0xb90087ff,0x76020:0x1a9f07e0,0x76028:0x1a9f17fc,
        0x7602c:0x6a1c001c,
    },
    'liblethe_tree.so':{
        0x30ee3c:0xd0001f41,0x30ee40:0x910d4021,
        0x30ee44:0x97fe92b2,0x30ee48:0xd00012d5,
        0x30ee58:0x97faddf2,
    },
}
EDGES={
    ('libbehaviortree_cpp.so',0x75894,'cond'):0x75ca0,
    ('libbehaviortree_cpp.so',0x758a4,'cbnz'):0x76008,
    ('libbehaviortree_cpp.so',0x759d0,'cbz'):0x759fc,
    ('libbehaviortree_cpp.so',0x75a18,'cond'):0x75dd8,
    ('libbehaviortree_cpp.so',0x75bc0,'cbz'):0x75ad4,
    ('libbehaviortree_cpp.so',0x75cfc,'bl'):0x39000,
    ('liblethe_tree.so',0x30ee44,'bl'):0x2b390c,
    ('liblethe_tree.so',0x30ee58,'bl'):0x1c6620,
}

def need(condition, message):
    if not condition: raise ValueError(message)

def va_bytes(raw, addr, size):
    need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,'Expected AArch64 ELF64LE')
    po=struct.unpack_from('<Q',raw,32)[0]
    ps,n=struct.unpack_from('<HH',raw,54)
    need(ps>=56 and n<=100 and po+ps*n<=len(raw),'Malformed ELF program headers')
    for i in range(n):
        kind,_,offset,virt,_,sz,_,_=struct.unpack_from('<IIQQQQQQ',raw,po+i*ps)
        if kind==1 and virt<=addr and addr+size<=virt+sz:
            index=offset+addr-virt
            need(index+size<=len(raw),'Truncated ELF segment')
            return raw[index:index+size]
    raise ValueError(f'Unmapped ELF VA {addr:#x}')

def word(raw, addr):
    return struct.unpack('<I',va_bytes(raw,addr,4))[0]

def target(addr,insn,kind):
    if kind=='bl':
        need(insn&0xfc000000==0x94000000,'Unexpected BL')
        n,bits=insn&0x3ffffff,26
    else:
        if kind=='cond':
            need(insn&0xff000010==0x54000000,'Unexpected B.cond')
        else:
            need(insn&0x7e000000==0x34000000 and ((insn>>24)&1)==(kind=='cbnz'),'Unexpected CBZ/CBNZ')
        n,bits=(insn>>5)&0x7ffff,19
    if n&(1<<(bits-1)):n-=1<<bits
    return addr+4*n

def run(prior):
    images={}
    with zipfile.ZipFile(prior) as z:
        for name, expected in PINS.items():
            items=[x for x in z.namelist() if '/files/'+name+'/' in x]
            need(len(items)==1,'Missing/ambiguous source ELF: '+name)
            raw=z.read(items[0])
            need(hashlib.sha256(raw).hexdigest()==expected,'Original source SHA mismatch: '+name)
            images[name]=raw
    for name,entries in WORDS.items():
        for address,expected in entries.items():
            need(word(images[name],address)==expected,f'Native opcode mismatch {name}@{address:#x}')
    for (name,address,kind),destination in EDGES.items():
        need(target(address,word(images[name],address),kind)==destination,
             f'Native edge mismatch {name}@{address:#x}')
    bb=images['libbehaviortree_cpp.so']
    tree=images['liblethe_tree.so']
    for address,value in ((0xad370,b'/\0'),(0xad900,b'.\0'),(0xad908,b'reuse\0')):
        need(va_bytes(bb,address,len(value))==value,'Path literal changed')
    for address,value in ((0x56832e,b'SubtreeCondition\0'),
                          (0x568350,b'subtree_file_path\0'),
                          (0x58eb2a,b'StationWash.xml\0')):
        need(va_bytes(tree,address,len(value))==value,'Generated parameter changed')
    p=struct.unpack('<QQQQ',va_bytes(tree,0x6f8370,32))
    need(p==(0x568350,17,0x58eb2a,15),'StationWash parameter pointer changed')
    need(b'reuse/StationWash' not in tree,'New statically embedded reused StationWash path')
    need(b'reuse/AiStainMop' in tree,'Other reused native subtree example missing')
    return sum(map(len,WORDS.values())),len(EDGES)

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--prior-zip',required=True)
    o=a.parse_args()
    try:
        count=run(o.prior_zip)
        print('X40_R2416_V205_REPO_REUSE_BOUNDARY_STATIC_PASS',*count)
        print('Plain StationWash.xml does not opt into cache insertion on a miss; preexisting cache hit remains possible.')
    except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
        raise SystemExit('X40_R2416_V205_REPO_FAIL: '+str(e))
