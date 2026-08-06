# BLD-M01-YAK-PROD-002 Source Runbook

Status: source-only, not executed  
Blender authority: 5.2  
Runtime authority: none; this task does not import into Unreal

## Purpose

Refine the governed 001 construction direction in response to the three review
renders without promoting or importing the 001 `.blend`, GLB, mesh datablocks,
materials, or L88 geometry.

The 002 generator uses the 001 Python file only for clean helper functions such
as mesh construction, UV creation, material construction, and airfoil sampling.
Both the 001 helper source and L88 datum reference are hash-bound.

## Review corrections encoded

- Yak-52-specific radial cowling shell, inlet ring, radial shutters, and inlet
  cone instead of a featureless drum.
- Shaped spinner and two thick, twisted, tapered propeller blades instead of a
  flat bar.
- Main and nose gear, wheels, wells, struts, and separate doors.
- Multi-station tapered fuselage with an open cockpit crown and a narrow tail
  cone.
- Wing-root and tailplane intersection fairings.
- Curved Yak-oriented vertical-fin and rudder profiles.
- Canopy rails, bows, and glass sharing the fuselage longeron height.
- Rear cockpit with floor, tapered sidewalls, bulkheads, shaped panel, coaming,
  eleven-gauge cluster, structural seat, cushion, harness, stick, throttle,
  trim wheel, and pedals.
- Panel-line and rivet decal-ready material slots, IDs, UV metadata, and
  separate movable-part pivot roles.

## Source-only preflight

```powershell
Set-Location D:\Skyguard52
py -3 Scripts\verify_bld_m01_yak_prod_002.py
py -3 -m unittest Scripts.tests.test_bld_m01_yak_prod_002
```

Expected:

- source verifier `gate=PASS`;
- `artifact_gate=NOT_RUN`;
- no Blender process;
- all tests pass.

## Exact serialized Blender command

Root may execute this only after the current heavyweight owner exits and the
supervisor confirms no Unreal, UBT, UAT, ShaderCompileWorker, packaging, or
Blender process is active:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background `
  --factory-startup `
  --python 'D:\Skyguard52\Scripts\blender_bld_m01_yak_prod_002.py'
```

The supervisor must redirect stdout/stderr to an attempt-specific directory,
record the PID and descendants, enforce a hard deadline, write an explicit
terminal state, and clean up only its own process tree.

## Isolated outputs

- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Production_002/BLD_M01_YAK_PROD_002_MASTER.blend`
- `Content/Skyguard/Meshes/Source/Mission01/Yak52_Production_002/bld_m01_yak_prod_002.glb`
- `Saved/Reports/BLD_M01_YAK_PROD_002_MANIFEST.json`

No 001 or L88 source/output is overwritten.

## Post-build offline artifact verification

```powershell
py -3 Scripts\verify_bld_m01_yak_prod_002.py `
  --artifact-manifest Saved\Reports\BLD_M01_YAK_PROD_002_MANIFEST.json
```

The artifact verifier rejects wrong version, source/reference drift, tampered
outputs, missing gear/cowling/cockpit parts, absent UV/material slots,
insufficient governed topology, dimension drift, forbidden names, incomplete
movable pivots, missing panel-line/rivet metadata, and any false final claim.

## Required manual review before any Unreal task

1. Render the same three views with matched focal length and framing.
2. Confirm the cowling reads as a radial Yak-52 nose rather than a cylinder.
3. Confirm propeller blade planform, thickness, twist, spinner, and pivot.
4. Inspect gear stance, wheel scale, wheel-well placement, and retraction
   clearances.
5. Confirm fuselage taper and wing/tail intersections from side and
   three-quarter views.
6. Confirm vertical-tail/rudder outline against the reference board.
7. Inspect canopy-to-longeron continuity and rear sliding travel.
8. Inspect from `SOCKET_CameraRearGunner`; the seat/back, sidewalls, panel,
   gauges, stick, throttle, trim wheel, and pedals must read as a cockpit.
9. Verify panel/rivet material IDs and movable-part pivots.

Even after offline and manual review passes, 002 remains a
production-direction refinement candidate. Unreal import, visible mission
review, performance acceptance, and AAA promotion are separate future gates.
