#!/bin/sh
# X40 R2416: process-root and native-library path inventory.
# Read-only: /proc metadata and exact XML filename metadata only.
set -u
if [ "$#" -ne 1 ] || [ "$1" != '--inventory' ]; then
    echo 'Usage: sh x40_v87_native_paths_readonly.sh --inventory' >&2
    exit 2
fi
printf '%s\n' 'X40_V87_NATIVE_PATHS_READ_ONLY_BEGIN'
if ! find /tmp -xdev -maxdepth 0 -type d -print >/dev/null 2>&1; then
    echo 'X40_V87_REFUSE: required bounded find flags unsupported' >&2
    exit 3
fi
pid=''
for p in /proc/[0-9]*/maps; do
    [ -r "$p" ] || continue
    if grep -q 'node_lethe\.so' "$p" 2>/dev/null; then
        pid=\${p#/proc/}
        pid=\${pid%/maps}
        break
    fi
done
if [ -z "$pid" ]; then
    printf '%s\n' 'X40_V87_NATIVE_PROCESS_NOT_FOUND'
    printf '%s\n' 'X40_V87_NATIVE_PATHS_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS'
    exit 0
fi
printf 'X40_V87_NATIVE_PID=%s\n' "$pid"
for k in cwd root ns/mnt; do
    value=$(readlink "/proc/$pid/$k" 2>/dev/null || true)
    [ -n "$value" ] || value='unavailable'
    printf 'X40_V87_PROCESS_%s=%s\n' "$k" "$value"
done
value=$(readlink '/proc/self/ns/mnt' 2>/dev/null || true)
[ -n "$value" ] || value='unavailable'
printf 'X40_V87_SSH_MOUNT_NAMESPACE=%s\n' "$value"
printf '%s\n' 'X40_V87_NATIVE_LIBRARIES_BEGIN'
awk '{ p=$NF; if (p ~ /\/(node_lethe|liblethe_tree|libbehaviortree_cpp)\.so$/) print p }' "/proc/$pid/maps" 2>/dev/null | sort -u | while IFS= read -r path; do
    printf 'X40_V87_NATIVE_LIBRARY=%s\n' "$path"
done
printf '%s\n' 'X40_V87_NATIVE_LIBRARIES_END'
{
    printf '%s\n' "/proc/$pid/cwd" "/proc/$pid/root/data/cleanbot_pro" "/proc/$pid/root/ava" "/proc/$pid/root/usr/lib/tree_lib" "/proc/$pid/root/opt" "/proc/$pid/root/root"
    awk '{ p=$NF; if (p ~ /\/(node_lethe|liblethe_tree|libbehaviortree_cpp)\.so$/) print p }' "/proc/$pid/maps" 2>/dev/null | sort -u | while IFS= read -r path; do
        case "$path" in
            /*) dir=\${path%/*}; printf '%s\n' "/proc/$pid/root$dir" ;;
        esac
    done
} | sort -u | while IFS= read -r base; do
    [ -d "$base" ] || continue
    printf 'X40_V87_SCANNED=%s depth=3\n' "$base"
    matches=$(find "$base" -xdev -maxdepth 3 \
        \( -type d \( -name user -o -name user_de -o -name app -o -name app-private -o -name cache -o -name misc -o -name system -o -name media -o -name backups -o -name dalvik-cache \) -prune \) -o \
        \( -type f \( -name StationWash.xml -o -name RobotNode.xml \) -print \) \
        2>/dev/null)
    rc=$?
    if [ "$rc" -ne 0 ]; then
        printf 'X40_V87_SCAN_INCOMPLETE=%s rc=%s\n' "$base" "$rc"
    fi
    if [ -n "$matches" ]; then
        printf '%s\n' "$matches" | while IFS= read -r candidate; do
            [ -f "$candidate" ] && [ ! -L "$candidate" ] || continue
            printf 'X40_V87_XML_MATCH=%s\n' "$candidate"
        done
    fi
done
printf '%s\n' 'X40_V87_NATIVE_PATHS_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_XML_CONTENT_EXPORTED'
