#!/usr/bin/env python3
"""X40 R2416 v29: offline RobotNode-to-StationWash parameter verification.

Usage: python3 x40_r2416_v28_dynamic_subtree_verify.py X40-Firmware-Reference.zip X40-R2416-v27.zip
Only reads supplied archives; no ELF execution, SSH, robot commands, or uploads.
Verification is static and does not prove that a selected subtree ticks on hardware.
"""
import argparse
import hashlib
import io
import struct
import sys
import tarfile
import zipfile

PINS={
 'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
 'liblethe_tactics_tree.so':'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
 'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
}
def require(v,msg):
 if not v: raise ValueError(msg)
def only(seq,match,label):
 arr=[x for x in seq if match(x)]
 require(len(arr)==1,f'{label}: expected one, got {len(arr)}')
 return arr[0]
def checked(name,blob):
 require(hashlib.sha256(blob).hexdigest()==PINS[name],f'{name}: SHA-256 pin mismatch')
 return blob
class Elf:
 def __init__(self,b):
  self.b=b
  require(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,'not an ELF64/AArch64 binary')
  off=struct.unpack_from('<Q',b,32)[0];ent,n=struct.unpack_from('<HH',b,54)
  self.loads=[]
  for j in range(n):
   typ,_,fileoff,vaddr,_,filesz,_,_=struct.unpack_from('<IIQQQQQQ',b,off+j*ent)
   if typ==1:self.loads.append((vaddr,vaddr+filesz,fileoff))
  self.sec=[]
  off=struct.unpack_from('<Q',b,40)[0];ent,n=struct.unpack_from('<HH',b,58)
  for j in range(n):
   x=struct.unpack_from('<IIQQQQIIQQ',b,off+j*ent)
   self.sec.append({'nameoff':x[0],'addr':x[3],'offset':x[4],'size':x[5],'link':x[6],'entsize':x[9]})
  names=self.secbytes(self.sec[struct.unpack_from('<H',b,62)[0]])
  for s in self.sec:
   k=s['nameoff'];s['name']=names[k:names.index(b'\0',k)].decode('ascii')
 def secbytes(self,s):return self.b[s['offset']:s['offset']+s['size']]
 def section(self,name):return only(self.sec,lambda s:s['name']==name,name)
 def va(self,addr,size):
  for a,z,off in self.loads:
   if a<=addr and addr+size<=z:return self.b[off+addr-a:off+addr-a+size]
  raise ValueError('VA not backed in ELF: %#x'%addr)
 def word(self,addr):return struct.unpack('<I',self.va(addr,4))[0]
 def ins(self,addr,w):require(self.word(addr)==w, f'changed instruction {addr:#x}')
 def call(self,addr,target):
  word=self.word(addr);require(word&0xfc000000==0x94000000,f'not BL {addr:#x}')
  delta=word&0x3ffffff
  if delta&(1<<25):delta-=1<<26
  require(addr+4*delta==target,f'BL target differs at {addr:#x}')
 def symbol(self,name):
  sym=self.section('.dynsym'); raw=self.secbytes(sym);strings=self.secbytes(self.sec[sym['link']])
  require(sym['entsize']==24,'invalid dynsym layout')
  for i in range(0,len(raw),24):
   k,_,_,_,val,_=struct.unpack_from('<IBBHQQ',raw,i)
   if strings[k:strings.find(b'\0',k)]==name:return val
  raise ValueError('missing symbol: '+name.decode())
 def adrp_add_references(self,target,max_gap=4):
  """Find only direct ADRP + ADD same-register pairs in .text."""
  s=self.section('.text');raw=self.secbytes(s);base=s['addr'];out=[]
  for i in range(0,len(raw)-4,4):
   w=struct.unpack_from('<I',raw,i)[0]
   if w&0x9f000000!=0x90000000:continue
   reg=w&31
   imm=((w>>5)&0x7ffff)<<2 | ((w>>29)&3)
   if imm&(1<<20):imm-=1<<21
   page=((base+i)&~4095)+(imm<<12)
   if page!=(target&~4095):continue
   for j in range(i+4,min(i+max_gap+4,len(raw)),4):
    a=struct.unpack_from('<I',raw,j)[0]
    if a&0xff000000!=0x91000000 or ((a>>5)&31)!=reg:continue
    delta=((a>>10)&4095)<<(12 if (a>>22)&1 else 0)
    if page+delta==target:out.append((base+i,base+j))
  return out
 def bl_sites(self,target):
  s=self.section('.text');raw=self.secbytes(s);out=[]
  for i in range(0,len(raw)-3,4):
   w=struct.unpack_from('<I',raw,i)[0]
   if w&0xfc000000!=0x94000000:continue
   delta=w&0x3ffffff
   if delta&(1<<25):delta-=1<<26
   if s['addr']+i+delta*4==target:out.append(s['addr']+i)
  return out

