# Next Gate: Recovery04 Runtime Binding Offline Design

```text
Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every prior Recovery01–04 source, build, package, preflight, and terminal artifact as immutable.

Treat these artifacts as authority:

- `Docs/AAA_Review/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY04_NATIVE_BUILD_FREEZE.json`
- `Saved/Reports/PHASE4_M01_RECOVERY04_UNREAL_EXECUTION_PREFLIGHT_TERMINAL.json`
- `Docs/AAA_Review/PHASE4_M01_RECOVERY04_UNREAL_EXECUTION_PREFLIGHT_TERMINAL_FREEZE.json`

Perform exactly one offline-only Recovery04 runtime-binding and launcher-design gate.

Do not launch Unreal, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, a compiler, capture, profiling, integration, promotion, or packaging.

Objective:

Create and hash-freeze a new Recovery04 execution binding around the already accepted binary without modifying or rebuilding that binary. The binding must honestly preserve and use the binary’s immutable inherited values:

- module: `SkyguardRecovery03NativeRecovery01`
- switches:
  - `SkyguardRecovery01ContractId`
  - `SkyguardRecovery01Authorization`
  - `SkyguardRecovery01ExpectedMap`
  - `SkyguardRecovery01AttemptRoot`
- contract:
  `P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01`
- authorization:
  `P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01-ONE-SHOT`
- required attempt suffix:
  `Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01/runtime_attempt_01`

The binding must identify the execution as Recovery04 provenance while never changing those binary-enforced values.

Before creating artifacts:

1. Verify every hash in the accepted Recovery04 native-build freeze and the new preflight terminal freeze.
2. Verify the accepted DLL, PDB, module receipt, descriptor, source, map, material, cameras, visual rubric, and performance rubric.
3. Confirm the source plugin remains disabled by default.
4. Confirm the accepted DLL hash remains:
   `2070765a5d44199f7116c2038c97d866b91a509706de73953ead1cad057cb6e3`
5. Confirm all proposed runtime, launcher, proof, and execution-preflight namespaces are absent.
6. Confirm no heavy process is active.

Create only fresh versioned offline artifacts:

- Recovery04 runtime-binding contract;
- exact one-shot PowerShell launcher;
- execution-preflight schema;
- postflight verifier;
- visual-inspection checklist;
- source inventory;
- readiness record;
- immutable hash freeze;
- exact separate prompt for one future Recovery04 Unreal execution.

The launcher must:

- enable only `SkyguardRecovery03NativeRecovery04`;
- explicitly disable the earlier plugins that could provide duplicate module identities;
- use UE 5.8 `UnrealEditor-Cmd.exe`;
- use D3D12 SM6;
- pass the exact immutable Recovery01 switches and tokens;
- target the exact required Recovery01 runtime-attempt suffix;
- preserve Recovery04 provenance in its launcher, preflight, and terminal evidence;
- verify all frozen hashes before namespace creation;
- create exactly one launcher namespace and one runtime namespace;
- retain one `Start-Process -PassThru` process object;
- record numeric exit code and type;
- use one launch and zero retries;
- write a terminal supervisor receipt on every outcome;
- apply the frozen network controls;
- never save the world;
- never launch a second process.

The verifier must require:

- terminal receipt before shutdown;
- lifecycle heartbeat;
- capture and restoration receipts;
- at least 900 frame samples;
- exactly eight 2560×1440 PNGs;
- five static and three temporal camera IDs;
- source/map/material hash parity;
- original material restoration;
- zero world saves;
- zero network attempts;
- all frozen visual, performance, log, timeout, and stability bounds.

Validate JSON, Python, and Windows PowerShell 5.1 syntax. Run only harmless offline tests. Verify exactly one Unreal launch path exists but do not execute it.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY04_UNREAL_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not spend the Unreal attempt during this gate. Stop after the immutable offline classification and, only if passed, creation of the separate one-shot Unreal execution prompt.
```
