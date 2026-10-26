# Reproduce v183 native stain-perception links
Source binary SHA-256 hashes are pinned in the accompanying JSON and Python source.
The complete **48-test** verifier and sanitized reporting kit is a separate, self-contained offline release named `X40-R2416-v183-sanitized-stain-perception-object-link.zip`, SHA-256 `302185d902c82ddfad8ad99eaf6920d5e0ac16d3dba2bf1957cbc6e4889cbc2d`; it is *not* a part of this GitHub commit. No proprietary ELFs are distributed.

This branch includes an additional compact offline instruction/hash/BL checker and five stdlib unit tests:
```sh
cd docs/research/x40-r2416-v183-tools
python3 -m unittest -v test_verify_v183_object_link.py
python3 verify_v183_object_link.py --laser-elf /private/path/node_laser_transfer.so --route-elf /private/path/liblethe_route_nodes.so
```
The ZIP's complete v182/v183 tests, independently checked against the original private ELFs, report 48 pass; without the ELFs 19 pass and 29 skip. Neither the compact checker nor the full ZIP proves real-world extra cleaning. No device operations are performed.
