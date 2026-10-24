# X40 R2416 v135b — conservative replay

The owner-side sanitized ZIP `X40-R2416-v135-sanitized-correlated-stack-state.zip` has verified SHA-256 `4d26106003da13242207d2fb6d7a27eae52ad4a084f9bde0eecbebcd02bb6176`, CRC integrity, complete SHA256SUMS pass and fresh-extraction self-test pass. The ZIP contains `x40_r2416_v135_joint_stack_last_writer_verify.py`, v112–v134 Python regression dependencies, technical report, aggregate JSON, README and checksums. It contains no original ELF binaries, native disassembly, raw model string or configuration.

Read-only local input archives required:

* `~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip` — ten SHA-pinned private original ELF files
* `~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip` — privacy-preserving exact compiled model-site identity

```sh
unzip ~/Downloads/X40-R2416-v135-sanitized-correlated-stack-state.zip -d ~/Downloads
cd ~/Downloads/x40-v135-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v135_joint_stack_last_writer_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Expected: 118,989 abstract node states, 35 terminal combinations, five possible flag stores under known-zero SP98 source class, ten possible writers overall, 20 SP100 zero consumer combinations, 15 combinations not traversing SP100 consumer, 27 original native instruction mutations rejected, six synthetic state-product tests. All sources are original SHA-pinned code; no robot access or actual instruction execution is demonstrated.

This is a conservative **addendum** to the existing v135 docs, not a replacement. `master`, original firmware/device and Valetudo runtime remain unchanged.
