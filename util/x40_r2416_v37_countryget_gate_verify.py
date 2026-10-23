#!/usr/bin/env python3
"""Read-only SHA-pinned v37 X40 R2416 CountryGet / AlwaysSuccess gate audit.

Requires the v36 verifier alongside this file and the owner's private original/runtime ZIPs.
No ELF execution, device commands, network access or firmware modification.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x40_r2416_v36_preloop_nodes_verify import (  # type: ignore
    collect, require, verify_v36, decode_bl_or_b, conststr_rows_with_empty,
    va_cstr
)


def verify_v37(reference, runtime):
    verify_v36(reference, runtime)
    src=collect(reference, runtime)
    f=src['liblethe_tree.so']
    bt=src['libbehaviortree_cpp.so']

    # Two named native generated builders. These are code identities, not tick observations.
    require(f.symbol(b'_Z15buildCountryGetRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE')==0x232a88,
            'CountryGet builder symbol moved')
    require(f.symbol(b'_Z18buildAlwaysSuccessRKN2BT19BehaviorTreeFactoryERKSt10shared_ptrINS_10BlackboardEE')==0x383420,
            'AlwaysSuccess builder symbol moved')
    # Six direct factory instantiations in the CountryGet generated function:
    # ForceSuccess -> SequenceStar -> [SetBlackboard, RetryUntilSuccesful(
    # BlackboardContains), SaySomething, SaySomething].
    factory=0x1c6620
    sites=(0x232ad8,0x232b08,0x232b4c,0x232b88,0x232bc8,0x232c0c,0x232c44)
    for addr in sites:f.call(addr,factory)
    require([a for a in f.bl_sites(factory) if 0x232a88<=a<0x232d18]==list(sites),
            'CountryGet factory-site census differs')
    labels=(
        (0x56938b,'ForceSuccess'),
        (0x5692df,'SequenceStar'),
        (0x5692fc,'SetBlackboard'),
        (0x5697b7,'RetryUntilSuccesful'),
        (0x56932f,'BlackboardContains'),
        (0x569342,'SaySomething'),
    )
    for addr,s in labels:require(va_cstr(f,addr)==s, 'CountryGet generated node label changed: '+s)

    # Factory attachment/depth shape: ForceSuccess root, SequenceStar decorator
    # child, SetBlackboard sibling of Retry/SaySomething children in SequenceStar;
    # RetryUntilSuccesful contains BlackboardContains as its decorator child.
    attach_calls={
        0x232ae4:0x1c6640, # root node push
        0x232ae8:0x1c6730, # increase ForceSuccess depth
        0x232b14:0x1c6800, # SequenceStar is ForceSuccess decorator-child
        0x232b1c:0x1c6730, # enter SequenceStar
        0x232b58:0x1c6900, # SetBlackboard control child
        0x232b94:0x1c6900, # RetryUntilSuccesful control child
        0x232b9c:0x1c6730, # enter retry decorator
        0x232bd4:0x1c6800, # BlackboardContains retry decorator child
        0x232bdc:0x1c6810, # leave retry scope
        0x232c18:0x1c6900, # 1st SaySomething control child
        0x232c50:0x1c6900, # 2nd SaySomething control child
        0x232c58:0x1c6810, # leave SequenceStar
        0x232c5c:0x1c6810, # leave ForceSuccess
    }
    for addr,target in attach_calls.items():f.call(addr,target)
    expected={
      0x6b1610: (('key','Get_Country_Event'),('value','')),
      0x6b1650: (('num_attempts','10'),),
      0x6b1670: (('key','country'),),
      0x6b1690: (('message','BT  -> Country:'),('xml_line_num','10'),('full_stack','CountryGet.xml,BehaviorTree,0 0 2')),
      0x6b16f0: (('message','${country}'),('xml_line_num','11'),('full_stack','CountryGet.xml,BehaviorTree,0 0 3')),
    }
    for addr,rows in expected.items():
        require(conststr_rows_with_empty(f,addr,len(rows))==rows,
                f'CountryGet parameter table mismatch at {addr:#x}')
    for callsite,table in ((0x232b38,0x6b1610),(0x232b74,0x6b1650),
                          (0x232bb4,0x6b1670),(0x232bf4,0x6b1690),(0x232c34,0x6b16f0)):
        f.call(callsite,0x1c6690) # vector<ConstStr> initializer-list construction
    print('PASS CountryGet generated ForceSuccess -> SequenceStar -> initialization/retry/log child tree')
    print('PASS CountryGet sets Get_Country_Event to an EMPTY textual value (not Boolean false)')
    print('PASS RetryUntilSuccesful num_attempts=10, BlackboardContains key=country')
    print('PASS two bounded SaySomething parameters; neither is a test of CleanGenius')

    # The separate named AlwaysSuccess tree is a single compiled node. This
    # proves structural shape, NOT its first or subsequent runtime status.
    f.call(0x383474,factory)
    f.call(0x383480,0x1c6640)
    require(va_cstr(f,0x569211)=='AlwaysSuccess','AlwaysSuccess node literal differs')
    require([a for a in f.bl_sites(factory) if 0x383420<=a<0x38351c]==[0x383474],
            'AlwaysSuccess builder child census differs')
    require(bt.symbol(b'_ZN2BT13AlwaysSuccess4tickEv')==0x63cf0,
            'AlwaysSuccess tick symbol moved')
    bt.ins(0x63cf0,0x52800040) # return numeric success 2
    bt.ins(0x63cf4,0xd65f03c0) # RET
    print('PASS generated AlwaysSuccess builder has one direct node; native tick returns numeric 2')

    # ForceSuccessDecorator compiles explicit status discrimination:
    # status 1 returns as running; 2 or 3 maps to 2 (success).
    require(bt.symbol(b'_ZN2BT21ForceSuccessDecorator4tickEv')==0x63d10,
            'ForceSuccess tick symbol moved')
    checks={
      0x63d14:0x52800021, # mov w1,#1 (running)
      0x63d34:0xd63f0020, # BLR child tick
      0x63d3c:0x7100041f, # cmp status,#1
      0x63d40:0x540000c0, # b.eq preserve running
      0x63d44:0x51000801, # status - 2
      0x63d48:0x52800040, # mov w0,#2 (success)
      0x63d50:0x7100043f, # compare status-2 range
      0x63d54:0x54000088, # b.hi else
      0x63d60:0xd65f03c0, # ret
    }
    for addr,word in checks.items(): bt.ins(addr,word)
    # Retry updates completed-failure count, checks signed bound and resets on
    # completion; no assertion of how many real-world ticks have occurred.
    require(bt.symbol(b'_ZN2BT9RetryNode4tickEv')==0x8b140,
            'RetryNode tick moved')
    for addr,word in {
      0x8b180:0xd63f0020, # virtual child tick
      0x8b188:0x7100081f, # status 2
      0x8b190:0x71000c1f, # status 3
      0x8b198:0x7100041f, # status 1
      0x8b21c:0x29450662, # attempt limit/current count
      0x8b220:0x11000421, # count++
      0x8b224:0xb9002e61, # store count
      0x8b228:0x7100005f, # cmp limit >=0 guard
      0x8b22c:0x7a42a021, # conditional count-to-limit comparison
      0x8b238:0xb9002e7f, # reset current count
    }.items():bt.ins(addr,word)
    print('PASS ForceSuccess child status 1 stays running; 2 and 3 map to success 2')
    print('PASS RetryNode has numeric status branches and bounded completed-attempt counter')
    print('X40_V37_COUNTRYGET_STATUS_STATIC_PASS')
    print('BOUNDARY: runtime tick outcomes, map/init subtree progress, the R2416 rewash eligibility')
    print('          key and actual second physical mop wash remain unproven.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('reference_zip');ap.add_argument('v27_zip')
    a=ap.parse_args()
    try: verify_v37(a.reference_zip,a.v27_zip)
    except Exception as e:
        print('X40_V37_STATIC_FAIL: '+str(e),file=sys.stderr)
        raise SystemExit(1)