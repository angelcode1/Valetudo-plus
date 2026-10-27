#!/usr/bin/env python3
"""Read-only offline audit of owner-uploaded X40 R2416 v209 live resolver ZIP.

No SSH, firmware execution, private payload extraction or external deps.
The complete historical v197–v210 native verification is in the source-only kit.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import PurePosixPath
from zipfile import ZipFile, BadZipFile

SHA='b5439e44d7286d9f7007f55fd26d326eb68d8dae1f29b62e275795a7255b8a7b'
KNOWN={'liblethe_tree.so','liblethe_route_nodes.so','liblethe_tactics_tree.so'}

def need(ok,msg):
    if not ok:raise ValueError(msg)

def check(raw):
    need(hashlib.sha256(raw).hexdigest()==SHA,'Uploaded ZIP SHA-256 changed')
    with ZipFile(io.BytesIO(raw)) as z:
        need(z.testzip() is None,'Archive CRC mismatch')
        names=z.namelist()
        need(len(names)==2 and len(set(names))==2,'Unexpected file payloads')
        need(all(n and not n.startswith('/') and '..' not in PurePosixPath(n).parts and
                 '\\' not in n for n in names),'Unsafe archive member path')
        i=[x for x in names if x.endswith('/inventory.SANITIZED.json')]
        m=[x for x in names if x.endswith('/manifest.PRIVATE.json')]
        need(len(i)==len(m)==1,'Missing metadata JSON')
        need(all(z.getinfo(n).file_size<=128000 for n in names),'Oversized metadata')
        inv=json.loads(z.read(i[0]));man=json.loads(z.read(m[0]))
    need(inv.get('schema')=='X40_R2416_V208_SANITIZED_INVENTORY_V1','Inventory schema changed')
    need(man.get('schema')=='X40_R2416_V208_PRIVATE_TARGETED_V1','Manifest schema changed')
    need(inv.get('prior_checksum_entries_checked')==man.get('prior_checksum_entries_checked')==18,
         'Prior checksum tally changed')
    need(inv.get('remote_path_candidates')==man.get('remote_path_candidates')==6,
         'Remote candidate tally changed')
    need(inv.get('new_file_count')==inv.get('new_plugin_ELFs')==
         inv.get('new_named_subtree_resources')==0 and man.get('saved')==[],
         'Unexpected collected resource')
    need(inv.get('search_not_exhaustive') is True and inv.get('robot_changed') is False,
         'Source scope/safety flag changed')
    skips=man.get('skipped')
    need(isinstance(skips,list) and len(skips)==6,'Unexpected skipped entries')
    tally=Counter()
    for x in skips:
        need(isinstance(x,dict) and x.get('name') in KNOWN and
             x.get('reason')=='byte-identical-to-prior-collection','Unknown skip record')
        tally[x['name']]+=1
    need(tally==Counter({name:2 for name in KNOWN}),'Unexpected duplicate distribution')
    return (6,len(tally),0)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live-resolver-zip',required=True)
    a=p.parse_args()
    try:
        raw=open(a.live_resolver_zip,'rb').read()
        n=check(raw)
        print('X40_R2416_V210_REPO_LIVE_RESOLVER_PASS',*n)
        print('Six matching paths for three known ELFs; no new resource retained.')
        print('No authenticated SSH transcript or complete directory-coverage evidence.')
    except (OSError,ValueError,TypeError,KeyError,IndexError,BadZipFile) as exc:
        raise SystemExit('X40_R2416_V210_REPO_FAIL: '+str(exc))
