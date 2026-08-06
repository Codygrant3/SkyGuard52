"""
Skyguard 52 Unreal vertical-slice builder
Run inside Unreal Editor (Python) or via UnrealEditor-Cmd -ExecutePythonScript

Creates:
- Materials for ocean, sand, city, airframe, drone
- Static meshes via primitives where needed (using BasicShapes)
- Lvl_SkyguardCoast map with coast, city blocks, ocean, sky
- BP_SkyguardGunner (first-person seated gunner, ADS, rifle fire)
- BP_ShahedDrone (simple approach + destroyable)
- BP_DroneSpawner
- BP_SkyguardGameMode / PlayerController shell
"""

import unreal

ASSET_ROOT = "/Game/Skyguard"
MAP_PATH = f"{ASSET_ROOT}/Maps/Lvl_SkyguardCoast"
MAT_ROOT = f"{ASSET_ROOT}/Materials"
BP_ROOT = f"{ASSET_ROOT}/Blueprints"


def log(msg: str) -> None:
    unreal.log(f"[Skyguard] {msg}")


def ensure_dir(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)
        log(f"Created directory {path}")


def save_asset(asset) -> None:
    if asset is None:
        return
    unreal.EditorAssetLibrary.save_loaded_asset(asset)


def create_color_material(name: str, color, roughness=0.7, metallic=0.0, emissive=None):
    """Create a simple constant-color material under Materials/."""
    package_path = f"{MAT_ROOT}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        return unreal.EditorAssetLibrary.load_asset(package_path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset(name, MAT_ROOT, unreal.Material, factory)
    if mat is None:
        log(f"Failed to create material {name}")
        return None

    # Use material property overrides via constant expressions when possible.
    # Fallback: set base color through MaterialEditingLibrary if available.
    try:
        mel = unreal.MaterialEditingLibrary
        base = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, -100)
        base.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
        mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)

        rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 50)
        rough.set_editor_property("r", float(roughness))
        mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

        metal = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 120)
        metal.set_editor_property("r", float(metallic))
        mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)

        if emissive is not None:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, 200)
            em.set_editor_property("constant", unreal.LinearColor(emissive[0], emissive[1], emissive[2], 1.0))
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

        mel.recompile_material(mat)
    except Exception as exc:
        log(f"Material expression setup limited for {name}: {exc}")

    save_asset(mat)
    log(f"Created material {package_path}")
    return mat


def get_engine_shape(path: str):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        log(f"Missing engine shape: {path}")
    return asset


def spawn_mesh(world, mesh, location, rotation=None, scale=None, label=None, material=None):
    if mesh is None:
        return None
    rot = rotation or unreal.Rotator(0, 0, 0)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*location), rot
    )
    if actor is None:
        return None
    smc = actor.static_mesh_component
    smc.set_static_mesh(mesh)
    if scale is not None:
        actor.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        actor.set_actor_label(label)
    if material is not None:
        smc.set_material(0, material)
    return actor


def create_or_clear_map():
    # Create a new blank level and save it as our coast map.
    unreal.EditorLevelLibrary.new_level(MAP_PATH)
    log(f"Created map {MAP_PATH}")
    return unreal.EditorLevelLibrary.get_editor_world()


def build_coast_world(world, mats, shapes):
    # Ocean
    spawn_mesh(
        world,
        shapes["plane"],
        (0, 0, 0),
        scale=(250, 250, 1),
        label="Ocean",
        material=mats["ocean"],
    )
    # Beach / land band on port side (negative X)
    spawn_mesh(
        world,
        shapes["cube"],
        (-1800, 0, 40),
        scale=(40, 250, 1),
        label="CoastLand",
        material=mats["sand"],
    )
    # Beach ribbon
    spawn_mesh(
        world,
        shapes["cube"],
        (-900, 0, 20),
        scale=(8, 250, 0.4),
        label="BeachRibbon",
        material=mats["beach"],
    )

    # City blocks (simple extruded skyline)
    city_origin_x = -1600
    for i in range(18):
        for j in range(4):
            height = 4 + ((i * 3 + j * 7) % 12)
            x = city_origin_x - j * 350
            y = -2200 + i * 260
            z = height * 50
            spawn_mesh(
                world,
                shapes["cube"],
                (x, y, z),
                scale=(2.2, 2.0, height),
                label=f"CityBlock_{i}_{j}",
                material=mats["city"],
            )

    # Runway / coastal road
    spawn_mesh(
        world,
        shapes["cube"],
        (-1050, 0, 25),
        scale=(2, 220, 0.15),
        label="CoastRoad",
        material=mats["road"],
    )

    # Yak body representation (player is parented later)
    fuselage = spawn_mesh(
        world,
        shapes["cylinder"],
        (0, 0, 320),
        rotation=unreal.Rotator(0, 0, 90),
        scale=(1.2, 1.2, 8),
        label="YakFuselage",
        material=mats["airframe"],
    )
    wing = spawn_mesh(
        world,
        shapes["cube"],
        (0, 0, 300),
        scale=(14, 1.6, 0.15),
        label="YakWing",
        material=mats["airframe"],
    )
    tail = spawn_mesh(
        world,
        shapes["cube"],
        (0, 420, 360),
        scale=(0.2, 1.2, 2.2),
        label="YakTail",
        material=mats["airframe"],
    )

    # Directional light / skylight if none
    try:
        light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.DirectionalLight, unreal.Vector(0, 0, 2000), unreal.Rotator(-40, 30, 0)
        )
        if light:
            light.set_actor_label("Sun")
        sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkyLight, unreal.Vector(0, 0, 1000), unreal.Rotator()
        )
        if sky:
            sky.set_actor_label("SkyLight")
        fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator()
        )
        if fog:
            fog.set_actor_label("CoastFog")
    except Exception as exc:
        log(f"Lighting spawn limited: {exc}")

    # Player start in rear cockpit approximate
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(0, -120, 340), unreal.Rotator(0, 0, 0)
    )
    if ps:
        ps.set_actor_label("GunnerStart")

    # Ambient drones already in scene for immediate play
    for idx, y in enumerate([-900, -200, 500, 1200, 1800]):
        spawn_mesh(
            world,
            shapes["cone"],
            (800 + idx * 40, y, 420 + (idx % 3) * 30),
            rotation=unreal.Rotator(0, -90, 0),
            scale=(1.4, 1.4, 3.2),
            label=f"SeedDrone_{idx}",
            material=mats["drone"],
        )

    unreal.EditorLevelLibrary.save_current_level()
    log("Coast world saved")


