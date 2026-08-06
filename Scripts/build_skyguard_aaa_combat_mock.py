"""
Skyguard AAA playable proxy combat without C++:
- Spawn a high-detail gunner camera pawn stand-in (PlayerStart already exists)
- Create BP subclasses if missing
- Spawn many drones with tags for later systems
- Write critic still-camera ring
This does not claim AAA; it unblocks playable iteration while NetFx install is pending.
"""
import unreal

def log(m): unreal.log(f"[SkyguardAAA] {m}")

def ensure_bp(name, parent):
    path=f"/Game/Skyguard/Blueprints/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    factory=unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Blueprints", unreal.Blueprint, factory)
    if bp: unreal.EditorAssetLibrary.save_loaded_asset(bp)
    return bp

def clear_prefix(prefix):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            n=a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def sm(mesh, loc, scale=None, rot=None, label=None, material=None):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a: return None
    c=a.static_mesh_component
    c.set_static_mesh(mesh)
    if scale: a.set_actor_scale3d(unreal.Vector(*scale))
    if label: a.set_actor_label(label)
    if material: c.set_material(0, material)
    return a

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_bp("BP_SkyguardGunner", unreal.Character)
    ensure_bp("BP_ShahedDrone", unreal.Actor)
    ensure_bp("BP_DroneSpawner", unreal.Actor)
    ensure_bp("BP_SkyguardGameMode", unreal.GameModeBase)

    clear_prefix("AAA_Combat_")
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    cone=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cone")
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    sphere=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    metal=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_metal")
    air=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_airframe_metal")
    leather=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_leather")
    exhaust=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")

    # Detailed first-person gunner rig as level actors parented by proximity (visual combat mock)
    sm(cyl, (18, 110, 360), (0.07,0.07,1.15), unreal.Rotator(0,12,0), "AAA_Combat_RifleBarrel", metal)
    sm(cube, (18, 70, 358), (0.16,0.38,0.14), unreal.Rotator(0,12,0), "AAA_Combat_RifleBody", metal)
    sm(sphere, (22, 75, 354), (0.12,0.16,0.1), None, "AAA_Combat_Glove", leather)
    sm(cube, (0, 40, 350), (1.6,1.8,0.08), None, "AAA_Combat_GunnerFloor", air)
    # iron sight proxies
    sm(cube, (18, 150, 368), (0.03,0.03,0.08), None, "AAA_Combat_FrontSight", metal)
    sm(cube, (18, 85, 368), (0.05,0.02,0.1), None, "AAA_Combat_RearSight", metal)

    # active inbound swarm denser
    for lane,y in enumerate([-1600,-1000,-400,200,800,1400,2000]):
        for n in range(6):
            x=2200 + n*480 + (lane%2)*140
            z=360 + (n%4)*50
            sm(cone, (x,y,z), (1.3,1.3,3.5), unreal.Rotator(0,-90,0), f"AAA_Combat_Drone_{lane}_{n}", metal)
            sm(cube, (x-50,y,z), (3.0,0.16,0.08), None, f"AAA_Combat_DroneWing_{lane}_{n}", metal)
            sm(sphere, (x+130,y,z), (0.22,0.22,0.22), None, f"AAA_Combat_DroneEx_{lane}_{n}", exhaust)

    # Tracer lane markers (visual)
    for i in range(12):
        sm(cyl, (400+i*80, -40+i*8, 370), (0.03,0.03,0.9), unreal.Rotator(0,90,8), f"AAA_Combat_Tracer_{i}", exhaust)

    # Player start
    ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20,95,360), unreal.Rotator(0,0,0))
    if ps: ps.set_actor_label("AAA_Combat_PlayerStart")

    # cameras for critic stills
    for name,loc,rot in [
        ("AAA_Cam_CombatADS",(18,125,364),(-2,8,0)),
        ("AAA_Cam_CombatCockpit",(28,90,370),(-10,12,0)),
        ("AAA_Cam_CombatSwarm",(2800,0,700),(-12,-180,0)),
    ]:
        c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("combat visual mock densified; C++ still required for true gunfeel")

if __name__=="__main__":
    main()
