#!/usr/bin/env python3
"""v203 bounded process-static BT::Tree* cache lifetime audit (Python stdlib).
Pass only the owner's PRIVATE collector archive; it is read in memory.
The complete v197-v203 verifier and mutation tests are in the offline ZIP.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import sys
from zipfile import ZipFile,BadZipFile

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'x40-r2416-v202-tools'))
from x40_r2416_v202_repo_check import verify as verify_v202,word,need,PIN

WORDS={
  0x74e94:0xf9401417,0x74eac:0xf94002e0,
  0x74eb8:0x97ff13d6,0x74f48:0xaa1703e0,0x74f4c:0x97ff12c9,
  0x752f0:0x97ff0f00,0x75390:0x97ff11d0,0x75578:0x97ff0e8e,
  0x759b8:0x90000333,0x759bc:0x9116c274,0x759c4:0x08dffec0,
  0x759c8:0x36003000,0x759e8:0x97ff1026,0x75a10:0x97ff101c,
  0x75ac4:0xf94022c0,0x75ac8:0xb4000580,0x75acc:0xf9400000,
  0x75ad0:0xa9027ea0,0x75b68:0x97fffdfa,0x75bb8:0xa9025aa0,
  0x75c90:0x97fffdb0,0x75c98:0xf90022b6,
  0x75fcc:0x97ff11c1,0x75ff8:0x97ff0f22,0x76000:0x97ff0d6c,
}
EDGES={
   (0x74f4c,'bl'):0x39a70,(0x759e8,'bl'):0x39a80,
   (0x75a10,'bl'):0x39a80,(0x75ac8,'cbz'):0x75b78,
   (0x75b68,'bl'):0x75350,(0x75c90,'bl'):0x75350,
   (0x75ff8,'bl'):0x39c80,(0x76000,'bl'):0x395b0,
}

def target(at,insn,kind):
    if kind=='bl':
        need((insn&0xfc000000)==0x94000000,'Unexpected BL')
        n=insn&0x3ffffff;bits=26
    elif kind=='cbz':
        need((insn&0x7f000000)==0x34000000,'Unexpected CBZ')
        n=(insn>>5)&0x7ffff;bits=19
    else:raise ValueError(kind)
    if n&(1<<(bits-1)):n-=1<<bits
    return at+n*4

def check(elf):
    verify_v202(elf)
    need(hashlib.sha256(elf).hexdigest()==PIN,'ELF SHA-256 changed')
    for va,expected in WORDS.items():
        need(word(elf,va)==expected,'Changed native instruction at %#x'%va)
    for (va,kind),expected in EDGES.items():
        need(target(va,word(elf,va),kind)==expected,
             'Changed branch/call at %#x'%va)
    need(b'PN2BT4TreeE' in elf and b'_Rb_tree' in elf,'Tree* map symbol missing')
    guard=word(elf,0x759c8)
    need((guard&0x7e000000)==0x36000000,'Unexpected TBZ/TBNZ guard')
    off=(guard>>5)&0x3fff
    if off&0x2000:off-=0x4000
    need(0x759c8+off*4==0x75fc8,'Static cache init target changed')
    # Count all direct BLs in the exact 352-byte owner-node destructor.
    # Whole-file pin allows VA==file offset assumptions only through PT_LOAD:
    # the v202 module's word() resolves each instruction VA with ELF headers.
    calls=[]
    for va in range(0x74e80,0x74e80+352,4):
        insn=word(elf,va)
        if (insn&0xfc000000)==0x94000000:
            calls.append((va,target(va,insn,'bl')))
    need(len(calls)==5,'Scoped destructor direct-call census changed')
    need((0x74f4c,0x39a70) in calls,'Tree owner delete call missing')
    need(not {dest for _,dest in calls} & {0x39a80,0x75350},
         'Unexpected direct cache lookup or insertion in destructor')
    return len(WORDS),len(EDGES)+1,len(calls)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    args=p.parse_args()
    with ZipFile(args.prior_zip) as z:
        found=[x for x in z.namelist() if '/files/libbehaviortree_cpp.so/' in x]
        need(len(found)==1,'Missing/ambiguous owner original library')
        results=check(z.read(found[0]))
    print('X40_R2416_V203_REPO_CACHE_LIFETIME_STATIC_PASS',
          *results)
    print('Static ownership hazard only; no observed live use-after-free.')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,IndexError,struct.error,BadZipFile) as exc:
        raise SystemExit('X40_R2416_V203_REPO_FAIL: '+str(exc))
