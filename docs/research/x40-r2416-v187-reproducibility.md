# v187 offline reproducibility

The complete package is X40-R2416-v187-sanitized-cleanbot-entry-app-control-evidence.zip, SHA-256 129411855989633a255ec972849d98b84192318193d2e31cd4b53ba7f66c567d.

Original private liblethe_route_nodes.so SHA-256: fcf706dfa3f4777415d86e95162bf1bbbe3453dcff3126da70946f46c851988e. Not included in commit or ZIP.

Commands:

    cd ~/Downloads
    unzip X40-R2416-v187-sanitized-cleanbot-entry-app-control-evidence.zip
    cd x40-v187-sanitized
    shasum -a 256 -c SHA256SUMS.txt
    python3 -m unittest -v test_x40_r2416_v184.py test_x40_r2416_v185.py test_x40_r2416_v186.py test_x40_r2416_v187.py

For original native replay, export X40_R2416_V184_ROUTE_ELF, X40_R2416_V185_ROUTE_ELF, X40_R2416_V186_ROUTE_ELF, X40_R2416_V187_ROUTE_ELF all pointing to the privately retained exact original ELF and rerun the unit tests. The standalone v187 script also supports --route-elf and --out to create a sanitized JSON without network access.

127 tests passed on original ELF; clean ZIP without ELF 60 passed/25 skipped. User-supplied YouTube video frames were NOT viewable; external Dreame documentation has been kept clearly separate.