def collect(original_path,runtime_path):
 with zipfile.ZipFile(original_path) as z:
  tarname=only(z.namelist(),lambda n:n.endswith('/X40_R2416_original_vendor_native_ELFs.tar') and not n.startswith('__MACOSX/'),'original archive')
  with tarfile.open(fileobj=io.BytesIO(z.read(tarname)),mode='r:') as tar:
   originals={}
   for name in PINS:
    if name=='node_lethe.so':continue
    member=only(tar.getmembers(),lambda m:m.isfile() and m.name.endswith('/'+name),name)
    originals[name]=checked(name,tar.extractfile(member).read())
  path=only(z.namelist(),lambda n:n.endswith('/robot/ava/lib/node_lethe.so') and not n.startswith('__MACOSX/'),'node_lethe')
  originals['node_lethe.so']=checked('node_lethe.so',z.read(path))
 with zipfile.ZipFile(runtime_path) as z:
  for name in ['liblethe_tree.so','liblethe_route_nodes.so','liblethe_tactics_tree.so']:
   path=only(z.namelist(),lambda n:n.endswith('/tree_lib/'+name) and not n.startswith('__MACOSX/'),name)
   require(z.read(path)==originals[name],f'original/runtime differs: {name}')
  cfg=only(z.namelist(),lambda n:n.endswith('/setting.yaml') and not n.startswith('__MACOSX/'),'setting.yaml')
  lines=z.read(cfg).decode('utf-8').splitlines()
  require(sum(x.strip()=='behavior_tree_path: RobotNode' for x in lines)==1,'active RobotNode selector missing or duplicated')
  require(sum(x.strip()=='tree_lib_path: /tmp/lib/tree_lib//' for x in lines)==1,'active library path missing or duplicated')
 return {k:Elf(v) for k,v in originals.items()}

