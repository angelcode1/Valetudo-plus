#!/bin/sh
# X40 R2416 v88: targeted native resource metadata only.
# Call via: ssh root@ROBOT 'sh -s -- --inventory' < script
# No file modifications, MIOT commands, process restarts, or source export.
set -u
if [ "$#" -ne 1 ] || [ "$1" != '--inventory' ]; then
    echo 'Usage: sh script --inventory' >&2
    exit 2
fi
printf '%s\n' 'X40_V88_NATIVE_RESOURCE_READ_ONLY_BEGIN'
if ! find /tmp -xdev -maxdepth 0 -type d -print >/dev/null 2>&1; then
    printf '%s\n' 'X40_V88_REFUSE: bounded find options unavailable' >&2
    exit 3
fi
pid=''
for p in /proc/[0-9]*/maps; do
    [ -r "$p" ] || continue
    if grep -q 'node_lethe\.so' "$p" 2>/dev/null; then
        pid=${p#/proc/}
        pid=${pid%/maps}
        break
    fi
done
if [ -z "$pid" ]; then
    printf '%s\n' 'X40_V88_NATIVE_PROCESS_NOT_FOUND'
    printf '%s\n' 'X40_V88_NATIVE_RESOURCE_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_FILE_CONTENT_EXPORTED'
    exit 0
fi
printf 'X40_V88_NATIVE_PID=%s\n' "$pid"
printf 'X40_V88_NATIVE_CWD=%s\n' "$(readlink /proc/$pid/cwd 2>/dev/null || printf unavailable)"
# /proc mountinfo field 5 is the mountpoint. Never publish source/device/credentials.
# Show only potentially relevant destinations; include separate mounts that -xdev skipped.
printf '%s\n' 'X40_V88_RELEVANT_MOUNT_TARGETS_BEGIN'
awk '
    $5 ~ /^\/(data|tmp|ava|usr|opt|mnt)(\/|$)/ {
        mp=$5
        if (mp ~ /^\/data\/(user|user_de|media|system|misc|app)(\/|$)/) next
        if (mp ~ /^\/mnt\/vendor(\/|$)/ || mp ~ /^\/tmp(\/|$)/ ||
            mp ~ /^\/ava(\/|$)/ || mp ~ /^\/opt(\/|$)/ ||
            mp ~ /^\/usr(\/|$)/ || mp == "/data" ||
            mp ~ /^\/data\/(robot|cleanbot_pro|ava|opt)(\/|$)/) print mp
    }
' "/proc/$pid/mountinfo" 2>/dev/null | sort -u | while IFS= read -r dest; do
    printf 'X40_V88_MOUNT_TARGET=%s\n' "$dest"
done
printf '%s\n' 'X40_V88_RELEVANT_MOUNT_TARGETS_END'
# Explicit narrow roots, no recursive /data or /usr/lib walk.
for root in /tmp/ava /tmp/lib/tree_lib /tmp/cleanbot_pro /ava /usr/lib/tree_lib /usr/share/ava /opt/ava /data/cleanbot_pro /data/robot; do
    [ -d "$root" ] || continue
    printf 'X40_V88_RESOURCE_ROOT=%s\n' "$root"
    # Link names and targets are limited to this small resource subtree.
    find "$root" -xdev -maxdepth 3 -type l -print 2>/dev/null | head -n 30 | while IFS= read -r link; do
        printf 'X40_V88_RESOURCE_SYMLINK=%s target=%s\n' "$link" "$(readlink "$link" 2>/dev/null || printf unavailable)"
    done
    # Only XML and likely XML containers; no binary contents are read.
    find "$root" -xdev -maxdepth 4 -type f \( \
        -iname '*.xml' -o -iname '*.zip' -o -iname '*.tar' -o -iname '*.tgz' -o \
        -iname '*.pak' -o -iname '*.bundle' -o -iname '*.rcc' \) -print 2>/dev/null | head -n 60 | while IFS= read -r f; do
        n=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
        printf 'X40_V88_RESOURCE_FILE=%s size=%s\n' "$f" "$n"
    done
    printf 'X40_V88_RESOURCE_ROOT_DONE=%s depth=4 output_limited=true\n' "$root"
done
printf '%s\n' 'X40_V88_NATIVE_RESOURCE_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_FILE_CONTENT_EXPORTED'
