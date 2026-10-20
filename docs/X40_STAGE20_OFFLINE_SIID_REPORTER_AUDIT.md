# X40 Stage 20 — offline wash-property reporter investigation

Status: **offline analyzer prepared and tested on synthetic ARM64 ELF only; actual R2416 SIID remains unverified.** No user-device action or firmware write has been performed.

## Evidence chain

1. User-provided prior private R2416 native study recovered a compiled `avanodemsgcvt::MsgClean::RptStationAutoWashState` routine producing MIOT **PIID 61**. The SIID is selected from a `MsgClean` instance, not established by those findings. `SetStationAutoWashState(int,bool)` provides a change/report path; `GetStationAutoWashState(AvaJson&,AvaJson&)` provides a getter for a stored integer. Compiled support does not demonstrate a supported public property, live values, or compatibility with `4:61`.
2. Separate AVA pipeline: `node_signal.so` defines typed `AI_MOP_DIRTY_INFO` publishing and `node_lethe.so` corresponding handlers; `node_camera_ai.so` defines stain-classification handlers. These are separate private message paths, **not demonstrated MIOT properties**.
3. Existing **device-confirmed** `4:50` values are setting snapshots only; `SmartHost=0`, `SmartAutoMop=-1` (unknown, not “off”), `SmartAutoWash=0`, `StainIdentify=1`, `HotWash=1`. The running `master` fork already exposes these through a cached read-only endpoint, with experimental controls disabled.

## Stage 20 deliverable

A separate Mac-side `x40-stage20-offline-siid.zip` kit was generated containing `stage20_offline_siid.py`, a README and test notes. The user-facing artifact is independent of any firmware or on-robot deployment and is not embedded as a raw proprietary output in Git.

The Python analyzer reads **only** a privately stored, local AArch64 ELF `node_msg_cvt.so`. It uses local `llvm-readelf`/GNU readelf, `c++filt`/llvm-cxxfilt, and `llvm-objdump --disassemble-symbols=<exact mangled symbol>` without `--demangle`. It explicitly verifies that a disassembly header and instructions exist (the LLVM 17 false-zero diagnostic previously identified in Stage 9), tracks only these function families:

- `MsgClean::RptStationAutoWashState`
- `MsgClean::GetStationAutoWashState`
- `MsgClean::SetStationAutoWashState`
- `MsgClean::MsgClean` constructor

It exports **only** an allowlisted JSON summary with bounded member-offset hints and instruction counts. No full disassembly, raw proprietary symbols, paths, runtime values, vendor property payloads, camera imagery, maps or credentials leave the local machine. Tool failures are explicit, rather than interpreted as absence of calls.

### Test evidence

- Standalone parser synthetic tests: **PASS** (symbol matching, exact disassembly header, literal PIID 61 and bounded offset counting, invalid-disassembly rejection).
- An intentionally synthetic **AArch64** C++ shared library was built using clang++ and lld and successfully analyzed: all four function categories were recovered; the synthetic reporter's literal PIID 61 was detected. It is *not* the Dreame firmware.
- Python compilation and generated ZIP integrity: **PASS**.
- **No R2416 firmware has been analyzed in this new Stage 20 run** because the user-local native ELF/archive is not available in the active working directory/session.

### Next gates

1. Owner runs `python3 stage20_offline_siid.py --self-test`, then the offline analyzer on their saved private `node_msg_cvt.so`; share **only** `x40-stage20-sanitized.json`.
2. If the reporter's caller/constructor path can be established through private, verified static analysis, derive the *actual* SIID from the instance initializer rather than guessing an `SIID` from a memory operand or assigning `4:61` from similarity to `4:50`.
3. Only after identity verification can naturally emitted candidate notifications be evaluated for harmless, high-level presence. Stage 19's passive `piid=61` observer is still an **unmerged, undeployed research-only prototype**.
4. Do not enable experimental SmartHost/SmartAutoWash writes, emit AVA messages, add unreviewed MIOT polling ranges, or alter the running `/data/valetudo` installation. Physical cleaning/docking validation is explicitly deferred by the owner.

The companion Stage 19 branch doc remains [Stage 19 passive MIOT candidate research](X40_STAGE19_PASSIVE_MIOT61_RESEARCH.md). No firmware, private measurements, or sensor values have been committed.
