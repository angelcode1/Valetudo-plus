#!/usr/bin/env python3
"""v59: producer proof + v58 Blackboard provenance of turbidity_clean_area and station_info_sub decision.

Read-only standard-library verifier. Runs against owner's original firmware ZIP
and independently collected runtime-tree ZIP. No device/network connections.

Usage: python3 x40_r2416_v58_turbidity_blackboard_provenance_verify.py ORIGINAL.zip RUNTIME.zip --self-test
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



# v56: every direct invocation of the native TubidityState typed Blackboard
# setter in this pinned tactics ELF, and the two threshold-controlled state-2
# transitions (one per state-machine function). Addresses are ELF virtual VAs.
V56_TYPED_STATE_SET_CALLS = {
    0x254a80:3,0x254cec:3,0x254df4:0,0x254f8c:3,
    0x254fe4:4,0x25527c:3,0x2553d8:2,
    0x25609c:3,0x256258:3,0x256388:0,
    0x256654:4,0x2568e8:3,0x256a40:2,
}
V56_STATE_VALUE_MOVES = {
    0x254a80:0x254a4c,0x254cec:0x254cbc,0x254f8c:0x254f5c,
    0x254fe4:0x254fb4,0x25527c:0x25524c,0x2553d8:0x2553a8,
    0x25609c:0x256068,0x256258:0x256228,0x256654:0x256624,
    0x2568e8:0x2568b8,0x256a40:0x256a10,
}
V56_STACK_VALUE_STORES = {
    0x254a80:0x254a58,0x254cec:0x254cc4,0x254df4:0x254dcc,
    0x254f8c:0x254f64,0x254fe4:0x254fbc,0x25527c:0x255254,
    0x2553d8:0x2553b0,0x25609c:0x256074,0x256258:0x256230,
    0x256388:0x256360,0x256654:0x25662c,0x2568e8:0x2568c0,
    0x256a40:0x256a18,
}

def examine_v56(blobs):
    t=ELF(blobs['liblethe_tactics_tree.so'])
    # Single typed specialization name, checked in this ELF's dynstr bytes;
    # the pinned image/relocations resolve its PLT entry to address 0xc83d0.
    mangled=b'_ZN2BT10Blackboard3setIR13TubidityStateEEvRKNSt7__cxx1112basic_string'
    must(mangled in t.raw,'TubidityState typed setter dynamic symbol absent')
    seen=[]
    for offset in range(0,len(t.text)//4*4,4):
        a=t.text_start+offset
        w=struct.unpack_from('<I',t.text,offset)[0]
        if w&0xfc000000 == 0x94000000 and t.dest(a)==0xc83d0:
            seen.append(a)
    must(seen==sorted(V56_TYPED_STATE_SET_CALLS),f'Unexpected typed-state direct-call census: {[hex(a) for a in seen]}')
    counts={0:0,2:0,3:0,4:0}
    for call,value in V56_TYPED_STATE_SET_CALLS.items():
        store=V56_STACK_VALUE_STORES[call]
        if value:
            # mov w1, #value; store w1 to the proper stack slot
            move=V56_STATE_VALUE_MOVES[call]
            must(t.word(move)==(0x52800001 | (value<<5)),f'State value changed at {move:#x}')
        # state zero is stored from zero register (an alternate sequence).
        else:
            must(t.word(store)==(0xb9009fff if call==0x254df4 else 0xb9007fff),f'State-zero store changed at {store:#x}')
        if value:
            expected_store=(0xb9009fe1 if call<0x255a50 else 0xb9007fe1)
            must(t.word(store)==expected_store,f'State stack store changed at {store:#x}')
        must(t.dest(call)==0xc83d0,'Setter call changed')
        counts[value]+=1
    must(counts=={0:2,2:2,3:7,4:2},f'Unexpected state value census: {counts}')
    print('PASS full tactics .text typed TubidityState setter census: 13 direct calls (0=2, 2=2, 3=7, 4=2)')

    # Threshold-based state=2 transitions. Both compare signed int32 values:
    #   threshold [+0x58c] < ([+0x680 or +0x684] - [+0x588])
    # and select the state=2 typed setter. Alternate path assigns state=3.
    common={
      0x255234:0xb9458a82, # reading baseline +0x588 -> w2
      0x255238:0xb9468280, # reading variant A +0x680 -> w0
      0x25523c:0xb9458e81, # table threshold +0x58c -> w1
      0x255240:0x4b020000, # sub w0,w0,w2
      0x255244:0x6b00003f, # cmp w1,w0
      0x255248:0x54000b0b, # b.lt to state2
      0x25524c:0x52800061, # state3 alternative
      0x2553a8:0x52800041, # state2
      0x2568a0:0xb9458a62, # baseline +0x588
      0x2568a4:0xb9468660, # variant B +0x684
      0x2568a8:0xb9458e61, # table threshold +0x58c
      0x2568ac:0x4b020000, # sub w0,w0,w2
      0x2568b0:0x6b00003f, # cmp w1,w0
      0x2568b4:0x54000aeb, # b.lt to state2
      0x2568b8:0x52800061, # state3 alternative
      0x256a10:0x52800041, # state2
      0x254f9c:0x52800002, # bool=false for table lookup A
      0x254fa0:0x97f9d1b8, # GetAByTable@plt
      0x254fa4:0xb9058e80, # store threshold +0x58c
      0x25660c:0x52800022, # bool=true for lookup B
      0x256610:0x97f9cc1c, # GetAByTable@plt
      0x256614:0xb9058e60, # store threshold +0x58c
      0x254fa8:0xb9464a80, # fail counter +0x648
      0x254fac:0x7100241f, # compare 9
      0x254fb0:0x5400020d, # branch if <=9, else state 4
      0x256618:0xb9464a60, # fail counter +0x648
      0x25661c:0x7100241f, # compare 9
      0x256620:0x540001ed, # branch if <=9, else state 4
    }
    for a,w in common.items():t.pinned(a,w)
    must(t.dest(0x255248)==0x2553a8,'Path A threshold/state2 branch changed')
    must(t.dest(0x2568b4)==0x256a10,'Path B threshold/state2 branch changed')
    must(t.dest(0x254fa0)==0xc9680 and t.dest(0x256610)==0xc9680,'Table threshold calculation target changed')
    must(t.dest(0x254fb0)==0x254ff0 and t.dest(0x256620)==0x25665c,'Counter 9 bypass branch changed')
    print('PASS both signed threshold comparisons and state2/state3 bifurcations')
    print('PASS branch operands: +0x58c threshold vs (+0x680/+0x684 minus +0x588)')
    print('PASS GetAByTable(...,false/true) stores +0x58c before subsequent comparisons')
    print('PASS counter +0x648 greater-than-nine branches to state4 in both functions')
    print('LIMIT: neither runtime reentry after failure-marker erase nor physical rewash is shown.')
    print('X40_V56_TYPED_TURBIDITY_STATE_TRANSITION_STATIC_PASS')


# v57: native two-table threshold selection and the counter-eligible
# CheckIfNeedReClean decision layer. Scope: static path only, no device.
def examine_v57(blobs):
    t=ELF(blobs['liblethe_tactics_tree.so'])
    expected = {
      0x252a30:0x12001c55,  # boolean argument reduced to 8 bits (and w21,w21,#0xff)
      0x252a40:0x97f9d2e8,  # InitTable@plt
      0x252a44:0x340004b5,  # false -> auxiliary Blackboard lookup
      0x252a48:0x7100027f,  # true mode, int input vs zero
      0x252a50:0x52842661,  # max input 8499
      0x252ab8:0xf9431684,  # C table begin +0x628
      0x252abc:0xf9431a83,  # C table end +0x630
      0x252ad4:0x17f9d883,  # FindC@plt tailcall
      0x252c08:0xf942fe81,  # A table begin +0x5f8
      0x252c0c:0xf9430283,  # A table end +0x600
      0x252c5c:0x17f9d015,  # FindA@plt tailcall
      0x252d24:0x12804480,  # input <=0 true mode fallback -549
      0x252e74:0x97f9d1db,  # GetB calls InitTable
      0x252e78:0x7100027f,  # B input versus 0
      0x252e80:0x71004e7f,  # B input versus 19
      0x252e88:0x1e2e1000,  # >19 -> 1.0 float
      0x252e98:0xf942fe81,  # required A table begin
      0x252e9c:0xf9430280,  # required A table end
      0x252eb0:0xf9430a84,  # B table begin +0x610
      0x252eb8:0xf9430e83,  # B table end +0x618
      0x252ed0:0x17f9d3fc,  # FindB tailcall
      0x252ed4:0x529eb860,  # <=0 fallback float .33 low 16bits
      0x252ed8:0x72a7d500,  # <=0 fallback float .33 high 16bits
      0x252eec:0x0f000400,  # empty table -> float 0
      0x2539e8:0x1e202118,  # float input compare against zero
      0x2539ec:0x52800001,  # negative input -> index 0
      0x2539f8:0x52800281,  # input >20 -> index20
      0x253a04:0x1e380101,  # in range: fcvtzs w1,s8
      0x253a0c:0x17fffdb8,  # rejoin GetB at 0x2530ec
      0x253a14:0x17fffdb6,  # rejoin GetB at 0x2530ec
      0x2530ec:0xaa1403e0,  # this receiver for GetBByTable
      0x2530f0:0x97f9d860,  # GetBByTable@plt
      0x2530f4:0xbd458e81,  # stored threshold field +0x58c
      0x2530fc:0x5e21d821,  # signed integer -> float
      0x253100:0x1e200821,  # product of B coefficient and threshold
      0x253104:0x1e380036,  # convert float product -> integer w22
      0x2532e8:0xb9458a81,  # baseline +0x588
      0x2532ec:0xb9468280,  # A reading +0x680
      0x2532f0:0x4b010000,  # difference
      0x2532f4:0x6b16001f,  # compare diff vs converted product
    }
    # Explicit instruction signatures produced from LLVM disassembly; all
    # exact matches protect the branch and call register provenance.
    for a,w in expected.items():t.pinned(a,w)
    targets={
      0x252a40:0xc75e0,0x252a44:0x252ad8,0x252a4c:0x252d24,
      0x252a5c:0x252a8c,0x252ad4:0xc8ce0,0x252c5c:0xc6cb0,
      0x252e74:0xc75e0,0x252e7c:0x252ed4,0x252e84:0x252e98,
      0x252ed0:0xc7ec0,0x2530f0:0xc9270,
      0x2532fc:0x253444,
      0x254fb0:0x254ff0,0x256620:0x25665c,
      0x254ff4:0xc7970,0x256660:0xc7970,
    }
    for a,d in targets.items():
        must(t.dest(a)==d,f'v57 expected branch/call {a:#x}->{d:#x}, got {t.dest(a)}')
    # The auxiliary `B` lookup is called at a constant input of 20, outside
    # that helper's integer table interpolation range 1..19. This makes its
    # >19 fallback constant 1.0 *for that direct call*.
    must(t.word(0x2530e8)==0x52800281,'Default GetB input=20 changed')
    for a,d in {0x2539f0:0x253a10,0x253a00:0x253a10,
                0x253a0c:0x2530ec,0x253a14:0x2530ec}.items():
        must(t.dest(a)==d,f'GetB index clamp/rejoin changed {a:#x}')
    print('PASS GetA boolean route: true->FindC table, false->Blackboard/FindA table')
    print('PASS GetB input range, fallback/empty-table paths and separate FindB table')
    print('PASS CheckIfNeedReClean: default B index 20 OR clamped/converted s8 index, both rejoin GetB')
    print('PASS counter <=9 branches both invoke CheckIfNeedReClean, >9 branches set numeric state4')
    print('LIMIT: default GetB(20) => 1.0 via >19 fallback, dynamic index can use B table;')
    print('       actual presence of required Blackboard key/branch, retry schedule and physical wash unknown.')
    print('X40_V57_TABLE_LOOKUP_AND_RECHECK_GATE_STATIC_PASS')


# v58: Cross-binary, direct-literal provenance of the dynamic B-table index.
# These are bounded native operations; runtime Blackboard contents and setter
# identity remain outside the evidence established here.
def examine_v58(blobs):
    t=ELF(blobs['liblethe_tactics_tree.so'])
    r=ELF(blobs['liblethe_route_nodes.so'])
    n=ELF(blobs['node_lethe.so'])
    key=b'turbidity_clean_area'
    # All direct ADRP+ADD references to the one exact key literal in these ELFs.
    direct={
      'liblethe_tactics_tree.so':[(0x252f68,0x252f6c),(0x254af0,0x254af4),(0x25653c,0x256540)],
      'liblethe_route_nodes.so':[(0xaf3204,0xaf3208),(0xb0f45c,0xb0f460),(0xb478b4,0xb478bc)],
      'node_lethe.so':[(0x52232c,0x522330)],
    }
    for name, refs in direct.items():
        elf=ELF(blobs[name]); must(blobs[name].count(key)==1,f'{name}: key literal count changed')
        must(elf.direct_refs(elf.find_va(key))==refs,f'{name}: key refs changed')
    must(t.find_va(key)==0x340ba0 and r.find_va(key)==0x10080b0 and
         n.find_va(key)==0xa06868,'turbidity_clean_area literal address changed')
    # The data key is extracted from the 20-byte literal, not a guessed name.
    must(t.at(0x340ba0,21)==key+b'\x00','turbidity_clean_area string changed')
    must(t.at(0x340bb8,21)==b'current_cell_val_vec\x00','adjacent key changed')
    print('PASS turbidity_clean_area: 3 tactics + 3 route + 1 node direct literal references')

    # A-helper's alternative false path fetches the independent station_info_sub
    # Blackboard object, then uses 16-bit field +0x5e to select A-table/fallback.
    must(t.find_va(b'station_info_sub')==0x32a600,'station_info_sub changed')
    must((0x252b10,0x252b14) in t.direct_refs(0x32a600),
         'station_info_sub reader direct reference changed')
    tactics={
      0x252ae0:0x97f9cd74, # BT::TreeNode::blackboard
      0x252b10:0x900006c1, 0x252b14:0x91180021, # station_info_sub key
      0x252b38:0xf9400700, # blackboard virtual storage
      0x252b48:0xf9400842, # virtual +0x10 get
      0x252b4c:0xd63f0040,
      0x252bcc:0xf94027e0,  # typed-value block
      0x252bd0:0x7940bc35,  # ldrh w21,[x1,#0x5e]
      0x252be8:0x34000495,  # branch on field ==0
      0x252bf4:0x71000abf, # branch on field ==2
      0x252c00:0x54000700, # branch on field ==3
      0x252c08:0xf942fe81,0x252c0c:0xf9430283, # A vector
      0x252c5c:0x17f9d015, # FindA
      0x252f68:0xd0000776, 0x252f6c:0x912e82c1, # turbidity_clean_area
      0x252fa8:0xaa1503e1, 0x252fac:0xf9401442,0x252fb0:0xd63f0040, # contains
      0x253038:0xb4004840, # no Blackboard get -> default float=20
      0x253044:0xf9400842, 0x253048:0xd63f0040, # virtual +0x10 get
      0x253050:0xb4004780, # no entry -> default
      0x2530c8:0xbd4002e8, # ldr s8,[x23] (float)
      0x2530cc:0x1400021e, # join fallback conversion route
      0x253940:0x1e269008, # explicit float default 20
      0x2539b8:0xf94006e0, # lookup for second key
      0x2539c8:0xf9401842, 0x2539cc:0xd63f0040, # erase second key
      0x2539e8:0x1e202118, 0x253a04:0x1e380101, # index clamp/convert
      0x254af0:0x90000761,0x254af4:0x912e8021, # same key
      0x254b14:0xf9401842,0x254b18:0xd63f0040, # erase
      0x25653c:0xd0000741,0x256540:0x912e8021,
      0x256560:0xf9401842,0x256564:0xd63f0040, # erase
    }
    for addr,word in tactics.items():t.pinned(addr,word)
    for addr,dst in {
        0x252a44:0x252ad8,0x252be8:0x252c78,
        0x253038:0x253940,0x253050:0x253940,
        0x2530cc:0x253944,0x253a0c:0x2530ec,
        0x253a14:0x2530ec,
    }.items():must(t.dest(addr)==dst,f'tactics branch changed {addr:#x}->{dst:#x}')
    print('PASS GetA(false) station_info_sub +0x5e selection of FindA/fallback')
    print('PASS recheck: dynamic s8 float read, default=20, clamped GetB index, and key erase')
    print('PASS both native wash paths erase turbidity_clean_area on covered branches')

    route={
      0xaf3204:0xb00028a2,0xaf3208:0x9102c042,
      0xaf3244:0x97e56e4b, # get<float> turbidity_clean_area
      0xaf3248:0xf9402fe2,0xaf3268:0x350004b6, # if available bypass next get
      0xaf3294:0xb00028a2,0xaf3298:0x91038042, # clean_area_bkwash
      0xaf32d4:0x97e56e27, # get<float>
      0xaf32f8:0x34000656, # second unavailable -> status2
      0xaf3324:0xb00028a2,0xaf3328:0x91032042, # last_turbid_area
      0xaf335c:0x97e56e05, # get<float>
      0xaf3378:0x2d490be0, # ldp s0,s2
      0xaf337c:0x1e229001, # fmov s1,#5
      0xaf3380:0x1e223800, # fsub s0,s0,s2
      0xaf3384:0x1e212010, # fcmpe s0,s1
      0xaf3388:0x540001cc, # gt -> status2
      0xaf338c:0x52800060, # status3
      0xaf33c0:0x52800040, # status2
      0xb0f45c:0xb00027c1,0xb0f460:0x9102c021,
      0xb0f4a0:0xf9401842,0xb0f4a4:0xd63f0040, # preset erase
      0xb478b4:0xb0002616,0xb478bc:0x9102c2c3, # map key in mop dirty
      0xb47940:0xf9401402, # hash-map value type check
      0xb47958:0x97e3ecd6, # hash of literal key
    }
    for addr,word in route.items():r.pinned(addr,word)
    for addr,dst in {0xaf3268:0xaf32fc,0xaf32f8:0xaf33c0,
                     0xaf3388:0xaf33c0,0xb0f4a4:None}.items():
        if dst is not None:must(r.dest(addr)==dst,f'route branch changed {addr:#x}->{dst:#x}')
    for literal,ref in [(b'clean_area_bkwash',(0xaf3294,0xaf3298)),
                        (b'last_turbid_area',(0xaf3324,0xaf3328))]:
        must(ref in r.direct_refs(r.find_va(literal)),f'CalTurbidArea missing {literal!r}')
    n.pinned(0x52232c,0x90002721);n.pinned(0x522330,0x9121a021)
    n.pinned(0x52234c,0x97f568bd) # node_lethe SendMap get<float>
    print('PASS CalTurbidArea::tick get<float> trio and 5.0 threshold status2/3')
    print('PASS PresetBlackboard erase and MopDirtyAccumulator direct key lookup')
    print('PASS node_lethe SendMap get<float> for same Blackboard key')
    print('v58 historical boundary: no writer established *by the v58 checks*; v59 tests producer separately')
    print('       static reads/erases are not evidence of runtime state or physical rewash.')
    print('X40_V58_TURBIDITY_BLACKBOARD_PROVENANCE_STATIC_PASS')

# v59: Typed production of turbidity_clean_area in MopDirtyAccumulator::tick.
# Exact instruction patterns and dynamic relocation checked against pinned bytes.
def relocation_symbol(raw, slot):
    # Minimal ELF64/AArch64 SHT_RELA reader; parses producer type metadata offline.
    soff=struct.unpack_from('<Q',raw,40)[0]
    entsize,count=struct.unpack_from('<HH',raw,58)
    heads=[struct.unpack_from('<IIQQQQIIQQ',raw,soff+i*entsize) for i in range(count)]
    dynsym=next(h for h in heads if h[1]==11)  # SHT_DYNSYM
    dynstr=heads[dynsym[6]]
    strings=raw[dynstr[4]:dynstr[4]+dynstr[5]]
    matches=[]
    for sh in heads:
        if sh[1]!=4:continue  # SHT_RELA
        for pos in range(sh[4],sh[4]+sh[5],sh[9]):
            offset,info,addend=struct.unpack_from('<QQq',raw,pos)
            if offset!=slot:continue
            index=info>>32
            symbol_entry=dynsym[4]+index*dynsym[9]
            name_off=struct.unpack_from('<I',raw,symbol_entry)[0]
            name=strings[name_off:].split(b'\0',1)[0]
            matches.append((name,info&0xffffffff,addend))
    must(len(matches)==1,f'Expected one relocation for {slot:#x}, found {len(matches)}')
    return matches[0]

def examine_v59(blobs):
    r=ELF(blobs['liblethe_route_nodes.so'])
    key=b'turbidity_clean_area'
    must(r.find_va(key)==0x10080b0,'Route key literal moved')
    # Route-side producer is the MopDirtyAccumulator::tick symbol body;
    # these four sites all use the same stack-allocated key at x23=sp+0x158.
    fixed={
       0xb47000:0x97e3ef50,0xb47004:0xf9400000,
       0xb478ac:0x54ffcc4d,0xb478b4:0xb0002616,0xb478bc:0x9102c2c3,
       0xb478d0:0x97e3ed1c,0xb47958:0x97e3ecd6,
       0xb47444:0xbd40f3e8,0xb47458:0x5e21d908,
       0xb4745c:0x1e211908,0xb47460:0x1e202908,
       0xb47614:0xb940f7e0,0xb47624:0x350000c0,
       0xb47628:0x7100035f,0xb47630:0x1e200514,
       0xb47634:0x1a9fd7e0,0xb47638:0x350095e0,
       0xb47640:0x97e3edc0,0xb47644:0xf9400000,
       0xb47648:0xf9400400,0xb47650:0xf9400003,0xb47654:0xf0003822,
       0xb47658:0x1e22c108,0xb4765c:0xaa1703e1,
       0xb47660:0xf9461842,0xb47664:0xf9401063,0xb47668:0xf900d7e2,
       0xb4766c:0xaa1503e2,0xb47670:0xfd00cfe8,
       0xb47674:0xd63f0060,
       0xb47c20:0xb94147e1,0xb47c24:0x52880000,
       0xb47c28:0x72a88f40,0xb47c2c:0xb900ffe0,
       0xb47c30:0x34ffcf21,0xb47c38:0x340000e0,
       0xb47c3c:0x7100035f,0xb47c40:0x7a43d824,
       0xb47c44:0x54000081,0xb47c48:0x1e269000,
       0xb47c4c:0x1e202110,0xb47c50:0x540067ec,
       0xb47c54:0xaa1403e0,0xb47c58:0x97e3ec3a,
       0xb47c60:0xf9400400,0xb47c64:0xb4ffd140,
       0xb47c68:0xf9400003,0xb47c6c:0xf0003822,
       0xb47c70:0x1e22c108,0xb47c74:0xaa1703e1,
       0xb47c78:0xf9461842,0xb47c7c:0xf9401063,
       0xb47c84:0xaa1503e2,0xb47c88:0xfd00cfe8,
       0xb47c8c:0xd63f0060,
       0xb488f4:0xaa1403e0,0xb48910:0xbd40ffe0,
       0xb48914:0xaa1703e1,0xb48918:0xf9461863,
       0xb48920:0x1e22c000,0xb48924:0xf9401084,
       0xb4892c:0xfd00cfe0,0xb48930:0xd63f0080,
       0xb48954:0xf9400000,0xb48958:0xaa1703e1,
       0xb4895c:0x9103f3e2,0xb48960:0x97e42750,
    }
    for addr,w in fixed.items():r.pinned(addr,w)
    must((0xb478b4,0xb478bc) in r.direct_refs(0x10080b0),
         'MopDirtyAccumulator key construction no longer anchored')
    for addr,target in {
        0xb478ac:0xb47234, 0xb47624:0xb4763c,
        0xb47638:0xb488f4,0xb47c30:0xb47614,
        0xb47c38:0xb47c54,0xb47c44:0xb47c54,
        0xb47c50:0xb4894c,
        0xb48960:0x4526a0,
    }.items():must(r.dest(addr)==target,f'Bad branch/call {addr:#x}')
    s,kind,addend=relocation_symbol(blobs['liblethe_route_nodes.so'],0x124ec30)
    must(kind==1025 and addend==0 and b'linb3any15vtable_for_typeIdE' in s,
         'Double linb::any vtable relocation changed')
    # The same GOT double Any vtable is selected for all three virtual set calls.
    for load in (0xb47660,0xb47c78,0xb48918):
        must(r.word(load)&0xffc00000==0xf9400000,'Unexpected double-vtable GOT load')
    # Confirm typed float setter is a distinct direct PLT call.
    must(r.dest(0xb48960)==0x4526a0,'Typed float setter PLT target changed')
    print('PASS MopDirtyAccumulator key construction and four Blackboard write sites')
    print('PASS three virtual set calls with double SafeAny payload and one typed float set')
    print('PASS accumulator arithmetic and conditional write/sentinel branches')
    print('LIMIT: shared concrete Blackboard lineage, runtime write success, and numeric conversion are unproven')
    print('LIMIT: no proven R2416 special_push_clean_dish producer or physical second wash')
    print('X40_V59_MOP_DIRTY_ACCUMULATOR_PRODUCER_STATIC_PASS')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip');p.add_argument('runtime_zip');p.add_argument('--self-test',action='store_true')
    x=p.parse_args()
    blobs=originals(x.original_zip,x.runtime_zip)
    examine(blobs)
    examine_v55(blobs)
    examine_v56(blobs)
    examine_v57(blobs)
    examine_v58(blobs)
    examine_v59(blobs)
    if x.self_test:
        changed=dict(blobs)
        raw=bytearray(blobs['liblethe_route_nodes.so']); e=ELF(raw)
        for start,end,off in e.loads:
            if start<=0xb47674<end:
                raw[off+0xb47674-start]^=1
                break
        changed['liblethe_route_nodes.so']=bytes(raw)
        try:examine_v59(changed)
        except AssertionError as err:must('Changed instruction' in str(err),'Wrong v59 instruction rejection: '+str(err))
        else:raise AssertionError('v59 failed to reject modified Blackboard writer instruction')
        print('X40_V59_INSTRUCTION_TAMPER_REJECTION_PASS')
        # Test 1: v58-specific anchored instruction rejection, independent of hashes.
        changed=dict(blobs)
        raw=bytearray(changed['liblethe_route_nodes.so'])
        va=0xaf3244
        e=ELF(raw)
        for start,end,off in e.loads:
            if start<=va<end:
                raw[off+va-start]^=1;break
        changed['liblethe_route_nodes.so']=bytes(raw)
        try: examine_v58(changed)
        except AssertionError as err:
            must('Changed instruction' in str(err),'Unexpected instruction tamper error: '+str(err))
        else:raise AssertionError('v58 instruction signature failed to detect modification')
        print('X40_V58_INSTRUCTION_TAMPER_REJECTION_PASS')
        # Test 2: original SHA pin rejects tampering elsewhere in ELF.
        changed=dict(blobs)
        raw=bytearray(changed['liblethe_tactics_tree.so']);raw[4096]^=1
        changed['liblethe_tactics_tree.so']=bytes(raw)
        try:examine(changed)
        except AssertionError as err:
            must('SHA-256 pin mismatch' in str(err),'Unexpected SHA tamper error: '+str(err))
        else:raise AssertionError('v58 SHA signature failed to reject alteration')
        print('X40_V58_SHA_TAMPER_REJECTION_PASS')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('X40_V59_FAIL:',exc,file=sys.stderr)
        sys.exit(1)