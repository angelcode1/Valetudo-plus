#!/usr/bin/env python3
"""Bounded R2416 Cleanbot/List direct caller census. Python stdlib only.

Reads the original owner PRIVATE collector ZIP. No robot/firmware access.
The separate full v218 kit checks 57 native words, 21 edges and all regressions.
"""
import argparse,hashlib,struct,zipfile
PIN='fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'
LO,HI=0x4526f0,0xf9c0b0
API={'preprocess':(0x449140,0xdf4eac),
 'edge_cleaning':(0x4416a0,0xcd0cd8),
 'SendCLeanListToCleanbot':(0x43d950,0x52f3c0),
 'post_process':(0x447ac0,0xdf4f2c)}
WORDS={
 0xcd0cd8:0x97ddc272,0x52f3b8:0x97fc4e62,0x52f3c0:0x97fc3964,
 0xdf4eac:0x97d950a5,0xdf4ed0:0x97d96258,0xdf4f2c:0x97d94ae5,
 0xdf2f48:0x97d93f7e,0xdf2f50:0x90000ee1,0xdf2f54:0x91178021,
 0xdf2f64:0xf9400660,0xdf2f68:0xb4002680,0xdf2f78:0xd63f0040,
 0xdf2f80:0xb40025c0,0xdf2fa0:0x97d960dc,0xdf2fa8:0x5400ea60,
 0xdf2fb4:0x97ffed0f,0xdf2fbc:0x5400eb80,0xdf2fc4:0xb400eb57,
 0xdf2fd4:0x97d94437,0xdf2fe8:0x5400a680,0xdf2ffc:0x97d9295d}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def va_blob(raw,va,n):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
      'Expected AArch64 ELF64LE')
 pos=struct.unpack_from('<Q',raw,32)[0]
 step,num=struct.unpack_from('<HH',raw,54)
 need(step>=56 and 0<num<=100 and pos+step*num<=len(raw),'Invalid ELF headers')
 for i in range(num):
  kind,_,off,start,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,pos+i*step)
  if kind==1 and start<=va and va+n<=start+size:
   at=off+va-start
   need(at+n<=len(raw),'Truncated original ELF')
   return raw[at:at+n]
 raise ValueError('Unmapped native VA')
def check(zip_path):
 with zipfile.ZipFile(zip_path) as z:
  hits=[m for m in z.namelist() if '/files/liblethe_route_nodes.so/' in m]
  need(len(hits)==1,'Missing/ambiguous original ELF')
  raw=z.read(hits[0])
 need(hashlib.sha256(raw).hexdigest()==PIN,'Original ELF digest mismatch')
 for va,expected in WORDS.items():
  need(struct.unpack('<I',va_blob(raw,va,4))[0]==expected,
       'Original native word mismatch '+hex(va))
 need(va_blob(raw,0xfce5e0,17)==b'Areas_Clean_List\0',
      'CleanList literal changed')
 text=va_blob(raw,LO,HI-LO)
 found={name:[] for name in API}
 target_to_name={p:name for name,(p,_) in API.items()}
 for (opcode,),at in zip(struct.iter_unpack('<I',text),range(LO,HI,4)):
  if opcode&0xfc000000!=0x94000000:continue
  imm=opcode&0x3ffffff
  if imm&(1<<25):imm-=1<<26
  name=target_to_name.get(at+4*imm)
  if name:found[name].append(at)
 for name,(_,expected) in API.items():
  need(found[name]==[expected],'Unexpected direct calls: '+name)
 return len(WORDS),len(API),sum(map(len,found.values()))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--prior-zip',required=True)
 options=ap.parse_args()
 try:
  print('X40_R2416_V218_REPO_DIRECT_CALL_CENSUS_PASS',*check(options.prior_zip))
  print('Indirect/dynamic calls, live scheduling and physical reclean are unproven.')
 except (OSError,ValueError,IndexError,TypeError,struct.error,zipfile.BadZipFile) as err:
  raise SystemExit('X40_R2416_V218_REPO_FAIL: '+str(err))
