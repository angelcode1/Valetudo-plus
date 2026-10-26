#!/usr/bin/env python3
"""X40 R2416 v201 bounded station-message/Blackboard checker.

Offline Python 3 stdlib only. Reads private collector ZIP IN MEMORY and prints
no original payload bytes. This is a smaller repo-side check; full v197–v201
regression and mutation tests live in the standalone sanitized ZIP.
"""
import argparse
import hashlib
import struct
from zipfile import ZipFile, BadZipFile

PINS={
  "node_lethe.so":"b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0",
  "liblethe_tactics_tree.so":"da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c",
}
WORDS={
 "node_lethe.so":{
   0x8f90a4:0xaa0003f4,0x8f9108:0x540041c0,
   0x8f916c:0x34004ab7,0x8f9178:0x540050a0,
   0x8f9184:0xf9401a84,0x8f91ac:0xd00007e1,
   0x8f91b0:0x9119c021,0x8f91f0:0xf940105a,
   0x8f9204:0xa94997e4,0x8f9228:0xa9021464,
   0x8f9238:0xa9041464,0x8f9240:0xa9051c66,
   0x8f9248:0xa9061464,0x8f924c:0xd63f0340,
   0x3552c0:0xf9401802,0x3552c8:0x97fc803e,
 },
 "liblethe_tactics_tree.so":{
   0x250770:0x97f9d650,0x250794:0xd00006c1,
   0x250798:0x91180021,0x250850:0x7940bc1b,
   0x251fbc:0xeb3b201f,0x251fc0:0x54ff6cc9,
   0x251fec:0x9ba20761,0x252004:0x17ffeae3,
 }
}
LITERALS={
  "node_lethe.so":(0x9f7670,b"station_info_sub\x00"),
  "liblethe_tactics_tree.so":(0x32a600,b"station_info_sub\x00"),
}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def load_elf(z,name):
    paths=[x for x in z.namelist() if '/files/'+name+'/' in x]
    need(len(paths)==1,'Missing/ambiguous evidence: '+name)
    data=z.read(paths[0])
    need(hashlib.sha256(data).hexdigest()==PINS[name],name+' whole-file SHA mismatch')
    return data
def va_bytes(blob,addr,length):
    need(blob[:6]==b'\x7fELF\x02\x01' and
         struct.unpack_from('<H',blob,18)[0]==183,'Expected AArch64 ELF64LE')
    po=struct.unpack_from('<Q',blob,32)[0]
    sz,count=struct.unpack_from('<HH',blob,54)
    need(sz>=56 and count<100 and po+sz*count<=len(blob),'Malformed ELF headers')
    for n in range(count):
        typ,_,off,va,_,extent,_,_=struct.unpack_from('<IIQQQQQQ',blob,po+n*sz)
        if typ==1 and va<=addr and addr+length<=va+extent:
            start=off+addr-va
            need(start+length<=len(blob),'ELF segment truncated')
            return blob[start:start+length]
    raise ValueError('Virtual address not file backed')
def word(b,v):return struct.unpack('<I',va_bytes(b,v,4))[0]
def target_b_cond(va,insn):
    need(insn&0xff000010==0x54000000,'Expected B.cond')
    imm=(insn>>5)&0x7ffff
    if imm&(1<<18): imm-=1<<19
    return va+imm*4
def target_bl(va,insn):
    need(insn&0xfc000000==0x94000000,'Expected BL')
    imm=insn&0x3ffffff
    if imm&(1<<25):imm-=1<<26
    return va+imm*4
def adrp_add(va,ap,ad):
    need(ap&0x9f000000==0x90000000,'Expected ADRP')
    r=ap&31
    need(ad&0xffc00000==0x91000000 and ad&31==r and (ad>>5)&31==r,'Expected ADD same register')
    imm=(((ap>>5)&0x7ffff)<<2)|((ap>>29)&3)
    if imm&(1<<20): imm-=1<<21
    return (va&~4095)+(imm<<12)+((ad>>10)&0xfff)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    opt=p.parse_args()
    with ZipFile(opt.prior_zip) as z:
        images={name:load_elf(z,name) for name in PINS}
    for name,insns in WORDS.items():
        for va,expected in insns.items():
            need(word(images[name],va)==expected,f'{name} instruction mismatch at {va:#x}')
        va,lit=LITERALS[name]
        need(va_bytes(images[name],va,len(lit))==lit,name+' key literal changed')
    h=images['node_lethe.so'];t=images['liblethe_tactics_tree.so']
    need(adrp_add(0x8f91ac,word(h,0x8f91ac),word(h,0x8f91b0))==0x9f7670,
         'Station producer key construction changed')
    need(adrp_add(0x250794,word(t,0x250794),word(t,0x250798))==0x32a600,
         'Station consumer key construction changed')
    need(target_b_cond(0x8f9108,word(h,0x8f9108))==0x8f9940,'Producer guard changed')
    need(target_b_cond(0x8f9178,word(h,0x8f9178))==0x8f9b8c,'Sentinel guard changed')
    need(target_b_cond(0x251fc0,word(t,0x251fc0))==0x250d58,'Subtype bounds guard changed')
    need(target_bl(0x3552c8,word(h,0x3552c8))==0x2753c0,'Tree root constructor call changed')
    print('X40_R2416_V201_REPO_NATIVE_STATION_INFO_PASS')
    print('2 original SHA-pinned native ELFs, 24 word anchors and 4 control-flow targets verified')
    print('Static producer and compatible consumer only; not proof of live Blackboard identity')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,struct.error,BadZipFile) as e:
        raise SystemExit('X40_R2416_V201_REPO_FAIL: '+str(e))
