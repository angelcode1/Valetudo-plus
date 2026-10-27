#!/usr/bin/env python3
"""R2416 v217 bounded original-native stain generated-tree placement checker.

Python 3 stdlib only; reads the owner's PRIVATE original firmware ZIP without
extracting, executing or publishing proprietary binaries.
"""
import argparse,hashlib,struct,zipfile
PINS={
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
}
TREE={
 0x45e6c8:0xf0000aa1,0x45e6cc:0x9118c421,0x45e6d8:0x97f59fd2,0x45e6e4:0x97f5a087,
 0x3c1ec8:0xf0000ee1,0x3c1ecc:0x912e3421,0x3c1ed8:0x97f811d2,0x3c1ee4:0x97f81287,
 0x4176b4:0xb0000c41,0x4176b8:0x912e3421,0x4176c4:0x97f6bbd7,0x4176d0:0x97f6bc8c,
}
ROUTE={
 0x5191c0:0xf0005581,0x5191c4:0x91352021,0x51921c:0x97fce4b9,
 0xad944c:0xf0002781,0xad9450:0x91352021,0xad947c:0x5401ce40,
 0xad94bc:0x97e5a6a9,0xad94ec:0x97e59721,
 0xdf2f50:0x90000ee1,0xdf2f54:0x91178021,
}
EDGES={
 ('liblethe_tree.so',0x45e6d8):0x1c6620,
 ('liblethe_tree.so',0x3c1ed8):0x1c6620,
 ('liblethe_tree.so',0x4176c4):0x1c6620,
 ('liblethe_route_nodes.so',0x51921c):0x452500,
 ('liblethe_route_nodes.so',0xad94bc):0x442f60,
 ('liblethe_route_nodes.so',0xad94ec):0x43f170,
}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def va_data(raw,addr,n):
 need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
      'Expected AArch64 ELF64LE')
 o=struct.unpack_from('<Q',raw,32)[0];step,cnt=struct.unpack_from('<HH',raw,54)
 need(step>=56 and 0<cnt<=100 and o+step*cnt<=len(raw),'Bad ELF program header bounds')
 for i in range(cnt):
  kind,_,off,va,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,o+i*step)
  if kind==1 and va<=addr and addr+n<=va+size:
   p=off+addr-va;need(p+n<=len(raw),'Truncated PT_LOAD');return raw[p:p+n]
 raise ValueError('Unmapped ELF virtual address')
def word(raw,addr):return struct.unpack('<I',va_data(raw,addr,4))[0]
def branch_target(addr,insn):
 need(insn&0xfc000000==0x94000000,'Expected BL')
 v=insn&0x3ffffff
 if v&(1<<25):v-=1<<26
 return addr+4*v
def adrp_add(addr,a,b):
 need(a&0x9f000000==0x90000000,'Expected ADRP')
 rd=a&31
 need(b&0xffc00000==0x91000000 and b&31==rd and ((b>>5)&31)==rd,
      'Expected same-register ADD')
 imm=(((a>>5)&0x7ffff)<<2)|((a>>29)&3)
 if imm&(1<<20):imm-=1<<21
 return (addr&~4095)+(imm<<12)+((b>>10)&4095)
def generated_node_name_sites(tree):
 start,end=0x1c6950,0x5682e0
 code=va_data(tree,start,end-start)
 names={0x5b5631:'AiStainCheck',0x5a0b8d:'SetExtraCleanArea'}
 out={'AiStainCheck':[],'SetExtraCleanArea':[]}
 for off in range(0,len(code)-4,4):
  a,b=struct.unpack_from('<II',code,off)
  if a&0x9f000000!=0x90000000 or b&0xffc00000!=0x91000000:continue
  rd=a&31
  if b&31!=rd or ((b>>5)&31)!=rd:continue
  imm=(((a>>5)&0x7ffff)<<2)|((a>>29)&3)
  if imm&(1<<20):imm-=1<<21
  dst=((start+off)&~4095)+(imm<<12)+((b>>10)&4095)
  if dst in names:out[names[dst]].append(start+off)
 need(out=={'AiStainCheck':[0x45e6c8],
            'SetExtraCleanArea':[0x3c1ec8,0x4176b4]},
      'Generated node placement/reference census changed')
 return out
def check(prior):
 with zipfile.ZipFile(prior) as z:
  images={}
  for name,digest in PINS.items():
   members=[x for x in z.namelist() if '/files/'+name+'/' in x]
   need(len(members)==1,'Missing/ambiguous original ELF '+name)
   original=z.read(members[0])
   need(hashlib.sha256(original).hexdigest()==digest,'Original firmware SHA mismatch '+name)
   images[name]=original
 for name,anchors in [('liblethe_tree.so',TREE),('liblethe_route_nodes.so',ROUTE)]:
  for at,expected in anchors.items():
   need(word(images[name],at)==expected,'Original AArch64 word changed '+name+':'+hex(at))
 for (name,at),dst in EDGES.items():
  need(branch_target(at,word(images[name],at))==dst,
       'Original native factory/helper call changed')
 tree=images['liblethe_tree.so'];route=images['liblethe_route_nodes.so']
 for name,va in (('AiStainCheck',0x5b5631),('SetExtraCleanArea',0x5a0b8d)):
  need(va_data(tree,va,len(name)+1)==name.encode()+b'\0',
       'Generated node type changed')
 for name,va in (('stain_area_for_logic',0xfccd48),('Areas_Clean_List',0xfce5e0)):
  need(va_data(route,va,len(name)+1)==name.encode()+b'\0',
       'Shared Blackboard key changed')
 for at,va in ((0x45e6c8,0x5b5631),(0x3c1ec8,0x5a0b8d),(0x4176b4,0x5a0b8d)):
  need(adrp_add(at,word(tree,at),word(tree,at+4))==va,
       'Generated child type address changed')
 generated_node_name_sites(tree)
 return len(TREE)+len(ROUTE),len(EDGES),1,2
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True);a=p.parse_args()
 try:
  print('X40_R2416_V217_REPO_STAIN_NODE_OWNERS_PASS',*check(a.prior_zip))
  print('No runtime execution order or additional cleaning-task dispatch established.')
 except (ValueError,OSError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V217_REPO_FAIL: '+str(e))
