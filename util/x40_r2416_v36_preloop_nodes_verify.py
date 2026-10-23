#!/usr/bin/env python3
"""Dreame X40 R2416 v36 offline root pre-Loop node census audit.

Inputs: X40-Firmware-Reference.zip X40-R2416-v27.zip.
Never executes ELF content, contacts the robot, changes device state, or accesses the network.
The static result does not establish actual ticks, R2416 eligibility or physical rewash.
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



def verify_v30(reference, runtime):
    # First reproduce every v29 ELF, runtime, factory and parameter-table check.
    verify_v29(reference, runtime)
    elfs=collect(reference,runtime)
    beh=elfs['libbehaviortree_cpp.so']
    tree=elfs['liblethe_tree.so']

    # Exact known source parameter from the generated RobotNode ConstStr table.
    entries=decode_static_conststr(tree,0x6f8350,2)
    require(entries[1][1][2]=='StationWash.xml','unexpected station-wash source parameter')
    src=entries[1][1][2]
    require(src.count('.')==1 and '/' not in src and src.rfind('.')>0,'source string outside verified no-directory extension case')
    basename=src[:src.rfind('.')]
    require(basename=='StationWash', 'unexpected derived builder name')
    require(tree.va(0x578590,len(basename)+1)==basename.encode()+b'\0','registered native builder name differs')

    # Built-in onInit: two distinct std::string::find_last_of delimiters,
    # then the no-slash, non-empty-extension-prefix branch.
    require(beh.symbol(b'_ZN2BT20SubtreeConditionNode6onInitEv')==0x757b0,'onInit entry moved')
    require(beh.va(0xad900,2)==b'.\0','extension delimiter changed')
    require(beh.va(0xad370,2)==b'/\0','directory delimiter changed')
    require((0x75844,0x75848) in beh.adrp_add_references(0xad900),'dot delimiter preparation differs')
    require((0x75858,0x75860) in beh.adrp_add_references(0xad370,max_gap=12),'slash delimiter preparation differs')
    beh.call(0x7584c,0x3a970)
    beh.call(0x75870,0x3a970)
    for addr,word in {
      0x75888:0xb100041f, # cmn x0,#1 (no slash sentinel)
      0x75898:0xb100069f, # cmn x20,#1 (no dot sentinel)
      0x758a4:0xb5003b34, # cbnz x20 => nonzero dot position
      0x76008:0xf94063f3, # load original string pointer
      0x76010:0x9a819294, # bound prefix length by total length
      0x76034:0xf9005bf4, # size of basename substring
      0x75dd8:0xf94077e0, # load basename size
      0x75de0:0xb4ffed40, # empty basename -> file path
      0x75f8c:0xaa1703e2, # x2 = node Blackboard for callback
      0x75f90:0xaa1a03e1, # x1 = factory argument
      0x75f94:0xaa1c03e0, # x0 = builder wrapper pointer
      0x75f98:0xaa1603e8, # indirect result storage
      0x75f9c:0xd63f0060, # blr x3 (registered builder invocation)
    }.items():beh.ins(addr,word)
    # Explicit branch destination and transfer checks; not a live C++ execution.
    require((beh.word(0x75894)&0xff000010)==0x54000000,'no-slash conditional branch changed')
    def branch_target(addr):
        w=beh.word(addr);signed=((w>>5)&0x7ffff)
        if signed&(1<<18):signed-=1<<19
        return addr+signed*4
    require(branch_target(0x75894)==0x75ca0,'has-slash branch destination changed')
    require((beh.word(0x758a4)&0x7f00001f)==0x35000014,'nonempty dot branch is no longer CBNZ x20')
    require(branch_target(0x758a4)==0x76008,'nonempty-dot branch destination differs')
    beh.call(0x759e8,0x39a80) # optional existing-tree cache lookup
    beh.call(0x75de8,0x39180) # tree_builders()
    beh.call(0x75f68,0x38f00) # TreeNode::blackboard()
    beh.call(0x75b8c,0x38f00)
    beh.call(0x75bb0,0x39260) # separate fallback buildTreeFromFile path
    require(beh.word(0x75f58)==0xd63f0060,'builder function-holder invocation changed')
    # Known complete published native StationWash builder + forwarded Blackboard.
    tree.call(0x566278,0x1c6930) # native StationWash registration
    tree.call(0x358574,0x1c6720) # native StationWash build -> init_fac
    require(tree.word(0x567ba0)==0xaa0103f6,'factory init helper no longer saves supplied Blackboard argument')
    require(tree.word(0x567bd8)==0xa901d4b6,'factory init helper stored-Blackboard field changed')

    print('PASS basename derivation in compiled SubtreeCondition onInit: StationWash.xml -> StationWash')
    print('PASS std::string last-of delimiter probes, no-slash/nonzero-dot decision, and basename construction anchors')
    print('PASS cache lookup and registered-builder lookup, plus indirect builder callback with TreeNode::blackboard()')
    print('PASS native StationWash factory registration and Blackboard-forwarding helper')
    print('X40_V30_STATIONWASH_RESOLVER_STATIC_PASS')
    print('BOUNDARY: exact compiled mechanism, not proof of plugin registry at runtime, StationWash tick,')
    print('          a R2416 special_push_clean_dish producer, or second physical wash.')



def verify_v31(reference, runtime):
    verify_v30(reference, runtime)
    x=collect(reference,runtime)
    route=x['liblethe_route_nodes.so']
    beh=x['libbehaviortree_cpp.so']
    n=x['node_lethe.so']
    tree=x['liblethe_tree.so']
    tac=x['liblethe_tactics_tree.so']

    # Exact C-string check: the route plugin's node is named
    # 'SubtreeConditionOpt', not the built-in 'SubtreeCondition'.
    require(route.va(0xf9f318,20)==b'SubtreeConditionOpt\0',
            'route plugin registered name changed')
    require(route.adrp_add_references(0xf9f318)==[(0x4f2bf0,0x4f2bf4)],
            'route registration name xref census changed')
    route.call(0x4f2bf8,0x489e30) # copy exact name into std::string
    route.call(0x4f2c04,0x4e14c0) # construct typed SubtreeConditionOpt function holder
    route.call(0x4f2b98,0x43b910) # earlier related builder registration
    # The named SubtreeConditionOpt registration follows the above name
    # preparation. Its typed factory handler and actual registerBuilder call
    # are at 0x4f2c04 and 0x4f2c38 respectively.
    route.call(0x4f2c38,0x4a94f0)
    require(route.symbol(b'BT_RegisterNodesFromPlugin')==0x48cc80,
            'route plugin entrypoint changed')
    # B to PLT trampoline, not BL; verify target.
    branch=route.word(0x48cc80)
    require(branch&0xfc000000==0x14000000, 'route plugin entrypoint is not B')
    delta=branch&0x3ffffff
    if delta&(1<<25): delta-=1<<26
    require(0x48cc80+delta*4==0x43f9b0,'route plugin entrypoint target changed')

    # Built-in registration remains distinct, and duplicate registration
    # normally throws rather than updating an existing builder mapping.
    require(beh.va(0xaa3c0,17)==b'SubtreeCondition\0',
            'built-in exact registration name changed')
    require(beh.adrp_add_references(0xaa3c0)==[(0x62edc,0x62ee0)],
            'built-in registration reference changed')
    beh.call(0x62f48,0x3a8c0) # BT::BehaviorTreeFactory::registerBuilder@plt
    require(beh.symbol(b'_ZN2BT19BehaviorTreeFactory15registerBuilderERKNS_16TreeNodeManifestESt8functionIFSt10unique_ptrINS_8TreeNodeESt14default_deleteIS6_EERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEERKNS_14NodeParametersEEE')==0x5e1c0,
            'BehaviorTreeFactory::registerBuilder location changed')
    beh.call(0x5e230,0x39330) # memcmp existing key
    beh.call(0x5e2ac,0x39310) # allocate exception on duplicate
    beh.call(0x5e2e8,0x3a060) # BehaviorTreeException constructor
    beh.call(0x5e328,0x3a520) # __cxa_throw

    # Native AVA route constructs the factory, enumerates plugin-directory
    # entries and invokes registerFromPlugin per selected entry. Plugin
    # iteration order depends on directory state: do not assert ordering.
    n.call(0x350e14,0x274190) # opendir
    n.call(0x350e5c,0x277170) # readdir
    n.call(0x350e80,0x277050) # BehaviorTreeFactory::ctor
    n.call(0x350f00,0x2762b0) # registerFromPlugin
    require(n.bl_sites(0x2762b0)==[0x350f00],
            'unexpected directly called registerFromPlugin sites')
    # No declared unregisterBuilder import within the three collected
    # plugin libraries. This is an import census, not a global proof of
    # the runtime's registry state or absence of indirect operations.
    for label, f in [('route_nodes',route),('tactics_tree',tac),('compiled_tree',tree)]:
        require(b'unregisterBuilder' not in f.secbytes(f.section('.dynstr')),
                f'{label}: newly imported unregisterBuilder')

    # Add bounded local parent/sibling evidence without claiming runtime tick.
    p=decode_static_conststr(tree,0x6f8350,2)
    q=decode_static_conststr(tree,0x6f8470,2)
    require(p[1][1][2]=='StationWash.xml' and q[1][1][2]=='RobotDropCharger',
            'adjacent RobotNode subtree parameter changed')
    for addr in [0x30ee58,0x30ee8c]:tree.call(addr,0x1c6620)
    for addr in [0x30ee64,0x30ee98]:tree.call(addr,0x1c6900)
    for addr in [0x30ee68,0x30ee9c]:tree.call(addr,0x1c6640)
    print('PASS registered built-in SubtreeCondition vs separate route plugin SubtreeConditionOpt')
    print('PASS route plugin entrypoint and typed registration; duplicate builder guard throws')
    print('PASS factory construction, directory enumeration, registerFromPlugin invocation')
    print('PASS bounded three-plugin dynamic-import census: no direct unregisterBuilder import')
    print('PASS adjacent RobotNode StationWash.xml / RobotDropCharger child construction')
    print('X40_V31_PLUGIN_REGISTRATION_STATIC_PASS')
    print('BOUNDARY: directory-order and complete plugin registry cannot be proven from these files;')
    print('          no actual StationWash tick, R2416 special_push producer or physical rewash proven.')



def verify_v32(reference, runtime):
    """Verify bounded structural evidence; never infer the current tick path."""
    verify_v31(reference, runtime)
    x=collect(reference, runtime)
    tree=x['liblethe_tree.so']
    route=x['liblethe_route_nodes.so']
    tactics=x['liblethe_tactics_tree.so']
    node=x['node_lethe.so']

    # Runtime plugin directory inventory is supplied as a separate manual
    # ls/hash observation. These are all three named tree plugins in that
    # snapshot, and each has a real BT_RegisterNodesFromPlugin entrypoint.
    expected_exports={'liblethe_tree.so':0x562b4c,
                      'liblethe_tactics_tree.so':0xd1620,
                      'liblethe_route_nodes.so':0x48cc80}
    for name, expected in expected_exports.items():
        require(x[name].symbol(b'BT_RegisterNodesFromPlugin') == expected,
                'BT plugin registration ABI moved: '+name)

    # Three neighbouring child constructors. The helper call in between
    # StationKeyProcess and StationWash is a DIFFERENT builder function;
    # no assumption is made about its internal depth-stack effect.
    require(tree.va(0x585f7e,18)==b'StationKeyProcess\0',
            'preceding StationKeyProcess factory literal differs')
    tree.ins(0x30ee0c,0xf00013a1) # ADRP x1
    tree.ins(0x30ee10,0x913df821) # ADD x1, x1, #0xf7e
    tree.call(0x30ee1c,0x1c6620) # instantiate native node
    tree.call(0x30ee28,0x1c6900) # prior control-parent child
    tree.call(0x30ee30,0x2edb70) # intervening nested builder
    tree.call(0x30ee58,0x1c6620) # StationWash.xml
    tree.call(0x30ee64,0x1c6900)
    tree.call(0x30ee68,0x1c6640)
    tree.call(0x30ee8c,0x1c6620) # RobotDropCharger
    tree.call(0x30ee98,0x1c6900)
    tree.call(0x30ee9c,0x1c6640)
    require(decode_static_conststr(tree,0x6f8350,2)[1][1][2]=='StationWash.xml',
            'StationWash parameter changed')
    require(decode_static_conststr(tree,0x6f8470,2)[1][1][2]=='RobotDropCharger',
            'RobotDropCharger parameter changed')
    # Native generated node creation is unconditional in this small region;
    # tree execution is *not* unconditional. No depth-stack changes between
    # these two factory calls, therefore they are emitted in one local scope.
    for target, label in [(0x1c6730,'increase_depth'),
                          (0x1c6810,'decrease_depth'),
                          (0x1c6800,'decorator_parent_setChild')]:
        sites=[a for a in tree.bl_sites(target) if 0x30ee58<a<=0x30ee9c]
        require(not sites, f'{label} appeared between StationWash and RobotDropCharger')

    # Repeat the bounded primary-string census on all five pinned libraries;
    # this does NOT exclude dynamically constructed/inherited Blackboard keys.
    literal=b'special_push_clean_dish'
    for label in ('node_lethe.so','liblethe_tree.so','liblethe_tactics_tree.so',
                  'liblethe_route_nodes.so','libbehaviortree_cpp.so'):
        f=x[label]
        c=f.b.count(literal)
        require(c==(1 if label in ('node_lethe.so','liblethe_tree.so',
                                  'liblethe_tactics_tree.so') else 0),
                f'changed exact key literal count: {label}')
    lit_addr=node.b.index(literal)
    # Derive its target VA from the binary PT_LOAD program mapping rather
    # than relying on a fixed filename offset.
    vals=[]
    for start,end,off in node.loads:
        if off<=lit_addr<off+(end-start): vals.append(start+lit_addr-off)
    require(len(vals)==1,'ambiguous node_lethe string VA')
    require(node.adrp_add_references(vals[0])==[(0x47052c,0x470530),
                                                 (0x7ca20c,0x7ca210)],
            'unexpected node_lethe direct key references')
    # R2416 is not in the three explicit model tests that gate that setter.
    # The model-specific branch truth table is separately verified in v20.
    print('PASS active tree plugin set corresponds to three pinned BT registration exports')
    print('PASS local RobotNode StationKeyProcess -> helper -> StationWash/RobotDropCharger construction sites')
    print('PASS no generated depth/decorator calls between StationWash and RobotDropCharger attachments')
    print('PASS five-library direct key literal census and two AVA direct reference sites')
    print('X40_V32_LOCAL_PARENT_AND_KEY_CENSUS_PASS')
    print('BOUNDARY: parent identity/tick, effective runtime Blackboard, and R2416 key producer unresolved.')



def decode_bl_or_b(f, address):
    """Return (branch kind, target) for immediate AArch64 BL/B."""
    w=f.word(address)
    op=w & 0xfc000000
    require(op in (0x94000000,0x14000000), f'not a BL/B at {address:#x}')
    d=w & 0x3ffffff
    if d & (1<<25): d-=1<<26
    return ('BL' if op==0x94000000 else 'B', address+4*d)


def depth_ledger(f,start,last):
    """Compiled callsite ledger: count direct BL and tail B to depth helpers.

    Does not emulate the program or model exception edges; these are bounded
    disassembly facts, NOT a proof of behaviour-tree runtime state.
    """
    require(start%4==last%4==0 and start<=last,'unaligned/empty range')
    entries=[]
    depth=0
    for address in range(start,last+4,4):
        w=f.word(address)
        if w&0xfc000000 not in (0x94000000,0x14000000):continue
        kind,target=decode_bl_or_b(f,address)
        if target==0x1c6730:
            require(kind=='BL','unexpected tail branch to increase_depth')
            depth+=1;entries.append((address,kind,'increase',depth))
        elif target==0x1c6810:
            depth-=1;entries.append((address,kind,'decrease',depth))
            require(depth>=0, f'negative compiled depth at {address:#x}')
    return entries,depth


def verify_v33(reference,runtime):
    verify_v32(reference,runtime)
    f=collect(reference,runtime)['liblethe_tree.so']

    # Validate that 0x2edb70 is not an unbounded fallthrough into 0x30ee30:
    # it ends with a tail B to decrease_depth, preserving the link register.
    require(decode_bl_or_b(f,0x2ee9c8)==('B',0x1c6810),
            'nested helper tail-call endpoint changed')
    require(decode_bl_or_b(f,0x30ee30)==('BL',0x2edb70),
            'RobotNode intervening helper call changed')
    require(decode_bl_or_b(f,0x311fac)==('B',0x1c6810),
            'RobotNode constructor tail-call endpoint changed')
    require(f.bl_sites(0x2edb70)==[0x30ee30],
            'unexpected direct callers of nested builder helper')

    helper,helper_final=depth_ledger(f,0x2edb70,0x2ee9c8)
    require(helper_final==0,'nested helper direct depth calls not balanced')
    require(sum(e[2]=='increase' for e in helper)==27 and
            sum(e[2]=='decrease' for e in helper)==27,
            'nested helper exact increase/decrease census changed')
    require(helper[0][:3]==(0x2edb98,'BL','increase') and
            helper[-1][:3]==(0x2ee9c8,'B','decrease'),
            'nested helper entry/end depth events changed')

    main,main_final=depth_ledger(f,0x30d8c0,0x311fac)
    require(main_final==0,'RobotNode direct depth calls not balanced')
    require(sum(e[2]=='increase' for e in main)==76 and
            sum(e[2]=='decrease' for e in main)==76,
            'RobotNode exact depth-event census changed')

    # Compile-time parent stack immediately prior to StationWash allocation.
    # The helper is a separate balanced call; no claim about successful
    # physical runtime execution or exception paths.
    seen=[]
    for addr,kind,operation,_ in main:
        if addr>=0x30ee58:break
        if operation=='increase':seen.append(addr)
        else:
            require(seen,'unbalanced RobotNode prefix')
            seen.pop()
    require(seen==[0x30d90c,0x30e124,0x30e154],
            'RobotNode constructor depth stack at StationWash changed')

    # Decode exact node strings and the instruction-level constructors
    # associated with those three outstanding depth frames.
    names=[(0x5692ec,b'SequenceStarRoF\0'),(0x586085,b'Loop\0'),
           (0x56930a,b'DoWhile\0')]
    for address,name in names:
        require(f.va(address,len(name))==name,'node name changed: '+name.decode())
    for addr in (0x30d8fc,0x30e110,0x30e140,
                 0x30ee58,0x30ee8c):f.call(addr,0x1c6620)
    for addr in (0x30d90c,0x30e124,0x30e154):f.call(addr,0x1c6730)
    f.call(0x30e11c,0x1c6900)  # Loop control-parent attachment
    f.call(0x30e14c,0x1c6800)  # DoWhile decorator-child attachment
    for addr in (0x30ee64,0x30ee98):f.call(addr,0x1c6900)
    for addr in (0x30ee68,0x30ee9c):f.call(addr,0x1c6640)
    require((0x30e100,0x30e104) in f.adrp_add_references(0x586085),
            'Loop constructor name-reference pair changed')
    require((0x30e12c,0x30e130) in f.adrp_add_references(0x56930a),
            'DoWhile constructor name-reference pair changed')
    require(decode_static_conststr(f,0x6eeeb0,1)[0] ==
            [(0x56cd14,10,'num_cycles'),(0x595f4a,2,'-1')],
            'Loop configuration ConstStr differs')
    require(decode_static_conststr(f,0x6f8350,2)[1][1][2]=='StationWash.xml',
            'StationWash parameter changed')
    require(decode_static_conststr(f,0x6f8470,2)[1][1][2]=='RobotDropCharger',
            'adjacent RobotDropCharger parameter changed')

    # The base BT implementation gives a narrow, compiled interpretation for
    # the negative cycle count: the tick uses a signed >=0 guard before
    # comparing the number of completed cycles with the configured bound.
    # This proves only its branch behaviour, not unlimited dock washing.
    bt=collect(reference,runtime)['libbehaviortree_cpp.so']
    require(bt.symbol(b'_ZN2BT8LoopNode4tickEv')==0x8bad0,
            'LoopNode tick symbol differs')
    require(bt.symbol(b'_ZN2BT11DoWhileNode4tickEv')==0x96fc0,
            'DoWhileNode tick symbol differs')
    for addr,word in {
        0x8bb30:0x29450662, # load signed cycle bound / completed count
        0x8bb3c:0x7100005f, # cmp w2,#0
        0x8bb40:0x7a42a021, # ccmp w1,w2,#1,ge
        0x8bb44:0x5400040a, # b.ge on bounded-cycle path
        0x96fe8:0x340018c1, # child-count zero branch
        0x97024:0xd63f0020, # child virtual tick call
    }.items():bt.ins(addr,word)
    require(decode_bl_or_b(f,0x30ee30)==('BL',0x2edb70),
            'nested helper callsite changed during tick checks')

    # Preserve caveat: a direct address census and balanced callsite ledger
    # cannot prove ticker scheduling, runtime active Blackboard or rewash.
    print('PASS exact nested helper 0x2edb70: 27 increases, 27 decreases; tail B at 0x2ee9c8')
    print('PASS RobotNode 0x30d8c0: 76 increases, 76 decreases; tail B at 0x311fac')
    print('PASS active depth stack before StationWash: SequenceStarRoF > Loop > DoWhile')
    print('PASS Loop num_cycles=-1; tick uses signed nonnegative-bound guard before cycle-limit compare')
    print('PASS DoWhile has distinct nonempty-child and child-tick code paths')
    print('PASS StationWash and RobotDropCharger consecutive control-parent child attachments')
    print('X40_V33_STATIONWASH_PARENT_DEPTH_STATIC_PASS')
    print('BOUNDARY: conditional runtime ticks, effective Blackboard, R2416 special-push producer,')
    print('          and physical rewash remain unproven.')



def decode_bcond_target(f,address):
    w=f.word(address)
    require(w&0xff000010==0x54000000, f'not conditional B at {address:#x}')
    x=(w>>5)&0x7ffff
    if x&(1<<18):x-=1<<19
    return address+4*x

def decode_cbz_target(f,address):
    w=f.word(address)
    require(w&0x7e000000==0x34000000, f'not CBZ at {address:#x}')
    x=(w>>5)&0x7ffff
    if x&(1<<18):x-=1<<19
    return address+4*x


def dowhile_direct_attach_sites(f):
    # Track direct generated depth helper calls only in the root constructor.
    # Subroutine 0x2edb70 has separately passed the v33 balanced-depth check.
    # This counts static callsites, NOT the resulting total runtime children.
    depth=[]
    hits=[]
    for a in range(0x30d8c0,0x311fac,4):
        w=f.word(a)
        if w&0xfc000000!=0x94000000:
            continue
        kind,target=decode_bl_or_b(f,a)
        if target==0x1c6900 and depth and depth[-1]==0x30e154:
            hits.append(a)
        elif target==0x1c6730:
            depth.append(a)
        elif target==0x1c6810:
            require(depth, f'compiled depth underflow at {a:#x}')
            depth.pop()
    return hits


def verify_v34(reference,runtime):
    verify_v33(reference,runtime)
    src=collect(reference,runtime)
    bt=src['libbehaviortree_cpp.so']
    tree=src['liblethe_tree.so']
    require(bt.symbol(b'_ZN2BT11DoWhileNode4tickEv')==0x96fc0,
            'DoWhile tick symbol changed')

    # Child vector extent and empty case.
    for a,w in {
      0x96fd4:0xf94006e1, # current child-vector end
      0x96fdc:0xf9401000, # beginning of vector
      0x96fe8:0x340018c1, # cbz w1 => no children
      0x97300:0x5280003b, # return numeric status 1 for zero-child case
    }.items():bt.ins(a,w)
    require(decode_cbz_target(bt,0x96fe8)==0x97300,
            'DoWhile zero-child edge changed')

    # Main loop reads children[i] and calls their virtual tick slot.
    # The non-final-child path does not compare w27 (child status) to
    # success/failure for an early return: it always advances to next.
    for a,w in {
      0x9701c:0xaa1403e0, # x0=child
      0x97020:0xf9400c21, # x1=child vtable tick method +0x18
      0x97024:0xd63f0020, # blr x1
      0x97030:0xf940003c, # status logger (not status guard)
      0x97048:0x7100077f, # compare status to numeric 1
      0x9704c:0x54000040, # branch if status equals 1 => index update
      0x97050:0x3900669f, # otherwise clear child running byte
      0x97054:0x11000673, # index++
      0x97058:0x910022b5, # child pointer += 8
      0x9705c:0x6b13031f, # index == child count?
      0x97060:0x54000740, # end loop after last child
      0x97064:0xf94002e0, # reload child vector for next iteration
      0x97070:0xf8756814, # child pointer at current index
      0x97148:0x7100077f, # compare FINAL observed child status with numeric 1
      0x9714c:0x54000180, # branch if final status == 1
      0x97154:0x52800001, # haltChildren(0) argument
      0x9715c:0x2a1b03e0, # return final status after halt
      0x9717c:0x2a1b03e0, # return final status without halt
    }.items():bt.ins(a,w)
    require(decode_bcond_target(bt,0x9704c)==0x97054,
            'per-child numeric-1 status branch does not advance')
    require(decode_bcond_target(bt,0x97060)==0x97148,
            'last-child exit destination changed')
    require(decode_bcond_target(bt,0x9714c)==0x9717c,
            'final status no-halt path changed')
    require(decode_bl_or_b(bt,0x97158)==('BL',0x397e0),
            'final non-1 status no longer halts children')

    # Confirm generated RobotNode direct attachment order on the active
    # top-level DoWhile depth. Nested helper attachments are not counted.
    hits=dowhile_direct_attach_sites(tree)
    require(len(hits)==50,'DoWhile direct child-attachment census changed')
    require(hits[21:25]==[0x30ee28,0x30ee64,0x30ee98,0x30eed8],
            'expected StationKeyProcess / StationWash / RobotDropCharger order differs')
    for a in (0x30ee28,0x30ee64,0x30ee98):
        tree.call(a,0x1c6900)
    require(decode_static_conststr(tree,0x6f8350,2)[1][1][2]=='StationWash.xml',
            'StationWash parameter changed')
    require(decode_static_conststr(tree,0x6f8470,2)[1][1][2]=='RobotDropCharger',
            'RobotDropCharger parameter changed')

    print('PASS generated DoWhile parent has 50 direct control-child attachment callsites')
    print('PASS among direct sites: StationWash 23rd; RobotDropCharger 24th')
    print('PASS DoWhile tick loops through child vector without per-child status short circuit')
    print('PASS final returned numeric child status decides haltChildren(0) path')
    print('PASS DoWhile no-child branch returns numeric status 1')
    print('X40_V34_DOWHILE_TICK_ORDER_STATIC_PASS')
    print('BOUNDARY: compiled callsite count excludes nested helper sites; no runtime ticks,')
    print('          eligibility key producer or physical rewash is demonstrated.')



def root_direct_attachments_before_loop(tree):
    """Enumerate generated DIRECT calls for SequenceStarRoF root-child attachments.

    Only instructions in the main RobotNode builder are counted. This is NOT
    a runtime child array census and does not trace nested helper routines.
    """
    stack=[]
    hits=[]
    for a in range(0x30d8c0,0x30e124,4):
        w=tree.word(a)
        if w&0xfc000000 not in (0x94000000,0x14000000):
            continue
        kind,target=decode_bl_or_b(tree,a)
        if target==0x1c6730:
            require(kind=='BL',f'invalid increase-depth branch {a:#x}')
            stack.append(a)
        elif target==0x1c6810:
            require(stack,f'unbalanced depth {a:#x}')
            stack.pop()
        elif target==0x1c6900 and stack==[0x30d90c]:
            hits.append(a)
    require(stack==[0x30d90c],'root depth before Loop push differs')
    return hits


def verify_v35(reference, runtime):
    verify_v34(reference,runtime)
    source=collect(reference,runtime)
    bt=source['libbehaviortree_cpp.so']
    robot=source['liblethe_tree.so']
    require(bt.symbol(b'_ZN2BT19SequenceStarRoFNode4tickEv')==0x90ac0,
            'SequenceStarRoF tick symbol changed')
    require(bt.symbol(b'_ZN2BT8LoopNode4tickEv')==0x8bad0,
            'Loop tick symbol changed')
    checks={
        # SequenceStarRoF: load current index, child tick and switch.
        0x90b08:0xb9403a80, # current index [this+0x38]
        0x90b10:0x6b0002bf, # compare child-count/index
        0x90b14:0x54001729, # beyond child count
        0x90b50:0xd63f0020, # child virtual tick
        0x90b74:0x71000a7f, # status == 2?
        0x90b78:0x54000340, # yes: increment index
        0x90b7c:0x54000168, # status >2?
        0x90b80:0x34001673, # status ==0 exception path
        0x90b84:0x52800033, # status 1 return
        0x90ba8:0x71000e7f, # status ==3?
        0x90bac:0x54000221, # else retry/unknown status path
        0x90bbc:0xb9003a9f, # status3 resets current index
        0x90be0:0xb9403a80, # read index
        0x90be4:0x11000400, # increment
        0x90be8:0xb9003a80, # save new index
        0x90df8:0x52800053, # status2 for full sequence
        # Loop: child virtual tick, compare and increment completed cycles
        0x8bafc:0xf9401260, # loaded child at +0x20
        0x8bb04:0x39006661, # running byte at +0x19 set to 1
        0x8bb10:0xd63f0020, # child virtual tick
        0x8bb18:0x7100041f, # status == 1?
        0x8bb1c:0x54000180, # status1 returns without increment
        0x8bb20:0x51000801, # status minus 2
        0x8bb24:0x12001c21, # mask byte
        0x8bb28:0x7100043f, # status2/3 range check
        0x8bb2c:0x540000e8, # outside status2/3 bypass counter
        0x8bb30:0x29450662, # bound/completed counter
        0x8bb34:0x11000421, # increment cycle counter
        0x8bb38:0xb9002e61, # store
        0x8bb3c:0x7100005f, # bound >=0 test
        0x8bb40:0x7a42a021, # conditional compare
        0x8bb44:0x5400040a, # bounded exit
        0x8bb48:0x39406660, # running byte return
        0x8bbc4:0xb9002e7f, # reset bounded counter
    }
    for addr,word in checks.items():bt.ins(addr,word)
    for a,target in {
        0x90b78:0x90be0, # status2 advances
        0x90b7c:0x90ba8, # status 3+ dispatch
        0x90bac:0x90bf0, # status not 3
        0x8bb1c:0x8bb4c, # status1 fast return
        0x8bb2c:0x8bb48, # out of range bypass
        0x8bb44:0x8bbc4, # positive bound met
    }.items():
        require(decode_bcond_target(bt,a)==target,
                f'status branch changed: {a:#x}')
    require(decode_bl_or_b(bt,0x90bb8)==('BL',0x397e0),
            'SequenceStarRoF failure haltChildren call changed')
    require(decode_bl_or_b(bt,0x90bec)==('B',0x90b0c),
            'SequenceStarRoF success does not resume next sibling')
    require(decode_bl_or_b(bt,0x8bbc8)==('B',0x8bb4c),
            'Loop bound-hit return path changed')

    # 15 preceding DIRECT root attachments must return success to advance
    # before this Loop, assuming the usual tick sequence and absent status
    # alterations by the other child implementations.
    sites=root_direct_attachments_before_loop(robot)
    expected=[0x30d940,0x30d978,0x30d9b0,0x30d9e8,0x30da20,
              0x30da54,0x30da88,0x30dabc,0x30daec,0x30db24,
              0x30db60,0x30e03c,0x30e078,0x30e0b0,0x30e0e4,
              0x30e11c]
    require(sites==expected,
            'RobotNode direct root-child attachment sites preceding Loop changed')
    robot.call(0x30e110,0x1c6620)
    robot.call(0x30e11c,0x1c6900)
    robot.call(0x30e140,0x1c6620)
    robot.call(0x30e14c,0x1c6800)
    require(decode_static_conststr(robot,0x6eeeb0,1)[0][1][2]=='-1',
            'Loop num_cycles=-1 compiled parameter changed')

    print('PASS SequenceStarRoF status 2 increments index, status 1 retains index, status 3 resets/haltChildren')
    print('PASS Loop statuses 2/3 count completed iterations; status 1 bypasses counter')
    print('PASS Loop negative cycle-bound check skips fixed-limit exit; normal tick returns running flag 1')
    print('PASS 15 direct RobotNode root child attachments precede Loop constructor / 16th root attachment')
    print('PASS Loop decorator child is DoWhile; nested StationWash direct attachment verified in v34')
    print('X40_V35_SEQUENCE_LOOP_ENTRY_STATIC_PASS')
    print('BOUNDARY: direct callsite ledger not full runtime child count; runtime scheduling,')
    print('          R2416 special-push key production, and dock rewash remain unproven.')



# v36: bounded DIRECT root-child creation census; does not execute native code.
# Each row = root attach VA, factory-instantiation VA, exact factory name,
# exact instance name, parameter table/row count, ADRP+ADD pair or None.
# The seventh SetBlackboard has an empty value (length zero), deliberately
# retained rather than incorrectly interpreting it as False/0.
PRE_LOOP = (
 (0x30d940,0x30d934,'LDS_Switch','LDS_Switch',0x6e3a90,1,(0x30d918,0x30d91c),(('state','false'),)),
 (0x30d978,0x30d96c,'EraseBlackboard','EraseBlackboard',0x6e5c30,1,(0x30d950,0x30d954),(('key','playspeech_pause'),)),
 (0x30d9b0,0x30d9a4,'SetBlackboardWithType','SetBlackboardWithType',0x6ecd30,3,(0x30d988,0x30d98c),(('key','config_tick_frequency'),('type','int'),('value','25'))),
 (0x30d9e8,0x30d9dc,'SetMusicPlayPara','SetMusicPlayPara',0x6f6ef0,5,(0x30d9c0,0x30d9c4),(('Interrupt_En','false'),('MusicNumber','0'),('MusicPlayPerSecond','10'),('MusicPlayTimes','0'),('Output','RobotMusic'))),
 (0x30da20,0x30da14,'SetBlackboard','SetBlackboard',0x6f9770,2,(0x30d9f8,0x30d9fc),(('key','Start_Map_Load'),('value','true'))),
 (0x30da54,0x30da48,'SetBlackboard','SetBlackboard',0x6f1b90,2,(0x30da30,0x30da34),(('key','robot_status'),('value','normal'))),
 (0x30da88,0x30da7c,'SetBlackboard','SetBlackboard',0x6fa530,2,(0x30da64,0x30da68),(('key','robot_power_on'),('value',''))),
 (0x30dabc,0x30dab0,'SetBlackboard','SetBlackboard',0x6fb010,2,(0x30da98,0x30da9c),(('key','reset_wheel_before_clean'),('value','1'))),
 (0x30daec,0x30dadc,'GetSegmentMapFuncRunning','GetSegmentMapFuncRunning',None,0,None,()),
 (0x30db24,0x30db18,'SubTree','MapLoad',0x6eeed0,1,(0x30dafc,0x30db00),(('display_name','SubTree'),)),
 (0x30db60,0x30db54,'SubTree','RobotSysInit',0x6eeed0,1,(0x30db38,0x30db3c),(('display_name','SubTree'),)),
 (0x30e03c,0x30ded8,'SubTree','StationSysInit',0x6eeed0,1,(0x30debc,0x30dec0),(('display_name','SubTree'),)),
 (0x30e078,0x30e06c,'SubTree','RobotmodeInit',0x6eeed0,1,(0x30e050,0x30e054),(('display_name','SubTree'),)),
 (0x30e0b0,0x30e0a4,'SubtreeCondition','SubtreeCondition',0x6f7ff0,2,(0x30e08c,0x30e090),(('expand_in_logger','true'),('subtree_file_path','AlwaysSuccess.xml'))),
 (0x30e0e4,0x30e0d8,'SubtreeCondition','SubtreeCondition',0x6e5c90,2,(0x30e0c0,0x30e0c4),(('expand_in_logger','true'),('subtree_file_path','CountryGet.xml'))),
)

NAME_VAS={
 'LDS_Switch':0x578394, 'EraseBlackboard':0x5ae6c2,
 'SetBlackboardWithType':0x569398, 'SetMusicPlayPara':0x5699a7,
 'SetBlackboard':0x5692fc, 'GetSegmentMapFuncRunning':0x585ddf,
 'SubTree':0x58fcdc, 'MapLoad':0x585df8,
 'RobotSysInit':0x585e00, 'StationSysInit':0x585e79,
 'RobotmodeInit':0x585e88, 'SubtreeCondition':0x56832e,
}

def conststr_rows_with_empty(f,addr,n):
    """Validate ConstStr pairs and support the zero-length value in slot 7."""
    require(0<=n<=5,'table count out of bounded scope')
    rows=[]
    for idx in range(n):
        row=[]
        for col in range(2):
            ptr,count=struct.unpack('<QQ',f.va(addr+idx*32+col*16,16))
            require(0<=count<=128,'oversize ConstStr')
            # A length-0 ConstStr is possible; do not force boolean coercion.
            s=f.va(ptr,count).decode('ascii') if count else ''
            row.append(s)
        require(bool(row[0]),'empty parameter key')
        rows.append(tuple(row))
    return tuple(rows)

def va_cstr(f,addr):
    raw=f.va(addr,128)
    return raw[:raw.index(b'\0')].decode('ascii')

def verify_v36(ref_zip, runtime_zip):
    # v35 transitively validates v19-v35 handoff markers and all SHA pins.
    verify_v35(ref_zip,runtime_zip)
    tree=collect(ref_zip,runtime_zip)['liblethe_tree.so']
    require(va_cstr(tree,0x5692ec)=='SequenceStarRoF','root control node changed')
    require(root_direct_attachments_before_loop(tree)==[x[0] for x in PRE_LOOP]+[0x30e11c],
            'direct root attachment identity/order changed')
    for index,(attach,factory,kind,instance,tab,count,construct,expected) in enumerate(PRE_LOOP,1):
        tree.call(factory,0x1c6620)
        tree.call(attach,0x1c6900)
        require(va_cstr(tree,NAME_VAS[kind])==kind, 'type literal changed at slot '+str(index))
        require(va_cstr(tree,NAME_VAS[instance])==instance, 'instance literal changed at slot '+str(index))
        if tab is None:
            require(count==0 and construct is None and not expected,'unexpected argument at no-parameter node')
            # Blank ConstStr vector in factory's local scope.
            require(tree.word(factory-4)==0xf90047ff,'node without ConstStr no longer zero-initializes table')
        else:
            require(tree.word(construct[0]-4)&0x1f==2,'parameter count construction changed')
            require(table_address(tree,*construct)==tab, f'slot {index} parameter table not referenced')
            require(conststr_rows_with_empty(tree,tab,count)==expected,
                    f'slot {index} parameter value changed')
        print(f'{index:02d}. {attach:#x}: {kind} [{instance}] '+
              ', '.join(f'{k}={v!r}' for k,v in expected))
    # A source-layout branch skips C++ exception cleanups between the 12th
    # direct construction and its attach call. It does not skip the attach.
    require(decode_bl_or_b(tree,0x30dedc)==('B',0x30e034),
            'StationSysInit no longer reaches post-cleanup attachment')
    # This is a finite-site census, not proof that each node returns success.
    print('X40_V36_PRE_LOOP_DIRECT_NODES_STATIC_PASS')
    print('BOUNDARY: compiled root child attachments only; the status of individual init')
    print('subtrees, runtime instance identity and physical rewash remain unobserved.')

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('firmware_reference_zip')
    ap.add_argument('v27_runtime_zip')
    args=ap.parse_args()
    try:
        verify_v36(args.firmware_reference_zip,args.v27_runtime_zip)
    except (ValueError,KeyError,IndexError,OSError,EOFError,UnicodeError,
            struct.error,zipfile.BadZipFile,tarfile.TarError) as err:
        print('X40_V36_STATIC_FAIL: '+str(err),file=sys.stderr)
        sys.exit(1)

