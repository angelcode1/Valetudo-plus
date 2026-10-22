#!/usr/bin/env python3
"""Verify three distinct native YAML path-loader branches, offline, hash pinned.

Usage: python3 x40_r2416_v26_selector_paths_verify.py X40-Firmware-Reference.zip
Requires sibling x40_r2416_v25_selector_provenance_verify.py (Python stdlib only).
This never executes vendor code or connects to the X40.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import x40_r2416_v25_selector_provenance_verify as previous

# Names, start address, getter branch, fallback branch and exception address,
# YAML-to-string conversion call, fallback Assign call, Parameter member offset.
LOADER_SPECS = [
    ('behavior_tree_path', 0x2c4040, 0x2c4088, 0x2c4164, 0x2c4184, 0x2c4240,
     0x2c40c8, 0x2c4194, 0x08, 0x9ce460, 0x9ce478, 'cleanbot_pro/RobotNode.xml'),
    ('tree_lib_path', 0x2c44c0, 0x2c4508, 0x2c45e4, 0x2c4604, 0x2c46c0,
     0x2c4548, 0x2c4614, 0x28, 0x9ce498, 0x9ce4a8, '/usr/lib/tree_lib'),
    ('robot_para_path', 0x2c4940, 0x2c4988, 0x2c4a64, 0x2c4a84, 0x2c4b40,
     0x2c49c8, 0x2c4a94, 0x68, 0x9ce4c0, 0x9ce4d0, '/data/Robot_Para.yaml'),
]

def cbz_target(elf, pc):
    word = elf.word(pc)
    previous.require(word & 0x7f00001f == 0x34000000, 'CBZ w0 mismatch at ' + hex(pc))
    imm = (word >> 5) & 0x7ffff
    if imm & (1 << 18):
        imm -= 1 << 19
    return pc + imm * 4

def verify(source):
    # V25 verifies five full original SHA-256 pins plus actual R2416 config path.
    prior = previous.archive_check(source)
    with zipfile.ZipFile(source) as z:
        names = [n for n in z.namelist() if not n.startswith('__MACOSX/') and '/._' not in n]
        name = previous.only(names, '/robot/ava/lib/node_lethe.so', 'Lethe ELF')
        raw = z.read(name)
    previous.require(hashlib.sha256(raw).hexdigest() == previous.PINS['node_lethe.so'],
                     'node_lethe hash mismatch')
    elf = previous.PinnedElf(raw)
    output = []
    for key, start, first, fallback, second, exception, value_call, assign_call, member, name_va, default_va, default in LOADER_SPECS:
        previous.require(elf.read(start, 4) == b'\xfd\x7b\xb8\xa9', 'loader prologue changed')
        previous.require(cbz_target(elf, first) == fallback, 'first conditional branch changed: ' + key)
        previous.require(cbz_target(elf, second) == exception, 'invalid-node branch changed: ' + key)
        elf.call(value_call, 0x275590) # YAML::Node::as<std::string>()
        elf.call(assign_call, 0x273b90) # YAML::Node::Assign(char const*)
        elf.call(exception+4, 0x275600) # __cxa_allocate_exception
        elf.call(exception+12, 0x272710) # YAML::InvalidNode::InvalidNode()
        elf.literal(name_va, key)
        elf.literal(default_va, default)
        # The routine's returned Parameter string is offset-specific; inspect
        # two LDRs in normal path + fallback store address used by _M_replace.
        offset_ldr = {0x08: 0x2c40d8, 0x28: 0x2c4558, 0x68: 0x2c49d8}[member]
        instr = elf.word(offset_ldr)
        previous.require((instr & 0xffc0001f) == 0xf9400000,
                         'unexpected normal-path ldr encoding for ' + key)
        previous.require(((instr >> 10) & 0xfff) * 8 == member,
                         'Parameter field offset changed for ' + key)
        output.append({'key': key, 'parameter_offset': hex(member),
                       'yaml_to_string_call': hex(value_call),
                       'fallback_assignment': hex(assign_call),
                       'fallback': default, 'invalid_node_error_branch': hex(second),
                       'runtime_value': 'UNKNOWN'})
    return {'status': 'X40_V26_SELECTOR_BRANCHES_PASS', 'whole_file_sha256_verified': 5,
            'configured_yaml_path': prior['config_file_path'],
            'verified_selector_loaders': output,
            'missing_effective_yaml_and_tree': prior['missing_from_supplied_zip'],
            'fallback_guaranteed_for_missing_yaml_file_or_key': 'NOT_ESTABLISHED',
            'tree_instance_selected': 'NOT_ESTABLISHED',
            'runtime_blackboard_shared': 'NOT_ESTABLISHED'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware_zip', type=Path)
    args = p.parse_args()
    print(json.dumps(verify(args.firmware_zip), indent=2, sort_keys=True))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, zipfile.BadZipFile) as exc:
        print('X40_V26_SELECTOR_BRANCHES_FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)
