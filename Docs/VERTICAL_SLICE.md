# Skyguard 52 Unreal Vertical Slice

## Status: GENERATED + EDITOR OPEN

Engine: **UE 5.8** (`D:\UE_5.8`)  
Project: `unreal/Skyguard52/Skyguard52.uproject`  
Map: `/Game/Skyguard/Maps/Lvl_SkyguardCoast`  
Editor: launched on the coast map

Plugins enabled:
- Fab
- Bridge
- PythonScriptPlugin
- ModelingToolsEditorMode
- GameplayStateTree

---

## What was generated automatically

### Map
- `Content/Skyguard/Maps/Lvl_SkyguardCoast.umap`
  - Ocean plane
  - Coastal land + beach ribbon
  - City block skyline
  - Coast road
  - Yak fuselage / wing / tail stand-in
  - Seed Shahed-like drones in approach lanes
  - Sun / sky light / fog
  - PlayerStart at rear-cockpit approx

### Materials
- `M_Ocean`, `M_Sand`, `M_Beach`, `M_CityConcrete`, `M_Road`
- `M_YakAirframe`, `M_ShahedDrone`, `M_CockpitInterior`, `M_RifleTan`

### Blueprint shells
- `BP_SkyguardGunner` (Character)
- `BP_ShahedDrone` (Actor)
- `BP_DroneSpawner` (Actor)
- `BP_SkyguardGameMode` (GameModeBase)
- `BP_SkyguardPlayerController`
- `BP_SkyguardHUD`

### Project defaults
- Startup map → `Lvl_SkyguardCoast`
- Default game mode → `BP_SkyguardGameMode`

### Generator script
`Scripts/build_skyguard_vertical_slice.py`  
(re-run anytime to rebuild procedural scene content)

---

## Play it now

1. Wait for Unreal Editor to finish loading the coast map.
2. Press **Play**.
3. You should see the coastal city + ocean + Yak stand-in + seed drones.

If map didn’t open automatically:
- Content Browser → `Skyguard/Maps/Lvl_SkyguardCoast` → double-click → Play

---

## Critical next authoring (in-editor, ~30–60 min)

Python created shells; gameplay graphs still need wiring.

### 1) `BP_SkyguardGunner`
- Add:
  - Camera (backseat eye height)
  - Rifle mesh (use cube/cylinder temporary, material `M_RifleTan`)
  - Optional hand mesh
- Inputs:
  - Mouse look (yaw/pitch clamp for open cockpit arc)
  - RMB = ADS (lerp camera + rifle to iron-sight pose)
  - LMB = fire (line trace 20k units, damage channel)
- No free walk; either:
  - disable movement input, or
  - attach pawn to Yak socket / fixed transform over wing root

### 2) `BP_ShahedDrone`
- Components: cone/cylinder body (`M_ShahedDrone`), collision, projectile movement or Tick move
- Move toward city (roughly toward -X / coast)
- Health 1 (standard) / 3 (heavy later)
- On destroy: spawn explosion emitter / destroy actor

### 3) `BP_DroneSpawner`
- Timer every 2–4s
- Spawn `BP_ShahedDrone` at far approach points over water
- Randomize altitude / lateral lane

### 4) `BP_SkyguardGameMode`
- Default Pawn = `BP_SkyguardGunner`
- Player Controller = `BP_SkyguardPlayerController`
- HUD = `BP_SkyguardHUD`

### 5) Fab / Bridge (light pull only)
Import 5–10 materials max for first realism pass:
- worn painted metal
- olive drab / grey airframe
- leather
- concrete / asphalt
- water

Do **not** bulk-import the library yet.

---

## Controls target

| Action | Input |
|---|---|
| Look | Mouse |
| ADS | Right Mouse |
| Fire rifle | Left Mouse |
| Snap port/starboard | A / D (optional) |
| Igla (later) | X |

---

## Regenerate scene

If you need a clean rebuild of procedural coast content:

```bat
"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "Skyguard52.uproject" -ExecutePythonScript="%CD%\Scripts\build_skyguard_vertical_slice.py" -unattended -NullRHI
```

Or in-editor: **Tools → Execute Python Script** → select the script.

---

## Relation to browser game
The web prototype remains Phase 2 green and playable.  
This Unreal slice is the native high-fidelity track.
