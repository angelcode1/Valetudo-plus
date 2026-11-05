#!/bin/sh
# Generic X40 UI launch policy. No native protocol calls or setting writes.
# Arguments: launch|watch STATE ORIGINAL CANDIDATE_SHA ORIGINAL_SHA RELEASE
set -eu
umask 077
[ "$#" -eq 6 ] || exit 64
launch_mode="$1"
shift
state_dir="$1"
original_bin="$2"
candidate_sha="$3"
original_sha="$4"
release_id="$5"
case "$launch_mode" in launch|watch) ;; *) exit 64 ;; esac
case "$state_dir" in /*) ;; *) exit 64 ;; esac
case "$original_bin" in /*) ;; *) exit 64 ;; esac
case "$release_id" in ""|*[!A-Za-z0-9_-]*) exit 64 ;; esac
[ "${#candidate_sha}" -eq 64 ] && [ "${#original_sha}" -eq 64 ] || exit 64
case "$candidate_sha$original_sha" in *[!0-9a-f]*) exit 64 ;; esac

matches() {
    [ -f "$1" ] && [ ! -L "$1" ] &&
        [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ]
}
marker() {
    [ -f "$state_dir/$1" ] && [ ! -L "$state_dir/$1" ] &&
        [ "$(cat "$state_dir/$1")" = "$release_id" ]
}
mark_rollback() {
    (
        set -C
        printf '%s\n' "$release_id" > "$state_dir/rollback"
    ) || [ -e "$state_dir/rollback" ] || [ -L "$state_dir/rollback" ]
}
original() {
    # The calling startup command supplies its original config/data/log values.
    # Restore main default-off; do not inherit advanced or old test opt-ins.
    VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0
    export VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS
    unset VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED
    unset VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED
    unset VALETUDO_X40_NATIVE_SMARTHOST_TEST
    exec "$original_bin"
}

matches "$original_bin" "$original_sha" || exit 66
[ -x "$original_bin" ] || exit 66
if [ ! -d "$state_dir" ] || [ -L "$state_dir" ] || ! marker release; then
    [ "$launch_mode" != watch ] || exit 65
    original
fi

if [ "$launch_mode" = watch ]; then
    (
        set -C
        printf '%s\n%s\n' "$$" "$release_id" > "$state_dir/watch.ready"
    )
    sleep 900
    # A rollback request always wins. Never undo it by accepting a release.
    [ ! -e "$state_dir/rollback" ] && [ ! -L "$state_dir/rollback" ] || exit 0
    marker accepted && exit 0
    mark_rollback || true
    sync
    reboot
    exit 0
fi

marker enabled || original
[ ! -e "$state_dir/rollback" ] && [ ! -L "$state_dir/rollback" ] || original
if [ -e "$state_dir/accepted" ] || [ -L "$state_dir/accepted" ]; then
    marker accepted || original
fi
matches "$state_dir/valetudo" "$candidate_sha" || original
[ -x "$state_dir/valetudo" ] || original
[ -f "$state_dir/config.json" ] && [ ! -L "$state_dir/config.json" ] || original
[ -d "$state_dir/data" ] && [ ! -L "$state_dir/data" ] || original

if ! marker accepted; then
    # An unconfirmed release gets only one boot attempt. A reboot or power loss
    # before acceptance selects the original service on the following boot.
    if ! mkdir "$state_dir/boot-attempt"; then
        mark_rollback || true
        original
    fi
    if [ -e "$state_dir/watch.ready" ] || [ -L "$state_dir/watch.ready" ]; then
        mark_rollback || true
        original
    fi
    nohup setsid sh "$0" watch "$@" > "$state_dir/watch.log" 2>&1 </dev/null &
    watch_count=0
    while [ ! -f "$state_dir/watch.ready" ]; do
        watch_count=$((watch_count+1))
        if [ "$watch_count" -ge 6 ]; then
            mark_rollback || true
            original
        fi
        sleep 1
    done
    watch_pid="$(sed -n '1p' "$state_dir/watch.ready")"
    watch_release="$(sed -n '2p' "$state_dir/watch.ready")"
    case "$watch_pid" in ""|*[!0-9]*) mark_rollback || true; original ;; esac
    if [ "$watch_release" != "$release_id" ] || ! kill -0 "$watch_pid"; then
        mark_rollback || true
        original
    fi
fi

# Enabling the manual UI control does not command SmartHost or start cleaning.
# Preserve the profile's ordinary integrations/timers; it is not a trial profile.
exec env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/root \
    VALETUDO_CONFIG_PATH="$state_dir/config.json" \
    VALETUDO_DATA_PATH="$state_dir/data" \
    VALETUDO_LOG_PATH="$state_dir/valetudo.log" \
    VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=1 \
    VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY=1 \
    VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED=0 \
    VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED=0 \
    VALETUDO_X40_NATIVE_SMARTHOST_TEST=0 \
    "$state_dir/valetudo"
