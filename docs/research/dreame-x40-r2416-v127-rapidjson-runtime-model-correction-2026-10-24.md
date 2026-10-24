# Dreame X40 R2416 — v127 corrective model-input parser analysis

**24 October 2026. Offline original SHA-256-pinned AArch64 ELF evidence, plus owner-uploaded *sanitized* v126 runtime model-class evidence. No robot actions or private source release.**

## v126 reading is inconclusive: original code expects RapidJSON

The owner uploaded `X40-R2416-v126-model-class-evidence-20261024T103334Z.zip`, which has a valid ZIP CRC and two classifications: `runtime_config_readable=true`, `MODEL=absent`, and `DEV_MODEL=absent`. The **v126 remote AWK was designed for line-oriented `KEY=value`, `KEY:value`, and `KEY value` formats**; thus its `absent` classes are not proof that the native reader could not find these keys.

**v127 independently verifies** the original `node_lethe.so:ReadModleInfo()`'s RapidJSON parsing sequence:

| Original VA | Pinned compiled operation |
|---|---|
| `0x46e8d8` | Native file-stream open using exact `/var/run/runava.conf` path (v126 regression) |
| `0x46ec64`–`0x46ec74` | Prepare native parser/document arguments |
| `0x46ec78` | Direct BL to RapidJSON `GenericReader::ParseValue` PLT `0x2757f0` |
| `0x46ec7c` | Read RapidJSON parser status |
| `0x46ec88` | Direct BL to RapidJSON `SkipWhitespace` PLT `0x279ad0` |
| `0x46ec8c` | Re-read parser status |

The two *separate* `MODEL` and `DEV_MODEL` return-value paths from v126 are retained. These are the compiled input keys, not observed live values. ELF source: original SHA-256 `b34eb5c71bccd90342f34d64a1871197455d69d9511cfa709ee027dd44b554e0`. All ten owner-private original ELFs pass their SHA-256 pins.

**Correction:** treat the v126 report as **readable file / unknown model classifications**. Never prune a positive or zero model-gate branch based on those two ungrounded `absent` results. All thirteen v125 candidate last direct stores remain possible; no *executed* address, effective `enable_turbidity`, or physical second wash is proven.

## Corrected v127 category-only read-only probe

`x40_v127_json_model_class_collector.py` reads **only** `/var/run/runava.conf` over existing root SSH and uses a source-bounded POSIX AWK JSON parser on the device. Only exact top-level `MODEL` and `DEV_MODEL` JSON string fields are classified. It handles nested irrelevant values without exporting them, refuses duplicate keys and malformed syntax, and caps file length (128 KiB) and recursive nesting (32).

Its sanitized ZIP contains exactly two model **classes**, schema, readable/format status, and safety metadata. Only whitelisted classes (`r2416`, `r2416f`, `r2449b`, `r2492x`, `other_vendor_model`, `unrecognized`, `nonstring`, `absent`) and a fixed JSON format status can appear. Exact values not on the allowlist are **never echoed**. Unlike v126, `absent` is emitted only for an actually parsed **valid top-level JSON object** without that literal top-level key; malformed/unsupported input becomes a noncommittal class.

The operator has **not yet run** v127 on the robot. Offline validation passed 13 JSON/format fixtures containing synthetic fake secrets, five malformed remote-output refusals, simulated SSH success and authentication failure, and POSIX shell/awk parsing. Robot actions, config modifications, raw log collection, network calls beyond optional operator SSH, and proprietary binary export: **none**.

## Reproduction

The operator-side **sanitized** download `X40-R2416-v127-sanitized-json-model-correction.zip` (SHA-256 `10c636568673be7638b05380382006127ae3e48cdf15e6a59b265dd8dfdf11c6`) contains both complete Python-standard-library scripts, v112–v126 verifier dependencies, a detailed report, JSON, README and SHA256SUMS. It does not contain the original private firmware ZIP, the readable original config, logs or secrets.

```sh
cd ~/Downloads
unzip X40-R2416-v127-sanitized-json-model-correction.zip
cd x40-v127-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v127_rapidjson_native_reader_verify.py \
  ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --self-test
python3 x40_v127_json_model_class_collector.py --self-test
python3 x40_v127_json_model_class_collector.py \
  --host root@192.168.8.149 --out ~/Downloads
```

Original offline verifier result:

```text
X40_V127_TEN_SHA256_PINNED_ORIGINAL_ELFS_PASS count=10
X40_V127_NATIVE_RAPIDJSON_CONFIG_PARSER_STATIC_PASS sites=2
X40_V127_V126_READER_INPUTS_REGRESSION_PASS two_model_keys=true
X40_V127_V126_LINE_PARSER_ABSENCE_NOT_PROOF_PASS
X40_V127_INDEPENDENT_NATIVE_INSTRUCTION_MUTATIONS_REJECTED count=8
```

Collector self-test passes 13 parser fixtures, five malformed remote response rejections, simulated successful SSH, simulated authentication failure. Eight independent native parser source instruction mutations are rejected without relying solely on the full-file hash.

**Next gate:** read and analyze only the v127 **sanitized** `X40-R2416-v127-json-model-evidence-*.zip`. Actual model classes narrow relevant branch predicates, but do not constitute a runtime instruction trace. Do not request/upload the original `runava.conf` or claim any one writer executed without source-justified constraints.

**Unchanged device:** last verified Valetudo+ v74, `SmartHost=0`, `writeGateOpen=false`, original launcher, backups and rollback binaries intact. Neither repository `master` nor runtime Valetudo code is modified.
