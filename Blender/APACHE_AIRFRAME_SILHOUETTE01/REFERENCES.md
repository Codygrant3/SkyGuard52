# AH-64 airframe silhouette — public layout only

Namespace: `Blender/APACHE_AIRFRAME_SILHOUETTE01`  
State: `source_candidate` — not accepted runtime art.

Stylized silhouette for helicopter distance. No classified internals,
no stencil copies, no unpublished dimensions.

## Live pawn scale (Unreal cm → Blender m)

Origin matches `ASkyguardApacheAircraft`. +X forward, +Z up.

| Socket | Meters |
| --- | --- |
| SO_FrontGunnerSeat | (1.68, 0.00, 1.18) |
| SO_RearPilotSeat | (0.48, 0.00, 1.18) |
| SO_FrontEye | (1.76, 0.00, 1.46) |
| SO_GunnerSensorTurret | (2.36, 0.00, 0.28) |
| SO_ChinWeapon | (2.70, 0.00, -0.48) |
| Main rotor disc | diameter 14.5 m at z = 2.58 |

## Public parts

HowStuffWorks diagram + user hangar / side photos (2026-08-14):

- Front CPG greenhouse, aft pilot greenhouse
- TADS ball + lens under the nose
- M230 hanging below the chin
- Stub wings, pylons, Hydra pods, Hellfire rails
- Twin engines, tail boom, tail rotor
- Main rotor + mast + Longbow-style dome
- Tricycle gear

## Review cameras

`side`, `three_quarter`, `front`, `cpg_down` (eye looking at TADS / M230).