def verify(a,b):
 x=collect(a,b);n=x['node_lethe.so'];route=x['liblethe_route_nodes.so'];tree=x['liblethe_tree.so'];beh=x['libbehaviortree_cpp.so']
 require(n.symbol(b'_ZN6BtTaskC2ERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEERKSt10shared_ptrIN2BT10BlackboardEE')==0x316410,'BtTask constructor differs')
 prefix=b'<root main_tree_to_execute="BehaviorTree">\n        <BehaviorTree ID="BehaviorTree"><SubtreeCondition subtree_file_path="'
 suffix=b'"/></BehaviorTree></root>'
 require(n.va(0x9d3380,len(prefix))==prefix,'BtTask wrapper prefix differs')
 require(n.va(0x9d3400,len(suffix))==suffix,'BtTask wrapper suffix differs')
 for p,w in {0x31642c:0xaa0103f5,0x316430:0xaa0203f3,0x3165f4:0xaa1803e2,0x3165f8:0xaa1903e1,0x3165fc:0xaa1303e0}.items():n.ins(p,w)
 n.call(0x316600,0x2753c0)
 require(n.bl_sites(0x2753c0)==[0x316600,0x35511c,0x3552c8,0x3553f4,0x3554e8], 'unexpected buildTreeFromText direct callsites')
 require(route.symbol(b'_ZN7utility23SubtreeConditionOptNode6onInitEv')==0x5b29b0,'SubtreeConditionOptNode onInit symbol differs')
 require(route.va(0xf9e498,len(b'subtree_file_path\0'))==b'subtree_file_path\0','subtree parameter key differs')
 require((0x5b29b8,0x5b29bc) in route.adrp_add_references(0xf9e498),'onInit not referencing subtree_file_path')
 route.call(0x5b2a20,0x44e820) # TreeNode::getParamImpl<string>
 route.call(0x5b3098,0x442d40) # TreeNode::blackboard
 for p,w in {0x5b30b4:0xaa1403e2,0x5b30b8:0xaa1703e1}.items():route.ins(p,w)
 route.call(0x5b30bc,0x44d5e0) # BT::buildTreeFromFile
 route.call(0x5b31c4,0x4484c0) # BehaviorTreeFactory::tree_builders()
 require(route.bl_sites(0x44d5e0)==[0x5b30bc],'unexpected buildTreeFromFile call census')
 require(beh.symbol(b'_ZN2BT19BehaviorTreeFactoryC2Ev')==0x61aa0,'BehaviorTreeFactory constructor differs')
 require(beh.va(0xaa3c0,len(b'SubtreeCondition\0'))==b'SubtreeCondition\0','built-in registration name differs')
 require(beh.adrp_add_references(0xaa3c0)==[(0x62edc,0x62ee0)],'built-in registration reference differs')
 beh.call(0x62f20,0x3a290)  # BT::SubtreeConditionNode::requiredNodeParameters()
 beh.call(0x62f48,0x3a8c0)  # BehaviorTreeFactory::registerBuilder
 require(beh.symbol(b'_ZN2BT20SubtreeConditionNode6onInitEv')==0x757b0,'built-in onInit differs')
 require(beh.va(0xaa4f0,len(b'subtree_file_path\0'))==b'subtree_file_path\0','built-in subtree parameter differs')
 require((0x757b8,0x757bc) in beh.adrp_add_references(0xaa4f0),'built-in onInit subtree key reference differs')
 beh.call(0x75b8c,0x38f00)  # BT::TreeNode::blackboard()
 for p,w in {0x75ba0:0xaa1703e2,0x75ba4:0xaa1803e1,0x75ba8:0xaa1a03e0}.items():beh.ins(p,w)
 beh.call(0x75bb0,0x39260)  # BT::buildTreeFromFile(..., x2=Blackboard)
 beh.call(0x75de8,0x39180)  # registered builder lookup
 require(tree.va(0x56832e,len(b'SubtreeCondition\0'))==b'SubtreeCondition\0','compiled node name differs')
 robot_subtree=[(a,b) for a,b in tree.adrp_add_references(0x56832e) if 0x30d8c0<=a<0x312c6c]
 expected=[0x30dc20,0x30e3b8,0x30ee48,0x30f554,0x30ff8c,0x3111f0]
 require([a for a,b in robot_subtree]==expected,'RobotNode subtree creation reference census differs')
 for addr,pair in robot_subtree:
  require(pair==addr+4,'unexpected generated node name preparation')
  tree.call(addr+0x10,0x1c6620)  # child_node_factory_instantiateTreeNode
 require(tree.va(0x578590,len(b'StationWash\0'))==b'StationWash\0','StationWash builder name differs')
 require(tree.symbol(b'_Z16buildStationWashRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE')==0x358540,'StationWash native builder symbol differs')
 require(tree.symbol(b'_Z14buildRobotNodeRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE')==0x312c6c,'RobotNode native builder symbol differs')
 print('PASS 5 original ELF SHA-256 pins and 3 original/runtime byte comparisons')
 print('PASS v27 effective RobotNode and /tmp/lib/tree_lib// configuration')
 print('PASS BtTask assembles SubtreeCondition subtree_file_path wrapper; passes supplied Blackboard into buildTreeFromText')
 print('PASS bounded node_lethe buildTreeFromText call census (5 sites)')
 print('PASS default BehaviorTreeFactory registers SubtreeCondition to BT::SubtreeConditionNode; onInit passes Blackboard into buildTreeFromFile')
 print('PASS separate SubtreeConditionOptNode onInit also has subtree_file_path and a conditional buildTreeFromFile path')
 print('PASS six compiled RobotNode SubtreeCondition child-node instantiations via factory')
 print('PASS bounded route_nodes buildTreeFromFile census (1 site) and registered-builder map reference')
 print('X40_V28_DYNAMIC_SUBTREE_STATIC_PASS')
 print('BOUNDARY: Built-in SubtreeCondition default registration is verified; later plugin replacement is untested.')
 print('          Cannot show StationWash selected, same Blackboard at runtime, R2416 special-push producer, or physical rewash.')



def decode_static_conststr(elf, table, count):
 """Decode fixed compiled ConstStr pair table, not user data or ELF code execution."""
 require(0<count<=6, 'unreasonable table entry count')
 result=[]
 for row in range(count):
  kv=[]
  for col in range(2):
   ptr,n=struct.unpack('<QQ',elf.va(table+32*row+16*col,16))
   require(0<n<=256, 'invalid or non-constant parameter length')
   value=elf.va(ptr,n).decode('ascii')
   kv.append((ptr,n,value))
  result.append(kv)
 return result

