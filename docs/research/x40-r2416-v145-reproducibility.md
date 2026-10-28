# v145 offline reproducibility

The operator's `X40-R2416-v145-sanitized-assembled-opcode-oracle.zip` SHA-256 `18ae0072b8ae6833c8373bbc362c6a36c9a3479867c7f27e91ecd3643a3d68cd` contains the full Python-standard-library v145 verifier and v112–v144 dependencies; 1,857 synthetic opcode/assembly TSV rows; standalone AArch64 assembler replay; report, JSON, and checksums. It has **no vendor ELF, APK, original configuration, maps, keys, tokens or command bytes**.

```sh
unzip ~/Downloads/X40-R2416-v145-sanitized-assembled-opcode-oracle.zip -d ~/Downloads
cd ~/Downloads/x40-v145-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v145_assembled_oracle_and_source_gate_verify.py --self-test
python3 x40_v145_standalone_compiler_oracle_replay.py x40_v145_assembled_opcode_oracle.tsv
```

The clean-extraction test and optional independent Clang/LLVM assembler replay passed for all 1,857 synthetic opcodes. The finite tested corpus yielded 0 semantic mismatches; 133 v144 assertions and 24 altered expectation tests also passed.

From a cloned repository, the checked-in `util/x40_v145_standalone_compiler_oracle_replay.py` can validate the ZIP's synthetic TSV:

```sh
python3 util/x40_v145_standalone_compiler_oracle_replay.py \
 ~/Downloads/x40-v145-sanitized/x40_v145_assembled_opcode_oracle.tsv
```

Run the native source census separately **only with your private original v62 ZIP**:

```sh
cd ~/Downloads/x40-v145-sanitized
python3 x40_r2416_v145_assembled_oracle_and_source_gate_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --self-test --out ~/Downloads/x40-v145-native-store-census.json
```

This command was not executed against vendor firmware here because the source bytes were absent from the container. The script refuses missing source or existing output. **Only share the sanitized result JSON.** The original ten candidate direct model writers, live Blackboard linkage and second physical wash remain unverified.
