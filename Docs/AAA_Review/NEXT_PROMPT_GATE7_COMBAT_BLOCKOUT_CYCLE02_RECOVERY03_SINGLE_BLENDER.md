Resume only the existing Unreal Engine 5.8/Blender AAA project at `D:\Skyguard52`. Do not use Three.js, external models, or subagents.

Treat Cycle02 Attempt01 and Recovery01–02 attempts as immutable and terminal. Never rerun or reuse them.

Treat this Recovery03 offline-design freeze as the sole new execution authority:

- File:
  `D:\Skyguard52\Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_OFFLINE_DESIGN_FREEZE.json`
- SHA-256:
  `1dd5b0660467dbd8d9fabee4da79f5a8d77a9b040b447c35c87c78286e2c73ef`
- Required classification:
  `PASSED_READY_FOR_EXPLICIT_SINGLE_BLENDER_RECOVERY03_AUTHORIZATION`

Do not edit any frozen member.

## Authorization

Authorize exactly one Recovery03 Blender execution:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\invoke_gate7_combat_blockout_cycle02_recovery03_once.ps1 -AuthorizeSingleBlender`

Run no UnrealEditor, Blender MCP, ShaderCompileWorker, AutomationTool, UnrealBuildTool, compiler, linker, import, integration, profiling, promotion, or packaging process concurrently.

Never retry and never reuse a failed namespace.

## Preflight

Before launching:

1. Verify the Recovery03 freeze and every member’s byte count and SHA-256 using the frozen self-contained .NET implementation.
2. Verify every earlier authority and failed attempt remains unchanged.
3. Verify Blender 5.2:
   - `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`
   - bytes: `112975320`;
   - SHA-256:
     `e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7`.
4. Confirm no heavy process is active.
5. Confirm these namespaces are absent:
   - `D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03\attempt_01`;
   - `D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01`;
   - `D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json`;
   - `D:\Skyguard52\Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_EMERGENCY_RECEIPT.jsonl`.
6. Run:
   `python D:\Skyguard52\Scripts\verify_gate7_combat_blockout_cycle02_recovery03_offline.py`
7. Require `PASS`.
8. Parse the supervisor under Windows PowerShell 5.1.
9. Require exactly one Blender `Start-Process` and zero retries.
10. Confirm native-handle retention occurs immediately after launch and before polling.
11. Confirm exit handling follows:
    - `WaitForExit`;
    - `Refresh`;
    - local exit-code capture;
    - null rejection;
    - `System.Int32` validation;
    - value and type persistence.
12. Confirm the Recovery03 Blender source differs from Recovery02 only by its gate identity and retains `BLENDER_EEVEE`.

If preflight fails, launch nothing, freeze `FAILED_WITH_EVIDENCE`, and stop.

## Single execution

The supervisor must launch Blender exactly once with the governed equivalent of:

`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe --background --factory-startup --python D:\Skyguard52\Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03\attempt_01\source\blender_gate7_combat_blockout_cycle02_recovery03_attempt01.py -- --output D:\Skyguard52\Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01`

Preserve:

- retained process and native handle;
- exact executable and arguments;
- PID and process-tree samples;
- timestamps and timeout;
- numeric exit code and `System.Int32` type;
- stdout and stderr;
- launch and retry counts;
- terminal and emergency evidence;
- complete output inventory.

Do not infer the exit code from logs, receipts, files, or process disappearance.

## Required outputs

Require exactly:

- one `.blend`;
- five `.glb` files;
- five 1024×1024 PNGs;
- `dimension_and_artifact_receipt.json`;
- `terminal_receipt.json`;
- hashes for every artifact.

Require the five frozen provisional collections and dimensional authorities.

Reject:

- null, nonnumeric, non-`System.Int32`, or nonzero exit code;
- Python traceback or Blender error;
- missing or extra output;
- invalid receipt;
- empty or hash-mismatched artifact;
- unsupported final-asset identity claim.

## Visual review

Only after automatic validation passes, inspect all five original renders at full resolution.

For each asset evaluate silhouette, proportions, dimensional plausibility, disconnected geometry, intersections, hierarchy, pivots, refinement suitability, and provisional labeling.

Classify each:

- `PASSED_PROVISIONAL_BLOCKOUT`;
- `AWAITING_VISUAL_REVIEW`; or
- `FAILED_WITH_EVIDENCE`.

## Terminal classification

On any failure:

1. Preserve the attempt and output unchanged.
2. Hash all evidence.
3. Confirm launch and retry counts.
4. Create an immutable terminal freeze.
5. Classify `FAILED_WITH_EVIDENCE`.
6. Stop without retrying.

If automatic and visual validation pass:

1. Create postflight, inventory, dimension, and visual-review evidence.
2. Create an immutable execution freeze.
3. Classify:
   `PASSED_RECOVERY03_PROVISIONAL_BLOCKOUTS_ACCEPTED`.
4. Create a separate Unreal-independent refinement-design prompt.

Do not import into Unreal, replace runtime assets, or claim final AAA hero-asset acceptance.

Stop after immutable terminal classification.
