#!/usr/bin/env python3
"""Offline v230 original two-ELF sensor consumer audit (Python 3 stdlib).

Reads owner-private original collector ZIP, no robot/device connection.
Use the downloadable complete v230 ZIP for all 51 native words, mutation
tests, branch edges and the full inherited private evidence replay.
"""
import argparse,hashlib,struct,zipfile
HOST='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
HEALTH='5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5'
HOST_WORDS={
 0x783d84:0x97ebc367,0x783e84:0xaa0103f4,0x783ee4:0x97ebdc8f,
 0x7867b4:0xb0001261,0x7867b8:0x912c0021,0x7867d4:0x97ebc023,
 0x7871f4:0x90001261,0x7871f8:0x912c0021,0x787210:0x97ebbd94,
 0x7932a4:0xd2802300,0x7932d4:0xd2802102,0x7932e0:0x97eb8cc0,
 0x7b840c:0x97eb0335,0x7b872c:0x3943e801}
HEALTH_WORDS={
 0x4d1d4:0x97fff493,0x4d1e0:0x97fff978,0x4d1ec:0x39416262,
 0x4d1fc:0x39000002,0x4d220:0xa9ad7bfd,0x4d228:0xd2802102,
 0x4d238:0x910083e4,0x4d240:0xaa0403e0,0x4d250:0x97fff328,
 0x4d254:0xaa0003e1,0x4d25c:0x97fff719,0x4d26c:0x91000421,
 0x4d270:0xf903de61}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def check(path):
 with zipfile.ZipFile(path) as z:
  raws={}
  for name,sha in [('node_lethe.so',HOST),('node_health_lethe.so',HEALTH)]:
   names=[p for p in z.namelist() if '/files/'+name+'/' in p]
   need(len(names)==1,'Missing or ambiguous original library')
   raw=z.read(names[0])
   need(hashlib.sha256(raw).hexdigest()==sha,'Original SHA-256 mismatch')
   raws[name]=raw
 for name,words in [('node_lethe.so',HOST_WORDS),('node_health_lethe.so',HEALTH_WORDS)]:
  b=raws[name]
  need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,
       'Original AArch64 ELF64LE expected')
  for addr,opcode in words.items():
   need(struct.unpack_from('<I',b,addr)[0]==opcode,'Original opcode mismatch')
 b=raws['node_health_lethe.so']
 for addr in range(0x4b800,0xbac20,4):
  op=struct.unpack_from('<I',b,addr)[0]
  need(not(op&0xffc00000==0x39400000 and (op>>10)&0xfff==0xfa),
       'Additional direct health LDRB #0xfa')
 return len(HOST_WORDS),len(HEALTH_WORDS),264,264
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 try:
  print('X40_R2416_V230_REPO_TWO_ELF_SENSOR_PASS',*check(p.parse_args().prior_zip))
  print('No live shared sender, physical sensor meaning, dock wash or new floor task proven.')
 except (ValueError,OSError,IndexError,struct.error,zipfile.BadZipFile) as err:
  raise SystemExit('X40_R2416_V230_REPO_FAIL: '+str(err))
