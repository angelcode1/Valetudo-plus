# X40 R2416 v132 — reproducibility record

The complete Python 3 standard-library-only offline verifier and sanitized v112–v131 regression dependencies are in the owner-side `X40-R2416-v132-sanitized-complete-native-regex-census.zip` (**SHA-256 `30604c805c52188572009103f5c03ab0ad60855f4cde7e923bf932c0d1e07aa3`**). ZIP CRC/integrity, every SHA256SUMS entry, and a separate fresh unzip plus full verifier self-test have passed.

The user privately supplies the unmodified ten-ELF source `X40-R2416-v62-readonly-20261023T051829Z.zip` and previously produced sanitized native model-site `X40-R2416-v128-model-compare-site-20261024T112745Z.zip`:

```sh
unzip ~/Downloads/X40-R2416-v132-sanitized-complete-native-regex-census.zip -d ~/Downloads
cd ~/Downloads/x40-v132-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v132_complete_regex_inventory_verify.py --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Checked: all ten SHA-256 original ELF pins, all 31 native typed regex-match calls accounted for, four additional source-bounded nonmatches including one compiled through the lower-level compiler, 12→11 possible direct writers by excluding `0x4703fc`, 37 independent mutated source instructions/literal bytes rejected without relying only on original full-file hash checks.

**No original binary, native disassembly, raw MODEL string, private runtime configuration, map, serial, token or hardware command value is published in this commit.** Research-only report and aggregate JSON are committed. Static possible paths are not an execution trace, active turbidity state or evidence of second physical wash. Existing Valetudo+ v74 safety gates, original launcher/recovery state, runtime code and `master` remain unchanged.
