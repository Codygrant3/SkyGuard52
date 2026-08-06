Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat Gate 2 Attempt 01, Recovery02 Supervisor Attempt 01, and every frozen Recovery02 artifact as immutable and terminal. Never rerun, modify, repair, rename, overwrite, or reuse them.

Treat this Recovery03 offline-design freeze as the sole new build authority:

- File:
  `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_OFFLINE_DESIGN_FREEZE.json`
- Bytes:
  `6448`
- SHA-256:
  `c44c48b496b9d150dd8a7151f54e1e6d3099e84ab202b3fea9e46d3e7c8edca0`
- Classification:
  `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_AUTHORIZATION`

Supporting authorities:

1. Recovery03 supervisor:
   - `D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1`
   - bytes: `21904`
   - SHA-256:
     `07b94689525496afecb3867ee91898223f32c9b1327d45a709729767dfbd4eb4`
2. Recovery03 offline verifier:
   - `D:\Skyguard52\Scripts\verify_phase4_m01_recovery05_environment_native_build_recovery03_offline.py`
   - bytes: `7503`
   - SHA-256:
     `9486e64feaca831d50c9151ec7fc621fd418fedb9129fb9def54253bb8abe091`
3. Recovery03 readiness:
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_READINESS.json`
   - bytes: `1125`
   - SHA-256:
     `19ab011bbdd56e1728986c50bd5065af39eb75776a0413257a2f5a58a72cdf22`
4. Source-parity contract:
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json`
   - bytes: `54738`
   - SHA-256:
     `d241f6ecae392d96d18955edb8610fbdfb80518c1f7d85fbbd43084a6b37c1df`
   - records: `170`
5. Mission 1 environment source:
   - `D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`
   - bytes: `15032`
   - SHA-256:
     `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`

I explicitly authorize exactly one Recovery03 isolated native project build by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1 -AuthorizeSingleBuild`

Do not broaden or reinterpret the frozen contract.

## Preflight

Before creating a governed namespace or launching anything:

1. Verify the Recovery03 freeze byte count and SHA-256.
2. Verify every freeze member’s byte count and SHA-256.
3. Verify all 170 source-parity records against `D:\Skyguard52`.
4. Verify the accepted Mission 1 environment source hash.
5. Verify the frozen Recovery02 authorities and failed attempts remain unchanged.
6. Confirm no Unreal, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler, linker, dotnet-build, or unrelated heavy process is active.
7. Confirm these future namespaces remain absent:
   - `D:\SG52M01R03`
   - `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03\build_attempt_01`
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json`
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_EMERGENCY_RECEIPT.jsonl`
8. Run:
   `python D:\Skyguard52\Scripts\verify_phase4_m01_recovery05_environment_native_build_recovery03_offline.py`
9. Require the verifier classification `PASS`.
10. Parse the supervisor under Windows PowerShell 5.1 and require zero errors.
11. Confirm exactly one normal-build `Start-Process`, zero retry paths, no alternate build command, and no UnrealEditor or Blender launch path.
12. Do not rerun `-OfflineContractTest`; its successful evidence is already frozen.

If any preflight condition fails, do not create the isolated view and do not launch UBT. Preserve the failure and classify `FAILED_WITH_EVIDENCE`.

## Isolated build view

Create exactly one fresh view:

`D:\SG52M01R03`

Copy only the 170 frozen parity records.

The view must include the exact project descriptor, Source, Config, unique `SkyguardRecovery03`, and unique `SkyguardRecovery03NativeRecovery05`.

It must exclude:

- `SkyguardRecovery03NativeRecovery01`
- `SkyguardRecovery03NativeRecovery04`
- Content
- existing Binaries
- Intermediate
- Saved
- DerivedDataCache

Do not modify, move, rename, delete, mask, or repair original project or plugin directories.

Verify every copied relative path, byte count, and SHA-256 before building. Require unique ModuleRules class names.

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
- `-Project=D:\SG52M01R03\Skyguard52.uproject`
- `-WaitMutex`
- `-NoHotReloadFromIDE`

Working directory:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool`

Maximum timeout: `1200` seconds.

Run exactly one heavy process. Never retry automatically and never reuse a failed namespace.

Do not invoke Luna, Terra, Grok, Sol, Opus 5, or another external model.

## Terminal evidence

Preserve:

- exact executable and arguments;
- working directory;
- supervisor and child PIDs;
- process-tree samples;
- timestamps;
- timeout state;
- numeric exit code and type;
- stdout and stderr;
- compiler and linker evidence;
- complete isolated-view inventory;
- source-parity verification;
- output inventory;
- external terminal supervisor manifest;
- emergency receipt, if created;
- launch and retry counts;
- no-copy-back status.

The terminal supervisor manifest is mandatory on every outcome.

## Failure handling

If preflight, namespace creation, copying, UBT, compilation, linking, timeout, output validation, source parity, or terminal evidence fails:

1. Preserve the attempt unchanged.
2. Never retry.
3. Hash all available evidence.
4. Confirm no UnrealEditor or Blender process launched.
5. Confirm no output was copied into `D:\Skyguard52`.
6. Create an immutable terminal freeze.
7. Classify exactly:
   `FAILED_WITH_EVIDENCE`.
8. Generate a bounded offline recovery-design prompt and stop.

## Successful-build validation

If UBT returns numeric `System.Int32` exit code `0`, require fresh:

- `D:\SG52M01R03\Binaries\Win64\UnrealEditor-Skyguard52.dll`
- `D:\SG52M01R03\Binaries\Win64\UnrealEditor-Skyguard52.pdb`
- `D:\SG52M01R03\Binaries\Win64\UnrealEditor.modules`

Require:

1. Every output postdates the governed build start.
2. Compiler and linker logs contain no terminal error.
3. The isolated and original Mission 1 environment source remain byte-for-byte identical to the accepted authority.
4. All copied source records retain parity.
5. Exactly one supervisor launch, one bundled-dotnet launch, and one UBT invocation occurred.
6. Retry count is zero.
7. No UnrealEditor or Blender process launched.
8. No output was copied back into `D:\Skyguard52`.

Create terminal build manifest, output inventory, acceptance record, readiness record, immutable terminal freeze, audit/dashboard updates, and the exact separate prompt for the future Recovery05 plugin build.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Even on success, preserve:

`CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_BEFORE_RUNTIME_BINDING`

Do not build the Recovery05 plugin, launch UnrealEditor or Blender, capture, profile, integrate, promote, or package.

Stop after immutable terminal classification and creation of the separate next prompt.
