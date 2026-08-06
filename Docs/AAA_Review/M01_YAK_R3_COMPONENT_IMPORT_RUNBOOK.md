# Mission 01 Yak R3 component import runbook

## Purpose

Evaluate only ten R3 donor components in Unreal without replacing the L88
aircraft. The cockpit, pilot, rear gunner, rifle, Igla, fuselage, wings, tail,
and canopy remain L88-owned. This lane does not touch a runtime map or config.

## Preconditions

- Close Unreal Editor and Blender.
- Confirm no Unreal, UBT, UAT, shader-worker, UBA, or Blender process is active.
- Keep the quarantine destination empty:
  `/Game/Skyguard/Quarantine/M01/YakR3ComponentEval`.
- Do not delete a partial quarantine manually until its attempt logs have been
  reviewed. A non-empty destination makes the gate stop instead of overwriting.

## Serialized root-only gate

```powershell
powershell -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\run_m01_yak_r3_component_quarantine_gate.ps1
```

The runner performs an offline hash and GLB audit, then starts one hidden
`UnrealEditor-Cmd` import process. Only after it exits does a new process audit
persistence. It does not run Blender, UBT, UAT, maps, automation, or packaging.
If a stage remains active after the supervisor window, wait for that exact PID;
never launch a duplicate.

## Pass meaning

`PASS_QUARANTINE_IMPORT_PERSISTED_NOT_PROMOTABLE` means only:

- the ten donor static meshes persisted in quarantine;
- non-whitelisted static meshes and unsafe imported classes are absent;
- source/build/quarantine metadata persisted;
- canonical pivot and safety/camera reference JSON persisted as metadata on
  every approved donor mesh, without creating an abstract DataAsset;
- no runtime map or config mutation was requested.

It is not a visual, gameplay, AAA, or production acceptance.

## Promotion evidence

Copy
`Docs/AAA_Review/M01_YAK_R3_COMPONENT_EVALUATION_TEMPLATE.json` to
`Saved/Reports/M01_YAK_R3_COMPONENT_EVALUATION.json`. For every donor component,
record hash-bound evidence for pivot transform, material slots, collision,
rear-gunner camera visibility, and all relevant safety clearances. The global
record also requires camera, pilot no-fire, rifle muzzle, Igla backblast,
matched before/after images, and the fresh-process persistence report.

Validate a completed record offline:

```powershell
python D:\Skyguard52\Scripts\audit_m01_yak_r3_component_import_source.py --evaluation D:\Skyguard52\Saved\Reports\M01_YAK_R3_COMPONENT_EVALUATION.json --no-write
```

Even a complete record returns only `READY_FOR_MANUAL_PROMOTION_REVIEW`.
Promotion remains a separate, human-reviewed change.
