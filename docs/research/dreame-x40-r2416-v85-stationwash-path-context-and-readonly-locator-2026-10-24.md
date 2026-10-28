# X40 R2416 v85 — working-directory XML loader evidence and read-only StationWash locator

**2026-10-24 · Offline SHA-pinned ELF research only.** Nothing was changed on the robot, and no native firmware binaries, XML file contents, private settings, map data or credentials are committed. The operator's last-confirmed installation is working **Valetudo+ v74**, with `SmartHost=0`, the original launcher restored, and the experimental write gate disabled after reboot.

## New original-library evidence

The v84 proof already showed compiled `subtree_file_path=StationWash.xml` without an absolute filename and a fresh-build `SubtreeConditionNode::onInit()` route that passes its wrapper Blackboard to `BT::buildTreeFromFile` and `BT::XMLParser::instantiateTree`. v85 examines the XML loader's path behavior:

| Original `libbehaviortree_cpp.so` VA | Pinned native operation |
|---|---|
| `0x6f9d8` | Calls imported `filesystem::path::getcwd()` in `BT::XMLParser::loadFromFile()` |
| `0x6f9e0` | Retains part of the process-current-directory path representation |
| `0x6fb68` | Loads ASCII slash `/` as the separator |
| `0x6fb90` | Calls `std::string::find_first_of` while splitting components |
| `0x6fe50` | Calls imported `filesystem::path::make_absolute()` |
| `0x70284` | `BT::buildTreeFromFile` calls `XMLParser::loadFromFile` |
| `0x7028c`, `0x702a4` | Forwards previously received Blackboard reference to `XMLParser::instantiateTree` |

**Interpretation:** the XML loader captures a **process CWD** and uses an absolute-path conversion. This establishes the value of checking the live native process working directory, instead of assuming the XML is colocated with a particular `.so`. It does **not** prove the final resolved filename, that `StationWash.xml` loaded during the observed robot session, or any XML NodeConfig/remapping.

The two existing owner-private evidence ZIPs, `X40-R2416-v62-readonly-20261023T051829Z.zip` and `X40-R2416-v63-runtime-gap-20261023T053118Z.zip`, have **no archive member** whose basename is `StationWash.xml`. This is only an archived-evidence gap, not a global filesystem-absence claim.

### Provenance and regression

SHA-256 of the original **private** files:
- `liblethe_tree.so`: `9d7eda3325b8278fc8caad66f7cb3f6b8c06d4ddd2821e414d57e6b7546e6c99`
- `libbehaviortree_cpp.so`: `665a7bab2231cb3352c1708fe04cb9739ea99752ffd6c752b35089052724af94`

The separately distributed sanitized package `X40-R2416-v85-sanitized-stationwash-path-20261024.zip` contains:
- `x40_r2416_v85_xml_path_context_verify.py` — stdlib-only, in-memory ZIP ELF verifier, with exact AArch64 instruction, PLT-symbol, `StationWash` parameter checks and two-archive inventory
- `x40_v85_readonly_stationwash_locator.sh` — optional metadata-only process-cwd and exact-XML-filename inventory
- The detailed sanitized report and README.

Offline verifier output against original owner-private ZIPs:

```text
X40_V85_STATIONWASH_FILENAME_RELATIVE_PARAMETER_STATIC_PASS
X40_V85_XML_LOADER_GETCWD_MAKE_ABSOLUTE_STATIC_PASS
X40_V85_XML_LOADER_SLASH_COMPONENT_SPLIT_STATIC_PASS
X40_V85_FRESH_TREE_FILE_LOAD_ROOT_FORWARD_STATIC_PASS
X40_V85_BOTH_PRIVATE_ARCHIVES_LACK_STATIONWASH_XML_PASS
X40_V85_INDEPENDENT_NATIVE_INSTRUCTION_MUTATIONS_REJECTED count=34
LIMIT: process cwd at runtime, real XML location/content, NodeConfig remaps, active station Blackboard and physical rewash unverified
```

The shell locator passed `sh -n` and a local execution test. **It has not been run on the vacuum.** It reads only `/proc/*/maps`, matching process `cwd`, and exact `StationWash.xml`/`RobotNode.xml` filenames in bounded conventional directories (`/ava`, `/tmp/ava`, `/tmp/lib`, `/tmp/cleanbot_pro`, `/usr/lib/tree_lib`, `/usr/share`, `/opt`, `/data/robot`). It prints a matching path, byte size and SHA-256, never exports XML contents, never scans all of `/data` or root, and performs **no writes, MIOT operations, restarts or debugger attachment**. The operator should inspect the script and can optionally run:

```sh
ssh root@ROBOT_IP 'sh -s -- --inventory' < x40_v85_readonly_stationwash_locator.sh
```

An empty result means **no match in the scoped search**, not that the real firmware lacks the XML. Publishing the XML itself, if found, is not requested; protect proprietary source. Do not guess a replacement XML or force a native gate.

## Next research boundary

If an authentic `StationWash.xml` path is identified, separately inspect a privately reviewed copy for NodeConfig Blackboard scopes and key remappings. Then revisit an R2416-reachable writer for `special_push_clean_dish` and the unclosed path from `TurbidityResultFail` through `r2343_start_rewash` to a genuinely **second physical station wash**. These remain unproven. Keep verified v74, `SmartHost=0`, closed write gate and existing rollback files intact.
