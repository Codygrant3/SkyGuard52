# Phase 4 M01 PCG/Landscape Serialized Acceptance

Date: 2026-08-02  
Scope: P4.4 serialized structural handoff only

## Result

P4.4 is structurally complete.

The project now contains:

- immutable map
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03`;
- governed graph
  `/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation`;
- one imported Landscape with a valid GUID and an exact 8×2 component grid;
- the exact governed transform, label, and tag;
- eight required PCG setting nodes and eight governed edges;
- one director with serialized Landscape/graph bindings;
- zero generated PCG components or instances;
- an empty licensed weighted-mesh selector;
- explicit generation and licensed-library authorization locks.

The source heightmap remains the deterministic 505×127 R16 file with SHA-256
`636044a61065e72ea18defad4e6893150c3cf9c274c6aa6b06584675f4db7b26`.

## Fresh-process evidence

Authoring attempt:

`D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_PCG_LANDSCAPE\attempt_20260802T134620627Z`

The attempt's first three stages passed:

1. UE 5.8 editor compile;
2. bounded NullRHI authoring;
3. independent fresh-process editor audit.

Canonical reports:

- `Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_BUILD.json`: `gate=PASS`;
- `Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_EDITOR_ACCEPTANCE.json`:
  `gate=PASS`;
- `Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_READINESS_AUDIT.json`:
  `gate=PASS`, `authoring_status=SERIALIZED_EDITOR_GATE_PASS`,
  `p4_4_complete=true`.

The authoring attempt's terminal receipt remained fail-closed because one
pre-authoring native regression still expected the governed graph not to
exist. The test was updated to require the newly serialized graph while still
requiring a transient world without the governed Landscape, approved library,
or authorization to remain generation-locked.

Post-authoring native regression:

`D:\Skyguard52\Saved\BuildAttempts\PHASE4_M01_PCG_LANDSCAPE_NATIVE_REGRESSION\attempt_20260802T134800Z`

- editor compile: succeeded;
- `Skyguard52.Environment.Mission01Production`: 3/3 succeeded;
- native test exit code: 0;
- fatal/assert/ensure/GPU-timeout signatures: 0;
- native log SHA-256:
  `8faa8b70a70bb11075ae11d778d44441f02d961d3362baf91a0d3d1c0435bafd`.

## Failed attempts retained

Two partial maps are deliberately retained as failed immutable evidence under
`Saved/Quarantine/Phase4FailedMaps/20260802`, outside Unreal's `Content`
discovery/cook boundary:

- `v5_attempt01`: failed before Landscape creation because the UE 5.8 import
  call lacked the required empty material-layer-info entry;
- `v5_attempt02`: created the Landscape but rejected a graph-output edge that
  used the ordinary `In` label rather than the graph output node's `Out`
  receiving label.

Neither partial map is promoted or referenced by the governed contract. Their
original hashes and paths are preserved in
`Saved/Quarantine/Phase4FailedMaps/20260802/QUARANTINE_MANIFEST.json`.

## What this does not prove

This acceptance does not prove:

- licensed vegetation acquisition;
- generated or baked PCG instances;
- Landscape material quality;
- shoreline/terrain seam quality;
- visible GPU performance;
- water, lighting, or final AAA visual acceptance.

Those remain separate P4.3, P4.5, P4.6, and P4.7 gates.
