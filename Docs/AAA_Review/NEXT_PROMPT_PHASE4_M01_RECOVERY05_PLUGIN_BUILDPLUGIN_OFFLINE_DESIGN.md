Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every prior Gate 2, Recovery01–04, migration-design, and Migration01 execution artifact as immutable.

Treat the accepted Migration01 terminal freeze as the sole new authority:

`D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_FREEZE.json`

Required classification:

`PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`

## Authorization

Perform exactly one offline-only Recovery05 `BuildPlugin` design gate.

Do not launch AutomationTool, UnrealBuildTool, UnrealEditor, Blender, ShaderCompileWorker, dotnet, compiler, linker, BuildPlugin, capture, profiling, gameplay, integration, promotion, or packaging.

Do not move, copy, modify, enable, disable, rename, overwrite, merge, or delete any plugin.

Do not modify project Source, Config, `.uproject`, accepted build outputs, quarantine evidence, or any frozen artifact.

## Objective

Design and freeze one deterministic, one-shot `BuildPlugin` supervisor for:

`D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.uplugin`

Use a fresh short package root:

`D:\SG52R05P01`

Do not create that package root during this offline gate.

## Preflight

1. Verify the Migration01 terminal freeze and every member.
2. Verify all five active Recovery05 plugin files and all 18 quarantined files.
3. Verify the active plugin-discovery set contains only:
   `SkyguardRecovery03NativeRecovery05`.
4. Verify its descriptor remains disabled by default.
5. Verify its module and ModuleRules identity are uniquely:
   `SkyguardRecovery03NativeRecovery05`.
6. Verify the accepted Recovery04 project-build freeze and isolated binaries remain unchanged.
7. Confirm no heavy process is active.
8. Confirm future BuildPlugin package, attempt, terminal, emergency, and runtime namespaces are absent.

If any authority differs, classify `FAILED_WITH_EVIDENCE` and stop.

## Future exact build

The future supervisor must launch exactly:

Executable:

`D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`

First argument:

`D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll`

Remaining arguments:

- `BuildPlugin`
- `-Plugin=D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.uplugin`
- `-Package=D:\SG52R05P01`
- `-TargetPlatforms=Win64`
- `-Rocket`
- `-StrictIncludes`
- `-NoP4`

Do not use:

- `AutomationTool.exe`;
- `RunUAT.bat`;
- `cmd.exe`;
- system dotnet;
- a shell association;
- another executable wrapper.

## Supervisor requirements

The future supervisor must:

1. Verify every frozen authority and source hash before namespace creation.
2. Confirm only Recovery05 remains beneath `Plugins`.
3. Confirm no heavy process is active.
4. Confirm every future namespace is absent.
5. Create one fresh attempt namespace.
6. Launch bundled dotnet exactly once.
7. Retain the exact process object and native handle.
8. Redirect stdout and stderr into immutable attempt files.
9. Persist process-tree samples.
10. Preserve numeric exit code and `System.Int32` type.
11. Never coerce null into zero.
12. Never infer exit status from logs.
13. Never retry.
14. Never reuse a failed namespace.
15. Persist a terminal manifest on every outcome.
16. Persist a minimal emergency receipt if normal terminal writing fails.
17. Never copy package outputs back into the active project.
18. Never launch UnrealEditor.

## Successful-build requirements

Require:

- numeric `System.Int32` exit code `0`;
- packaged Recovery05 editor DLL;
- PDB;
- module receipt;
- packaged descriptor;
- Build.cs;
- complete packaged source;
- exact source parity;
- complete package inventory;
- compiler and linker evidence;
- one launch and zero retries;
- plugin disabled by default;
- no legacy plugin reintroduced into active discovery;
- no mutation of active or quarantined source.

## Offline tests

Add `-OfflineContractTest`.

Under Windows PowerShell 5.1 require:

- parser errors `0`;
- numeric `System.Int32` exit code `0`;
- frozen hash checks pass;
- exact argument-array checks pass;
- terminal JSON serialization succeeds;
- missing-file, mismatched-hash, null-code, and nonnumeric-code rejection pass;
- package and attempt namespaces remain absent;
- zero dotnet, AutomationTool, UBT, Unreal, Blender, compiler, or linker launches.

## Required artifacts

Create:

- terminal-evidence reconciliation;
- Recovery05 source and active-discovery inventory;
- BuildPlugin contract;
- one-shot BuildPlugin supervisor;
- offline verifier;
- projected-path report;
- exact-host offline-test result;
- readiness record;
- immutable offline-design freeze;
- exact separate prompt for one future Recovery05 BuildPlugin execution.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY05_BUILDPLUGIN_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not execute BuildPlugin during this gate.

Do not launch Unreal or create a runtime-binding proof.

Stop after immutable offline classification and, only if passed, creation of the separate one-shot BuildPlugin prompt.
