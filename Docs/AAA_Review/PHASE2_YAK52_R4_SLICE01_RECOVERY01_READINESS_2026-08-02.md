# Phase 2 Yak-52 R4 Slice 01 Recovery01 readiness

## Result

`BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY01` is offline-ready for a later explicitly authorized Blender invocation.

Status: `PASS_RECOVERY01_READY_NOT_RUN`

No Blender or Unreal process was launched by this recovery work. No `.blend`, GLB, render directory, artifact manifest, import, runtime replacement, promotion, or acceptance was created.

## Preserved failure

The original Slice 01 invocation is preserved exactly:

- stdout: `Saved/Logs/phase2_r4_slice01_blender_20260802T190637Z.stdout.log`
- stderr: `Saved/Logs/phase2_r4_slice01_blender_20260802T190637Z.stderr.log`
- stdout SHA-256: `62aa68d052234759fcf2f662c9277a117896bb0a66d46f104de825c9b1ad1ecc`
- stderr SHA-256: `d4b9e5f04981a9e84007746980b86be1aa0ab080d63243398018c80166ded977`
- exact failure: `KeyError: 'outputs'`
- stage: `ensure_canonical_outputs_absent`, before scene reset or canonical output creation

The frozen Blender source expected:

- `outputs.blend`
- `outputs.glb`
- `outputs.manifest`
- `outputs.comparison_directory`

The frozen Slice 01 contract instead exposed only `output_policy.paths`. Recovery01 corrects the interface mismatch in a new contract rather than altering either frozen file.

## Recovery design

Recovery01:

- reuses the frozen deterministic implementation as code only;
- binds the frozen source, frozen Slice 01 contract, R4 authority, dimension ledger, camera manifest, failure logs, review evidence, and baselines by SHA-256;
- supplies both the exact `outputs.*` alias required by the frozen implementation and the corresponding `output_policy.paths`;
- proves both output representations are identical;
- redirects all outputs to a new `Slice01_Recovery01` namespace;
- keeps the factory-empty scene, no-donor, no-import, no-network, no-overwrite, no-Unreal, and no-promotion boundaries;
- keeps the missing-reference and draft-only truth boundary unchanged.

## Contract-access proof

The offline verifier parses the frozen Blender source with Python AST analysis. It follows direct dictionary access, chained `.get()` calls, and the `authority_inputs[]` loop alias.

All extracted paths must exactly equal the contract’s frozen-access manifest:

1. `build_id`
2. `authority_inputs`
3. `authority_inputs[]`
4. `authority_inputs[].path`
5. `authority_inputs[].bytes`
6. `authority_inputs[].sha256`
7. `authoring_script`
8. `authoring_script.sha256`
9. `outputs`
10. `outputs.blend`
11. `outputs.glb`
12. `outputs.manifest`
13. `outputs.comparison_directory`
14. `claims`
15. `claims.silhouette_locked`

Every path must exist and every authority item must contain its path, byte count, and SHA-256.

## Exact launch wrapper

`Scripts/invoke_phase2_yak52_r4_slice01_recovery01.ps1` is the only contracted production entrypoint.

It:

- refuses to run without `-AuthorizeProduction`;
- refuses to duplicate an active Blender process;
- reruns the offline gate immediately before launch;
- invokes Blender 5.2 with `--background --factory-startup --python`;
- creates a unique immutable attempt directory;
- redirects stdout and stderr directly to attempt-specific files;
- records command, timestamps, PID, exit code, hashes, output presence, and truth-boundary flags in `launch_receipt.json`;
- writes `SHA256SUMS.txt`;
- returns failure if Blender exits nonzero or required draft outputs are missing;
- never launches Unreal or promotes output.

The wrapper has not been executed.

## Verification

- Python compilation: PASS
- Recovery01 offline contract and authority gate: PASS
- Frozen-source contract-access extraction: exact 15-path match
- Mutation tests: 14/14 PASS
- Original failed-attempt outputs: absent
- Recovery01 outputs: absent
- Recovery01 production attempt root: absent
- Blender/Unreal launched by gate: no

## Remaining truth boundary

Even a successful future Recovery01 invocation can produce only `DRAFT_REFERENCE_PACKAGE_MISSING`. The cleared primary Yak-52 reference package remains missing. Silhouette lock still requires cleared and hash-bound references, governed measurement conformance, all five fixed-camera renders, human reference comparison, and explicit separate acceptance.
