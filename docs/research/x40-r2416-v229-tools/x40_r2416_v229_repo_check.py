#!/usr/bin/env python3
"""Original SHA-pinned R2416 typed sensor callback/retained byte audit, offline only.

Python 3 standard library. No robot communication or firmware execution.
Original owner PRIVATE ELF required locally, not redistributed.
"""
import argparse,hashlib,struct,zipfile

PIN='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
WORDS={
0x783d08:0x39416282,0x783d18:0x39072062,0x783d34:0xf940d884,
0x783d4c:0xf9000873,0x783d68:0xf9401e73,0x783d84:0x97ebc367,
0x783e84:0xaa0103f4,0x783edc:0x9103f281,0x783ee4:0x97ebdc8f,
0x7932a4:0xd2802300,0x7932d4:0xd2802102,0x7932dc:0xaa0403e0,
0x7932e0:0x97eb8cc0,0x7b872c:0x3943e801,0x7b8730:0x7100103f,
0x7b8734:0x54003240,0x7b873c:0x394b8002,0x7b8740:0x6b01005f,
0x7b8744:0x54000aa0,0x7b8808:0x3943e863,0x7b8814:0x97eaee07,
0x7b8890:0x3943e821,0x7b8894:0x390b8001,0x7b88d8:0x97eaf48e}
CALLS={0x274b20:[0x783d84],0x27b120:[0x783ee4]}

def need(ok,msg):
 if not ok:raise ValueError(msg)
def got_reloc(b,slot):
 shoff=struct.unpack_from('<Q',b,40)[0]
 stride,count=struct.unpack_from('<HH',b,58)
 need(stride>=64 and 0<count<100 and shoff+stride*count<=len(b),'ELF sections invalid')
 sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*stride) for i in range(count)]
 result=[]
 for sec in sections:
  if sec[1]!=4 or sec[9]<24:continue
  for at in range(sec[4],sec[4]+sec[5],sec[9]):
   target,info,_=struct.unpack_from('<QQq',b,at)
   if target!=slot:continue
   need(info&0xffffffff==1025,'Expected AArch64 GLOB_DAT')
   sym=sections[sec[6]]
   need(sym[9]>=24 and (info>>32)*sym[9]+24<=sym[5],'Invalid dynamic symbol')
   result.append(struct.unpack_from('<Q',b,sym[4]+(info>>32)*sym[9]+8)[0])
 need(len(result)==1,'Expected one original GOT relocation')
 return result[0]
def verify(path):
 with zipfile.ZipFile(path) as z:
  names=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
  need(len(names)==1,'Expected original host ELF')
  b=z.read(names[0])
 need(hashlib.sha256(b).hexdigest()==PIN,'Original host SHA changed')
 need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,
      'Expected original AArch64 ELF64LE')
 for at,op in WORDS.items():
  need(struct.unpack_from('<I',b,at)[0]==op,'Original machine word changed')
 need(got_reloc(b,0xb784c0)==0x783ce0 and got_reloc(b,0xb7b1b0)==0x783e70,
      'Exact original sensor callback binding changed')
 found={dest:[] for dest in CALLS}
 reads=[]
 for at in range(0x2a0000,0x9c0000,4):
  op=struct.unpack_from('<I',b,at)[0]
  if op&0xffc00000==0x39400000 and ((op>>10)&0xfff)==0xfa:reads.append(at)
  if op&0xfc000000!=0x94000000:continue
  imm=op&0x3ffffff
  if imm&0x2000000:imm-=0x4000000
  dest=at+imm*4
  if dest in found:found[dest].append(at)
 need(found==CALLS,'Original typed sensor or battery handler caller census changed')
 need(reads==[0x7b872c,0x7b8808,0x7b8890],
      'Original sensor offset+0xfa unsigned byte-read census changed')
 return len(WORDS),2,len(reads),264,250
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prior-zip',required=True)
 try:
  print('X40_R2416_V229_REPO_TYPED_SENSOR_PATH_PASS',*verify(p.parse_args().prior_zip))
  print('Sensor semantics, runtime callback delivery, wash and floor reclean remain unproven.')
 except (ValueError,OSError,IndexError,struct.error,zipfile.BadZipFile) as exc:
  raise SystemExit('X40_R2416_V229_REPO_FAIL: '+str(exc))
