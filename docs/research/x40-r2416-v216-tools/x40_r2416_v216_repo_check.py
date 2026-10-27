#!/usr/bin/env python3
"""Original SHA-pinned R2416 ReuseTree tick-order check. Python 3 stdlib only.

Only reads original PRIVATE collector ZIP. No robot access or external deps.
Full 42-word/18-edge historical replay: v216 standalone source ZIP.
"""
import argparse,hashlib,struct,zipfile

PINS={
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
}
TREE={
 0x1c9be8:0xf0001ce1,0x1c9bec:0x910c9421,0x1c9c0c:0x97fff285,
 0x1c9c24:0x90001d01,0x1c9c28:0x91084421,0x1c9c38:0x97fff27a,
 0x1c9c44:0x97fff32f,0x1c9c48:0x97fff27e,
 0x1c9c5c:0x97ffffbe,0x1c9c70:0x97fff26c,0x1c9c7c:0x97fff321,
 0x1cb3e8:0xf00025e1,0x1cb3ec:0x911dc021,0x1cb400:0x97ffec88,
}
CORE={
 0x63cf0:0x52800040,0x63cf4:0xd65f03c0,0x929f0:0xd63f0020,
 0x92a14:0x71000b7f,0x92a18:0x54000180,0x92a1c:0x540002c8,
 0x92a50:0x97fe9b64,0x92a74:0x11000694,
}

def need(ok,msg):
 if not ok:raise ValueError(msg)

def elf_va(raw,addr,n):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,'Expected AArch64 ELF64LE')
 o=struct.unpack_from('<Q',raw,32)[0];step,count=struct.unpack_from('<HH',raw,54)
 need(step>=56 and 0<count<=100 and o+step*count<=len(raw),'Malformed original ELF headers')
 for i in range(count):
  typ,_,offset,va,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,o+i*step)
  if typ==1 and va<=addr and addr+n<=va+size:
   at=offset+addr-va
   need(at+n<=len(raw),'Truncated ELF PT_LOAD segment')
   return raw[at:at+n]
 raise ValueError('Native virtual address not mapped')

def word(raw,addr):return struct.unpack('<I',elf_va(raw,addr,4))[0]

def target(addr,op):
 need(op&0xfc000000==0x94000000,'Expected AArch64 BL')
 imm=op&0x3ffffff
 if imm&(1<<25):imm-=1<<26
 return addr+4*imm

def ref_address(va,adrp,add):
 need(adrp&0x9f00001f==0x90000001 and add&0xffc003ff==0x91000021,
      'Expected ADRP+ADD x1')
 imm=(((adrp>>5)&0x7ffff)<<2)|((adrp>>29)&3)
 if imm&(1<<20):imm-=1<<21
 return (va&~4095)+4096*imm+((add>>10)&4095)

def verify(prior):
 with zipfile.ZipFile(prior) as z:
  images={}
  for name,digest in PINS.items():
   items=[path for path in z.namelist() if '/files/'+name+'/' in path]
   need(len(items)==1,'Missing/ambiguous original ELF '+name)
   raw=z.read(items[0])
   need(hashlib.sha256(raw).hexdigest()==digest,'Original ELF SHA mismatch '+name)
   images[name]=raw
 tree=images['liblethe_tree.so'];core=images['libbehaviortree_cpp.so']
 for raw,anchors in ((tree,TREE),(core,CORE)):
  for va,w in anchors.items():
   need(word(raw,va)==w,'Compiled original opcode mismatch %#x'%va)
 need(elf_va(tree,0x568325,9)==b'Fallback\0' and
      elf_va(tree,0x569211,14)==b'AlwaysSuccess\0',
      'Generated root or first child name changed')
 need(ref_address(0x1c9be8,word(tree,0x1c9be8),word(tree,0x1c9bec))==0x568325,
      'Generated root name reference changed')
 need(ref_address(0x1c9c24,word(tree,0x1c9c24),word(tree,0x1c9c28))==0x569211,
      'Generated first child name reference changed')
 nodes=[];pushed=[];children=[]
 for at in range(0x1c9be4,0x1cc8f4,4):
  code=word(tree,at)
  if code&0xfc000000!=0x94000000:continue
  dst=target(at,code)
  if dst==0x1c6620:nodes.append(at)
  elif dst==0x1c6640:pushed.append(at)
  elif dst==0x1c6900:children.append(at)
 need(len(nodes)==len(pushed)==160 and len(children)==159,
      'Generated 160 node/159 child census changed')
 need(nodes[:3]==[0x1c9c0c,0x1c9c38,0x1c9c70] and
      children[:2]==[0x1c9c44,0x1c9c7c],
      'Fallback -> AlwaysSuccess -> reuse child order changed')
 need(word(core,0x63cf0)==0x52800040 and
      word(core,0x92a14)==0x71000b7f and
      word(core,0x92a18)==0x54000180 and
      word(core,0x92a1c)==0x540002c8,
      'AlwaysSuccess or Fallback success short-circuit changed')
 need(tree.count(b'AiStainMop')==1 and core.count(b'AiStainMop')==0,
      'Unexpected exact generated subtree literal census')
 return len(TREE)+len(CORE),len(nodes),len(pushed),len(children)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 a=p.parse_args()
 try:
  print('X40_R2416_V216_REPO_REUSETREE_TICK_ORDER_PASS',*verify(a.prior_zip))
  print('Compiled path only; live cache preparation, execution and reclean remain unproven.')
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V216_REPO_FAIL: '+str(e))
