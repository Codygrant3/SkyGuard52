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
    clear_prefix("AAA_L7CINE_")
    # Key/fill/rim lights
    try:
        key = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1500), unreal.Rotator(-32, 48, 0))
        if key:
            key.set_actor_label("AAA_L7CINE_KeySun")
        fill = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,700), unreal.Rotator())
        if fill:
            fill.set_actor_label("AAA_L7CINE_SkyFill")
        fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0,0,0), unreal.Rotator())
        if fog:
            fog.set_actor_label("AAA_L7CINE_Fog")
        pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,400), unreal.Rotator())
        if pp:
            pp.set_actor_label("AAA_L7CINE_Post")
            try:
                pp.set_editor_property("unbound", True)
            except Exception:
                pass
        # local point lights in cockpit and city for specular read
        for i, loc in enumerate([(10, 80, 370), (-1900, 0, 70), (-400, -800, 90), (900, -1800, 40)]):
            pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
            if pl:
                pl.set_actor_label("AAA_L7CINE_Point_%d" % i)
        log("cinematic lights spawned")
    except Exception as e:
        log("cine lights " + str(e))

    # more review cameras
    for name, loc, rot in [
        ("AAA_Cam_L7CINE_GoldenHourCity", (-1800, -500, 300), (-12, 20, 0)),
        ("AAA_Cam_L7CINE_OverShoulder", (40, 90, 365), (-5, 15, 0)),
        ("AAA_Cam_L7CINE_OceanGlint", (1400, -1000, 250), (-10, 50, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop7 cinematic lighting pass complete")
    log("CRITIC: lighting improved but content still FAIL vs AAA")

if __name__ == "__main__":
    main()
