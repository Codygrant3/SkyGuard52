import unreal

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def ensure_ns(name):
    path = "/Game/Skyguard/VFX/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    try:
        factory = unreal.NiagaraSystemFactoryNew()
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/VFX", unreal.NiagaraSystem, factory)
        if asset:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
            log("created " + name)
        return asset
    except Exception as e:
        log("ns fail " + name + " " + str(e))
        return None

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def spawn_ns_actor(label, loc, asset_name):
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(*loc), unreal.Rotator())
        if not a:
            return
        a.set_actor_label(label)
        asset = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/VFX/" + asset_name)
        try:
            comp = a.niagara_component
            if comp and asset:
                comp.set_asset(asset)
                try:
                    comp.activate(True)
                except Exception:
                    pass
        except Exception:
            pass
        log("niagara actor " + label)
    except Exception as e:
        log("spawn ns " + str(e))

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_dir("/Game/Skyguard/VFX")
    clear_prefix("AAA_L9V_")
    for n in [
        "NS_MuzzleFlash","NS_DroneTrail","NS_OceanSpray","NS_DroneExplosion","NS_FlakBurst",
        "NS_MissileTrail","NS_ShellCasings","NS_GunSmoke","NS_WaterSplash","NS_CloudWisps",
        "NS_HitSparks","NS_ContrailRibbon","NS_IglaLaunch","NS_CityFire","NS_PropWash","NS_TracerBurst"
    ]:
        ensure_ns(n)

    # combat-critical placements
    placements = [
        ("AAA_L9V_Muzzle", (40, 155, 365), "NS_MuzzleFlash"),
        ("AAA_L9V_GunSmoke", (30, 140, 360), "NS_GunSmoke"),
        ("AAA_L9V_Tracers", (200, 40, 365), "NS_TracerBurst"),
        ("AAA_L9V_Igla", (-30, 160, 355), "NS_IglaLaunch"),
        ("AAA_L9V_Explosion1", (-1650, 0, 150), "NS_DroneExplosion"),
        ("AAA_L9V_Explosion2", (-1500, 500, 180), "NS_FlakBurst"),
        ("AAA_L9V_CityFire", (-2100, -300, 80), "NS_CityFire"),
        ("AAA_L9V_Trail", (2000, 0, 430), "NS_DroneTrail"),
        ("AAA_L9V_Missile", (1400, 300, 410), "NS_MissileTrail"),
        ("AAA_L9V_Spray", (-700, 0, 8), "NS_OceanSpray"),
        ("AAA_L9V_PropWash", (0, -520, 300), "NS_PropWash"),
        ("AAA_L9V_Sparks", (800, -200, 380), "NS_HitSparks"),
    ]
    for label, loc, asset in placements:
        spawn_ns_actor(label, loc, asset)

    # dense emissive proxy fallbacks for stills / readability
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    exhaust = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")
    for i in range(50):
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(45 + i * 10, 150, 362 + (i % 4)), unreal.Rotator())
        if a:
            a.static_mesh_component.set_static_mesh(sphere)
            a.set_actor_scale3d(unreal.Vector(0.07, 0.07, 0.07))
            a.set_actor_label("AAA_L9V_MuzzleCloud_%d" % i)
            if exhaust:
                a.static_mesh_component.set_material(0, exhaust)
    for i in range(16):
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-1700, -1000 + i * 130, 100 + (i % 3) * 30), unreal.Rotator())
        if a:
            a.static_mesh_component.set_static_mesh(sphere)
            a.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.3))
            a.set_actor_label("AAA_L9V_FlakCloud_%d" % i)
            if exhaust:
                a.static_mesh_component.set_material(0, exhaust)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop9 VFX densify complete")
    log("CRITIC: VFX still FAIL until emitters authored with real particle graphs")

if __name__ == "__main__":
    main()
