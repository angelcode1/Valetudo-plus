# X40 R2416 v88 — native resource layout and mount-target inventory

**2026-10-24 · User-supplied v87 metadata; v88 tool not executed on X40.** No native MIOT command, restart, firmware update or vendor binary collection.

## Operator's v87 output

The operator supplied the following native-process and namespace results:

```text
X40_V87_NATIVE_PID=1736
X40_V87_PROCESS_cwd=/data
X40_V87_PROCESS_root=/
X40_V87_PROCESS_ns/mnt=mnt:[4026531840]
X40_V87_SSH_MOUNT_NAMESPACE=mnt:[4026531840]
X40_V87_NATIVE_LIBRARY=/tmp/ava/lib/node_lethe.so
X40_V87_NATIVE_LIBRARY=/tmp/lib/tree_lib/liblethe_tree.so
X40_V87_NATIVE_LIBRARY=/usr/lib/libbehaviortree_cpp.so
X40_V87_SCANNED=/proc/1736/cwd depth=3
X40_V87_SCANNED=/proc/1736/root/ava depth=3
X40_V87_SCANNED=/proc/1736/root/tmp/ava/lib depth=3
X40_V87_SCANNED=/proc/1736/root/tmp/lib/tree_lib depth=3
X40_V87_SCANNED=/proc/1736/root/usr/lib depth=3
X40_V87_SCANNED=/proc/1736/root/usr/lib/tree_lib depth=3
X40_V87_NATIVE_PATHS_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_XML_CONTENT_EXPORTED
```

There were **no XML_MATCH markers** in that scoped run. The native process had root `/` and exactly the **same mount namespace identifier as SSH**, so separate namespaces and a process-specific chroot do not explain these particular no-match observations. No global absence conclusion follows: v87 scanned only a few roots to a depth of 3, and earlier v86 explicitly used `-xdev` and pruned multiple subtrees.

## New v88 read-only hypothesis test

`scripts/research/x40_v88_native_resource_layout_readonly.sh` (also downloadable separately) inspects:
1. Relevant mount **destinations only** from `/proc/PID/mountinfo`, never mount sources, credentials or full mount options, to learn whether `-xdev` could skip resource mounts;
2. Directory symlinks and filenames of `*.xml`, `*.zip`, `*.tar`, `*.tgz`, `*.pak`, `*.bundle`, `*.rcc` under selected native resource dirs: `/tmp/ava`, `/tmp/lib/tree_lib`, `/tmp/cleanbot_pro`, `/ava`, `/usr/lib/tree_lib`, `/usr/share/ava`, `/opt/ava`, `/data/cleanbot_pro`, `/data/robot`.

The script finds the current native PID through mapped `node_lethe.so`, performs bounded `find -xdev -maxdepth` calls, limits output per candidate resource directory and reads file size only. It does **not** dump XML contents or archive members, enumerate general personal data under `/data`, read native MIOT properties or make writes. Syntax check and a local no-native-process smoke test passed. **The actual X40 has not been probed with v88 at time of this commit.**

Operator command from a reviewed local copy:

```sh
ssh root@192.168.8.149 'sh -s -- --inventory' < x40_v88_native_resource_layout_readonly.sh
```

The result may suggest an XML file in a package or in a mounted resource directory, but filenames alone cannot prove such a package contains `StationWash.xml`. Further file inspection must remain separately reviewed and private.

## Established limits

The v84 pinned ELF evidence demonstrates the relative `StationWash.xml` parameter in a compiled subtree and fresh Blackboard forwarding to `XMLParser::instantiateTree`. Neither active `StationWash.xml` remapping nor same live child Blackboard instance has been observed. Other R2416-compatible writers of `special_push_clean_dish`, actual sensor triggers and physical second station wash also remain unverified.

**Live X40 unchanged**: last operator-confirmed Valetudo+ v74; `SmartHost=0`, `writeGateOpen=false`, launcher restored, native baseline intact following the successful controlled 1→0 write/readback and disarm. Keep all original/parent/v70/v73 backups; do not enable the test gate to pursue this research.
