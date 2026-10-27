#!/usr/bin/env python3
"""Bounded offline verification of original R2416 AI command state.

No robot access. For full 56-instruction, two-relocation evidence replay,
use the downloadable source-only v223 kit.
"""
import argparse
import hashlib
import struct
import zipfile

EXPECTED_SHA="b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0"
ANCHORS={0x3db598:0x97fa6a12,0x5db478:0x97f281da,
         0x5dc9c0:0x7100141f,0x5dc9c8:0x7100181f,
         0x5dc9d0:0x71003c1f,0x5dcf84:0x97f2718f,
         0x5dcfd8:0x97f2717a,0x5dd010:0x97f2716c}
KEYS={0xa12820:b"start_offline",0xa12830:b"start_material_detect",
      0xa13488:b"ai_set_mop_is_dirty_data"}

def check(path):
    with zipfile.ZipFile(path) as archive:
        matches=[p for p in archive.namelist() if "/files/node_lethe.so/" in p]
        if len(matches)!=1:
            raise ValueError("Expected exactly one original host binary")
        binary=archive.read(matches[0])
    if hashlib.sha256(binary).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Original host hash does not match")
    for offset,word in ANCHORS.items():
        if struct.unpack_from("<I",binary,offset)[0]!=word:
            raise ValueError("Native instruction mismatch")
    for offset,key in KEYS.items():
        if binary[offset:offset+len(key)+1]!=key+b"\0":
            raise ValueError("AI state key mismatch")
    return len(ANCHORS),len(KEYS)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-zip",required=True)
    args=parser.parse_args()
    try:
        print("X40_R2416_V223_REPO_BOUNDED_PASS",*check(args.prior_zip))
    except (OSError,ValueError,struct.error,zipfile.BadZipFile) as err:
        raise SystemExit("X40_R2416_V223_REPO_FAIL: "+str(err))
