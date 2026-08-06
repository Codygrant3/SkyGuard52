Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every prior Gate 2, Recovery01-04, migration, and failed namespace as immutable and terminal.

Treat this offline-design freeze as the sole new authority:

- `D:\Skyguard52\Docs\AAA_Review\PHASE4_M01_RECOVERY05_BUILDPLUGIN01_OFFLINE_DESIGN_FREEZE.json`
- Required classification: `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY05_BUILDPLUGIN_AUTHORIZATION`

I explicitly authorize exactly one Recovery05 BuildPlugin execution by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_phase4_m01_recovery05_buildplugin01_once.ps1 -AuthorizeSingleBuild`

Before launching, verify the freeze and every recorded member, all 5 active and 18 quarantined plugin records, the Recovery04 project-build freeze and isolated binaries, disabled-by-default state, unique Recovery05 plugin/module/ModuleRules identities, zero heavy processes, and absence of all future namespaces.

The supervisor must launch bundled .NET 10 exactly once with `AutomationTool.dll` as its first argument, followed by `BuildPlugin`, the frozen Recovery05 descriptor, `D:\SG52R05P01`, Win64, Rocket, StrictIncludes, and NoP4. Never use AutomationTool.exe, RunUAT.bat, cmd.exe, system dotnet, a wrapper, an automatic retry, a reused namespace, copy-back, UnrealEditor, or Blender.

Preserve the attempt, stdout, stderr, exact process evidence, numeric exit code and type, terminal manifest, emergency receipt if needed, complete package inventory, and source parity.

On failure, freeze the single attempt and classify `FAILED_WITH_EVIDENCE`; stop without retrying.

On success, require numeric `System.Int32` exit code 0 and validate/hash the packaged DLL, PDB, `UnrealEditor.modules`, descriptor, Build.cs, complete source, receipts, logs, and source parity. Verify one supervisor launch, one bundled-dotnet launch, one AutomationTool invocation, zero retries, zero engine/Blender launches, disabled-by-default state, and no mutation of active or quarantined plugin authorities.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_RECOVERY05_RUNTIME_BINDING_DESIGN`; or
- `FAILED_WITH_EVIDENCE`.

Do not launch UnrealEditor, capture, integrate, promote, or package the game. Stop after immutable BuildPlugin classification and creation of the separate next offline runtime-binding design prompt.
