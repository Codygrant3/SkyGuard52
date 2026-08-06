# Skyguard 52 — Mission 9 Playable Integration v1

Status: `SOURCE_ONLY_NOT_RUN`

The existing
`/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1`
remains the preserved assembly. The candidate builder duplicates it to the
separate:

`/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Playable_v1`

Neither `Config/DefaultGame.ini` nor
`Docs/AAA_Review/PHASE8_MISSION_SOAK_MATRIX.json` belongs to this integration.

## Playable contract

- Four-point, 90 km Unreal-unit metropolitan approach with a 25 km-plus lateral
  canyon signature, dense skyline, power station, major bridge and rooftop
  relay roles.
- Three protected targets: metropolitan skyline, coastal power station and
  major bridge. At least two must survive.
- Three deterministic saturation waves of 8, 12 and 16 logical threats.
- Logical threats reserve and recycle through a 48-entry pool; active threats
  never exceed 24 and the authored waves peak at 16.
- Decoys are capped at 12, simultaneous explosions at 6, each dispenser at six
  releases, and Iron Rain defeat breakup at three pre-authored pieces.
- The composed map disables director-owned runtime actor spawning.

## Iron Rain encounter

1. Three exposed dispenser bays release only bounded, pooled escorts. Rifle
   fire destroys each bay and completes the three relay milestones.
2. Two command antennae become exposed after the bays are destroyed.
3. Destroying both antennae exposes the decoy controller.
4. After the decoy controller is destroyed, the pilot must execute explicit
   `Climb` and `Cross` commands. These propagate to the current Yak command
   vocabulary as `Extend` and `OrbitRight`.
5. The cross exposes three upper engine pods and enables the first Igla lock.
6. After one engine pod is destroyed, the player chooses:

   - a second Igla strike that disables both remaining exposed pods; or
   - a difficult `Break` pass exposing two rifle-only fuel-control units.

7. Either finish deterministically defeats Iron Rain. Only the three registered
   breakup components can detach.

## Deterministic outcomes

Success requires all three waves cleared, Iron Rain defeated, and at least two
protected infrastructure targets surviving. Destruction of any two protected
targets immediately fails `ProtectCityInfrastructure`; later boss damage cannot
reverse that terminal state.

## Four focused automation tests

- `Skyguard52.Mission09.Integration.GovernedContractEscalationAndPoolBounds`
- `Skyguard52.Mission09.IronRain.DispensersClimbCrossAndSecondIgla`
- `Skyguard52.Mission09.IronRain.DifficultRifleFuelControlFinish`
- `Skyguard52.Mission09.Integration.DeterministicSuccessAndInfrastructureFailure`

## Offline source audit

This command launches no Unreal tooling:

```powershell
python D:\Skyguard52\Scripts\audit_skyguard_m09_playable_source.py
```

## Root-only serialized gate

Only the root build supervisor may run the heavy gate, and only while the
shared Unreal lane is idle:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_m09_playable_integration_gate_root_only.ps1 `
  -RootAuthorized
```

The supervisor performs source audit, editor build, candidate composition,
fresh-process persistence audit and exactly four Mission 09 tests. It does not
package, edit map-cook configuration, or alter the soak matrix.

## Honest limitations

This source package has not been compiled or executed by its authoring task.
The skyline, power station, bridge and Iron Rain body use existing proxy art.
Native state tests cannot prove rendering, controls, player experience,
frame-time, streaming, cook or packaged stability. Performance safety here is
a deterministic allocation/count contract that still requires measured
runtime validation.
