# X40 R2416 v193 — Next-point vs original-point consumers

Date: 26 October 2026 · Offline analysis of the user's privately supplied original `liblethe_route_nodes.so`, SHA-256 `fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e`. No runtime changes or robot access.

## Exact bounded native reference census

An executable-section, **strict adjacent AArch64 ADRP+ADD** address-construction scan of two exact Blackboard literal strings found:

| Blackboard key | Literal VA | All adjacent references |
| --- | --- | --- |
| `next_dynamic_obstacles_point` | `0x1007d08` | `0xaeee4c` in `GetNextDynamicObstaclesArea::tick`; `0xb14e2c` in `PresetBlackboard::tick` |
| `original_dynamic_obstacles_point` | `0x1007ce0` | `0xaee92c` (next-area selector); `0xaf0268` (dynamic area clear check); `0xaf1be4` (obstacle check); `0xaf231c` (goal angle); `0xf82920` (MapSensor::PointCloudEliminate); `0xf8be54` (MapSensor::CleanedAreaBuild) |

The `next` key is staged by a setter-compatible virtual call at `0xaeee90` (v192). At the other direct-reference site, `PresetBlackboard::tick()` invokes an internal key routine at `0xb14e3c`, tests a pointer, and calls **virtual slot +0x30** at `0xb14e54`. It is not established whether the latter is a typed read, erase, or some other operation. Thus **no unambiguous direct named reader** of the next-point key is identified by this bounded reference census. This is **not** proof that no indirect reader, behavior-tree port binding, dynamically constructed reference, or cross-module consumer exists.

For `original_dynamic_obstacles_point`, `GetNextDynamicObstaclesArea::tick()` stages the point through a virtual setter-compatible call at `0xaee990`. Three different functions—`DynamicObstanceAreaIsClear::tick()` (`0xaf038c`), `CheckDynamicObstance::tick()` (`0xaf1d0c`) and `GetToGoalAngle::tick()` (`0xaf248c`)—contain direct calls to `SafeAny::Any::cast<gte::Vector<2,int>>` after constructing the same key. Two additional MapSensor functions reference the string; their access direction is not established from literal xrefs alone.

### Navigation-specific code

`GetToGoalAngle::tick()` uses integer coordinate arithmetic and contains `atan2` at `0xaf24e4` plus `fmod` at `0xaf250c`, with angle and coordinate arithmetic in the same function. Together these are **compiled support for a navigation/heading-related use** of the original point. Runtime execution, exact goal source, motion-controller command, or a second-area cleaning task are not demonstrated.

## Validation and limitations

The full **v184–v193** verifier suite on the pinned private original ELF passed **239 tests**, including isolated instruction mutations. The new v193-specific suite contains 17 tests (five independent plus 12 original-ELF tests). A fresh extract of the release ZIP with no private ELF ran **197 tests: 114 passed, 83 skipped**. All **35 packaged-file SHA256SUMS checks** passed.

Validated private/offline archive: `X40-R2416-v193-sanitized-dynamic-point-consumers.zip`, SHA-256 `7e3b23509728f3e434c4e6dfd63d35e6766c96de36bf15e31d3dde071ae48d43`. The executable full standard-library Python verifiers and tests remain **inside the separately supplied ZIP**; this commit additionally includes a compact independent repository-side check and tests. No proprietary ELF, photos, map coordinates, credentials or robot-control code included.

**Not proven:** a direct task-start edge, a navigation goal becoming a new cleaning task, same runtime Blackboard instance, a dirt-driven scheduling event, any physical second floor pass, or CleanGenius causation for the v165 revisits.

**Next research focus:** inspect behavior-tree configuration / port bindings for `next_dynamic_obstacles_point`, `original_dynamic_obstacles_point`, `CheckDynamicObstance`, `GetToGoalAngle` and any actual *cleaning-task dispatch* action. A string-reference census by itself has reached its evidence limit.

Safety: preserve working Valetudo+ v74, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, `writeGateOpen=false`. No device actions.
