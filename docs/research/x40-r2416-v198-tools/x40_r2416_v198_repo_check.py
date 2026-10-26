#!/usr/bin/env python3
"""Bounded, offline X40 R2416 v198 A-table branch checker (Python stdlib)."""
import argparse
import hashlib
import struct
import zipfile

ELF_SHA = 'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c'
WORDS = {
    0x250d50:0x395902c0, 0x250d74:0xa94153f3, 0x250d8c:0xd65f03c0,
    0x250df0:0x340051bb, 0x250df4:0x7100077f, 0x250dfc:0x54009960,
    0x252be8:0x34000495, 0x252bec:0x710006bf, 0x252bf0:0x54000580,
    0x252bf4:0x71000abf, 0x252bf8:0x54000840, 0x252bfc:0x71000ebf,
    0x252c00:0x54000700, 0x252c04:0x52800000, 0x252c10:0xeb01007f,
    0x252c14:0x54000420, 0x252c34:0xcb010063, 0x252c38:0xaa1403e0,
    0x252c3c:0x2a1303e1, 0x252c40:0x52800002, 0x252c50:0x51000463,
    0x252c98:0xa94363f7, 0x252c9c:0x17ffff71, 0x252ca0:0x52875301,
    0x252cc0:0x52800000, 0x252cc4:0x17ffffd1, 0x252ce0:0x7100027f,
    0x252cf8:0x52825700, 0x252cfc:0x17ffffc3, 0x252d00:0x7100027f,
    0x252d1c:0x52800000, 0x252d20:0x17ffffba,
}

def require(ok, msg):
    if not ok: raise ValueError(msg)

def word_at_va(elf, va):
    require(elf[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', elf, 18)[0] == 183, 'Expected AArch64 ELF64LE')
    offset = struct.unpack_from('<Q', elf, 32)[0]
    phsize, phnum = struct.unpack_from('<HH', elf, 54)
    require(phsize >= 56 and phnum < 100 and offset+phsize*phnum <= len(elf), 'Bad ELF program headers')
    for i in range(phnum):
        kind, _, fileoff, virt, _, filesize, _, _ = struct.unpack_from('<IIQQQQQQ', elf, offset+i*phsize)
        if kind == 1 and virt <= va and va+4 <= virt+filesize:
            return struct.unpack_from('<I', elf, fileoff+va-virt)[0]
    raise ValueError('Unmapped ELF virtual address')

def target(at, instr, style):
    if style == 'b':
        require(instr & 0xfc000000 == 0x14000000, 'Expected unconditional B')
        bits, sign, multiplier = instr & 0x3ffffff, 1<<25, 1<<26
    else:
        require((instr & 0xff000010 == 0x54000000) if style=='cond' else
                (instr & 0x7f000000 == 0x34000000), 'Expected conditional/CBZ')
        bits, sign, multiplier = (instr>>5)&0x7ffff, 1<<18, 1<<19
    return at + (bits-multiplier if bits & sign else bits)*4

def verify(elf):
    require(hashlib.sha256(elf).hexdigest()==ELF_SHA, 'Original tactics ELF SHA-256 mismatch')
    for va, expected in WORDS.items():
        require(word_at_va(elf,va)==expected, f'Native anchor changed at {va:#x}')
    edges={
        (0x252bf0,'cond'):0x252ca0, (0x252bf8,'cond'):0x252d00,
        (0x252c00,'cond'):0x252ce0, (0x252c14,'cond'):0x252c98,
        (0x250dfc,'cond'):0x252128, (0x250df0,'cbz'):0x251824,
        (0x252be8,'cbz'):0x252c78, (0x252c9c,'b'):0x252a60,
        (0x252cc4,'b'):0x252c08, (0x252cfc,'b'):0x252c08,
        (0x252d20,'b'):0x252c08,
    }
    for (addr,mode), expected in edges.items():
        require(target(addr,word_at_va(elf,addr),mode)==expected,
                f'Native edge changed at {addr:#x}')
    require(word_at_va(elf,0x252c5c)==0x17f9d015 and
            target(0x252c5c,word_at_va(elf,0x252c5c),'b')==0xc6cb0,
            'FindA tail-call changed')
    return len(WORDS),len(edges)+1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior-zip',required=True)
    args=parser.parse_args()
    with zipfile.ZipFile(args.prior_zip) as f:
        matches=[p for p in f.namelist() if '/files/liblethe_tactics_tree.so/' in p]
        require(len(matches)==1,'Expected exactly one original tactics ELF')
        words,edges=verify(f.read(matches[0]))
    print(f'X40_R2416_V198_REPO_NATIVE_BRANCH_PASS {words} anchors {edges} edges')
    print('Static compiled behavior only; no live calibration selection or physical rewash proven.')

if __name__=='__main__':
    try: main()
    except (OSError,ValueError,KeyError,struct.error,zipfile.BadZipFile) as exc:
        raise SystemExit(f'X40_R2416_V198_REPO_NATIVE_BRANCH_FAIL: {exc}')
