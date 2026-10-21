#!/usr/bin/env python3
"""Offline-only R2416 BT turbidity branch verification. No device access."""
import argparse, hashlib, struct
from pathlib import Path
PIN={
'tree':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
'tactics':'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
'bt':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94'}
BRANCHES=[(0x1da0b0,0x1da0c4,0x1da0e0,0x1da114,0x1da148,0x1da15c),
(0x1f6518,0x1f652c,0x1f6548,0x1f657c,0x1f65b0,0x1f65c4),
(0x238128,0x23813c,0x238158,0x23818c,0x2381c0,0x2381d4)]
class ELF:
 def __init__(self,path,pin):
  self.b=Path(path).read_bytes()
  if hashlib.sha256(self.b).hexdigest()!=pin:raise ValueError('SHA256 mismatch: '+str(path))
  if self.b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',self.b,18)[0]!=183:raise ValueError('not AArch64 ELF64')
  self.segs=[]
  off=struct.unpack_from('<Q',self.b,32)[0];step=struct.unpack_from('<H',self.b,54)[0]
  for i in range(struct.unpack_from('<H',self.b,56)[0]):
   p=off+i*step
   if struct.unpack_from('<I',self.b,p)[0]==1:
    fo,va,_,sz=struct.unpack_from('<QQQQ',self.b,p+8)
    self.segs.append((va,va+sz,fo))
 def at(self,addr,n):
  for a,b,o in self.segs:
   if a<=addr and addr+n<=b:return self.b[o+addr-a:o+addr-a+n]
  raise ValueError('unmapped '+hex(addr))
 def w(self,a):return struct.unpack('<I',self.at(a,4))[0]
def call(e,pc,target):
 w=e.w(pc)
 if w&0xfc000000!=0x94000000:raise ValueError('expected BL '+hex(pc))
 imm=w&0x3ffffff
 if imm&(1<<25):imm-=1<<26
 if pc+4*imm!=target:raise ValueError('wrong target '+hex(pc))
def verify(tree,tactics,bt):
 t=ELF(tree,PIN['tree']);p=ELF(tactics,PIN['tactics']);b=ELF(bt,PIN['bt'])
 if t.at(0x56935f,11)!=b'IfThenElse\0' or t.at(0x56b4c2,19)!=b'IsTurbidityReclean\0':
  raise ValueError('BT node literals')
 for parent,open_,condition,set_,erase,close in BRANCHES:
  for x in (parent,condition,set_,erase):call(t,x,0x1c6620)
  call(t,open_,0x1c6730);call(t,close,0x1c6810)
  for x in (parent+12,condition+12,set_+12,erase+12):call(t,x,0x1c6900)
 if p.at(0x33b2f8,16)!=b'enable_turbidity' or p.at(0x32a698,20)!=b'smart_host_clean_set':
  raise ValueError('predicate key literals')
 for at in (0x1fd2b8,0x1fd344):call(p,at,0xc60b0)
 for slot,blr in ((0x1fd314,0x1fd318),(0x1fd37c,0x1fd380)):
  if p.w(slot)&0xffc00000!=0xf9400000 or (p.w(slot)>>10)&4095!=5:raise ValueError('contains slot')
  if p.w(blr)&0xfffffc1f!=0xd63f0000:raise ValueError('contains BLR')
 if p.w(0x1fd3dc)&0xffc00000!=0xf9400000 or (p.w(0x1fd3dc)>>10)&4095!=2:raise ValueError('getter')
 for addr,w in ((0x1fd464,0xeb010017),(0x1fd4bc,0xeb1402bf),(0x1fd4c0,0x1a9f17f3),
 (0x1fd4c4,0x11000a73)): 
  if p.w(addr)!=w:raise ValueError('predicate status '+hex(addr))
 for addr,w in ((0x94734,0x71000a7f),(0x948a4,0x52800034),(0x94784,0x71000e7f),(0x9479c,0x52800054)):
  if b.w(addr)!=w:raise ValueError('IfThenElse status '+hex(addr))
def main():
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--self-test',action='store_true')
 for x in PIN:a.add_argument('--'+x)
 v=a.parse_args()
 if v.self_test:
  assert len(BRANCHES)==3 and all(len(x)==6 for x in BRANCHES)
  print('X40_TURBIDITY_BRANCH_SELFTEST_PASS synthetic_only=true');return
 if not all(getattr(v,x) for x in PIN):a.error('supply --tree --tactics --bt')
 try:verify(v.tree,v.tactics,v.bt)
 except (ValueError,OSError) as e:raise SystemExit('X40_TURBIDITY_BRANCH_REFUSED '+str(e))
 print('X40_TURBIDITY_BRANCH_ELF_PASS sha256_all_three=true conditions=3 no_device_access=true')
if __name__=='__main__':main()
