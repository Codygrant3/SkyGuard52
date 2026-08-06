import hashlib
import os
import time

import unreal


MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"
YAK_ROOT = (
    "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit/"
    "yak52-detail-kit-blender/StaticMeshes"
)
PREFIX = "AAA_L87_"
CAM_PREFIX = "AAA_Cam_L87_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L87"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L86"
STAGE = unreal.Vector(100000.0, 100000.0, 5000.0)
AIRCRAFT_SCALE = unreal.Vector(0.35164835, 0.35164835, 0.35164835)


def log(message):
    unreal.log(f"[SkyguardAAA] {message}")


def asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def actors():
    return unreal.get_editor_subsystem(
        unreal.EditorActorSubsystem
    ).get_all_level_actors()


def clear_owned():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    owned = [
        actor
        for actor in actors()
        if actor.get_actor_label().startswith(("AAA_L", "AAA_Cam_L"))
    ]
    if owned and subsystem.destroy_actors(owned) is False:
        raise RuntimeError("failed to clear prior AAA loop actors")
    log(f"loop87 cleared prior loop actors={len(owned)}")


def clear_prior_after_capture():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    prior = []
    for actor in actors():
        label = actor.get_actor_label()
        if not label.startswith(("AAA_L", "AAA_Cam_L")):
            continue
        if label.startswith((PREFIX, CAM_PREFIX)):
            continue
        prior.append(actor)
    if prior and subsystem.destroy_actors(prior) is False:
        raise RuntimeError("failed to clear prior loops after L87 capture")
    log(f"loop87 post-capture prior actors cleared={len(prior)}")


def spawn_mesh(mesh, location, scale, label, rotation=None, material=None):
    if not mesh:
        raise RuntimeError(f"missing mesh: {label}")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        rotation or unreal.Rotator(),
    )
    if not actor:
        raise RuntimeError(f"failed to spawn: {label}")
    actor.set_actor_label(label)
    actor.set_actor_scale3d(scale)
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_editor_property("cast_shadow", True)
    if material:
        for index in range(max(1, component.get_num_materials())):
            component.set_material(index, material)
    return actor


def production_yak_assets():
    result = []
    for path in sorted(
        unreal.EditorAssetLibrary.list_assets(
            YAK_ROOT,
            recursive=False,
            include_folder=False,
        )
    ):
        name = path.rsplit("/", 1)[-1].split(".", 1)[0]
        if name.startswith(("production-yak52", "production-rear")):
            mesh = asset(path)
            if mesh:
                result.append((name, mesh))
    if len(result) != 19:
        raise RuntimeError(f"expected exactly 19 production Yak meshes, found {len(result)}")
    return result


def build_stage():
    cube = asset("/Engine/BasicShapes/Cube")
    concrete = (
        asset("/Game/Skyguard/Materials/M_Tex_L8_plaster2")
        or asset("/Game/Skyguard/Materials/M_CityConcrete")
    )
    spawn_mesh(
        cube,
        STAGE + unreal.Vector(0.0, 0.0, -310.0),
        unreal.Vector(35.0, 35.0, 0.25),
        PREFIX + "StudioFloor",
        material=concrete,
    )
    spawn_mesh(
        cube,
        STAGE + unreal.Vector(-1850.0, 0.0, 700.0),
        unreal.Vector(0.25, 35.0, 15.0),
        PREFIX + "StudioBackdrop",
        material=concrete,
    )

    for name, mesh in production_yak_assets():
        spawn_mesh(
            mesh,
            STAGE,
            AIRCRAFT_SCALE,
            PREFIX + "Yak_" + name[:58],
        )
    log("loop87 assembled exactly 19 production Yak meshes")

    prop = asset("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    if prop:
        spawn_mesh(
            prop,
            STAGE + unreal.Vector(0.0, -635.0, -34.0),
            unreal.Vector(105.0, 105.0, 105.0),
            PREFIX + "Propeller",
            unreal.Rotator(0.0, 0.0, 90.0),
            asset("/Game/Skyguard/Materials/M_PropDisc"),
        )


def look_at(location, target):
    return unreal.MathLibrary.find_look_at_rotation(location, target)


def build_lighting():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        STAGE + unreal.Vector(0.0, 0.0, 5000.0),
        unreal.Rotator(-42.0, 28.0, 0.0),
    )
    sun.set_actor_label(PREFIX + "Sun")
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sun_component.set_editor_property("intensity", 8.0)
    sun_component.set_editor_property(
        "light_color",
        unreal.Color(255, 238, 218, 255),
    )

    for label, offset, intensity, color in (
        (
            "Key",
            unreal.Vector(1200.0, -900.0, 1250.0),
            85000.0,
            unreal.Color(255, 225, 195, 255),
        ),
        (
            "Fill",
            unreal.Vector(900.0, 850.0, 650.0),
            50000.0,
            unreal.Color(185, 215, 255, 255),
        ),
        (
            "Rim",
            unreal.Vector(-1000.0, 300.0, 950.0),
            65000.0,
            unreal.Color(225, 235, 255, 255),
        ),
    ):
        location = STAGE + offset
        light = subsystem.spawn_actor_from_class(
            unreal.RectLight,
            location,
            look_at(location, STAGE),
        )
        light.set_actor_label(PREFIX + label)
        component = light.get_component_by_class(unreal.RectLightComponent)
        component.set_editor_property("intensity", intensity)
        component.set_editor_property("source_width", 700.0)
        component.set_editor_property("source_height", 500.0)
        component.set_editor_property("attenuation_radius", 6000.0)
        component.set_editor_property("light_color", color)


