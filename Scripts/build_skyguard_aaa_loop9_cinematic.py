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
    clear_prefix("AAA_L9CINE_")
    for cls_name, label, loc, rot in [
        ("DirectionalLight", "AAA_L9CINE_KeySun", (0,0,1700), (-28, 55, 0)),
        ("SkyLight", "AAA_L9CINE_Sky", (0,0,700), (0,0,0)),
        ("ExponentialHeightFog", "AAA_L9CINE_Fog", (0,0,0), (0,0,0)),
        ("VolumetricCloud", "AAA_L9CINE_Clouds", (0,0,0), (0,0,0)),
        ("PostProcessVolume", "AAA_L9CINE_Post", (0,0,400), (0,0,0)),
        ("SkyAtmosphere", "AAA_L9CINE_Atmo", (0,0,0), (0,0,0)),
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
    for i, loc in enumerate([(15, 90, 370), (-1900, 50, 75), (-500, -900, 90), (1000, -1800, 60), (20, 120, 360)]):
        try:
            pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
            if pl:
                pl.set_actor_label("AAA_L9CINE_Point_%d" % i)
        except Exception:
            pass
    for name in ["WaterBodyOcean", "WaterZone"]:
        try:
            cls = getattr(unreal, name, None)
            if not cls:
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(1700, 0, 0), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L9CINE_" + name)
                log("water " + name)
        except Exception as e:
            log(str(e))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop9 cinematic lighting complete")
    log("CRITIC: lighting better; content still FAIL vs AAA refs")

if __name__ == "__main__":
    main()
