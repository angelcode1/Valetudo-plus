#!/usr/bin/env python3
"""Read-only, standard-library-only R2416 v48 GlobalHook pre-tick callback audit.

Usage: python3 x40_r2416_v48_globalhook_callback_verify.py ORIGINAL_ZIP RUNTIME_ZIP
Reads SHA-pinned ELFs as inert bytes; makes no robot/network calls. Does not
claim that the default callback is the only possible runtime callback.
"""
import argparse
import hashlib
import io
import struct
import sys
import tarfile
import zipfile

PINS = {
    'node_lethe.so':'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
    'liblethe_tree.so':'9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
    'liblethe_tactics_tree.so':'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
    'liblethe_route_nodes.so':'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
    'libbehaviortree_cpp.so':'665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
}

def check(v, msg):
    if not v: raise ValueError(msg)

def exactly(seq, pred, label):
    found = [x for x in seq if pred(x)]
    check(len(found)==1, f'{label}: expected one entry, got {len(found)}')
    return found[0]

class ELF:
    def __init__(self, blob):
        self.blob = blob
        check(blob[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H',blob,18)[0] == 183,
              'not a little-endian AArch64 ELF64')
        po=struct.unpack_from('<Q',blob,32)[0]
        pe,pn=struct.unpack_from('<HH',blob,54)
        self.loads=[]
        for i in range(pn):
            typ,_,fileoff,addr,_,size,_,_=struct.unpack_from('<IIQQQQQQ',blob,po+pe*i)
            if typ==1: self.loads.append((addr,addr+size,fileoff))
        so=struct.unpack_from('<Q',blob,40)[0]
        se,sn=struct.unpack_from('<HH',blob,58)
        self.sections=[]
        for i in range(sn):
            v=struct.unpack_from('<IIQQQQIIQQ',blob,so+se*i)
            self.sections.append(dict(no=v[0],addr=v[3],offset=v[4],size=v[5],link=v[6],entsize=v[9]))
        names=self.secdata(self.sections[struct.unpack_from('<H',blob,62)[0]])
        for s in self.sections:
            start=s['no']; end=names.find(b'\0',start)
            check(end>=0,'invalid ELF section-name index')
            s['name']=names[start:end].decode('ascii')
    def secdata(self, sec): return self.blob[sec['offset']:sec['offset']+sec['size']]
    def sec(self, name): return exactly(self.sections,lambda s:s['name']==name,name)
    def va(self, addr, n):
        for start,end,off in self.loads:
            if start<=addr and addr+n<=end:
                return self.blob[off+addr-start:off+addr-start+n]
        raise ValueError(f'unmapped virtual address {addr:#x}')
    def word(self, addr):return struct.unpack('<I',self.va(addr,4))[0]
    def instruction(self, addr, expected):
        check(self.word(addr)==expected, f'instruction changed at {addr:#x}')
    def symbol(self, name):
        sec=self.sec('.dynsym'); raw=self.secdata(sec); strs=self.secdata(self.sections[sec['link']]); found=[]
        for i in range(0,len(raw),24):
            index,_,_,_,addr,sz=struct.unpack_from('<IBBHQQ',raw,i)
            e=strs.find(b'\0',index)
            if strs[index:e]==name: found.append((addr,sz))
        return exactly(found,lambda x:True,name.decode())
    def relocation(self, slot, name, addr):
        sym=self.sec('.dynsym');rawsym=self.secdata(sym);strs=self.secdata(self.sections[sym['link']]);matches=[]
        raw=self.secdata(self.sec('.rela.dyn'))
        for i in range(0,len(raw),24):
            pos,info,addend=struct.unpack_from('<QQq',raw,i)
            if pos!=slot:continue
            index=info>>32;typ=info&0xffffffff
            check(index*24+24<=len(rawsym),'invalid relocation symbol index')
            string_offset,_,_,_,value,_=struct.unpack_from('<IBBHQQ',rawsym,index*24)
            e=strs.find(b'\0',string_offset)
            matches.append((typ,strs[string_offset:e],value,addend))
        check(matches == [(1025,name,addr,0)],f'wrong GOT relocation at {slot:#x}: {matches}')
    def call(self, addr, target):
        w=self.word(addr)
        check(w&0xfc000000==0x94000000, f'not BL at {addr:#x}')
        off=w&0x3ffffff
        if off&(1<<25):off-=1<<26
        check(addr+4*off==target, f'call target changed at {addr:#x}')


def original_and_runtime(original_zip,runtime_zip):
    with zipfile.ZipFile(original_zip) as z:
        t=exactly(z.namelist(),lambda n:n.endswith('/X40_R2416_original_vendor_native_ELFs.tar') and not n.startswith('__MACOSX/'),'original ELFs tar')
        with tarfile.open(fileobj=io.BytesIO(z.read(t)),mode='r:') as archive:
            original={}
            for name in PINS:
                if name=='node_lethe.so':continue
                m=exactly(archive.getmembers(),lambda x:x.isfile() and x.name.endswith('/'+name),name)
                original[name]=archive.extractfile(m).read()
        n=exactly(z.namelist(),lambda x:x.endswith('/robot/ava/lib/node_lethe.so') and not x.startswith('__MACOSX/'),'original node_lethe')
        original['node_lethe.so']=z.read(n)
    for name,pin in PINS.items():
        check(hashlib.sha256(original[name]).hexdigest()==pin, f'{name}: full SHA-256 mismatch')
    with zipfile.ZipFile(runtime_zip) as z:
        for name in ('liblethe_tree.so','liblethe_tactics_tree.so','liblethe_route_nodes.so'):
            path=exactly(z.namelist(),lambda n:n.endswith('/tree_lib/'+name) and not n.startswith('__MACOSX/'),name)
            check(z.read(path)==original[name],f'{name}: runtime copy mismatch')
        cfg=exactly(z.namelist(),lambda n:n.endswith('/setting.yaml') and not n.startswith('__MACOSX/'),'setting.yaml')
        lines=z.read(cfg).decode('utf-8').splitlines()
        check(lines.count('behavior_tree_path: RobotNode')==1,'robot tree selector changed')
        check(lines.count('tree_lib_path: /tmp/lib/tree_lib//')==1,'runtime tree directory changed')
    return {name:ELF(blob) for name,blob in original.items()}

INVOKER_SUFFIX = b'9_M_invokeERKSt9_Any_dataS1_S6_'
MANAGER_SUFFIX = b'10_M_managerERSt9_Any_dataRKSC_St18_Manager_operation'
NAME_PREFIX = b'_ZNSt17_Function_handlerIFvRKmRSt10shared_ptrIN2BT10BlackboardEEEN11route_nodes10GlobalHook10hook_func_MUlS1_S6_E_EE'

def verify(original_zip, runtime_zip):
    elfs=original_and_runtime(original_zip,runtime_zip)
    node=elfs['node_lethe.so'];route=elfs['liblethe_route_nodes.so']
    check(node.symbol(NAME_PREFIX+INVOKER_SUFFIX)==(0x3ec460,4),'node default callback symbol changed')
    check(route.symbol(NAME_PREFIX+INVOKER_SUFFIX)==(0x48ce00,4),'route default callback symbol changed')
    node.instruction(0x3ec460,0xd65f03c0)  # ret
    route.instruction(0x48ce00,0xd65f03c0) # ret
    check(node.symbol(NAME_PREFIX+MANAGER_SUFFIX)==(0x3ee2f0,44),'node std::function manager changed')
    check(route.symbol(NAME_PREFIX+MANAGER_SUFFIX)==(0x48d500,44),'route std::function manager changed')
    print('PASS two ELF default GlobalHook callback handlers contain single AArch64 RET')

    node.relocation(0xb7ccf8,NAME_PREFIX+INVOKER_SUFFIX,0x3ec460)
    node.relocation(0xb7e4b8,NAME_PREFIX+MANAGER_SUFFIX,0x3ee2f0)
    route.relocation(0x124f100,NAME_PREFIX+INVOKER_SUFFIX,0x48ce00)
    route.relocation(0x1250c60,NAME_PREFIX+MANAGER_SUFFIX,0x48d500)
    print('PASS four GOT relocations bind the respective default invoker/manager functions')

    for a,w in {
        0x3ee7c8:0x52800026,  # mov w6,1
        0x3ee7cc:0x78008426,  # strh w6,[x1],#8
        0x3ee7d0:0xf9467ca5,  # ldr x5,[x5,#0xcf8]
        0x3ee7d8:0xf9425c84,  # ldr x4,[x4,#0x4b8]
        0x3ee7dc:0xa9011424,  # stp x4,x5,[x1,#0x10]
        0x4a2048:0x52800026,  # mov w6,1
        0x4a204c:0x78008426,  # strh w6,[x1],#8
        0x4a2050:0xf94080a5,  # ldr x5,[x5,#0x100]
        0x4a2058:0xf9463084,  # ldr x4,[x4,#0xc60]
        0x4a205c:0xa9011424,  # stp x4,x5,[x1,#0x10]
    }.items():
        (node if a<0x400000 else route).instruction(a,w)
    print('PASS both singleton initializers store std::function manager and no-op invoker pointers')

    node.relocation(0xb7c9d8,b'_ZZN11route_nodes10GlobalHook8InstanceEbE8instance',0xb85620)
    for addr,word in {
        0x3e1360:0xf944ef03, # GOT singleton pointer
        0x3e1368:0xf9400060, # load instance
        0x3e1374:0xf9400c01, # load x1,[x0,#24] invoker nonnull check
        0x3e1378:0x91002000, # add x0,x0,#8 (std::function storage)
        0x3e137c:0xf9401a82, # shared Blackboard holder
        0x3e1380:0xb40185e1, # null -> throw path
        0x3e1384:0xf9400c03, # invoke pointer (x0+0x18)
        0x3e1388:0xaa1703e1, # x1 points to time/sequence reference
        0x3e138c:0xd63f0060, # blr x3
        0x3e1390:0xf947a680, # retained tree root
        0x3e1398:0xf9400c21, # root executeTick vslot
        0x3e139c:0xd63f0020, # blr x1
        0x3e13a0:0x12001c19, # preserve status w25
    }.items():node.instruction(addr,word)
    node.call(0x3e443c,0x27cf20) # null std::function throws
    print('PASS callback dispatch, nonnull check, exception target and subsequent retained-root virtual executeTick')
    print('X40_V48_GLOBALHOOK_DEFAULT_CALLBACK_STATIC_PASS')
    print('LIMITS: runtime function may be replaced; actual callback destination/override state,')
    print('        runtime tick delivery, R2416 special_push_clean_dish producer and physical rewash unproven.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip')
    a=p.parse_args()
    try:verify(a.original_zip,a.runtime_zip)
    except Exception as exc:
        print('X40_V48_STATIC_FAIL:',exc,file=sys.stderr)
        sys.exit(1)

