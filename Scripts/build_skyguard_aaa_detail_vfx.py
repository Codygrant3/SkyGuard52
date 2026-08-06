"""AAA densification + VFX proxy pass"""
import unreal

def log(m): unreal.log(f"[SkyguardAAA] {m}")

def clear_prefix(prefix):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            n=a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def mesh(p): return unreal.EditorAssetLibrary.load_asset(p)
def mat(p): return unreal.EditorAssetLibrary.load_asset(p)

def sm(mesh_asset, loc, scale=None, rot=None, label=None, material=None):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a: return None
    c=a.static_mesh_component
    c.set_static_mesh(mesh_asset)
    if scale: a.set_actor_scale3d(unreal.Vector(*scale))
    if label: a.set_actor_label(label)
    if material: c.set_material(0, material)
    return a

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_VFX_")
    clear_prefix("AAA_CityDetail_")
    cube=mesh("/Engine/BasicShapes/Cube")
    sphere=mesh("/Engine/BasicShapes/Sphere")
    cyl=mesh("/Engine/BasicShapes/Cylinder")
    cone=mesh("/Engine/BasicShapes/Cone")
    concrete=mat("/Game/Skyguard/Materials/M_CityConcrete")
    glass=mat("/Game/Skyguard/Materials/M_CityGlass")
    asphalt=mat("/Game/Skyguard/Materials/M_Asphalt")
    metal=mat("/Game/Skyguard/Materials/M_MetalRust")
    exhaust=mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    # balconies / ledges / AC / antennas
    for i in range(60):
        x=-1700 - (i%5)*220
        y=-2400 + i*85
        z=220 + (i%8)*70
        sm(cube,(x+60,y,z), (0.9,0.25,0.08), None, f"AAA_CityDetail_Balcony_{i}", concrete)
        if i%2==0:
            sm(cube,(x-40,y,z+40), (0.25,0.25,0.2), None, f"AAA_CityDetail_AC_{i}", metal)
        if i%4==0:
            sm(cyl,(x,y,z+120), (0.05,0.05,1.2), None, f"AAA_CityDetail_Antenna_{i}", metal)
        if i%3==0:
            sm(cube,(x+20,y+40,z-30), (0.05,0.7,0.5), None, f"AAA_CityDetail_Window_{i}", glass)
    # billboards / signs
    for i,y in enumerate([-1500,-500,500,1500]):
        sm(cube,(-1400,y,260), (0.1,2.0,1.0), None, f"AAA_CityDetail_Billboard_{i}", asphalt)
        sm(cube,(-1390,y,260), (0.05,1.8,0.8), None, f"AAA_CityDetail_BillboardFace_{i}", glass)
    # destruction smoke proxies near drones
    for i in range(25):
        sm(sphere,(2200 - i*30, -1000 + i*90, 420 + (i%5)*20), (0.4,0.4,0.4), None, f"AAA_VFX_SmokeProxy_{i}", exhaust)
    # muzzle flash proxies near gunner
    sm(sphere,(40,140,365), (0.15,0.15,0.15), None, "AAA_VFX_MuzzleProxy", exhaust)
    # explosion ring proxies over city for cinematic stills
    for i,y in enumerate([-800,0,900]):
        sm(cyl,(-1600,y,80), (3.5,3.5,0.05), None, f"AAA_VFX_BlastRing_{i}", exhaust)

    # Niagara system asset create if possible
    try:
        factory = unreal.NiagaraSystemFactoryNew()
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        path="/Game/Skyguard/VFX"
        if not unreal.EditorAssetLibrary.does_directory_exist(path):
            unreal.EditorAssetLibrary.make_directory(path)
        if not unreal.EditorAssetLibrary.does_asset_exist(path+"/NS_DroneExplosion"):
            ns = asset_tools.create_asset("NS_DroneExplosion", path, unreal.NiagaraSystem, factory)
            if ns:
                unreal.EditorAssetLibrary.save_loaded_asset(ns)
                log("Created NS_DroneExplosion shell")
    except Exception as e:
        log(f"Niagara create limited: {e}")

    # Review note asset folder
    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Skyguard/Review"):
        unreal.EditorAssetLibrary.make_directory("/Game/Skyguard/Review")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("City detail + VFX proxy pass complete")
    log("CRITIC: still FAIL vs AAA until hero meshes and authored VFX replace proxies")

if __name__=="__main__":
    main()
