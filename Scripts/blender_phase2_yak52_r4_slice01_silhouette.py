"""Deterministic Blender authoring for Yak-52 R4 Slice 01.

This source is prepared for a later explicitly authorized Blender 5.2 run.
Importing or compiling this file does not create output. ``main()`` refuses to
overwrite any canonical output and creates only the isolated Slice 01 draft:
primary silhouette volumes, fixed cameras, neutral review lighting, hashes,
measurements, comparison renders, a blend, a GLB, and a manifest.

The generated draft is never final art. The dimension ledger explicitly lacks
a cleared primary reference package, so even a successful future run remains
``DRAFT_REFERENCE_PACKAGE_MISSING`` until separate human silhouette review.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import bpy
from mathutils import Vector


BUILD_ID = "BLD-M01-YAK-FINAL-ART-R4-S01"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_OUTPUT_CONTRACT.json"
)
DIMENSION_LEDGER_PATH = (
    ROOT / "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_DIMENSION_LEDGER.json"
)
CAMERA_MANIFEST_PATH = (
    ROOT / "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_CAMERA_MANIFEST.json"
)
R4_CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE2_YAK52_R4_OFFLINE_PRODUCTION_CONTRACT.json"
)
SCRIPT_PATH = Path(__file__).resolve()

OUTPUT_DIR = (
    ROOT
    / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R4/Slice01"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_FINAL_ART_R4_S01_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_final_art_r4_s01.glb"
MANIFEST_PATH = (
    ROOT / "Saved/Reports/BLD_M01_YAK_FINAL_ART_R4_S01_MANIFEST.json"
)
SCREENSHOT_DIR = ROOT / "Saved/Screenshots/BLD_M01_YAK_FINAL_ART_R4_S01"

COLLECTIONS = {
    "root": "R4_S01_ROOT",
    "geometry": "R4_S01_GEOMETRY",
    "primary": "R4_S01_PRIMARY",
    "reference": "R4_S01_REFERENCE",
    "datums": "R4_S01_DATUMS",
    "cameras": "R4_S01_CAMERAS",
    "lighting": "R4_S01_LIGHTING",
}
PRIMARY_OBJECTS = (
    "GEO_R4S01_FuselagePrimary",
    "GEO_R4S01_CowlingEnvelope",
    "GEO_R4S01_WingPrimary_L",
    "GEO_R4S01_WingPrimary_R",
    "GEO_R4S01_HorizontalTail_L",
    "GEO_R4S01_HorizontalTail_R",
    "GEO_R4S01_VerticalTail",
    "GEO_R4S01_CanopyEnvelope_Front",
    "GEO_R4S01_CanopyEnvelope_Rear",
    "GEO_R4S01_GearEnvelope_Main_L",
    "GEO_R4S01_GearEnvelope_Main_R",
    "GEO_R4S01_GearEnvelope_Nose",
    "GEO_R4S01_PropellerDisc",
)
DATUM_OBJECTS = (
    "DATUM_R4S01_AircraftOrigin",
    "DATUM_R4S01_TailExtreme",
    "DATUM_R4S01_PropellerPlane",
    "DATUM_R4S01_WingReference",
)
MATERIALS = (
    "MAT_R4S01_PrimaryNeutral",
    "MAT_R4S01_CanopyNeutral",
    "MAT_R4S01_GearNeutral",
)
CAMERA_IDS = (
    "R4_CAM_BEAUTY_PORT",
    "R4_CAM_SIDE_ORTHO",
    "R4_CAM_TOP_ORTHO",
    "R4_CAM_REAR_QUARTER",
    "R4_CAM_UNDERSIDE_ORTHO",
)
RANDOM_SEED = 5201


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def require_blender_52() -> None:
    if bpy.app.version[:2] != (5, 2):
        raise RuntimeError(
            f"{BUILD_ID} requires Blender 5.2; found "
            f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        )


def validate_authorities(contract: dict[str, Any]) -> None:
    if contract.get("build_id") != BUILD_ID:
        raise RuntimeError("Slice 01 output contract build id mismatch")
    for authority in contract.get("authority_inputs", []):
        path = ROOT / authority["path"]
        if (
            not path.is_file()
            or path.stat().st_size != authority["bytes"]
            or sha256_file(path) != authority["sha256"]
        ):
            raise RuntimeError(f"Slice 01 authority missing or drifted: {path}")
    expected_script = contract.get("authoring_script", {}).get("sha256")
    if sha256_file(SCRIPT_PATH) != expected_script:
        raise RuntimeError("Slice 01 authoring script hash does not match contract")


def ensure_canonical_outputs_absent(contract: dict[str, Any]) -> None:
    expected = {
        str(BLEND_PATH.relative_to(ROOT)).replace("\\", "/"),
        str(GLB_PATH.relative_to(ROOT)).replace("\\", "/"),
        str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        str(SCREENSHOT_DIR.relative_to(ROOT)).replace("\\", "/"),
    }
    contracted = {
        contract["outputs"]["blend"],
        contract["outputs"]["glb"],
        contract["outputs"]["manifest"],
        contract["outputs"]["comparison_directory"],
    }
    if expected != contracted:
        raise RuntimeError("Slice 01 canonical output path mismatch")
    present = [str(ROOT / value) for value in sorted(contracted) if (ROOT / value).exists()]
    if present:
        raise RuntimeError(f"Slice 01 refuses to overwrite existing outputs: {present}")


def new_collection(name: str, parent: bpy.types.Collection) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    parent.children.link(collection)
    return collection


def reset_scene() -> dict[str, bpy.types.Collection]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    root_collection = new_collection(COLLECTIONS["root"], scene.collection)
    geometry = new_collection(COLLECTIONS["geometry"], root_collection)
    collections = {
        "root": root_collection,
        "geometry": geometry,
        "primary": new_collection(COLLECTIONS["primary"], geometry),
        "reference": new_collection(COLLECTIONS["reference"], geometry),
        "datums": new_collection(COLLECTIONS["datums"], root_collection),
        "cameras": new_collection(COLLECTIONS["cameras"], root_collection),
        "lighting": new_collection(COLLECTIONS["lighting"], root_collection),
    }
    scene["SKG_BuildId"] = BUILD_ID
    scene["SKG_Slice"] = "R4-S01"
    scene["SKG_Final"] = False
    scene["SKG_AAA"] = False
    scene["SKG_PromotionAllowed"] = False
    scene["SKG_ReferencePackageStatus"] = "MISSING"
    return collections


def neutral_material(
    name: str, color: tuple[float, float, float, float], roughness: float
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
    material["SKG_DiagnosticOnly"] = True
    material["SKG_PromotionAllowed"] = False
    return material


def link_object(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> bpy.types.Object:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    obj["SKG_BuildId"] = BUILD_ID
    obj["SKG_Slice"] = "R4-S01"
    obj["SKG_PromotionAllowed"] = False
    return obj


def mesh_from_sections(
    name: str,
    sections: Iterable[tuple[float, float, float, float]],
    radial_segments: int,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    section_list = list(sections)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for x, half_width, half_height, center_z in section_list:
        for index in range(radial_segments):
            angle = 2.0 * math.pi * index / radial_segments
            vertices.append(
                (
                    x,
                    math.cos(angle) * half_width,
                    center_z + math.sin(angle) * half_height,
                )
            )
    for station in range(len(section_list) - 1):
        base_a = station * radial_segments
        base_b = (station + 1) * radial_segments
        for index in range(radial_segments):
            next_index = (index + 1) % radial_segments
            faces.append(
                (
                    base_a + index,
                    base_a + next_index,
                    base_b + next_index,
                    base_b + index,
                )
            )
    faces.append(tuple(reversed(range(radial_segments))))
    last = (len(section_list) - 1) * radial_segments
    faces.append(tuple(last + index for index in range(radial_segments)))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection)
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def prism_from_planform(
    name: str,
    points_xy: list[tuple[float, float]],
    z_center: float,
    thickness: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    half = thickness / 2.0
    vertices = [(x, y, z_center - half) for x, y in points_xy]
    vertices += [(x, y, z_center + half) for x, y in points_xy]
    count = len(points_xy)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection)
    obj.data.materials.append(material)
    return obj


def create_primary_geometry(
    ledger: dict[str, Any],
    collections: dict[str, bpy.types.Collection],
    materials: dict[str, bpy.types.Material],
) -> None:
    dimensions = {
        entry["id"]: float(entry["target"])
        for entry in ledger["governed_dimensions_m"]
    }
    half_length = dimensions["overall_length"] / 2.0
    stations = [
        (
            float(item["x_fraction_of_half_length"]) * half_length,
            float(item["half_width_m"]),
            float(item["half_height_m"]),
            float(item["center_z_m"]),
        )
        for item in ledger["normalized_station_plan"]
    ]
    mesh_from_sections(
        "GEO_R4S01_FuselagePrimary",
        stations,
        32,
        collections["primary"],
        materials["primary"],
    )
    mesh_from_sections(
        "GEO_R4S01_CowlingEnvelope",
        [(2.94, 0.68, 0.68, 0.13), (3.72, 0.68, 0.68, 0.13)],
        32,
        collections["primary"],
        materials["primary"],
    )

    half_span = dimensions["wingspan"] / 2.0
    root_leading, root_trailing = 1.1, -0.95
    tip_leading, tip_trailing = 0.32, -0.73
    prism_from_planform(
        "GEO_R4S01_WingPrimary_L",
        [(root_leading, 0.0), (tip_leading, half_span), (tip_trailing, half_span), (root_trailing, 0.0)],
        0.0,
        0.16,
        collections["primary"],
        materials["primary"],
    )
    prism_from_planform(
        "GEO_R4S01_WingPrimary_R",
        [(root_leading, 0.0), (root_trailing, 0.0), (tip_trailing, -half_span), (tip_leading, -half_span)],
        0.0,
        0.16,
        collections["primary"],
        materials["primary"],
    )

    tail_half_span = float(
        ledger["provisional_authoring_parameters_m"]["horizontal_tail_span"]["value"]
    ) / 2.0
    prism_from_planform(
        "GEO_R4S01_HorizontalTail_L",
        [(-2.72, 0.0), (-3.02, tail_half_span), (-3.66, tail_half_span), (-3.55, 0.0)],
        0.47,
        0.1,
        collections["primary"],
        materials["primary"],
    )
    prism_from_planform(
        "GEO_R4S01_HorizontalTail_R",
        [(-2.72, 0.0), (-3.55, 0.0), (-3.66, -tail_half_span), (-3.02, -tail_half_span)],
        0.47,
        0.1,
        collections["primary"],
        materials["primary"],
    )

    vertical_points = [
        (-3.52, 0.48),
        (-3.34, 1.35),
        (-2.82, 1.33),
        (-2.64, 0.47),
    ]
    vertical_vertices = [
        (x, -0.05, z) for x, z in vertical_points
    ] + [(x, 0.05, z) for x, z in vertical_points]
    vertical_faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    vertical_mesh = bpy.data.meshes.new("GEO_R4S01_VerticalTail_MESH")
    vertical_mesh.from_pydata(vertical_vertices, [], vertical_faces)
    vertical_mesh.update()
    vertical_obj = bpy.data.objects.new(
        "GEO_R4S01_VerticalTail", vertical_mesh
    )
    link_object(vertical_obj, collections["primary"])
    vertical_obj.data.materials.append(materials["primary"])

    mesh_from_sections(
        "GEO_R4S01_CanopyEnvelope_Front",
        [(0.25, 0.43, 0.43, 0.91), (1.37, 0.38, 0.43, 0.92)],
        24,
        collections["primary"],
        materials["canopy"],
    )
    mesh_from_sections(
        "GEO_R4S01_CanopyEnvelope_Rear",
        [(-1.25, 0.43, 0.42, 0.91), (0.25, 0.43, 0.43, 0.91)],
        24,
        collections["primary"],
        materials["canopy"],
    )

    gear_track = float(
        ledger["provisional_authoring_parameters_m"]["main_gear_track"]["value"]
    )
    for name, location in (
        ("GEO_R4S01_GearEnvelope_Main_L", (0.25, gear_track / 2.0, -1.02)),
        ("GEO_R4S01_GearEnvelope_Main_R", (0.25, -gear_track / 2.0, -1.02)),
        ("GEO_R4S01_GearEnvelope_Nose", (2.55, 0.0, -1.02)),
    ):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20, ring_count=12, radius=0.28, location=location
        )
        gear = bpy.context.object
        gear.name = name
        gear.scale = (0.42, 1.0, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        link_object(gear, collections["primary"])
        gear.data.materials.append(materials["gear"])

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,
        radius=dimensions["propeller_diameter"] / 2.0,
        depth=0.01,
        location=(half_length - 0.005, 0.0, 0.13),
        rotation=(0.0, math.pi / 2.0, 0.0),
    )
    propeller = bpy.context.object
    propeller.name = "GEO_R4S01_PropellerDisc"
    link_object(propeller, collections["primary"])
    propeller.data.materials.append(materials["canopy"])
    propeller.display_type = "WIRE"


def create_datums(collection: bpy.types.Collection, overall_length: float) -> None:
    half_length = overall_length / 2.0
    for name, location in (
        ("DATUM_R4S01_AircraftOrigin", (0.0, 0.0, 0.0)),
        ("DATUM_R4S01_TailExtreme", (-half_length, 0.0, 0.34)),
        ("DATUM_R4S01_PropellerPlane", (half_length, 0.0, 0.13)),
        ("DATUM_R4S01_WingReference", (0.0, 0.0, 0.0)),
    ):
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = "CROSS"
        obj.empty_display_size = 0.25
        obj.location = location
        link_object(obj, collection)


def point_camera(
    camera: bpy.types.Object, target: tuple[float, float, float]
) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_cameras(
    camera_manifest: dict[str, Any], collection: bpy.types.Collection
) -> dict[str, bpy.types.Object]:
    if tuple(camera_manifest["required_camera_ids"]) != CAMERA_IDS:
        raise RuntimeError("Slice 01 camera ids/order drifted")
    cameras: dict[str, bpy.types.Object] = {}
    for spec in camera_manifest["cameras"]:
        data = bpy.data.cameras.new(spec["id"] + "_DATA")
        data.lens = float(spec["lens_mm"])
        data.clip_start = float(spec["clip_start_m"])
        if spec["projection"] == "ORTHOGRAPHIC":
            data.type = "ORTHO"
            data.ortho_scale = float(spec["ortho_scale_m"])
        camera = bpy.data.objects.new(spec["id"], data)
        camera.location = tuple(float(value) for value in spec["location_m"])
        collection.objects.link(camera)
        point_camera(camera, tuple(float(value) for value in spec["target_m"]))
        camera["SKG_OutputFilename"] = spec["output_filename"]
        camera["SKG_PromotionAllowed"] = False
        cameras[spec["id"]] = camera
    return cameras


def create_lighting(collection: bpy.types.Collection) -> None:
    specs = (
        ("LIGHT_R4S01_Key", "AREA", (4.5, -6.0, 8.0), 1600.0, 5.0),
        ("LIGHT_R4S01_Fill", "AREA", (-3.5, -4.0, 4.5), 900.0, 4.0),
        ("LIGHT_R4S01_Rim", "AREA", (-5.0, 4.0, 6.5), 1300.0, 3.0),
    )
    for name, light_type, location, energy, size in specs:
        data = bpy.data.lights.new(name + "_DATA", light_type)
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = location
        collection.objects.link(light)
        point_camera(light, (0.0, 0.0, 0.2))


def world_bounds(objects: Iterable[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("No primary mesh bounds available")
    minimum = Vector(
        (min(point.x for point in points), min(point.y for point in points), min(point.z for point in points))
    )
    maximum = Vector(
        (max(point.x for point in points), max(point.y for point in points), max(point.z for point in points))
    )
    return minimum, maximum


def triangulated_face_count(obj: bpy.types.Object) -> int:
    return sum(max(1, len(polygon.vertices) - 2) for polygon in obj.data.polygons)


def validate_scene(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    camera_manifest: dict[str, Any],
    collections: dict[str, bpy.types.Collection],
) -> dict[str, Any]:
    errors: list[str] = []
    expected_collections = set(COLLECTIONS.values())
    observed_collections = {
        name for name in expected_collections if bpy.data.collections.get(name)
    }
    if observed_collections != expected_collections:
        errors.append("collection_set_mismatch")
    observed_primary = {obj.name for obj in collections["primary"].objects}
    if observed_primary != set(PRIMARY_OBJECTS):
        errors.append("primary_object_set_mismatch")
    observed_datums = {obj.name for obj in collections["datums"].objects}
    if observed_datums != set(DATUM_OBJECTS):
        errors.append("datum_object_set_mismatch")
    observed_cameras = {obj.name for obj in collections["cameras"].objects}
    required_cameras = set(camera_manifest["required_camera_ids"])
    if observed_cameras != required_cameras:
        errors.append("camera_object_set_mismatch")

    primary_objects = [bpy.data.objects[name] for name in PRIMARY_OBJECTS]
    minimum, maximum = world_bounds(primary_objects)
    measured = {
        "overall_length": maximum.x - minimum.x,
        "wingspan": maximum.y - minimum.y,
        "overall_height": maximum.z - minimum.z,
    }
    dimensions = {
        entry["id"]: entry for entry in ledger["governed_dimensions_m"]
    }
    for dimension_id in ("overall_length", "wingspan", "overall_height"):
        entry = dimensions[dimension_id]
        if abs(measured[dimension_id] - float(entry["target"])) > float(
            entry["tolerance"]
        ):
            errors.append(f"dimension_out_of_tolerance:{dimension_id}")
    prop = bpy.data.objects["GEO_R4S01_PropellerDisc"]
    prop_diameter = max(prop.dimensions.y, prop.dimensions.z)
    prop_entry = dimensions["propeller_diameter"]
    measured["propeller_diameter"] = prop_diameter
    if abs(prop_diameter - float(prop_entry["target"])) > float(
        prop_entry["tolerance"]
    ):
        errors.append("dimension_out_of_tolerance:propeller_diameter")

    left = bpy.data.objects["GEO_R4S01_WingPrimary_L"]
    right = bpy.data.objects["GEO_R4S01_WingPrimary_R"]
    symmetry_error = max(
        abs(left.dimensions.x - right.dimensions.x),
        abs(left.dimensions.y - right.dimensions.y),
        abs(left.dimensions.z - right.dimensions.z),
    )
    if symmetry_error > float(ledger["offline_checks"]["symmetry_tolerance_m"]):
        errors.append("wing_symmetry_tolerance_exceeded")
    total_triangles = sum(triangulated_face_count(obj) for obj in primary_objects)
    if total_triangles > int(
        ledger["offline_checks"]["primary_mesh_total_triangle_budget"]
    ):
        errors.append("primary_triangle_budget_exceeded")
    for obj in primary_objects:
        if any(abs(value - 1.0) > 1e-6 for value in obj.scale):
            errors.append(f"unapplied_scale:{obj.name}")
        if obj.get("SKG_PromotionAllowed") is not False:
            errors.append(f"promotion_flag_invalid:{obj.name}")
    if ledger["reference_package_status"]["silhouette_lock_allowed"] is not False:
        errors.append("reference_package_untruthfully_allows_lock")
    if contract["claims"]["silhouette_locked"] is not False:
        errors.append("contract_untruthfully_claims_silhouette_lock")
    if errors:
        raise RuntimeError("Slice 01 scene validation failed: " + ";".join(errors))
    return {
        "bounds_min_m": list(minimum),
        "bounds_max_m": list(maximum),
        "measured_dimensions_m": measured,
        "wing_symmetry_error_m": symmetry_error,
        "primary_triangle_count": total_triangles,
        "primary_object_count": len(primary_objects),
        "camera_count": len(required_cameras),
        "validation_errors": errors,
    }


def configure_render(camera_manifest: dict[str, Any]) -> None:
    render = camera_manifest["render_contract"]
    scene = bpy.context.scene
    scene.render.engine = render["engine"]
    scene.render.resolution_x = int(render["resolution_x"])
    scene.render.resolution_y = int(render["resolution_y"])
    scene.render.resolution_percentage = int(render["resolution_percentage"])
    scene.render.pixel_aspect_x = float(render["pixel_aspect"])
    scene.render.pixel_aspect_y = 1.0
    scene.render.image_settings.file_format = render["file_format"]
    scene.world.color = tuple(render["neutral_world_color"][:3])


def render_comparisons(
    camera_manifest: dict[str, Any], cameras: dict[str, bpy.types.Object]
) -> list[dict[str, Any]]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=False)
    receipts: list[dict[str, Any]] = []
    for spec in camera_manifest["cameras"]:
        path = SCREENSHOT_DIR / spec["output_filename"]
        bpy.context.scene.camera = cameras[spec["id"]]
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        receipts.append(
            {
                "camera_id": spec["id"],
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return receipts


def export_glb(primary_collection: bpy.types.Collection, temp_path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in primary_collection.objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(temp_path),
        export_format="GLB",
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_yup=True,
    )


def main() -> None:
    started = time.perf_counter()
    random.seed(RANDOM_SEED)
    require_blender_52()
    contract = read_json(OUTPUT_CONTRACT_PATH)
    ledger = read_json(DIMENSION_LEDGER_PATH)
    camera_manifest = read_json(CAMERA_MANIFEST_PATH)
    r4_contract = read_json(R4_CONTRACT_PATH)
    validate_authorities(contract)
    ensure_canonical_outputs_absent(contract)
    if r4_contract.get("contract_id") != (
        "PHASE2-YAK52-R4-FINAL-ART-GAP-20260802-V1"
    ):
        raise RuntimeError("Accepted R4 contract id mismatch")

    collections = reset_scene()
    material_map = {
        "primary": neutral_material(
            MATERIALS[0], (0.32, 0.38, 0.43, 1.0), 0.52
        ),
        "canopy": neutral_material(
            MATERIALS[1], (0.12, 0.34, 0.50, 1.0), 0.24
        ),
        "gear": neutral_material(
            MATERIALS[2], (0.08, 0.08, 0.08, 1.0), 0.62
        ),
    }
    create_primary_geometry(ledger, collections, material_map)
    overall_length = next(
        float(entry["target"])
        for entry in ledger["governed_dimensions_m"]
        if entry["id"] == "overall_length"
    )
    create_datums(collections["datums"], overall_length)
    cameras = create_cameras(camera_manifest, collections["cameras"])
    create_lighting(collections["lighting"])
    configure_render(camera_manifest)
    measurements = validate_scene(contract, ledger, camera_manifest, collections)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_blend = BLEND_PATH.with_suffix(".blend.tmp")
    temp_glb = GLB_PATH.with_suffix(".glb.tmp")
    bpy.ops.wm.save_as_mainfile(filepath=str(temp_blend))
    export_glb(collections["primary"], temp_glb)
    comparisons = render_comparisons(camera_manifest, cameras)

    manifest = {
        "schema": "skyguard.phase2.yak52-r4-slice01-artifact-manifest.v1",
        "build_id": BUILD_ID,
        "status": "DRAFT_REFERENCE_PACKAGE_MISSING",
        "authorities": {
            entry["path"]: entry["sha256"]
            for entry in contract["authority_inputs"]
        },
        "authoring_script_sha256": sha256_file(SCRIPT_PATH),
        "collection_names": sorted(COLLECTIONS.values()),
        "primary_objects": list(PRIMARY_OBJECTS),
        "datum_objects": list(DATUM_OBJECTS),
        "camera_ids": camera_manifest["required_camera_ids"],
        "measurements": measurements,
        "comparisons": comparisons,
        "claims": {
            "reference_package_complete": False,
            "silhouette_locked": False,
            "slice01_human_accepted": False,
            "final": False,
            "aaa": False,
            "unreal_imported": False,
            "runtime_replaced": False,
            "promotion_allowed": False,
        },
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    temp_manifest = MANIFEST_PATH.with_suffix(".json.tmp")
    temp_manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp_blend.replace(BLEND_PATH)
    temp_glb.replace(GLB_PATH)
    temp_manifest.replace(MANIFEST_PATH)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"{BUILD_ID} FAILED: {exc}", file=sys.stderr)
        raise
