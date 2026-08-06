Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`.
Do not use the retired Three.js project, external models, or subagents.

Treat every prior Recovery01, Recovery02, Recovery03, and Native Build Attempt01
artifact as immutable. Treat the Recovery03 Native Build Recovery01 offline
freeze and its SHA-256 as the sole new authority.

Authorize exactly one native plugin build for
`Plugins/SkyguardRecovery03NativeRecovery01` by running:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\build_skyguard_recovery03_native_recovery01_once.ps1`

Before launch, verify every frozen hash, the installed UE 5.8 authority, absence
of `D:\SG52R03B02`, absence of the Recovery01 build/runtime namespaces, and zero
heavy processes. Launch no UnrealEditor or Blender process.

The supervisor must invoke the frozen native `AutomationTool.exe` directly,
use `D:\SG52R03B02`, retain the process object, preserve stdout/stderr and
process-tree evidence, and persist a numeric `System.Int32` exit code. Run once,
never retry, and never reuse a failed namespace.

If the build fails or the exit code is null, freeze the attempt and classify
`FAILED_WITH_EVIDENCE`.

If it succeeds, verify and hash-freeze the DLL, PDB, module receipt, descriptor,
source, package outputs, rebound project-plugin binaries, manifest, logs, and
process evidence. Rerun all offline lifecycle, path-length, and exit-code tests.
Confirm the plugin remains disabled by default and all governed Unreal runtime
namespaces remain absent.

Classify exactly:

- `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY01_UNREAL_AUTHORIZATION`; or
- `FAILED_WITH_EVIDENCE`.

Do not launch Unreal, capture images, promote, integrate, or package. If passed,
produce but do not execute the exact one-shot Unreal proof prompt. Stop after
the immutable build classification.
