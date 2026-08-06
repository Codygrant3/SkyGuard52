from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01"
ASSET = "PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON"
DIMENSIONS_M = {
    "coupon_length": 0.12,
    "top_width": 0.021209,
    "profile_height_min": 0.009322,
    "dovetail_width": 0.018999,
    "groove_width": 0.005232,
    "pitch": 0.010008,
}
LOWER_WIDTH_M = 0.015672
BASE_HEIGHT_M = 0.004
TOOTH_LENGTH_M = DIMENSIONS_M["pitch"] - DIMENSIONS_M["groove_width"]
RENDER_RESOLUTION = 2048


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            datablocks.remove(datablock)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def make_collection() -> bpy.types.Collection:
    collection = bpy.data.collections.new(ASSET)
    bpy.context.scene.collection.children.link(collection)
    collection["gate"] = GATE
    collection["classification"] = "PRODUCTION_REFINEMENT_PASS_01"
    collection["provisional"] = True
    collection["scope"] = "dimensional validation coupon only; not a complete weapon component"
    collection["authoritative_dimensions_m"] = json.dumps(DIMENSIONS_M, sort_keys=True)
    return collection


def make_phosphate_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_PROVISIONAL_Rail_Phosphate_PBR")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = (0.035, 0.042, 0.048, 1.0)
    shader.inputs["Metallic"].default_value = 0.88
    shader.inputs["Roughness"].default_value = 0.36

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 460.0
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.72
    noise.inputs["Distortion"].default_value = 0.08

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.018, 0.022, 0.026, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.075, 0.085, 0.095, 1)

    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.00004

    roughness_map = nodes.new("ShaderNodeMapRange")
    roughness_map.inputs["From Min"].default_value = 0.0
    roughness_map.inputs["From Max"].default_value = 1.0
    roughness_map.inputs["To Min"].default_value = 0.28
    roughness_map.inputs["To Max"].default_value = 0.46

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(noise.outputs["Fac"], roughness_map.inputs["Value"])
    links.new(roughness_map.outputs["Result"], shader.inputs["Roughness"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    material["pbr_layers"] = json.dumps(
        ["phosphate/anodized metal", "micro scratch", "subtle edge wear", "oil response"]
    )
    material["identity_scope"] = "generic validation coupon surface; no manufacturer claim"
    return material


def make_stage_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = roughness
    return material


def apply_bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    modifier = obj.modifiers.new("REFINEMENT_MicroEdgeBevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(25.0)


def make_box(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    target: bpy.types.Collection,
    material: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj["provisional"] = True
    obj["asset_scope"] = "validation coupon"
    move_to_collection(obj, target)
    if bevel > 0.0:
        apply_bevel(obj, bevel)
    return obj


def make_profile_prism(
    name: str,
    x0: float,
    x1: float,
    bottom_width: float,
    top_width: float,
    z0: float,
    z1: float,
    target: bpy.types.Collection,
    material: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bottom = bottom_width / 2.0
    top = top_width / 2.0
    vertices = [
        (x0, -bottom, z0),
        (x0, bottom, z0),
        (x0, -top, z1),
        (x0, top, z1),
        (x1, -bottom, z0),
        (x1, bottom, z0),
        (x1, -top, z1),
        (x1, top, z1),
    ]
    faces = [
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
        (0, 1, 3, 2),
        (4, 6, 7, 5),
    ]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.data.materials.append(material)
    obj["provisional"] = True
    obj["asset_scope"] = "validation coupon"
    if bevel > 0.0:
        apply_bevel(obj, bevel)
    return obj


def make_empty(name: str, target: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.012
    obj.location = (0.0, 0.0, 0.0)
    obj["role"] = "validation origin"
    obj["provisional"] = True
    target.objects.link(obj)
    return obj


def add_planar_uv(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def build_coupon() -> tuple[bpy.types.Collection, bpy.types.Material]:
    collection = make_collection()
    material = make_phosphate_material()

    base = make_box(
        "RAIL_Coupon_Base",
        (DIMENSIONS_M["coupon_length"], LOWER_WIDTH_M, BASE_HEIGHT_M),
        (0.0, 0.0, BASE_HEIGHT_M / 2.0),
        collection,
        material,
        bevel=0.00018,
    )
    base["authoritative_coupon_length_m"] = DIMENSIONS_M["coupon_length"]
    base["lower_width_m"] = LOWER_WIDTH_M

    tooth_count = 12
    first_center = -((tooth_count - 1) * DIMENSIONS_M["pitch"]) / 2.0
    for index in range(tooth_count):
        center = first_center + index * DIMENSIONS_M["pitch"]
        tooth = make_profile_prism(
            f"RAIL_Coupon_Tooth_{index:02d}",
            center - TOOTH_LENGTH_M / 2.0,
            center + TOOTH_LENGTH_M / 2.0,
            DIMENSIONS_M["dovetail_width"],
            DIMENSIONS_M["top_width"],
            BASE_HEIGHT_M,
            DIMENSIONS_M["profile_height_min"],
            collection,
            material,
            bevel=0.00012,
        )
        tooth["tooth_index"] = index
        tooth["authoritative_pitch_m"] = DIMENSIONS_M["pitch"]
        tooth["authoritative_groove_width_m"] = DIMENSIONS_M["groove_width"]

    collision_material = make_stage_material("MAT_UCX_NonRender", (0.08, 0.15, 0.10, 1), 0.8)
    collision = make_profile_prism(
        "UCX_RailCoupon_ProfilePrism",
        -DIMENSIONS_M["coupon_length"] / 2.0,
        DIMENSIONS_M["coupon_length"] / 2.0,
        LOWER_WIDTH_M,
        DIMENSIONS_M["top_width"],
        0.0,
        DIMENSIONS_M["profile_height_min"],
        collection,
        collision_material,
    )
    collision.hide_render = True
    collision.display_type = "WIRE"
    collision["collision_scope"] = "simple validation prism; not gameplay weapon collision"

    make_empty("SOCKET_Rail_Origin", collection)
    for obj in collection.all_objects:
        add_planar_uv(obj)
    return collection, material


def collection_bbox(collection: bpy.types.Collection, include_collision: bool = False) -> dict[str, list[float]]:
    points: list[Vector] = []
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        if not include_collision and obj.name.startswith("UCX_"):
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    lower = [min(point[index] for point in points) for index in range(3)]
    upper = [max(point[index] for point in points) for index in range(3)]
    return {
        "min_m": lower,
        "max_m": upper,
        "size_m": [upper[index] - lower[index] for index in range(3)],
    }


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_stage() -> dict[str, bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RENDER_RESOLUTION
    scene.render.resolution_y = RENDER_RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15

    floor_material = make_stage_material("MAT_STAGE_Neutral", (0.055, 0.062, 0.072, 1), 0.74)
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0.0, 0.0, -0.0012))
    floor = bpy.context.object
    floor.name = "STAGE_NeutralFloor"
    floor.data.materials.append(floor_material)

    bpy.ops.object.light_add(type="AREA", location=(0.18, -0.16, 0.20))
    key = bpy.context.object
    key.name = "LIGHT_Key"
    key.data.shape = "DISK"
    key.data.size = 0.20
    look_at(key, (0.0, 0.0, 0.004))

    bpy.ops.object.light_add(type="AREA", location=(-0.16, -0.10, 0.10))
    fill = bpy.context.object
    fill.name = "LIGHT_Fill"
    fill.data.size = 0.16
    look_at(fill, (0.0, 0.0, 0.004))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.15, 0.12))
    rim = bpy.context.object
    rim.name = "LIGHT_Rim"
    rim.data.size = 0.12
    look_at(rim, (0.0, 0.0, 0.004))

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "CAMERA_Cycle03_FixedReview"
    scene.camera = camera
    return {"floor": floor, "key": key, "fill": fill, "rim": rim, "camera": camera}


LIGHTING = {
    "daylight": {
        "world": (0.075, 0.095, 0.13),
        "key": (1150.0, (1.0, 0.84, 0.68)),
        "fill": (520.0, (0.50, 0.67, 1.0)),
        "rim": (760.0, (0.75, 0.86, 1.0)),
    },
    "overcast": {
        "world": (0.095, 0.105, 0.12),
        "key": (680.0, (0.78, 0.84, 0.94)),
        "fill": (570.0, (0.72, 0.80, 0.92)),
        "rim": (430.0, (0.80, 0.86, 0.96)),
    },
    "night": {
        "world": (0.004, 0.007, 0.016),
        "key": (520.0, (0.18, 0.34, 1.0)),
        "fill": (130.0, (0.08, 0.14, 0.32)),
        "rim": (820.0, (0.95, 0.22, 0.08)),
    },
    "wet": {
        "world": (0.025, 0.035, 0.055),
        "key": (980.0, (0.55, 0.72, 1.0)),
        "fill": (320.0, (0.32, 0.50, 0.88)),
        "rim": (1080.0, (1.0, 0.54, 0.24)),
    },
    "cockpit_light": {
        "world": (0.007, 0.010, 0.015),
        "key": (520.0, (0.22, 0.78, 0.44)),
        "fill": (260.0, (0.95, 0.16, 0.08)),
        "rim": (460.0, (0.14, 0.32, 0.72)),
    },
}


def apply_lighting(stage: dict[str, bpy.types.Object], lighting_name: str) -> None:
    values = LIGHTING[lighting_name]
    bpy.context.scene.world.color = values["world"]
    for light_name in ("key", "fill", "rim"):
        light = stage[light_name]
        energy, color = values[light_name]
        light.data.energy = energy
        light.data.color = color


def configure_camera(
    camera: bpy.types.Object,
    camera_type: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float | None = None,
    lens: float | None = None,
) -> None:
    camera.data.type = camera_type
    camera.location = location
    look_at(camera, target)
    if camera_type == "ORTHO" and ortho_scale is not None:
        camera.data.ortho_scale = ortho_scale
    if camera_type == "PERSP" and lens is not None:
        camera.data.lens = lens


def render_review_set(
    output: Path,
    stage: dict[str, bpy.types.Object],
    rail_material: bpy.types.Material,
) -> list[dict[str, object]]:
    renders = output / "renders"
    renders.mkdir()
    camera = stage["camera"]
    shader = rail_material.node_tree.nodes.get("Principled BSDF")
    dry_metallic = float(shader.inputs["Metallic"].default_value)
    render_specs = [
        ("ortho_front_daylight", "daylight", "ORTHO", (0.18, 0.0, 0.012), (0.0, 0.0, 0.0047), 0.032, None),
        ("ortho_side_overcast", "overcast", "ORTHO", (0.0, -0.22, 0.020), (0.0, 0.0, 0.0047), 0.140, None),
        ("ortho_top_daylight", "daylight", "ORTHO", (0.0, 0.0, 0.24), (0.0, 0.0, 0.0), 0.140, None),
        ("ortho_rear_cockpit_light", "cockpit_light", "ORTHO", (-0.18, 0.0, 0.012), (0.0, 0.0, 0.0047), 0.032, None),
        ("section_cockpit_light", "cockpit_light", "ORTHO", (0.18, 0.0, 0.012), (0.0, 0.0, 0.0047), 0.026, None),
        ("hero_q_daylight", "daylight", "PERSP", (0.145, -0.135, 0.085), (0.0, 0.0, 0.004), None, 72.0),
        ("hero_q_overcast", "overcast", "PERSP", (0.145, -0.135, 0.085), (0.0, 0.0, 0.004), None, 72.0),
        ("hero_q_night", "night", "PERSP", (0.145, -0.135, 0.085), (0.0, 0.0, 0.004), None, 72.0),
        ("hero_q_wet", "wet", "PERSP", (0.145, -0.135, 0.085), (0.0, 0.0, 0.004), None, 72.0),
        ("hero_q_cockpit_light", "cockpit_light", "PERSP", (0.145, -0.135, 0.085), (0.0, 0.0, 0.004), None, 72.0),
        ("detail_wet", "wet", "PERSP", (0.035, -0.060, 0.030), (0.017, 0.0, 0.006), None, 92.0),
    ]
    records: list[dict[str, object]] = []
    for name, lighting, camera_type, location, target, ortho_scale, lens in render_specs:
        apply_lighting(stage, lighting)
        configure_camera(camera, camera_type, location, target, ortho_scale, lens)
        if lighting == "wet":
            shader.inputs["Metallic"].default_value = 0.94
        else:
            shader.inputs["Metallic"].default_value = dry_metallic
        render_path = renders / f"{name}.png"
        bpy.context.scene.render.filepath = str(render_path)
        bpy.ops.render.render(write_still=True)
        records.append(
            {
                "name": name,
                "camera_type": camera_type,
                "lighting": lighting,
                "resolution": [RENDER_RESOLUTION, RENDER_RESOLUTION],
                "path": render_path.relative_to(output).as_posix(),
                "bytes": render_path.stat().st_size,
                "sha256": sha256(render_path),
            }
        )
    shader.inputs["Metallic"].default_value = dry_metallic
    apply_lighting(stage, "daylight")
    return records


def export_glb(collection: bpy.types.Collection, output_path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.all_objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
    )


def inspect_glb(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        header = stream.read(12)
        magic, version, total_length = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2:
            raise RuntimeError("GLB header is not glTF 2.0")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        if json_type != 0x4E4F534A:
            raise RuntimeError("GLB first chunk is not JSON")
        document = json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 "))
    node_names = [node.get("name") for node in document.get("nodes", [])]
    return {
        "version": version,
        "declared_length": total_length,
        "actual_length": path.stat().st_size,
        "node_names": node_names,
        "socket_present": "SOCKET_Rail_Origin" in node_names,
        "collision_present": "UCX_RailCoupon_ProfilePrism" in node_names,
        "mesh_count": len(document.get("meshes", [])),
        "material_count": len(document.get("materials", [])),
    }


def validate_dimensions(bbox: dict[str, list[float]]) -> dict[str, object]:
    measured = bbox["size_m"]
    expected = [
        DIMENSIONS_M["coupon_length"],
        DIMENSIONS_M["top_width"],
        DIMENSIONS_M["profile_height_min"],
    ]
    tolerance = 0.000001
    axes = ["length_x", "top_width_y", "height_z"]
    checks = []
    for axis, actual, target in zip(axes, measured, expected):
        delta = abs(actual - target)
        checks.append(
            {
                "axis": axis,
                "measured_m": actual,
                "expected_m": target,
                "absolute_delta_m": delta,
                "tolerance_m": tolerance,
                "passed": delta <= tolerance,
            }
        )
    return {
        "checks": checks,
        "all_passed": all(item["passed"] for item in checks),
        "authoritative_dimensions_m": DIMENSIONS_M,
        "derived_tooth_length_m": TOOTH_LENGTH_M,
        "tooth_count": 12,
    }


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    exports = output / "exports"
    exports.mkdir()

    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    collection, rail_material = build_coupon()
    stage = setup_stage()
    bbox = collection_bbox(collection)
    dimension_validation = validate_dimensions(bbox)
    if not dimension_validation["all_passed"]:
        raise RuntimeError("Rail coupon bounding dimensions failed authority validation")

    render_records = render_review_set(output, stage, rail_material)
    if len(render_records) != 11:
        raise RuntimeError("Cycle03 camera/lighting contract did not produce exactly eleven governed renders")

    glb_path = exports / f"{ASSET}.glb"
    export_glb(collection, glb_path)
    glb_structure = inspect_glb(glb_path)
    if not glb_structure["socket_present"] or not glb_structure["collision_present"]:
        raise RuntimeError("GLB is missing the governed socket or collision node")

    blend_path = output / f"{GATE}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    dimension_receipt = {
        "gate": GATE,
        "asset": ASSET,
        "classification": "PASSED_DIMENSIONAL_REFINEMENT_VALIDATION",
        "timestamp_utc": utc_now(),
        "blender_version": bpy.app.version_string,
        "units": "metres",
        "scope": "dimensional validation coupon only; not a complete weapon component",
        "bbox": bbox,
        "dimension_validation": dimension_validation,
        "socket": "SOCKET_Rail_Origin",
        "collision": "UCX_RailCoupon_ProfilePrism",
        "unsupported_identity_claims": [],
    }
    dimension_receipt_path = output / "dimension_receipt.json"
    write_json(dimension_receipt_path, dimension_receipt)

    glb_receipt = {
        "gate": GATE,
        "asset": ASSET,
        "path": glb_path.relative_to(output).as_posix(),
        "bytes": glb_path.stat().st_size,
        "sha256": sha256(glb_path),
        "structure": glb_structure,
    }
    glb_receipt_path = output / "glb_structure_receipt.json"
    write_json(glb_receipt_path, glb_receipt)

    core_artifacts = [blend_path, glb_path, dimension_receipt_path, glb_receipt_path]
    core_artifacts.extend(output / record["path"] for record in render_records)
    inventory = {
        "gate": GATE,
        "asset": ASSET,
        "timestamp_utc": utc_now(),
        "files": [
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in core_artifacts
        ],
        "counts": {
            "blend": 1,
            "glb": 1,
            "png": len(render_records),
            "dimension_receipt": 1,
            "glb_structure_receipt": 1,
        },
        "renders": render_records,
    }
    inventory_path = output / "artifact_inventory.json"
    write_json(inventory_path, inventory)

    terminal = {
        "gate": GATE,
        "asset": ASSET,
        "status": "BLENDER_COMPLETED_AWAITING_EXTERNAL_VISUAL_REVIEW",
        "timestamp_utc": utc_now(),
        "blender_version": bpy.app.version_string,
        "blend_count": 1,
        "glb_count": 1,
        "render_count": len(render_records),
        "socket_present": glb_structure["socket_present"],
        "collision_present": glb_structure["collision_present"],
        "dimensions_passed": dimension_validation["all_passed"],
        "scope": "dimensional validation coupon only; not a complete weapon component",
    }
    terminal_path = output / "terminal_receipt.json"
    write_json(terminal_path, terminal)
    print(json.dumps(terminal, indent=2))


if __name__ == "__main__":
    main()
