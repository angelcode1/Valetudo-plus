#!/usr/bin/env python3
"""v211 bounded offline cross-check of two owner-private scope metadata JSONs.

No robot connection, native code execution, extra dependency or private path output.
Full v197-v211 ELF regression replay is distributed in the source-only v211 ZIP.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

PINS={
 'san':'b07f79db0d78a411e8d97478b6527422b9ed82206e6ddd8076e33711f0ddc880',
 'pri':'5963cbd3d583812d59ff72fef09299406243ff223da7504f8b1fe8c1bda25878',
}
ROOTS=('/tmp/lib/tree_lib','/usr/lib/tree_lib','/ava/lib','/tmp/ava/lib')
LIBS={'liblethe_tree.so','liblethe_tactics_tree.so','liblethe_route_nodes.so'}

def require(ok,why):
    if not ok:raise ValueError(why)

def check(san,pri):
    require(hashlib.sha256(san).hexdigest()==PINS['san'],'SANITIZED JSON SHA-256 changed')
    require(hashlib.sha256(pri).hexdigest()==PINS['pri'],'PRIVATE JSON SHA-256 changed')
    require(len(san)<64000 and len(pri)<64000,'Unexpected metadata size')
    s=json.loads(san);p=json.loads(pri)
    require(s.get('schema')=='X40_R2416_V210_SCOPED_REMOTE_COVERAGE_V1' and
            p.get('schema')=='X40_R2416_V210_SCOPED_COVERAGE_PRIVATE_V1',
            'Unknown input schemas')
    require(s.get('remote_ssh_requested') is True and
            s.get('maximum_recursion_depth')==8 and
            s.get('symlinks_followed') is False and
            s.get('scan_stderr_warning') is False,'Unknown scope boundary')
    require(s.get('exhaustive_installed_implementation_proof') is False and
            s.get('native_binary_or_config_file_contents_collected') is False and
            s.get('robot_files_modified') is False,'Unknown safety/coverage scope')
    roots=s.get('roots');matches=p.get('matching_paths_by_root')
    require(isinstance(roots,dict) and isinstance(matches,dict) and
            set(roots)==set(matches)==set(ROOTS),'Unexpected roots')
    total=0;plugins=0
    for root in ROOTS:
        x=roots[root];y=matches[root]
        want=3 if root.endswith('/tree_lib') else 0
        expected={root+'/'+name for name in LIBS} if want else set()
        paths=y.get('plugin_library_paths')
        require(isinstance(paths,list) and set(paths)==expected and len(paths)==want,
                'Private plugin-path census changed')
        require(y.get('AiStainMop_named_paths')==[],'Named AiStainMop resource detected')
        require(x.get('present') is True and x.get('root_symlink_unfollowed') is False and
                x.get('symlinks_seen_not_followed')==0 and x.get('scan_error_kinds')==[],
                'Scan errors or symlinks present')
        require(x.get('tree_plugin_elfs_seen')==want and
                x.get('AiStainMop_named_paths_seen')==0 and
                x.get('regular_files_seen')==(3 if want else 32),
                'Per-root coverage tally changed')
        total+=x['regular_files_seen'];plugins+=want
    require(total==70 and plugins==s.get('total_tree_plugin_elfs_seen')==6 and
            s.get('total_AiStainMop_named_paths_seen')==0,'Summary count mismatch')
    return total,plugins,0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope-sanitized',type=Path,required=True)
    parser.add_argument('--scope-private',type=Path,required=True)
    opts=parser.parse_args()
    try:
        counts=check(opts.scope_sanitized.read_bytes(),opts.scope_private.read_bytes())
        print('X40_R2416_V211_REPO_SCOPE_CONSISTENCY_PASS',*counts)
        print('Four scoped roots only; no proof of global absence or runtime resolution.')
    except (OSError,ValueError,KeyError,TypeError) as err:
        raise SystemExit('X40_R2416_V211_REPO_FAIL: '+str(err))
