#!/usr/bin/env python3
"""Original R2416 SHA-pinned mop-dirty consumer direct-call audit. Offline only."""
import argparse,hashlib,struct,zipfile
SHA="b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0"
WORDS={0x3db47c:0x97fa8549,0x3db484:0x97fa7ca7,0x3db598:0x97fa6a12,
0x5dcfec:0xf00021a1,0x5dcff0:0x91122021,0x5dd010:0x97f2716c,
0x5dd024:0xd00021a1,0x5dd028:0x91122021,0x7b8b10:0xf00012c1,
0x7b8b14:0x91122021,0x7b8b28:0xb40022e0,0x7b8b38:0xd63f0040,
0x7b8b40:0x54002220,0x7b88d8:0x97eaf48e,0x7b8c18:0x97eaf3be}
HOST={0x27c9a0:[0x3db47c],0x27a720:[0x3db484],0x275de0:[0x3db598]}
MOP={0x275b10:[0x7b88d8,0x7b8c18]}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def calls(binary,lo,hi,expect):
 hits={v:[] for v in expect}
 for at in range(lo,hi,4):
  op=struct.unpack_from("<I",binary,at)[0]
  if op&0xfc000000!=0x94000000:continue
  delta=op&0x3ffffff
  if delta&0x2000000:delta-=0x4000000
  to=at+4*delta
  if to in hits:hits[to].append(at)
 need(hits==expect,"Native direct caller census changed")
def check(path):
 with zipfile.ZipFile(path) as z:
  files=[n for n in z.namelist() if "/files/node_lethe.so/" in n]
  need(len(files)==1,"Expected one original host ELF")
  b=z.read(files[0])
 need(hashlib.sha256(b).hexdigest()==SHA,"Original host SHA changed")
 need(b[0xa13488:0xa13488+25]==b"ai_set_mop_is_dirty_data\0",
      "Dirty-mop key changed")
 for at,op in WORDS.items():
  need(struct.unpack_from("<I",b,at)[0]==op,"Changed instruction "+hex(at))
 calls(b,0x27e5f0,0x9cdd40,HOST)
 calls(b,0x7b8360,0x7b977c,MOP)
 return len(WORDS),len(HOST),len(MOP[0x275b10])
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--prior-zip",required=True)
 a=p.parse_args()
 try:print("X40_R2416_V224_REPO_DIRTY_MOP_MCU_PASS",*check(a.prior_zip))
 except (OSError,ValueError,struct.error,zipfile.BadZipFile) as e:
  raise SystemExit("X40_R2416_V224_REPO_FAIL: "+str(e))
