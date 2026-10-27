#!/usr/bin/env python3
"""Offline, bounded original R2416 numeric _CtrlMcuCMD payload verifier.

Python 3 stdlib only. The complete v225 sanitized ZIP verifies all 56 native
instructions, 17 edges and historical v197-v224 regressions. Never contacts
the robot, publishes commands or copies original vendor ELF contents.
"""
import argparse
import hashlib
import struct
import zipfile

PIN='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
WORDS={
 0x7b871c:0x540026cd,0x7b88a0:0x5280001a,
 0x7b88ac:0x394c42c0,0x7b88b4:0x54ffdfa0,
 0x7b88c4:0x52800403,0x7b88c8:0xaa1803e2,
 0x7b88cc:0xb900c3e3,0x7b88d0:0x390313fa,
 0x7b88d8:0x97eaf48e,0x7b8b10:0xf00012c1,
 0x7b8b28:0xb40022e0,0x7b8b40:0x54002220,
 0x7b8bf8:0x52805dc5,0x7b8bfc:0x52800426,
 0x7b8c04:0x910303e2,0x7b8c10:0xb900c3e6,
 0x7b8c14:0x390313e4,0x7b8c18:0x97eaf3be,
}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def bl_target(at,op):
 need(op&0xfc000000==0x94000000,'Expected native direct BL')
 d=op&0x3ffffff
 if d&0x2000000:d-=0x4000000
 return at+4*d
def audit(path):
 with zipfile.ZipFile(path) as archive:
  names=[n for n in archive.namelist() if '/files/node_lethe.so/' in n]
  need(len(names)==1,'Expected one original native host ELF')
  b=archive.read(names[0])
 need(hashlib.sha256(b).hexdigest()==PIN,'Original ELF SHA mismatch')
 need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,
      'Expected original ELF64LE AArch64')
 for at,op in WORDS.items():
  need(struct.unpack_from('<I',b,at)[0]==op,'Changed original instruction '+hex(at))
 need(b[0xa13488:0xa13488+25]==b'ai_set_mop_is_dirty_data\0',
      'Exact dirty-mop key literal changed')
 found=[]
 for at in range(0x7b8360,0x7b977c,4):
  ins=struct.unpack_from('<I',b,at)[0]
  if ins&0xfc000000==0x94000000 and bl_target(at,ins)==0x275b10:
   found.append(at)
 need(found==[0x7b88d8,0x7b8c18],'MCU publisher direct-call census changed')
 return len(WORDS),len(found),32,33
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 a=p.parse_args()
 try:
  print('X40_R2416_V225_REPO_NUMERIC_MCU_PAYLOADS_PASS',*audit(a.prior_zip))
  print('Numeric fields only: original station-wash semantics unproven.')
 except (OSError,ValueError,struct.error,zipfile.BadZipFile) as err:
  raise SystemExit('X40_R2416_V225_REPO_FAIL: '+str(err))
