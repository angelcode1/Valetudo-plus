#!/usr/bin/env python3
"""Small standalone, original-SHA-pinned, read-only v204 cache-flag checker.

This verifies only a bounded subset. Full v197-v204 replay is in the ZIP kit.
"""
import argparse
import hashlib
import struct
import zipfile

ORIGINAL_SHA='665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94'
WORDS={
 0x759d0:0x3400017c,0x759f8:0x54004fc0,0x75a18:0x54001e00,
 0x75ac4:0xf94022c0,0x75ac8:0xb4000580,0x75ad0:0xa9027ea0,
 0x75b78:0x52800020,0x75b7c:0xb90087e0,0x75b84:0xb5001300,
 0x75bbc:0xb94087e0,0x75bc0:0x34fff8a0,0x75c90:0x97fffdb0,
 0x75c98:0xf90022b6,0x75ddc:0xb90087ff,0x75de0:0xb4ffed40,
 0x764b0:0x97fffba8,0x764b8:0xf90022ff,0x764bc:0x17fffd86,
 0x74e94:0xf9401417,0x74f4c:0x97ff12c9,
}
EDGES={
 (0x759d0,'cbz'):0x759fc,(0x759f8,'cond'):0x763f0,
 (0x75a18,'cond'):0x75dd8,(0x75ac8,'cbz'):0x75b78,
 (0x75b84,'cbnz'):0x75de4,(0x75bc0,'cbz'):0x75ad4,
 (0x75de0,'cbz'):0x75b88,(0x75c90,'bl'):0x75350,
 (0x764b0,'bl'):0x75350,(0x764bc,'b'):0x75ad4,
}
def require(ok,message):
 if not ok: raise ValueError(message)
def va_word(raw,addr):
 require(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,'Not AArch64 ELF64LE')
 po=struct.unpack_from('<Q',raw,32)[0]
 size,n=struct.unpack_from('<HH',raw,54)
 require(size>=56 and n<=100 and po+size*n<=len(raw),'Malformed program headers')
 for i in range(n):
  typ,_,off,va,_,length,_,_=struct.unpack_from('<IIQQQQQQ',raw,po+i*size)
  if typ==1 and va<=addr and addr+4<=va+length:
   o=off+addr-va
   require(o+4<=len(raw),'Truncated ELF segment')
   return struct.unpack_from('<I',raw,o)[0]
 raise ValueError('Unmapped native instruction')
def destination(addr,opcode,kind):
 if kind in ('bl','b'):
  require(opcode&0xfc000000==(0x94000000 if kind=='bl' else 0x14000000),'Wrong B/BL instruction')
  imm=opcode&0x3ffffff;bits=26
 elif kind=='cond':
  require(opcode&0xff000010==0x54000000,'Wrong B.cond instruction')
  imm=(opcode>>5)&0x7ffff;bits=19
 else:
  require(opcode&0x7e000000==0x34000000 and ((opcode>>24)&1)==(kind=='cbnz'),'Wrong CBZ/CBNZ')
  imm=(opcode>>5)&0x7ffff;bits=19
 if imm&(1<<(bits-1)):imm-=1<<bits
 return addr+imm*4
def verify(raw):
 require(hashlib.sha256(raw).hexdigest()==ORIGINAL_SHA,'Original libbehaviortree_cpp SHA mismatch')
 for va,expected in WORDS.items():
  require(va_word(raw,va)==expected,'Native word changed at %#x'%va)
 for (va,kind),target in EDGES.items():
  require(destination(va,va_word(raw,va),kind)==target,'Native branch changed at %#x'%va)
 return len(WORDS),len(EDGES)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 a=p.parse_args()
 with zipfile.ZipFile(a.prior_zip) as z:
  items=[n for n in z.namelist() if '/files/libbehaviortree_cpp.so/' in n]
  require(len(items)==1,'Original behavior-tree ELF not uniquely present')
  counts=verify(z.read(items[0]))
 print('X40_R2416_V204_REPO_CACHE_FLAG_STATIC_PASS',*counts)
 print('Compiled conditions only; no runtime cache occupancy, dangling pointer or physical reclean established.')
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as exc:
  raise SystemExit('X40_R2416_V204_REPO_FAIL: '+str(exc))
