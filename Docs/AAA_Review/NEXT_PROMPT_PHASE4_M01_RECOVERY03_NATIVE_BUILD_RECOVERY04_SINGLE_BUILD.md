Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`.
Do not use the retired Three.js project, external models, or subagents.

Treat every prior Recovery01–03 artifact and failed namespace as immutable.
Treat the Recovery04 offline source-correction freeze and its separately
reported SHA-256 as the sole new authority.

Authorize exactly one native plugin build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_skyguard_recovery03_native_recovery04_once.ps1 -AuthorizeSingleBuild`

Before launch, verify every frozen hash, rerun the Recovery04 offline verifier,
require zero heavy processes, and confirm absence of:

- `D:\SG52R03B05`;
- the Recovery04 build-attempt namespace;
- the Recovery04 runtime namespace;
- the Recovery04 terminal supervisor manifest;
- the Recovery04 emergency receipt.

Never retry automatically and never reuse a failed namespace.

The supervisor must directly launch the frozen bundled `.NET 10` host with
`AutomationTool.dll` as its first argument, target the frozen Recovery04
descriptor, package only to `D:\SG52R03B05`, preserve process and compiler
evidence, and write its external terminal manifest on every outcome.

If any preflight, process, compilation, inventory, source-parity, output,
rebinding, or manifest gate fails, preserve and hash all evidence, classify
`FAILED_WITH_EVIDENCE`, and stop without retrying.

If the build succeeds, require and hash the module DLL, PDB, module receipt,
packaged descriptor, complete source, logs, process tree, terminal manifest,
and rebound binaries. Verify source parity, single-attempt provenance,
disabled-by-default plugin state, and every frozen offline test.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY04_UNREAL_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not launch UnrealEditor, Blender, capture, gameplay, profiling, promotion,
integration, or game packaging. If passed, create but do not execute the exact
one-shot Unreal proof prompt. Stop after immutable build classification.
