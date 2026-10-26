#!/usr/bin/env python3
"""Bounded v207 SHA-pinned ReuseTree/native-export census. Stdlib, offline."""
import argparse
import re
import struct
import sys
from pathlib import Path
from zipfile import ZipFile, BadZipFile

# Reuse the versioned publicly committed original-SHA verification from v206.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'x40-r2416-v206-tools'))
from x40_r2416_v206_repo_check import PINS, verify as verify_v206, count_reuse, require as need

def exported_builders(blob):
    shoff=struct.unpack_from('<Q',blob,40)[0]
    entry,n=struct.unpack_from('<HH',blob,58)
    need(64<=entry and n<100 and shoff+n*entry<=len(blob),'ELF section header bounds')
    sections=[struct.unpack_from('<IIQQQQIIQQ',blob,shoff+i*entry) for i in range(n)]
    tables=[s for s in sections if s[1]==11]
    need(len(tables)==1,'Expected one ELF .dynsym')
    d=tables[0]
    need(d[9]>=24 and d[4]+d[5]<=len(blob) and 0<=d[6]<n,'ELF dynamic symbols invalid')
    st=sections[d[6]]
    need(st[1]==3 and st[4]+st[5]<=len(blob),'ELF string table invalid')
    out=set()
    for offset in range(d[4],d[4]+d[5],d[9]):
        so,typ,other,shidx,addr,size=struct.unpack_from('<IBBHQQ',blob,offset)
        if not shidx or typ&15!=2:continue
        begin=st[4]+so
        need(st[4]<=begin<st[4]+st[5],'Bad ELF .dynstr index')
        end=blob.find(b'\0',begin,st[4]+st[5])
        need(end>=begin,'Unterminated ELF dynamic name')
        name=blob[begin:end].decode('ascii','replace')
        m=re.match(r'^_Z([0-9]+)',name)
        if not m:continue
        nlen=int(m.group(1))
        simple=name[m.end():m.end()+nlen]
        if 0<nlen<100 and len(simple)==nlen and simple.startswith('build'):
            out.add(simple)
    return out

def audit(prior):
    with ZipFile(prior) as z:
        images={}
        for name in PINS:
            paths=[p for p in z.namelist() if '/files/'+name+'/' in p]
            need(len(paths)==1,'Missing or ambiguous private ELF '+name)
            images[name]=z.read(paths[0])
    need(verify_v206(images)==158,'v206 pinned ReuseTree verification failed')
    tree=images['liblethe_tree.so']
    paths=[p.decode('ascii') for _,_,p in count_reuse(tree)]
    builders=exported_builders(tree)
    covered=[p for p in paths if 'build'+p.split('/',1)[1] in builders]
    unmatched=sorted(set(paths)-set(covered))
    need(len(builders)==199 and len(paths)==158 and len(covered)==138 and len(unmatched)==20,
         'v207 original builder coverage changed')
    need('reuse/AiStainMop' in unmatched and 'reuse/CleanSelectedAreas' in covered,
         'AiStainMop/control comparison changed')
    return (len(paths),len(builders),len(covered),len(unmatched))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    args=p.parse_args()
    try:
        sizes=audit(args.prior_zip)
        print('X40_R2416_V207_REPO_NATIVE_AISTAIN_EXPORT_CENSUS_PASS',*sizes)
        print('Export matching is not proof of registration. Other plugins/XML remain unverified.')
    except (OSError,ValueError,IndexError,struct.error,BadZipFile) as exc:
        raise SystemExit('X40_R2416_V207_REPO_FAIL: '+str(exc))
