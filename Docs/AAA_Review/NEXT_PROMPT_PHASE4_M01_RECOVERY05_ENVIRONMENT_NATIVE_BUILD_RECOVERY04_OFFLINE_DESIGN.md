Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat Gate 2 Attempt 01, Recovery02 Supervisor Attempt 01, and Recovery03 Build Attempt 01 as immutable and terminal. Never rerun, modify, repair, rename, overwrite, delete, or reuse them.

Treat the latest Recovery03 Attempt 01 terminal freeze as authoritative. Verify its exact path, byte count, SHA-256, and every member before creating anything.

Recovery03 copied and verified all 170 parity records, then stopped before UBT because its Windows PowerShell 5.1 ModuleRules check reported:

`Duplicate ModuleRules classes remain in build view: `

Independent evidence proves the isolated view contains exactly two distinct ModuleRules classes:

- `SkyguardRecovery03`
- `SkyguardRecovery03NativeRecovery05`

Root cause: the supervisor appends `[ordered]` dictionaries directly to `$classes`. Under Windows PowerShell 5.1, `Group-Object class` does not reliably expose the dictionary key as an object property, so both records group under a blank key.

## Authorization

Perform exactly one offline-only Recovery04 supervisor-correction design gate.

Do not launch UnrealEditor, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, dotnet, compiler, linker, BuildPlugin, capture, profiling, gameplay, promotion, integration, or packaging.

Do not modify project source, Config, the `.uproject`, any plugin, the failed Recovery03 isolated view, or any prior evidence.

## Immutable authorities

Verify:

1. The Recovery03 Attempt 01 terminal freeze and every member.
2. Recovery03 offline-design freeze:
   `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY03_OFFLINE_DESIGN_FREEZE.json`
   bytes `6448`;
   SHA-256 `c44c48b496b9d150dd8a7151f54e1e6d3099e84ab202b3fea9e46d3e7c8edca0`.
3. Recovery03 supervisor:
   `D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery03_once.ps1`
   bytes `21904`;
   SHA-256 `07b94689525496afecb3867ee91898223f32c9b1327d45a709729767dfbd4eb4`.
4. Recovery03 failed view inventory and ModuleRules analysis.
5. All 170 source-parity records.
6. Mission 1 environment source:
   bytes `15032`;
   SHA-256 `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.

If any authority differs, classify `FAILED_WITH_EVIDENCE` and stop.

## Fresh Recovery04 namespaces

Reserve and require absence of:

- `D:\Skyguard52\Scripts\build_phase4_m01_recovery05_environment_native_build_recovery04_once.ps1`
- `D:\SG52M01R04`
- `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04\build_attempt_01`
- Recovery04 terminal supervisor manifest
- Recovery04 emergency receipt
- Recovery04 reports, readiness, freeze, and future prompt

Do not create the future view or build-attempt namespace during this offline gate.

## Exact bounded correction

Derive Recovery04 from the frozen Recovery03 supervisor.

The only normal-build functional correction permitted is changing:

`$classes += [ordered]@{`

to:

`$classes += [pscustomobject][ordered]@{`

Preserve the class record keys, regex, duplicate grouping, duplicate rejection, exact UBT command, parity contract, exclusions, timeout, output validation, one-launch rule, zero-retry rule, terminal lifecycle, and no-copy-back rule.

Version only future Recovery04 namespaces and evidence paths from `R03` to `R04`.

## Exact-host offline grouping tests

Extend `-OfflineContractTest` without reaching the build path:

1. Create two `[pscustomobject][ordered]` mock records named `SkyguardRecovery03` and `SkyguardRecovery03NativeRecovery05`.
2. Run the exact production `Group-Object class` pipeline.
3. Require duplicate count `0`.
4. Create two records with the same class name.
5. Require duplicate count `1` with the exact expected name.
6. Verify blank class names are rejected.
7. Verify the real two frozen Build.cs files parse to the two distinct expected class names.
8. Require Windows PowerShell 5.1 parser errors `0`.
9. Require numeric `System.Int32` test exit code `0`.
10. Require zero governed namespaces and zero UBT, dotnet-build, Unreal, Blender, compiler, or linker launches.

## Static diff contract

Create a machine-readable Recovery03-to-Recovery04 diff.

Allow only:

- the one `[pscustomobject]` cast;
- the exact-host ModuleRules grouping probes;
- Recovery04 namespace and evidence-path versioning.

Reject all other changes to build behavior, sources, plugins, parity, exclusions, executable, arguments, timeout, output requirements, retry handling, or copy-back behavior.

## Required artifacts

Create only fresh Recovery04 artifacts:

- terminal-evidence reconciliation;
- supervisor-correction contract;
- corrected one-shot supervisor;
- strict source-diff report;
- exact-host grouping-test result;
- strengthened offline verifier;
- projected-path report;
- source inventory;
- readiness record;
- immutable offline-design freeze;
- exact separate prompt for one future Recovery04 native project build.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not execute the native build during this gate.

Stop after immutable offline classification and, only if passed, creation of the separate one-shot Recovery04 build prompt.
