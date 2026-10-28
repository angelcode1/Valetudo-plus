#!/bin/sh
# X40 R2416 Stage47: fixed-path read-only native evidence stream.
# stdout is ALWAYS a tar stream on --emit. No scratch file is created.
set -eu
LC_ALL=C
export LC_ALL
TARGET=/usr/lib/tree_lib/liblethe_tactics_tree.so
MAX_BYTES=80000000

case "${1:-}" in
    --self-test)
        [ "$#" -eq 1 ] || exit 64
        [ "$TARGET" = /usr/lib/tree_lib/liblethe_tactics_tree.so ] || exit 70
        [ "$MAX_BYTES" -eq 80000000 ] || exit 70
        printf '%s\n' 'X40_STAGE47_REMOTE_SELFTEST_PASS fixed_path=true no_device_actions=true'
        exit 0 ;;
    --emit)
        [ "$#" -eq 1 ] || exit 64 ;;
    *)
        printf '%s\n' 'Usage: sh stage47_on_vacuum.sh --self-test|--emit' >&2
        exit 64 ;;
esac

[ -f "$TARGET" ] && [ -r "$TARGET" ] || {
    printf '%s\n' 'X40_STAGE47_REMOTE_STOP=LIBRARY_UNREADABLE' >&2
    exit 65
}
SIZE=$(wc -c < "$TARGET" 2>/dev/null) || {
    printf '%s\n' 'X40_STAGE47_REMOTE_STOP=SIZE_CHECK_FAILED' >&2
    exit 65
}
case "$SIZE" in ''|*[!0-9]*)
    printf '%s\n' 'X40_STAGE47_REMOTE_STOP=BAD_FILE_SIZE' >&2
    exit 65 ;;
esac
[ "$SIZE" -gt 0 ] && [ "$SIZE" -le "$MAX_BYTES" ] || {
    printf '%s\n' 'X40_STAGE47_REMOTE_STOP=FILE_SIZE_OUT_OF_BOUNDS' >&2
    exit 65
}

# No log, credential, map, model, config or token is accessed. No robot writes.
# exec avoids appending any script output after the binary tar data.
cd /
exec tar -cf - usr/lib/tree_lib/liblethe_tactics_tree.so
