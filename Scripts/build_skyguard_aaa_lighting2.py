"""AAA lighting polish + exponential fog/post using UE5.8-safe property methods."""
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

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_Light2_")

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(3000,-2500,7000), unreal.Rotator(-48, 155, 0))
    sun.set_actor_label("AAA_Light2_Sun")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if sc:
        sc.set_intensity(14.0)
        try: sc.set_light_color(unreal.LinearColor(1.0, 0.95, 0.88, 1.0))
        except Exception: pass
        for prop,val in [("atmosphere_sun_light", True),("cast_shadows", True),("dynamic_shadow_distance_movable_light", 80000.0),("shadow_amount", 1.0)]:
            try: sc.set_editor_property(prop,val)
            except Exception: pass

    try:
        atm = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(), unreal.Rotator())
        atm.set_actor_label("AAA_Light2_SkyAtmosphere")
    except Exception as e:
        log(f"atm {e}")

    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,3000), unreal.Rotator())
    sky.set_actor_label("AAA_Light2_SkyLight")
    sk = sky.get_component_by_class(unreal.SkyLightComponent)
    if sk:
        try:
            sk.set_editor_property("real_time_capture", True)
            sk.set_intensity(1.35)
        except Exception as e:
            log(f"sky {e}")

    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(), unreal.Rotator())
    fog.set_actor_label("AAA_Light2_Fog")
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if fc:
        try:
            fc.set_fog_density(0.012)
            fc.set_fog_height_falloff(0.22)
        except Exception: pass
        for prop,val in [
            ("volumetric_fog", True),
            ("b_enable_volumetric_fog", True),
            ("volumetric_fog_scattering_distribution", 0.25),
            ("volumetric_fog_extinction_scale", 0.9),
            ("second_fog_data", None),
        ]:
            try:
                if val is not None:
                    fc.set_editor_property(prop, val)
            except Exception:
                pass

    # Post process
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,500), unreal.Rotator())
    pp.set_actor_label("AAA_Light2_Post")
    for prop in ("unbound","b_unbound","bUnbound"):
        try:
            pp.set_editor_property(prop, True)
            break
        except Exception:
            continue
    try:
        s = pp.get_editor_property("settings")
        pairs = [
            ("override_auto_exposure_bias", True), ("auto_exposure_bias", 0.55),
            ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", 0.45),
            ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 1.4),
            ("override_bloom_intensity", True), ("bloom_intensity", 0.45),
            ("override_vignette_intensity", True), ("vignette_intensity", 0.28),
            ("override_motion_blur_amount", True), ("motion_blur_amount", 0.35),
            ("override_scene_fringe_intensity", True), ("scene_fringe_intensity", 0.2),
            ("override_color_saturation", True), ("color_saturation", unreal.Vector4(1.06,1.03,0.98,1)),
            ("override_color_contrast", True), ("color_contrast", unreal.Vector4(1.07,1.06,1.04,1)),
            ("override_film_slope", True), ("film_slope", 0.9),
            ("override_film_toe", True), ("film_toe", 0.5),
            ("override_film_shoulder", True), ("film_shoulder", 0.28),
        ]
        for i in range(0,len(pairs),2):
            try:
                s.set_editor_property(pairs[i][0], pairs[i][1])
                s.set_editor_property(pairs[i+1][0], pairs[i+1][1])
            except Exception:
                pass
        pp.set_editor_property("settings", s)
    except Exception as e:
        log(f"pp {e}")

    # Local practical lights over city
    for i,y in enumerate([-1500,-500,500,1500]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(-1700,y,420), unreal.Rotator())
        if pl:
            pl.set_actor_label(f"AAA_Light2_CityPoint_{i}")
            pc = pl.get_component_by_class(unreal.PointLightComponent)
            if pc:
                try:
                    pc.set_intensity(8000.0)
                    pc.set_attenuation_radius(1800.0)
                    pc.set_light_color(unreal.LinearColor(1.0,0.85,0.55,1.0))
                except Exception:
                    pass

    unreal.EditorLevelLibrary.save_current_level()
    log("lighting polish complete")

if __name__=="__main__":
    main()
