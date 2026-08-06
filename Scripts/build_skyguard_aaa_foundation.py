"""
Skyguard 52 AAA visual foundation builder (UE 5.8 Python)

Goal: push the vertical slice from BasicShapes/flat colors toward a cinematic coastal combat look.
This is iterative AAA construction, not a claim of finished AAA.

Creates/upgrades:
- Richer layered materials (multi-expression)
- High-density coastal city + industrial port dressing
- Yak cockpit frame + rifle proxy with more hierarchy
- Drone formation denser approach lanes
- Atmosphere actors (sky atmosphere, volumetric fog, exponential height fog, post process AAA defaults)
- Cine camera-friendly lighting
- Screenshot camera book marks (as camera actors)
"""

import math
import unreal

ASSET_ROOT = "/Game/Skyguard"
MAP_PATH = f"{ASSET_ROOT}/Maps/Lvl_SkyguardCoast"
MAT_ROOT = f"{ASSET_ROOT}/Materials"
BP_ROOT = f"{ASSET_ROOT}/Blueprints"
MESH_ROOT = f"{ASSET_ROOT}/Meshes"
REVIEW_ROOT = f"{ASSET_ROOT}/Review"


def log(msg: str) -> None:
    unreal.log(f"[SkyguardAAA] {msg}")


def ensure_dir(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def save_asset(asset) -> None:
    if asset:
        unreal.EditorAssetLibrary.save_loaded_asset(asset)


def create_material(name: str, base_color, roughness=0.7, metallic=0.0, specular=0.5, emissive=None, opacity=None):
    package_path = f"{MAT_ROOT}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        mat = unreal.EditorAssetLibrary.load_asset(package_path)
    else:
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, MAT_ROOT, unreal.Material, factory
        )
    if not mat:
        log(f"Failed material {name}")
        return None

    try:
        mel = unreal.MaterialEditingLibrary
        # wipe old expressions for rebuild
        try:
            mel.delete_all_material_expressions(mat)
        except Exception:
            pass

        base = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, -120)
        base.set_editor_property("constant", unreal.LinearColor(base_color[0], base_color[1], base_color[2], 1.0))

        # subtle variation via cheap noise-ish fake: multiply by constant
        mult = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, -120)
        var = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, -20)
        var.set_editor_property("r", 1.0)
        mel.connect_material_expressions(base, "", mult, "A")
        mel.connect_material_expressions(var, "", mult, "B")
        mel.connect_material_property(mult, "", unreal.MaterialProperty.MP_BASE_COLOR)

        rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 80)
        rough.set_editor_property("r", float(roughness))
        mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

        metal = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 150)
        metal.set_editor_property("r", float(metallic))
        mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)

        spec = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 220)
        spec.set_editor_property("r", float(specular))
        mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)

        if emissive is not None:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, 300)
            em.set_editor_property("constant", unreal.LinearColor(emissive[0], emissive[1], emissive[2], 1.0))
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

        mel.recompile_material(mat)
    except Exception as exc:
        log(f"Material rebuild limited {name}: {exc}")

    save_asset(mat)
    return mat


def shape(path: str):
    return unreal.EditorAssetLibrary.load_asset(path)


def spawn_sm(mesh, loc, rot=None, scale=None, label=None, mat=None):
    if not mesh:
        return None
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(loc[0], loc[1], loc[2]),
        rot or unreal.Rotator(0, 0, 0),
    )
    if not actor:
        return None
    smc = actor.static_mesh_component
    smc.set_static_mesh(mesh)
    if scale:
        actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))
    if label:
        actor.set_actor_label(label)
    if mat:
        smc.set_material(0, mat)
    # enable shadows
    try:
        smc.set_editor_property("cast_shadow", True)
    except Exception:
        pass
    return actor


def clear_labeled_prefix(prefix: str):
    # Remove previously generated AAA helpers to allow re-run
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for a in actors:
        try:
            name = a.get_actor_label()
            if name and name.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass


