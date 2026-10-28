# X40 R2416 v151 source-checked exact last SP98 source sites

Full tested owner-side kit: `X40-R2416-v151-sanitized-stack-source-site-provenance.zip`; SHA-256 `c73e34f013a3acc00734abb84064aa5297465bc51993a608095bb071e115816f`.

The ZIP contains `x40_r2416_v151_stack_source_site_product_verify.py`, all sanitized v112–v150 Python dependencies, the v151 detailed report, source-checked aggregate JSON, README and SHA256SUMS. It does **not** contain the private original ten-ELF source archive, private MODEL string or robot runtime configuration.

```sh
cd ~/Downloads
unzip X40-R2416-v151-sanitized-stack-source-site-provenance.zip
cd x40-v151-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 x40_r2416_v151_stack_source_site_product_verify.py \
 --owner-private-v62 ~/Downloads/X40-R2416-v62-readonly-20261023T051829Z.zip \
 --v128 ~/Downloads/X40-R2416-v128-model-compare-site-20261025T030544Z.zip \
 --self-test --out ~/Downloads/x40-v151-source-site-evidence.json
```

All source verification was actually run in the assistant environment with recovered original v62 and newly authenticated v128 archives. 10 ELF source pins and the prior v150 five-writer regression passed; 29 local mutation attempts were detected. Native graph: 100,132 states, 30 source-site/writer outcomes, seven SP98 last sources and still five SPBC possible last writers. The entire package was unpacked into a clean directory and replayed, producing byte-for-byte identical sanitized results.

The output is **not** a live instruction trace. No uniquely executed model-gate writer or physical second mop wash is proved. The working robot, its safety gates and GitHub master are untouched.
