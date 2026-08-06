Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`. Do not use the retired Three.js project, external models, or subagents.

Treat every Recovery01–04 artifact and the Recovery05 offline-design freeze as immutable.

Use the Recovery05 offline-design freeze named by the latest readiness record as the sole authority. Verify its SHA-256 and every recorded file hash before making any change.

## Authorization

Authorize exactly one bounded, offline Mission 1 environment-source correction.

Do not launch UnrealEditor, Blender, ShaderCompileWorker, AutomationTool, UnrealBuildTool, a compiler, linker, BuildPlugin, capture, profiling, gameplay, integration, promotion, or packaging.

Do not modify the Recovery05 plugin during this gate.

## Target

The only mutable project file is:

`D:\Skyguard52\Source\Skyguard52\SkyguardMission01EnvironmentDirector.cpp`

Required frozen pre-correction authority:

- bytes: `14984`
- SHA-256:
  `7cb7dae93bce8c2b0ff3f1eca45ce84cb5f74194f4e38a1ed02bb07c55262980`

Authorized patch:

`D:\Skyguard52\SourceCorrections\Recovery05\SkyguardMission01EnvironmentDirector.mobility.patch`

## Exact permitted correction

Insert exactly:

`Root->SetMobility(EComponentMobility::Static);`

immediately after:

`Root = CreateDefaultSubobject<USceneComponent>(TEXT("Mission01EnvironmentRoot"));`

and before:

`SetRootComponent(Root);`

No other source line, whitespace outside the insertion location, literal, condition, include, declaration, function, asset, map, configuration, plugin, or test may change.

## Preflight

1. Verify every Recovery05 freeze hash.
2. Verify the target source still has the required byte count and SHA-256.
3. Verify the patch hash recorded in the Recovery05 freeze.
4. Verify the installed UE 5.8 `SceneComponent.cpp` mobility authority remains unchanged.
5. Verify no heavy process is active.
6. Verify no future correction-attempt or build namespace exists.
7. Create an immutable pre-correction copy in a fresh Recovery05 correction-attempt namespace.
8. Hash the pre-correction copy and require exact parity with the target.

If any preflight condition fails, do not modify the target. Freeze the failure and classify `FAILED_WITH_EVIDENCE`.

## Application

1. Apply the frozen patch exactly once.
2. Never retry automatically.
3. Do not use a fuzzy or three-way patch.
4. Require the exact expected context.
5. Preserve the original line endings and encoding.
6. Record the patch tool, numeric exit code, and stdout/stderr.

## Post-application validation

1. Require exactly one added source line and zero removed or otherwise changed lines.
2. Require the added line to match the authorized statement byte-for-byte.
3. Verify it appears between root creation and `SetRootComponent`.
4. Verify `OceanTiles`, `BeachTiles`, and `LandTiles` still attach to the same root.
5. Verify `ConfigureInstanceComponent` still makes the tile components static.
6. Verify every Recovery05 plugin and Recovery01–04 authority hash remains unchanged.
7. Run syntax-neutral static source tests only; do not invoke a compiler or UBT.
8. Confirm no Unreal, Blender, build, capture, integration, or packaging process ran.

## Success evidence

If validation passes, create:

- immutable pre/post source inventory;
- exact one-line diff report;
- correction receipt;
- focused static-test result;
- readiness record;
- immutable correction freeze;
- exact separate prompt for one future project native-build validation.

The future native-build prompt must use one fresh build namespace, one heavy process, exactly one launch, zero retries, and must not launch UnrealEditor.

## Classification

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_M01_ENVIRONMENT_NATIVE_BUILD_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not compile during this gate.

Stop after immutable source-correction classification and creation of the separate one-shot project-build prompt.
