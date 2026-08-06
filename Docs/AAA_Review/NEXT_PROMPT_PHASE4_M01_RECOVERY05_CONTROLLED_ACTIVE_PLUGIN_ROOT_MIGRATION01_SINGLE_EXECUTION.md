Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every prior Gate 2 and Recovery01–04 artifact and failed namespace as immutable.

Treat this offline-design freeze as the sole migration authority:

`D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_OFFLINE_DESIGN_FREEZE.json`

Required classification:

`PASSED_READY_FOR_EXPLICIT_CONTROLLED_ACTIVE_PLUGIN_ROOT_MIGRATION_AUTHORIZATION`

I explicitly authorize exactly one controlled active-plugin-root migration by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\invoke_phase4_m01_recovery05_active_plugin_root_migration01_once.ps1 -AuthorizeSingleMigration`

Do not broaden or replace the frozen contract.

## Preflight

Before creating any namespace or moving any directory:

1. Verify the offline-design freeze and every member’s byte count and SHA-256.
2. Verify the accepted Recovery04 terminal freeze remains unchanged.
3. Verify all 23 plugin inventory records at their original active paths.
4. Confirm exactly four active plugin roots:
   - `SkyguardRecovery03`;
   - `SkyguardRecovery03NativeRecovery01`;
   - `SkyguardRecovery03NativeRecovery04`;
   - `SkyguardRecovery03NativeRecovery05`.
5. Confirm the selected active Recovery05 descriptor remains disabled by default and hash-identical.
6. Confirm no Unreal, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, dotnet, compiler, linker, or other heavy process is active.
7. Confirm these namespaces are absent:
   - `D:\Skyguard52\Saved\PluginQuarantine\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01`;
   - `D:\Skyguard52\Saved\MigrationAttempts\PHASE4_M01_RECOVERY05_ACTIVE_ROOT_MIGRATION01\attempt_01`;
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_MANIFEST.json`;
   - `D:\Skyguard52\Saved\Reports\PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_EMERGENCY_RECEIPT.jsonl`.
8. Run:
   `python D:\Skyguard52\Scripts\verify_phase4_m01_recovery05_active_plugin_root_migration01_offline.py`
9. Require `PASS`.
10. Parse the migration and rollback supervisors under Windows PowerShell 5.1 and require zero parser errors.

If any preflight condition fails, create no namespace, perform no move, freeze the failure as `FAILED_WITH_EVIDENCE`, and stop.

## Single migration

Launch the frozen migration supervisor exactly once.

It must:

1. Create one fresh attempt namespace.
2. Create one fresh quarantine root outside `D:\Skyguard52\Plugins`.
3. Move exactly these complete directories, in order:
   - `SkyguardRecovery03NativeRecovery01`;
   - `SkyguardRecovery03NativeRecovery04`;
   - `SkyguardRecovery03`.
4. Use atomic `System.IO.Directory.Move` operations only.
5. Preserve every filename, byte count, and SHA-256.
6. Never copy, delete, overwrite, merge, or retry.
7. Automatically roll back completed moves in reverse order if a later move or validation fails.
8. Leave only:
   `D:\Skyguard52\Plugins\SkyguardRecovery03NativeRecovery05`
   in Unreal’s active plugin-discovery root.
9. Verify the selected plugin remains disabled by default.
10. Write terminal evidence on every outcome.

Do not run the separate rollback supervisor unless a later prompt explicitly authorizes it.

## Postflight

If the supervisor succeeds:

1. Require numeric `System.Int32` exit code `0`.
2. Require exactly three directory moves and zero retries.
3. Verify all 18 quarantined file hashes.
4. Verify all five selected Recovery05 file hashes at their original active path.
5. Verify the active plugin-discovery set contains exactly one root and one unique module/ModuleRules identity:
   `SkyguardRecovery03NativeRecovery05`.
6. Verify zero deletion, overwrite, merge, or copy operations.
7. Verify no project source, Config, `.uproject`, plugin file, isolated build output, or prior evidence changed.
8. Verify no UnrealEditor, Blender, build, compiler, linker, or capture process launched.
9. Create:
   - terminal migration manifest;
   - complete post-migration inventory;
   - active discovery-set report;
   - immutable terminal freeze;
   - Phase 1–8 audit, dashboard, and Mission 1 matrix addenda;
   - exact separate next prompt for the Recovery05 plugin BuildPlugin gate.

Classify exactly:

`PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION`

If the supervisor fails:

1. Preserve all evidence.
2. Verify the automatic rollback result.
3. Never retry.
4. Do not invoke the separate rollback supervisor automatically.
5. Classify exactly:
   `FAILED_WITH_EVIDENCE`.
6. Stop.

Do not build the Recovery05 plugin, launch UnrealEditor or Blender, bind runtime assets, capture, profile, integrate, promote, or package during this gate.

Stop after immutable terminal classification and creation of the next separate prompt.
