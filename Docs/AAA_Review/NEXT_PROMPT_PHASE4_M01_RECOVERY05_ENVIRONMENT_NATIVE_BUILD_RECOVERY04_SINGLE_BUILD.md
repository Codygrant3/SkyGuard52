Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat Gate 2 Attempt 01, Recovery02 Supervisor Attempt 01, and Recovery03 Build Attempt 01 as immutable and terminal. Never rerun, modify, repair, rename, overwrite, delete, or reuse them.

Treat the Recovery04 offline-design freeze as the sole new build authority:

- `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_OFFLINE_DESIGN_FREEZE.json`
- Required classification:
  `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_AUTHORIZATION`

I explicitly authorize exactly one Recovery04 isolated native project build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery04_once.ps1 -AuthorizeSingleBuild`

Do not reinterpret, broaden, or replace the frozen contract.

## Preflight

Before creating a namespace or launching anything:

1. Verify the Recovery04 offline-design freeze and every member’s byte count and SHA-256.
2. Verify every controlling Recovery03 authority remains unchanged.
3. Verify all 170 source-parity records.
4. Verify all 170 files in the failed Recovery03 isolated view remain unchanged.
5. Verify the Mission 1 environment source remains:
   - path:
     `D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`;
   - bytes:
     `15032`;
   - SHA-256:
     `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.
6. Confirm no Unreal, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, dotnet, compiler, linker, or unrelated heavy process is active.
7. Confirm these future namespaces are absent:
   - `D:\SG52M01R04`;
   - `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04\build_attempt_01`;
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_TERMINAL_SUPERVISOR_MANIFEST.json`;
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_EMERGENCY_RECEIPT.jsonl`.
8. Run:
   `python D:\Skyguard52\Scripts\verify_phase4_m01_recovery05_environment_native_build_recovery04_offline.py`
9. Require its classification to be `PASS`.
10. Parse the supervisor under Windows PowerShell 5.1 and require zero parser errors.
11. Require exactly one normal-build `Start-Process`, zero retry paths, no alternate build command, no UnrealEditor or Blender launch path, and no output copy-back path.

If any preflight condition fails, create no isolated view and launch no build process. Preserve the failure evidence, classify `FAILED_WITH_EVIDENCE`, and stop.

## Isolated build view

Create exactly one fresh view at:

`D:\SG52M01R04`

Copy only the 170 frozen source-parity records.

The view must include:

- the exact project descriptor;
- exact Source;
- exact Config;
- unique `SkyguardRecovery03`;
- unique `SkyguardRecovery03NativeRecovery05`.

It must exclude:

- `SkyguardRecovery03NativeRecovery01`;
- `SkyguardRecovery03NativeRecovery04`;
- Content;
- existing Binaries;
- Intermediate;
- Saved;
- DerivedDataCache.

Do not modify, move, rename, delete, mask, or repair the original plugin directories.

Before building, verify every copied file’s relative path, byte count, and SHA-256. Parse ModuleRules records as `[pscustomobject][ordered]` values. Require exactly two nonblank distinct plugin ModuleRules classes:

- `SkyguardRecovery03`;
- `SkyguardRecovery03NativeRecovery05`.

## Exact build

Launch exactly:

Executable:

`D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`

First argument:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`

Remaining arguments:

- `Skyguard52Editor`
- `Win64`
- `Development`
- `-Project=D:\SG52M01R04\Skyguard52.uproject`
- `-WaitMutex`
- `-NoHotReloadFromIDE`

Working directory:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool`

Maximum timeout: `1200` seconds.

Run exactly one heavy process. Never retry automatically and never reuse a failed namespace.

Do not invoke Luna, Terra, Grok, Sol, Opus 5, UnrealEditor, Blender, capture, profiling, gameplay, integration, promotion, or packaging.

## Terminal evidence

Preserve:

- exact executable, argument array, and working directory;
- supervisor and child-process IDs;
- process-tree samples;
- timestamps;
- timeout status;
- numeric exit code and its type;
- launch and retry counts;
- stdout and stderr;
- compiler and linker output;
- copied-view inventory;
- ModuleRules analysis;
- output inventory;
- source parity;
- terminal supervisor manifest;
- emergency receipt if required.

Treat missing, null, unreadable, or nonnumeric exit code evidence as failure. Never coerce null into zero and never infer an exit code from logs.

## Failure handling

If any preflight, view, ModuleRules, launch, timeout, compiler, linker, output, parity, inventory, or terminal-evidence condition fails:

1. Preserve the attempt unchanged.
2. Hash all evidence.
3. Confirm zero retries, zero copy-back, zero UnrealEditor launches, and zero Blender launches.
4. Create an immutable terminal freeze.
5. Classify exactly:
   `FAILED_WITH_EVIDENCE`.
6. Stop.

## Successful-build validation

If UBT returns numeric `System.Int32` exit code `0`, require fresh:

- `D:\SG52M01R04\Binaries\Win64\UnrealEditor-Skyguard52.dll`;
- its PDB;
- `D:\SG52M01R04\Binaries\Win64\UnrealEditor.modules`.

Verify:

1. Every output was created by this single attempt.
2. Original and isolated source parity remains exact.
3. The Mission 1 environment source remains at the accepted hash.
4. No output was copied back into `D:\Skyguard52`.
5. Every Recovery01–03 artifact and failed namespace remains unchanged.
6. One build launch, zero retries, zero UnrealEditor launches, and zero Blender launches.

Create:

- terminal native-build manifest;
- complete source and binary inventory;
- build acceptance record;
- immutable terminal freeze;
- audit and dashboard updates;
- exact separate next prompt for the controlled active-plugin-root migration prerequisite.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Even on success, preserve this later prerequisite:

`CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_BEFORE_RUNTIME_BINDING`

Do not build the Recovery05 plugin, launch UnrealEditor or Blender, capture, integrate, profile, promote, or package.

Stop after immutable terminal classification and creation of the exact separate next prompt.
