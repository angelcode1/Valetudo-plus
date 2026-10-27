#!/usr/bin/env python3
"""Offline v212 bounded check of user-uploaded process cwd metadata only."""
import argparse
import hashlib
import json
from pathlib import Path

PINS={
 'san':'c35bc6085b78875256c0e985227e0d34c1a670e301f9c5e1c79d3b8159e2f255',
 'pri':'b1f2a6cf2dc75342af77e022331837078aea39d1a867af8949ad3696defc9767',
}
CANDIDATES={'AiStainMop','AiStainMop.xml','reuse/AiStainMop','reuse/AiStainMop.xml'}

def require(condition,message):
    if not condition:raise ValueError(message)

def check(sbytes,pbytes):
    require(hashlib.sha256(sbytes).hexdigest()==PINS['san'], 'Sanitized report hash changed')
    require(hashlib.sha256(pbytes).hexdigest()==PINS['pri'], 'Private report hash changed')
    require(max(len(sbytes),len(pbytes))<=32768,'Oversized metadata report')
    s=json.loads(sbytes);p=json.loads(pbytes)
    require(s.get('schema')=='X40_R2416_V211_PROCESS_CWD_SANITIZED_V1', 'Unexpected public schema')
    require(p.get('schema')=='X40_R2416_V211_PROCESS_CWD_PRIVATE_V1', 'Unexpected private schema')
    require(s.get('ssh_requested') is True and s.get('stderr_warning') is False,
            'Unexpected collection status')
    require(s.get('robot_files_modified') is False and
            s.get('robot_file_contents_collected') is False,'Unexpected robot state change')
    require(s.get('actual_behavior_tree_file_fallback_execution_observed') is False and
            s.get('complete_AiStainMop_runtime_resolution_proven') is False,
            'Unverified runtime conclusion')
    require(s.get('processes_mapping_original_tree_library')==1 and
            s.get('process_cwds_readable')==1 and s.get('process_cwds_unreadable')==0,
            'Unexpected mapped-process totals')
    matched=p.get('matched_processes')
    require(isinstance(matched,dict) and len(matched)==1 and
            p.get('processes_with_unreadable_cwd')==[], 'Unexpected private process counts')
    (pid,rec),=matched.items()
    require(pid.isdecimal() and isinstance(rec.get('cwd'),str) and rec['cwd'].startswith('/'),
            'Unexpected private process record')
    require(isinstance(rec.get('candidates'),dict) and
            set(rec['candidates'])==CANDIDATES and
            all(x=='absent' for x in rec['candidates'].values()),
            'Private candidate evidence changed')
    tally=s.get('per_relative_candidate_presence_counts')
    require(isinstance(tally,dict) and set(tally)==CANDIDATES,
            'Public candidate names changed')
    require(all(tally[x]=={'absent':1,'file':0,'symlink':0} for x in CANDIDATES),
            'Public candidate status mismatch')
    return 1,4,0

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sanitized',type=Path,required=True)
    p.add_argument('--private',type=Path,required=True)
    a=p.parse_args()
    try:
        print('X40_R2416_V212_REPO_PROCESS_CWD_PASS',*check(a.sanitized.read_bytes(),a.private.read_bytes()))
        print('No PID/cwd output; this does not prove native AiStainMop resolution.')
    except (OSError,ValueError,KeyError,TypeError) as e:
        raise SystemExit('X40_R2416_V212_REPO_FAIL: '+str(e))
