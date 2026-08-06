"""Cinematic density pass: volumetric clouds proxy, more interior city lights, debris fields, runway lights."""
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
    clear_prefix("AAA_Cine_")
    sphere=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    glass=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_CityGlass")
    metal=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_metal")
    exhaust=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_ExhaustGlow")
    concrete=unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_concrete")

    # Cloud proxies
    for i in range(24):
        x=-1000 + (i%6)*700
        y=-3000 + (i//6)*1500
        z=1800 + (i%3)*250
        sm(sphere, (x,y,z), (12,18,4), None, f"AAA_Cine_Cloud_{i}", glass)

    # Runway/approach lights out to sea
    for i in range(40):
        sm(sphere, (200+i*90, 0, 30), (0.25,0.25,0.25), None, f"AAA_Cine_ApproachLight_{i}", exhaust)

    # Debris field near coast combat zone
    for i in range(60):
        x=-700 + (i%10)*40
        y=-500 + (i//10)*90
        sm(cube, (x,y,35+(i%4)*8), (0.2+(i%3)*0.1, 0.3, 0.15), unreal.Rotator(i*7,i*13,i*3), f"AAA_Cine_Debris_{i}", metal)

    # Additional coastal warehouses
    for i,y in enumerate([-2200,-1400,-600,200,1000,1800,2500]):
        sm(cube, (-1500,y,90), (6,3,2.2), None, f"AAA_Cine_Warehouse_{i}", concrete)
        sm(cube, (-1500,y,160), (5.5,2.7,0.3), None, f"AAA_Cine_WarehouseRoof_{i}", metal)

    # Spotlights
    for i,y in enumerate([-1200,0,1200]):
        sl=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(-1300,y,520), unreal.Rotator(-35,0,0))
        if sl:
            sl.set_actor_label(f"AAA_Cine_Spot_{i}")
            sc=sl.get_component_by_class(unreal.SpotLightComponent)
            if sc:
                try:
                    sc.set_intensity(120000.0)
                    sc.set_outer_cone_angle(40.0)
                    sc.set_attenuation_radius(5000.0)
                except Exception:
                    pass

    unreal.EditorLevelLibrary.save_current_level()
    log("cinematic densify complete")
    log("CRITIC: FAIL AAA - still proxy geometry under textured materials")

if __name__=="__main__":
    main()
