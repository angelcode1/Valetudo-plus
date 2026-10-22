#!/usr/bin/env python3
"""Read-only, standard-library v27 R2416 tree-library provenance verifier.

Usage: python3 x40_r2416_v27_runtime_tree_verify.py X40-R2416-v27.zip
Verifies SHA pins, duplicate TAR member equivalence, effective selector fields,
ELF64/AArch64 exported factory symbols, GOT relocations, factory registration
calls and RobotNode's generated builder entry. Static evidence only.
"""
import argparse
import hashlib
import io
import re
import struct
import sys
import tarfile
import zipfile
from pathlib import PurePosixPath

PINS = {
    'liblethe_tree.so': '9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
    'liblethe_tactics_tree.so': 'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
    'liblethe_route_nodes.so': 'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
}
EXPECTED_SETTINGS = {
    'behavior_tree_path': 'RobotNode',
    'tree_lib_path': '/tmp/lib/tree_lib//',
    'robot_para_path': '/data/Robot_Para.yaml',
}


def require(cond, why):
    if not cond:
        raise ValueError(why)


def exactly_one(seq, predicate, label):
    vals = [x for x in seq if predicate(x)]
    require(len(vals) == 1, '%s: expected one, found %d' % (label, len(vals)))
    return vals[0]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Elf:
    def __init__(self, raw):
        self.raw = raw
        require(raw[:6] == b'\x7fELF\x02\x01', 'not little-endian ELF64')
        require(struct.unpack_from('<H', raw, 18)[0] == 183, 'not AArch64')
        phoff = struct.unpack_from('<Q', raw, 32)[0]
        phent, phnum = struct.unpack_from('<HH', raw, 54)
        self.loads = []
        for i in range(phnum):
            typ, _, offset, va, _, size, _, _ = struct.unpack_from('<IIQQQQQQ', raw, phoff+i*phent)
            if typ == 1:
                self.loads.append((va, va+size, offset))
        shoff = struct.unpack_from('<Q', raw, 40)[0]
        shent, shnum = struct.unpack_from('<HH', raw, 58)
        self.sections = []
        for i in range(shnum):
            r = struct.unpack_from('<IIQQQQIIQQ', raw, shoff+i*shent)
            self.sections.append({'nameoff': r[0], 'offset': r[4], 'size': r[5],
                                  'addr': r[3], 'link': r[6], 'entsize': r[9]})
        table = self.sbytes(self.sections[struct.unpack_from('<H', raw, 62)[0]])
        for s in self.sections:
            k=s['nameoff']
            s['name']=table[k:table.find(b'\0',k)].decode('ascii')

    def sbytes(self, sec):
        return self.raw[sec['offset']:sec['offset']+sec['size']]

    def sec(self, name):
        return exactly_one(self.sections, lambda s: s['name']==name, name)

    def va(self, pc, size):
        for low, high, off in self.loads:
            if low <= pc and pc+size <= high:
                return self.raw[off+pc-low:off+pc-low+size]
        raise ValueError('invalid ELF virtual address %x' % pc)

    def word(self, pc):
        return struct.unpack('<I', self.va(pc, 4))[0]

    def instruction(self, pc, expected):
        got=self.word(pc)
        require(got == expected, 'instruction mismatch at %#x: %#x' % (pc, got))

    def call(self, pc, target):
        w=self.word(pc)
        require((w&0xfc000000)==0x94000000, 'missing BL at %#x' % pc)
        off=w&0x3ffffff
        if off&(1<<25): off-=1<<26
        require(pc+4*off == target, 'branch target differs at %#x' % pc)

    def symbol(self, name):
        sym=self.sec('.dynsym')
        strings=self.sbytes(self.sections[sym['link']])
        require(sym['entsize']==24,'unexpected .dynsym entry size')
        raw=self.sbytes(sym)
        for i in range(0,len(raw),24):
            stname,_,_,_,vaddr,_=struct.unpack_from('<IBBHQQ',raw,i)
            if strings[stname:strings.find(b'\0',stname)].decode('ascii','replace')==name:
                return (i//24,vaddr)
        raise ValueError('missing export '+name)

    def relocation(self, pc):
        s=self.sec('.rela.dyn')
        require(s['entsize']==24,'unexpected .rela.dyn entry size')
        raw=self.sbytes(s)
        for i in range(0,len(raw),24):
            loc, info, add=struct.unpack_from('<QQq', raw, i)
            if loc==pc: return (info>>32,info&0xffffffff,add)
        raise ValueError('missing relocation at %#x' % pc)

    def adrp_add_references(self, target, max_gap=44):
        """Census of direct ADRP+ADD-immediate pairs to exact VA in .text.
        This does not cover GOT loads or computed addresses.
        """
        s=self.sec('.text')
        data=self.sbytes(s)
        base=s['addr']
        refs=[]
        for i in range(0,len(data)-4,4):
            ins=struct.unpack_from('<I',data,i)[0]
            if ins&0x9f000000 != 0x90000000: continue
            r=ins&31
            val=((ins>>5)&0x7ffff)*4 | ((ins>>29)&3)
            if val & (1<<20):val-=1<<21
            page=((base+i)&~4095)+(val<<12)
            if (target&~4095)!=page:continue
            for j in range(i+4,min(i+max_gap+4,len(data)),4):
                a=struct.unpack_from('<I',data,j)[0]
                if a&0xff000000 != 0x91000000 or (a>>5)&31 != r:continue
                imm=((a>>10)&4095) << (12 if (a>>22)&1 else 0)
                if page+imm==target:
                    refs.append((base+i,base+j))
        return refs


def verify(p):
    with zipfile.ZipFile(p) as z:
        names=[n for n in z.namelist() if not n.endswith('/') and '__MACOSX/' not in n]
        libs={}
        for name,pin in PINS.items():
            member=exactly_one(names,lambda x:x.endswith('/tree_lib/'+name),name)
            raw=z.read(member)
            require(sha(raw)==pin, 'SHA-256 pin mismatch: '+name)
            libs[name]=raw
        sn=exactly_one(names,lambda x:x.endswith('/setting.yaml'),'setting.yaml')
        lines=z.read(sn).decode('utf-8').splitlines()
        fields={}
        for line in lines:
            match=re.match(r'^([a-z][a-z0-9_]*)\s*:\s*(.*?)\s*$',line)
            if match and match.group(1) in EXPECTED_SETTINGS:
                require(match.group(1) not in fields,'duplicate selector: '+match.group(1))
                fields[match.group(1)]=match.group(2)
        require(fields == EXPECTED_SETTINGS, 'effective selector fields do not match v27 evidence')
        tn=exactly_one(names,lambda x:x.endswith('/runtime-tree-libs.tar'),'runtime tar')
        with tarfile.open(fileobj=io.BytesIO(z.read(tn)),mode='r:') as t:
            members=t.getmembers()
            require(len(members)==3 and all(m.isfile() for m in members),'unexpected TAR layout')
            require({PurePosixPath(m.name).name for m in members}==set(PINS),'unexpected TAR names')
            for m in members:
                require(m.name==PurePosixPath(m.name).name,'unexpected TAR path')
                require(t.extractfile(m).read()==libs[m.name], 'TAR and ZIP copies differ: '+m.name)
        empty=exactly_one(names,lambda x:x.endswith('/RobotNode.xml'),'failed XML retrieval placeholder')
        require(z.getinfo(empty).file_size==0,'RobotNode.xml is no longer an empty placeholder')
    tree=Elf(libs['liblethe_tree.so'])
    factories=[('RobotNode',0x568a74,0x565bf8,0x565bfc,0x565c38,0x7b1c48,
                '_Z14buildRobotNodeRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE',0x312c6c),
               ('StationWash',0x578590,0x566240,0x566244,0x566278,0x7b1c50,
                '_Z16buildStationWashRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE',0x358540)]
    for name,ptr,adrp,add,call,got,mangled,addr in factories:
        require(tree.va(ptr,len(name)+1)==name.encode()+b'\0','factory name mismatch: '+name)
        require((tree.word(adrp)&0x9f00001f)==0x90000001,'name ADRP opcode differs: '+name)
        require((tree.word(add)&0xffc003ff)==0x91000021,'name ADD opcode differs: '+name)
        refs=tree.adrp_add_references(ptr)
        require((adrp,add) in refs,'registration literal reference changed: '+name)
        tree.call(call,0x1c6930)
        idx,func=tree.symbol(mangled)
        require(func==addr,'builder address differs: '+name)
        require(tree.relocation(got)==(idx,1025,0),'builder GOT relocation mismatch: '+name)
    # Explicit entry into generated RobotNode builder, then a large generated
    # sequence, not a dereference of an XML file on disk.
    tree.call(0x312ca0,0x1c6720)  # init_fac@plt
    tree.call(0x312ca4,0x30d8c0)  # generated RobotNode body
    root_name_refs=tree.adrp_add_references(0x568a74)
    wash_name_refs=tree.adrp_add_references(0x578590)
    require(root_name_refs==[(0x565bf8,0x565bfc)],'unexpected direct RobotNode string references')
    require(wash_name_refs==[(0x566240,0x566244)],'unexpected direct StationWash string references')
    # A direct call to buildStationWash would be a BL with an immediate target.
    # Absence does not exclude indirect GOT/function-pointer dispatch.
    code=tree.sec('.text')
    raw=tree.sbytes(code)
    direct_station_calls=[]
    for off in range(0,len(raw)-3,4):
        word=struct.unpack_from('<I',raw,off)[0]
        if word & 0xfc000000 != 0x94000000: continue
        displacement=word & 0x3ffffff
        if displacement & (1<<25): displacement -= 1<<26
        pc=code['addr']+off
        if pc + displacement*4 == 0x358540:
            direct_station_calls.append(pc)
    require(not direct_station_calls,'unexpected direct call to StationWash builder')
    print('PASS 3 SHA-256-pinned runtime tree ELF files')
    print('PASS original TAR members identical to ZIP tree_lib copies')
    print('PASS setting.yaml: behavior_tree_path=RobotNode; tree_lib_path=/tmp/lib/tree_lib//')
    print('PASS RobotNode and StationWash builder registrations and GOT relocations')
    print('PASS buildRobotNode enters compiled generated builder at 0x30d8c0')
    print('PASS bounded direct name-reference census: StationWash name only in registration')
    print('PASS direct-call census: no BL targeting buildStationWash in this tree library')
    print('NOTE RobotNode.xml is zero-length failed-copy artifact')
    print('X40_V27_RUNTIME_TREE_REGISTRATION_PASS')
    print('BOUNDARY: No proof StationWash is instantiated/ticked or shares AvaNodeRoute Blackboard;')
    print('          no proof special_push_clean_dish exists on R2416 or physical rewash occurs.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collection_zip')
    args=parser.parse_args()
    try:verify(args.collection_zip)
    except (ValueError,KeyError,IndexError,EOFError,OSError,struct.error,zipfile.BadZipFile,tarfile.TarError,UnicodeError) as e:
        print('X40_V27_RUNTIME_TREE_REGISTRATION_FAIL: '+str(e),file=sys.stderr)
        sys.exit(1)
