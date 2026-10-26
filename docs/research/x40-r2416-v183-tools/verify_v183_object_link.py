#!/usr/bin/env python3
"""Standalone read-only v183 instruction and object-path checksum verification (Python stdlib).
The full v182-v183 typed subscriber/relocation and mutation verifier is in the companion ZIP.
"""
import argparse,hashlib,json,struct
from pathlib import Path
SHA={
 'node_laser_transfer.so':'16b487f486fb34d8fe85fb6e383243100657e0769d6df823aa13c34643644856',
 'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'
}
WORDS={
 'node_laser_transfer.so':{
 0x1306bc:0xd292fe00,0x1306c8:0x97ff0a4e,0x1306dc:0x97fef711,0x1306e4:0xf909c274,
 0x3b8380:0xaa1c03e0,0x3b8384:0x97f4ef17,
 0x3ac890:0x91402015,0x3ac910:0xd2821600,0x3ac928:0x97f519b6,0x3ac93c:0x97f52485,0x3ac948:0xf904d2b3,
 0x112390:0xf949c000,0x112394:0x91402000,0x112398:0xf944d000,0x11239c:0xb9400021,0x1123a0:0x913f4000,0x1123a4:0x889ffc01,
 0x3a5254:0x91402003,0x3a5268:0xf944d074,
 0x1e3008:0xaa1503e0,0x1e300c:0x97fc3385,0x1e9ab0:0xaa1603e0,0x1e9ab4:0x97fc0f77,
 0x1db720:0x913f4004,0x1db724:0x88dffc81,0x1db768:0x6b02007f,0x1db788:0x889ffc9f,
 0x1e9b14:0x52800020,0x1e9b18:0x3917a6c0,
 },
 'liblethe_route_nodes.so':{0xc267e0:0xf0001f5c,0xc26bec:0xb9807a62,0xc26bfc:0xd63f0080}
}
CALLS={0x1306dc:0xee320,0x3b8384:0xf3fe0,0x3ac93c:0xf5b50,0x1e300c:0xefe20,0x1e9ab4:0xed890}
class Refusal(ValueError):pass
def require(ok,msg):
 if not ok:raise Refusal(msg)
def native_words(data):
 require(data[:6]==bytes([127,69,76,70,2,1]) and struct.unpack_from('<H',data,18)[0]==183,'not ELF64 AArch64')
 off=struct.unpack_from('<Q',data,40)[0]
 entsize,n,idx=struct.unpack_from('<HHH',data,58)
 require(entsize>=64 and 1<n<100 and idx<n and off+n*entsize<=len(data),'bad section table')
 sections=[]
 for i in range(n):
  p=off+i*entsize
  _name,kind,flags,va,fo,size,*_=struct.unpack_from('<IIQQQQIIQQ',data,p)
  if kind!=8:
   require(fo+size<=len(data),'truncated section')
   sections.append((va,fo,size,bool(flags&4)))
 def word(va):
  for v,f,n,exe in sections:
   if exe and v<=va and va+4<=v+n:return struct.unpack_from('<I',data,f+va-v)[0]
  raise Refusal('instruction VA not executable: '+hex(va))
 return word
def branch_target(word,src):
 require(word>>26==0b100101,'not BL: '+hex(src))
 n=word&((1<<26)-1)
 if n&(1<<25):n-=1<<26
 return src+4*n
def check(paths):
 checked=0
 for name,path in paths.items():
  data=Path(path).read_bytes()
  require(hashlib.sha256(data).hexdigest()==SHA[name],name+' hash mismatch')
  word=native_words(data)
  for va,expected in WORDS[name].items():
   require(word(va)==expected,f'{name} instruction changed: {va:#x}')
   checked+=1
  if name=='node_laser_transfer.so':
   for src,dst in CALLS.items():
    require(branch_target(word(src),src)==dst,f'BL destination changed: {src:#x}')
 return {'schema':'X40_R2416_V183_REPO_COMPACT_CHECK_V1','checkedInstructionSites':checked,
 'checkedDirectCalls':len(CALLS),'originalHashesVerified':True,
 'compiledPerceptionObjectChainVerified':True,'autonomousFloorRecleanProven':False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--laser-elf',type=Path,required=True)
 p.add_argument('--route-elf',type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(check({'node_laser_transfer.so':a.laser_elf,'liblethe_route_nodes.so':a.route_elf}),indent=2))
if __name__=='__main__':
 try:main()
 except (Refusal,ValueError,OSError,struct.error) as exc:raise SystemExit('V183_REFUSED: '+str(exc))
