Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every prior Gate 2 attempt and every Recovery01–04 source, build, package, preflight, terminal, and failed namespace as immutable.

Treat the accepted Recovery04 native-build terminal freeze as the sole new authority:

- `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json`
- Required classification:
  `PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`

## Authorization

Perform exactly one offline-only controlled active-plugin-root migration design gate.

Do not move, rename, delete, quarantine, copy, overwrite, enable, disable, build, or load any plugin during this gate.

Do not launch UnrealEditor, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, dotnet, compiler, linker, BuildPlugin, capture, profiling, gameplay, promotion, integration, or packaging.

Do not modify:

- `Skyguard52.uproject`;
- project Source or Config;
- any `.uplugin`;
- any plugin source, binary, receipt, or frozen evidence;
- `D:\SG52M01R04`;
- any failed attempt namespace.

## Objective

Design and freeze the exact migration required by:

`CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_BEFORE_RUNTIME_BINDING`

The design must ensure that only the accepted Recovery05 runtime-binding plugin root can be visible to a future Unreal launch, while all legacy or duplicate-module roots remain preserved as immutable evidence outside the active discovery path.

## Preflight

1. Verify the Recovery04 terminal freeze and every member’s byte count and SHA-256.
2. Verify the Recovery04 offline-design freeze remains unchanged.
3. Verify the isolated build outputs and all 170 source records remain unchanged.
4. Confirm no heavy process is active.
5. Inventory every directory and file beneath:
   `D:\Skyguard52\Plugins`.
6. Record byte count and SHA-256 for every plugin descriptor, Build.cs, source file, binary, PDB, module receipt, manifest, and test.
7. Parse every descriptor and record:
   - plugin identity;
   - `EnabledByDefault`;
   - module name;
   - module type;
   - loading phase.
8. Parse every Build.cs and record each ModuleRules class.
9. Detect duplicate plugin identities, duplicate runtime module identities, duplicate ModuleRules classes, and incompatible binary/source pairings.
10. Verify the current roots include:
    - `SkyguardRecovery03`;
    - `SkyguardRecovery03NativeRecovery01`;
    - `SkyguardRecovery03NativeRecovery04`;
    - `SkyguardRecovery03NativeRecovery05`.

If any frozen authority differs, classify `FAILED_WITH_EVIDENCE` and stop.

## Migration design requirements

Create a machine-readable migration contract that identifies:

1. The one intended active Recovery05 plugin root for the future runtime proof.
2. Every legacy root that must be removed from Unreal’s active plugin-discovery path.
3. A fresh immutable quarantine namespace outside `D:\Skyguard52\Plugins`.
4. Exact source and destination paths for every future move.
5. Pre-move and required post-move hashes for every file.
6. Collision checks proving every destination is absent.
7. Atomic move ordering.
8. Rollback ordering.
9. A no-delete rule.
10. A no-overwrite rule.
11. A no-merge rule.
12. A no-partial-success rule.
13. Terminal evidence for every path on success or failure.
14. Verification that the intended active plugin remains disabled by default until a separately authorized runtime launcher enables it explicitly.
15. Verification that the future plugin discovery set contains no duplicate module or ModuleRules identities.

Do not infer that a newer directory name is accepted. Bind the intended active root only to previously accepted source, build, and provenance hashes.

## Future execution design

Prepare—but do not execute—a one-shot migration supervisor that:

- verifies all frozen hashes before mutation;
- confirms all destination paths are absent;
- confirms zero heavy processes;
- creates one fresh attempt namespace;
- performs only the frozen atomic moves;
- never deletes or overwrites;
- never retries;
- preserves a terminal manifest on every outcome;
- automatically rolls back completed moves if a later move fails;
- independently verifies source/destination parity;
- verifies the final active plugin-discovery set;
- never launches UnrealEditor or a build process.

Prepare a separate rollback supervisor, but do not run it.

## Required artifacts

Create fresh versioned artifacts:

- plugin-root inventory;
- descriptor and ModuleRules collision report;
- selected active-root authority;
- migration contract;
- rollback contract;
- projected source/destination path report;
- one-shot migration supervisor;
- rollback supervisor;
- offline verifier;
- exact-host offline-test result;
- readiness record;
- immutable offline-design freeze;
- exact separate prompt for one future controlled migration execution.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not execute the migration during this gate.

Do not build the Recovery05 plugin or launch Unreal.

Stop after immutable offline classification and, only if passed, creation of the separate one-shot migration prompt.
