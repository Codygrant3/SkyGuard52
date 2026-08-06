import hashlib
import os
import time
import unreal


MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"
PREFIX = "AAA_L86_"
CAM_PREFIX = "AAA_Cam_L86_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L86"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L86"
YAK_ROOT = (
    "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit/"
    "yak52-detail-kit-blender/StaticMeshes"
)


def log(message):
    unreal.log(f"[SkyguardAAA] {message}")


def load_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def ensure_directory(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def spawn_static_mesh(mesh, location, scale, label, rotation=None, material=None):
    if not mesh:
        raise RuntimeError(f"missing mesh for {label}")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
        rotation or unreal.Rotator(),
    )
    if not actor:
        raise RuntimeError(f"failed to spawn {label}")
    actor.set_actor_label(label)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_editor_property("cast_shadow", True)
    if material:
        component.set_material(0, material)
    return actor


def clear_owned_loop_actors():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    owned = [
        actor
        for actor in actors
        if actor.get_actor_label().startswith(("AAA_L", "AAA_Cam_L"))
    ]
    if owned:
        destroyed = subsystem.destroy_actors(owned)
        if destroyed is False:
            raise RuntimeError("batch destroy of owned loop actors failed")
    log(f"loop86 cleared owned loop actors={len(owned)}")


def production_yak_assets():
    assets = unreal.EditorAssetLibrary.list_assets(
        YAK_ROOT,
        recursive=False,
        include_folder=False,
    )
    result = []
    for path in sorted(assets):
        name = path.rsplit("/", 1)[-1].split(".", 1)[0]
        if name.startswith("production-yak52") or name.startswith("production-rear"):
            mesh = load_asset(path)
            if mesh:
                result.append((name, mesh))
    if len(result) < 19:
        raise RuntimeError(
            f"production Yak package incomplete: expected >=19, found {len(result)}"
        )
    return result


