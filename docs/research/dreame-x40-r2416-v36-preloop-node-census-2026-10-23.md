# X40 R2416 v36 — direct pre-Loop node census

Date: 2026-10-23. Offline static analysis against pinned original ELFs and matching active tree-library hashes. No robot actions, firmware patching or Valetudo+ production changes.

## Verified direct RobotNode attachments preceding the Loop

| Slot | Attachment VA | Node type | Compiled instance / selected parameter |
|---|---|---|---|
| 1 | 0x30d940 | LDS_Switch | state=false |
| 2 | 0x30d978 | EraseBlackboard | key=playspeech_pause |
| 3 | 0x30d9b0 | SetBlackboardWithType | config_tick_frequency, int, 25 |
| 4 | 0x30d9e8 | SetMusicPlayPara | initialization music parameters |
| 5 | 0x30da20 | SetBlackboard | Start_Map_Load=true |
| 6 | 0x30da54 | SetBlackboard | robot_status=normal |
| 7 | 0x30da88 | SetBlackboard | robot_power_on has zero-length value |
| 8 | 0x30dabc | SetBlackboard | reset_wheel_before_clean=1 |
| 9 | 0x30daec | GetSegmentMapFuncRunning | empty parameter vector |
| 10 | 0x30db24 | SubTree | MapLoad |
| 11 | 0x30db60 | SubTree | RobotSysInit |
| 12 | 0x30e03c | SubTree | StationSysInit |
| 13 | 0x30e078 | SubTree | RobotmodeInit |
| 14 | 0x30e0b0 | SubtreeCondition | AlwaysSuccess.xml |
| 15 | 0x30e0e4 | SubtreeCondition | CountryGet.xml |
| 16 | 0x30e11c | Loop | num_cycles=-1 (prior v33–v35 check) |

The verifier checks the direct child-instantiation calls and attachment sites, constant-string parameter tables, and root construction-depth callsite census. It imports the committed v32 read-only SHA-pinned ELF loader. The earlier full standalone v36 verifier independently passed, and the changed-runtime-library test failed closed.

The StationSysInit factory call at 0x30ded8 branches past generated exception-cleanup blocks before the attach at 0x30e03c. This is why a naive nearest-BL scan is insufficient.

The zero-length robot_power_on value is a compiled ConstStr, not a proven Boolean or a runtime reading. Do not coerce it to false or zero.

## Implication and limitations

The earlier nodes include initialization tasks and subtree selectors. Their **actual return statuses** could govern whether the parent SequenceStarRoF advances into the Loop, but none of them is proven to fail, succeed or run on a particular live wash. This is a bounded direct-attachment census, not a complete live tree or nested-helper enumeration.

The compiled RobotNode → Loop → DoWhile → StationWash structure is increasingly well established. Yet the known ProcessModelInfo producer of special_push_clean_dish remains gated to other models; no R2416-compatible alternative producer, effective shared runtime Blackboard, normal dirty-water-to-rewash request chain or additional physical dock washing has been proven.

Reproduce the repository verifier with private archives:

    python3 util/x40_r2416_v36_preloop_nodes_verify.py X40-Firmware-Reference.zip X40-R2416-v27.zip

Expected final marker: X40_V36_PRE_LOOP_DIRECT_NODES_STATIC_PASS.

Keep VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0. Never commit private native ELFs, maps, raw device configuration or credentials.
