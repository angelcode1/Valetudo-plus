#!/usr/bin/env python3
"""v199 bounded native subtype/A-table layout check; read-only, stdlib-only.

Requires the user's original private v1 collector ZIP locally. The full
v197–v199 replay with all anchors/tests is in the separate offline kit.
"""
import argparse
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                       'x40-r2416-v198-tools'))
import x40_r2416_v198_repo_check as base

WORDS = {
  0x24df58:0xf942fc05, 0x24df5c:0xf9430004, 0x24df64:0x9343fc84,
  0x24dfa4:0xb9400460, 0x24dfd0:0xb86068a7, 0x24dfd4:0xb9400500,
  0x24e0f8:0xf9430804, 0x24e0fc:0xf9430c00, 0x24e104:0x9343fc00,
  0x24e144:0xbd400460, 0x24e170:0xb8666886, 0x24e174:0xbd4004e0,
  0x24e028:0xf9431405, 0x24e02c:0xf9431804, 0x24e034:0x9343fc84,
  0x24e074:0xb9400460, 0x250850:0x7940bc1b,
  0x251fa0:0xf942dac1, 0x251fa8:0xf942dec0, 0x251fb8:0x9b027c00,
  0x251fbc:0xeb3b201f, 0x251fc0:0x54ff6cc9, 0x251fe0:0x52800302,
  0x251fe4:0x9117e2c0, 0x251fec:0x9ba20761, 0x252004:0x17ffeae3,
}

def verify(elf):
    base.verify(elf)
    for addr, expected in WORDS.items():
        base.require(base.word_at_va(elf, addr) == expected,
                     'v199 native anchor changed at %#x' % addr)
    base.require(base.target(0x251fc0, base.word_at_va(elf,0x251fc0),'cond')
                 == 0x250d58,'Subtype bounds-check target changed')
    base.require(base.target(0x252004, base.word_at_va(elf,0x252004),'b')
                 == 0x24cb90,'Selected inner-vector copy target changed')
    return len(WORDS),2

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-zip',required=True)
    args=p.parse_args()
    with zipfile.ZipFile(args.prior_zip) as z:
        matches=[n for n in z.namelist()
                 if '/files/liblethe_tactics_tree.so/' in n]
        base.require(len(matches)==1,'Missing/ambiguous tactics ELF')
        count,edges=verify(z.read(matches[0]))
    print('X40_R2416_V199_REPO_SUBTYPE_INDEX_STATIC_PASS',
          count,'new word anchors',edges,'new edges')
    print('Not proof of runtime subtype, loaded calibration or physical reclean')

if __name__ == '__main__':
    try:main()
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        raise SystemExit('X40_R2416_V199_REPO_FAIL: '+str(exc))