def build_atmosphere():
    clear_labeled_prefix("AAA_")

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-38, 145, 0)
    )
    if sun:
        sun.set_actor_label("AAA_Sun")
        try:
            comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if comp:
                comp.set_editor_property("intensity", 12.0)
                comp.set_editor_property("light_color", unreal.LinearColor(1.0, 0.96, 0.90, 1.0))
                comp.set_editor_property("atmosphere_sun_light", True)
                comp.set_editor_property("cast_shadows", True)
                comp.set_editor_property("dynamic_shadow_distance_movable_light", 50000.0)
        except Exception as exc:
            log(f"Sun setup limited: {exc}")

    sky_atm = None
    try:
        sky_atm = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()
        )
        if sky_atm:
            sky_atm.set_actor_label("AAA_SkyAtmosphere")
    except Exception as exc:
        log(f"SkyAtmosphere unavailable: {exc}")

    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0, 0, 2000), unreal.Rotator()
    )
    if sky_light:
        sky_light.set_actor_label("AAA_SkyLight")
        try:
            comp = sky_light.get_component_by_class(unreal.SkyLightComponent)
            if comp:
                comp.set_editor_property("real_time_capture", True)
                comp.set_editor_property("intensity", 1.15)
        except Exception:
            pass

    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator()
    )
    if fog:
        fog.set_actor_label("AAA_HeightFog")
        try:
            comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if comp:
                comp.set_editor_property("fog_density", 0.018)
                comp.set_editor_property("fog_height_falloff", 0.18)
                comp.set_editor_property("fog_inscattering_color", unreal.LinearColor(0.45, 0.55, 0.65, 1.0))
                comp.set_editor_property("volumetric_fog", True)
                comp.set_editor_property("volumetric_fog_scattering_distribution", 0.3)
                comp.set_editor_property("volumetric_fog_extinction_scale", 0.7)
        except Exception as exc:
            log(f"Fog setup limited: {exc}")

    # Post process AAA cinematic baseline
    try:
        pp = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PostProcessVolume, unreal.Vector(0, 0, 500), unreal.Rotator()
        )
        if pp:
            pp.set_actor_label("AAA_PostProcess")
            pp.set_editor_property("b_unbound", True)
            settings = pp.get_editor_property("settings")
            # Exposure
            settings.set_editor_property("override_auto_exposure_method", True)
            settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
            settings.set_editor_property("override_auto_exposure_bias", True)
            settings.set_editor_property("auto_exposure_bias", 0.35)
            settings.set_editor_property("override_auto_exposure_min_brightness", True)
            settings.set_editor_property("auto_exposure_min_brightness", 0.35)
            settings.set_editor_property("override_auto_exposure_max_brightness", True)
            settings.set_editor_property("auto_exposure_max_brightness", 1.6)
            # Bloom / vignette / chromatic subtle
            settings.set_editor_property("override_bloom_method", True)
            settings.set_editor_property("override_bloom_intensity", True)
            settings.set_editor_property("bloom_intensity", 0.35)
            settings.set_editor_property("override_vignette_intensity", True)
            settings.set_editor_property("vignette_intensity", 0.35)
            settings.set_editor_property("override_scene_fringe_intensity", True)
            settings.set_editor_property("scene_fringe_intensity", 0.25)
            # Color grade warm coastal
            settings.set_editor_property("override_color_saturation", True)
            settings.set_editor_property("color_saturation", unreal.Vector4(1.05, 1.02, 0.98, 1.0))
            settings.set_editor_property("override_color_contrast", True)
            settings.set_editor_property("color_contrast", unreal.Vector4(1.05, 1.05, 1.03, 1.0))
            settings.set_editor_property("override_film_slope", True)
            settings.set_editor_property("film_slope", 0.88)
            settings.set_editor_property("override_film_toe", True)
            settings.set_editor_property("film_toe", 0.55)
            settings.set_editor_property("override_film_shoulder", True)
            settings.set_editor_property("film_shoulder", 0.26)
            pp.set_editor_property("settings", settings)
    except Exception as exc:
        log(f"Post process setup limited: {exc}")


