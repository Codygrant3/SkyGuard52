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
    clear_prefix("AAA_L10CINE_")
    for cls_name, label, loc, rot in [
        ("DirectionalLight", "AAA_L10CINE_KeySun", (0,0,1800), (-26, 58, 0)),
        ("SkyLight", "AAA_L10CINE_Sky", (0,0,750), (0,0,0)),
        ("ExponentialHeightFog", "AAA_L10CINE_Fog", (0,0,0), (0,0,0)),
        ("VolumetricCloud", "AAA_L10CINE_Clouds", (0,0,0), (0,0,0)),
        ("PostProcessVolume", "AAA_L10CINE_Post", (0,0,420), (0,0,0)),
        ("SkyAtmosphere", "AAA_L10CINE_Atmo", (0,0,0), (0,0,0)),
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
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(1800, 0, 0), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L10CINE_" + name)
                log("water " + name)
        except Exception as e:
            log(str(e))
    for i, loc in enumerate([(15, 95, 370), (-1900, 0, 70), (-450, -1000, 80), (1100, -1800, 50)]):
        try:
            pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
            if pl:
                pl.set_actor_label("AAA_L10CINE_Point_%d" % i)
        except Exception:
            pass
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop10 cinematic complete")
    log("CRITIC: still FAIL vs AAA overall")

if __name__ == "__main__":
    main()
