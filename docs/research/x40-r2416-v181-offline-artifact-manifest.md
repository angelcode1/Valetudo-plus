# X40 R2416 v181 offline artifact manifest

**Immutable source evidence**: `X40-R2416-v180c-loaded-modules-20261026T085603Z-aee17628-SANITIZED.json`, SHA-256 `a8e5e6bc8df39af518f3523c0818462cd26df7838b95989c24772ab5f444c0f9`.

**Validated kit**: `X40-R2416-v181-sanitized-two-module-native-followup.zip`, SHA-256 `8dc779c778a8d2335d01637d2dd946728fb025a8a52ef6602014358fa7a19290`. The complete runnable Python sources, synthetic tests, README and own SHA256SUMS.txt reside inside the self-contained ZIP delivered separately. No native proprietary ELF bytes are in the kit.

Run on Mac after downloading to `~/Downloads`:

```sh
cd ~/Downloads
unzip X40-R2416-v181-sanitized-two-module-native-followup.zip
cd x40-v181-sanitized
shasum -a 256 -c SHA256SUMS.txt
python3 -m unittest -v test_x40_r2416_v181.py test_x40_r2416_v181_xref.py
python3 x40_r2416_v181_private_two_module_collector.py --ssh root@192.168.8.149 --ssh-auth password --output-dir ~/Downloads
```

The final command makes one **user-authorized read-only SSH** connection, privately copies only `node_laser_transfer.so` and `liblethe_route_nodes.so` from mapped paths, and attempts an offline metadata-only xref report. Private ELF copies must remain local or be explicitly shared privately, and must not be committed.

The ZIP was tested on synthetic fixtures. The two actual candidate ELF files were not available to the assistant for native disassembly during this run. **Subscriber, writer and automatic reclean are not proven.**
