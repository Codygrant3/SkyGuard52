Resume only the existing Unreal Engine 5.8/Blender AAA project at
`D:\Skyguard52`. Do not use the retired Three.js project, external models, or
subagents.

Treat Gate 2 Attempt 01 as immutable and terminal:

- classification: `FAILED_WITH_EVIDENCE`;
- attempt:
  `D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01\build_attempt_01`;
- terminal supervisor manifest:
  `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_VALIDATION_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json`;
- terminal manifest SHA-256:
  `6b754d34ba9941ea15cd428f9b85531326e57826d6496da067d64dfb8da79e62`;
- build stdout SHA-256:
  `13ce52b1302cf08f024c849c13ca572ba3db817f33cbb618a2bbd4c13c4824c6`;
- numeric exit code: `8`;
- exit-code type: `System.Int32`;
- retries: `0`.

Do not rerun, modify, rename, overwrite, repair, or reuse that attempt or its
namespace.

## Authorization

Perform exactly one offline-only Recovery02 plugin-discovery isolation design
gate.

Do not launch UnrealBuildTool, AutomationTool, UnrealEditor, Blender,
ShaderCompileWorker, a compiler, linker, build, capture, profiling,
integration, promotion, or packaging.

Do not modify:

- `Skyguard52.uproject`;
- any project source;
- any plugin descriptor;
- any Build.cs, header, or implementation file;
- any frozen evidence;
- any accepted binary;
- the failed attempt.

## Objective

Design and freeze the minimum supported recovery that allows the complete
`Skyguard52Editor Win64 Development` target to compile without allowing
immutable duplicate Recovery plugin rules into the same UBT project rules
assembly.

The recovery must preserve the accepted Mission 1 source:

- file:
  `D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`;
- bytes: `15032`;
- SHA-256:
  `73e736b088dd77dfaed42081bd988094d6743057175626db01a1fb9a92ceec44`.

## Recorded collision

Freeze and reconcile:

1. Recovery01:
   - descriptor:
     `Plugins\SkyguardRecovery03NativeRecovery01\SkyguardRecovery03NativeRecovery01.uplugin`;
   - descriptor SHA-256:
     `4953138e24d76aee6db3636ae1c7a0fe3ed84cf1fabcb746c762d2f5a908963e`;
   - module and ModuleRules class:
     `SkyguardRecovery03NativeRecovery01`;
   - Build.cs SHA-256:
     `503a39136a154158474f5d54ad55a00ccaed50c975b008174c3678434d2f1831`.
2. Recovery04:
   - descriptor:
     `Plugins\SkyguardRecovery03NativeRecovery04\SkyguardRecovery03NativeRecovery04.uplugin`;
   - descriptor SHA-256:
     `fbee133982f770cdd9bacec49144585e779c9f92f1ec011b6e601eb3b86e4a19`;
   - module and ModuleRules class:
     `SkyguardRecovery03NativeRecovery01`;
   - Build.cs SHA-256:
     `503a39136a154158474f5d54ad55a00ccaed50c975b008174c3678434d2f1831`.
3. Recovery05 unique candidate:
   - descriptor:
     `Plugins\SkyguardRecovery03NativeRecovery05\SkyguardRecovery03NativeRecovery05.uplugin`;
   - descriptor SHA-256:
     `63e70f723e27f3c29536834dac8a7757629e43b02c13a02ae954fe2c432d57a5`;
   - unique module:
     `SkyguardRecovery03NativeRecovery05`;
   - Build.cs SHA-256:
     `d5735c78adc4fcb24ca3760cec50426d9f039e1a08178ea00a309672efdaa7b6`.

## Installed UE 5.8 authorities

Inspect and freeze exact relevant line ranges, byte counts, and hashes:

1. `D:\UE_5.8\Engine\Source\Programs\Shared\EpicGames.Build\System\EnumeratePlugins.cs`
   - bytes: `9220`;
   - SHA-256:
     `05b88b65a85a9e6b5e15843b1183d6a434bfe711d82d97ef4c78c42aa1a56833`.
2. `D:\UE_5.8\Engine\Source\Programs\UnrealBuildTool\System\Plugins.cs`
   - bytes: `27301`;
   - SHA-256:
     `6c6c52016ad86bc6092389a4879695084a81c8e06a1a94038a1a0a2d266e51b5`.
3. `D:\UE_5.8\Engine\Source\Programs\UnrealBuildTool\Configuration\Rules\RulesCompiler.cs`
   - bytes: `31017`;
   - SHA-256:
     `98e597b1c0aab5a824de7b4ee45cacbede352e355e7cb6b4d7eea70e0bb942f6`.

Prove from installed source that:

- every `.uplugin` below the project `Plugins` root is enumerated;
- all project-plugin Build.cs rules are added to the project rules assembly;
- enablement filtering occurs too late to prevent duplicate ModuleRules types;
- `.ubtignore` in the same directory as a `.uplugin` does not suppress that
  descriptor;
- `EnabledByDefault=false`, a disabled `.uproject` reference, and
  `-DisablePlugins` cannot be accepted as rules-assembly isolation.

## Required options analysis

Evaluate at least:

1. A fresh, immutable isolated build view containing exact project source,
   targets, config and only non-conflicting required project plugins.
2. A separately authorized active-plugin-root cleanup that preserves exact
   immutable copies outside UBT discovery.
3. Any installed-UE-supported project or target mechanism that actually
   prevents obsolete plugin Build.cs rules from entering the project assembly.

Reject any option that:

- modifies frozen plugin artifacts in place;
- relies only on plugin enablement;
- reuses the failed namespace;
- cannot prove exact source and dependency parity;
- cannot produce attributable compiler, linker and binary evidence;
- requires an ungoverned junction, symlink, mount, or environment mutation;
- leaves the normal project permanently unable to build or launch.

## Preferred recovery properties

The selected design should:

- leave `D:\Skyguard52` source and all frozen evidence unchanged;
- use a fresh short recovery namespace;
- preserve exact source, target and config hashes;
- include only the required non-conflicting project plugins;
- prove which project plugins are excluded and why;
- produce deterministic source/dependency parity receipts;
- define how successful outputs are attributed and validated;
- launch exactly one future UBT build;
- never retry;
- never launch UnrealEditor or Blender;
- define the later controlled migration needed to make the normal project root
  buildable without invalidating evidence.

## Offline deliverables

Create fresh versioned Recovery02 artifacts:

- terminal-evidence reconciliation;
- UBT plugin-discovery authority report;
- plugin identity and collision inventory;
- options and rejection matrix;
- selected recovery architecture;
- exact source/config/plugin parity contract;
- fresh namespace contract;
- future one-shot build supervisor;
- PowerShell 5.1 syntax result;
- static verifier;
- readiness record;
- immutable freeze;
- exact separate prompt for one future Recovery02 native build.

Do not create the future build namespace during this gate.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not run the Recovery02 build during this gate. Stop after immutable offline
classification and creation of the separate one-shot build authorization
prompt.
