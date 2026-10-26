#!/usr/bin/env python3
"""Bounded, offline, SHA-pinned v206 generated ReuseTree/AiStainMop audit.

Python 3 stdlib only. Reads original private collector archive in memory;
never extracts, executes or publishes vendor firmware.
"""
import argparse, hashlib, struct, zipfile

PINS={
 'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
}
WORDS={
 'liblethe_tree.so':{
  0x1cc928:0x97ffe77e,0x1cc92c:0x97fff4ae,0x1c9be8:0xf0001ce1,
  0x1ca138:0xb0002601,0x1ca13c:0x9114c021,
  0x1cb3e8:0xf00025e1,0x1cb3ec:0x911dc021,0x1cb3f0:0x97fff9d9,
  0x1cb400:0x97ffec88,
 },
 'node_lethe.so':{
  0x3550f8:0xb0003401,0x3550fc:0x91134021,0x355114:0xf9401802,
  0x35511c:0x97fc80a9,0x35512c:0xf9079401,0x3552c0:0xf9401802,
  0x3552c8:0x97fc803e,0x3552d8:0xf907a401,
 },
 'libbehaviortree_cpp.so':{
  0x5f638:0x97ff68a6,0x5f650:0x97ff689c,0x4fb04:0x36000142,
 },
}
BL_EDGES={
 ('liblethe_tree.so',0x1cc92c):0x1c9be4,
 ('liblethe_tree.so',0x1cb3f0):0x1c9b54,
 ('liblethe_tree.so',0x1cb400):0x1c6620,
 ('node_lethe.so',0x35511c):0x2753c0,
 ('node_lethe.so',0x3552c8):0x2753c0,
 ('libbehaviortree_cpp.so',0x5f638):0x398d0,
 ('libbehaviortree_cpp.so',0x5f650):0x398c0,
}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def data_at(data,addr,n):
 need(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',data,18)[0]==183,'Expected ARM64 ELF64LE')
 start=struct.unpack_from('<Q',data,32)[0]
 step,count=struct.unpack_from('<HH',data,54)
 need(step>=56 and count<100 and start+step*count<=len(data),'ELF headers invalid')
 for i in range(count):
  kind,_,off,vaddr,_,size,_,_=struct.unpack_from('<IIQQQQQQ',data,start+i*step)
  if kind==1 and vaddr<=addr and addr+n<=vaddr+size:
   at=off+addr-vaddr
   need(at+n<=len(data),'ELF segment truncated')
   return data[at:at+n]
 raise ValueError('Virtual address not file-backed')
def word(b,va):return struct.unpack('<I',data_at(b,va,4))[0]
def bl_target(va,insn):
 need(insn&0xfc000000==0x94000000,'Unexpected BL opcode')
 imm=insn&0x3ffffff
 if imm&(1<<25):imm-=1<<26
 return va+4*imm
def addr_adrp_add(va,a,b):
 need(a&0x9f000000==0x90000000,'Expected ADRP')
 reg=a&31
 need(b&0xffc00000==0x91000000 and b&31==reg and (b>>5)&31==reg,'Expected ADD same register')
 imm=(((a>>5)&0x7ffff)<<2)|((a>>29)&3)
 if imm&(1<<20):imm-=1<<21
 return (va&~4095)+(imm<<12)+((b>>10)&4095)
def param_table(data,addr):
 v=struct.unpack('<8Q',data_at(data,addr,64))
 return tuple(data_at(data,v[i],v[i+1]) for i in (0,2,4,6))
def child_census(tree):
 sites=[]
 for va in range(0x1c9be4,0x1cc8f4,4):
  a=word(tree,va)
  if a&0x9f00001f!=0x90000001:continue
  b=word(tree,va+4);c=word(tree,va+8)
  if b&0xffc003ff!=0x91000021 or c&0xfc000000!=0x94000000:continue
  if bl_target(va+8,c)!=0x1c9b54:continue
  try:
   addr=addr_adrp_add(va,a,b)
   vals=param_table(tree,addr)
   if vals[2]==b'subtree_file_path' and vals[3].startswith(b'reuse/'):
    sites.append((va,addr,vals[3]))
  except (ValueError,struct.error):continue
 return sites
def verify(images):
 for name,blob in images.items():
  need(hashlib.sha256(blob).hexdigest()==PINS[name],'Whole-file SHA-256 mismatch '+name)
  for addr,val in WORDS[name].items():
   need(word(blob,addr)==val,f'Native instruction mismatch {name}@{addr:#x}')
 for (name,addr),expected in BL_EDGES.items():
  need(bl_target(addr,word(images[name],addr))==expected,'Native call target changed')
 tree=images['liblethe_tree.so'];host=images['node_lethe.so']
 need(addr_adrp_add(0x1cb3e8,word(tree,0x1cb3e8),word(tree,0x1cb3ec))==0x68a770,
      'AiStainMop table address changed')
 for at,p in ((0x68a770,b'reuse/AiStainMop'),(0x68b530,b'reuse/CleanSelectedAreas')):
  need(param_table(tree,at)==(b'expand_in_logger',b'true',b'subtree_file_path',p),
       'Generated subtree parameter changed')
 need(b'ReuseTree.xml' in data_at(host,0x9d64d0,165),'Host wrapper changed')
 need(word(host,0x355114)==word(host,0x3552c0)==0xf9401802,
      'Common route Blackboard holder field changed')
 children=child_census(tree)
 need(len(children)==158 and len(set(x[2] for x in children))==158,'Generated reuse census changed')
 need((0x1cb3e8,0x68a770,b'reuse/AiStainMop') in children,'Stain child placement changed')
 need((0x1ca138,0x68b530,b'reuse/CleanSelectedAreas') in children,'Cleaning child placement changed')
 need(not any(b'StationWash' in x[2] for x in children),'Unexpected StationWash reuse')
 return len(children)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 args=p.parse_args()
 with zipfile.ZipFile(args.prior_zip) as z:
  images={}
  for name in PINS:
   paths=[x for x in z.namelist() if '/files/'+name+'/' in x]
   need(len(paths)==1,'Missing or ambiguous private ELF '+name)
   images[name]=z.read(paths[0])
 count=verify(images)
 print('X40_R2416_V206_REPO_REUSETREE_STATIC_PASS',count,'distinct reuse children')
 print('No live cache population, stain-triggered task or physical rewash proven.')
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V206_REPO_FAIL: '+str(e))