def table_address(elf, adrp, add):
 w=elf.word(adrp)
 require((w&0x9f00001f)==0x90000001, 'expected ADRP x1')
 w2=elf.word(add)
 require((w2&0xffc003ff)==0x91000021, 'expected ADD x1,x1,#imm')
 imm=((((w>>5)&0x7ffff)<<2)|((w>>29)&3))
 if imm&(1<<20):imm-=1<<21
 require(((w2>>22)&1)==0, 'unexpected scaled add')
 return ((adrp&~0xfff)+(imm<<12))+((w2>>10)&0xfff)

SITES=[
 (0x30dc20,0x6fd0d0,'PlanningReuseRestartCleaning'),
 (0x30e3b8,0x6ee190,'LongTimePauseStrategy.xml'),
 (0x30ee48,0x6f8350,'StationWash.xml'),
 (0x30f554,0x6f7ff0,'AlwaysSuccess.xml'),
 (0x30ff8c,0x6edab0,'SearchChargeEnding'),
 (0x3111f0,0x6facf0,'LabOldTestIndex'),
]

def verify_v29(reference, runtime):
 # v28 checks pins, original/runtime equivalence, direct site census and
 # default SubtreeCondition factory semantics before v29 parameter work.
 verify(reference,runtime)
 tree=collect(reference,runtime)['liblethe_tree.so']
 for site,table,expected in SITES:
  require(tree.word(site-0x10)==0xd2800042,'expected mov x2,#2')
  require(table_address(tree,site-0xc,site-0x8)==table,'parameter table address moved')
  tree.call(site-0x4,0x2b390c)
  pars=decode_static_conststr(tree,table,2)
  require([(x[0][2],x[1][2]) for x in pars]==[
   ('expand_in_logger','true'),('subtree_file_path',expected)
  ],f'subtree parameters differ at {site:#x}')
  if expected=='StationWash.xml':
   require(pars[1][1][0]==0x58eb2a and pars[1][1][1]==15, 'StationWash literal address/length changed')
  print(f'PASS direct RobotNode SubtreeCondition site {site:#x}: subtree_file_path={expected}')

 # The direct-preparation census is not an exhaustive instantiation census:
 # x21 is callee-saved, and the next node reuses the SubtreeCondition name.
 require(tree.word(0x30ee80)==0x910cbaa1, 'missing reused x21 SubtreeCondition name')
 tree.call(0x30ee8c,0x1c6620)
 reused=decode_static_conststr(tree,0x6f8470,2)
 require([(k[0][2],k[1][2]) for k in reused]==[
  ('expand_in_logger','true'),('subtree_file_path','RobotDropCharger')
 ],'adjacent reused-name site changed')
 print('PASS adjacent reused-register SubtreeCondition at 0x30ee80: RobotDropCharger')

 # The actual StationWash builder is registered in the same pinned ELF;
 # validate via an ELF dynamic relocation, not a same-name substring.
 syms=tree.section('.dynsym'); raw=tree.secbytes(syms)
 strings=tree.secbytes(tree.sec[syms['link']]);target=b'_Z16buildStationWashRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE'
 matches=[]
 for i in range(0,len(raw),24):
  k,_,_,_,val,_=struct.unpack_from('<IBBHQQ',raw,i)
  if strings[k:strings.find(b'\0',k)]==target:matches.append((i//24,val))
 require(matches==[(matches[0][0],0x358540)] if matches else False,'StationWash exported builder location differs')
 rel=tree.section('.rela.dyn');entries=tree.secbytes(rel)
 got=[]
 for i in range(0,len(entries),24):
  r_off,r_info,r_add=struct.unpack_from('<QQq',entries,i)
  if r_off==0x7b1c50:got.append((r_info>>32,r_info&0xffffffff,r_add))
 require(got==[(matches[0][0],1025,0)],'StationWash builder GOT relocation differs')
 tree.call(0x566278,0x1c6930)
 print('PASS independently pinned StationWash builder relocation and registration call')
 print('X40_V29_ROBOTNODE_STATIONWASH_PARAMETER_PASS')
 print('BOUNDARY: Compiled structural linkage only: no demonstrated runtime tick, shared Blackboard identity,')
 print('          R2416-compatible special_push_clean_dish producer, or physical extra dock wash.')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('firmware_reference_zip')
 parser.add_argument('v27_runtime_zip')
 opts=parser.parse_args()
 try:verify_v29(opts.firmware_reference_zip,opts.v27_runtime_zip)
 except (ValueError,KeyError,IndexError,OSError,EOFError,UnicodeError,struct.error,zipfile.BadZipFile,tarfile.TarError) as e:
  print('X40_V29_ROBOTNODE_STATIONWASH_PARAMETER_FAIL: '+str(e),file=sys.stderr);sys.exit(1)
