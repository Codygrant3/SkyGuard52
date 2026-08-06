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
    clear_prefix("AAA_L4ATMO_")
    for cls_name, label, loc in [
        ("SkyAtmosphere", "AAA_L4ATMO_SkyAtmosphere", (0,0,0)),
        ("SkyLight", "AAA_L4ATMO_SkyLight", (0,0,500)),
        ("ExponentialHeightFog", "AAA_L4ATMO_HeightFog", (0,0,0)),
        ("PostProcessVolume", "AAA_L4ATMO_Post", (0,0,300)),
        ("VolumetricCloud", "AAA_L4ATMO_Clouds", (0,0,0)),
    ]:
        try:
            cls = getattr(unreal, cls_name, None)
            if cls is None:
                log("missing class " + cls_name)
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
            if a:
                a.set_actor_label(label)
                if cls_name == "PostProcessVolume":
                    try:
                        a.set_editor_property("unbound", True)
                    except Exception:
                        pass
                log("spawned " + label)
        except Exception as e:
            log(cls_name + " failed: " + str(e))
    for name in ["WaterBodyOcean", "WaterZone"]:
        try:
            cls = getattr(unreal, name, None)
            if cls is None:
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(1500, 0, 0), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L4ATMO_" + name)
                log("spawned water " + name)
        except Exception as e:
            log("water " + name + ": " + str(e))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop4 atmosphere pass complete")

if __name__ == "__main__":
    main()
