Resume only the existing Unreal Engine 5.8/Blender AAA project at
`D:\Skyguard52`. Do not use the retired Three.js project, external models, or
subagents.

Treat Gate 2 Attempt 01 as immutable and terminal:

- terminal freeze:
  `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json`;
- SHA-256:
  `95c485434f0b6cb0fe023c23ad628a6a87c338f9019521ca1730055335479fb5`;
- classification:
  `FAILED_WITH_EVIDENCE`;
- retries:
  `0`.

Treat the current Recovery02 offline-design freeze and every file recorded
inside it as immutable authority. Verify its current byte count, SHA-256, every
member hash, and its classification before acting:

`PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_AUTHORIZATION`

## Authorization

Authorize exactly one isolated Recovery02 native project build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery02_once.ps1 -AuthorizeSingleBuild`

Do not launch UnrealEditor, Blender, AutomationTool, capture, profiling,
integration, promotion, Recovery05 plugin packaging, or game packaging.

Do not invoke Luna, Terra, Grok, Sol, or Opus 5.

## Recovery architecture

The supervisor must create one fresh isolated native-build view at:

`D:\SG52M01R02`

It must copy exactly the 170 records in:

`D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json`

The view includes:

- exact `Skyguard52.uproject`;
- exact `Source`;
- exact `Config`;
- unique `SkyguardRecovery03` descriptor and source;
- unique `SkyguardRecovery03NativeRecovery05` descriptor and source.

The view must not include:

- `SkyguardRecovery03NativeRecovery01`;
- `SkyguardRecovery03NativeRecovery04`;
- Content;
- existing Binaries;
- Intermediate;
- Saved;
- DerivedDataCache.

The exclusions apply only to the fresh build view. Do not modify, move, rename,
delete, mask, or repair the immutable source-project plugin directories.

## Preflight

Before creating any future namespace:

1. Verify every hash and byte count in the Recovery02 offline freeze.
2. Verify Gate 2 Attempt 01 remains unchanged.
3. Verify all 170 parity records against `D:\Skyguard52`.
4. Verify the environment source remains:
   - bytes: `15032`;
   - SHA-256:
     `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.
5. Verify bundled .NET and UnrealBuildTool:
   - `D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`;
   - `D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`.
6. Confirm no Unreal, Blender, ShaderCompileWorker, AutomationTool,
   UnrealBuildTool, compiler, linker, dotnet, or other heavy process is active.
7. Confirm absence of:
   - `D:\SG52M01R02`;
   - `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02\build_attempt_01`;
   - the future terminal supervisor manifest;
   - the future emergency receipt.
8. Rerun the frozen offline verifier and require `PASS`.
9. Syntax-check the supervisor under Windows PowerShell 5.1.
10. Require exactly one normal-build `Start-Process`, zero retries, no
    alternate build command, no UnrealEditor or Blender launch path, and no
    copy-back path.

If any preflight fails, create no build view and launch no build. Freeze the
failure as `FAILED_WITH_EVIDENCE`.

## Exact build

The supervisor must directly launch:

`D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`

First argument:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`

Remaining arguments:

- `Skyguard52Editor`
- `Win64`
- `Development`
- `-Project=D:\SG52M01R02\Skyguard52.uproject`
- `-WaitMutex`
- `-NoHotReloadFromIDE`

Working directory:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool`

Maximum timeout: `1200` seconds.

Launch exactly once. Never retry and never reuse a failed namespace.

## Evidence and validation

Preserve:

- exact executable and arguments;
- working directory;
- PID and process-tree samples;
- start and end timestamps;
- timeout state;
- numeric exit code and its type;
- stdout and stderr;
- compiler and linker evidence;
- exact copied-view inventory;
- unique ModuleRules inventory;
- produced binary inventory;
- source and config parity;
- terminal supervisor manifest;
- emergency receipt, if required.

Require before launch:

- every copied file matches its source byte count and SHA-256;
- no undeclared file exists in the view;
- Recovery01 and Recovery04 are absent from the view;
- all included ModuleRules class names are unique.

If the build succeeds, require fresh:

- `D:\SG52M01R02\Binaries\Win64\UnrealEditor-Skyguard52.dll`;
- its PDB;
- `UnrealEditor.modules`.

Verify the isolated environment source and original source retain the accepted
hash. Do not copy binaries back into `D:\Skyguard52`.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Even if the build passes, record:

`CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_BEFORE_RUNTIME_BINDING`

as a required later gate. An isolated build does not prove that the normal
project plugin root is runtime-safe.

Do not build Recovery05, launch UnrealEditor, integrate, capture, profile, or
package during this gate.

Stop after immutable terminal classification, audit/dashboard updates, and
creation of the separate next prompt.
