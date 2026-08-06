"""Generate higher-quality static meshes for Yak and drones via Geometry Scripting if available."""
import unreal

def log(m): unreal.log(f"[SkyguardAAA] {m}")

def create_dynamic_mesh_actor(label, loc, scale=(1,1,1)):
    try:
        cls = unreal.DynamicMeshActor
    except Exception:
        log("DynamicMeshActor unavailable")
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
    if a:
        a.set_actor_label(label)
        a.set_actor_scale3d(unreal.Vector(*scale))
    return a

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    # densify water foam again near shore with better spacing
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    beach = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_concrete")
    # Ensure more review cameras with golden hour angles
    for name, loc, rot in [
        ("AAA_Cam_GoldenHour", (1400, -1600, 650), (-18, 40, 0)),
        ("AAA_Cam_OverWing", (80, -40, 390), (-12, 20, 0)),
        ("AAA_Cam_DroneNose", (1900, 100, 450), (-5, -170, 0)),
    ]:
        exists=False
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try:
                if a.get_actor_label()==name:
                    exists=True
            except Exception:
                pass
        if not exists:
            c=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
            if c: c.set_actor_label(name)

    # Add more layered aircraft surface plates for silhouette complexity
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    metal = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_airframe_metal")
    for i, (loc, scale) in enumerate([
        ((0, -200, 340), (1.0, 2.0, 0.08)),
        ((0, 100, 340), (1.0, 2.5, 0.08)),
        ((-120, 0, 310), (1.5, 0.4, 0.06)),
        ((120, 0, 310), (1.5, 0.4, 0.06)),
        ((0, 380, 360), (0.5, 0.8, 0.2)),
    ]):
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator())
        if a:
            a.set_actor_label(f"AAA_Yak_Panel_{i}")
            c=a.static_mesh_component
            c.set_static_mesh(cube)
            a.set_actor_scale3d(unreal.Vector(*scale))
            if metal: c.set_material(0, metal)

    # Fill more unique city landmarks
    glass = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_CityGlass")
    concrete = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_FacadeAtlas") or unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Tex_concrete")
    for i, y in enumerate([-1800, -600, 600, 1800]):
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-2100, y, 700), unreal.Rotator())
        if a:
            a.set_actor_label(f"AAA_Landmark_Tower_{i}")
            c=a.static_mesh_component
            c.set_static_mesh(cube)
            a.set_actor_scale3d(unreal.Vector(3.5, 3.5, 14))
            if concrete: c.set_material(0, concrete)
        b=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-2100, y, 1450), unreal.Rotator())
        if b:
            b.set_actor_label(f"AAA_Landmark_Crown_{i}")
            c=b.static_mesh_component
            c.set_static_mesh(cube)
            b.set_actor_scale3d(unreal.Vector(4.0, 4.0, 1.2))
            if glass: c.set_material(0, glass)

    unreal.EditorLevelLibrary.save_current_level()
    log("silhouette densify + landmarks complete")

if __name__ == "__main__":
    main()
