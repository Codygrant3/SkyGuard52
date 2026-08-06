"""Author the immutable M01 Landscape material visible-review candidate.

This recreates the accepted scene from governed sources, imports the accepted
505x127 Landscape against the existing PCG graph, exposes the Landscape by
removing only the candidate's legacy inland HISM slabs, and binds one new
six-sampler material. It imports nothing and never invokes PCG generation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


TARGET_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v4_attempt04"
BASELINE_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03"
GRAPH_PATH = (
    "/Game/Skyguard/Environment/Mission01/PCG/"
    "PCG_M01_InlandVegetation"
)
MATERIAL_ROOT = "/Game/Skyguard/Materials/Mission01/LandscapeValidation_v4"
MATERIAL_PATH = "/Game/Skyguard/Materials/Mission01/LandscapeValidation_v4/M_M01_Landscape_Validation_v4"
HEIGHTMAP_PATH = (
    ROOT
    / "Content/Skyguard/Environment/Source/Mission01"
    / "HM_M01_CoastalProduction_505x127.r16"
)
HEIGHTMAP_MANIFEST = (
    ROOT / "Saved/Reports/PHASE4_M01_LANDSCAPE_SOURCE_MANIFEST.json"
)
ASSET_MANIFEST = (
    ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
)
BASELINE_FILE = (
    ROOT
    / "Content/Skyguard/Maps/"
    / "Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03.umap"
)
REPORT_PATH = (
    ROOT / "Saved/Reports/PHASE4_M01_LANDSCAPE_MATERIAL_BUILD_ATTEMPT04.json"
)
PREFIX = "M01_P45_"

TEXTURES = {
    "sand_base": "/Game/Skyguard/Textures/Imported/T_L3_sand_A",
    "sand_normal": "/Game/Skyguard/Textures/Imported/T_L3_sand_N",
    "sand_roughness": "/Game/Skyguard/Textures/Imported/T_L3_sand_R",
    "inland_base": "/Game/Skyguard/Textures/Imported/T_L4_grassrock_A",
    "inland_normal": "/Game/Skyguard/Textures/Imported/T_L4_grassrock_N",
    "inland_roughness": "/Game/Skyguard/Textures/Imported/T_L4_grassrock_R",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_locked_texture(
    asset_path: str, *, required_flip: bool | None = None
):
    texture = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("Locked texture unavailable: " + asset_path)
    if required_flip is not None:
        actual_flip = bool(
            texture.get_editor_property("flip_green_channel")
        )
        if actual_flip is not required_flip:
            raise RuntimeError(
                "Locked normal green policy mismatch: "
                + asset_path
            )
        compression = str(texture.get_editor_property("compression_settings"))
        if "NORMALMAP" not in compression.upper():
            raise RuntimeError(
                "Locked normal lacks normal-map compression: " + asset_path
            )
    return texture


def preflight_locked_textures(contract: dict) -> dict:
    policy = contract["material_design"]["normal_green_handling"]
    locked = {
        "sand_base": load_locked_texture(TEXTURES["sand_base"]),
        "sand_normal": load_locked_texture(
            TEXTURES["sand_normal"],
            required_flip=policy[TEXTURES["sand_normal"]][
                "required_source_flip_green_channel"
            ],
        ),
        "sand_roughness": load_locked_texture(TEXTURES["sand_roughness"]),
        "inland_base": load_locked_texture(TEXTURES["inland_base"]),
        "inland_normal": load_locked_texture(
            TEXTURES["inland_normal"],
            required_flip=policy[TEXTURES["inland_normal"]][
                "required_source_flip_green_channel"
            ],
        ),
        "inland_roughness": load_locked_texture(
            TEXTURES["inland_roughness"]
        ),
    }
    if policy[TEXTURES["sand_normal"]]["material_space_green_inversion"]:
        raise RuntimeError("Sand normal must use its locked imported green flip")
    inland_policy = policy[TEXTURES["inland_normal"]]
    if (
        not inland_policy["material_space_green_inversion"]
        or inland_policy["correction_vector"] != [1.0, -1.0, 1.0]
    ):
        raise RuntimeError("Inland material-space green correction is not exact")
    return locked


def make_expression(material, cls, x: int, y: int):
    return unreal.MaterialEditingLibrary.create_material_expression(
        material, cls, x, y
    )


def component_mask(material, source, x, y, *, r=False, g=False, b=False):
    mask = make_expression(
        material, unreal.MaterialExpressionComponentMask, x, y
    )
    mask.set_editor_property("r", r)
    mask.set_editor_property("g", g)
    mask.set_editor_property("b", b)
    mask.set_editor_property("a", False)
    unreal.MaterialEditingLibrary.connect_material_expressions(
        source, "", mask, ""
    )
    return mask


def divided_uv(material, world_position, scale_cm, x, y):
    xy = component_mask(
        material, world_position, x, y, r=True, g=True
    )
    divide = make_expression(
        material, unreal.MaterialExpressionDivide, x + 190, y
    )
    divide.set_editor_property("const_b", float(scale_cm))
    unreal.MaterialEditingLibrary.connect_material_expressions(
        xy, "", divide, "A"
    )
    return divide


def sample(material, texture, uv, x, y, *, normal=False):
    node = make_expression(
        material, unreal.MaterialExpressionTextureSample, x, y
    )
    node.set_editor_property("texture", texture)
    if normal:
        node.set_editor_property(
            "sampler_type",
            unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
        )
    unreal.MaterialEditingLibrary.connect_material_expressions(
        uv, "", node, "Coordinates"
    )
    return node


def lerp(material, a, a_output, b, b_output, alpha, x, y):
    node = make_expression(
        material, unreal.MaterialExpressionLinearInterpolate, x, y
    )
    mel = unreal.MaterialEditingLibrary
    mel.connect_material_expressions(a, a_output, node, "A")
    mel.connect_material_expressions(b, b_output, node, "B")
    mel.connect_material_expressions(alpha, "", node, "Alpha")
    return node


def apply_normal_green_correction(material, normal_sample, x, y):
    vector = make_expression(
        material, unreal.MaterialExpressionConstant3Vector, x, y + 90
    )
    vector.set_editor_property(
        "constant", unreal.LinearColor(1.0, -1.0, 1.0, 1.0)
    )
    multiply = make_expression(
        material, unreal.MaterialExpressionMultiply, x + 210, y
    )
    mel = unreal.MaterialEditingLibrary
    mel.connect_material_expressions(normal_sample, "RGB", multiply, "A")
    mel.connect_material_expressions(vector, "", multiply, "B")
    return multiply


def build_landscape_material(contract: dict):
    if unreal.EditorAssetLibrary.does_asset_exist(MATERIAL_PATH):
        raise RuntimeError(
            "Immutable candidate material already exists: " + MATERIAL_PATH
        )
    if not unreal.EditorAssetLibrary.does_directory_exist(MATERIAL_ROOT):
        unreal.EditorAssetLibrary.make_directory(MATERIAL_ROOT)
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        MATERIAL_PATH.rsplit("/", 1)[-1],
        MATERIAL_ROOT,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    if not isinstance(material, unreal.Material):
        raise RuntimeError("Could not create candidate Landscape material")

    locked = preflight_locked_textures(contract)
    design = contract["material_design"]
    mel = unreal.MaterialEditingLibrary
    mel.delete_all_material_expressions(material)
    world = make_expression(
        material, unreal.MaterialExpressionWorldPosition, -1300, -100
    )
    sand_uv = divided_uv(
        material, world, design["sand_world_scale_cm"], -1100, -280
    )
    inland_uv = divided_uv(
        material, world, design["inland_world_scale_cm"], -1100, 300
    )

    world_y = component_mask(
        material, world, -1100, 40, g=True
    )
    subtract = make_expression(
        material, unreal.MaterialExpressionSubtract, -880, 40
    )
    subtract.set_editor_property(
        "const_b", float(design["shoreline_landscape_start_y_cm"])
    )
    mel.connect_material_expressions(world_y, "", subtract, "A")
    divide = make_expression(
        material, unreal.MaterialExpressionDivide, -680, 40
    )
    divide.set_editor_property(
        "const_b", float(design["sand_to_inland_transition_width_cm"])
    )
    mel.connect_material_expressions(subtract, "", divide, "A")
    alpha = make_expression(
        material, unreal.MaterialExpressionSaturate, -480, 40
    )
    mel.connect_material_expressions(divide, "", alpha, "")

    sand_base = sample(
        material, locked["sand_base"], sand_uv, -650, -430
    )
    sand_normal = sample(
        material,
        locked["sand_normal"],
        sand_uv,
        -650,
        -290,
        normal=True,
    )
    sand_rough = sample(
        material, locked["sand_roughness"], sand_uv, -650, -150
    )
    inland_base = sample(
        material, locked["inland_base"], inland_uv, -650, 230
    )
    inland_normal = sample(
        material,
        locked["inland_normal"],
        inland_uv,
        -650,
        370,
        normal=True,
    )
    inland_normal_corrected = apply_normal_green_correction(
        material, inland_normal, -420, 370
    )
    inland_rough = sample(
        material, locked["inland_roughness"], inland_uv, -650, 510
    )

    base_lerp = lerp(
        material,
        sand_base,
        "RGB",
        inland_base,
        "RGB",
        alpha,
        -180,
        -250,
    )
    normal_lerp = lerp(
        material,
        sand_normal,
        "RGB",
        inland_normal_corrected,
        "",
        alpha,
        -180,
        20,
    )
    rough_lerp = lerp(
        material,
        sand_rough,
        "R",
        inland_rough,
        "R",
        alpha,
        -180,
        290,
    )
    mel.connect_material_property(
        base_lerp, "", unreal.MaterialProperty.MP_BASE_COLOR
    )
    mel.connect_material_property(
        normal_lerp, "", unreal.MaterialProperty.MP_NORMAL
    )
    mel.connect_material_property(
        rough_lerp, "", unreal.MaterialProperty.MP_ROUGHNESS
    )
    material.set_editor_property("two_sided", False)
    mel.recompile_material(material)
    if not unreal.EditorAssetLibrary.save_loaded_asset(material, False):
        raise RuntimeError("Could not save candidate Landscape material")
    return material


def build_unlit_diagnostic_material(asset_path: str, component_ids: bool):
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        raise RuntimeError(
            "Immutable diagnostic material already exists: " + asset_path
        )
    package, name = asset_path.rsplit("/", 1)
    if not unreal.EditorAssetLibrary.does_directory_exist(package):
        unreal.EditorAssetLibrary.make_directory(package)
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name,
        package,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    if not isinstance(material, unreal.Material):
        raise RuntimeError("Could not create diagnostic material " + asset_path)
    mel = unreal.MaterialEditingLibrary
    mel.delete_all_material_expressions(material)
    material.set_editor_property(
        "shading_model", unreal.MaterialShadingModel.MSM_UNLIT
    )
    # UE 5.8 has no Landscape EMaterialUsage flag. The live proof must instead
    # block on each generated Landscape material resource and verify its shader
    # map after this completed graph is recompiled and saved.
    material.set_editor_property("two_sided", False)
    if not component_ids:
        color = make_expression(
            material, unreal.MaterialExpressionConstant3Vector, -200, 0
        )
        color.set_editor_property(
            "constant", unreal.LinearColor(1.0, 1.0, 1.0, 1.0)
        )
        mel.connect_material_property(
            color, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR
        )
    else:
        world = make_expression(
            material, unreal.MaterialExpressionWorldPosition, -1200, 0
        )
        world_x = component_mask(material, world, -1000, -160, r=True)
        world_y = component_mask(material, world, -1000, 180, g=True)
        y_offset = make_expression(
            material, unreal.MaterialExpressionSubtract, -810, 180
        )
        y_offset.set_editor_property("const_b", 7000.0)
        mel.connect_material_expressions(world_y, "", y_offset, "A")
        x_divide = make_expression(
            material, unreal.MaterialExpressionDivide, -620, -160
        )
        x_divide.set_editor_property("const_b", 6300.0)
        mel.connect_material_expressions(world_x, "", x_divide, "A")
        y_divide = make_expression(
            material, unreal.MaterialExpressionDivide, -620, 180
        )
        y_divide.set_editor_property("const_b", 6300.0)
        mel.connect_material_expressions(y_offset, "", y_divide, "A")
        floor_x = make_expression(
            material, unreal.MaterialExpressionFloor, -430, -160
        )
        floor_y = make_expression(
            material, unreal.MaterialExpressionFloor, -430, 180
        )
        mel.connect_material_expressions(x_divide, "", floor_x, "")
        mel.connect_material_expressions(y_divide, "", floor_y, "")
        red_add = make_expression(
            material, unreal.MaterialExpressionAdd, -230, -210
        )
        red_add.set_editor_property("const_b", 1.0)
        mel.connect_material_expressions(floor_x, "", red_add, "A")
        red = make_expression(
            material, unreal.MaterialExpressionDivide, -40, -210
        )
        red.set_editor_property("const_b", 9.0)
        mel.connect_material_expressions(red_add, "", red, "A")
        green_add = make_expression(
            material, unreal.MaterialExpressionAdd, -230, 80
        )
        green_add.set_editor_property("const_b", 1.0)
        mel.connect_material_expressions(floor_y, "", green_add, "A")
        green = make_expression(
            material, unreal.MaterialExpressionDivide, -40, 80
        )
        green.set_editor_property("const_b", 3.0)
        mel.connect_material_expressions(green_add, "", green, "A")
        y_index = make_expression(
            material, unreal.MaterialExpressionMultiply, -230, 300
        )
        y_index.set_editor_property("const_b", 8.0)
        mel.connect_material_expressions(floor_y, "", y_index, "A")
        index = make_expression(
            material, unreal.MaterialExpressionAdd, -40, 300
        )
        mel.connect_material_expressions(floor_x, "", index, "A")
        mel.connect_material_expressions(y_index, "", index, "B")
        hash_multiply = make_expression(
            material, unreal.MaterialExpressionMultiply, 150, 300
        )
        hash_multiply.set_editor_property("const_b", 0.61803398875)
        mel.connect_material_expressions(index, "", hash_multiply, "A")
        blue_frac = make_expression(
            material, unreal.MaterialExpressionFrac, 340, 300
        )
        mel.connect_material_expressions(hash_multiply, "", blue_frac, "")
        blue_scale = make_expression(
            material, unreal.MaterialExpressionMultiply, 520, 300
        )
        blue_scale.set_editor_property("const_b", 0.75)
        mel.connect_material_expressions(blue_frac, "", blue_scale, "A")
        blue = make_expression(
            material, unreal.MaterialExpressionAdd, 700, 300
        )
        blue.set_editor_property("const_b", 0.25)
        mel.connect_material_expressions(blue_scale, "", blue, "A")
        red_green = make_expression(
            material, unreal.MaterialExpressionAppendVector, 190, -60
        )
        mel.connect_material_expressions(red, "", red_green, "A")
        mel.connect_material_expressions(green, "", red_green, "B")
        rgb = make_expression(
            material, unreal.MaterialExpressionAppendVector, 900, 0
        )
        mel.connect_material_expressions(red_green, "", rgb, "A")
        mel.connect_material_expressions(blue, "", rgb, "B")
        mel.connect_material_property(
            rgb, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR
        )
    mel.recompile_material(material)
    if not unreal.EditorAssetLibrary.save_loaded_asset(material, False):
        raise RuntimeError("Could not save diagnostic material " + asset_path)
    return material


def spawn_review_cameras(contract: dict):
    cameras = []
    for spec in contract["capture"]["cameras"]:
        rotation = spec["rotation_degrees"]
        camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor,
            unreal.Vector(*spec["location_cm"]),
            unreal.Rotator(
                roll=rotation["roll"],
                pitch=rotation["pitch"],
                yaw=rotation["yaw"],
            ),
        )
        if camera is None:
            raise RuntimeError("Could not spawn camera " + spec["id"])
        camera.set_actor_label(PREFIX + "Camera_" + spec["id"])
        cameras.append(camera)
    return cameras


def main():
    contract = load_effective_contract()
    if contract["baseline"]["immutable_map"] != BASELINE_MAP:
        raise RuntimeError("Baseline path differs from governed contract")
    if contract["candidate"]["immutable_map"] != TARGET_MAP:
        raise RuntimeError("Candidate path differs from governed contract")
    if contract["candidate"]["landscape_material"] != MATERIAL_PATH:
        raise RuntimeError("Material path differs from governed contract")
    for target in (TARGET_MAP, MATERIAL_PATH):
        if unreal.EditorAssetLibrary.does_asset_exist(target):
            raise RuntimeError(
                "Immutable candidate target already exists: " + target
            )

    # Validate locked texture metadata and the attempt02 material-space
    # correction policy before creating any package.
    preflight_locked_textures(contract)

    baseline_expected = contract["baseline"]["sha256"]
    if not BASELINE_FILE.is_file():
        raise RuntimeError("Accepted v5 baseline is missing")
    baseline_hash_before = sha256_file(BASELINE_FILE)
    if baseline_hash_before != baseline_expected:
        raise RuntimeError("Accepted v5 baseline hash drifted before authoring")

    source_manifest = json.loads(
        HEIGHTMAP_MANIFEST.read_text(encoding="utf-8-sig")
    )
    if (
        HEIGHTMAP_PATH.stat().st_size != 505 * 127 * 2
        or sha256_file(HEIGHTMAP_PATH) != source_manifest.get("sha256")
    ):
        raise RuntimeError("Governed Landscape source integrity failed")

    scripts_path = str(ROOT / "Scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    import build_skyguard_m01_wave1_refinement_validation as geometry
    import build_skyguard_phase4_m01_production_environment as base

    asset_manifest = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    meshes, _ = geometry.collect_meshes()
    expected = {entry["name"] for entry in asset_manifest["assets"]}
    if set(meshes) != expected:
        raise RuntimeError("Refined mesh set differs from governed manifest")
    if not unreal.EditorLevelLibrary.new_level(TARGET_MAP):
        raise RuntimeError("Could not create immutable candidate map")

    placed = []
    for index, spec in enumerate(asset_manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        geometry.spawn_static(
            meshes[spec["asset"]],
            "%sRefined_%03d_%s" % (
                PREFIX,
                index,
                spec["asset"][:42],
            ),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
        placed.append(spec["asset"])

    boss, bindings, required = geometry.spawn_and_bind_pathfinder(meshes)
    if boss is None or bindings != required:
        raise RuntimeError("Governed Pathfinder could not be bound")
    boss.set_actor_label(PREFIX + "Boss_Pathfinder")

    director_class = getattr(
        unreal, "SkyguardMission01EnvironmentDirector", None
    )
    authoring = getattr(
        unreal, "SkyguardMission01EnvironmentAuthoringLibrary", None
    )
    if director_class is None or authoring is None:
        raise RuntimeError("Native Phase 4 authoring classes are unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector(), unreal.Rotator()
    )
    if director is None:
        raise RuntimeError("Mission 1 environment director did not spawn")
    director.set_actor_label(PREFIX + "ProductionEnvironmentDirector")
    director.set_use_authored_landscape_surface_for_validation(True)

    authored = authoring.author_governed_landscape_with_existing_graph(
        director, str(HEIGHTMAP_PATH), GRAPH_PATH
    )
    if not bool(authored.success):
        raise RuntimeError(
            "Native Landscape import/binding failed: " + str(authored.error)
        )
    landscape = authored.landscape
    material = build_landscape_material(contract)
    landscape.set_editor_property("landscape_material", material)
    visible_audit = (
        authoring.prepare_governed_landscape_for_visible_validation(
            landscape, material
        )
    )
    if not bool(visible_audit.success):
        raise RuntimeError(
            "Landscape did not reach live render readiness: "
            + str(visible_audit.error)
        )
    diagnostic_materials = {}
    if contract["contract_id"] in {
        "P4.5-M01-LANDSCAPE-VISIBLE-005",
        "P4.5-M01-LANDSCAPE-VISIBLE-006",
    }:
        repair_outputs = contract["repair"]["future_immutable_outputs"]
        diagnostic_materials = {
            "coverage": build_unlit_diagnostic_material(
                repair_outputs["coverage_material"], False
            ),
            "component_id": build_unlit_diagnostic_material(
                repair_outputs["component_id_material"], True
            ),
        }

    atmosphere = base.spawn_actor(
        "/Script/Engine.SkyAtmosphere", PREFIX + "SkyAtmosphere"
    )
    cloud = base.spawn_actor(
        "/Script/Engine.VolumetricCloud", PREFIX + "VolumetricCloud"
    )
    fog = base.spawn_actor(
        "/Script/Engine.ExponentialHeightFog", PREFIX + "HeightFog"
    )
    wind = base.spawn_actor(
        "/Script/Engine.WindDirectionalSource",
        PREFIX + "WorldWind",
        rotation=(0.0, 35.0, 0.0),
    )
    sun = base.spawn_actor(
        "/Script/Engine.DirectionalLight",
        PREFIX + "Sun",
        location=(-4200.0, -5000.0, 7500.0),
        rotation=(-38.0, -32.0, 0.0),
    )
    skylight = base.spawn_actor(
        "/Script/Engine.SkyLight",
        PREFIX + "SkyFill",
        location=(0.0, 0.0, 3500.0),
    )
    for actor, tag in (
        (atmosphere, "Skyguard.Environment.Atmosphere"),
        (cloud, "Skyguard.Environment.Cloud"),
        (fog, "Skyguard.Environment.Fog"),
        (wind, "Skyguard.Environment.Wind"),
    ):
        if actor:
            base.add_tag(actor, tag)
    if fog:
        component = fog.get_component_by_class(
            unreal.ExponentialHeightFogComponent
        )
        component.set_editor_property("fog_density", 0.012)
        component.set_editor_property("fog_height_falloff", 0.17)
    if sun:
        component = sun.get_component_by_class(
            unreal.DirectionalLightComponent
        )
        component.set_editor_property("intensity", 4.5)
        component.set_editor_property("atmosphere_sun_light", True)
    if skylight:
        component = skylight.get_component_by_class(
            unreal.SkyLightComponent
        )
        component.set_editor_property("intensity", 1.2)

    cameras = spawn_review_cameras(contract)
    unreal.EditorLevelLibrary.save_current_level()
    if not unreal.EditorAssetLibrary.save_asset(TARGET_MAP, False):
        raise RuntimeError("Could not save immutable candidate map")

    baseline_hash_after = sha256_file(BASELINE_FILE)
    readiness = director.get_readiness()
    material_expressions = list(
        unreal.MaterialEditingLibrary.get_material_expressions(material) or []
    )
    material_expression_count = int(
        unreal.MaterialEditingLibrary.get_num_material_expressions(material)
    )
    texture_samples = [
        expression
        for expression in material_expressions
        if isinstance(expression, unreal.MaterialExpressionTextureSample)
    ]
    green_correction_multiply = [
        expression
        for expression in material_expressions
        if isinstance(expression, unreal.MaterialExpressionMultiply)
    ]
    correction_vectors = [
        expression.get_editor_property("constant")
        for expression in material_expressions
        if isinstance(expression, unreal.MaterialExpressionConstant3Vector)
    ]
    location = landscape.get_actor_location()
    scale = landscape.get_actor_scale3d()
    checks = {
        "baseline_hash_unchanged": (
            baseline_hash_before == baseline_hash_after == baseline_expected
        ),
        "immutable_candidate_map_saved": (
            unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP)
        ),
        "immutable_candidate_material_saved": (
            unreal.EditorAssetLibrary.does_asset_exist(MATERIAL_PATH)
        ),
        "refined_assets_recreated": len(placed) > 0,
        "pathfinder_bindings_complete": bindings == required,
        "landscape_components_exact": (
            int(authored.landscape_component_count) == 16
        ),
        "landscape_transform_exact": (
            abs(location.x) <= 0.01
            and abs(location.y - 7000.0) <= 0.01
            and abs(location.z + 120.0) <= 0.01
            and abs(scale.x - 100.0) <= 0.01
            and abs(scale.y - 100.0) <= 0.01
            and abs(scale.z - 100.0) <= 0.01
        ),
        "landscape_material_bound": (
            landscape.get_editor_property("landscape_material") == material
        ),
        "landscape_live_render_readiness": (
            bool(visible_audit.success)
            and int(visible_audit.landscape_component_count) == 16
            and int(visible_audit.visible_component_count) == 16
            and int(visible_audit.registered_component_count) == 16
            and int(
                visible_audit.render_state_created_component_count
            )
            == 16
            and int(visible_audit.hidden_in_game_component_count) == 0
            and int(
                visible_audit.generated_material_instance_ready_component_count
            )
            == 16
            and int(
                visible_audit.governed_material_parent_match_component_count
            )
            == 16
            and int(
                visible_audit.contract_camera_frustum_intersection_count
            )
            == 5
        ),
        "six_texture_samples": len(texture_samples) == 6,
        "material_expression_api_count_matches": (
            material_expression_count == len(material_expressions)
        ),
        "one_material_space_green_correction": (
            len(green_correction_multiply) >= 1
            and any(
                abs(value.r - 1.0) <= 0.001
                and abs(value.g + 1.0) <= 0.001
                and abs(value.b - 1.0) <= 0.001
                for value in correction_vectors
            )
        ),
        "legacy_land_tiles_disabled": (
            bool(readiness.authored_landscape_surface_exposed)
            and int(readiness.land_tile_count) == 0
            and not bool(director.land_tiles.is_visible())
        ),
        "ocean_and_beach_retained": (
            int(readiness.ocean_tile_count) == 6
            and int(readiness.beach_tile_count) == 6
        ),
        "five_fixed_cameras": len(cameras) == 5,
        "attempt05_diagnostic_materials_ready": (
            contract["contract_id"] != "P4.5-M01-LANDSCAPE-VISIBLE-005"
            or (
                len(diagnostic_materials) == 2
                and all(
                    unreal.EditorAssetLibrary.does_asset_exist(
                        unreal.SystemLibrary.get_path_name(asset).split(".", 1)[0]
                    )
                    for asset in diagnostic_materials.values()
                )
            )
        ),
        "pcg_generation_locked": (
            bool(authored.generation_locked)
            and not bool(readiness.ready_for_authored_pcg_generation)
        ),
        "zero_generated_pcg_output": (
            int(authored.generated_pcg_component_count) == 0
            and int(authored.generated_pcg_instance_count) == 0
        ),
    }
    report = {
        "schema": "skyguard.phase4.m01-landscape-material-build.v2",
        "contract_id": contract["contract_id"],
        "target_map": TARGET_MAP,
        "landscape_material": MATERIAL_PATH,
        "baseline_map_sha256_before": baseline_hash_before,
        "baseline_map_sha256_after": baseline_hash_after,
        "locked_texture_assets": TEXTURES,
        "material_texture_sample_count": len(texture_samples),
        "landscape_visible_audit": {
            "success": bool(visible_audit.success),
            "visible_component_count": int(
                visible_audit.visible_component_count
            ),
            "registered_component_count": int(
                visible_audit.registered_component_count
            ),
            "render_state_created_component_count": int(
                visible_audit.render_state_created_component_count
            ),
            "generated_material_instance_ready_component_count": int(
                visible_audit.generated_material_instance_ready_component_count
            ),
            "governed_material_parent_match_component_count": int(
                visible_audit.governed_material_parent_match_component_count
            ),
            "contract_camera_frustum_intersection_count": int(
                visible_audit.contract_camera_frustum_intersection_count
            ),
        },
        "pcg_generation_invoked": False,
        "generated_pcg_component_count": int(
            authored.generated_pcg_component_count
        ),
        "generated_pcg_instance_count": int(
            authored.generated_pcg_instance_count
        ),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": {
            "candidate_serialized_ready_for_visible_review": all(
                checks.values()
            ),
            "visible_gpu_accepted": False,
            "production_vegetation_complete": False,
            "mission01_aaa_complete": False,
        },
        "limitations": [
            "No visible GPU judgment is made by the authoring pass.",
            "No PCG content was generated.",
            "No Fab, Quixel, network, or new external content was used.",
        ],
    }
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[SkyguardP45LandscapeBuild] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Landscape material candidate build gate failed")


if __name__ == "__main__":
    main()
