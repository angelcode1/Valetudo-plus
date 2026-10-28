# Dreame X40 R2416 — v141 direct route Blackboard field store census

**25 October 2026 · SHA-pinned offline original native AArch64 evidence; no robot changes.**

## Uploaded evidence correction

The operator's latest `X40-R2416-v126-model-class-evidence-20261024T145427Z.zip` is a valid sanitized archive, but its `MODEL=absent` and `DEV_MODEL=absent` classifications are **not native-model evidence**: the v126 collector parsed line-based assignments, whereas the original `ReadModleInfo()` parses JSON. The correctly parsed, owner-sanitized v127 result was `MODEL=other_vendor_model` and `DEV_MODEL=absent`. v128 identified native compiled model comparison `site_0x473540`, and the model-specific bound already incorporated in v140 is **ten** possible direct flag writers. The newly uploaded v126 ZIP does **not** increase or otherwise revise that bound.

## Bounded new native audit

v140 established source-pinned argument loads from `AvaNodeRoute` field `+0x30` at the original `ProcessModelInfo()` call and four subsequent `BT::buildTreeFromText()` calls. It deliberately did not exclude field replacement between those calls.

v141 scans the original `node_lethe.so` native route constructor corridor **`0x352304` through `0x3554e8` inclusive**, or **3,194 original 32-bit ARM64 instruction words**. A Python-stdlib verifier classifies LDR X unsigned-offset instructions and bounded direct GPR STR/STRB/STRH, STUR/indexed STR, and STP immediate-offset forms with potential writes overlapping **relative offset `+0x30..+0x37`** from any register base.

- **101** `LDR X` instructions with any register as base at offset `+0x30`, including **98** with `x0` as base and three with another base.
- **227** direct GPR immediate-offset store instructions decoded across the corridor in the audited forms.
- **Zero** of these stores has an immediate effective offset overlapping `+0x30..+0x37` relative to *its own base register*.
- **19** independent checks pass: eight original in-memory LDR-to-STR native instruction substitutions, eight synthetic positive decoder cases and three negative cases. The original ten ELF SHA-256 source pins, v140 source-anchored field handoff and ten-writer regression also passed.

**Precise scope:** zero *syntactically overlapping base-plus-immediate* stores **does not prove the route field cannot change**. These base registers are not proven to designate the route object; register-offset addressing, aliases using different relative offsets, indirect callees, concurrency and XML subtree Blackboard remapping are not excluded. The 101 same-offset loads are not 101 independently proven route-field reads.

No unique executed `SP+0xBC` flag writer, effective native `enable_turbidity` value, model-triggered second physical mop wash, or active StationWash Blackboard instance is established. Ten possible *direct* flag writer sites remain. This result strengthens the direct inlined-store scope only, not live operation.

## Repeatable safe audit

The companion, separately delivered **`X40-R2416-v141-sanitized-route-field-store-census.zip`** (SHA-256 **`111fc7e3ef046ba81e16328e90a51065978ed9b1bc10faf88a84c3d4193c7a09`**) includes the complete Python 3 standard-library `x40_r2416_v141_route_blackboard_direct_store_census_verify.py`, v112–v140 dependencies, technical report, aggregate JSON, README and SHA256SUMS.

Requires the owner's **private** `X40-R2416-v62-readonly-20261023T051829Z.zip` and **sanitized** v128 comparison-site ZIP as local inputs:

```sh
cd ~/Downloads
unzip X40-R2416-v141-sanitized-route-field-store-census.zip
cd x40-v141-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v141_route_blackboard_direct_store_census_verify.py \
  --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
  --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip \
  --self-test
```

Verified:
```text
X40_V141_ORIGINAL_SOURCE_PINS_AND_V140_BLACKBOARD_REGRESSION_PASS
X40_V141_DIRECT_ROUTE_FIELD_LOAD_CENSUS_PASS all=101 x0=98
X40_V141_DIRECT_IMMEDIATE_STORE_OVERLAP_CENSUS_PASS count=0
X40_V141_MUTATIONS_AND_DECODER_TESTS_PASS count=19
LIMIT: no runtime object identity or unique native flag writer proven
```

**Security boundary:** no original ELF, APK, raw MODEL string, config, hardware command, log, map, credential or serial committed. This research commit modifies documentation and sanitized aggregates only. Valetudo+ v74, SmartHost=0, `writeGateOpen=false`, original launcher/recovery and GitHub `master` remain intact.
