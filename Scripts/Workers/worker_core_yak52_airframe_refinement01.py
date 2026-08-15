from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "core-yak52-airframe"
SOURCE_BLEND = (
    PROJECT_ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Uplift_003_R3"
    / "BLD_M01_YAK_UPLIFT_003_R3_MASTER.blend"
)
SOURCE_GLB = SOURCE_BLEND.with_name("bld_m01_yak_uplift_003_r3.glb")
CONTRACT = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_CONTRACT.json"
POLICY = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_CAMERAS.json"
RUBRIC = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_VISUAL_RUBRIC.json"

EXPECTED_SOURCE = {
    SOURCE_BLEND: (1526526, "512f13fde09edaeb77d75f0c27372a340dc0b2b123e7d0b813c89df3acdf22e6"),
    SOURCE_GLB: (6793008, "bcb046ae1fb92ed2a907b331fdabb2627dd364e721d30f394616f21f83ebdf58"),
}

AUTHORITATIVE = {
    "overall_length_m": 7.745,
    "overall_height_m": 2.7,
    "wingspan_m": 9.3,
    "horizontal_tail_span_m": 3.16,
    "propeller_diameter_m": 2.4,
    "gear_track_m": 2.715,
    "wheelbase_m": 1.285,
}

REQUIRED_SOCKETS = {
    "SOCKET_Origin": (0.0, 0.0, 0.0),
    "SOCKET_Propeller": (3.82, 0.0, 1.22),
    "SOCKET_MainGear_L": (0.42, -1.3575, 0.44),
    "SOCKET_MainGear_R": (0.42, 1.3575, 0.44),
    "SOCKET_NoseGear": (1.705, 0.0, 0.38),
    "SOCKET_CanopyRearClosed": (-0.62, 0.0, 1.56),
    "SOCKET_CanopyRearOpen": (-1.32, 0.0, 1.56),
    "SOCKET_RearGunnerCamera": (-0.78, -0.36, 1.55),
    "SOCKET_RifleClearance": (-0.35, -0.72, 1.58),
    "SOCKET_IglaBackblast": (-1.42, 0.70, 1.58),
}

EXCLUDE_TOKENS = (
    "gunner",
    "pilot",
    "rifle",
    "igla",
    "glove",
    "forearm",
    "sleeve",
    "helmet",
    "headset",
    "camera",
    "light",
    "review_",
    "vol_",
    "datum_",
)

AIRFRAME_TOKENS = (
    "airframe",
    "fuselage",
    "wing",
    "aileron",
    "flap",
    "tail",
    "stabil",
    "elevator",
    "rudder",
    "cowl",
    "engine",
    "shutter",
    "inlet",
    "spinner",
    "prop",
    "gear",
    "wheel",
    "canopy",
    "windscreen",
    "glass",
    "fairing",
    "fillet",
    "accesspanel",
    "panelring",
    "fuselagerivet",
    "stripe",
    "roundel",
    "antenna",
    "pitot",
    "exhaust",
    "fastener",
    "hinge",
    "door",
    "well",
    "vent",
)


class RefinementError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    source = list(sys.argv)
    if "--" in source:
        source = source[source.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    args = parser.parse_args(source)
    if args.asset_id != ASSET_ID:
        raise RefinementError(f"Unexpected asset id: {args.asset_id}")
    return args


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def verify_sources() -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path, (expected_bytes, expected_hash) in EXPECTED_SOURCE.items():
        if not path.is_file():
            raise RefinementError(f"Missing immutable source: {path}")
        actual = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        if actual["bytes"] != expected_bytes or actual["sha256"] != expected_hash:
            raise RefinementError(f"Immutable source mismatch: {path}")
        inventory.append(actual)
    for path in (CONTRACT, POLICY, CAMERAS, RUBRIC):
        if not path.is_file():
            raise RefinementError(f"Missing governed contract: {path}")
        inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return inventory


def keep_object(obj: Any) -> bool:
    lowered = obj.name.lower()
    if any(token in lowered for token in EXCLUDE_TOKENS):
        return False
    if obj.type != "MESH":
        return False
    return any(token in lowered for token in AIRFRAME_TOKENS)


def bounds(objects: list[Any]) -> tuple[Any, Any]:
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    if not corners:
        raise RefinementError("No governed mesh bounds were found.")
    minimum = Vector(tuple(min(point[index] for point in corners) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in corners) for index in range(3)))
    return minimum, maximum


