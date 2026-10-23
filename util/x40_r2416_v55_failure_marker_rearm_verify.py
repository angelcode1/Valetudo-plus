#!/usr/bin/env python3
"""v55: verify state-2 re-arm paths after failure-marker consumption.

Read-only standard-library verifier. Runs against owner's original firmware ZIP
and independently collected runtime-tree ZIP. No device/network connections.

Usage: python3 x40_r2416_v55_failure_marker_rearm_verify.py ORIGINAL.zip RUNTIME.zip
       python3 x40_r2416_v54_failure_marker_consumption_verify.py ORIGINAL.zip RUNTIME.zip --self-test
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
EXTRAS = ['node_camera_ai.so','node_map_divide.so','node_iot.so','node_cmd.so','node_msg_cvt.so']

def must(test, detail):
    if not test: raise AssertionError(detail)

def unique(it, condition, label):
    xs=[x for x in it if condition(x)]
    must(len(xs)==1,f'{label}: wanted exactly one match, got {len(xs)}')
    return xs[0]

class ELF:
    def __init__(self, raw):
        self.raw=raw
        must(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,
             'Expected little-endian AArch64 ELF64')
        po=struct.unpack_from('<Q',raw,32)[0]
        pe,pn=struct.unpack_from('<HH',raw,54)
        self.loads=[]
        for i in range(pn):
            typ,_,off,addr,_,size,_,_=struct.unpack_from('<IIQQQQQQ',raw,po+i*pe)
            if typ==1:self.loads.append((addr,addr+size,off))
        so=struct.unpack_from('<Q',raw,40)[0]
        se,sn,si=struct.unpack_from('<HHH',raw,58)
        sh=[struct.unpack_from('<IIQQQQIIQQ',raw,so+i*se) for i in range(sn)]
        strings=raw[sh[si][4]:sh[si][4]+sh[si][5]]
        text=unique(sh,lambda e: strings[e[0]:].split(b'\x00',1)[0]==b'.text','ELF .text')
        self.text_start=text[3]
        self.text=raw[text[4]:text[4]+text[5]]

    def at(self,va,n):
        for start,end,off in self.loads:
            if start<=va and va+n<=end: return self.raw[off+va-start:off+va-start+n]
        raise AssertionError(f'Unmapped virtual address {va:#x}')

    def word(self,va):return struct.unpack('<I',self.at(va,4))[0]
    def pinned(self,addr,word):must(self.word(addr)==word,f'Changed instruction at {addr:#x}')
    def dest(self,addr):
        w=self.word(addr)
        if w&0xff000010==0x54000000 or w&0x7e000000==0x34000000:
            v=(w>>5)&0x7ffff
            if v&(1<<18):v-=1<<19
            return addr+v*4
        if w&0x7c000000==0x14000000:
            v=w&0x3ffffff
            if v&(1<<25):v-=1<<26
            return addr+v*4
        return None
    def find_va(self,s):
        pos=self.raw.find(s)
        must(pos>=0,f'Literal missing: {s!r}')
        for start,end,off in self.loads:
            if off<=pos<off+(end-start):return start+pos-off
        raise AssertionError('literal not in a load segment')
    def direct_refs(self, target):
        b=self.text; base=self.text_start
        words=[x[0] for x in struct.iter_unpack('<I',b[:len(b)//4*4])]
        hits=[]
        for i,a in enumerate(words[:-4]):
            if a & 0x9f000000 != 0x90000000: continue
            reg=a&31
            delta=(((a>>5)&0x7ffff)<<2)|((a>>29)&3)
            if delta&(1<<20):delta-=1<<21
            page=((base+4*i)&~0xfff)+(delta<<12)
            for j in range(1,5):
                w=words[i+j]
                if w&0xff000000!=0x91000000 or ((w>>5)&31)!=reg:continue
                va=page+(((w>>10)&4095)<<(((w>>22)&1)*12))
                if va==target: hits.append((base+4*i,base+4*(i+j)))
        return hits

def originals(a,b):
    blobs={}
    with zipfile.ZipFile(a) as z:
        tarname=unique(z.namelist(),lambda x:x.endswith('/X40_R2416_original_vendor_native_ELFs.tar') and not x.startswith('__MACOSX/'), 'original TAR')
        with tarfile.open(fileobj=io.BytesIO(z.read(tarname)), mode='r:') as t:
            for name in PINS:
                if name=='node_lethe.so':continue
                m=unique(t.getmembers(),lambda x:x.isfile() and x.name.endswith('/'+name), name)
                blobs[name]=t.extractfile(m).read()
        for name in ['node_lethe.so']+EXTRAS:
            path=unique(z.namelist(),lambda x:x.endswith('/robot/ava/lib/'+name) and not x.startswith('__MACOSX/'),name)
            blobs[name]=z.read(path)
    with zipfile.ZipFile(b) as z:
        for name in ('liblethe_tree.so','liblethe_tactics_tree.so','liblethe_route_nodes.so'):
            path=unique(z.namelist(),lambda x:x.endswith('/tree_lib/'+name) and not x.startswith('__MACOSX/'),name)
            must(blobs[name]==z.read(path),'Original/runtime mismatch: '+name)
    return blobs

def examine(blobs):
    for name,digest in PINS.items():
        must(hashlib.sha256(blobs[name]).hexdigest()==digest,'SHA-256 pin mismatch: '+name)
    print('PASS five complete ELF SHA-256 pins and three runtime comparisons')

    # Direct key uses: 10 collected ELFs, exact ASCII spelling only.
    special=b'special_push_clean_dish'
    request=b'r2343_start_rewash'
    expected_special={'node_lethe.so':2,'liblethe_tactics_tree.so':1,'liblethe_tree.so':0}
    expected_request={'node_lethe.so':1,'liblethe_tactics_tree.so':1}
    for key,refs in ((special,expected_special),(request,expected_request)):
        for name,raw in blobs.items():
            e=ELF(raw)
            count=raw.count(key)
            must(count==int(name in (['node_lethe.so','liblethe_tactics_tree.so','liblethe_tree.so'] if key==special else ['node_lethe.so','liblethe_tactics_tree.so'])),f'Changed {key!r} literal count in {name}')
            va=e.find_va(key) if count else None
            got=e.direct_refs(va) if va is not None else []
            must(len(got)==refs.get(name,0),f'Changed direct xrefs to {key!r} in {name}: {got}')
            if key==request and name=='liblethe_tactics_tree.so':
                must(got==[(0x2352e4,0x2352e8)],'Rewash request producer xref shifted')
            if key==special and name=='liblethe_tactics_tree.so':
                must(got==[(0x23526c,0x235270)],'Special-push gate xref shifted')
    print('PASS 10-ELF bounded literal / direct ADRP+ADD census for eligibility and request keys')

    t=ELF(blobs['liblethe_tactics_tree.so'])
    # Three distinct contains checks (first failure key, then special-push), an erase,
    # two later gates and conditional set of the request marker. Exact instruction
    # anchors, dispatch slots and branch destinations are checked separately.
    expected_words={
        0x23516c:0xb4000fa0, # null Blackboard -> skip failure marker
        0x235178:0xf9401442, # virtual +0x28 contains
        0x23517c:0xd63f0040,
        0x235184:0x54000ee0, # failure key absent -> skip
        0x235200:0xb40000a0, # null Blackboard -> bypass erase
        0x23520c:0xf9401842, # virtual +0x30 erase
        0x235210:0xd63f0040, # erase attempted on nonnull Blackboard
        0x23522c:0x395a2260, # load wash gate at this +0x688
        0x235230:0x340020a0, # gate zero -> bypass
        0x235234:0x52800021, # may begin state=1 write, before special gate
        0x2352a4:0xb40025a0, # null Blackboard -> bypass
        0x2352b0:0xf9401442, # virtual +0x28 contains
        0x2352b4:0xd63f0040,
        0x2352bc:0x540024e0, # special-push absent -> bypass
        0x2352fc:0xb4000220, # null Blackboard -> bypass set
        0x235308:0xd2800022, # value integer 1
        0x235314:0xf9401063, # virtual +0x20 set
        0x235318:0xf9002be2, # store value 1
        0x235328:0xd63f0060, # request setter invocation
    }
    for addr,word in expected_words.items(): t.pinned(addr,word)
    for addr,dst in {
        0x23516c:0x235360, 0x235184:0x235360,
        0x235200:0x235214,
        0x235230:0x235644,
        0x2352a4:0x235758, 0x2352bc:0x235758,
        0x2352fc:0x235340,
    }.items():must(t.dest(addr)==dst,f'Unexpected branch destination {addr:#x}')
    must(0x235184<0x235210<0x235230<0x2352bc<0x235328,'Unexpected guard ordering')
    failure_refs=t.direct_refs(t.find_va(b'TurbidityResultFail'))
    must(failure_refs==[(0x235134,0x235138),(0x254e1c,0x254e20),(0x2563b0,0x2563b4)],
         'TurbidityResultFail direct-reference list changed')
    must(t.dest(0x23523c)==0xc69c0,'Pre-eligibility SetRunState call changed')
    print('PASS contains(failure) -> erase(failure) -> wash gate -> contains(special) -> set(request) ordering')
    print('PASS failure marker literal reference and pre-eligibility SetRunState(1) call')
    print('PASS three request-bypass branches and two null-handle branches')

    # Check the R2416-excluding model gate and setter in the only identified
    # direct-literal producer. Does not exclude computed/indirect key producers.
    n=ELF(blobs['node_lethe.so'])
    for addr,dest in {
        0x4704d0:0x4704e8,
        0x4704e4:0x4731d8,
        0x4731e8:0x4704e8,
        0x4731ec:0x4705b4,
    }.items(): must(n.dest(addr)==dest,f'Model branch changed at {addr:#x}')
    must(n.dest(0x470554)==0x27c860,'Known typed set<int> call target changed')
    must(n.find_va(special)==0x9fc7f8,'Producer key literal changed')
    print('PASS known ProcessModelInfo model-equality branch and unmatched-model bypass')
    print('X40_V54_FAILURE_MARKER_CONSUMPTION_STATIC_PASS')
    print('LIMIT: erased only where nonnull Blackboard and successful contains; later rewrites,')
    print('      alternate indirect key producers, runtime values, and physical rewash unproven.')



def examine_v55(blobs):
    """Check exact state-2 producer branches; no runtime causality is inferred."""
    t=ELF(blobs['liblethe_tactics_tree.so'])
    # The two producers consume a numeric state-2 from a Blackboard-associated
    # lookup. Each writes TubidityState=0 before the failure string marker.
    expected={
        0x2549bc:0xb9409be0, 0x2549c0:0x7100081f, 0x2549c4:0x54002020,
        0x255fd4:0xb9407be0, 0x255fd8:0x7100081f, 0x255fdc:0x54001c00,
        0x254dcc:0xb9009fff, 0x254df4:0x97f9cd77,
        0x256360:0xb9007fff, 0x256388:0x97f9c812,
        0x254e1c:0x90000761, 0x254e20:0x9116e021,
        0x254e3c:0x911f62e2, 0x254e40:0x97f9c710,
        0x2563b0:0xd0000741, 0x2563b4:0x9116e021,
        0x2563d0:0x911f62e2, 0x2563d4:0x97f9c1ab,
        0x254e5c:0xb9467a81,0x254e60:0x52800c80,
        0x254e64:0xb9067680,0x254e6c:0x51000421,
        0x254e70:0xb9067a81,
        0x2563f0:0xb9467a61,0x2563f4:0x52800c80,
        0x2563f8:0xb9067660,0x256400:0x51000421,
        0x256404:0xb9067a61,
        0x254eb8:0xb9464a80,0x254ebc:0x11000400,
        0x254ec0:0xb9064a80,0x254ec4:0x7100241f,
        0x254ec8:0x5400026d,
        0x256458:0xb9464a60,0x25645c:0x11000400,
        0x256460:0xb9064a60,0x256464:0x7100241f,
        0x256468:0x5400026d,
    }
    for addr,w in expected.items(): t.pinned(addr,w)
    expected_targets={
      0x2549c4:0x254dc8,0x255fdc:0x25635c,
      0x254df4:0xc83d0,0x256388:0xc83d0,
      0x254e40:0xc6a80,0x2563d4:0xc6a80,
      0x254ec8:0x254f14,0x256468:0x2564b4,
    }
    for addr,target in expected_targets.items():
        must(t.dest(addr)==target,f'v55 unexpected branch/call at {addr:#x}')
    must(t.at(0x3277d8,5)==b'true\0','Failure payload literal changed')
    must(t.find_va(b'TurbidityResultFail')==0x3405b8,'Failure marker address changed')
    must(t.direct_refs(0x3405b8)==[
          (0x235134,0x235138),(0x254e1c,0x254e20),(0x2563b0,0x2563b4)
        ],'Unexpected additional/direct marker writer')
    # Each state-2 arm resets numeric status before publishing the marker.
    must(0x2549c4<0x254df4<0x254e40<0x254e70<0x254ec0,
         'WashErrorLogicRun producer order changed')
    must(0x255fdc<0x256388<0x2563d4<0x256404<0x256460,
         'WashFloorTubidityCheck producer order changed')
    print('PASS state-2 dispatches to both failure-marker producer paths')
    print('PASS both state-2 paths reset TubidityState=0 BEFORE writing failure marker=true')
    print('PASS both state-2 paths decrement max_rewash_cnt, set +0x674=100 and increment +0x648')
    print('PASS per-path counter >9 conditional branch verified (policy/units not inferred)')

    # Bounded direct BL census over *one* function body: this is not a call
    # graph proof across dynamic dispatch or later event-loop invocations.
    direct_calls=[]
    for a in range(0x235000,0x235804,4):
        w=t.word(a)
        if w&0xfc000000==0x94000000:
            direct_calls.append((a,t.dest(a)))
    writer_entries=(0x254170,0x255a50)
    must(not any(dst in writer_entries for _,dst in direct_calls),
         'WashDonePrecess gained direct call to known writer')
    # Both failure paths start elsewhere; direct callsites to them may be via
    # PLT stubs, indirect BT dispatch, callbacks, or later tick processing.
    print(f'PASS WashDonePrecess direct BL call census: {len(direct_calls)} instructions; none targets known writer entry')
    print('LIMIT: v55 proves re-arm *capability* after renewed state-2 entry, NOT a retry schedule.')
    print('LIMIT: other keys, runtime Blackboard identity, feature support, dock actuation unknown.')
    print('X40_V55_FAILURE_MARKER_REARM_STATIC_PASS')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip');p.add_argument('--self-test',action='store_true')
    x=p.parse_args()
    blobs=originals(x.original_zip,x.runtime_zip)
    examine(blobs)
    examine_v55(blobs)
    if x.self_test:
        tampered=dict(blobs)
        raw=bytearray(tampered['liblethe_tactics_tree.so'])
        raw[4096]^=1
        tampered['liblethe_tactics_tree.so']=bytes(raw)
        try:
            examine(tampered)
            examine_v55(tampered)
        except AssertionError as err:
            must('SHA-256 pin mismatch' in str(err),'Tamper check failed for wrong reason: '+str(err))
            print('X40_V55_TAMPER_REJECTION_PASS')
        else:raise AssertionError('Tamper was not rejected')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('X40_V55_FAIL:',exc,file=sys.stderr)
        sys.exit(1)