#!/usr/bin/env python3
"""Bounded offline v208 check of AiStainMop file-path fallback and six ELFs."""
import argparse
import hashlib
import struct
from pathlib import Path
import sys
from zipfile import ZipFile,BadZipFile
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'x40-r2416-v207-tools'))
from x40_r2416_v207_repo_check import audit,exported_builders
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'x40-r2416-v206-tools'))
from x40_r2416_v206_repo_check import va_bytes,word,bltarget,require as need

PINS={
 'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
 'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
 'liblethe_tactics_tree.so':'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
 'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
 'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
 'node_health_lethe.so':'5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5',
}
WORDS={
 'libbehaviortree_cpp.so':{
   0x757dc:0x910303f8,0x75800:0xaa1803e2,
   0x75b88:0xaa1503e0,0x75b8c:0x97ff0cdd,
   0x75ba0:0xaa1703e2,0x75ba4:0xaa1803e1,
   0x75ba8:0xaa1a03e0,0x75bb0:0x97ff0dac,
   0x75de8:0x97ff0ce6,0x75f8c:0xaa1703e2,
   0x75f9c:0xd63f0060,0x70244:0xaa0103f4,
   0x7027c:0xaa1403e1,0x70280:0xaa1703e0,
   0x70284:0x97ff2603,
 },
 'liblethe_tree.so':{
   0x1cb3e8:0xf00025e1,0x1cb3ec:0x911dc021,
   0x1cb3f0:0x97fff9d9,0x1cb400:0x97ffec88,
 },
}
EDGES={
 ('libbehaviortree_cpp.so',0x75b8c):0x38f00,
 ('libbehaviortree_cpp.so',0x75bb0):0x39260,
 ('libbehaviortree_cpp.so',0x75de8):0x39180,
 ('libbehaviortree_cpp.so',0x70284):0x39a90,
 ('liblethe_tree.so',0x1cb3f0):0x1c9b54,
 ('liblethe_tree.so',0x1cb400):0x1c6620,
}
def verify(prior):
 need(audit(prior)==(158,199,138,20),'v207 native builder coverage changed')
 images={}
 with ZipFile(prior) as z:
  for name,digest in PINS.items():
   found=[p for p in z.namelist() if '/files/'+name+'/' in p]
   need(len(found)==1,'Missing/ambiguous original ELF '+name)
   d=z.read(found[0]);need(hashlib.sha256(d).hexdigest()==digest,'Original ELF SHA mismatch: '+name)
   images[name]=d
 for name,words in WORDS.items():
  for va,opcode in words.items():
   need(word(images[name],va)==opcode,'Native opcode changed '+name+':'+hex(va))
 for (name,va),target in EDGES.items():
  need(bltarget(va,word(images[name],va))==target,'Native call target changed '+name+':'+hex(va))
 builders={name:exported_builders(d) for name,d in images.items()}
 need({name:len(x) for name,x in builders.items()}==
      {name:(199 if name=='liblethe_tree.so' else 0) for name in PINS},
      'Six ELF exported build census changed')
 need(all('buildAiStainMop' not in x for x in builders.values()),
      'Unexpected exported AiStainMop builder')
 return len(PINS),sum(map(len,WORDS.values())),len(EDGES)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prior-zip',required=True);a=p.parse_args()
 try:
  print('X40_R2416_V208_REPO_ORIGINAL_FILE_FALLBACK_PASS',*verify(a.prior_zip))
  print('Compiled API paths only; no live file resolution or second cleaning task proven.')
 except (OSError,ValueError,struct.error,BadZipFile) as e:
  raise SystemExit('X40_R2416_V208_REPO_FAIL: '+str(e))
