#!/usr/bin/env python3
"""Bounded offline X40 R2416 v221 original production AI-handler check.

Standalone Python 3 stdlib only. Reads original PRIVATE collector ZIP but
emits no original ELF, private path, config or device data. The source-only
v221 ZIP supplies the full 52-word/21-edge and v197-v220 regression replay.
"""
import argparse,hashlib,struct,zipfile

PIN='b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0'
WORDS={
 0x5cec20:0xf00021b3,0x5cec24:0x91394261,0x5cec68:0xd63f0040,
 0x5cec78:0xf00021a0,0x5cec7c:0x91258000,0x5cecd0:0xd63f0040,
 0x5ced94:0x97f2b0ab,0x5cf148:0x97f2a096,0x5cf15c:0x97f2a651,
 0x5cf3d8:0x97f2b292,0x5cf5b0:0x97f2a364,0x5cfacc:0xb0002021,
 0x5cfad0:0x9134c021,0x5cfb18:0x97f292ee,0x5cfb38:0xb9408ff3,
 0x5cfb44:0x1a9f07fb,0x5cfb58:0x37000053,0x5cfb98:0xd00020e1,
 0x5cfb9c:0x912fc021,0x5cfc68:0x9130a381,0x5cfc78:0x97f2abe2,
 0x5cfc90:0x97f2abdc,0x5cfdc4:0x97fff127,0x5cfe28:0xd63f00a0,
}
LITERALS={
 'RobotAiSwitch':0x9d4d30,
 'current_motion_type':0x9edbf0,
 'Followwall':0x9edc28,
 'ai_model_info':0xa05960,
 'online_pqklfilename':0xa05e50,
}
BL={
 0x5cfb18:0x2746d0,0x5ced94:0x27b040,
 0x5cf148:0x2773a0,0x5cf15c:0x278aa0,0x5cf5b0:0x278340,
}
FORBIDDEN={0x27afd0,0x5d1fd0,0x5cd770,0x315ed0}
BODIES=((0x5cebc0,0x5cfa80),(0x5cfa80,0x5d0050))

def need(ok,why):
    if not ok: raise ValueError(why)
def get(raw,va,size):
    need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
         'Expected AArch64 ELF64LE')
    po=struct.unpack_from('<Q',raw,32)[0]
    step,count=struct.unpack_from('<HH',raw,54)
    need(step>=56 and 0<count<100 and po+step*count<=len(raw),
         'Malformed ELF PT_LOAD headers')
    for i in range(count):
        typ,_,off,start,_,length,_,_=struct.unpack_from('<IIQQQQQQ',raw,po+step*i)
        if typ==1 and start<=va and va+size<=start+length:
            at=off+va-start
            need(at+size<=len(raw),'Truncated native ELF')
            return raw[at:at+size]
    raise ValueError('Unmapped original VA')
def word(raw,va):return struct.unpack('<I',get(raw,va,4))[0]
def bl_target(at,op):
    need(op&0xfc000000==0x94000000,'Expected direct BL')
    delta=op&0x3ffffff
    if delta&0x2000000:delta-=0x4000000
    return at+4*delta

def check(path):
    with zipfile.ZipFile(path) as z:
        candidates=[n for n in z.namelist() if '/files/node_lethe.so/' in n]
        need(len(candidates)==1,'Missing/ambiguous original host')
        original=z.read(candidates[0])
    need(hashlib.sha256(original).hexdigest()==PIN,'Original ELF hash changed')
    for at,expected in WORDS.items():
        need(word(original,at)==expected,'Original AI opcode changed '+hex(at))
    for name,va in LITERALS.items():
        need(get(original,va,len(name)+1)==name.encode()+b'\0','Changed literal '+name)
    for at,dst in BL.items():
        need(bl_target(at,word(original,at))==dst,'Changed direct call '+hex(at))
    count=0
    for first,last in BODIES:
        for (op,),at in zip(struct.iter_unpack('<I',get(original,first,last-first)),
                             range(first,last,4)):
            if op&0xfc000000!=0x94000000:continue
            need(bl_target(at,op) not in FORBIDDEN,
                 'Unexpected direct task-stack or named AI-send call')
            count+=1
    need(count>20,'Incomplete native direct-call scan')
    return len(WORDS),len(LITERALS),0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior-zip',required=True)
    opts=parser.parse_args()
    try:
        print('X40_R2416_V221_REPO_AI_HANDLERS_BOUNDARY_PASS',*check(opts.prior_zip))
        print('Indirect scheduling and physical reclean are not excluded or proven.')
    except (OSError,ValueError,IndexError,TypeError,struct.error,zipfile.BadZipFile) as exc:
        raise SystemExit('X40_R2416_V221_REPO_FAIL: '+str(exc))
