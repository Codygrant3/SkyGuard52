# Next Prompt — Phase 4 Attempt08 Single Unreal Visual Proof

```text
Resume only `D:\Skyguard52`. Do not use the retired Three.js project,
external models, or subagents.

Treat
`Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_FREEZE.json`
as the immutable offline design authority.

Authorize exactly one Unreal execution of:

`P4.6-M01-REPRESENTATIVE-VISUAL-008`

Do not modify the frozen contract, cameras, rubrics, executor, verifier, tests,
source inventory, readiness record, maps, assets, project configuration,
Recovery04 evidence, accepted runtime assets, or Phase 8 baseline.

Before launch:

1. Verify every byte count and SHA-256 in the freeze and source inventory.
2. Rerun the seven focused offline tests.
3. Confirm these are absent:
   - `Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08/attempt_01`
   - its `proof` child.
4. Confirm no Unreal, Blender, ShaderCompileWorker, UnrealBuildTool,
   AutomationTool, RunUAT, or BuildCookRun process is active.
5. Confirm `D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe` exists.
6. Stop without launching if any preflight check fails.

Run one heavy process only. Create only the governed `attempt_01` parent and
its `logs` directory before launch; the Unreal executor must create the
previously absent `proof` child itself.

Launch exactly once with:

`D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`

Arguments:

- `D:\Skyguard52\Skyguard52.uproject`
- `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03`
- `-ExecutePythonScript=D:\Skyguard52\Scripts\capture_skyguard_phase4_m01_representative_visual_attempt08.py`
- `-SkyguardAttempt08OutputRoot=D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08\attempt_01\proof`
- `-unattended`
- `-nop4`
- `-NoSplash`
- `-RenderOffscreen`
- `-windowed`
- `-ResX=2560`
- `-ResY=1440`
- `-d3d12`
- `-sm6`
- `-NoVSync`
- `-stdout`
- `-FullStdOutLogOutput`
- `-csvCategories=Global`
- `-csvGpuStats`
- `-csvNamedEvents`
- `-csvCaptureFrames=7200`
- `-abslog=D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08\attempt_01\logs\representative_visual.engine.log`

Redirect process stdout and stderr directly to:

- `attempt_01\logs\representative_visual.stdout.log`
- `attempt_01\logs\representative_visual.stderr.log`

Supervise the PID for at most 420 seconds. Do not start another Unreal or
Blender process. If it times out or fails, preserve the entire attempt
unchanged, write terminal evidence, and stop. Never automatically retry or
reuse `attempt_01`.

The executor must:

- use deferred editor ticks;
- wait for two stable polls with all Landscape shader resources compiled and
  global shader/asset queues empty;
- perform at least 30 seconds of warmup before capturing;
- capture five fixed 2560x1440 static views and three tick-spaced route samples;
- collect at least 30 measured seconds and 900 frame samples;
- never force same-stack compilation;
- never save the world, mutate assets, generate PCG, use the network, promote,
  integrate, or package.

After process exit:

1. Preserve and hash stdout, stderr, engine log, receipt, frame CSV, every PNG,
   and any Unreal CSV profiler output created by this process.
2. Require an exit code of zero and receipt gate
   `PASS_CAPTURE_COMPLETE_PENDING_OFFLINE_ACCEPTANCE`.
3. Verify all eight PNGs at exactly 2560x1440.
4. Apply every automatic visual bound and every absolute performance/stability
   bound. Missing metrics fail closed.
5. Inspect all eight PNGs directly at full resolution.
6. Reject diagnostic blocks, floating/disconnected geometry, ungrounded
   buildings, obvious repetition, bad exposure, missing shore contact,
   low-poly hero silhouettes, unstable world elements, clipping, and traversal
   hitches.
7. Create a machine-readable gate report, immutable terminal manifest, and
   direct visual-review report.

Classify the attempt as:

- `PASSED_REPRESENTATIVE_VISUAL_PROOF_AWAITING_SEPARATE_INTEGRATION_DECISION`;
  or
- `FAILED_WITH_IMMUTABLE_EVIDENCE`.

Even on pass, do not promote, integrate, package, or claim Mission 1 or the AAA
build is complete. Update the Phase 1–8 audit and Mission 1 acceptance matrix,
then stop.
```
