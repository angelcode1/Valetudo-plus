#!/usr/bin/env python3
"""Standalone v209 original-native path and no-new-resolver metadata check.

Python 3 stdlib only. Never extracts original firmware, accesses the robot,
or publishes private archive contents. Full historical replay is in v209 kit.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile

BT_SHA="665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94"
COLLECTION_SHA="47905a5e9ed7e59a25ef6db1ae07ccb3f5641d439cf3e31a76f018bd7e3907ee"
WORDS={
  0x6f9ac:0xaa0103f5,0x6f9d8:0x97ff2b9e,0x6fb6c:0xd2800023,
  0x6fb90:0x97ff29a8,0x6fe48:0xaa1903e8,0x6fe50:0x97ff24e4,
  0x733b4:0xf94063e0,0x733b8:0xaa1403e1,0x733bc:0x97ff1d01,
  0x733c0:0xaa0003f3,0x733dc:0xb40024d3
}
CALLS={0x6f9d8:0x3a850,0x6fb90:0x3a230,0x6fe50:0x391e0,0x733bc:0x3a7c0}

def need(ok,msg):
    if not ok: raise ValueError(msg)

def word_at(raw,addr):
    need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
         'Expected AArch64 ELF64LE')
    ph=struct.unpack_from('<Q',raw,32)[0]
    ent,n=struct.unpack_from('<HH',raw,54)
    need(ent>=56 and n<=100 and ph+ent*n<=len(raw),'Bad ELF program headers')
    for i in range(n):
        typ,_,offset,va,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,ph+i*ent)
        if typ==1 and va<=addr and addr+4<=va+size:
            off=offset+addr-va
            need(off+4<=len(raw),'Truncated ELF segment')
            return struct.unpack_from('<I',raw,off)[0]
    raise ValueError('Unmapped native instruction')

def target(at,insn,mode):
    if mode=='bl':
        need(insn&0xfc000000==0x94000000,'Unexpected BL')
        imm,bits=insn&0x3ffffff,26
    else:
        need(insn&0x7f000000==0x34000000,'Unexpected CBZ')
        imm,bits=(insn>>5)&0x7ffff,19
    if imm&(1<<(bits-1)): imm-=1<<bits
    return at+4*imm

def verify(prior,resolver):
    with zipfile.ZipFile(prior) as z:
        matches=[p for p in z.namelist() if '/files/libbehaviortree_cpp.so/' in p]
        need(len(matches)==1,'Missing/ambiguous private core ELF')
        elf=z.read(matches[0])
    need(hashlib.sha256(elf).hexdigest()==BT_SHA,'Original ELF digest mismatch')
    for addr,expected in WORDS.items():
        need(word_at(elf,addr)==expected,'Native word changed at %#x'%addr)
    for addr,expected in CALLS.items():
        need(target(addr,word_at(elf,addr),'bl')==expected,
             'Native direct call changed at %#x'%addr)
    need(target(0x733dc,word_at(elf,0x733dc),'cbz')==0x73874,
         'realpath null-result branch changed')

    received=Path(resolver).read_bytes()
    need(hashlib.sha256(received).hexdigest()==COLLECTION_SHA,
         'Uploaded resolver collection digest mismatch')
    with zipfile.ZipFile(io.BytesIO(received)) as z:
        need(z.testzip() is None,'Resolver CRC mismatch')
        members=z.namelist()
        need(len(members)==2 and len(set(members))==2 and
             all(not n.startswith('/') and '..' not in PurePosixPath(n).parts
                 and '\\' not in n for n in members),
             'Unsafe or unexpected collection entries')
        a=[m for m in members if m.endswith('/inventory.SANITIZED.json')]
        b=[m for m in members if m.endswith('/manifest.PRIVATE.json')]
        need(len(a)==len(b)==1,'Missing collection metadata')
        inv=json.loads(z.read(a[0]))
        man=json.loads(z.read(b[0]))
    need(inv.get('schema')=='X40_R2416_V208_SANITIZED_INVENTORY_V1' and
         man.get('schema')=='X40_R2416_V208_PRIVATE_TARGETED_V1',
         'Unexpected schema')
    need(inv.get('prior_checksum_entries_checked')==
         man.get('prior_checksum_entries_checked')==18,'Prior checksum count changed')
    need(inv.get('remote_path_candidates')==
         man.get('remote_path_candidates')==0,'Unexpected remote inventory')
    need(all(inv.get(k)==0 for k in
         ('new_file_count','new_plugin_ELFs','new_named_subtree_resources')) and
         man.get('saved')==[],'New resource present')
    skipped=man.get('skipped')
    need(isinstance(skipped,list) and len(skipped)==6 and
         all(x.get('reason')=='byte-identical-to-prior-collection'
             for x in skipped),'Duplicate evidence changed')
    return len(WORDS),len(CALLS)+1,len(skipped)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    p.add_argument('--resolver-zip',required=True)
    args=p.parse_args()
    try:
        print('X40_R2416_V209_REPO_EMPTY_RESOLVER_REALPATH_PASS',
              *verify(args.prior_zip,args.resolver_zip))
        print('No new collector files. Actual AiStainMop resolution and reclean remain unknown.')
    except (OSError,ValueError,IndexError,KeyError,TypeError,struct.error,
            zipfile.BadZipFile) as exc:
        raise SystemExit('X40_R2416_V209_REPO_FAIL: '+str(exc))
