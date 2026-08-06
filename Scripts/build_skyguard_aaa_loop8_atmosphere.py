import unreal

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

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
    clear_prefix("AAA_L8ATMO_")
    for cls_name, label, loc, rot in [
        ("SkyAtmosphere", "AAA_L8ATMO_SkyAtmosphere", (0,0,0), (0,0,0)),
        ("SkyLight", "AAA_L8ATMO_SkyLight", (0,0,600), (0,0,0)),
        ("ExponentialHeightFog", "AAA_L8ATMO_Fog", (0,0,0), (0,0,0)),
        ("VolumetricCloud", "AAA_L8ATMO_Clouds", (0,0,0), (0,0,0)),
        ("PostProcessVolume", "AAA_L8ATMO_Post", (0,0,400), (0,0,0)),
        ("DirectionalLight", "AAA_L8ATMO_Sun", (0,0,1600), (-30, 52, 0)),
    ]:
        try:
            cls = getattr(unreal, cls_name, None)
            if not cls:
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(*rot))
            if a:
                a.set_actor_label(label)
                if cls_name == "PostProcessVolume":
                    try:
                        a.set_editor_property("unbound", True)
                    except Exception:
                        pass
                log("spawned " + label)
        except Exception as e:
            log(cls_name + " " + str(e))
    for name in ["WaterBodyOcean", "WaterZone"]:
        try:
            cls = getattr(unreal, name, None)
            if not cls:
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(1600, 0, 0), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L8ATMO_" + name)
                log("spawned water " + name)
        except Exception as e:
            log("water " + str(e))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop8 atmosphere pass complete")

if __name__ == "__main__":
    main()
