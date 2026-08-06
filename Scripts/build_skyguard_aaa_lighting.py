"""Skyguard AAA lighting/post fix pass for UE5.8 property names + denser set dressing."""
import unreal

def log(m):
    unreal.log(f"[SkyguardAAA] {m}")

def clear_prefix(prefix):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def shape(p):
    return unreal.EditorAssetLibrary.load_asset(p)

def mat(p):
    return unreal.EditorAssetLibrary.load_asset(p)

def spawn_sm(mesh, loc, rot=None, scale=None, label=None, material=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator()
    )
    if not actor:
        return None
    c = actor.static_mesh_component
    c.set_static_mesh(mesh)
    if scale:
        actor.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        actor.set_actor_label(label)
    if material:
        c.set_material(0, material)
    return actor

def main():
    map_path = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"
    unreal.EditorLevelLibrary.load_level(map_path)
    clear_prefix("AAA_Light_")
    clear_prefix("AAA_Dress_")

    # Sun
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(2000, -3000, 6000), unreal.Rotator(-42, 150, 0)
    )
    sun.set_actor_label("AAA_Light_Sun")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if sc:
        sc.set_intensity(12.0)
        try:
            sc.set_light_color(unreal.LinearColor(1.0, 0.97, 0.92, 1.0))
        except Exception:
            try:
                sc.set_editor_property("light_color", unreal.Color(255, 247, 235, 255))
            except Exception as e:
                log(f"sun color fail {e}")
        for prop, val in [
            ("atmosphere_sun_light", True),
            ("cast_shadows", True),
            ("forward_shading_priority", 0),
        ]:
            try:
                sc.set_editor_property(prop, val)
            except Exception:
                pass

    # Sky atmosphere
    try:
        atm = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(), unreal.Rotator())
        atm.set_actor_label("AAA_Light_SkyAtmosphere")
    except Exception as e:
        log(f"atm {e}")

    # Sky light
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2500), unreal.Rotator())
    sky.set_actor_label("AAA_Light_SkyLight")
    skc = sky.get_component_by_class(unreal.SkyLightComponent)
    if skc:
        try:
            skc.set_editor_property("real_time_capture", True)
            skc.set_intensity(1.2)
        except Exception as e:
            log(f"skylight {e}")

    # Height fog
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(), unreal.Rotator())
    fog.set_actor_label("AAA_Light_HeightFog")
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if fc:
        try:
            fc.set_fog_density(0.016)
            fc.set_fog_height_falloff(0.2)
            fc.set_editor_property("volumetric_fog", True)
            fc.set_editor_property("volumetric_fog_extinction_scale", 0.85)
        except Exception as e:
            log(f"fog {e}")

    # Post process unbound
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 400), unreal.Rotator())
    pp.set_actor_label("AAA_Light_Post")
    try:
        # property name variations across versions
        for prop in ("unbound", "b_unbound", "bUnbound"):
            try:
                pp.set_editor_property(prop, True)
                break
            except Exception:
                continue
        settings = pp.get_editor_property("settings")
        # Use enable overrides via methods when possible
        for method, args in [
            ("set_editor_property", ("override_auto_exposure_bias", True)),
        ]:
            pass
        try:
            settings.set_editor_property("override_auto_exposure_bias", True)
            settings.set_editor_property("auto_exposure_bias", 0.4)
            settings.set_editor_property("override_bloom_intensity", True)
            settings.set_editor_property("bloom_intensity", 0.4)
            settings.set_editor_property("override_vignette_intensity", True)
            settings.set_editor_property("vignette_intensity", 0.32)
            settings.set_editor_property("override_auto_exposure_min_brightness", True)
            settings.set_editor_property("auto_exposure_min_brightness", 0.4)
            settings.set_editor_property("override_auto_exposure_max_brightness", True)
            settings.set_editor_property("auto_exposure_max_brightness", 1.5)
            pp.set_editor_property("settings", settings)
        except Exception as e:
            log(f"pp settings {e}")
    except Exception as e:
        log(f"pp {e}")

    # Extra harbor ships / containers / rubble dressing
    cube = shape("/Engine/BasicShapes/Cube")
    cyl = shape("/Engine/BasicShapes/Cylinder")
    sphere = shape("/Engine/BasicShapes/Sphere")
    metal = mat("/Game/Skyguard/Materials/M_MetalRust")
    city = mat("/Game/Skyguard/Materials/M_CityConcrete")
    asphalt = mat("/Game/Skyguard/Materials/M_Asphalt")
    for i, y in enumerate([-2000, -1000, 0, 1000, 2000]):
        spawn_sm(cube, (-500, y, 80), None, (8, 2.2, 1.6), f"AAA_Dress_ShipHull_{i}", metal)
        spawn_sm(cube, (-500, y, 130), None, (7, 1.8, 0.8), f"AAA_Dress_ShipSuper_{i}", city)
        for c in range(4):
            spawn_sm(cube, (-1450, y - 120 + c * 60, 70), None, (1.2, 0.7, 0.7), f"AAA_Dress_Container_{i}_{c}", metal)
    # Debris / sandbags near road
    for i in range(30):
        y = -1800 + i * 120
        spawn_sm(cube, (-1120, y, 40), None, (0.4, 0.7, 0.25), f"AAA_Dress_Sandbag_{i}", city)
        if i % 3 == 0:
            spawn_sm(sphere, (-1080, y + 20, 45), None, (0.3, 0.3, 0.2), f"AAA_Dress_Rubble_{i}", asphalt)

    # High wires / poles
    for i in range(20):
        y = -2200 + i * 230
        spawn_sm(cyl, (-1250, y, 120), None, (0.12, 0.12, 3.5), f"AAA_Dress_Pole_{i}", metal)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Lighting+dressing pass complete")

if __name__ == "__main__":
    main()
