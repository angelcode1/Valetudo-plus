#!/usr/bin/env python3
"""Bounded offline v215 original R2416 reuse placeholder/fallback checker.

Uses inherited v213 repo checker for exact 199 registration names. Only original
PRIVATE collector ZIP is read; no robot access, private output or dependencies.
"""
import argparse,hashlib,struct,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'x40-r2416-v213-tools'))
from x40_r2416_v213_repo_check import check as verify_tree_registrations
CORE_SHA='665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94'
SELECTED={
 0x75894:0x54002061,0x75cfc:0x97ff0cc1,0x75d08:0x1a9f17fc,
 0x759d0:0x3400017c,0x759f8:0x54004fc0,0x764b0:0x97fffba8,
 0x764b8:0xf90022ff,0x764bc:0x17fffd86,0x75a18:0x54001e00,
 0x75ac8:0xb4000580,0x75b80:0xf94077e0,0x75b84:0xb5001300,
 0x75ddc:0xb90087ff,0x75dfc:0xb4001cfc,0x75e5c:0x540019e0,
 0x761f4:0xd2800322,0x761f8:0x97ff0ba2,0x7624c:0x17fffe4f,
 0x75ba4:0xaa1803e1,0x75bb0:0x97ff0dac}
EDGES={(0x75894,'cond'):0x75ca0,(0x759d0,'cbz'):0x759fc,
 (0x759f8,'cond'):0x763f0,(0x764b0,'bl'):0x75350,
 (0x764bc,'b'):0x75ad4,(0x75a18,'cond'):0x75dd8,
 (0x75ac8,'cbz'):0x75b78,(0x75b84,'cbnz'):0x75de4,
 (0x75dfc,'cbz'):0x76198,(0x75e5c,'cond'):0x76198,
 (0x7624c,'b'):0x75b88,(0x75bb0,'bl'):0x39260}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read_va(raw,addr,n):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,'Expected AArch64 ELF64LE')
 off=struct.unpack_from('<Q',raw,32)[0];step,count=struct.unpack_from('<HH',raw,54)
 need(step>=56 and 0<count<100 and off+step*count<=len(raw),'Malformed PT_LOAD headers')
 for i in range(count):
  typ,_,pos,va,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,off+step*i)
  if typ==1 and va<=addr and addr+n<=va+size:
   at=pos+addr-va;need(at+n<=len(raw),'Truncated ELF');return raw[at:at+n]
 raise ValueError('Unmapped native address')
def word(raw,va):return struct.unpack('<I',read_va(raw,va,4))[0]
def target(at,w,kind):
 if kind in ('b','bl'):
  need((w&0xfc000000)==(0x14000000 if kind=='b' else 0x94000000),'Wrong B/BL opcode')
  value,bits=w&0x3ffffff,26
 else:
  if kind=='cond':need(w&0xff000010==0x54000000,'Wrong B.cond opcode')
  else:need(w&0x7e000000==0x34000000 and ((w>>24)&1)==(kind=='cbnz'),'Wrong CBZ/CBNZ opcode')
  value,bits=(w>>5)&0x7ffff,19
 if value&(1<<(bits-1)):value-=1<<bits
 return at+4*value
def audit(prior):
 with zipfile.ZipFile(prior) as z:
  data={}
  for name in ('liblethe_tree.so','libbehaviortree_cpp.so'):
   paths=[p for p in z.namelist() if '/files/'+name+'/' in p]
   need(len(paths)==1,'Missing or ambiguous original ELF '+name)
   data[name]=z.read(paths[0])
 core=data['libbehaviortree_cpp.so']
 need(hashlib.sha256(core).hexdigest()==CORE_SHA,'Original BT core SHA mismatch')
 regs=verify_tree_registrations(data['liblethe_tree.so'])
 need(regs==(199,199),'Original native registration census changed')
 for va,expected in SELECTED.items():
  need(word(core,va)==expected,'Native instruction changed at %#x'%va)
 for (va,kind),expected in EDGES.items():
  need(target(va,word(core,va),kind)==expected,'Native control edge changed at %#x'%va)
 need(read_va(core,0xad908,6)==b'reuse\0','reuse marker changed')
 need(read_va(core,0xad930,26)==b' is not a registered tree\0','missing-builder diagnostic changed')
 return len(SELECTED),len(EDGES),regs[0]
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prior-zip',required=True);a=p.parse_args()
 try:
  print('X40_R2416_V215_REPO_REUSE_FALLBACK_PASS',*audit(a.prior_zip))
  print('Static conditional paths; no runtime AiStainMop builder/file resolution proven.')
 except (OSError,ValueError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V215_REPO_FAIL: '+str(e))