def dimensions(objects: list[Any]) -> dict[str, float]:
    minimum, maximum = bounds(objects)
    extent = maximum - minimum
    return {
        "overall_length_m": float(extent.x),
        "wingspan_m": float(extent.y),
        "overall_height_m": float(extent.z),
        "minimum_x_m": float(minimum.x),
        "maximum_x_m": float(maximum.x),
        "minimum_y_m": float(minimum.y),
        "maximum_y_m": float(maximum.y),
        "minimum_z_m": float(minimum.z),
        "maximum_z_m": float(maximum.z),
    }


def apply_global_reconciliation(objects: list[Any]) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    from mathutils import Matrix, Vector

    before = dimensions(objects)
    scale = {
        "x": AUTHORITATIVE["overall_length_m"] / before["overall_length_m"],
        "y": AUTHORITATIVE["wingspan_m"] / before["wingspan_m"],
        "z": AUTHORITATIVE["overall_height_m"] / before["overall_height_m"],
    }
    if any(abs(value - 1.0) > 0.08 for value in scale.values()):
        raise RefinementError(f"R3 source requires an axis correction beyond the 8% contract: {scale}")
    affine = Matrix.Diagonal((scale["x"], scale["y"], scale["z"], 1.0))
    for obj in objects:
        obj.matrix_world = affine @ obj.matrix_world
    after_scale = dimensions(objects)
    shift = Vector(
        (
            -(after_scale["minimum_x_m"] + after_scale["maximum_x_m"]) / 2.0,
            -(after_scale["minimum_y_m"] + after_scale["maximum_y_m"]) / 2.0,
            -after_scale["minimum_z_m"],
        )
    )
    for obj in objects:
        obj.location += shift
    return before, dimensions(objects), scale


def ensure_uv(obj: Any) -> None:
    if obj.data.uv_layers:
        return
    uv_layer = obj.data.uv_layers.new(name="UVMap")
    mesh = obj.data
    mesh.calc_normals_split if hasattr(mesh, "calc_normals_split") else None
    for polygon in mesh.polygons:
        normal = polygon.normal
        axis = max(range(3), key=lambda index: abs(normal[index]))
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if axis == 0:
                uv = (coordinate.y, coordinate.z)
            elif axis == 1:
                uv = (coordinate.x, coordinate.z)
            else:
                uv = (coordinate.x, coordinate.y)
            uv_layer.data[loop_index].uv = (float(uv[0]), float(uv[1]))


def configure_material(material: Any) -> str:
    lowered = material.name.lower()
    role = "painted_aluminum"
    base = (0.19, 0.22, 0.24, 1.0)
    metallic = 0.0
    roughness = 0.38
    if "glass" in lowered or "canopy" in lowered:
        role, base, metallic, roughness = "canopy_glass", (0.10, 0.20, 0.24, 0.22), 0.0, 0.12
    elif "rubber" in lowered or "tire" in lowered:
        role, base, metallic, roughness = "rubber", (0.018, 0.022, 0.025, 1.0), 0.0, 0.78
    elif "bare" in lowered or "metal" in lowered or "aluminum" in lowered:
        role, base, metallic, roughness = "bare_aluminum", (0.42, 0.46, 0.49, 1.0), 0.82, 0.31
    elif "yellow" in lowered:
        role, base, metallic, roughness = "paint_yellow", (0.72, 0.46, 0.03, 1.0), 0.0, 0.42
    elif "blue" in lowered:
        role, base, metallic, roughness = "paint_blue", (0.025, 0.18, 0.42, 1.0), 0.0, 0.40
    elif "black" in lowered or "dark" in lowered:
        role, base, metallic, roughness = "paint_dark", (0.035, 0.045, 0.052, 1.0), 0.0, 0.52
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = base
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        if role == "canopy_glass":
            for candidate in ("Transmission Weight", "Transmission"):
                if candidate in principled.inputs:
                    principled.inputs[candidate].default_value = 0.88
            principled.inputs["IOR"].default_value = 1.45
            if hasattr(material, "surface_render_method"):
                material.surface_render_method = "DITHERED"
    material["SKG_MaterialRole"] = role
    material["SKG_Status"] = "PROVISIONAL_PBR_REQUIRES_UNREAL_CALIBRATION"
    return role


def refine_meshes(objects: list[Any]) -> dict[str, Any]:
    material_roles: dict[str, str] = {}
    for obj in objects:
        ensure_uv(obj)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        if obj.name in {"GEO_Airframe", "GEO_EngineCowling", "GEO_Wings", "GEO_HorizontalTail", "GEO_VerticalTail"}:
            modifier = obj.modifiers.get("SKG_BoundedBevel") or obj.modifiers.new("SKG_BoundedBevel", "BEVEL")
            modifier.width = 0.006 if obj.name == "GEO_Airframe" else 0.003
            modifier.segments = 3
            modifier.limit_method = "ANGLE"
            modifier.angle_limit = math.radians(32.0)
        obj["SKG_AssetID"] = ASSET_ID
        obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
        for slot in obj.material_slots:
            if slot.material is not None and slot.material.name not in material_roles:
                material_roles[slot.material.name] = configure_material(slot.material)
    return {"material_roles": material_roles, "mesh_count": len(objects)}


