#!/usr/bin/env python3
"""Bounded native R2416 direct registration NAME census; Python 3 stdlib only.

Full 199-callback GOT-relocation matching is in the separate v213 offline ZIP.
"""
import argparse,hashlib,re,struct,zipfile

PIN='9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99'
START,SIZE,PLT,CTOR=0x562b4c,20268,0x1c6930,0x56299c
def need(ok,why):
    if not ok:raise ValueError(why)
def file_va(b,va,n):
    need(b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183,'Not ARM64 ELF64LE')
    po=struct.unpack_from('<Q',b,32)[0];step,count=struct.unpack_from('<HH',b,54)
    need(step>=56 and 0<count<100 and po+step*count<=len(b),'Bad ELF load headers')
    for i in range(count):
        typ,_,off,v,_,size,_,_=struct.unpack_from('<IIQQQQQQ',b,po+step*i)
        if typ==1 and v<=va and va+n<=v+size:
            at=off+va-v;need(at+n<=len(b),'Truncated ELF load segment')
            return b[at:at+n]
    raise ValueError('Unmapped ELF address')
def word(b,va):return struct.unpack('<I',file_va(b,va,4))[0]
def branch(at,opcode):
    need(opcode&0xfc000000==0x94000000,'Not direct BL')
    val=opcode&0x3ffffff
    if val&(1<<25):val-=1<<26
    return at+4*val
def address(va,adrp,add):
    need(adrp&0x9f00001f==0x90000001 and add&0xffc003ff==0x91000021,'Not x1 ADRP/ADD')
    imm=(((adrp>>5)&0x7ffff)<<2)|((adrp>>29)&3)
    if imm&(1<<20):imm-=1<<21
    return (va&~4095)+(imm<<12)+((add>>10)&4095)
def exports(b):
    o=struct.unpack_from('<Q',b,40)[0];step,n=struct.unpack_from('<HH',b,58)
    need(step>=64 and 0<n<100 and o+step*n<=len(b),'Bad ELF sections')
    ss=[struct.unpack_from('<IIQQQQIIQQ',b,o+i*step) for i in range(n)]
    dyn=[s for s in ss if s[1]==11];need(len(dyn)==1,'Expected one .dynsym')
    d=dyn[0];st=ss[d[6]]
    need(d[9]>=24 and d[5]%d[9]==0 and d[4]+d[5]<=len(b) and st[4]+st[5]<=len(b),
         'Malformed ELF symbol/string section')
    names=set()
    for at in range(d[4],d[4]+d[5],d[9]):
        nameoffset,info,_,defined,_,_=struct.unpack_from('<IBBHQQ',b,at)
        if defined==0 or info&15!=2:continue
        begin=st[4]+nameoffset
        need(st[4]<=begin<st[4]+st[5],'Bad string table index')
        stop=b.find(b'\0',begin,st[4]+st[5])
        need(stop>=begin,'Unterminated ELF dynamic symbol')
        value=b[begin:stop].decode('ascii','replace')
        m=re.match(r'^_Z(\d+)',value)
        if m:
            n=int(m.group(1));simple=value[m.end():m.end()+n]
            if n>5 and len(simple)==n and simple.startswith('build'):names.add(simple[5:])
    return names
def census(b):
    need(hashlib.sha256(b).hexdigest()==PIN,'Original ELF SHA mismatch')
    need(word(b,START)==0xd10a83ff,'Plugin entry changed')
    calls=[]
    for va in range(START,START+SIZE,4):
        op=word(b,va)
        if op&0xfc000000==0x94000000 and branch(va,op)==PLT:calls.append(va)
    need(len(calls)==199 and (calls[0],calls[-1])==(0x562c80,0x566784),
         'Original registration call census changed')
    out=[]
    for i,call in enumerate(calls):
        prev=calls[i-1] if i else START-4
        matches=[]
        for at in range(prev+4,call-12,4):
            a,p,m,q=(word(b,at+4*j) for j in range(4))
            if a&0x9f00001f==0x90000001 and p&0xffc003ff==0x91000021 and \
               m&0xffe0ffff==0xaa0003e0 and q&0xfc000000==0x94000000 and \
               branch(at+12,q)==CTOR:
                key=file_va(b,address(at,a,p),112).split(b'\0',1)[0]
                need(0<len(key)<=100 and all(32<=x<127 for x in key),'Invalid registered ID')
                matches.append(key.decode('ascii'))
        need(len(matches)==1,'Missing/ambiguous native registered ID')
        out.append(matches[0])
    need(len(set(out))==199 and set(out)==exports(b),'Registered IDs differ from exported build names')
    need('AiStainMop' not in out and
         {'RobotNode','ReuseTree','StationWash','CleanSelectedAreas'}.issubset(out),
         'Unexpected native registered builder')
    return len(out),len(set(out))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    a=p.parse_args()
    try:
        with zipfile.ZipFile(a.prior_zip) as z:
            names=[x for x in z.namelist() if '/files/liblethe_tree.so/' in x]
            need(len(names)==1,'Missing/ambiguous original tree ELF')
            result=census(z.read(names[0]))
        print('X40_R2416_V213_REPO_DIRECT_REGISTERED_NAMES_PASS',*result)
        print('The full v213 offline ZIP additionally checks all 199 GOT callback relocations.')
    except (OSError,ValueError,IndexError,struct.error,zipfile.BadZipFile) as e:
        raise SystemExit('X40_R2416_V213_REPO_FAIL: '+str(e))
