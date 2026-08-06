"""Try to create a WaterBodyOcean if Water plugin is available; else densify ocean planes."""
import unreal

def log(m):
    unreal.log(f"[SkyguardAAA] {m}")

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    created = False
    # Discover water classes
    for name in ["WaterBodyOcean", "WaterBodyCustom", "WaterZone"]:
        try:
            cls = getattr(unreal, name, None)
            if cls is None:
                continue
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(0,0,0), unreal.Rotator())
            if actor:
                actor.set_actor_label(f"AAA_Water_{name}")
                created = True
                log(f"Spawned {name}")
        except Exception as e:
            log(f"{name} spawn failed: {e}")
    if not created:
        # densify ocean with multi-layer planes
        plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
        deep = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_OceanDeep")
        near = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Materials/M_Ocean")
        for i, (loc, scale, mat, label) in enumerate([
            ((2500,0,-20), (500,500,1), deep, "AAA_Water_DeepLayer"),
            ((800,0,-8), (300,400,1), near, "AAA_Water_NearLayer"),
            ((200,0,-2), (180,300,1), near, "AAA_Water_ShoreLayer"),
        ]):
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator())
            if a:
                a.set_actor_label(label)
                c=a.static_mesh_component
                c.set_static_mesh(plane)
                a.set_actor_scale3d(unreal.Vector(*scale))
                if mat: c.set_material(0, mat)
        log("Water plugin class spawn unavailable; layered ocean planes densified")
    unreal.EditorLevelLibrary.save_current_level()
    log("Water pass complete")

if __name__ == "__main__":
    main()
