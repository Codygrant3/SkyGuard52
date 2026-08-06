Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat Gate 2 Attempt 01 and Recovery02 Supervisor Attempt 01 as immutable and terminal. Never rerun, modify, rename, repair, overwrite, or reuse either attempt.

Treat the latest Recovery02 Supervisor Attempt 01 terminal freeze as authoritative. Verify its exact path, byte count, and SHA-256 from the current project before creating any new artifact.

The authorized Recovery02 supervisor failed before namespace creation or UBT launch because its `$State` hashtable used bare PowerShell expressions:

- line 231: `copy_back_performed = false`
- line 232: `unreal_editor_launched = false`
- line 233: `blender_launched = false`

Windows PowerShell treated `false` as a command. State initialization occurred before the script `try` block, so the supervisor also failed to write its promised terminal manifest.

## Authorization

Perform exactly one offline-only Recovery03 supervisor-correction design gate.

Do not launch UnrealEditor, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, dotnet, a compiler, a linker, BuildPlugin, capture, profiling, gameplay, promotion, integration, or packaging.

Do not modify project source, Config, the `.uproject`, or any plugin.

## Immutable authorities

Verify and freeze:

1. The new Recovery02 Supervisor Attempt 01 terminal freeze and all of its members.
2. Recovery02 offline-design freeze:
   `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_OFFLINE_DESIGN_FREEZE.json`
   SHA-256 `6daa7c5f0860174567bd027c43c2e7273fda870e97226bb4fbb728d69b479818`.
3. Frozen Recovery02 supervisor:
   `D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery02_once.ps1`
   bytes `16132`;
   SHA-256 `5d42533af89f4223a60531168da446a471a9a26fce50961df4721ef8bc2465dd`.
4. Mission 1 environment source:
   `D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`
   bytes `15032`;
   SHA-256 `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.
5. All 170 Recovery02 source-parity records.
6. Gate 2 Attempt 01 evidence.

If any authority differs, classify `FAILED_WITH_EVIDENCE` and stop.

## Fresh namespaces

Reserve and require absence of:

- `D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1`
- `D:\SG52M01R03`
- `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03\build_attempt_01`
- Recovery03 terminal supervisor manifest;
- Recovery03 emergency receipt;
- Recovery03 readiness, inventory, validation, and freeze artifacts.

Do not create the future view, build-attempt, runtime, launcher, or capture namespaces during this offline gate.

## Bounded supervisor correction

Derive a fresh Recovery03 supervisor from the frozen Recovery02 supervisor.

Permitted executable corrections are limited to:

1. Replace exactly the three bare value expressions `false` at frozen lines 231–233 with `$false`.
2. Establish the terminal-evidence lifecycle before any fallible state construction:
   - initialize a minimal terminal state using valid PowerShell literals;
   - enter an outer `try/catch/finally` before authority, namespace, or full-state checks;
   - guarantee a terminal supervisor manifest for every outcome;
   - guarantee a minimal emergency receipt if normal manifest writing fails.
3. Add an explicit `-OfflineContractTest` path that exercises state initialization, hash verification, failure capture, and terminal JSON serialization without creating governed namespaces or reaching the UBT launch.
4. Strengthen the offline verifier to reject bare `true`, `false`, or `null` expressions wherever PowerShell value expressions require `$true`, `$false`, or `$null`.

No other build behavior may change.

## Static diff contract

Require a machine-readable diff between Recovery02 and Recovery03.

Allow only:

- the three `$false` literal corrections;
- the minimum outer terminal-lifecycle correction;
- offline-test isolation;
- Recovery03 namespace and evidence-path versioning.

Reject changes to:

- the 170-record parity contract;
- isolated-view inclusion or exclusion rules;
- exact UBT executable, DLL, arguments, or working directory;
- timeout;
- one-launch and zero-retry rules;
- output requirements;
- source-parity validation;
- no-copy-back rule;
- project or plugin sources.

## Exact-host offline tests

Under:

`powershell.exe -NoProfile -ExecutionPolicy Bypass`

require:

1. Windows PowerShell 5.1 syntax parsing with zero errors.
2. Recovery03 `-OfflineContractTest` returns numeric `System.Int32` exit code `0`.
3. Full `$State` initialization succeeds.
4. JSON serialization succeeds.
5. A deliberate temporary preflight failure produces a temporary terminal manifest.
6. A deliberate manifest-write failure produces a temporary emergency receipt.
7. Bare-literal static scans pass.
8. Exactly zero UBT, dotnet-build, Unreal, Blender, compiler, and linker launches.
9. No governed Recovery03 namespace is created.

Temporary test evidence must live outside all governed namespaces.

## Future build contract

Prepare but do not execute one frozen Recovery03 build supervisor using:

- view: `D:\SG52M01R03`;
- bundled UE 5.8 dotnet;
- `UnrealBuildTool.dll`;
- `Skyguard52Editor Win64 Development`;
- exact project argument for the Recovery03 isolated view;
- 1200-second timeout;
- exactly one launch;
- zero retries;
- no output copy-back.

The future isolated view must copy the same 170 frozen parity records and preserve the same collision exclusions.

## Required artifacts

Create only fresh Recovery03 artifacts:

- terminal-evidence reconciliation;
- supervisor correction contract;
- corrected one-shot supervisor;
- strict source-diff report;
- exact-host offline-test result;
- strengthened offline verifier;
- projected-path report;
- source inventory;
- readiness record;
- immutable offline-design freeze;
- exact separate prompt for one future Recovery03 native project build.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not execute the native build during this gate.

Stop after immutable offline classification and, only if passed, creation of the separate one-shot Recovery03 build prompt.
