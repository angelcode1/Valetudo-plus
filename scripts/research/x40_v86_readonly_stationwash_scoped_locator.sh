#!/bin/sh
# X40 R2416 v86: only exact XML name metadata in bounded roots.
# Usage: ssh root@ROBOT 'sh -s -- --inventory' < x40_v86_readonly_stationwash_scoped_locator.sh
# Does not read file contents except sha256 for exact XML names; no writes or service actions.
set -u
if [ "${1:-}" != '--inventory' ] || [ "${2:-}" != '' ]; then
    echo 'Usage: sh script --inventory' >&2
    exit 2
fi
printf '%s\n' 'X40_V86_SCOPED_XML_READ_ONLY_BEGIN'
if ! find /tmp -xdev -maxdepth 0 -type d -print >/dev/null 2>&1; then
    echo 'X40_V86_REFUSE: bounded find options unsupported' >&2
    exit 3
fi
for root in /data /tmp /etc /usr/etc /usr/local /var/lib /mnt/vendor; do
    [ -d "$root" ] || continue
    # -xdev prevents following another mounted filesystem. The exclusions
    # protect Android/user state, caches, libraries and old Valetudo backups.
    # -maxdepth restricts the amount of disk metadata traversed.
    find "$root" -xdev -maxdepth 5 \
        \( -type d \( \
          -name user -o -name user_de -o -name app -o -name system -o \
          -name misc -o -name media -o -name cache -o -name backup -o \
          -name backups -o -name dalvik-cache -o -name valetudo-x40-fork-stage14 \
        \) -prune \) -o \
        \( -type f \( -name StationWash.xml -o -name RobotNode.xml \) -print \) \
        2>/dev/null | while IFS= read -r f; do
            [ -f "$f" ] && [ ! -L "$f" ] || continue
            size=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
            hash=$(sha256sum "$f" 2>/dev/null | awk '{print $1}')
            printf 'X40_V86_XML_FOUND path=%s size=%s sha256=%s\n' "$f" "$size" "$hash"
        done
    printf 'X40_V86_SCANNED_ROOT=%s maxdepth=5 exact_names_only\n' "$root"
done
printf '%s\n' 'X40_V86_SCOPED_XML_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_FILE_CONTENT_EXPORTED'
