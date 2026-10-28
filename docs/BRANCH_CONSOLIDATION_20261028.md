# Branch consolidation and research preservation — 2026-10-28

## Completed cleanup and verified result — 2026-10-28

- **Only branch remaining:** `master`. GitHub branches endpoint returned precisely one ref after [successful one-time prune job 40656864797](https://github.com/angelcode1/Valetudo-plus/actions/runs/40656864797).
- **90 stale branch refs deleted** with exact SHA verification and lease-based pushes. All 89 non-default tip commits captured before consolidation were verified as parent ancestry, in addition to the canonical feature branch's first-parent lineage.
- **172 research documents/tools recovered into HEAD**, plus legacy code preserved in reachable history; no force-push and no upstream reset.
- **Workflows:** four retained on master (Node.js CI, CodeQL, Manual Build, Release). The four outdated housekeeping workflows were removed; the temporary prune workflow and trigger were also removed after completing the cleanup.
- **PR #2:** closed as superseded, without indicating SmartHost acceptance or production rollout. The installed X40 Valetudo remains untouched.
- **Workflow validation:** the consolidated code passed [run 40656404002](https://github.com/angelcode1/Valetudo-plus/actions/runs/40656404002), and the final repository HEAD `177aa2526a0144f584475862fe8f087012e68d75` passed [full Node.js CI run 40657258670](https://github.com/angelcode1/Valetudo-plus/actions/runs/40657258670). Documentation-only amendments after that do not change runtime logic.

## Canonical branch
`master` is the **only supported source-of-truth branch**. The original implementation basis is the passing guarded X40 feature commit `942e3175a2ac26138cf90f6a852eb93444c6f9ff` and its verified documentation state `661fd0184e728edc80d42d40e856c3e5f32e4dea`. The X40's installed `/data/valetudo` remains unchanged and was last owner-confirmed running as PID 1752 with watchdog not running.

This consolidation brings in previously branch-only **sanitized historical research** while preserving the latest CI-tested guarded code. Incompatible legacy experimental backend code and abandoned standalone test helpers are not reactivated; they remain accessible via merged Git history and the exact pre-cleanup commit hashes below.

**Caveat:** CI proves compilation/tests, **not** physical SmartHost acceptance, actual reclean or dock rewash. Keep `VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS=0` by default; do not run another hardware trial merely because branches were consolidated.

## Research archive
- The consolidated master branch's verified guarded runtime and X40 handoff remain authoritative; the extra research docs/scripts are archival, not implementation requirements.
- Missing `v70–v151` sanitized research reports and checks from the independent `v117` lineage are included as documentation.
- Missing `v233–v237` sanitized reports and checkers are added from the later `v237` lineage.
- Previous `stage9`, passive MIOT61, and the alternate v82 research checkpoint are preserved.
- Every pre-cleanup branch tip is incorporated as a *merge parent* of the canonical history. Thus `git show <sha>:<path>` and `git log` can still recover a former branch's original files even if that variant's code is not active at HEAD. This is an intentional **history-preserving ours-style consolidation**, not a claim that all divergent experimental implementations have been merged into the live application.

## CI / workflow policy
Keep: `.github/workflows/nodejs.yml`, `.github/workflows/manual_build.yml`, `.github/workflows/release.yml`, `.github/workflows/codeql-analysis.yml`.
Remove obsolete: `.github/workflows/close_threads.yml`, `.github/workflows/lock_threads.yml`, `.github/workflows/request.yml`, `.github/workflows/loc.yml`.
The Node.js CI artifact condition targets pushes to `master`. This does not authorize deploying it to a robot.

## Complete pre-cleanup branch ref inventory (91 refs, including master)
These hashes are recorded to detect accidental data loss or unexpected branch movement. Any cleanup must verify the exact old tip is reachable before deleting its ref.

| Branch | Captured SHA |
|---|---|
| `diagnostics/x40-stage9-parent-fork-ab` | `190aae591d90daa944eecce66bc0cd6fc1376829` |
| `feature/x40-cleangenius-research` | `5be3c3e53c3cb25e8408d23776200c57ddaa5353` |
| `feature/x40-cleangenius-supervised-activation-20261028` | `661fd0184e728edc80d42d40e856c3e5f32e4dea` |
| `master` | `7b49cf63356e57c5a493914e452752caef815f04` |
| `research/x40-cleangenius-passive-miot61` | `7b81b12f637048229a957cd6e1ae11b3f1f05afc` |
| `research/x40-cleangenius-v70-passive-observer-20261023` | `f20851b577c128f6ebd0f3fd8443fa82aad5a270` |
| `research/x40-cleangenius-v73-single-key-gate-20261023` | `8384b9a218c420d9f7f7ba0c8024cf1d232a8451` |
| `research/x40-cleangenius-v74-dock-error-observer-20261023` | `24200089fc187a588af66528bedd9782a7f1e70b` |
| `research/x40-cleangenius-v75-native-bb-gates-20261024` | `a8d1d5057e3b3460a2796c0946b982da7cf7a39d` |
| `research/x40-cleangenius-v76-native-switch-ingress-20261024` | `78dd52a6dc20d5da31616589976477ca13bd5c2e` |
| `research/x40-cleangenius-v77-smartwash-enum-boundary-20261024` | `f66928e3c78b320f4efa997d60fbb36c64d3e9b9` |
| `research/x40-cleangenius-v78-miot-4-50-string-20261024` | `8360ad7c41f5aa615e544d23895a730a766caede` |
| `research/x40-cleangenius-v79-state-to-logic-subscriber-20261024` | `4538b0c3312e60474522c98f9dd9c263f6bc4a36` |
| `research/x40-cleangenius-v80-kv-receiver-boundary-20261024` | `6251633c9a3b0cde112819b86ddaf6cd63619270` |
| `research/x40-cleangenius-v81-app-status-blackboard-20261024` | `3f39fe0173e249b569876a6c9e7eabbde4483867` |
| `research/x40-cleangenius-v82-model-special-key-20261024` | `5d1e43792cbe7363a06945dff7b846cd937badfb` |
| `research/x40-cleangenius-v82-shared-root-blackboard-20261024` | `ba656a7437ba35e54d44fa77f5a03cee368c1752` |
| `research/x40-cleangenius-v83-special-key-audit-20261024` | `5af7d8c077f7a5771639c1ba45d44ab4e3b91092` |
| `research/x40-cleangenius-v84-stationwash-root-20261024` | `8b09bd9a73391dca620bc899e0abcb284f2172b6` |
| `research/x40-cleangenius-v85-stationwash-path-context-20261024` | `54f15cdfb671e05909661ac02efe6f914297a08d` |
| `research/x40-cleangenius-v86-scoped-data-xml-20261024` | `d6cf500d24f793033e8d18bddf629209f27092b0` |
| `research/x40-cleangenius-v87-native-process-root-20261024` | `fccbbf7344545364911b12ce88016ee32541a4f9` |
| `research/x40-cleangenius-v88-native-resource-layout-20261024` | `e385b3850b3dab05a8ac151b842f3440c205f287` |
| `research/x40-cleangenius-v89-station-control-boundary-20261024` | `210504a2974d7cdc1e73cdc867193402bb57e54e` |
| `research/x40-cleangenius-v90-station-set-typed-bridge-20261024` | `b5c3fbc648baf09bb92b5500e5c4644a57a33bd8` |
| `research/x40-cleangenius-v91-station-ui-publisher-20261024` | `b5a42a27d514b4dd35bfa920c0860ede870f91e1` |
| `research/x40-cleangenius-v92-output-order-washcontrol-20261024` | `dcc80340da62a6a27c6740efdda91ef0c6b19f4e` |
| `research/x40-cleangenius-v93-wash-control-callback-20261024` | `ba7d804baa8850e7ef986f79bc18e46ad0618778` |
| `research/x40-cleangenius-v94-control-machine-state-20261024` | `ce4dfa2e02e618238fc634731f8ad89f92d20475` |
| `research/x40-cleangenius-v95-compiled-stationwash-builder-20261024` | `6caf406f7471c48a3869996209c7c9ac7ba9651d` |
| `research/x40-cleangenius-v96-stationwash-helper-reachability-20261024` | `910dd9bedb51ef6ec18c2c5d1e01a76816238370` |
| `research/x40-cleangenius-v97-native-stationwash-resolution-20261024` | `a102e29d76f54506813c264fe7920f3ca8be9db5` |
| `research/x40-cleangenius-v98-native-plugin-factory-20261024` | `6532a5cad7db5a5722d2a94dfe0c3dca79279aa3` |
| `research/x40-cleangenius-v99-two-level-native-root-20261024` | `91e1f0c0a60a648274b1ba8d915c545fcec83543` |
| `research/x40-cleangenius-v100-extensionless-root-opt-20261024` | `1482a3d5913f14d065816ef7000c94d0bb059cc9` |
| `research/x40-cleangenius-v117-native-key-provenance-20261024` | `057f9808c2622c014377e5a3177553cb90470798` |
| `research/x40-cleangenius-v177-stain-id-async-int-20261026` | `3b672eab559833e926d0be02a5ceddcc81b7f638` |
| `research/x40-cleangenius-v181-cross-module-leads-20261026` | `86063f3b9b551aeed9af104714b33d58f25c3134` |
| `research/x40-cleangenius-v182-stain-writer-subscriber-20261026` | `5c6bc16b42964566d10c18b302779c062d717136` |
| `research/x40-cleangenius-v183-perception-object-link-20261026` | `8cbd58eb2a67b0c21433dce026de6da6bfb46c97` |
| `research/x40-cleangenius-v184-extra-clean-planner-20261026` | `c03cd2658b54b312dadfefab3a90a4640c1d4261` |
| `research/x40-cleangenius-v185-stain-extra-planner-20261026` | `2819990593eb0fb0d63c24fce87b86ad0cb52b8c` |
| `research/x40-cleangenius-v186-cleanlist-preprocess-20261026` | `5e6c25ef33b21b9d1466fd305bb91c42b97a8200` |
| `research/x40-cleangenius-v187-cleanbot-entry-app-evidence-20261026` | `1af4459dd114def9d6930c57ffedd8fa2c4d355e` |
| `research/x40-cleangenius-v188-extra-type-x50-ui-20261026` | `24e8e60778723f3365c079086559d3ded373dbc4` |
| `research/x40-cleangenius-v189-task-end-guard-20261026` | `1a0a6f14b202e6316dca5e27e1168de4da6dc7b7` |
| `research/x40-cleangenius-v190-extra-clean-key-roles-20261026` | `3307eb6131381b9efa22658ae5de74f039acbfb7` |
| `research/x40-cleangenius-v191-next-dynamic-area-guard-20261026` | `001f536a3863e5097c6a726f99d044fced68827f` |
| `research/x40-cleangenius-v192-dynamic-point-handoff-20261026` | `83dce42d8e0359a08c0aaffaad27f9f731385314` |
| `research/x40-cleangenius-v193-point-consumers-20261026` | `9ef358ce0abe45c10070fce785caf439ee31ee26` |
| `research/x40-cleangenius-v194-external-bt-xml-20261026` | `d70dbe89798ac1d06e202ddbfc036db923ebadf6` |
| `research/x40-cleangenius-v195-native-robotnode-20261026` | `c09a76b73b3d584ffaf2192009bf39746223229e` |
| `research/x40-cleangenius-v197-turbidity-blackboard-20261026` | `763023e63f621f72fd85556789f6933f99906e47` |
| `research/x40-cleangenius-v198-a-table-fallback-20261026` | `656468d36a0af634b483d2558b1e8cf3226bd731` |
| `research/x40-cleangenius-v199-a-subtype-index-20261027` | `92bd665ff934f9bca0fa2be9a34f032052072ef2` |
| `research/x40-cleangenius-v200-json-series-order-20261027` | `7953e47212a7cdec2e0136d8e1cd72d102b7ceaa` |
| `research/x40-cleangenius-v201-station-subtype-producer-20261027` | `39822992531cd44e046364c37dd74c757a0789cd` |
| `research/x40-cleangenius-v202-subtree-blackboard-cache-20261027` | `bd280678f826e3613ce0445fbe6ab703a7947828` |
| `research/x40-cleangenius-v203-static-tree-cache-lifetime-20261027` | `14b5acec13812759347405797fd1fe37864e3668` |
| `research/x40-cleangenius-v204-cache-miss-null-entry-20261027` | `8d4f147b1aba5f30c966d884c3403e41d549d572` |
| `research/x40-cleangenius-v205-reuse-prefix-20261027` | `7f4324432cb90da1e8fd36ad948d7018059247a0` |
| `research/x40-cleangenius-v206-reusetree-aistain-20261027` | `2187516cbe7658026c2af6119e2660dd2fbd81e6` |
| `research/x40-cleangenius-v207-aistain-resolution-20261027` | `9e30d65d81cee8c9cc50f993a39cb8e89e038b72` |
| `research/x40-cleangenius-v208-aistain-file-fallback-20261027` | `a16f8b730aa6079a64cca68f69b55c500315f175` |
| `research/x40-cleangenius-v209-resolver-empty-path-20261027` | `a0d4e17da333c99e38adaffbf0613c5729caaf46` |
| `research/x40-cleangenius-v210-live-resolver-coverage-20261027` | `1d83db5e034afd6b0b8beaeb70da980cdb4d4fc3` |
| `research/x40-cleangenius-v211-live-scope-cwd-20261027` | `a4359dcdf2f0018fa83b35ff59b16bb68cebe166` |
| `research/x40-cleangenius-v212-cwd-branch-20261027` | `103f7880737bfe9259e6b6d69a4b638cbfb495ea` |
| `research/x40-cleangenius-v213-builder-registration-20261027` | `851847e54f18ec182ecde0ce8001d278ea2b82de` |
| `research/x40-cleangenius-v214-plugin-loader-abi-20261027` | `70239ca9fb284b4cdbce3ceaa6946b5c7356c0d9` |
| `research/x40-cleangenius-v215-reuse-placeholder-fallback-20261027` | `6f0b436b631492d5892b437c6a757fd4ec889fb5` |
| `research/x40-cleangenius-v216-reusetree-success-20261027` | `9aa4dc9396e680f7c21a9d5664ebfd6269dd4ab0` |
| `research/x40-cleangenius-v217-stain-cleanlist-20261027` | `aa45021f7935ab3592f4a9df14507bd8103ddb10` |
| `research/x40-cleangenius-v218-cleanlist-consumer-20261027` | `df2f607806150961c8015cc45dbec6eb51d65760` |
| `research/x40-cleangenius-v219-debug-task-stack-20261027` | `f0e9424d2522d3d2f395dc8dbbeb95a612e9d341` |
| `research/x40-cleangenius-v220-production-root-20261027` | `a57c4e1373e10974c99262b99adb7f3234f4e72f` |
| `research/x40-cleangenius-v221-production-AI-handlers-20261027` | `0d7cb4190264d6cc3f5a9ecfe51c3f09ff058ca7` |
| `research/x40-cleangenius-v222-async-callback-20261027` | `b0cbcc31a9174e3917e22e5bf17c451ccec0808f` |
| `research/x40-cleangenius-v223-ai-flag-20261027` | `ed4e1e2537e258d4e8cbea508cdb1430e4e37d1d` |
| `research/x40-cleangenius-v224-dirty-mop-consumer-20261027` | `a297446e313c7159e3a4dd0645e092906520c4fa` |
| `research/x40-cleangenius-v225-mcu-numeric-guards-20261027` | `25cc2aa09c5f2d7a760b6755b1eca03e86a9fc68` |
| `research/x40-cleangenius-v226-mcu-publisher-responder-20261027` | `c8ce93ffb401c1fbb92982ebdb20be3fb3bb6a76` |
| `research/x40-cleangenius-v227-station-sampling-20261027` | `669b347ee735b5ac88e4fd345f302b0e18857199` |
| `research/x40-cleangenius-v228-switch-sensor-20261027` | `c4ea273517e0d9ef36ad21d9c8f0be2b9e225add` |
| `research/x40-cleangenius-v229-sensor-retention-20261027` | `1f2b9957128332ad7ccfd7528a844953c717ce85` |
| `research/x40-cleangenius-v230-two-sensor-consumers-20261027` | `4495cd7e097800793715a11be17f530204c467e4` |
| `research/x40-cleangenius-v233-health-sensors-subscription-20261027` | `41609dc5cdcae79d0999b91b5dcd72bd91749925` |
| `research/x40-cleangenius-v234-ava-topic-contract-20261027` | `9306bf93104fc59e01de732cdcb596943c772b8e` |
| `research/x40-cleangenius-v235-health-topic-census-20261027` | `49472799a7f852dbc7db56e7c2e6e704cfe41cae` |
| `research/x40-cleangenius-v236-route-health-typed-interface-20261027` | `49fa743d4bb9f54d84a2d2ea0ff0d779bd632f73` |
| `research/x40-cleangenius-v237-route-health-retained-reset-20261027` | `ac2581bba7948688d3c60849ff66b6dfd7de1d77` |

## Review / safety
- Open PR #2 is superseded after its full tested feature tree enters `master`, not evidence of hardware acceptance.
- Old branch refs may only be pruned **after** the consolidated HEAD passes CI and every captured ref is ancestor-reachable.
- No force push, no hard reset, no robot installation and no change to third-party upstream branches.
