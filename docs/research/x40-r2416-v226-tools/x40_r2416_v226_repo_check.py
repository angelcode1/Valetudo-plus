#!/usr/bin/env python3
"""SHA-pinned original R2416 typed-MCU direct call/near-immediate census.

Python 3 standard library only; reads owner PRIVATE collector ZIP in memory.
Never executes firmware, contacts robot, sends commands, or prints private data.
"""
import argparse,hashlib,struct,zipfile
SHA='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
PUB=0x275b10
SITES=(0x648c90,0x648e7c,0x653938,0x655884,0x6558a0,0x655954,0x655a88,
 0x6586cc,0x65ab60,0x65ada8,0x79b214,0x7a094c,0x7a1c38,0x7a1e8c,
 0x7a2870,0x7a2928,0x7a2a08,0x7a2b1c,0x7a3d48,0x7a4868,0x7a6934,
 0x7a6a44,0x7a6b64,0x7a6c3c,0x7a8ec4,0x7acb4c,0x7acc34,0x7b88d8,
 0x7b8c18,0x834bc0,0x834e3c,0x835938)
WORDS={0x3cd778:0xf943fc84,0x3cd7c8:0x97fa93b6,
 0x3d910c:0xb9400020,0x3d911c:0x39401035,
 0x3d9120:0x7100681f,0x3d9128:0x71006c1f,
 0x3d9130:0x7100901f,0x3d9138:0x7100601f,
 0x7b88c4:0x52800403,0x7b88cc:0xb900c3e3,
 0x7b88d0:0x390313fa,0x7b88d8:0x97eaf48e,
 0x7b8bfc:0x52800426,0x7b8c10:0xb900c3e6,
 0x7b8c14:0x390313e4,0x7b8c18:0x97eaf3be}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def check(path):
 with zipfile.ZipFile(path) as z:
  members=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
  need(len(members)==1,'Missing or ambiguous original ELF')
  b=z.read(members[0])
 need(hashlib.sha256(b).hexdigest()==SHA,'Original host SHA mismatch')
 need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,
      'Expected AArch64 ELF64LE')
 for at,word in WORDS.items():
  need(struct.unpack_from('<I',b,at)[0]==word,'Original native opcode changed')
 def target(at,op):
  d=op&0x3ffffff
  if d&0x2000000:d-=0x4000000
  return at+4*d
 hits=[]
 for at in range(0x2a0000,0x9c0000,4):
  ins=struct.unpack_from('<I',b,at)[0]
  if ins&0xfc000000==0x94000000 and target(at,ins)==PUB:hits.append(at)
 need(hits==list(SITES),'Original typed MCU publisher call census changed')
 mov=[]
 for site in SITES:
  for at in range(site-144,site,4):
   ins=struct.unpack_from('<I',b,at)[0]
   if ins&0x7f800000==0x52800000 and ((ins>>5)&0xffff) in (32,33):
    mov.append((site,at,(ins>>5)&0xffff))
 need(mov==[(0x7b88d8,0x7b88c4,32),(0x7b8c18,0x7b8bfc,33)],
      'Restricted 144-byte W-MOVZ immediate census changed')
 return len(WORDS),len(SITES),len(mov),4
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True);a=p.parse_args()
 try:
  print('X40_R2416_V226_REPO_MCU_CENSUS_PASS',*check(a.prior_zip))
  print('Numeric command meaning and any actual wash/reclean remain unproven.')
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V226_REPO_FAIL: '+str(e))
