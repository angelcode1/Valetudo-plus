# X40 R2416 — private wash-status to MIOT property candidate

**Evidence date:** 2026-10-19. **Source:** offline ARM64 analysis of the user-supplied, screened, private firmware archive. This document contains original research descriptions only, not proprietary binaries, disassembly, credentials, model weights, map records, or raw firmware configuration.

## Static findings

In the user's saved `node_msg_cvt.so`, the exported native converter defines:

- `avanodemsgcvt::MsgClean::GetStationAutoWashState(AvaJson&, AvaJson&)`: reads the converter's stored 32-bit status integer and inserts it into an `AvaJson` result.
- `avanodemsgcvt::MsgClean::SetStationAutoWashState(int, bool)`: compares the new 32-bit value with the stored value, updates it on change and calls `AvaNodeMsgCvt::AddReportMsg(...)`. A *compiled report scheduling path* exists.
- `avanodemsgcvt::MsgClean::RptStationAutoWashState(char*, int)`: formats a standard MIOT property report containing `did`, `siid`, `piid` and an integer `value`.

The Setter and Report functions both encode property identifier **PIID 61 (0x3d)**, while the **SIID is taken from the MsgClean instance**. The getter and reporter read the same stored integer. This is stronger evidence than a string-name match. It establishes the *compiled property/report format*, not the configured service identifier, real runtime value, or whether X40 R2416 advertises it to connected local clients. `node_msg_cvt.so` also defines `MsgClean::GetMopStatus`, `GetSpecTaskStatus`, `GetAutoWaterStatus` and other status getters. Their existence does not establish that these are public, model-supported MIOT properties.

## Integration boundaries

- **Do not assume `4:61` is supported.** We know `PIID=61` for the internal `MsgClean` property but have **not independently verified its SIID or live publication** on the R2416 device.
- Do not write to this candidate property or enumerate arbitrary MIOT ranges; do not install hooks or transmit AVA messages.
- If a supported, naturally emitted `properties_changed` notification later provides both verified `siid` and `piid=61`, an *allowlisted passive, read-only* observation may be added with a bounded cache and an explicitly unknown semantic mapping, subject to device-specific validation.
- The currently implemented `GET /api/v2/robot/clean-genius/status` remains limited to verified existing MIOT 4:50 settings and already-polled mop-dock activity. That endpoint provides no measured dirtiness, no water turbidity, and no proven cause for extra mop washes.
- All proprietary firmware files stay private and out of the public Git repository. Running Valetudo 2026.10.0 and mapping remain untouched.

**Provenance and status:** only offline compiled behaviors have been checked; no live MIOT protocol test, frontend build, or robot deployment was performed.
