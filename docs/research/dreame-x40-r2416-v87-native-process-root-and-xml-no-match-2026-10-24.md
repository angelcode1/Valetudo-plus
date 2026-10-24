# Dreame X40 R2416 — v87: scoped XML no-match and process namespace checkpoint

**2026-10-24. Operator-supplied read-only evidence; no robot change.**

## v86 result

The operator executed the v86 exact-name, max-depth-five scanner and supplied:

```text
X40_V86_SCOPED_XML_READ_ONLY_BEGIN
X40_V86_SCANNED_ROOT=/data maxdepth=5 exact_names_only
X40_V86_SCANNED_ROOT=/tmp maxdepth=5 exact_names_only
X40_V86_SCANNED_ROOT=/etc maxdepth=5 exact_names_only
X40_V86_SCANNED_ROOT=/usr/etc maxdepth=5 exact_names_only
X40_V86_SCANNED_ROOT=/usr/local maxdepth=5 exact_names_only
X40_V86_SCANNED_ROOT=/var/lib maxdepth=5 exact_names_only
X40_V86_SCOPED_XML_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_FILE_CONTENT_EXPORTED
```

No `X40_V86_XML_FOUND` line was produced. A missing `/mnt/vendor` scan marker means that root was not enumerated by the conditional root loop. **No XML was found in the enumerated paths, within the stated depth and prune exclusions.** Notably, v86 excluded Android app/user, internal system and cached subtrees, skipped mounted subfilesystems with `-xdev`, did not follow directory symlinks, and redirected `find` errors to `/dev/null` while still printing `SCANNED_ROOT`. Therefore this is **not an audited proof of a complete scan**, global XML absence, or missing runtime native station capability.

The preceding v85 metadata-only check independently found native process PID `1736` and `cwd=/data`, with no exact XML matches in its different limited roots. PID may change without notice; do not hardcode it.

## v87 follow-up: native process mount/root/library metadata

Instead of another blind-wide recursive scan, `scripts/research/x40_v87_native_paths_readonly.sh` reads `/proc/[pid]/maps` to identify a process containing `node_lethe.so`. It reports:

- the current PID, CWD, `/proc/PID/root` target and PID/SSH process mount namespace identifiers;
- only the mapped paths of `node_lethe.so`, `liblethe_tree.so` and `libbehaviortree_cpp.so`, not full memory maps;
- exact `StationWash.xml` and `RobotNode.xml` filenames if present within three levels of a few **process-visible** candidate resource roots and the native library directories.

The script has a bounded BusyBox-`find` compatibility check, applies directory pruning, uses `-xdev`, and reports `X40_V87_SCAN_INCOMPLETE` if any scoped `find` returns a nonzero status. It does not dump file contents, seek device identifiers, inspect MIOT settings or write files. It was syntax-checked and smoke-tested locally, **not executed on the robot**.

Operator may opt to run from a locally reviewed copy:

```sh
ssh root@192.168.8.149 'sh -s -- --inventory' < x40_v87_native_paths_readonly.sh
```

If library paths are in a different filesystem/mount namespace, this may explain some negative results. A `StationWash.xml` match provides only a path, **not** its contents or evidence of active NodeConfig scope and key mapping. Missing matches cannot establish absence: packed, generated, renamed, mounted or inaccessible resources remain possible.

### Existing firmware conclusions

The v84 static evidence confirms `subtree_file_path=StationWash.xml` and the root Blackboard argument on a fresh file-tree path; v82/v83 found one known model-gated `special_push_clean_dish` writer not selected by the direct R2416 model branch, and a separate reader. These are *compiled* facts; the active subtree key scope, other writers, genuine turbidity/soil decisions and a second physical station wash remain unproven.

**No native settings change.** Keep live tested Valetudo+ v74 with original launcher restored, `SmartHost=0`, `writeGateOpen=false`, original settings baseline and all recovery binaries preserved. No firmware installation, reboot, invasive tracing or native MIOT write is warranted.

No original vendor binary, XML, secrets, full maps or device-specific private data are committed.
