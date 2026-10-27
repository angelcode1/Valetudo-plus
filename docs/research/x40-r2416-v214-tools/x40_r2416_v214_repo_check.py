#!/usr/bin/env python3
"""Offline original R2416 native plugin ABI audit. Python 3 stdlib only."""
import argparse,hashlib,struct,zipfile
PINS={
 'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
 'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'liblethe_tactics_tree.so':'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
 'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'}
ANCHORS={
 'node_lethe.so':{0x350e14:0x97fc8cdf,0x350e30:0x91004c13,0x350e4c:0x97fca4a5,0x350e50:0x340079a0,0x350e5c:0x97fc98c5,0x350e80:0x97fc9874,0x350f00:0x97fc94ec,0x350f2c:0x540015c0},
 'libbehaviortree_cpp.so':{0x5cc40:0x97ff7310,0x5cc50:0x97ff7294,0x5cc7c:0x97ff75a5,0x5cc98:0x34000579,0x5ccb8:0x97ff707a,0x5ccd8:0xd63f0280}}
def need(x,msg):
 if not x:raise ValueError(msg)
def va_bytes(b,va,n):
 need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,'Expected AArch64 ELF64LE')
 po=struct.unpack_from('<Q',b,32)[0];step,count=struct.unpack_from('<HH',b,54)
 need(step>=56 and 0<count<100 and po+step*count<=len(b),'Bad program headers')
 for i in range(count):
  typ,_,o,v,_,sz,_,_=struct.unpack_from('<IIQQQQQQ',b,po+step*i)
  if typ==1 and v<=va and va+n<=v+sz:
   at=o+va-v;need(at+n<=len(b),'Truncated PT_LOAD');return b[at:at+n]
 raise ValueError('Unmapped ELF VA')
def names(b):
 off=struct.unpack_from('<Q',b,40)[0];size,n=struct.unpack_from('<HH',b,58)
 need(size>=64 and 0<n<100 and off+size*n<=len(b),'Bad section headers')
 secs=[struct.unpack_from('<IIQQQQIIQQ',b,off+i*size) for i in range(n)]
 d=[x for x in secs if x[1]==11];need(len(d)==1,'Missing dynamic symbols');d=d[0]
 need(d[9]>=24 and d[5]%d[9]==0 and 0<=d[6]<n and d[4]+d[5]<=len(b),'Bad dynsym bounds')
 st=secs[d[6]];end=st[4]+st[5];need(st[1]==3 and end<=len(b),'Bad dynstr bounds')
 out={}
 for at in range(d[4],d[4]+d[5],d[9]):
  index,info,_,shndx,_,_=struct.unpack_from('<IBBHQQ',b,at)
  if info&15!=2:continue
  start=st[4]+index;need(st[4]<=start<end,'Bad symbol name index')
  terminator=b.find(b'\0',start,end);need(terminator>=start,'Unterminated symbol')
  name=b[start:terminator].decode('ascii','replace')
  if name:out[name]=bool(shndx)
 return out
def run(prior):
 with zipfile.ZipFile(prior) as z:
  imgs={}
  for name,sha in PINS.items():
   matches=[p for p in z.namelist() if '/files/'+name+'/' in p]
   need(len(matches)==1,'Missing/ambiguous source ELF '+name)
   b=z.read(matches[0]);need(hashlib.sha256(b).hexdigest()==sha,'ELF SHA mismatch '+name)
   imgs[name]=b
 for name,anchors in ANCHORS.items():
  for va,expected in anchors.items():
   insn=struct.unpack('<I',va_bytes(imgs[name],va,4))[0]
   need(insn==expected,'Original instruction mismatch '+name+' '+hex(va))
 need(va_bytes(imgs['node_lethe.so'],0x9d5a78,4)==b'.so\0','Plugin suffix changed')
 need(va_bytes(imgs['libbehaviortree_cpp.so'],0xaca80,27)==b'BT_RegisterNodesFromPlugin\0',
      'Native entrypoint name changed')
 n=0
 for name in ('liblethe_tree.so','liblethe_tactics_tree.so','liblethe_route_nodes.so'):
  symbols=names(imgs[name]);need(symbols.get('BT_RegisterNodesFromPlugin') is True,'Plugin entrypoint missing')
  has_tree=sum('registerTreeBuilder' in k and not defined for k,defined in symbols.items())
  has_node=sum('registerBuilder' in k and 'registerTreeBuilder' not in k and not defined for k,defined in symbols.items())
  need(has_tree==(name=='liblethe_tree.so') and has_node==(name!='liblethe_tree.so'),
       'Native plugin builder API changed '+name)
  n+=1
 return n,sum(len(x) for x in ANCHORS.values())
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prior-zip',required=True);a=p.parse_args()
 try:
  print('X40_R2416_V214_REPO_PLUGIN_ABI_STATIC_PASS',*run(a.prior_zip))
  print('For 199 actual name/GOT callback pairs and full prior replay use the complete v214 kit.')
 except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit('X40_R2416_V214_REPO_FAIL: '+str(e))
