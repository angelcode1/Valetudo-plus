#!/usr/bin/env python3
"""Original SHA-pinned R2416 v222 bounded async callback proof. Python stdlib only."""
import argparse,hashlib,struct,zipfile
HOST_SHA="b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0"
WORDS={3242484:2549971875,3242532:960495684,3242536:1895938207,
3242540:1426063169,3242556:872416213,3242564:2549967191,
3248392:2549973758,3248464:3019901281,3248504:3594453088,
3248608:3594453024,3248632:3594453088,3248660:2549971631,
3248860:3019901323,3248980:3594453024,6091080:2549260438,
6091100:2549261905,6091736:2549265042,6092208:2549261156,
6127216:2415930625,6127448:3594453024,6127732:2549251275}
DIRECT={3242484:2582656,3242564:2564000,3248392:2596096,
3248660:2587856,6091080:2585504,6091736:2604576,6127732:2585504}
def need(ok,why):
 if not ok:raise ValueError(why)
def get(b,va,n):
 need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,
      'Expected ELF64LE AArch64')
 pos=struct.unpack_from('<Q',b,32)[0];step,count=struct.unpack_from('<HH',b,54)
 need(step>=56 and 0<count<=100 and pos+step*count<=len(b),'Malformed program headers')
 for i in range(count):
  typ,_,off,start,_,sz,_,_=struct.unpack_from('<IIQQQQQQ',b,pos+i*step)
  if typ==1 and start<=va and va+n<=start+sz:
   p=off+va-start
   need(p+n<=len(b),'Truncated ELF')
   return b[p:p+n]
 raise ValueError('Original VA not mapped')
def word(b,va):return struct.unpack('<I',get(b,va,4))[0]
def to(va,op):
 need(op&0xfc000000==0x94000000,'Expected direct BL')
 imm=op&0x3ffffff
 if imm&0x2000000:imm-=0x4000000
 return va+imm*4
def run(path):
 with zipfile.ZipFile(path) as z:
  names=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
  need(len(names)==1,'Original host ELF missing or ambiguous')
  b=z.read(names[0])
 need(hashlib.sha256(b).hexdigest()==HOST_SHA,'Original firmware SHA mismatch')
 for va,expected in WORDS.items():
  need(word(b,va)==expected,'Native opcode changed at '+hex(va))
 for va,expected in DIRECT.items():
  need(to(va,word(b,va))==expected,'Direct-call target changed at '+hex(va))
 lo,hi=0x5cebc0,0x5cfa80
 for (op,),va in zip(struct.iter_unpack('<I',get(b,lo,hi-lo)),range(lo,hi,4)):
  if op&0xfc000000==0x94000000:
   need(to(va,op) not in (0x271fa0,0x5d7e30),
       'New direct CleanBot -> AsyncDeque drain/typed publisher edge')
 return len(WORDS),len(DIRECT)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 a=p.parse_args()
 try:
  print('X40_R2416_V222_REPO_ASYNC_BOUNDARY_PASS',*run(a.prior_zip))
  print('Asynchronous mechanisms present; runtime identity and stain-triggered cleaning unverified.')
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V222_REPO_FAIL: '+str(e))
