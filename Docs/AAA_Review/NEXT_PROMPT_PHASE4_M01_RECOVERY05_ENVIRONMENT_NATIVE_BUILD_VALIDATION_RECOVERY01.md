Resume only the existing Unreal Engine 5.8 and Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every earlier Recovery01–05 artifact and failed namespace as immutable.

Treat this accepted validation-recovery freeze as the sole new build authority:

- file:
  `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01_FREEZE.json`;
- bytes: `10044`;
- SHA-256:
  `0bd0bfee24e28d7cfd8a4f086209ed97cab7d4ffc40b09913e85d9c031b6293a`;
- classification:
  `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION`.

Supporting artifact inventory:

- file:
  `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_SOURCE_RECOVERY01_VALIDATION_RECOVERY01_ARTIFACT_INVENTORY.json`;
- bytes: `8302`;
- SHA-256:
  `2a649b222addfd43bab8d2393a25668549d6f86b744888efe7458d39cc8fd8d0`.

Do not edit any file recorded in the accepted freeze.

## Authorization

I explicitly authorize exactly one native project build of:

`Skyguard52Editor Win64 Development`

This authorization covers one build process only. It does not authorize UnrealEditor, Blender, ShaderCompileWorker outside the governed build tree, Recovery05 plugin packaging, capture, gameplay, profiling, promotion, integration, or game packaging.

## Objective

Prove that the accepted Mission 1 environment mobility correction compiles and links in the complete UE 5.8 editor target without changing the accepted source.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

## Immutable source authority

Require:

- file:
  `D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`;
- bytes: `15032`;
- SHA-256:
  `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`;
- LF-only source;
- exactly one:
  `Root->SetMobility(EComponentMobility::Static);`;
- exact position between root creation and `SetRootComponent(Root)`.

Verify every hash and byte count in the accepted freeze before creating any build namespace.

## Installed UE authorities

Verify before launch:

1. Bundled .NET host:
   - `D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`;
   - bytes: `178400`;
   - SHA-256:
     `a8d3105441b568cfd44ac5eab8c0fc190cdefb0047e3e84e49cbce819a197a7a`.
2. UnrealBuildTool assembly:
   - `D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`;
   - bytes: `3209656`;
   - SHA-256:
     `b0931427529b907eea171f1913ed8a50c5753a3cae733ac2773be537f633d1a8`.
3. Project descriptor:
   - `D:\Skyguard52\Skyguard52.uproject`;
   - bytes: `1542`;
   - SHA-256:
     `99461a1a562ede732da52c84f05002dcc88f772cd30fdccd45ff46d6836f3b60`.
4. Editor target:
   - `D:\Skyguard52\Source\Skyguard52Editor.Target.cs`;
   - bytes: `489`;
   - SHA-256:
     `83468f9644058f4431f2ffc3fe7e011dbe8a01ce93f9f35fc4f098363fd1e78d`.
5. Game target:
   - `D:\Skyguard52\Source\Skyguard52.Target.cs`;
   - bytes: `346`;
   - SHA-256:
     `f7a96095d9c7681c33ad259d4f5d6e9b2e593600d4fd2e0c09fe02bcf4358584`.

Use the self-contained `FileStream` plus `SHA256` implementation. Do not depend on `Get-FileHash`.

## Fresh build namespace

Reserve and require absence of:

`D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01\build_attempt_01`

Never reuse any earlier attempt or package namespace.

Before creating the fresh namespace:

1. Confirm no UnrealEditor, UnrealEditor-Cmd, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler, linker, or unrelated dotnet build process is active.
2. Verify the accepted validation freeze and all 23 frozen records.
3. Create a complete pre-build inventory of:
   - `Skyguard52.uproject`;
   - `Source`;
   - relevant project `Config`;
   - enabled project plugin descriptors and source;
   - current `Binaries\Win64` editor outputs.
4. Record exact byte counts, SHA-256 hashes, and timestamps.
5. Record the current binary baseline:
   - `UnrealEditor-Skyguard52.dll`: bytes `2891264`, SHA-256 `5776561194ddec0fc23c476a41a467aef5d72dcb883b1105deed6ab72daf336f`;
   - `UnrealEditor-Skyguard52.pdb`: bytes `98291712`, SHA-256 `5bd4a7e82d72f71cf7634ea2c09d1126856bcc50675317bb45d8737028ae4cc4`;
   - `UnrealEditor.modules`: bytes `98`, SHA-256 `17821e7c0f6aba09788fc98dd80299e0b4de98cbb09cc2e8c8f9b0e17146bfeb`.
