#!/usr/bin/env python3
"""Standalone bounded X40 R2416 original native production root and debug census.

Python 3 stdlib only. Reads owner-private original ZIP; no robot communication,
ELF execution, filesystem overwrite, or private data output. The separate
v220 ZIP supplies the full v197-v220 original-firmware regression chain.
"""
import argparse
import hashlib
import struct
import zipfile

SHA='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
WORDS={
 0x3552c0:0xf9401802,0x3552c8:0x97fc803e,0x3552d8:0xf907a401,
 0x3e0260:0x97fa5b84,0x3e0270:0x97fa56e8,0x3e1028:0x97fa4f32,
 0x3e1390:0xf947a680,0x3e1394:0xf9400001,0x3e1398:0xf9400c21,
 0x3e139c:0xd63f0020,0x3e13a0:0x12001c19,
 0x315ed0:0xf9400400,0x315ed8:0xf9400c21,0x315ee0:0xd61f0200,
 0x3e1844:0x97fa618b,0x3e1fcc:0x97fa4c89
}
SITES={
 0x274cf0:[0x3e1028],
 0x277070:[0x3e0260],
 0x275e10:[0x3e0270],
 0x27afd0:[0x51ad68,0x51b478,0x51ba28,0x51be54,0x51cc6c,
           0x6e26a8,0x6e2ce0,0x6e3340,0x6e4894,0x6e5358]
}
def need(ok,message):
 if not ok:raise ValueError(message)
def va_data(raw,addr,size):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
      'Not original AArch64 ELF64LE')
 ph=struct.unpack_from('<Q',raw,32)[0]
 step,count=struct.unpack_from('<HH',raw,54)
 need(step>=56 and 0<count<=100 and ph+step*count<=len(raw),'Malformed ELF headers')
 for i in range(count):
  typ,_,off,va,_,length,_,_=struct.unpack_from('<IIQQQQQQ',raw,ph+i*step)
  if typ==1 and va<=addr and addr+size<=va+length:
   offset=off+addr-va
   need(offset+size<=len(raw),'ELF segment truncated')
   return raw[offset:offset+size]
 raise ValueError('Original native address is unmapped')
def audit(path):
 with zipfile.ZipFile(path) as z:
  matches=[member for member in z.namelist() if '/files/node_lethe.so/' in member]
  need(len(matches)==1,'Original host ELF missing or ambiguous')
  raw=z.read(matches[0])
 need(hashlib.sha256(raw).hexdigest()==SHA,'Original host SHA-256 changed')
 for at,opcode in WORDS.items():
  need(struct.unpack('<I',va_data(raw,at,4))[0]==opcode,
       'Native instruction changed at '+hex(at))
 lo,hi=0x2a0000,0x9c0000
 blob=va_data(raw,lo,hi-lo)
 found={target:[] for target in SITES}
 for (opcode,),at in zip(struct.iter_unpack('<I',blob),range(lo,hi,4)):
  if opcode&0xfc000000!=0x94000000:continue
  offset=opcode&0x3ffffff
  if offset&0x2000000:offset-=0x4000000
  dest=at+4*offset
  if dest in found:found[dest].append(at)
 need(found==SITES,'Original production AI and debug direct-call sites changed')
 return len(WORDS),3,len(SITES[0x27afd0])
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--prior-zip',required=True)
 args=parser.parse_args()
 try:
  print('X40_R2416_V220_REPO_PRODUCTION_ROOT_PASS',*audit(args.prior_zip))
  print('Compiled production tick; no AI-stain-triggered new cleaning task proven.')
 except (OSError,ValueError,IndexError,TypeError,struct.error,zipfile.BadZipFile) as exc:
  raise SystemExit('X40_R2416_V220_REPO_FAIL: '+str(exc))
