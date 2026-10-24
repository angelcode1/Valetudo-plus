# X40 R2416 v86 — live CWD checkpoint and scoped follow-up XML locator

**2026-10-24. No native setting writes or robot modifications.** This is a record of operator-supplied **read-only v85** output, not an independently executed remote session.

The operator ran the v85 filename locator through SSH on a rooted X40 and reported exactly:

```text
X40_V85_XML_LOCATOR_READ_ONLY_BEGIN
X40_V85_NATIVE_PID=1736
X40_V85_NATIVE_CWD=/data
X40_V85_XML_LOCATOR_READ_ONLY_END NO_NATIVE_WRITES NO_RESTARTS NO_FILE_CONTENT_EXPORTED
```

**What the output supports:** the running process whose `/proc/PID/maps` mentioned `node_lethe.so` had PID 1736 and an observable CWD of **`/data`**. The bounded v85 search printed **no** matching `StationWash.xml` or `RobotNode.xml` in its scanned locations.

**What the output does not support:** a complete `/data` file inventory, global absence of StationWash.xml, absence of compiled station code, or proof of active subtree semantics. The v85 locator checks only `/data/StationWash.xml` and `/data/cleanbot_pro/{StationWash,RobotNode}.xml` relative to the reported CWD, recursively checks `/data/robot`, and searches a few conventional system/resource paths. It does **not** recursively scan arbitrary `/data` children. Any current PID may change after reboot.

## v86 optional bounded follow-up

`scripts/research/x40_v86_readonly_stationwash_scoped_locator.sh` is a separate narrow read-only filename locator. Before searching, it refuses to proceed if the target `find` lacks the necessary `-maxdepth` and `-xdev` options. It scans a maximum of five directory levels below existing roots `/data`, `/tmp`, `/etc`, `/usr/etc`, `/usr/local`, `/var/lib` and `/mnt/vendor`; it prunes Android application/user/system/cache locations and previous Valetudo working state. It prints only exact `StationWash.xml`/`RobotNode.xml` path, byte size and SHA-256; it does not export XML contents, probe MIOT, write firmware, or restart anything. It was syntax-checked and smoke-tested **locally**, not yet run on the X40.

Operator command, from a trusted local copy of the checked script:

```sh
ssh root@192.168.8.149 'sh -s -- --inventory' < x40_v86_readonly_stationwash_scoped_locator.sh
```

Missing output remains a **scoped negative**, never proof of file absence. If exact XML is found, inspect it privately for active `StationWash` NodeConfig and Blackboard scopes before concluding that `special_push_clean_dish` is populated or physical rewash works. Do not collect unrelated files or copy proprietary XML to a public repo.

## Existing firmware state

Working Valetudo+ **v74** is last operator-confirmed, with native `SmartHost=0` restored, experimental `writeGateOpen=false`, original launcher reverted, and baseline intact after reboot. No changes are needed. Keep v70/v73, parent/original backups and settings protected.

The v84/v85 pin-based static evidence (original owner-private ELF) remains valid; this record adds **one live CWD observation and a limited metadata-only next step**, not a new static firmware proof.
