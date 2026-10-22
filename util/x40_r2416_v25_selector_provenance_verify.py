#!/usr/bin/env python3
"""X40 R2416 v25: offline selector-loader provenance and minimal file inventory.

Usage:
  python3 x40_r2416_v25_selector_provenance_verify.py X40-Firmware-Reference.zip
  python3 x40_r2416_v25_selector_provenance_verify.py X40-Firmware-Reference.zip --rootfs /path/to/offline/extracted/rootfs

Reads local data only. Does not connect to a robot, execute ELF code, copy original
firmware or publish private config. Default output is a sanitized JSON summary.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import sys
import tarfile
import zipfile

PINS = {
    'node_lethe.so': 'b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0',
    'liblethe_tactics_tree.so': 'da7c04cab9c2dd0a4e857a3c9fddac646a50e6d565b58c8f058b8d4e910a383c',
    'liblethe_tree.so': '9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99',
    'liblethe_route_nodes.so': 'fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e',
    'libbehaviortree_cpp.so': '665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94',
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def only(items, endswith, label):
    matched = [v for v in items if v.endswith(endswith)]
    require(len(matched) == 1, '{}: expected exactly one match, found {}'.format(label, len(matched)))
    return matched[0]

class PinnedElf:
    def __init__(self, raw):
        self.raw = raw
        require(raw[:6] == b'\x7fELF\x02\x01', 'expected ELF64 little endian')
        require(struct.unpack_from('<H', raw, 18)[0] == 183, 'expected AArch64')
        self.ranges = []
        phoff = struct.unpack_from('<Q', raw, 32)[0]
        ent, count = struct.unpack_from('<HH', raw, 54)
        require(ent >= 56 and count < 256, 'invalid program headers')
        for i in range(count):
            typ, _, off, va, _, length, _, _ = struct.unpack_from('<IIQQQQQQ', raw, phoff + i * ent)
            if typ == 1:
                require(off + length <= len(raw), 'bad segment extent')
                self.ranges.append((va, va + length, off))

    def read(self, va, size):
        for lo, hi, off in self.ranges:
            if lo <= va and va + size <= hi:
                return self.raw[off + va - lo:off + va - lo + size]
        raise ValueError('unmapped ELF address {}'.format(hex(va)))

    def word(self, va):
        return struct.unpack('<I', self.read(va, 4))[0]

    def instruction(self, va, expected):
        require(self.word(va) == expected, 'instruction mismatch at {}'.format(hex(va)))

    def call(self, pc, target):
        ins = self.word(pc)
        require(ins & 0xfc000000 == 0x94000000, 'not BL at {}'.format(hex(pc)))
        rel = ins & 0x03ffffff
        if rel & (1 << 25):
            rel -= 1 << 26
        require(pc + rel * 4 == target, 'different branch target at {}'.format(hex(pc)))

    def literal(self, va, value):
        require(self.read(va, len(value) + 1) == value.encode() + b'\x00',
                'literal mismatch at {}'.format(hex(va)))


def archive_check(source):
    with zipfile.ZipFile(source) as z:
        names = [n for n in z.namelist() if not n.startswith('__MACOSX/') and '/._' not in n]
        archive = only(names, '/X40_R2416_original_vendor_native_ELFs.tar', 'original TAR')
        with tarfile.open(fileobj=io.BytesIO(z.read(archive)), mode='r:') as t:
            members = [m for m in t.getmembers() if m.isfile()]
            libs = {}
            for name in PINS:
                if name == 'node_lethe.so':
                    continue
                candidates = [m for m in members if m.name.endswith('/' + name)]
                require(len(candidates) == 1, 'bad TAR member count for ' + name)
                libs[name] = t.extractfile(candidates[0]).read()
        libs['node_lethe.so'] = z.read(only(names, '/robot/ava/lib/node_lethe.so', 'collected Lethe'))
        config = json.loads(z.read(only(names, '/robot/ava/conf/r2416.conf', 'R2416 model config')))
        for name, expected in PINS.items():
            require(hashlib.sha256(libs[name]).hexdigest() == expected, 'SHA-256 mismatch for ' + name)
        nodes = [n for n in config['nodes'] if n.get('ID') == 'AvaNodeLethe']
        require(len(nodes) == 1, 'expected one AvaNodeLethe node')
        require(nodes[0].get('config_file_path') == '/ava/conf/setting.yaml',
                'model-specific selector-config path mismatch')
        missing = [name for name in ['setting.yaml', 'RobotNode.xml', 'Robot_Para.yaml']
                   if not any(n.split('/')[-1] == name for n in names)]
        require(len(missing) == 3, 'new selector files in source ZIP; inspect separately')
        elf = PinnedElf(libs['node_lethe.so'])
        # x23 <- original Parameter(string const&) argument, then x0 <- x23.
        elf.instruction(0x2bde74, 0xaa0103f7)
        elf.instruction(0x2be18c, 0xaa1703e0)
        elf.call(0x2be198, 0x279840)  # YAML::LoadFile import
        for pc, target, mov_x1, mov_x0 in [
            (0x2be310, 0x275d70, 0x2be308, 0x2be30c),
            (0x2be31c, 0x27a020, 0x2be314, 0x2be318),
            (0x2be328, 0x279280, 0x2be320, 0x2be324),
        ]:
            elf.instruction(mov_x1, 0xaa1403e1)  # same YAML subnode x20
            elf.instruction(mov_x0, 0xaa1303e0)  # same Parameter object x19
            elf.call(pc, target)
        for va, literal in [
            (0x9ce460, 'behavior_tree_path'),
            (0x9ce478, 'cleanbot_pro/RobotNode.xml'),
            (0x9ce498, 'tree_lib_path'),
            (0x9ce4a8, '/usr/lib/tree_lib'),
            (0x9ce4c0, 'robot_para_path'),
            (0x9ce4d0, '/data/Robot_Para.yaml'),
        ]:
            elf.literal(va, literal)
        elf.call(0x3901cc, 0x278bb0)  # GetInstance -> Parameter ctor import
        return {
            'status': 'X40_V25_SELECTOR_PROVENANCE_PASS',
            'libraries_verified': len(PINS),
            'config_file_path': '/ava/conf/setting.yaml',
            'compiled_config_load': 'Parameter(string const&) -> YAML::LoadFile',
            'compiled_selector_loader_order': [
                'behavior_tree_path', 'tree_lib_path', 'robot_para_path'],
            'compiled_fallbacks_not_runtime_values': {
                'behavior_tree_path': 'cleanbot_pro/RobotNode.xml',
                'tree_lib_path': '/usr/lib/tree_lib',
                'robot_para_path': '/data/Robot_Para.yaml',
            },
            'missing_from_supplied_zip': missing,
            'runtime_tree_selected': 'NOT_ESTABLISHED',
            'station_wash_instance_binding': 'NOT_ESTABLISHED',
        }


def safe_file_entry(root, rel):
    """Only open an ordinary local file and never follow symlinks in its ancestry."""
    p = root
    for part in rel.parts:
        p = p / part
        if p.is_symlink():
            return {'present': False, 'reason': 'symlink_refused'}
    if not p.is_file():
        return {'present': False}
    size = p.stat().st_size
    if size > 2_000_000:
        return {'present': True, 'hash_skipped': 'file_too_large'}
    raw = p.read_bytes()
    return {'present': True, 'size_bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def inventory(root):
    require(root.is_dir() and not root.is_symlink(), 'offline rootfs directory required')
    # Existence and hashes only. Never copy, print or upload private config/XML.
    candidates = [
        Path('ava/conf/setting.yaml'),
        Path('data/Robot_Para.yaml'),
        Path('ava/conf/cleanbot_pro/RobotNode.xml'),
        Path('ava/cleanbot_pro/RobotNode.xml'),
        Path('usr/lib/tree_lib/cleanbot_pro/RobotNode.xml'),
        Path('usr/lib/cleanbot_pro/RobotNode.xml'),
    ]
    return {str(path): safe_file_entry(root, path) for path in candidates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware_zip', type=Path)
    parser.add_argument('--rootfs', type=Path, help='Optional previously extracted offline rootfs directory')
    args = parser.parse_args()
    report = archive_check(args.firmware_zip)
    if args.rootfs:
        report['offline_rootfs_candidate_inventory'] = inventory(args.rootfs)
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, struct.error, tarfile.TarError,
            zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print('X40_V25_SELECTOR_PROVENANCE_FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)
