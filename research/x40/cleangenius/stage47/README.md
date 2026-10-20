# X40 Stage47: fixed-path read-only native collector

This source is retained **only** on the unmerged CleanGenius research branch. It reads exactly one existing vendor-native ELF from the rooted X40. It contains no write operations or commands to start washing and never reads device tokens or maps.

The shell collector can be executed without installing anything on the vacuum:

```sh
ssh -T root@<vacuum-ip> 'sh -s -- --emit' < stage47_on_vacuum.sh > ./x40-stage47-PRIVATE-native.tar
```

**PRIVATE:** The tar command above creates a proprietary vendor binary on your local machine; do not upload or commit that tar. Prefer the complete Mac-side automated research kit `x40-stage47-vacuum-readonly-collector.zip`, which validates the tar's single-file membership, SHA-256 pin and ELF identity, executes the Stage46 analyzer, and removes its temporary copies. Its Mac-side Python runner is distributed in the research kit, **not included in this Git commit**.

The source-only `stage47_on_vacuum.sh` supports `--self-test` (local checks only) and `--emit`. It streams only `/usr/lib/tree_lib/liblethe_tactics_tree.so`, with a file-size ceiling, to stdout. No robot file is created.

The operator's real `x40-stage47-sanitized.json` is included for reproducibility. Its result proves collection and narrowly scoped register-analysis counts **but not** actual `open`/`close` payload delivery, callback identity, a physical actuator action or a semantic mapping for MIOT 4:61. More sophisticated register/stack alias and callback-target analysis is still needed. No experimental CleanGenius controls, fork deployment, firmware writes or physical wash/dock tests are authorized by this artifact.
