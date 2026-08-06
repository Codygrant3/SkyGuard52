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
        log("create " + name + " failed: " + str(e))
        return None

def spawn_vfx_proxy(label, loc, scale, mat):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator())
    if not a:
        return
    mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_actor_label(label)
    if mat:
        a.static_mesh_component.set_material(0, mat)

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_dir("/Game/Skyguard/VFX")
    for n in ["NS_MuzzleFlash", "NS_DroneTrail", "NS_OceanSpray", "NS_DroneExplosion", "NS_FlakBurst", "NS_MissileTrail", "NS_ShellCasings"]:
        ensure_ns(n)
    # denser combat VFX proxies near gunner and over city
    exhaust = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")
    for i in range(30):
        spawn_vfx_proxy("AAA_L4VFX_MuzzleCloud_%d" % i, (40 + i * 8, 140, 365 + (i % 3)), (0.12, 0.12, 0.12), exhaust)
    for i in range(18):
        spawn_vfx_proxy("AAA_L4VFX_CitySmoke_%d" % i, (-1600, -1000 + i * 120, 90 + (i % 4) * 25), (1.8, 1.8, 1.5), exhaust)
    for i in range(10):
        spawn_vfx_proxy("AAA_L4VFX_Impact_%d" % i, (900 + i * 70, -200 + i * 40, 380), (0.5, 0.5, 0.5), exhaust)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop4 VFX author/proxy pass complete; Niagara graphs still need manual emitter authoring for AAA")
    log("CRITIC: VFX pillar still FAIL")

if __name__ == "__main__":
    main()
