Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`.
Do not use the retired Three.js project, external models, or subagents.

Treat every prior Recovery01, Recovery02, Recovery03, and failed attempt as
immutable. Treat the Recovery03 offline supervisor freeze and its separately
reported SHA-256 as the sole new authority.

Authorize exactly one native plugin build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_skyguard_recovery03_native_recovery03_once.ps1 -AuthorizeSingleBuild`

Before launch, verify every frozen hash, zero heavy processes, and absence of:

- `D:\SG52R03B04`
- the Recovery03 governed build-attempt namespace;
- the Recovery03 runtime namespace;
- the Recovery03 terminal supervisor manifest;
- the Recovery03 emergency receipt.

Rerun the frozen offline verifier and require `PASS`. Never reuse a failed
namespace and never retry automatically.

The supervisor must directly launch UE's frozen bundled `dotnet.exe`, with the
frozen `AutomationTool.dll` as its first argument. It must launch once, retain
the native process handle, preserve logs and process-tree evidence, and persist
a numeric `System.Int32` exit code plus the external terminal manifest on every
outcome.

If any preflight, process, build, inventory, source-parity, output, rebinding,
or manifest gate fails, preserve and hash all evidence, classify
`FAILED_WITH_EVIDENCE`, and stop without retrying.

If the build succeeds, require and hash the DLL, PDB, module receipt, packaged
plugin, complete source, manifest, logs, process evidence, and rebound
binaries. Verify source parity, attempt provenance, disabled-by-default plugin
state, and every frozen offline test.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY03_UNREAL_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not launch UnrealEditor, Blender, capture, promotion, integration, gameplay,
profiling, or packaging. If passed, create but do not execute the exact
one-shot Unreal proof prompt. Stop after immutable build classification.
