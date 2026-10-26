#!/usr/bin/env python3
"""v193 repo compact original R2416 AArch64 strict adjacent key-reference audit.
For full mutation-tested v184-v193 verification use the checksum-pinned ZIP.
No robot access. Original copyrighted ELF is supplied by the user locally.
"""
import argparse,hashlib,json,struct
from pathlib import Path
SHA="fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e"
KEYS={
 "next_dynamic_obstacles_point":(0x1007d08,[0xaeee4c,0xb14e2c]),
 "original_dynamic_obstacles_point":(0x1007ce0,[0xaee92c,0xaf0268,0xaf1be4,0xaf231c,0xf82920,0xf8be54])
}
CALLS={0xaf038c:0x445870,0xaf1d0c:0x445870,0xaf248c:0x445870,0xaf24e4:0x44f5e0,0xaf250c:0x4526d0}
class Refusal(ValueError): pass
def require(value,reason):
 if not value: raise Refusal(reason)
def signed(value,bits):
 return value-(1<<bits) if value&(1<<(bits-1)) else value
def adrp_add(a,b,pc):
 if a&0x9f000000!=0x90000000 or b&0xff000000!=0x91000000 or (a&31)!=((b>>5)&31):return None
 imm=(((a>>5)&0x7ffff)<<2)|((a>>29)&3)
 return (pc&~4095)+(signed(imm,21)<<12)+(((b>>10)&0xfff)<<(12 if b&(1<<22) else 0))
def bl_target(word,pc):
 require(word>>26==0b100101,"expected direct AArch64 BL")
 return pc+(signed(word&((1<<26)-1),26)<<2)
class ELF:
 def __init__(self,data):
  self.data=data
  require(data[:6]==bytes([127,69,76,70,2,1]) and struct.unpack_from("<H",data,18)[0]==183,"expected ELF64 little-endian AArch64")
  shoff=struct.unpack_from("<Q",data,40)[0]
  stride,count,names=struct.unpack_from("<HHH",data,58)
  require(64<=stride<=256 and 1<count<256 and names<count and shoff+stride*count<=len(data),"bad ELF section bounds")
  self.sections=[]
  for i in range(count):
   _,kind,flags,va,off,length,*_=struct.unpack_from("<IIQQQQIIQQ",data,shoff+stride*i)
   if kind!=8:
    require(off<=len(data) and length<=len(data)-off,"section outside ELF")
    self.sections.append((flags,va,off,length))
 def at(self,va,size):
  for flags,base,off,length in self.sections:
   if base<=va and va+size<=base+length:return self.data[off+va-base:off+va-base+size]
  raise Refusal("unmapped VA")
 def word(self,va):
  require(any(flags&4 and base<=va and va+4<=base+length for flags,base,off,length in self.sections),"nonexec VA")
  return struct.unpack("<I",self.at(va,4))[0]
 def xrefs(self,addresses):
  result={v:[] for v in addresses}
  for flags,base,off,length in self.sections:
   if not flags&4:continue
   for i in range(0,length-7,4):
    a,b=struct.unpack_from("<II",self.data,off+i)
    if a&0x9f000000!=0x90000000:continue
    va=adrp_add(a,b,base+i)
    if va in result:result[va].append(base+i)
  return result
def verify(data):
 require(hashlib.sha256(data).hexdigest()==SHA,"original firmware SHA mismatch")
 elf=ELF(data)
 actual=elf.xrefs([row[0] for row in KEYS.values()])
 for key,(va,sites) in KEYS.items():
  require(elf.at(va,len(key)+1)==key.encode()+bytes([0]),"literal changed: "+key)
  require(actual[va]==sites,"reference census changed: "+key)
 for call,dest in CALLS.items():
  require(bl_target(elf.word(call),call)==dest,"named direct call changed: "+hex(call))
 require(elf.word(0xb14e50)==0xf9401842 and elf.word(0xb14e54)==0xd63f0040,"PresetBlackboard virtual slot changed")
 require(elf.word(0xaeee78)==0xf9401063 and elf.word(0xaeee90)==0xd63f0060,"next-point setter-compatible operation changed")
 return {"schema":"X40_R2416_V193_REPO_COMPACT_CHECK_V1","originalSHA256":SHA,
 "adjacentReferenceSites":{key:[hex(a) for a in sites] for key,(addr,sites) in KEYS.items()},
 "compiledHeadingMathCallsVerified":True,"presetVirtualSlotExactMeaningProven":False,
 "newCleaningTaskOrAutonomousRecleanProven":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--route-elf",type=Path,required=True)
 a=p.parse_args()
 try:print(json.dumps(verify(a.route_elf.read_bytes()),indent=2))
 except (Refusal,OSError,struct.error) as exc:raise SystemExit("X40_V193_REFUSED: "+str(exc))
if __name__=="__main__":main()