def build_aircraft_and_cockpit():
    origin = (0.0, 0.0, 500.0)
    scale = (0.35164835, 0.35164835, 0.35164835)
    yak_assets = production_yak_assets()
    for name, mesh in yak_assets:
        spawn_static_mesh(
            mesh,
            origin,
            scale,
            PREFIX + "Yak_" + name[:56],
        )
    log(f"loop86 production Yak meshes placed={len(yak_assets)}")

    prop = load_asset("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    if prop:
        spawn_static_mesh(
            prop,
            (0.0, -635.0, 466.0),
            (105.0, 105.0, 105.0),
            PREFIX + "Propeller",
            unreal.Rotator(0.0, 0.0, 90.0),
            load_asset("/Game/Skyguard/Materials/M_PropDisc"),
        )

    weapon_origin = (18.0, 12.0, 555.0)
    for asset_path, suffix, scale_value in (
        (
            "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde",
            "Rifle",
            0.62,
        ),
        (
            "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove",
            "Glove",
            0.62,
        ),
        (
            "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve",
            "Sleeve",
            0.62,
        ),
    ):
        mesh = load_asset(asset_path)
        if mesh:
            spawn_static_mesh(
                mesh,
                weapon_origin,
                (scale_value, scale_value, scale_value),
                PREFIX + suffix,
            )


def build_drones():
    assets = {}
    for name in ("body", "wing", "fins", "motor"):
        path = (
            "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/"
            f"drone-{name}"
        )
        assets[name] = load_asset(path)
    if not assets["body"] or not assets["wing"]:
        raise RuntimeError("web Shahed asset package is incomplete")

    positions = (
        (1700.0, -650.0, 650.0),
        (2150.0, -150.0, 710.0),
        (2550.0, 500.0, 770.0),
        (3100.0, 1050.0, 840.0),
    )
    for index, location in enumerate(positions):
        for part, mesh in assets.items():
            if mesh:
                spawn_static_mesh(
                    mesh,
                    location,
                    (0.78, 0.78, 0.78),
                    f"{PREFIX}Drone_{index}_{part}",
                    unreal.Rotator(),
                )
    log(f"loop86 production drone assemblies placed={len(positions)}")


def build_world_hero_additions():
    materials = {
        "concrete": load_asset("/Game/Skyguard/Materials/M_Tex_L8_plaster2")
        or load_asset("/Game/Skyguard/Materials/M_CityConcrete"),
        "brick": load_asset("/Game/Skyguard/Materials/M_Tex_L3_brick2")
        or load_asset("/Game/Skyguard/Materials/M_Brick"),
        "ocean": load_asset("/Game/Skyguard/Materials/M_Ocean"),
        "beach": load_asset("/Game/Skyguard/Materials/M_Tex_L7_beach2")
        or load_asset("/Game/Skyguard/Materials/M_Beach"),
        "metal": load_asset("/Game/Skyguard/Materials/M_Metal"),
        "rust": load_asset("/Game/Skyguard/Materials/M_MetalRust"),
    }
    city_meshes = (
        load_asset("/Game/Skyguard/Meshes/Hero/facade_tower_proxy"),
        load_asset("/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy"),
        load_asset("/Game/Skyguard/Meshes/Hero/coast_block_proxy"),
    )
    city_positions = (
        (-2200.0, -1050.0, 90.0, 115.0),
        (-2450.0, -300.0, 80.0, 95.0),
        (-2050.0, 500.0, 70.0, 105.0),
        (-2550.0, 1150.0, 95.0, 120.0),
        (-1750.0, 1500.0, 65.0, 90.0),
    )
    for index, (x, y, z, size) in enumerate(city_positions):
        mesh = city_meshes[index % len(city_meshes)]
        if mesh:
            spawn_static_mesh(
                mesh,
                (x, y, z),
                (size, size, size),
                f"{PREFIX}CityHero_{index}",
                unreal.Rotator(0.0, float((index * 23) % 70 - 35), 0.0),
                materials["concrete"] if index % 2 == 0 else materials["brick"],
            )

    for index, (path, location, scale, material_key) in enumerate(
        (
            (
                "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy",
                (-520.0, -650.0, 80.0),
                (70.0, 70.0, 70.0),
                "rust",
            ),
            (
                "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy",
                (-520.0, 350.0, 80.0),
                (78.0, 78.0, 78.0),
                "metal",
            ),
            (
                "/Game/Skyguard/Meshes/Hero/container_ship_proxy",
                (260.0, 700.0, 38.0),
                (92.0, 92.0, 92.0),
                "metal",
            ),
            (
                "/Game/Skyguard/Meshes/Hero/submarine_proxy",
                (720.0, -650.0, 32.0),
                (92.0, 92.0, 92.0),
                "metal",
            ),
        )
    ):
        mesh = load_asset(path)
        if mesh:
            spawn_static_mesh(
                mesh,
                location,
                scale,
                f"{PREFIX}HarborHero_{index}",
                unreal.Rotator(),
                materials[material_key],
            )

    plane = load_asset("/Engine/BasicShapes/Plane")
    cube = load_asset("/Engine/BasicShapes/Cube")
    if plane and materials["ocean"]:
        for index, x in enumerate((200.0, 1200.0, 2200.0)):
            spawn_static_mesh(
                plane,
                (x, 0.0, -2.0),
                (22.0, 70.0, 1.0),
                f"{PREFIX}OceanTruth_{index}",
                unreal.Rotator(),
                materials["ocean"],
            )
    if cube and materials["beach"]:
        spawn_static_mesh(
            cube,
            (-900.0, 0.0, 12.0),
            (7.0, 70.0, 0.3),
            PREFIX + "BeachTruth",
            unreal.Rotator(),
            materials["beach"],
        )


def build_lighting():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 3500.0),
        unreal.Rotator(-32.0, 28.0, 0.0),
    )
    if not sun:
        raise RuntimeError("failed to spawn loop86 sun")
    sun.set_actor_label(PREFIX + "Sun")
    light = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if light:
        light.set_editor_property("intensity", 5.5)
        light.set_editor_property("light_color", unreal.Color(255, 232, 205, 255))

    sky = subsystem.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0.0, 0.0, 1800.0),
        unreal.Rotator(),
    )
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        component = sky.get_component_by_class(unreal.SkyLightComponent)
        if component:
            component.set_editor_property("intensity", 1.25)
            try:
                component.set_editor_property("real_time_capture", True)
            except Exception:
                pass

    fill = subsystem.spawn_actor_from_class(
        unreal.RectLight,
        unreal.Vector(420.0, -520.0, 1050.0),
        unreal.Rotator(-25.0, 145.0, 0.0),
    )
    if fill:
        fill.set_actor_label(PREFIX + "HeroFill")
        component = fill.get_component_by_class(unreal.RectLightComponent)
        if component:
            component.set_editor_property("intensity", 35000.0)
            component.set_editor_property("source_width", 500.0)
            component.set_editor_property("source_height", 320.0)
            component.set_editor_property("attenuation_radius", 5000.0)


def camera_specs():
    return (
        ("Prop", (420.0, -1050.0, 540.0), (0.0, -610.0, 475.0), 52.0),
        ("PropHub", (0.0, -930.0, 500.0), (0.0, -625.0, 470.0), 42.0),
        ("PropNose", (-460.0, -1020.0, 590.0), (0.0, -500.0, 485.0), 52.0),
        ("YakBeauty", (1320.0, -1180.0, 920.0), (0.0, 120.0, 480.0), 48.0),
        ("Cockpit", (0.0, 8.0, 590.0), (0.0, -420.0, 485.0), 72.0),
        ("ADS", (0.0, 18.0, 568.0), (0.0, -720.0, 530.0), 44.0),
        ("City", (250.0, -1800.0, 920.0), (-2200.0, 120.0, 330.0), 58.0),
        ("Combat", (280.0, -500.0, 720.0), (2250.0, 150.0, 720.0), 55.0),
        ("Harbor", (-120.0, -1600.0, 560.0), (-420.0, 100.0, 100.0), 62.0),
        ("Ocean", (1800.0, -1800.0, 760.0), (650.0, 100.0, 10.0), 65.0),
        ("Wide", (1900.0, -2300.0, 1280.0), (-250.0, 100.0, 320.0), 65.0),
    )