def build_world(mats, shapes):
    # Remove previous AAA world dressing only
    clear_labeled_prefix("AAA_World_")
    clear_labeled_prefix("AAA_Yak_")
    clear_labeled_prefix("AAA_Drone_")
    clear_labeled_prefix("AAA_Cam_")

    # Deep ocean + nearshore gradient planes
    spawn_sm(shapes["plane"], (1200, 0, -10), scale=(400, 400, 1), label="AAA_World_OceanDeep", mat=mats["ocean_deep"])
    spawn_sm(shapes["plane"], (200, 0, -5), scale=(220, 320, 1), label="AAA_World_OceanNear", mat=mats["ocean"])
    # Land shelf
    spawn_sm(shapes["cube"], (-2400, 0, 35), scale=(70, 360, 1.1), label="AAA_World_Landmass", mat=mats["terrain"])
    # Beach bands
    spawn_sm(shapes["cube"], (-980, 0, 18), scale=(10, 340, 0.35), label="AAA_World_Beach", mat=mats["beach"])
    spawn_sm(shapes["cube"], (-860, 0, 12), scale=(4, 340, 0.2), label="AAA_World_WetSand", mat=mats["wet_sand"])
    # Coastal road / promenade
    spawn_sm(shapes["cube"], (-1180, 0, 28), scale=(3.2, 300, 0.18), label="AAA_World_Promenade", mat=mats["asphalt"])
    # Harbor piers
    for i, y in enumerate([-1600, -400, 900, 1800]):
        spawn_sm(shapes["cube"], (-700, y, 40), scale=(12, 1.5, 0.4), label=f"AAA_World_Pier_{i}", mat=mats["wood"])
        spawn_sm(shapes["cube"], (-350, y, 70), scale=(0.7, 0.7, 3.5), label=f"AAA_World_Crane_{i}", mat=mats["metal_rust"])
        spawn_sm(shapes["cube"], (-350, y, 160), scale=(4.5, 0.5, 0.4), label=f"AAA_World_CraneArm_{i}", mat=mats["metal_rust"])

    # Dense city districts
    rng = 0
    for district in range(3):
        base_x = -1900 - district * 420
        for i in range(22):
            for j in range(5):
                rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
                h = 3 + (rng % 16)
                if (i + j + district) % 7 == 0:
                    h += 8  # landmark towers
                x = base_x - j * 280
                y = -2800 + i * 270 + district * 40
                z = h * 55
                mat = mats["city_glass"] if h > 12 else mats["city"]
                spawn_sm(
                    shapes["cube"],
                    (x, y, z),
                    scale=(2.4 + (rng % 3) * 0.15, 2.1 + (rng % 2) * 0.2, h),
                    label=f"AAA_World_Bld_{district}_{i}_{j}",
                    mat=mat,
                )
                # rooftop AC / clutter proxies
                if h > 6 and (rng % 3 == 0):
                    spawn_sm(
                        shapes["cube"],
                        (x, y, z * 2 + 40),
                        scale=(0.6, 0.6, 0.35),
                        label=f"AAA_World_Roof_{district}_{i}_{j}",
                        mat=mats["metal"],
                    )

    # Tree / vegetation proxies along coast
    for i in range(40):
        y = -2500 + i * 130
        spawn_sm(
            shapes["cylinder"],
            (-1300, y, 70),
            scale=(0.25, 0.25, 1.4 + (i % 4) * 0.2),
            label=f"AAA_World_Trunk_{i}",
            mat=mats["bark"],
        )
        spawn_sm(
            shapes["sphere"],
            (-1300, y, 160 + (i % 3) * 10),
            scale=(1.2, 1.2, 0.9),
            label=f"AAA_World_Canopy_{i}",
            mat=mats["foliage"],
        )


def build_yak(mats, shapes):
    # Layered airframe hierarchy near origin, nose along +Y (Unreal forward)
    spawn_sm(shapes["cylinder"], (0, 40, 320), unreal.Rotator(0, 0, 90), (1.35, 1.35, 9.5), "AAA_Yak_Fuselage", mats["airframe"])
    spawn_sm(shapes["sphere"], (0, -420, 320), None, (1.3, 1.6, 1.3), "AAA_Yak_Nose", mats["airframe"])
    spawn_sm(shapes["cube"], (0, 0, 305), None, (16, 2.0, 0.18), "AAA_Yak_Wing", mats["airframe"])
    spawn_sm(shapes["cube"], (0, 420, 390), None, (0.18, 1.3, 2.6), "AAA_Yak_Fin", mats["airframe"])
    spawn_sm(shapes["cube"], (0, 400, 330), None, (4.5, 1.2, 0.14), "AAA_Yak_Stab", mats["airframe"])
    # Open cockpit rails / bows
    for i, y in enumerate([-160, -80, 0, 80, 160]):
        spawn_sm(shapes["cylinder"], (0, y, 365), unreal.Rotator(0, 0, 90), (1.15, 0.08, 0.08), f"AAA_Yak_Bow_{i}", mats["metal"])
    # Pilot canopy glass (front)
    spawn_sm(shapes["sphere"], (0, -90, 370), None, (1.0, 1.4, 0.7), "AAA_Yak_CanopyFront", mats["glass"])
    # Rear gunner open section (no full enclosure)
    spawn_sm(shapes["cube"], (0, 70, 350), None, (1.5, 1.8, 0.08), "AAA_Yak_GunnerFloor", mats["cockpit"])
    # Instrument panel proxy
    spawn_sm(shapes["cube"], (0, -20, 355), None, (1.2, 0.15, 0.55), "AAA_Yak_Panel", mats["cockpit"])
    for i, x in enumerate([-20, 0, 20]):
        spawn_sm(shapes["cylinder"], (x, -18, 365), None, (0.08, 0.08, 0.02), f"AAA_Yak_Gauge_{i}", mats["gauge"])
    # Rifle + glove proxy in gunner space
    spawn_sm(shapes["cube"], (18, 90, 360), unreal.Rotator(0, 12, 8), (0.08, 1.15, 0.08), "AAA_Yak_RifleBarrel", mats["rifle"])
    spawn_sm(shapes["cube"], (18, 50, 358), unreal.Rotator(0, 12, 8), (0.16, 0.35, 0.14), "AAA_Yak_RifleBody", mats["rifle"])
    spawn_sm(shapes["sphere"], (22, 55, 354), None, (0.12, 0.16, 0.1), "AAA_Yak_Glove", mats["leather"])
    # Prop disc
    spawn_sm(shapes["cylinder"], (0, -520, 320), unreal.Rotator(0, 0, 90), (1.8, 1.8, 0.05), "AAA_Yak_PropDisc", mats["prop"])