def new_empty(name: str, location: tuple[float, float, float], collection: Any, role: str) -> Any:
    import bpy

    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.09
    obj.location = location
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_Role"] = role
    obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
    collection.objects.link(obj)
    return obj


def add_datums(collection: Any) -> list[str]:
    names: list[str] = []
    for name, location in REQUIRED_SOCKETS.items():
        new_empty(name, location, collection, "unreal_socket")
        names.append(name)
    for index in range(11):
        fraction = index / 10.0
        x = -AUTHORITATIVE["overall_length_m"] / 2.0 + fraction * AUTHORITATIVE["overall_length_m"]
        name = f"DATUM_DERIVED_Station_{index:02d}"
        datum = new_empty(name, (x, 0.0, 1.12), collection, "derived_station")
        datum["SKG_LongitudinalFraction"] = fraction
        names.append(name)
    return names


def add_collision_box(name: str, location: tuple[float, float, float], size: tuple[float, float, float], collection: Any) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.display_type = "WIRE"
    obj.hide_render = True
    obj["SKG_Role"] = "unreal_collision"
    obj["SKG_AssetID"] = ASSET_ID
    ensure_uv(obj)
    return obj


def add_collisions(collection: Any) -> list[str]:
    specifications = [
        ("UCX_Yak52_Fuselage", (0.0, 0.0, 1.06), (6.65, 1.18, 1.32)),
        ("UCX_Yak52_Wing_L", (0.35, -2.55, 1.08), (2.05, 3.95, 0.18)),
        ("UCX_Yak52_Wing_R", (0.35, 2.55, 1.08), (2.05, 3.95, 0.18)),
        ("UCX_Yak52_Tail", (-2.82, 0.0, 1.28), (1.55, 3.16, 0.34)),
    ]
    return [add_collision_box(name, location, size, collection).name for name, location, size in specifications]


def set_lighting(profile: str, key: Any, fill: Any, rim: Any, world: Any) -> None:
    settings = {
        "daylight": (4.0, 1750.0, 720.0, 850.0, (0.055, 0.075, 0.11)),
        "overcast": (2.0, 1050.0, 900.0, 500.0, (0.09, 0.10, 0.12)),
        "night": (0.7, 640.0, 280.0, 1050.0, (0.006, 0.012, 0.028)),
        "wet": (2.4, 1350.0, 620.0, 1100.0, (0.025, 0.04, 0.065)),
        "cockpit": (1.3, 800.0, 360.0, 700.0, (0.012, 0.022, 0.034)),
    }
    exposure, key.energy, fill.energy, rim.energy, color = settings[profile]
    world.color = color
    key.data.color = (1.0, 0.82, 0.66) if profile in {"night", "cockpit"} else (1.0, 0.94, 0.84)
    rim.data.color = (0.20, 0.42, 1.0) if profile in {"night", "wet"} else (0.68, 0.80, 1.0)
    key["SKG_ExposureHint"] = exposure


