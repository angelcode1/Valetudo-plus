#!/usr/bin/env python3
"""Compact standalone R2416 v189 verifier: original ELF, literal, PLT/GOT, direct BL."""
import argparse, hashlib, json, struct
from pathlib import Path
SHA='fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'
PLTS={'end':(0x4435b0,0x1241358,[0x5d2ec4,0xad9fd0]),
      'complete':(0x4468b0,0x1242cd8,[0xb6c60c,0xb81e30,0xb86700]),
      'update_vector':(0x44e910,0x1246d08,[0xab2770]),
      'update_noargs':(0x448350,0x1243a28,[])}
WORDS={
 0xad9fb8:0xd0002841,0xad9fbc:0x913e2021,
 0xad9fc0:0x97e5c700,0xad9fc4:0x35ff1dc0,
 0xad9fcc:0x97e5a35d,0xad9fd0:0x97e5a578,
 0xad4964:0x97e5d36f,0xad4970:0x540002a0,
 0xad4978:0x34000261,0xad49bc:0x97e5d291,
 0xb606e0:0x90002561,0xb606e4:0x9117c021,
 0xb607f8:0x52000273,0xb60890:0x52000273,
 0xb6c60c:0x97e368a9,0xb6c610:0x72001c1f,0xb6c614:0x54003ca0,
 0xb81e30:0x97e312a0,0xb81e34:0x72001c1f,
 0xb86700:0x97e3006c,0xb86708:0x12001c00,
 0xab2760:0x97e67540,0xab2770:0x97e67068
}
class Refusal(ValueError):pass
def check(ok,why):
 if not ok:raise Refusal(why)
def sign(v,width):return v-(1<<width) if v&(1<<(width-1)) else v
def adrpa(w,pc):
 check(w&0x9f000000==0x90000000,'ADRP changed')
 n=(((w>>5)&0x7ffff)<<2)|((w>>29)&3)
 return (pc&~4095)+(sign(n,21)<<12)
def adrpa_add(w,v,pc):
 check(v&0xff000000==0x91000000,'ADD changed')
 check(w&31==(v>>5)&31,'ADRP/ADD register mismatch')
 return adrpa(w,pc)+(((v>>10)&4095)<<(12 if v&(1<<22) else 0))
def bl(w,pc):
 check((w>>26)==0b100101,'BL opcode changed')
 return pc+4*sign(w&((1<<26)-1),26)
class ELF:
 def __init__(self,data):
  check(data[:6]==bytes([127,69,76,70,2,1]),'not ELF64 little-endian')
  check(struct.unpack_from('<H',data,18)[0]==183,'not AArch64')
  self.data=data
  off=struct.unpack_from('<Q',data,40)[0]
  step,n,strings=struct.unpack_from('<HHH',data,58)
  check(64<=step<=256 and 1<n<=256 and strings<n and off+n*step<=len(data),'bad ELF sections')
  self.sections=[]
  for i in range(n):
   _,typ,flags,va,fileoff,length,*_=struct.unpack_from('<IIQQQQIIQQ',data,off+i*step)
   check(typ==8 or (fileoff<=len(data) and length<=len(data)-fileoff),'truncated ELF section')
   if typ!=8:self.sections.append((flags,va,fileoff,length))
 def at(self,va,size):
  for f,v,off,n in self.sections:
   if v<=va and va+size<=v+n:return self.data[off+va-v:off+va-v+size]
  raise Refusal('unmapped ELF VA '+hex(va))
 def word(self,va):
  check(any(f&4 and v<=va and va+4<=v+n for f,v,off,n in self.sections),'not executable VA')
  return struct.unpack('<I',self.at(va,4))[0]
 def calls(self,targets):
  ans={t:[] for t in targets}
  for flags,va,off,length in self.sections:
   if not flags&4:continue
   for idx in range(0,length-3,4):
    w=struct.unpack_from('<I',self.data,off+idx)[0]
    if w>>26==0b100101:
     target=bl(w,va+idx)
     if target in ans:ans[target].append(va+idx)
  return ans
def got(elf,va):
 a=elf.word(va);l=elf.word(va+4)
 check(l&0xffc00000==0xf9400000,'PLT must load pointer')
 check((a&31)==((l>>5)&31),'PLT registers mismatch')
 return adrpa(a,va)+(((l>>10)&4095)<<3)
def verify(data):
 check(hashlib.sha256(data).hexdigest()==SHA,'original ELF SHA-256 mismatch')
 elf=ELF(data)
 for addr,w in WORDS.items():check(elf.word(addr)==w,'instruction changed at '+hex(addr))
 check(elf.at(0xfe3f88,4)==b'end'+bytes([0]),'end literal changed')
 flag=b'auto_mode_break_by_high_level_event_flag'+bytes([0])
 check(elf.at(0x100c5f0,len(flag))==flag,'completion flag literal changed')
 check(adrpa_add(elf.word(0xad9fb8),elf.word(0xad9fbc),0xad9fb8)==0xfe3f88,'end reference changed')
 check(adrpa_add(elf.word(0xb606e0),elf.word(0xb606e4),0xb606e0)==0x100c5f0,'completion flag reference changed')
 # CBNZ w0 with a signed 19-bit branch to the known nonmatching path.
 w=elf.word(0xad9fc4)
 check(w&0x7f00001f==0x35000000,'end guard changed')
 check(0xad9fc4+4*sign((w>>5)&0x7ffff,19)==0xad837c,'end guard destination changed')
 check(bl(elf.word(0xad9fc0),0xad9fc0)==0x44bbc0,'string comparison changed')
 check(bl(elf.word(0xad9fcc),0xad9fcc)==0x442d40,'Blackboard acquisition changed')
 check(bl(elf.word(0xad49bc),0xad49bc)==0x449400,'conditional flag setter changed')
 expected={}
 for name,(plt,cell,sites) in PLTS.items():
  check(got(elf,plt)==cell,'PLT/GOT binding changed: '+name)
  expected[plt]=sites
 actual=elf.calls(expected)
 for plt,sites in expected.items():check(actual[plt]==sites,'direct caller census changed: '+hex(plt))
 return {'schema':'X40_R2416_V189_GITHUB_COMPACT_CHECK_V1','sha256':SHA,
 'exactEndGuardAndFlagUpdateValidated':True,
 'completionHelperFlagReadAndCallerCensusValidated':True,
 'directCallerCounts':{name:len(calls) for name,(_,_,calls) in PLTS.items()},
 'runtimeRecleanProven':False,'noDeviceAccess':True}
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--route-elf',type=Path,required=True)
 a=p.parse_args()
 try:print(json.dumps(verify(a.route_elf.read_bytes()),indent=2))
 except (Refusal,OSError,struct.error) as exc:raise SystemExit('X40_V189_REFUSED: '+str(exc))
if __name__=='__main__':main()
