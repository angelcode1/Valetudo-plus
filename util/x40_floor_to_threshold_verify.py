#!/usr/bin/env python3
"""Verify X40 R2416 floor turbidity gate -> threshold call, offline/read-only."""
import argparse
import hashlib
import struct
from pathlib import Path

PIN='da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c'
WORDS={
 0x255d10:0x51000421,0x255d14:0xb9067661,0x255d20:0xb9467a60,
 0x255da8:0xb94077e0,0x255dac:0x7100001f,0x255db0:0x7a40cb60,
 0x255db4:0x54fffc01,0x255e30:0xf9401442,0x255e34:0xd63f0040,
 0x255e3c:0x54000220,0x255ea4:0xf000075a,0x255ea8:0x911e8341,
 0x255fbc:0xf940ffe0,0x256048:0xb9468660,0x25604c:0x340000c0,
 0x256050:0x900006a1,0x256054:0x91244021,0x256058:0xaa1c03e0,
 0x25605c:0x97f9c095,0x256060:0x35002d20,0x256604:0xb9468661,
 0x256608:0xaa1303e0,0x25660c:0x52800022,0x256610:0x97f9cc1c,
 0x256614:0xb9058e60,0x256618:0xb9464a60,0x25661c:0x7100241f,
 0x256620:0x540001ed,0x25665c:0xaa1303e0,0x256660:0x97f9c4c4}
LITERALS={
 0x3407a0:b'TubidityState\x00',0x32a910:b'precleaning\x00',
 0x340bf8:b'turbidity_reclean_flag\x00',
 0x340c10:b'robot_oversea_avoid_turbidity\x00'}
class ELF:
 def __init__(self,path):
  self.b=Path(path).read_bytes()
  if hashlib.sha256(self.b).hexdigest()!=PIN:raise ValueError('SHA256 mismatch')
  if self.b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',self.b,18)[0]!=183:
   raise ValueError('not AArch64 ELF64')
  off=struct.unpack_from('<Q',self.b,32)[0]
  step=struct.unpack_from('<H',self.b,54)[0]
  self.loads=[]
  for i in range(struct.unpack_from('<H',self.b,56)[0]):
   p=off+i*step
   if struct.unpack_from('<I',self.b,p)[0]==1:
    f,v,_,s=struct.unpack_from('<QQQQ',self.b,p+8)
    self.loads.append((v,v+s,f))
 def at(self,a,n):
  for lo,hi,off in self.loads:
   if lo<=a and a+n<=hi:return self.b[off+a-lo:off+a-lo+n]
  raise ValueError('unmapped address '+hex(a))
 def w(self,a):return struct.unpack('<I',self.at(a,4))[0]
def signed(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def target(w,pc,kind):
 if kind=='BL':
  if w>>26!=0b100101:raise ValueError('BL opcode')
  return pc+4*signed(w&0x3ffffff,26)
 if kind=='CBNZ':
  if w&0x7f000000!=0x35000000:raise ValueError('CBNZ opcode')
 elif kind=='B.cond':
  if w&0xff000010!=0x54000000:raise ValueError('B.cond opcode')
 else:raise ValueError('unknown branch kind')
 return pc+4*signed((w>>5)&0x7ffff,19)
BRANCHES=[
 (0x255e3c,'B.cond',0x255e80),
 (0x256060,'CBNZ',0x256604),
 (0x256620,'B.cond',0x25665c),
 (0x256610,'BL',0xc9680),
 (0x256660,'BL',0xc7970)]
def verify(path):
 e=ELF(path)
 for a,w in WORDS.items():
  if e.w(a)!=w:raise ValueError('instruction mismatch '+hex(a))
 for a,s in LITERALS.items():
  if e.at(a,len(s))!=s:raise ValueError('literal mismatch '+hex(a))
 for a,kind,dst in BRANCHES:
  if target(e.w(a),a,kind)!=dst:raise ValueError('branch mismatch '+hex(a))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--elf',help='original, private liblethe_tactics_tree.so')
 p.add_argument('--self-test',action='store_true')
 a=p.parse_args()
 if a.self_test:
  assert len(WORDS)==30 and len(LITERALS)==4 and len(BRANCHES)==5
  assert target(0x35002d20,0x256060,'CBNZ')==0x256604
  print('X40_FLOOR_TO_THRESHOLD_SELFTEST_PASS synthetic_only=true no_device_access=true')
  return
 if not a.elf:p.error('provide --elf')
 try:verify(a.elf)
 except (ValueError,OSError) as err:p.exit(1,'X40_FLOOR_TO_THRESHOLD_REFUSED '+str(err)+'\n')
 print('X40_FLOOR_TO_THRESHOLD_ELF_PASS full_sha256=true opcodes=30 literals=4 branches=5 no_device_access=true')
if __name__=='__main__':main()
