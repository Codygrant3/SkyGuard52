Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`.
Do not use the retired Three.js project, external models, or subagents.

Treat every prior Recovery01/02/03 and failed build artifact as immutable.
Treat the Recovery02 supervisor freeze and its SHA-256 as the sole new authority.

Authorize exactly one build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_skyguard_recovery03_native_recovery02_once.ps1`

Before launch, verify every frozen hash, zero heavy processes, and absence of
`D:\SG52R03B03`, the Recovery02 build namespace, and every governed runtime
namespace. Never reuse a failed namespace.

The supervisor must directly launch UE's frozen bundled `dotnet.exe`, with the
frozen `AutomationTool.dll` as its first argument. It must launch once, never
retry, preserve logs/process evidence, and persist a numeric `System.Int32`
exit code plus a terminal manifest on every outcome.

If any preflight, process, build, inventory, source-parity, output, rebinding,
or manifest gate fails, freeze the evidence and classify
`FAILED_WITH_EVIDENCE`.

If the build succeeds, hash-freeze the DLL, PDB, module receipt, package,
rebound binaries, source parity, manifest, logs, and process evidence. Rerun
all offline tests and confirm the plugin remains disabled by default.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY02_UNREAL_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not launch UnrealEditor, Blender, capture, promotion, integration, or
packaging. If passed, produce but do not execute the exact one-shot Unreal
proof prompt. Stop after immutable build classification.