def look_at(location, target):
    return unreal.MathLibrary.find_look_at_rotation(
        unreal.Vector(*location),
        unreal.Vector(*target),
    )


def build_render_target():
    ensure_directory("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        target = load_asset(RT_PATH)
    else:
        target = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L86",
            "/Game/Skyguard/Capture",
            unreal.TextureRenderTarget2D,
            unreal.TextureRenderTargetFactoryNew(),
        )
    if not target:
        raise RuntimeError("failed to create/load L86 render target")
    target.set_editor_property("size_x", 1920)
    target.set_editor_property("size_y", 1080)
    target.set_editor_property(
        "render_target_format",
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    unreal.EditorAssetLibrary.save_loaded_asset(target)
    return target


def validate_existing_output_names():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, _location, _target, _fov in camera_specs():
        for source in ("BASE", "FINAL", "SCENE"):
            path = os.path.join(OUT_DIR, f"{CAM_PREFIX}{name}_{source}.png")
            if os.path.isfile(path):
                os.remove(path)
    manifest = os.path.join(OUT_DIR, "MANIFEST_SHA256.txt")
    if os.path.isfile(manifest):
        os.remove(manifest)


def capture_truth_views():
    validate_existing_output_names()
    target = build_render_target()
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    for name, location, aim, fov in camera_specs():
        actor = subsystem.spawn_actor_from_class(
            unreal.CameraActor,
            unreal.Vector(*location),
            look_at(location, aim),
        )
        if not actor:
            raise RuntimeError(f"failed to create camera {name}")
        actor.set_actor_label(CAM_PREFIX + name)
        component = actor.get_component_by_class(unreal.CameraComponent)
        if component:
            component.set_editor_property("field_of_view", fov)

    capture_actor = subsystem.spawn_actor_from_class(
        unreal.SceneCapture2D,
        unreal.Vector(0.0, 0.0, 500.0),
        unreal.Rotator(),
    )
    if not capture_actor:
        raise RuntimeError("failed to spawn L86 SceneCapture2D")
    capture_actor.set_actor_label(PREFIX + "SceneCapture")
    component = capture_actor.get_editor_property("capture_component2d")
    if not component:
        raise RuntimeError("L86 SceneCapture2D has no capture component")
    component.set_editor_property("texture_target", target)
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property(
        "primitive_render_mode",
        unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES,
    )

    world = unreal.get_editor_subsystem(
        unreal.UnrealEditorSubsystem
    ).get_editor_world()
    if not world:
        raise RuntimeError("editor world unavailable for L86 capture")

    sources = (
        ("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR),
        ("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR),
        ("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR),
    )
    saved = []
    for name, location, aim, fov in camera_specs():
        rotation = look_at(location, aim)
        capture_actor.set_actor_location(unreal.Vector(*location), False, True)
        capture_actor.set_actor_rotation(rotation, False)
        component.set_editor_property("fov_angle", fov)
        log(
            f"CAM {CAM_PREFIX}{name} loc={location} target={aim} "
            f"rotation={rotation} fov={fov}"
        )
        for source_name, source in sources:
            component.set_editor_property("capture_source", source)
            component.capture_scene()
            component.capture_scene()
            filename = f"{CAM_PREFIX}{name}_{source_name}.png"
            unreal.RenderingLibrary.export_render_target(
                world,
                target,
                OUT_DIR,
                filename,
            )
            path = os.path.join(OUT_DIR, filename)
            if not os.path.isfile(path):
                raise RuntimeError(f"capture export missing: {path}")
            size = os.path.getsize(path)
            if size < 1000:
                raise RuntimeError(f"capture export too small: {path} ({size})")
            digest = hashlib.sha256()
            with open(path, "rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            saved.append((path, size, digest.hexdigest(), source_name, CAM_PREFIX + name))
            log(
                f"still {filename} size={size} sha={saved[-1][2][:16]}"
            )

    if len(saved) != 33:
        raise RuntimeError(f"L86 expected 33 captures, produced {len(saved)}")
    manifest_path = os.path.join(OUT_DIR, "MANIFEST_SHA256.txt")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as manifest:
        manifest.write("Skyguard AAA Loop86 truth-capture stills\n")
        manifest.write(f"time={time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        manifest.write("note=real_subject_truth_capture_no_checker_scoring_geometry\n")
        for path, size, digest, source, camera in saved:
            manifest.write(
                f"{digest}  {size}  src={source} cam={camera}  {path}\n"
            )
        manifest.write(f"total={len(saved)}\n")
    log(f"manifest total={len(saved)}")
    return saved


def main():
    log("loop86 truth-capture reset start")
    if not unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH):
        raise RuntimeError(f"failed to load {MAP_PATH}")
    clear_owned_loop_actors()
    build_aircraft_and_cockpit()
    build_drones()
    build_world_hero_additions()
    build_lighting()
    saved = capture_truth_views()
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log(f"Loop86 complete stills={len(saved)}")
    log("CRITIC: visual truth review required; structural pass cannot promote art")


main()
