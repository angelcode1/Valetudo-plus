#!/usr/bin/env python3
"""Standalone SHA-pinned R2416 v219 debug task-stack caller census. Offline/stdlib."""
import argparse,hashlib,struct,zipfile
PINS={
'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'}
PUSH=[0x51ad68,0x51b478,0x51ba28,0x51be54,0x51cc6c,
      0x6e26a8,0x6e2ce0,0x6e3340,0x6e4894,0x6e5358]
HOST={'Push':(0x27afd0,PUSH),
      'Reset':(0x27e0f0,[a-12 for a in PUSH]),
      'DebugTask':(0x275ba0,[a-48 for a in PUSH])}
ROUTE={'Empty':(0x44c390,[0x6a87b8]),
       'Front':(0x449130,[0x6a87f4]),
       'Pop':(0x449df0,[0x6a8820])}

def need(ok,message):
 if not ok:raise ValueError(message)
def va_bytes(blob,va,size):
 need(blob[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',blob,18)[0]==183,
      'Expected AArch64 ELF64LE')
 pos=struct.unpack_from('<Q',blob,32)[0];step,count=struct.unpack_from('<HH',blob,54)
 need(step>=56 and 0<count<100 and pos+step*count<=len(blob),'Bad ELF headers')
 for i in range(count):
  typ,_,off,start,_,length,_,_=struct.unpack_from('<IIQQQQQQ',blob,pos+step*i)
  if typ==1 and start<=va and va+size<=start+length:
   off+=va-start
   need(off+size<=len(blob),'Truncated ELF PT_LOAD')
   return blob[off:off+size]
 raise ValueError('Native VA not mapped')
def census(blob,start,end,apis):
 data=va_bytes(blob,start,end-start);found={t:[] for t,_ in apis.values()}
 for (opcode,),at in zip(struct.iter_unpack('<I',data),range(start,end,4)):
  if opcode&0xfc000000!=0x94000000:continue
  offset=opcode&0x3ffffff
  if offset&0x2000000:offset-=0x4000000
  to=at+4*offset
  if to in found:found[to].append(at)
 for key,(target,expected) in apis.items():
  need(found[target]==expected,'Unexpected direct caller '+key)
 return sum(map(len,found.values()))
def audit(path):
 with zipfile.ZipFile(path) as z:
  images={}
  for name,sha in PINS.items():
   matches=[entry for entry in z.namelist() if '/files/'+name+'/' in entry]
   need(len(matches)==1,'Missing/ambiguous original ELF '+name)
   raw=z.read(matches[0])
   need(hashlib.sha256(raw).hexdigest()==sha,'Original native SHA mismatch '+name)
   images[name]=raw
 host=images['node_lethe.so'];route=images['liblethe_route_nodes.so']
 h=census(host,0x2a0000,0x9c0000,HOST)
 r=census(route,0x4526f0,0xf9c0b0,ROUTE)
 need(struct.unpack('<I',va_bytes(route,0x6a8800,4))[0]==0xd63f0020,
      'Changed indirect task method invocation')
 need(struct.unpack('<I',va_bytes(route,0x6a8818,4))[0]==0x54fffd60,
      'Changed task continuation guard')
 need(struct.unpack('<I',va_bytes(host,0x316fa0,4))[0]==0xf9001aa0,
      'Changed actual task queue insertion pointer update')
 return h,r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 a=p.parse_args()
 try:
  print('X40_R2416_V219_REPO_DEBUG_TASK_STACK_PASS',*audit(a.prior_zip))
  print('Compiled debug-stack interface only. Autonomous AI-stain reclean not demonstrated.')
 except (OSError,ValueError,struct.error,zipfile.BadZipFile) as exc:
  raise SystemExit('X40_R2416_V219_REPO_FAIL: '+str(exc))