def render_target(world):
    # Keep Loop86's saved SceneCapture2D actor alive until L87 exports finish.
    # That actor owns the active RHI resource in a headless commandlet.
    target = asset(RT_PATH)
    if not target:
        raise RuntimeError(f"missing proven render target: {RT_PATH}")
    return target


def camera_specs():
    return (
        (
            "YakSide",
            STAGE + unreal.Vector(1750.0, 0.0, 360.0),
            STAGE + unreal.Vector(0.0, 0.0, 0.0),
            48.0,
        ),
        (
            "YakFront",
            STAGE + unreal.Vector(700.0, -1750.0, 380.0),
            STAGE + unreal.Vector(0.0, -120.0, 0.0),
            48.0,
        ),
        (
            "YakRear",
            STAGE + unreal.Vector(850.0, 1700.0, 420.0),
            STAGE + unreal.Vector(0.0, 150.0, 20.0),
            50.0,
        ),
        (
            "CockpitProbe",
            STAGE + unreal.Vector(520.0, 150.0, 360.0),
            STAGE + unreal.Vector(0.0, 60.0, 40.0),
            55.0,
        ),
    )


def capture():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename in os.listdir(OUT_DIR):
        if filename.startswith(CAM_PREFIX) and filename.endswith(".png"):
            os.remove(os.path.join(OUT_DIR, filename))

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(
        unreal.UnrealEditorSubsystem
    ).get_editor_world()
    if not world:
        raise RuntimeError("editor world unavailable")
    capture_actor = None
    component = None
    target = None
    for candidate in actors():
        if not isinstance(candidate, unreal.SceneCapture2D):
            continue
        candidate_component = candidate.get_editor_property("capture_component2d")
        candidate_target = candidate_component.get_editor_property("texture_target")
        if candidate_target:
            capture_actor = candidate
            component = candidate_component
            target = candidate_target
            break
    if not capture_actor or not component or not target:
        raise RuntimeError("no live saved SceneCapture2D/target pair available")
    capture_actor.set_actor_label(PREFIX + "SceneCapture")
    target.set_editor_property("size_x", 1920)
    target.set_editor_property("size_y", 1080)
    target.set_editor_property(
        "render_target_format",
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    unreal.EditorAssetLibrary.save_loaded_asset(target)
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property(
        "primitive_render_mode",
        unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES,
    )
    component.set_editor_property(
        "capture_source",
        unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR,
    )
    # Resource initialization is queued to the render thread. Loop86's large
    # cleanup naturally supplied this window; the compact probe must do so.
    time.sleep(3.0)
    saved = []
    for name, location, target_location, fov in camera_specs():
        rotation = look_at(location, target_location)
        camera = subsystem.spawn_actor_from_class(
            unreal.CameraActor,
            location,
            rotation,
        )
        camera.set_actor_label(CAM_PREFIX + name)
        camera.get_component_by_class(unreal.CameraComponent).set_editor_property(
            "field_of_view",
            fov,
        )
        capture_actor.set_actor_location(location, False, True)
        capture_actor.set_actor_rotation(rotation, False)
        component.set_editor_property("fov_angle", fov)
        component.capture_scene()
        component.capture_scene()
        filename = f"{CAM_PREFIX}{name}_FINAL.png"
        unreal.RenderingLibrary.export_render_target(
            world,
            target,
            OUT_DIR,
            filename,
        )
        path = os.path.join(OUT_DIR, filename)
        if not os.path.isfile(path) or os.path.getsize(path) < 1000:
            raise RuntimeError(f"invalid capture: {path}")
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        saved.append((filename, os.path.getsize(path), digest))
        log(f"loop87 still={filename} sha={digest[:16]}")

    manifest = os.path.join(OUT_DIR, "MANIFEST_SHA256.txt")
    with open(manifest, "w", encoding="utf-8", newline="\n") as stream:
        stream.write("Skyguard AAA Loop87 isolated aircraft truth stage\n")
        stream.write(f"time={time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        stream.write("gate=visual_probe_not_promotion\n")
        for filename, size, digest in saved:
            stream.write(f"{digest}  {size}  {filename}\n")
        stream.write(f"total={len(saved)}\n")
    return saved


def main():
    log("loop87 isolated aircraft truth stage start")
    if not unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH):
        raise RuntimeError(f"failed to load map: {MAP_PATH}")
    log("loop87 preserving prior capture owner until exports validate")
    build_stage()
    build_lighting()
    saved = capture()
    clear_prior_after_capture()
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log(f"Loop87 complete stills={len(saved)}")
    log("CRITIC: isolated aircraft visuals require direct human/agent review")


main()
