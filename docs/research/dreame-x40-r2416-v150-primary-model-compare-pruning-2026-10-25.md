# X40 R2416 v150 — verified model comparison pruning

Date: 2026-10-25. Offline source research, no device changes.

The newly uploaded sanitized v127/v128 captures identify the primary model using compiled site `0x473540`. The original owner-held v62 archive passes all ten ELF SHA-256 pins.

A real source-backed v147 replay found 118,989 correlated graph states, 35 terminal classes, and ten candidate last-direct model flag writers. A real v148 replay completed 16 branch-edge necessity cuts. v150 pins 19 additional noncanonical primary-model `std::string::compare` sequences. Each uses the primary model in x20 and has an original ADRP/ADD literal pointer, typed comparison call, conditional branch, exact instruction-window hash, and compiled-literal hash. All 19 literals differ from the source-authenticated model; only their impossible equality edges are removed.

**Verified v150 bound:** 52,713 states, 16 terminal classes, and five possible last-direct flag writer PCs: `0x475bc4`, `0x4774d8`, `0x4775a4`, `0x478160`, `0x47826c`. If the separate SP+0x98 value is known zero, only `0x4775a4` survives, but its live value is unobserved.

This result does not assume x26 always retains the secondary model. There is no claim that a specific writer executed, that native turbidity is enabled, or that a second physical mop wash occurred.

The locally tested Python-only verifier rejects 114 independent native instruction/literal mutations, separately from source SHA checks. The complete verifier, v112–v149 dependencies, authentic sanitized v147/v148 replay JSON, source-verified v150 JSON and checksum manifest are available in `X40-R2416-v150-sanitized-primary-model-compare-gate.zip`, SHA-256 `e8c916817101fa1f281d122e920e2ebe5b500df379e3d2ea3caaedb195cc23c5`.

Keep original vendor ELF archives and raw model data private. No runtime or master branch changes.
