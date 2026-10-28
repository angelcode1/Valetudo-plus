# X40 R2416 v134 — offline verifier, privacy and scope

The operator's validated sanitized download is `X40-R2416-v134-sanitized-overlapping-stack-provenance.zip`, SHA-256 `c4ffde39078a192802b8ef3f54191af9e58dc4145a9b94310ef4ae56dd59351e`, containing the Python-standard-library v134 verifier, v112–v133 regression dependencies, report, sanitized JSON, README, and SHA256SUMS.

Use the owner-held `X40-R2416-v62-readonly-20261023T051829Z.zip` and the separately generated sanitized `X40-R2416-v128-model-compare-site-20261024T112745Z.zip` **only as private local inputs**.

```sh
unzip ~/Downloads/X40-R2416-v134-sanitized-overlapping-stack-provenance.zip -d ~/Downloads
cd ~/Downloads/x40-v134-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v134_overlapping_stack_provenance_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261024T112745Z.zip --self-test
```

Checks: ten original SHA-256 ELF pins and v133 model regression; 25 direct STR W sites and one overlapping STR X site at SP+0x98; eight W32 and one X64 possible last-direct source at the later load; six independently pinned shared-block branch entries; 32 original instruction, literal and corridor mutations rejected without using the whole-original-ELF hash as the feature check. Separate turbidity gate writer bound remains ten and is **not** an execution record.

No proprietary binaries, native disassembly, original MODEL, settings, credentials, serials, maps or hardware command values in the archive or public commit. No robot actions, runtime code changes, `master` changes or recovery modifications.
