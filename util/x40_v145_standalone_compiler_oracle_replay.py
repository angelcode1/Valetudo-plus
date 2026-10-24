#!/usr/bin/env python3
"""Independently reassemble synthetic X40 v145 AArch64 opcode oracle (no vendor code)."""
import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

SHA256='77934d23a47c1dae5a6a146ebeadff415242d53259c93d47f60de40366bef925'
PATTERN=re.compile(r'^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s+',re.I)
MNEMONICS=set('str strb strh stur sturb sturh stp stnp sttr sttrb sttrh ldr ldrb ldrh ldur ldurb ldurh ldp ldnp ldtr stadd ldadd ldaddal swp cas stlr ldar stxr ldxr'.split())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('oracle',type=Path)
    p.add_argument('--clang',default=shutil.which('clang'))
    p.add_argument('--objdump',default=shutil.which('llvm-objdump'))
    a=p.parse_args()
    if not a.clang or not a.objdump:p.error('requires AArch64 Clang and llvm-objdump')
    raw=a.oracle.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA256:raise ValueError('synthetic fixture SHA-256 mismatch')
    with a.oracle.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
    if len(rows)!=1857 or set(rows[0])!={'word_hex','store','offset','width','variable','assembly'}:
        raise ValueError('unexpected oracle schema/count')
    for r in rows:
        asm=r['assembly']
        if not asm or len(asm)>128 or '\n' in asm or asm.split()[0] not in MNEMONICS:
            raise ValueError('unexpected assembly content')
    text='.text\n.global x40_v145_fixture\nx40_v145_fixture:\n'+''.join('    '+r['assembly']+'\n' for r in rows)
    with tempfile.TemporaryDirectory(prefix='x40-v145-') as td:
        source=Path(td)/'fixture.s';obj=Path(td)/'fixture.o'
        source.write_text(text)
        subprocess.run([a.clang,'--target=aarch64-none-elf','-march=armv8.5-a+lse','-c',str(source),'-o',str(obj)],check=True,capture_output=True)
        output=subprocess.run([a.objdump,'-d',str(obj)],check=True,capture_output=True,text=True).stdout
    got=[int(m.group(1),16) for line in output.splitlines() if (m:=PATTERN.match(line))]
    expected=[int(r['word_hex'],16) for r in rows]
    if got!=expected:raise AssertionError('assembled AArch64 opcode mismatch')
    print('X40_V145_STANDALONE_ASSEMBLER_REPLAY_PASS opcodes=1857')

if __name__=='__main__':main()