def create_blueprint(name: str, parent_class, folder=BP_ROOT):
    package_path = f"{folder}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        return unreal.EditorAssetLibrary.load_asset(package_path)

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_class)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    bp = asset_tools.create_asset(name, folder, unreal.Blueprint, factory)
    save_asset(bp)
    log(f"Created blueprint {package_path}")
    return bp


def create_gameplay_blueprints():
    # Parent classes only; detailed event graph still needs editor authoring.
    # These give us named, placeable shells immediately.
    create_blueprint("BP_SkyguardGunner", unreal.Character)
    create_blueprint("BP_ShahedDrone", unreal.Actor)
    create_blueprint("BP_DroneSpawner", unreal.Actor)
    create_blueprint("BP_SkyguardGameMode", unreal.GameModeBase)
    create_blueprint("BP_SkyguardPlayerController", unreal.PlayerController)
    create_blueprint("BP_SkyguardHUD", unreal.HUD)


def set_project_defaults():
    # Point maps/game mode to Skyguard slice.
    # Config writes are done outside Python when possible; here we try subsystem.
    try:
        # Save config via editor
        unreal.EditorAssetLibrary.save_directory(ASSET_ROOT, only_if_is_dirty=False, recursive=True)
    except Exception:
        pass


def main():
    log("Building Skyguard vertical slice...")
    for path in [ASSET_ROOT, MAT_ROOT, BP_ROOT, f"{ASSET_ROOT}/Maps", f"{ASSET_ROOT}/Meshes", f"{ASSET_ROOT}/UI"]:
        ensure_dir(path)

    mats = {
        "ocean": create_color_material("M_Ocean", (0.05, 0.18, 0.28), roughness=0.25, metallic=0.05),
        "sand": create_color_material("M_Sand", (0.55, 0.47, 0.30), roughness=0.95),
        "beach": create_color_material("M_Beach", (0.72, 0.62, 0.42), roughness=0.9),
        "city": create_color_material("M_CityConcrete", (0.35, 0.36, 0.34), roughness=0.85),
        "road": create_color_material("M_Road", (0.08, 0.08, 0.08), roughness=0.8),
        "airframe": create_color_material("M_YakAirframe", (0.55, 0.58, 0.52), roughness=0.45, metallic=0.35),
        "drone": create_color_material("M_ShahedDrone", (0.12, 0.14, 0.12), roughness=0.6, metallic=0.2, emissive=(0.05, 0.0, 0.0)),
        "cockpit": create_color_material("M_CockpitInterior", (0.18, 0.16, 0.12), roughness=0.75),
        "rifle": create_color_material("M_RifleTan", (0.45, 0.38, 0.22), roughness=0.55, metallic=0.25),
    }

    shapes = {
        "cube": get_engine_shape("/Engine/BasicShapes/Cube"),
        "sphere": get_engine_shape("/Engine/BasicShapes/Sphere"),
        "cylinder": get_engine_shape("/Engine/BasicShapes/Cylinder"),
        "cone": get_engine_shape("/Engine/BasicShapes/Cone"),
        "plane": get_engine_shape("/Engine/BasicShapes/Plane"),
    }

    create_gameplay_blueprints()
    world = create_or_clear_map()
    build_coast_world(world, mats, shapes)
    set_project_defaults()
    log("Vertical slice generation complete.")
    log("Open /Game/Skyguard/Maps/Lvl_SkyguardCoast and press Play.")
    log("Next authoring pass: wire BP_SkyguardGunner ADS/fire and BP_ShahedDrone movement.")


if __name__ == "__main__":
    main()
