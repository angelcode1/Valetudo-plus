#!/usr/bin/env python3
"""Offline, SHA-pinned X40 R2416 station guards checker (Python 3 stdlib).

Only reads the owner's original PRIVATE firmware ZIP. Does not execute code
on the robot or send commands. Complete v197-v227 proof: download v227 kit.
"""
import argparse
import hashlib
import struct
import zipfile

SHA='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
WORDS={
 0x7b83d0:0xf00010c2,0x7b83d4:0x912c0042,0x7b840c:0x97eb0335,
 0x7b8584:0xd00010e1,0x7b8588:0x9109c021,0x7b85a4:0x97eb04d7,
 0x7b85e8:0xf00010c3,0x7b85ec:0x913f2063,0x7b8618:0x97eb0f92,
 0x7b8638:0xf00013c3,0x7b863c:0x91094063,0x7b8668:0x97eae9a6,
 0x7b8688:0x7100401f,0x7b8694:0x7100081f,0x7b871c:0x540026cd,
 0x7b8730:0x7100103f,0x7b88c4:0x52800403,0x7b88d8:0x97eaf48e,
 0x7b8ac8:0x52800783,0x7b8acc:0xd00012e1,0x7b8ad0:0x9105a021,
 0x7b8af0:0x97eaff78,0x7b8b60:0x52823267,0x7b8b94:0x6b07003f,
 0x7b8bd0:0x1e273001,0x7b8bf8:0x52805dc5,0x7b8bfc:0x52800426,
 0x7b8c18:0x97eaf3be,
}
KEYS={
 'AvaSensors':(0x9d3b00,0x7b83d0,0x7b83d4,2),
 'open_stain_identify':(0x9d6270,0x7b8584,0x7b8588,1),
 'RobotMode':(0x9d3fc8,0x7b85e8,0x7b85ec,3),
 'wash_status':(0xa33250,0x7b8638,0x7b863c,3),
 'mop_stain_check_time':(0xa16168,0x7b8acc,0x7b8ad0,1),
 'ai_set_mop_is_dirty_data':(0xa13488,0x7b8b10,0x7b8b14,1),
}

def need(ok,msg):
 if not ok:
  raise ValueError(msg)

def key_pointer(at,adrp,add,reg):
 need(adrp&0x9f00001f==(0x90000000|reg),'Expected ADRP')
 need(add&0xffc003ff==(0x91000000|reg|(reg<<5)),
      'Expected same-register ADD')
 imm=(((adrp>>5)&0x7ffff)<<2)|((adrp>>29)&3)
 if imm&(1<<20):
  imm-=1<<21
 return (at&~4095)+(imm<<12)+((add>>10)&4095)

def check(path):
 with zipfile.ZipFile(path) as z:
  members=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
  need(len(members)==1,'Expected one owner original ELF')
  raw=z.read(members[0])
 need(hashlib.sha256(raw).hexdigest()==SHA,'Original ELF SHA mismatch')
 need(raw[:6]==b'\x7fELF\x02\x01'
      and struct.unpack_from('<H',raw,18)[0]==183,
      'Expected original AArch64 ELF64LE')
 def word(va):
  return struct.unpack_from('<I',raw,va)[0]
 for at,expected in WORDS.items():
  need(word(at)==expected,'Original native opcode mismatch')
 for key,(string_va,at,following,reg) in KEYS.items():
  need(raw[string_va:string_va+len(key)+1]==key.encode()+b'\0',
       'Original named key changed')
  need(key_pointer(at,word(at),word(following),reg)==string_va,
       'Compiled key reference changed')
 return len(WORDS),len(KEYS),60,25,750,4499

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--prior-zip',required=True)
 args=parser.parse_args()
 try:
  print('X40_R2416_V227_REPO_STATION_GUARDS_PASS',*check(args.prior_zip))
  print('OEM numeric meanings and physical mop rewash are unproven.')
 except (ValueError,OSError,IndexError,struct.error,zipfile.BadZipFile) as error:
  raise SystemExit('X40_R2416_V227_REPO_FAIL: '+str(error))
