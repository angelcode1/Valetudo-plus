# X40 R2416 v118 — sanitized reproducibility

This commit documents the new native model/turbidity gate boundary. The Python-standard-library offline verifier and its v112–v117 imported dependencies are delivered in the **owner-available** sanitized `X40-R2416-v118-sanitized-model-eligibility.zip`; the original firmware ZIP is neither included nor published.

Run the zipped `x40_r2416_v118_model_turbidity_flag_verify.py` against the owner's **private** `X40-R2416-v62-readonly-20261023T051829Z.zip` with `--self-test`. It validates 10 SHA-256 pins, the v117 regression and 44 independently altered native instructions/literals. The package also contains SHA256SUMS, a detailed report and sanitized metadata.

This commit changes **documentation and JSON only**. The repo's executable Valetudo code, the user device, the native switch settings, the original launcher and all restore artifacts are untouched. The exact R2416 branch does not itself establish `enable_turbidity` eligibility. Do not publish vendor ELFs, credentials, private settings or native station-command parameters.

Next: precise symbolic model-group reachability across all relevant stack-flag stores.
