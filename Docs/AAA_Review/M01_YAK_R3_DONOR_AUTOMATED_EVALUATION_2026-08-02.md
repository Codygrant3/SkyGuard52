# M01 Yak R3 Donor Automated Evaluation — 2026-08-02

## Outcome

The ten approved R3 donor meshes now have a quarantined Unreal evaluation rig.
It is a transient actor, is not referenced by a runtime map, and never replaces
`ASkyguardYak52Aircraft`.

The rig binds only the governed donor set:

- cowling shell;
- cowling front ring;
- cowling shutters;
- cowling inlet cone;
- spinner;
- two propeller blades;
- two main wheel wells;
- nose wheel well.

It also reproduces the governed rear-gunner eye/target and the four contract
volumes for camera clearance, pilot safety, rifle muzzle sweep, and Igla
backblast.

## Automated evidence

Current editor source compiled successfully.

Fresh focused attempt:

`D:\Skyguard52\Saved\BuildAttempts\YAK_R3_AND_SORTIE_PRESENTATION\attempt_20260802T115147040Z`

Native automation:

- `Skyguard52.Yak.R3DonorEvaluation.AssetPivotMaterialAndCollisionContract`:
  success;
- `Skyguard52.Yak.R3DonorEvaluation.CameraPilotRifleAndIglaClearanceContract`:
  success;
- zero fatal, assert, ensure, GPU-timeout, or automation-failure signatures.

The tests verify:

- exactly ten quarantine assets load;
- each mesh bounds origin matches its governed pivot datum;
- every mesh has a material slot;
- every mesh has simple collision;
- evaluation collision is `QueryAndPhysics`;
- no donor bounds intersect the four safety/clearance volumes;
- the physical rear-gunner sightline remains level and unobstructed.

Four static contract tests also pass.

## Acceptance boundary

This is automated component compatibility evidence, not manual visual
promotion. Before any donor replaces an L88 runtime component, the remaining
gate still requires:

- matched before/after rendered images;
- visible scale and material review;
- ADS, rifle, Igla, pilot-safety, animation, and frame-time evidence;
- explicit human promotion approval.
