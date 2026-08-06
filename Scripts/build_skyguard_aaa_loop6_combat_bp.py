import unreal

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def ensure_bp(name, parent_cls):
    path = "/Game/Skyguard/Blueprints/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_cls)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Blueprints", unreal.Blueprint, factory)
    if bp:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("created BP " + name)
    return bp

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    # Ensure BP shells for playable iteration without C++ editor module
    ensure_bp("BP_SkyguardGunner", unreal.Character)
    ensure_bp("BP_ShahedDrone", unreal.Actor)
    ensure_bp("BP_DroneSpawner", unreal.Actor)
    ensure_bp("BP_SkyguardGameMode", unreal.GameModeBase)
    ensure_bp("BP_SkyguardPlayerController", unreal.PlayerController)
    ensure_bp("BP_SkyguardHUD", unreal.HUD)

    clear_prefix("AAA_L6C_")
    # Visual combat mock anchors: ADS camera, swarm tags, igla lock ring proxies
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    cyl = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    exhaust = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")
    plate = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_L3_plate")
    # Iron sight optical axis marker (no HUD reticle; world-aligned sight plane)
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(18, 140, 368), unreal.Rotator())
    if a:
        a.static_mesh_component.set_static_mesh(cube)
        a.set_actor_scale3d(unreal.Vector(0.02, 0.02, 0.08))
        a.set_actor_label("AAA_L6C_FrontSightAxis")
        if plate: a.static_mesh_component.set_material(0, plate)
    # Tracer corridor markers
    for i in range(16):
        t = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(200 + i * 90, 20, 365), unreal.Rotator(0, 90, 5))
        if t:
            t.static_mesh_component.set_static_mesh(cyl)
            t.set_actor_scale3d(unreal.Vector(0.03, 0.03, 0.8))
            t.set_actor_label("AAA_L6C_Tracer_%d" % i)
            if exhaust: t.static_mesh_component.set_material(0, exhaust)
    # Explosion bookmarks over city for cinematic stills
    for i, y in enumerate([-900, -300, 300, 900]):
        e = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-1700, y, 120), unreal.Rotator())
        if e:
            e.static_mesh_component.set_static_mesh(sphere)
            e.set_actor_scale3d(unreal.Vector(1.4, 1.4, 1.2))
            e.set_actor_label("AAA_L6C_FlakMark_%d" % i)
            if exhaust: e.static_mesh_component.set_material(0, exhaust)

    # Game mode override attempt on world settings
    try:
        gm = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Blueprints/BP_SkyguardGameMode")
        if gm:
            # Set default game mode via world settings if API available
            ws = unreal.EditorLevelLibrary.get_game_world()
            log("world " + str(ws))
    except Exception as e:
        log("gm note " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop6 combat BP/visual mock complete; C++ editor module still required for true gunfeel")
    log("CRITIC: gameplay pillar still FAIL")

if __name__ == "__main__":
    main()
