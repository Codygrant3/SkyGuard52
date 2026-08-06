"""Procedural source generator for BLD-M01-COAST-PROD-001.

This script starts from Blender factory state, imports no geometry, reads the
review screenshot only through its hash-bound contract record, and writes into
an isolated Mission 1 coastal-production namespace.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy


BUILD_ID = "BLD-M01-COAST-PROD-001"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_COAST_PROD_001_CONTRACT.json"
)
OUTPUT_DIR = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Coastal_Production_001"
)
EXPORT_DIR = OUTPUT_DIR / "Exports"
BLEND_PATH = OUTPUT_DIR / "BLD_M01_COAST_PROD_001_MASTER.blend"
MANIFEST_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_COAST_PROD_001_MANIFEST.json"
COLLECTION_NAME = "BLD_M01_COAST_PROD_001_EXPORT"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("build_id") != BUILD_ID:
        raise RuntimeError("Coastal production contract id mismatch")
    return contract


def require_blender_52() -> None:
    if bpy.app.version[:2] != (5, 2):
        raise RuntimeError(
            f"{BUILD_ID} requires Blender 5.2, found "
            f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        )


def verify_rejection_evidence(contract: dict) -> None:
    record = contract["rejection_evidence"]
    path = ROOT / record["path"]
    if (
        not path.is_file()
        or path.stat().st_size != record["bytes"]
        or sha256_file(path) != record["sha256"]
    ):
        raise RuntimeError("Hash-bound rejection evidence is missing or drifted")
    if record["allowed_use"] != "Visual rejection evidence only.":
        raise RuntimeError("Review evidence use widened beyond rejection evidence")


def reset_factory_scene() -> bpy.types.Collection:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    return collection


def material(name: str, color: tuple[float, float, float, float], roughness: float,
             metallic: float = 0.0) -> bpy.types.Material:
    value = bpy.data.materials.new(name)
    value.diffuse_color = color
    value.use_nodes = True
    node = value.node_tree.nodes.get("Principled BSDF")
    if node:
        node.inputs["Base Color"].default_value = color
        node.inputs["Roughness"].default_value = roughness
        node.inputs["Metallic"].default_value = metallic
    return value


def build_materials(contract: dict) -> dict[int, bpy.types.Material]:
    definitions = {
        1: ("MAT_COAST001_SandMacro", (0.42, 0.34, 0.23, 1.0), 0.88, 0.0),
        2: ("MAT_COAST001_DuneSoil", (0.25, 0.20, 0.13, 1.0), 0.94, 0.0),
        3: ("MAT_COAST001_VegetationMask", (0.18, 0.25, 0.10, 1.0), 0.90, 0.0),
        10: ("MAT_COAST001_SeawallConcrete", (0.34, 0.36, 0.35, 1.0), 0.72, 0.0),
        11: ("MAT_COAST001_Asphalt", (0.055, 0.06, 0.065, 1.0), 0.80, 0.0),
        12: ("MAT_COAST001_CurbConcrete", (0.44, 0.45, 0.43, 1.0), 0.70, 0.0),
        13: ("MAT_COAST001_DrainMetal", (0.12, 0.14, 0.15, 1.0), 0.42, 0.72),
        14: ("MAT_COAST001_SidewalkPaver", (0.38, 0.35, 0.31, 1.0), 0.75, 0.0),
        20: ("MAT_COAST001_Plaster", (0.46, 0.43, 0.36, 1.0), 0.78, 0.0),
        21: ("MAT_COAST001_ExposedConcrete", (0.30, 0.31, 0.29, 1.0), 0.82, 0.0),
        22: ("MAT_COAST001_Brick", (0.29, 0.12, 0.075, 1.0), 0.86, 0.0),
        23: ("MAT_COAST001_WindowGlass", (0.07, 0.16, 0.20, 0.65), 0.15, 0.05),
        24: ("MAT_COAST001_BalconyMetal", (0.09, 0.10, 0.10, 1.0), 0.43, 0.75),
        25: ("MAT_COAST001_RoofMembrane", (0.10, 0.11, 0.105, 1.0), 0.84, 0.0),
        90: ("MAT_COAST001_TrimSheet", (0.37, 0.39, 0.38, 1.0), 0.58, 0.12),
        100: ("MAT_COAST001_DecalGrime", (0.08, 0.07, 0.055, 1.0), 0.90, 0.0),
        101: ("MAT_COAST001_DecalSalt", (0.62, 0.62, 0.57, 1.0), 0.80, 0.0),
        102: ("MAT_COAST001_DecalDamage", (0.13, 0.12, 0.105, 1.0), 0.82, 0.0),
    }
    expected = set(contract["material_id_contract"].values())
    if expected != set(definitions):
        raise RuntimeError("Material id definitions drifted from contract")
    return {
        identity: material(*definition)
        for identity, definition in definitions.items()
    }


def link_only(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def ensure_uv0_uv1(obj: bpy.types.Object, dimensions: list[float]) -> None:
    mesh = obj.data
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])
    uv0 = mesh.uv_layers.new(name="UV0")
    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(normal.z) >= max(abs(normal.x), abs(normal.y)):
                uv = (co.x / 4.0, co.y / 4.0)
            elif abs(normal.y) >= abs(normal.x):
                uv = (co.x / 4.0, co.z / 4.0)
            else:
                uv = (co.y / 4.0, co.z / 4.0)
            uv0.data[loop_index].uv = uv
    uv1 = mesh.uv_layers.new(name="UV1")
    mesh.uv_layers.active = uv1
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66.0),
        island_margin=0.025,
        area_weight=0.0,
        correct_aspect=True,
        scale_to_bounds=True,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    mesh["sg_uv0_intent"] = "tiling_trim_decal_real_world_scale"
    mesh["sg_uv1_intent"] = "smart_project_unique_lightmap_candidate"


def apply_asset_metadata(obj: bpy.types.Object, spec: dict) -> None:
    obj["sg_build_id"] = BUILD_ID
    obj["sg_kind"] = spec["kind"]
    obj["sg_dimensions_m"] = json.dumps(spec["dimensions_m"])
    obj["sg_material_ids"] = json.dumps(spec["materials"])
    obj["sg_snap_sockets"] = json.dumps(spec["snap_sockets"])
    obj["sg_collision_strategy"] = spec["collision"]
    obj["sg_nanite_intent"] = bool(spec["nanite"])
    obj["sg_lod_intent"] = spec["lod_intent"]
    obj["sg_pivot_contract"] = "southwest_ground_or_seaward_west_bottom"
    obj["sg_external_geometry_imported"] = False


def assign_materials(obj: bpy.types.Object, ids: list[int],
                     materials: dict[int, bpy.types.Material]) -> None:
    for identity in ids:
        obj.data.materials.append(materials[identity])
    for index, polygon in enumerate(obj.data.polygons):
        polygon.material_index = index % max(1, len(ids))


def set_pivot_to_origin(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    obj.select_set(False)


def create_box(name: str, dimensions: list[float], collection: bpy.types.Collection,
               bevel: float = 0.03) -> bpy.types.Object:
    dx, dy, dz = map(float, dimensions)
    bpy.ops.mesh.primitive_cube_add(location=(dx * 0.5, dy * 0.5, dz * 0.5))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (dx, dy, dz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj, collection)
    if bevel > 0.0:
        modifier = obj.modifiers.new("MOD_COAST001_EdgeBevel", "BEVEL")
        modifier.width = min(bevel, min(dx, dy, dz) * 0.2)
        modifier.segments = 2
    set_pivot_to_origin(obj)
    return obj


def join_components(name: str, parts: list[bpy.types.Object],
                    collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    result = bpy.context.object
    result.name = name
    link_only(result, collection)
    set_pivot_to_origin(result)
    return result


def terrain_height(kind: str, x: float, y: float, variant: float) -> float:
    along = math.sin(math.pi * x / 100.0) ** 2
    if y < 18.0:
        base = 0.10 + y * 0.025
    elif y < 38.0:
        t = (y - 18.0) / 20.0
        base = 0.55 + 1.45 * math.sin(t * math.pi * 0.5)
    elif y < 50.0:
        base = 2.0 - (y - 38.0) * 0.035
    elif y < 62.0:
        base = 1.58
    elif y < 72.0:
        crown = 1.0 - abs((y - 67.0) / 5.0)
        base = 1.48 + max(0.0, crown) * 0.12
    else:
        base = 1.52 + (y - 72.0) * 0.02
    if kind == "terrain_transition":
        base += 0.10 * max(0.0, min(1.0, (y - 42.0) / 20.0))
    return base + variant * along * math.sin(y * 0.37) * 0.18


def create_solid_terrain(spec: dict, collection: bpy.types.Collection,
                         variant: float) -> bpy.types.Object:
    name = spec["name"]
    length, width, _ = map(float, spec["dimensions_m"])
    x_steps, y_steps = 20, 16
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for yi in range(y_steps + 1):
        y = width * yi / y_steps
        for xi in range(x_steps + 1):
            x = length * xi / x_steps
            vertices.append((x, y, terrain_height(spec["kind"], x, y, variant)))
    row = x_steps + 1
    for yi in range(y_steps):
        for xi in range(x_steps):
            a = yi * row + xi
            faces.append((a, a + 1, a + row + 1, a + row))
    bottom_z = -2.0
    bottom_start = len(vertices)
    vertices.extend(
        [(0.0, 0.0, bottom_z), (length, 0.0, bottom_z),
         (length, width, bottom_z), (0.0, width, bottom_z)]
    )
    faces.append((bottom_start, bottom_start + 3, bottom_start + 2, bottom_start + 1))
    south = [xi for xi in range(row)]
    north = [y_steps * row + xi for xi in range(row)]
    west = [yi * row for yi in range(y_steps + 1)]
    east = [yi * row + x_steps for yi in range(y_steps + 1)]
    for boundary, b0, b1 in (
        (south, bottom_start, bottom_start + 1),
        (east, bottom_start + 1, bottom_start + 2),
        (list(reversed(north)), bottom_start + 2, bottom_start + 3),
        (list(reversed(west)), bottom_start + 3, bottom_start),
    ):
        for index in range(len(boundary) - 1):
            t0 = index / (len(boundary) - 1)
            t1 = (index + 1) / (len(boundary) - 1)
            base0 = len(vertices)
            p0 = vertices[b0]
            p1 = vertices[b1]
            vertices.append(
                (p0[0] + (p1[0] - p0[0]) * t0,
                 p0[1] + (p1[1] - p0[1]) * t0, bottom_z)
            )
            vertices.append(
                (p0[0] + (p1[0] - p0[0]) * t1,
                 p0[1] + (p1[1] - p0[1]) * t1, bottom_z)
            )
            faces.append((boundary[index], boundary[index + 1], base0 + 1, base0))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def create_crowned_road(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    length, width, height = map(float, spec["dimensions_m"])
    crown = 0.12
    vertices = [
        (0, 0, 0), (length, 0, 0), (length, width, 0), (0, width, 0),
        (0, 0, height), (length, 0, height),
        (length, width * 0.5, height + crown), (0, width * 0.5, height + crown),
        (length, width, height), (0, width, height),
    ]
    faces = [
        (0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 8, 9),
        (4, 7, 6, 5), (7, 9, 8, 6), (0, 3, 9, 7, 4),
        (1, 5, 6, 8, 2),
    ]
    mesh = bpy.data.meshes.new(spec["name"] + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(spec["name"], mesh)
    collection.objects.link(obj)
    return obj


def create_l_shape(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    width = min(1.2, dx, dy)
    parts = [
        create_box(spec["name"] + "_LEG_X", [dx, width, dz], collection, 0.04),
        create_box(spec["name"] + "_LEG_Y", [width, dy, dz], collection, 0.04),
    ]
    return join_components(spec["name"], parts, collection)


def create_ramp(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    vertices = [
        (0, 0, 0), (dx, 0, 0), (dx, dy, 0), (0, dy, 0),
        (0, 0, dz), (0, dy, dz), (dx, 0, dz * 0.35), (dx, dy, dz * 0.35),
    ]
    faces = [
        (0, 1, 2, 3), (0, 4, 6, 1), (3, 2, 7, 5),
        (0, 3, 5, 4), (1, 6, 7, 2), (4, 5, 7, 6),
    ]
    mesh = bpy.data.meshes.new(spec["name"] + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(spec["name"], mesh)
    collection.objects.link(obj)
    return obj


def create_drain_channel(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    wall = 0.08
    parts = [
        create_box(spec["name"] + "_BED", [dx, dy, wall], collection, 0.015),
        create_box(spec["name"] + "_SIDE_A", [dx, wall, dz], collection, 0.015),
        create_box(spec["name"] + "_SIDE_B", [dx, wall, dz], collection, 0.015),
    ]
    parts[2].location.y = dy - wall
    return join_components(spec["name"], parts, collection)


def create_building_shell(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    wall = 0.28
    slab = 0.22
    foundation = 0.8
    parts = [
        create_box(spec["name"] + "_WALL_S", [dx, wall, dz + foundation], collection, 0.05),
        create_box(spec["name"] + "_WALL_N", [dx, wall, dz + foundation], collection, 0.05),
        create_box(spec["name"] + "_WALL_W", [wall, dy, dz + foundation], collection, 0.05),
        create_box(spec["name"] + "_WALL_E", [wall, dy, dz + foundation], collection, 0.05),
        create_box(spec["name"] + "_SLAB_G", [dx, dy, slab], collection, 0.025),
        create_box(spec["name"] + "_SLAB_R", [dx, dy, slab], collection, 0.025),
    ]
    parts[0].location.z = -foundation
    parts[1].location.y = dy - wall
    parts[1].location.z = -foundation
    parts[2].location.z = -foundation
    parts[3].location.x = dx - wall
    parts[3].location.z = -foundation
    parts[4].location.z = -foundation
    parts[5].location.z = dz - slab
    floors = max(1, round((dz - 1.2) / 3.0))
    for floor in range(1, floors):
        level = create_box(
            f"{spec['name']}_SLAB_{floor:02d}", [dx, dy, slab], collection, 0.02
        )
        level.location.z = floor * 3.0
        parts.append(level)
    return join_components(spec["name"], parts, collection)


def create_roof(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    if spec["kind"] == "roof_variant":
        parts = [
            create_box(spec["name"] + "_BASE", [dx, dy, 0.25], collection, 0.03),
            create_box(spec["name"] + "_SCREEN_S", [dx, 0.12, dz], collection, 0.02),
            create_box(spec["name"] + "_SCREEN_N", [dx, 0.12, dz], collection, 0.02),
        ]
        parts[2].location.y = dy - 0.12
        return join_components(spec["name"], parts, collection)
    parts = [create_box(spec["name"] + "_SLAB", [dx, dy, 0.25], collection, 0.03)]
    parapet = 0.25
    for suffix, dims, location in (
        ("S", [dx, parapet, dz], (0.0, 0.0, 0.0)),
        ("N", [dx, parapet, dz], (0.0, dy - parapet, 0.0)),
        ("W", [parapet, dy, dz], (0.0, 0.0, 0.0)),
        ("E", [parapet, dy, dz], (dx - parapet, 0.0, 0.0)),
    ):
        part = create_box(spec["name"] + "_" + suffix, dims, collection, 0.02)
        part.location = location
        parts.append(part)
    return join_components(spec["name"], parts, collection)


def create_window_variant(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    frame = 0.12
    sill = 0.15
    parts = [
        create_box(spec["name"] + "_LEFT", [frame, dy, dz], collection, 0.015),
        create_box(spec["name"] + "_RIGHT", [frame, dy, dz], collection, 0.015),
        create_box(spec["name"] + "_HEAD", [dx, dy, frame], collection, 0.015),
        create_box(spec["name"] + "_SILL", [dx, dy + 0.08, sill], collection, 0.015),
        create_box(
            spec["name"] + "_GLAZING",
            [max(frame, dx - 2 * frame), max(0.03, dy * 0.2), max(frame, dz - frame - sill)],
            collection,
            0.0,
        ),
    ]
    parts[1].location.x = dx - frame
    parts[2].location.z = dz - frame
    parts[4].location.x = frame
    parts[4].location.y = dy * 0.4
    parts[4].location.z = sill
    if spec["kind"] == "window_variant" and spec["name"].endswith("_B"):
        mullion = create_box(
            spec["name"] + "_MULLION", [frame, dy, dz - sill], collection, 0.012
        )
        mullion.location.x = dx * 0.5 - frame * 0.5
        mullion.location.z = sill
        parts.append(mullion)
    return join_components(spec["name"], parts, collection)


def create_balcony_variant(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    dx, dy, dz = map(float, spec["dimensions_m"])
    rail = 0.06
    parts = [
        create_box(spec["name"] + "_SLAB", [dx, dy, 0.18], collection, 0.025),
        create_box(spec["name"] + "_RAIL_FRONT", [dx, rail, dz], collection, 0.012),
        create_box(spec["name"] + "_RAIL_L", [rail, dy, dz], collection, 0.012),
        create_box(spec["name"] + "_RAIL_R", [rail, dy, dz], collection, 0.012),
    ]
    parts[1].location.y = dy - rail
    parts[2].location.z = 0.18
    parts[3].location.x = dx - rail
    parts[3].location.z = 0.18
    for index in range(1, 5):
        upright = create_box(
            f"{spec['name']}_UPRIGHT_{index:02d}", [rail, rail, dz], collection, 0.01
        )
        upright.location.x = dx * index / 5.0
        upright.location.y = dy - rail
        upright.location.z = 0.18
        parts.append(upright)
    return join_components(spec["name"], parts, collection)


def create_generic_asset(spec: dict, collection: bpy.types.Collection) -> bpy.types.Object:
    kind = spec["kind"]
    if kind in {"seawall_corner", "road_junction", "curb_corner", "sidewalk_corner",
                "facade_corner"}:
        return create_l_shape(spec, collection)
    if kind in {"curb_ramp", "sidewalk_ramp"}:
        return create_ramp(spec, collection)
    if kind == "drain_channel":
        return create_drain_channel(spec, collection)
    return create_box(spec["name"], spec["dimensions_m"], collection, 0.025)


def create_asset(spec: dict, collection: bpy.types.Collection,
                 materials: dict[int, bpy.types.Material], terrain_index: int
                 ) -> bpy.types.Object:
    kind = spec["kind"]
    if kind in {"terrain", "terrain_transition"}:
        obj = create_solid_terrain(spec, collection, 0.7 if terrain_index % 2 else 0.35)
    elif kind == "road_crowned":
        obj = create_crowned_road(spec, collection)
    elif kind.startswith("building_"):
        obj = create_building_shell(spec, collection)
    elif kind in {"roof", "roof_variant"}:
        obj = create_roof(spec, collection)
    elif kind == "window_variant":
        obj = create_window_variant(spec, collection)
    elif kind == "balcony_variant":
        obj = create_balcony_variant(spec, collection)
    else:
        obj = create_generic_asset(spec, collection)
    assign_materials(obj, spec["materials"], materials)
    ensure_uv0_uv1(obj, spec["dimensions_m"])
    apply_asset_metadata(obj, spec)
    return obj


def create_snap_sockets(obj: bpy.types.Object, spec: dict,
                        collection: bpy.types.Collection) -> list[bpy.types.Object]:
    dx, dy, _ = map(float, spec["dimensions_m"])
    positions = {
        "W": (0.0, dy * 0.5, 0.0),
        "E": (dx, dy * 0.5, 0.0),
        "S": (dx * 0.5, 0.0, 0.0),
        "N": (dx * 0.5, dy, 0.0),
    }
    sockets = []
    short = spec["name"].replace("GEO_COAST001_", "")
    for direction in spec["snap_sockets"]:
        empty = bpy.data.objects.new(f"SOCKET_COAST001_{short}_{direction}", None)
        empty.empty_display_type = "ARROWS"
        empty.empty_display_size = 0.45
        collection.objects.link(empty)
        empty.parent = obj
        empty.location = positions[direction]
        empty["sg_owner_asset"] = spec["name"]
        empty["sg_snap_direction"] = direction
        empty["sg_snap_grid_m"] = min(
            value for value in (1.0, 2.0, 10.0, 20.0, 100.0)
            if max(dx, dy) <= value or value == 100.0
        )
        sockets.append(empty)
    return sockets


def validate_source_scene(contract: dict, assets: list[bpy.types.Object]) -> None:
    required = {spec["name"] for spec in contract["asset_specs"]}
    actual = {obj.name for obj in assets}
    if actual != required:
        raise RuntimeError(f"Asset set mismatch missing={sorted(required-actual)}")
    forbidden = tuple(token.lower() for token in contract["forbidden_name_tokens"])
    for obj in assets:
        if any(token in obj.name.lower() for token in forbidden):
            raise RuntimeError("Forbidden asset name token: " + obj.name)
        layers = {layer.name for layer in obj.data.uv_layers}
        if layers != {"UV0", "UV1"}:
            raise RuntimeError("UV0/UV1 contract failed: " + obj.name)
        if obj.get("sg_external_geometry_imported") is not False:
            raise RuntimeError("External geometry lineage detected: " + obj.name)
    terrains = [obj for obj in assets if obj.get("sg_kind") in {
        "terrain", "terrain_transition"
    }]
    for obj in terrains:
        dimensions = json.loads(obj["sg_dimensions_m"])
        if dimensions[0] != 100.0 or min(vertex.co.z for vertex in obj.data.vertices) > -2.0:
            raise RuntimeError("Terrain length/thickness contract failed: " + obj.name)


def arrange_review_catalog(assets: list[bpy.types.Object]) -> None:
    for index, obj in enumerate(assets):
        column = index % 6
        row = index // 6
        obj.location.x = column * 125.0
        obj.location.y = row * 95.0


def export_individual_assets(assets: list[bpy.types.Object]) -> list[dict]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for obj in assets:
        original_location = obj.location.copy()
        obj.location = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        for child in obj.children:
            child.select_set(True)
        bpy.context.view_layer.objects.active = obj
        path = EXPORT_DIR / f"{obj.name}.glb"
        bpy.ops.export_scene.gltf(
            filepath=str(path),
            export_format="GLB",
            use_selection=True,
            export_apply=True,
            export_yup=True,
        )
        obj.location = original_location
        records.append(
            {
                "name": obj.name,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "dimensions_m": json.loads(obj["sg_dimensions_m"]),
                "uv_layers": [layer.name for layer in obj.data.uv_layers],
                "material_ids": json.loads(obj["sg_material_ids"]),
                "collision": obj["sg_collision_strategy"],
                "snap_sockets": json.loads(obj["sg_snap_sockets"]),
                "nanite": bool(obj["sg_nanite_intent"]),
                "lod_intent": obj["sg_lod_intent"],
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
            }
        )
    return records


def save_and_export(contract: dict, assets: list[bpy.types.Object]) -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    arrange_review_catalog(assets)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    return export_individual_assets(assets)


def write_manifest(contract: dict, asset_records: list[dict]) -> None:
    manifest = {
        "schema": "skyguard.bld-m01-coast-prod-001.artifact-manifest.v1",
        "build_id": BUILD_ID,
        "quality_claim": "production_direction_candidate_not_aaa",
        "blender_version": ".".join(map(str, bpy.app.version)),
        "contract": {
            "path": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(CONTRACT_PATH),
        },
        "generator": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "rejection_evidence": {
            "path": contract["rejection_evidence"]["path"],
            "sha256": contract["rejection_evidence"]["sha256"],
            "use": "visual_rejection_evidence_only_no_geometry_input",
        },
        "source_policy": contract["source_policy"],
        "blend": {
            "path": str(BLEND_PATH.relative_to(ROOT)).replace("\\", "/"),
            "bytes": BLEND_PATH.stat().st_size,
            "sha256": sha256_file(BLEND_PATH),
        },
        "asset_count": len(asset_records),
        "assets": asset_records,
        "promotion": "requires_offline_artifact_audit_manual_visual_review_seam_test_and_unreal_validation",
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    contract = load_contract()
    require_blender_52()
    verify_rejection_evidence(contract)
    collection = reset_factory_scene()
    materials = build_materials(contract)
    assets = []
    terrain_index = 0
    for spec in contract["asset_specs"]:
        obj = create_asset(spec, collection, materials, terrain_index)
        create_snap_sockets(obj, spec, collection)
        assets.append(obj)
        if spec["kind"] in {"terrain", "terrain_transition"}:
            terrain_index += 1
    validate_source_scene(contract, assets)
    records = save_and_export(contract, assets)
    write_manifest(contract, records)
    print(
        json.dumps(
            {
                "build_id": BUILD_ID,
                "asset_count": len(assets),
                "status": "SOURCE_ARTIFACTS_GENERATED_PENDING_AUDIT",
                "manifest": str(MANIFEST_PATH),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
