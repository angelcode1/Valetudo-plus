# X40 R2416 v228 — stain-identification switch, sensor value 4 and separate station-status decoder

**27 October 2026. Offline SHA-pinned owner firmware analysis.** Descends from v227; no robot commands, runtime Valetudo+ changes, feature enablement, or `master` change. Source-only and sanitized: no original vendor ELF, PRIVATE collector archives, device IP/PID, configuration or maps committed.

Original `node_lethe.so` SHA-256: `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`.

## Exact property Boolean writer → typed consumer

A complete *adjacent same-register ADRP+ADD* census of original host executable range **`0x2a0000–0x9c0000`** finds **two references** to exact `open_stain_identify` key at `0x9d6270`:

1. **`0x582bc8/0x582bcc`** in `AvaNodeRoute::WritePropIntProcessSUB`. A byte loaded from the handler's local property data at `0x582bc4` is staged at `0x582bd0` and passed through typed `BT::Blackboard::set<bool&>` at **`0x582be8 → 0x278ae0`**.
2. **`0x7b8584/0x7b8588`** in `AvaNodeRoute::SendMopStainCheckCmd`. The function calls typed `BT::Blackboard::get<bool>` at **`0x7b85a4 → 0x279900`** and branches at `0x7b85e0` based on getter success. **Getter success is not proof that the Boolean value itself was true**, and the compiled writer/reader is not proof both execute on the same runtime Blackboard instance.

The same narrow native instruction census finds **47 references** to literal `wash_status` (`0xa33250`) and **104** to `RobotMode` (`0x9d3fc8`). These are bounded syntactic references, not a census of actual runtime readers, writes, callers or live status values.

## Sensor byte 4 does not directly mean wash/MCU publication

The original `SendMopStainCheckCmd` path loads **`AvaSensorsMsg+0xfa`** at `0x7b872c`, compares it with numeric **4** at `0x7b8730`, and at **`0x7b8734`** branches **to `0x7b8d7c`**. This target stages **750** at `0x7b8d80` and writes it to a retained state counter at **`0x7b8d94`**. It is **not** either typed `_CtrlMcuCMD` publication entry.

A *separate* nonpositive retained-countdown branch **`0x7b871c → 0x7b8bf4`** leads to the previously established numeric **33/1** MCU payload path and conditional publisher at **`0x7b8c18`**. Earlier retained state could link conditions, but these immediate code paths are different.

The numeric **`RobotMode=16`** and **`WashStatus=2`** comparisons at `0x7b8688` and `0x7b8694` both branch to local block `0x7b8a80` when equal. Neither comparison reveals its manufacturer-defined enum meaning.

## Distinct message type: do not transfer interpretations across layouts

The independently compiled `ancp::StationWashStatus::GetWashBoxState(ancp::STATION_WASH_STATE_TYPE, ava_mop_station_msg const&)` at `0x899980` switches on **STATION_WASH_STATE_TYPE values 5, 6, 7, 8** and reads **`ava_mop_station_msg`** bytes from distinct offsets such as `+0x4,+0x5,+0x8,+0x21,+0x2d,+0x52,+0x5a`. Some cases return numbers **0–3**. This is **not the same enum** as Blackboard `WashStatus`, and **not the same source structure** as `AvaSensorsMsg` with its `+0xfa` sensor byte.

Thus `WashStatus=2`, `RobotMode=16`, and sensor byte `4` **are not decoded to trustworthy OEM labels** by the inspected native evidence. In particular, don't label byte 4 as `start_wash` or `mop_dirty`.

## Verified kit, limitations and next work

Complete source-only `X40-R2416-v228-sanitized-analysis-kit.zip` SHA-256 **`f7de89e02ee788fdb5be67ce7d48395d74636e152a6208e54efba058bc33abb7`**, **292,943 bytes**, **139 ZIP entries** including manifest, **138/138 per-file SHA-256 checks** and ZIP CRC passed from a clean extraction. **11/11 focused v228 native and mutation tests passed from source and again from clean extraction**, including one key reference outside the word-anchor list being deliberately changed. The **separate complete historical v197–v227 regression replay exceeded the time limit** in v228; a full v228 historical pass is **not claimed**. Historical v227 clean replay passed previously. The new v228 native verifier checks **63 exact AArch64 instruction words, 2 switch references, 47 status references, 104 mode references, 6 decoded control-flow edges, four direct calls and the separate four-case station decoder**. Standalone Python 3 stdlib checker verified 18 words and all three key censuses. Vendor ELF and PRIVATE evidence are required locally to rerun and are not redistributed.

**Still not proven:** live enabled stain-identify flag, same runtime Blackboard identity, vendor enum meaning, code-15→MCU wash causality, dock rewash, or AI-stain-caused new floor-clean task and physical second pass. Next should investigate documented OEM enums/real station event producers offline, and independently trace `stain_area_for_logic` / `SetExtraCleanArea` to a production task start. Do not send raw test MCU commands.

Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0`, `SmartHost=0`, `SmartAutoMop=-1`, `SmartAutoWash=0`, and `writeGateOpen=false`.