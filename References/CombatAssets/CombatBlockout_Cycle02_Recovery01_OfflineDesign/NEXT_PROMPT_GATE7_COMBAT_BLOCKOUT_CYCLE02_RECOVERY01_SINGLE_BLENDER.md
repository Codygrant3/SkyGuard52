Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`.

Treat the following as immutable:

- Cycle02 freeze:
  `D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_FREEZE.json`
- failed Blender Attempt01 freeze:
  `D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_ATTEMPT01_TERMINAL_FREEZE.json`
- Recovery01 offline-design freeze:
  `D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_OFFLINE_DESIGN_FREEZE.json`

Required Recovery01 readiness:

`PASSED_READY_FOR_EXPLICIT_SINGLE_BLENDER_RECOVERY01_AUTHORIZATION`

Frozen Recovery01 source authority:

`D:\Skyguard52\References\CombatAssets\CombatBlockout_Cycle02_Recovery01_OfflineDesign\source\blender_gate7_combat_blockout_cycle02_recovery01_attempt01.py`

- bytes: `19609`
- SHA-256:
  `40b3997ebc6075e702ee659722a90503320e019dc13af3c5d5bec67d67f79a71`

Authorize exactly one Blender execution using:

`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe --background --factory-startup --python D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01\attempt_01\source\blender_gate7_combat_blockout_cycle02_recovery01_attempt01.py -- --output D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01`

Before launch, verify every frozen hash, confirm the failed Attempt01 and its empty output namespace remain unchanged, confirm Recovery01 namespaces are absent, and confirm no Unreal, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler or linker process is active.

Create the fresh Recovery01 attempt namespace and copy only the frozen Recovery01 source and contract into it.

Launch Blender exactly once. Run no other heavy process. Never retry automatically and never reuse a failed namespace.

Do not trust Blender's process exit code by itself. Require:

- no Python traceback in stderr;
- Blender terminal receipt;
- dimension and artifact receipt;
- one `.blend`;
- five individual GLBs;
- five 1024x1024 PNG renders;
- exact authoritative 9K38, Shahed and rail dimension validation;
- hashes for every output.

If anything fails or is absent, preserve the attempt and classify:

`FAILED_WITH_EVIDENCE`

If automatic checks pass, inspect all five renders directly at full resolution and classify each:

- `PASSED_PROVISIONAL_BLOCKOUT`;
- `FAILED_WITH_EVIDENCE`; or
- `AWAITING_VISUAL_REVIEW`.

Do not import into Unreal, modify accepted runtime assets, invoke external AI models, or claim production acceptance.

Stop after immutable Recovery01 terminal classification and creation of the next Unreal-independent refinement prompt.
