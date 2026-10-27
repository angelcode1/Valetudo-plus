#!/usr/bin/env python3
"""R2416 offline original SHA-pinned stain switch and station guard census.

Python 3 standard library. Reads owner PRIVATE ELF from ZIP in memory only.
Never contacts the robot or writes private firmware or settings.
For full native mutation checks and inherited research use v228 source-only ZIP.
"""
import argparse,hashlib,struct,zipfile
SHA='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
KEYS={'open_stain_identify':(0x9d6270,[0x582bc8,0x7b8584]),
      'wash_status':(0xa33250,47),'RobotMode':(0x9d3fc8,104)}
PINS={
0x582bc4:0x394183e3,0x582bc8:0x900022a1,0x582bd0:0x3902d3e3,
0x582be8:0x97f3d7be,0x7b8584:0xd00010e1,0x7b85a4:0x97eb04d7,
0x7b8688:0x7100401f,0x7b8694:0x7100081f,0x7b871c:0x540026cd,
0x7b872c:0x3943e801,0x7b8730:0x7100103f,0x7b8734:0x54003240,
0x7b8d80:0x52805dc4,0x7b8d94:0xb9007064,0x899980:0x71001c3f,
0x89998c:0x7100143f,0x899994:0x7100183f,0x8999b0:0x7100203f}
def need(ok,why):
 if not ok:raise ValueError(why)
def elf(raw,va,size):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
      'Expected original AArch64 ELF64LE')
 header=struct.unpack_from('<Q',raw,32)[0]
 stride,count=struct.unpack_from('<HH',raw,54)
 need(stride>=56 and 0<count<100 and header+stride*count<=len(raw),
      'Malformed original ELF program headers')
 for i in range(count):
  typ,_,offset,start,_,length,_,_=struct.unpack_from('<IIQQQQQQ',raw,header+i*stride)
  if typ==1 and start<=va and va+size<=start+length:
   index=offset+va-start
   need(index+size<=len(raw),'Truncated original native segment')
   return raw[index:index+size]
 raise ValueError('Original ELF virtual address unmapped')
def references(text,start,target):
 hits=[]
 for at in range(start,start+len(text)-4,4):
  adrp,add=struct.unpack_from('<II',text,at-start)
  if adrp&0x9f000000!=0x90000000 or add&0xffc00000!=0x91000000:continue
  r=adrp&31
  if add&31!=r or (add>>5)&31!=r:continue
  imm=(((adrp>>5)&0x7ffff)<<2)|((adrp>>29)&3)
  if imm&(1<<20):imm-=1<<21
  if (at&~4095)+(imm<<12)+((add>>10)&4095)==target:hits.append(at)
 return hits
def verify(path):
 with zipfile.ZipFile(path) as z:
  matches=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
  need(len(matches)==1,'Expected one original owner host ELF')
  raw=z.read(matches[0])
 need(hashlib.sha256(raw).hexdigest()==SHA,'Original native host hash changed')
 for at,word in PINS.items():
  need(struct.unpack('<I',elf(raw,at,4))[0]==word,
       'Native instruction changed '+hex(at))
 text=elf(raw,0x2a0000,0x9c0000-0x2a0000)
 for key,(target,expected) in KEYS.items():
  need(elf(raw,target,len(key)+1)==key.encode()+b'\0',
       'Original key literal changed '+key)
  sites=references(text,0x2a0000,target)
  need(sites==expected if isinstance(expected,list) else len(sites)==expected,
       'Bounded key-reference census changed '+key)
 return len(PINS),2,47,104
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--prior-zip',required=True)
 try:
  print('X40_R2416_V228_REPO_SWITCH_SENSOR_PASS',*verify(parser.parse_args().prior_zip))
  print('Compiled state only: vendor enum meanings, wash and reclean unverified.')
 except (ValueError,OSError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V228_REPO_FAIL: '+str(e))
