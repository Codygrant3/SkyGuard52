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
        log("ns " + name + " " + str(e))
        return None

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
    ensure_dir("/Game/Skyguard/VFX")
    clear_prefix("AAA_L6V_")
    for n in [
        "NS_MuzzleFlash","NS_DroneTrail","NS_OceanSpray","NS_DroneExplosion",
        "NS_FlakBurst","NS_MissileTrail","NS_ShellCasings","NS_GunSmoke",
        "NS_WaterSplash","NS_CloudWisps","NS_HitSparks","NS_ContrailRibbon"
    ]:
        ensure_ns(n)

    # Place Niagara actors if class available
    try:
        ns_cls = unreal.NiagaraActor
        for i, (label, loc, asset_name) in enumerate([
            ("AAA_L6V_Muzzle", (40, 150, 365), "NS_MuzzleFlash"),
            ("AAA_L6V_Trail", (1800, 0, 420), "NS_DroneTrail"),
            ("AAA_L6V_Explosion", (-1600, 0, 140), "NS_DroneExplosion"),
            ("AAA_L6V_Flak", (-1500, 400, 200), "NS_FlakBurst"),
            ("AAA_L6V_Missile", (1200, 200, 400), "NS_MissileTrail"),
            ("AAA_L6V_Spray", (-700, 0, 10), "NS_OceanSpray"),
        ]):
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(ns_cls, unreal.Vector(*loc), unreal.Rotator())
            if a:
                a.set_actor_label(label)
                # try assign asset
                asset = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/VFX/" + asset_name)
                try:
                    comp = a.niagara_component
                    if comp and asset:
                        comp.set_asset(asset)
                except Exception:
                    pass
                log("spawned niagara actor " + label)
    except Exception as e:
        log("niagara actor limited: " + str(e))

    # dense sprite-proxy field as fallback visual energy
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    exhaust = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")
    for i in range(40):
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(50 + i * 12, 145, 360 + (i % 5)), unreal.Rotator())
        if a:
            a.static_mesh_component.set_static_mesh(sphere)
            a.set_actor_scale3d(unreal.Vector(0.08, 0.08, 0.08))
            a.set_actor_label("AAA_L6V_MuzzleCloud_%d" % i)
            if exhaust:
                a.static_mesh_component.set_material(0, exhaust)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop6 VFX densify complete; emitters still not authored graphs")
    log("CRITIC: VFX pillar still FAIL")

if __name__ == "__main__":
    main()
