#!/usr/bin/env python3
"""Bounded, read-only X40 R2416 v200 native JSON ordering verifier.

Python 3 standard library only. Private collector ZIPs are inputs, never
extracted to disk. This repo-side subset is smaller than the full v200 kit.
"""
import argparse
import hashlib
import json
import struct
import zipfile

HOST_SHA="b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0"
REDACTED_SHA="7395f5b43168caa2c28c4e1ed9bc1225f513cc93bc907029e3d493896e8c4745"
WORDS={
  0x62b0bc:0x52800301, 0x62b0c0:0x9ba15040, 0x62b0e4:0x91006294,
  0x62b0fc:0x97f13715, 0x62b130:0xf94053e1, 0x62b138:0x97f13eb2,
  0x62b13c:0x340006c0, 0x62b14c:0x97f13ead, 0x62b150:0x34001060,
  0x62b160:0x97f13ea8, 0x62b164:0x35fffbe0, 0x62b214:0xf9403be1,
  0x62b224:0x97f1493b, 0x62b228:0xb9400002, 0x62b230:0xf9400400,
  0x62b238:0x9ba10041, 0x62b260:0x91006000, 0x62b27c:0xb9400003,
  0x62b280:0xb9401802, 0x62b284:0xf9407be0, 0x62b29c:0x97f11d09,
  0x62b2a4:0xf94087e0, 0x62b2b8:0x54000f60, 0x62b2c0:0xa94e07e0,
  0x62b30c:0xeb01001f, 0x62b320:0xf8626803, 0x62b328:0x91002042,
  0x62b330:0x54ffff81, 0x62b340:0x910060a1, 0x62b344:0xf90087e1,
  0x62b35c:0xf9403be1, 0x62b370:0xb9400002, 0x62b378:0xf9400400,
  0x62b3c8:0x97f125e2, 0x62b3cc:0x1e624000, 0x62b3d0:0xb9409be1,
  0x62b3dc:0xbd00bfe0, 0x62b3e0:0xf9407be0, 0x62b3f4:0x97f13367,
  0x62b490:0xf94047e1, 0x62b498:0x910060a1, 0x62b4a0:0x17ffffaa,
  0x62b4ac:0x97f11e55, 0x62b548:0xf94047e1,
}
EDGES={
  0x62b13c:('cbz',0x62b214),
  0x62b150:('cbz',0x62b35c),
  0x62b164:('cbnz',0x62b0e0),
  0x62b2b8:('cond',0x62b4a4),
  0x62b330:('cond',0x62b320),
  0x62b4a0:('b',0x62b348),
  0x62b4ac:('bl',0x272e00),
  0x62b3c8:('bl',0x274b50),
}
def check(ok, what):
    if not ok: raise ValueError(what)

def va_bytes(blob, va, length):
    check(blob[:6]==b'\x7fELF\x02\x01' and
          struct.unpack_from('<H',blob,18)[0]==183,'Expected ARM64 little-endian ELF')
    p=struct.unpack_from('<Q',blob,32)[0]
    size,n=struct.unpack_from('<HH',blob,54)
    check(size>=56 and n<100 and p+size*n<=len(blob),'Bad ELF headers')
    for i in range(n):
        kind,_,off,vaddr,_,length_file,_,_=struct.unpack_from('<IIQQQQQQ',blob,p+i*size)
        if kind==1 and vaddr<=va and va+length<=vaddr+length_file:
            start=off+va-vaddr
            check(start+length<=len(blob),'Truncated ELF')
            return blob[start:start+length]
    raise ValueError('ELF virtual address not file-backed')

def word(blob,va):
    return struct.unpack('<I',va_bytes(blob,va,4))[0]

def edge(at, insn, mode):
    if mode in ('b','bl'):
        check((insn&0xfc000000)==(0x94000000 if mode=='bl' else 0x14000000),'Unexpected branch kind')
        imm=insn&0x3ffffff; bits=26
    else:
        if mode=='cond':
            check((insn&0xff000010)==0x54000000,'Expected B.cond')
        else:
            check((insn&0x7e000000)==0x34000000 and ((insn>>24)&1)==(mode=='cbnz'),
                  'Expected CBZ/CBNZ polarity')
        imm=(insn>>5)&0x7ffff;bits=19
    if imm&(1<<(bits-1)):imm-=1<<bits
    return at+imm*4

def entry(z, pattern):
    found=[x for x in z.namelist() if pattern in x]
    check(len(found)==1,'Missing or ambiguous private evidence: '+pattern)
    raw=z.read(found[0])
    check(len(raw)<30_000_000,'Unexpected size')
    return raw

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    p.add_argument('--delta-zip',required=True)
    args=p.parse_args()
    with zipfile.ZipFile(args.prior_zip) as z:
        host=entry(z,'/files/node_lethe.so/')
    with zipfile.ZipFile(args.delta_zip) as z:
        raw=entry(z,'/files/turbidity_check_config.json/')
    check(hashlib.sha256(host).hexdigest()==HOST_SHA,'Host SHA256 mismatch')
    check(hashlib.sha256(raw).hexdigest()==REDACTED_SHA,'Saved redacted JSON SHA256 mismatch')
    for va, expected in WORDS.items():
        check(word(host,va)==expected,f'Native instruction mismatch at {va:#x}')
    for va,(mode,target) in EDGES.items():
        check(edge(va,word(host,va),mode)==target,f'Native branch changed at {va:#x}')
    for addr,name in ((0xa16360,b'table_a\x00'),(0xa16368,b'table_b\x00'),
                      (0xa16370,b'table_c\x00'),(0x9d5e28,b'value\x00')):
        check(va_bytes(host,addr,len(name))==name,'Native table key changed')
    j=json.loads(raw)
    check([i.get('id') for i in j['table_a']]==[0,1,2,3],
          'Saved A-series labels/order changed')
    check([len(i['value']) for i in j['table_a']]==[63,35,60,60],
          'Saved A-series array shape changed')
    print('X40_R2416_V200_REPO_JSON_NATIVE_ORDER_PASS')
    print(f'Exact original host SHA + {len(WORDS)} anchors + {len(EDGES)} native edges verified')
    print('This establishes compiled array ordering only, not live subtype or physical reclean.')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError,IndexError,struct.error,
            zipfile.BadZipFile) as exc:
        raise SystemExit('X40_R2416_V200_REPO_FAIL: '+str(exc))