def render_views(asset_collection: Any, output: Path) -> list[Path]:
    import bpy
    from mathutils import Vector

    camera_contract = json.loads(CAMERAS.read_text(encoding="utf-8"))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("WORLD_Yak52Review")

    review = bpy.data.collections.new("REVIEW_ONLY")
    scene.collection.children.link(review)
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0.0, 0.0, -0.015))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for owner in list(ground.users_collection):
        owner.objects.unlink(ground)
    review.objects.link(ground)
    ground_material = bpy.data.materials.new("MAT_REVIEW_Ground")
    ground_material.diffuse_color = (0.055, 0.065, 0.075, 1.0)
    ground.data.materials.append(ground_material)

    camera_data = bpy.data.cameras.new("CAM_REVIEW")
    camera = bpy.data.objects.new("CAM_REVIEW", camera_data)
    review.objects.link(camera)
    scene.camera = camera

    lights = []
    for name, location, size in (
        ("REVIEW_Key", (6.0, -7.0, 8.5), 6.0),
        ("REVIEW_Fill", (-4.0, 5.0, 5.0), 7.0),
        ("REVIEW_Rim", (-5.0, -4.0, 6.0), 5.0),
    ):
        data = bpy.data.lights.new(name + "_Data", "AREA")
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = location
        light.rotation_euler = (Vector((0.0, 0.0, 1.0)) - light.location).to_track_quat("-Z", "Y").to_euler()
        review.objects.link(light)
        lights.append(light)
    key, fill, rim = lights

    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=False)
    paths: list[Path] = []
    for specification in camera_contract["views"]:
        camera.location = specification["camera"]
        target = Vector(specification["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        if specification["mode"] == "ORTHO":
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = specification["ortho_scale"]
        else:
            camera.data.type = "PERSP"
            camera.data.lens = specification["lens_mm"]
        set_lighting(specification["lighting"], key, fill, rim, scene.world)
        path = render_dir / f"{specification['name']}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def export_outputs(asset_collection: Any, output: Path) -> tuple[Path, Path]:
    import bpy

    blend_path = output / "SKG_Yak52_Airframe_Refinement01.blend"
    glb_path = output / "SKG_Yak52_Airframe_Refinement01.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for obj in asset_collection.all_objects:
        if obj.type in {"MESH", "EMPTY", "ARMATURE"}:
            obj.hide_set(False)
            obj.select_set(True)
            selected.append(obj)
    bpy.context.view_layer.objects.active = next((obj for obj in selected if obj.type == "MESH"), None)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    return blend_path, glb_path


def main() -> int:
    import bpy

    args = parse_args()
    output = Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise RefinementError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    source_inventory = verify_sources()
    source_before = {str(path): sha256(path) for path in EXPECTED_SOURCE}

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND), load_ui=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"

    kept = [obj for obj in list(bpy.data.objects) if keep_object(obj)]
    if not {"GEO_Airframe", "GEO_Wings", "GEO_HorizontalTail", "GEO_VerticalTail"}.issubset({obj.name for obj in kept}):
        raise RefinementError("R3 donor is missing one or more governed primary airframe objects.")
    for obj in list(bpy.data.objects):
        if obj not in kept:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name != scene.collection.name:
            bpy.data.collections.remove(collection)
    asset_collection = bpy.data.collections.new("ASSET")
    scene.collection.children.link(asset_collection)
    for obj in kept:
        for owner in list(obj.users_collection):
            owner.objects.unlink(obj)
        asset_collection.objects.link(obj)

    before, reconciled, axis_scale = apply_global_reconciliation(kept)
    refinement = refine_meshes(kept)
    datum_names = add_datums(asset_collection)
    collision_names = add_collisions(asset_collection)
    renders = render_views(asset_collection, output)
    blend_path, glb_path = export_outputs(asset_collection, output)

    source_after = {str(path): sha256(path) for path in EXPECTED_SOURCE}
    if source_before != source_after:
        raise RefinementError("An immutable R3 source changed during the worker run.")

    final_dimensions = dimensions(kept)
    dimension_receipt = {
        "schema": "skyguard.phase2.yak52-airframe-refinement01.dimension-receipt.v1",
        "authoritative_targets": AUTHORITATIVE,
        "source_dimensions_m": before,
        "axis_scale": axis_scale,
        "reconciled_dimensions_m": final_dimensions,
        "global_envelope_pass": all(
            abs(final_dimensions[key] - AUTHORITATIVE[key]) <= 0.008
            for key in ("overall_length_m", "overall_height_m", "wingspan_m")
        ),
        "derived_geometry_label": "PROJECT_DERIVED_NONAUTHORITATIVE",
    }
    write_json(output / "dimension_receipt.json", dimension_receipt)
    write_json(
        output / "source_parity_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-refinement01.source-parity.v1",
            "sources": source_inventory,
            "before": source_before,
            "after": source_after,
            "unchanged": source_before == source_after,
        },
    )
    write_json(
        output / "topology_material_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-refinement01.topology-material.v1",
            "retained_meshes": [obj.name for obj in sorted(kept, key=lambda item: item.name)],
            "retained_mesh_count": len(kept),
            "excluded_proxy_tokens": list(EXCLUDE_TOKENS),
            "material_roles": refinement["material_roles"],
            "sockets": datum_names,
            "collision": collision_names,
            "derived_geometry_label": "PROJECT_DERIVED_NONAUTHORITATIVE",
            "visual_acceptance_claimed": False,
        },
    )
    artifacts = [blend_path, glb_path, *renders]
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-refinement01.artifact-receipt.v1",
            "asset_id": ASSET_ID,
            "blender_version": bpy.app.version_string,
            "classification": "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW",
            "artifacts": [
                {"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in artifacts
            ],
            "render_count": len(renders),
            "render_dimensions": [2560, 1440],
            "unreal_import_authorized": False,
            "aaa_claimed": False,
        },
    )
    print(json.dumps({"asset_id": ASSET_ID, "status": "awaiting_review", "render_count": len(renders)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