6. Create a one-shot supervisor in a new versioned path.
7. Syntax-check the supervisor under Windows PowerShell 5.1.
8. Require exactly one normal-build `Start-Process`, zero retry paths, a guaranteed terminal manifest, and numeric exit-code preservation.

If any preflight condition fails, do not launch the build. Freeze the failure and classify `FAILED_WITH_EVIDENCE`.

## Exact build launch

Launch exactly:

Executable:

`D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe`

First argument:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`

Remaining arguments:

- `Skyguard52Editor`
- `Win64`
- `Development`
- `-Project=D:\Skyguard52\Skyguard52.uproject`
- `-WaitMutex`
- `-NoHotReloadFromIDE`

Working directory:

`D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool`

Do not use:

- `cmd.exe`;
- `Build.bat`;
- system dotnet;
- a shell association;
- another wrapper;
- an alternate build command.

Use a maximum governed timeout of 1,200 seconds. A timeout is failure. Do not launch a replacement process.

## Process and evidence requirements

The supervisor must:

1. Create the build-attempt namespace only after all preflight checks pass.
2. Launch bundled dotnet exactly once.
3. Retain the exact process object and native process handle.
4. Redirect stdout and stderr directly into the immutable attempt.
5. Record process-tree samples throughout the build.
6. Record start and end UTC timestamps.
7. Call `WaitForExit()` and `Refresh()`.
8. Persist:
   - numeric exit code;
   - exit-code type;
   - timeout status;
   - exact executable;
   - exact argument array;
   - working directory;
   - supervisor launch count;
   - bundled-dotnet launch count;
   - UBT invocation count;
   - retry count;
   - process tree;
   - compiler and linker evidence;
   - complete produced-file inventory.
9. Write a terminal supervisor manifest on every outcome.
10. Treat a null, missing, unreadable, or nonnumeric exit code as failure.
11. Never coerce null into zero.
12. Never infer the exit code from log text.
13. Never retry.
14. Never launch UnrealEditor or Blender.

## Failure handling

If preflight, launch, timeout, UHT, compile, link, inventory, source-parity, output, or terminal-evidence validation fails:

1. Preserve the attempt unchanged.
2. Record the exact failure stage and message.
3. Hash every available artifact.
4. Confirm zero retries.
5. Confirm no UnrealEditor or Blender process launched.
6. Create immutable terminal evidence and a terminal freeze.
7. Classify exactly:
   `FAILED_WITH_EVIDENCE`.
8. Stop.

Do not repair source or retry the build in this gate.

## Successful-build validation

If bundled dotnet returns numeric `System.Int32` exit code zero:

1. Require UHT, compilation, and linking to complete successfully.
2. Reject compiler errors, linker errors, fatal errors, cancelled actions, and unresolved symbols.
3. Require fresh post-build records for:
   - `D:\Skyguard52\Binaries\Win64\UnrealEditor-Skyguard52.dll`;
   - its PDB;
   - `UnrealEditor.modules`;
   - relevant `Intermediate` object, dependency, manifest, and receipt files.
4. Require the editor DLL and PDB timestamps to be no earlier than the governed build start.
5. Require the resulting editor DLL to differ from the pre-build binary baseline, proving activation of the accepted source change.
6. Verify the accepted environment source remained exactly `15032` bytes at SHA-256 `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.
7. Re-run the frozen offline validation checks without creating or modifying their frozen namespaces.
8. Require source/candidate byte parity, exact one-line diff, attachment invariants, and authority preservation to remain green.
9. Confirm the Recovery05 plugin remains unbuilt and disabled by default.
10. Confirm no UnrealEditor, Blender, capture, integration, promotion, or packaging process launched.
11. Create:
    - pre-build source and binary inventory;
    - terminal build manifest;
    - compiler/linker evidence index;
    - post-build source and binary inventory;
    - focused environment validation result;
    - readiness record;
    - immutable native-build freeze;
    - Phase 1–8 audit addendum;
    - Mission 1 acceptance-matrix addendum;
    - updated production dashboard;
    - exact separate prompt for one future Recovery05 plugin build.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not build the Recovery05 plugin during this gate.

Do not launch UnrealEditor, Blender, capture, profiling, promotion, integration, or packaging.

Run only this one heavy process and stop after immutable terminal classification, audit/dashboard updates, and creation of the separate Recovery05 plugin-build prompt.
