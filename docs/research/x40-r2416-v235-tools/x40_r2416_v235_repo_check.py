#!/usr/bin/env python3
"""v235 original SHA-pinned health topic census. Python 3 stdlib; owner PRIVATE ZIP required.
The matching v234 checker on this research branch verifies all prior archive hashes.
This script executes no vendor code and makes no robot/network calls.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

prior = Path(__file__).resolve().parents[1]/'x40-r2416-v234-tools'
sys.path.insert(0, str(prior))
from x40_r2416_v234_repo_check import check as verify_v234, HEALTH_SHA

# (direct original call VA, ADRP VA, literal VA, expected name).
SITES = (
(0x61180,0x61118,0xbc3a0,'HEALTH'),
(0x61364,0x6131c,0xbc3a8,'NEW_HEALTH_ERROR_INFO'),
(0x61544,0x614fc,0xbc3c0,'LINELASERCAMERAERR'),
(0x61724,0x616dc,0xbc3d8,'STATIONSTATUSTYPE'),
(0x6190c,0x618bc,0xbc3f0,'HEALTH_MSG_EVENT_RECALL_CMD'),
(0xaf304,0xaf298,0xc0108,'SKID_DATA'),
(0xaf4a8,0xaf460,0xc0118,'SIGNAL_STATISTICS'),
(0xaf648,0xaf600,0xc0130,'HEALTH_MOTOR_CTRL'),
(0xaf7d4,0xaf79c,0xc0148,'HEALTH_BIG_DATA'),
(0xaf948,0xaf910,0xc0158,'HEALTH_CONFIG'),
(0xafad4,0xafa9c,0xc0168,'OBSTACLERECORD'),
(0xafc84,0xafc44,0xc0178,'DROPTOBLACKBOARD'),
(0xafdf0,0xafdbc,0xc0190,'LOWSPEEDFLAG'),
(0xaff60,0xaff28,0xc01a0,'WEAKESCAPE'),
(0xb00e8,0xb00b4,0xc01b0,'HBACKOFFBUMP'),
(0xb0254,0xb021c,0xc01c0,'HEALTH_TO_ROUTE'),
(0xb03a8,0xb0370,0xc01d0,'HEALTH_CLIFF'),
(0xb0544,0xb04fc,0xc01e0,'CLIFF_TOF_POWER_STATE'),
)

def w(b, a): return struct.unpack_from('<I', b, a)[0]
def signed(x, n): return x-(1<<n) if x & (1<<(n-1)) else x
def bl(pc, ins):
    if ins >> 26 != 0b100101: return None
    return pc + (signed(ins & 0x3ffffff, 26) << 2)
def adrp_add_pointer(b, a):
    x,y=w(b,a),w(b,a+4)
    if x & 0x9f000000 != 0x90000000 or y & 0xff000000 != 0x91000000:
        raise ValueError('Wrong original ADRP/ADD encoding')
    rd=x & 31
    if (y & 31)!=rd or ((y >> 5) & 31)!=rd or ((y >> 22) & 3):
        raise ValueError('Wrong original literal-source registers')
    delta=(((x >> 5)&0x7ffff)<<2)|((x >> 29)&3)
    return (a & ~4095)+(signed(delta,21)<<12)+((y >> 10)&4095)
def verify(path):
    verify_v234(path)
    with zipfile.ZipFile(path) as z:
        rows=[r for r in json.loads(z.read('manifest.PRIVATE.json'))['records']
              if r.get('status')=='saved']
        health=None
        matches=0
        native=0
        for r in rows:
            if r.get('category')!='native': continue
            native+=1
            b=z.read(r['stored_as'])
            matches += b.count(b'HEALTH_TO_ROUTE\x00')
            if hashlib.sha256(b).hexdigest()==HEALTH_SHA:
                if health is not None: raise ValueError('Duplicate original health ELF')
                health=b
    if len(rows)!=35 or native!=8 or health is None or matches!=1:
        raise ValueError('Expected owner-private original evidence incomplete')
    # Original fully SHA-pinned ELF has identical .text/.rodata VAs and offsets.
    if health[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',health,18)[0]!=183:
        raise ValueError('Original AArch64 ELF format mismatch')
    if health[0xbc270:0xbc278]!=b'SENSORS\x00':
        raise ValueError('Named sensor subscription literal mismatch')
    pubs=[];subs=[]
    for a in range(0x4b800,0xbac20,4):
        dest=bl(a,w(health,a))
        if dest==0x4a510: pubs.append(a)
        if dest==0x4b540: subs.append(a)
    if pubs!=[site for site,_,_,_ in SITES] or len(subs)!=40 or 0x5f36c not in subs:
        raise ValueError('Direct AVA registration census mismatch')
    for site,src,ptr,name in SITES:
        if adrp_add_pointer(health,src)!=ptr or health[ptr:ptr+len(name)+1]!=name.encode()+b'\x00':
            raise ValueError('Original named advertisement source mismatch')
    print('X40_R2416_V235_REPO_HEALTH_TOPIC_PASS',len(pubs),len(subs),len(rows))
if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v230-private',required=True)
    verify(p.parse_args().v230_private)
