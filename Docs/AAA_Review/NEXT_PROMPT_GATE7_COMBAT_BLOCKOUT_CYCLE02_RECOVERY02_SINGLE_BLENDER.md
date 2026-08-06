Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use Three.js, external models, or subagents.

Treat the original Cycle02 Attempt01, Recovery01 Attempt01, and every prior failed namespace as immutable and terminal.

Treat this Recovery02 offline-design freeze as the sole new execution authority:

- File:
  `D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_OFFLINE_DESIGN_FREEZE.json`
- SHA-256:
  `211d30e6167dc735cdf5489a413e0cd27d7311b64a2b2f2f2e7f8ce5d6b2da5b`
- Required classification:
  `PASSED_READY_FOR_EXPLICIT_SINGLE_BLENDER_RECOVERY02_AUTHORIZATION`

Do not edit any file recorded in that freeze.

## Authorization

Authorize exactly one Recovery02 Blender execution by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\invoke_gate7_combat_blockout_cycle02_recovery02_once.ps1 -AuthorizeSingleBlender`

Run no UnrealEditor, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler, linker, import, profiling, integration, promotion, or packaging process concurrently.

Never retry automatically and never reuse a failed namespace.

## Preflight

Before launching:

1. Verify the Recovery02 freeze and every member’s byte count and SHA-256 using the frozen self-contained .NET hashing implementation.
2. Verify every original Cycle02 and Recovery01 authority remains unchanged.
3. Verify the Blender 5.2 executable remains:
   - `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`
   - bytes: `112975320`;
   - SHA-256:
     `e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7`;
   - version: `5.2`.
4. Confirm no Blender, UnrealEditor, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler, linker, or other heavy process is active.
5. Confirm these governed namespaces are absent:
   - `D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02\attempt_01`;
   - `D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01`;
   - `D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_TERMINAL_SUPERVISOR_MANIFEST.json`;
   - `D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_EMERGENCY_RECEIPT.jsonl`.
6. Rerun:
   `python D:\Skyguard52\Scripts\verify_gate7_combat_blockout_cycle02_recovery02_offline.py`
7. Require `PASS`.
8. Parse the supervisor under Windows PowerShell 5.1 with zero syntax errors.
9. Require exactly one Blender `Start-Process`, zero retry paths, and no Unreal launch path.
10. Confirm the frozen Blender source differs from Recovery01 by only its Recovery02 gate identity and retains:
    `scene.render.engine = "BLENDER_EEVEE"`.

If any preflight condition fails, create no governed namespace, launch nothing, preserve evidence, classify `FAILED_WITH_EVIDENCE`, and stop.

## Single execution

The frozen supervisor must launch Blender exactly once with the governed equivalent of:

`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe --background --factory-startup --python D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02\attempt_01\source\blender_gate7_combat_blockout_cycle02_recovery02_attempt01.py -- --output D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01`

Preserve:

- exact executable and argument array;
- working directory;
- PID and process-tree samples;
- start and end timestamps;
- timeout state;
- numeric exit code and its type;
- Blender launch count;
- retry count;
- stdout and stderr;
- complete output inventory;
- external terminal manifest;
- emergency receipt if required.

Do not treat exit code `0` alone as success.

## Required outputs

Require exactly:

- one governed `.blend`;
- five individual `.glb` files;
- five 1024×1024 PNG renders;
- `dimension_and_artifact_receipt.json`;
- `terminal_receipt.json`;
- complete SHA-256 hashes.

Require these five governed collections:

1. `PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON`
2. `PROVISIONAL_AR_M4_FAMILY_RIFLE_BLOCKOUT`
3. `PROVISIONAL_9K38_MISSILE_ENVELOPE`
4. `PROVISIONAL_REAR_GUNNER_HAND_FOREARM_MANNEQUIN`
5. `PROVISIONAL_SHAHED136_ENVELOPE`

Reject:

- Python tracebacks;
- Blender errors;
- missing or extra outputs;
- invalid JSON receipts;
- receipt identity mismatch;
- empty artifacts;
- artifact-hash mismatch;
- unsupported final-asset claims.

Verify:

- 9K38 length `1.574 m`;
- 9K38 diameter `0.072 m`;
- Shahed-136 length `3.3 m`;
- Shahed-136 wingspan `3.0 m`;
- frozen MIL-STD-1913 coupon dimensions;
- hand/forearm remains explicitly provisional and not a measured percentile.

## Visual inspection

If automatic validation passes, inspect all five original PNG renders directly at full resolution.

For every asset assess:

- recognizable silhouette;
- dimensional plausibility;
- coherent proportions;
- disconnected or floating geometry;
- unintended intersections;
- useful hierarchy and pivots;
- suitability for refinement;
- honest provisional labeling.

Classify every asset as:

- `PASSED_PROVISIONAL_BLOCKOUT`;
- `AWAITING_VISUAL_REVIEW`; or
- `FAILED_WITH_EVIDENCE`.

Do not promote an asset solely because Blender returned exit code `0`.

## Terminal handling

On any failure:

1. Preserve the attempt and partial output unchanged.
2. Hash all available evidence.
3. Confirm exactly one or zero Blender launches, depending on the failure stage.
4. Confirm zero retries and zero Unreal launches.
5. Create an immutable terminal freeze.
6. Classify:
   `FAILED_WITH_EVIDENCE`.
7. Stop without retrying.

If automatic and direct visual validation pass:

1. Create the postflight validation, artifact inventory, dimension report, per-asset visual review, terminal manifest, and immutable execution freeze.
2. Classify:
   `PASSED_RECOVERY02_PROVISIONAL_BLOCKOUTS_ACCEPTED`.
3. Create a separate Unreal-independent refinement-design prompt.

Do not import assets into Unreal, replace runtime assets, begin ungoverned high-poly production, or claim final AAA hero-asset acceptance.

Stop after immutable terminal classification and creation of the next offline refinement prompt only if passed.
