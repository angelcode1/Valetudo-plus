#!/usr/bin/env python3
"""Compact offline R2416 v100 regression; full 34-mutation verifier in sanitized ZIP.

Usage: python3 x40_r2416_v100_compact_repo_regression.py ORIGINAL_OWNER_V62.zip
No device/network I/O, no vendor binary execution, and no source firmware export.
"""
import hashlib
import struct
import sys
import zipfile

PINS = {
    'libbehaviortree_cpp.so': ('/files/usr/lib/libbehaviortree_cpp.so', '665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94'),
    'liblethe_route_nodes.so': ('/files/usr/lib/tree_lib/liblethe_route_nodes.so', 'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e'),
    'liblethe_tree.so': ('/files/usr/lib/tree_lib/liblethe_tree.so', '9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99'),
}

class Original:
    def __init__(self, data):
        if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0] != 183:
            raise ValueError('not an AArch64 ELF')
        self.data = data
        off = struct.unpack_from('<Q',data,32)[0]
        ent,n = struct.unpack_from('<HH',data,54)
        if ent != 56 or not 0 < n < 100: raise ValueError('invalid ELF program headers')
        self.loads = []
        for i in range(n):
            kind,_,f,v,_,size,_,_ = struct.unpack_from('<IIQQQQQQ',data,off+i*ent)
            if kind==1:self.loads.append((v,v+size,f))
    def read(self,va,size):
        for start,end,offset in self.loads:
            if start<=va and va+size<=end:return self.data[offset+va-start:offset+va-start+size]
        raise ValueError('unmapped ELF virtual address')
    def word(self,va):return struct.unpack('<I',self.read(va,4))[0]


def verify(es):
    b,r,t=(es[n] for n in ('libbehaviortree_cpp.so','liblethe_route_nodes.so','liblethe_tree.so'))
    # Pin exact branch *conditions*, not just destinations.
    core={0x75894:0x54002061,0x758a0:0x54004180,0x760d0:0xf94063f6,
          0x760f8:0xcb030033,0x76174:0x17fffe11,0x75de8:0x97ff0ce6,
          0x75f9c:0xd63f0060,0x62edc:0x90000241,0x62ee0:0x910f0021,
          0x62f48:0x97ff5e5e}
    opt={0x48c224:0x97ff03bb,0x4f2bf0:0xb0005561,0x4f2bf4:0x910c6021,
         0x4f2c04:0x97ffba2f,0x4e15c8:0x97fd68d2}
    for obj,pins in ((b,core),(r,opt)):
        for va,word in pins.items():
            if obj.word(va)!=word:raise ValueError('native opcode differs at %#x'%va)
    if b.read(0xaa3c0,17)!=b'SubtreeCondition\0':raise ValueError('core node name differs')
    if r.read(0xf9f318,20)!=b'SubtreeConditionOpt\0':raise ValueError('optional name differs')
    if b'SubtreeCondition\0' in r.data:raise ValueError('unexpected standalone core name in route binary')
    if t.read(0x568a74,10)!=b'RobotNode\0' or t.read(0x578590,12)!=b'StationWash\0':
        raise ValueError('native registered tree names differ')
    return True


def main():
    if len(sys.argv)!=2:raise SystemExit('Usage: script.py OWNER_PRIVATE_V62.zip')
    es={}
    with zipfile.ZipFile(sys.argv[1]) as z:
        for name,(suffix,digest) in PINS.items():
            matches=[n for n in z.namelist() if n.endswith(suffix)]
            if len(matches)!=1:raise ValueError('missing or ambiguous '+name)
            payload=z.read(matches[0])
            if hashlib.sha256(payload).hexdigest()!=digest:raise ValueError('SHA-256 pin mismatch '+name)
            es[name]=Original(payload)
    verify(es)
    print('X40_V100_COMPACT_REPO_REGRESSION_PASS originals=3 core_name=SubtreeCondition optional_name=SubtreeConditionOpt extensionless_root=RobotNode')
    print('LIMIT: compact test checks pinned anchors, full control-flow/34 mutations require the separately delivered v100 verifier')

if __name__=='__main__':main()