def build_drones(mats, shapes):
    # Denser inbound formations over water
    lanes = [-900, -450, 0, 450, 900, 1350, 1800]
    for lane_i, y in enumerate(lanes):
        for n in range(5):
            x = 1800 + n * 520 + (lane_i % 2) * 160
            z = 380 + (n % 3) * 45 + (lane_i % 2) * 20
            body = spawn_sm(
                shapes["cone"],
                (x, y, z),
                unreal.Rotator(0, -90, 0),
                (1.2, 1.2, 3.4),
                f"AAA_Drone_Body_{lane_i}_{n}",
                mats["drone"],
            )
            spawn_sm(
                shapes["cube"],
                (x - 40, y, z),
                None,
                (2.8, 0.15, 0.08),
                f"AAA_Drone_Wing_{lane_i}_{n}",
                mats["drone"],
            )
            # exhaust glow proxy
            spawn_sm(
                shapes["sphere"],
                (x + 120, y, z),
                None,
                (0.2, 0.2, 0.2),
                f"AAA_Drone_Exhaust_{lane_i}_{n}",
                mats["exhaust"],
            )


def build_review_cameras():
    cams = [
        ("AAA_Cam_Cockpit", (25, 95, 368), unreal.Rotator(-8, 5, 0)),
        ("AAA_Cam_ADS", (18, 110, 362), unreal.Rotator(-3, 8, 0)),
        ("AAA_Cam_ExteriorChase", (600, -900, 520), unreal.Rotator(-12, 130, 0)),
        ("AAA_Cam_CityInbound", (2500, 200, 700), unreal.Rotator(-15, -175, 0)),
        ("AAA_Cam_CoastWide", (800, -2200, 900), unreal.Rotator(-20, 50, 0)),
    ]
    for name, loc, rot in cams:
        cam = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(*loc), rot
        )
        if cam:
            cam.set_actor_label(name)


def ensure_bps():
    for name, parent in [
        ("BP_SkyguardGunner", unreal.Character),
        ("BP_ShahedDrone", unreal.Actor),
        ("BP_DroneSpawner", unreal.Actor),
        ("BP_SkyguardGameMode", unreal.GameModeBase),
        ("BP_SkyguardPlayerController", unreal.PlayerController),
        ("BP_SkyguardHUD", unreal.HUD),
    ]:
        path = f"{BP_ROOT}/{name}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            continue
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, BP_ROOT, unreal.Blueprint, factory)
        save_asset(bp)


