#!/usr/bin/env python3
"""Compact X40 R2416 v233 original-health subscriber verifier (Python 3 stdlib).
Source-only: requires the owner's v230 PRIVATE archive; never publishes its bytes.
Full verifier and mutation suite are distributed in the separate source-only v233 kit.
"""
import argparse
import hashlib
import json
import struct
import zipfile

PIN = "5eb715d9f66816794823e31484f1f0c229cef07ea611414e1c3b020fc99471d5"
# Exact original AArch64 instruction words from the pinned AArch64 ELF.
ANCHORS = {
    0x5f2c4: 0xb00002e1, 0x5f2c8: 0x9109c021,
    0x5f2cc: 0xaa1403e0, 0x5f2d0: 0x97ffff34,
    0x5f2f0: 0xf9451c42, 0x5f2fc: 0xa9007c22,
    0x5f300: 0xf9466c63, 0x5f354: 0xaa1603e2,
    0x5f358: 0xaa1403e1, 0x5f35c: 0xf9475084,
    0x5f360: 0xaa1303e0, 0x5f364: 0x52800123,
    0x5f36c: 0x97ffb075, 0x4d228: 0xd2802102,
    0x4d250: 0x97fff328, 0x4d25c: 0x97fff719,
    0x5e66c: 0x3943e285, 0x5e67c: 0x3943e68c,
}
CALLS = {0x5f36c: 0x4b540, 0x4d250: 0x49ef0, 0x4d25c: 0x4aec0}

def digest(b):
    return hashlib.sha256(b).hexdigest()

def word(b, p):
    return struct.unpack_from("<I", b, p)[0]

def verify(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip():
            raise ValueError("Archive CRC failure")
        manifest = json.loads(z.read("manifest.PRIVATE.json"))
        saved = [r for r in manifest["records"] if r["status"] == "saved"]
        if len(saved) != 35:
            raise ValueError("Expected 35 original evidence members")
        checksums = dict(line.split("  ", 1) for line in
                         z.read("SHA256SUMS.PRIVATE.txt").decode().splitlines())
        if len(checksums) != 35:
            raise ValueError("Bad checksum manifest")
        original = None
        for r in saved:
            member = r["stored_as"]
            if not member.startswith("files/") or ".." in member:
                raise ValueError("Unsafe member")
            data = z.read(member)
            if (len(data) != r["size"] or digest(data) != r["original_sha256"]
                    or checksums.get(member) != digest(data)):
                raise ValueError("Original evidence hash/size mismatch")
            if member.endswith("-node_health_lethe.so"):
                if original is not None:
                    raise ValueError("Ambiguous original health ELF")
                original = data
    if original is None or digest(original) != PIN:
        raise ValueError("Wrong or missing SHA-pinned original health ELF")
    if original[0xbc270:0xbc278] != b"SENSORS\x00":
        raise ValueError("Original named-topic string mismatch")
    for a, expected in ANCHORS.items():
        if word(original, a) != expected:
            raise ValueError("Original AArch64 anchor mismatch: "+hex(a))
    for a, target in CALLS.items():
        inst = word(original, a)
        imm = inst & 0x03ffffff
        if imm & 0x02000000:
            imm -= 0x04000000
        if inst >> 26 != 0b100101 or a + 4*imm != target:
            raise ValueError("Original direct-call target mismatch")
    # The pinned ELF's .rela.dyn address/size and known R_AARCH64_GLOB_DAT
    # symbol indices (405: callback, 649: AvaSensorsMsg RTTI).
    relocations = {}
    for p in range(0x3a628, 0x3a628+0xd188, 24):
        where, info, _ = struct.unpack_from("<QQq", original, p)
        if where in (0xe8a38, 0xe8ea0):
            relocations[where] = info
    if (relocations.get(0xe8a38) != (405 << 32) + 1025
            or relocations.get(0xe8ea0) != (649 << 32) + 1025):
        raise ValueError("Callback/type-info relocation mismatch")
    # Exact unsigned-offset LDRB encoding, not all equivalent addressing modes.
    for p in range(0x4b800, 0x4b800+0x6f420, 4):
        inst = word(original, p)
        if (inst & 0xffc00000) == 0x39400000 and ((inst >> 10) & 0xfff) == 0xfa:
            raise ValueError("Unexpected exact offset-250 load in health .text")
    print("X40_R2416_V233_REPO_HEALTH_SUBSCRIBE_PASS", len(ANCHORS),
          len(CALLS), len(saved))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v230-private", required=True)
    verify(parser.parse_args().v230_private)