def main():
    log("AAA foundation pass starting")
    for p in [ASSET_ROOT, MAT_ROOT, BP_ROOT, MESH_ROOT, REVIEW_ROOT, f"{ASSET_ROOT}/Maps", f"{ASSET_ROOT}/UI"]:
        ensure_dir(p)

    # Load or create map
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        unreal.EditorLevelLibrary.load_level(MAP_PATH)
        log(f"Loaded {MAP_PATH}")
    else:
        unreal.EditorLevelLibrary.new_level(MAP_PATH)
        log(f"Created {MAP_PATH}")

    mats = {
        "ocean": create_material("M_Ocean", (0.03, 0.14, 0.22), roughness=0.18, metallic=0.08, specular=0.7),
        "ocean_deep": create_material("M_OceanDeep", (0.01, 0.05, 0.10), roughness=0.22, metallic=0.05, specular=0.65),
        "beach": create_material("M_Beach", (0.72, 0.62, 0.42), roughness=0.92),
        "wet_sand": create_material("M_WetSand", (0.35, 0.30, 0.22), roughness=0.35, specular=0.6),
        "terrain": create_material("M_Terrain", (0.28, 0.30, 0.18), roughness=0.95),
        "city": create_material("M_CityConcrete", (0.38, 0.37, 0.35), roughness=0.82),
        "city_glass": create_material("M_CityGlass", (0.18, 0.24, 0.30), roughness=0.12, metallic=0.1, specular=0.9, emissive=(0.02, 0.03, 0.04)),
        "asphalt": create_material("M_Asphalt", (0.07, 0.07, 0.07), roughness=0.88),
        "wood": create_material("M_PierWood", (0.28, 0.18, 0.10), roughness=0.8),
        "metal": create_material("M_Metal", (0.45, 0.45, 0.47), roughness=0.35, metallic=0.85),
        "metal_rust": create_material("M_MetalRust", (0.28, 0.16, 0.08), roughness=0.7, metallic=0.55),
        "airframe": create_material("M_YakAirframe", (0.58, 0.60, 0.55), roughness=0.42, metallic=0.4),
        "glass": create_material("M_CockpitGlass", (0.55, 0.65, 0.7), roughness=0.05, metallic=0.0, specular=1.0),
        "cockpit": create_material("M_CockpitInterior", (0.16, 0.14, 0.11), roughness=0.78),
        "gauge": create_material("M_GaugeGlass", (0.7, 0.75, 0.8), roughness=0.08, emissive=(0.05, 0.08, 0.04)),
        "rifle": create_material("M_RifleTan", (0.42, 0.35, 0.2), roughness=0.55, metallic=0.25),
        "leather": create_material("M_LeatherGlove", (0.12, 0.07, 0.04), roughness=0.7),
        "prop": create_material("M_PropDisc", (0.15, 0.15, 0.15), roughness=0.5, metallic=0.2),
        "drone": create_material("M_ShahedDrone", (0.1, 0.12, 0.1), roughness=0.55, metallic=0.25),
        "exhaust": create_material("M_ExhaustGlow", (0.6, 0.15, 0.02), roughness=0.4, emissive=(2.5, 0.5, 0.05)),
        "bark": create_material("M_Bark", (0.18, 0.11, 0.06), roughness=0.9),
        "foliage": create_material("M_Foliage", (0.12, 0.28, 0.08), roughness=0.85),
    }

    shapes = {
        "cube": shape("/Engine/BasicShapes/Cube"),
        "sphere": shape("/Engine/BasicShapes/Sphere"),
        "cylinder": shape("/Engine/BasicShapes/Cylinder"),
        "cone": shape("/Engine/BasicShapes/Cone"),
        "plane": shape("/Engine/BasicShapes/Plane"),
    }

    ensure_bps = True
    if ensure_bps:
        # blueprints
        for name, parent in [
            ("BP_SkyguardGunner", unreal.Character),
            ("BP_ShahedDrone", unreal.Actor),
            ("BP_DroneSpawner", unreal.Actor),
            ("BP_SkyguardGameMode", unreal.GameModeBase),
            ("BP_SkyguardPlayerController", unreal.PlayerController),
            ("BP_SkyguardHUD", unreal.HUD),
        ]:
            path = f"{BP_ROOT}/{name}"
            if not unreal.EditorAssetLibrary.does_asset_exist(path):
                factory = unreal.BlueprintFactory()
                factory.set_editor_property("parent_class", parent)
                bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, BP_ROOT, unreal.Blueprint, factory)
                save_asset(bp)

    build_atmosphere()
    build_world(mats, shapes)
    build_yak(mats, shapes)
    build_drones(mats, shapes)
    build_review_cameras()

    # Player start near gunner
    # destroy old unlabeled clutter starts if needed
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(20, 95, 360), unreal.Rotator(0, 0, 0)
    )
    if ps:
        ps.set_actor_label("AAA_GunnerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory(ASSET_ROOT, only_if_is_dirty=False, recursive=True)
    log("AAA foundation pass complete")
    log("Open Lvl_SkyguardCoast and inspect AAA_Cam_* cameras")
    log("CRITIC REQUIRED: this is still geometric proxy stage, not finished AAA")


if __name__ == "__main__":
    main()
