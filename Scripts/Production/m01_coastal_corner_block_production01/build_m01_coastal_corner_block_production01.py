"""Build one fresh Mission 1 coastal corner-block production candidate.

The building shell, roofline, entrances, balconies, frontage and rooftop detail
are new geometry.  The accepted Recovery06 prewar window module is appended
from its frozen Blender handoff and used as a governed facade dependency.  No
failed whole-building or StageA environment geometry is reused.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import struct
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
BASE_SCRIPT = ROOT / "Scripts/Production/m01_lighthouse_production_refinement01/build_m01_lighthouse_production_refinement01.py"
WINDOW_BLEND = ROOT / "Production/Attempts/m01-hero-prewar-window-bay-a01-recovery06-unrealready01-grok-mcp/attempt_20260811T013000000000Z/output/M01_Hero_Prewar_Window_Bay_A01_Recovery06_UnrealReady01.blend"
TEXTURE_ROOT = ROOT / "Content/Skyguard/Textures/PolyHaven"
ASSET_ID = "m01-coastal-corner-block-production01"
RENDER_MESHES = (
    "SM_M01_CoastalCornerBlock_A_Structural",
    "SM_M01_CoastalCornerBlock_A_Glazing",
    "SM_M01_CoastalCornerBlock_A_Interior",
    "SM_M01_CoastalCornerBlock_A_Details",
)
COLLISIONS = (
    "UCX_SM_M01_CoastalCornerBlock_A_Structural_00",
    "UCX_SM_M01_CoastalCornerBlock_A_Structural_01",
    "UCX_SM_M01_CoastalCornerBlock_A_Structural_02",
)
SOCKETS = (
    "SOCKET_M01_CoastalCornerBlock_Origin",
    "SOCKET_M01_CoastalCornerBlock_Entrance",
    "SOCKET_M01_CoastalCornerBlock_Roof",
    "SOCKET_M01_CoastalCornerBlock_DistrictW",
    "SOCKET_M01_CoastalCornerBlock_DistrictE",
)
WINDOW_OBJECTS = (
    "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "SM_M01_PrewarWindowBay_A01_Glass",
    "SM_M01_PrewarWindowBay_A01_Interior",
)


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_lighthouse_asset_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load helper module: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ASSET_ID = ASSET_ID
    return module


base = load_base()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def texture_set(folder: str, base_name: str, normal_name: str, rough_name: str) -> dict[str, Path]:
    return {
        "base": TEXTURE_ROOT / folder / base_name,
        "normal": TEXTURE_ROOT / folder / normal_name,
        "roughness": TEXTURE_ROOT / folder / rough_name,
    }


def make_materials() -> dict[str, bpy.types.Material]:
    plaster = texture_set(
        "blue_plaster_weathered",
        "blue_plaster_weathered-diffuse-2k.jpg",
        "blue_plaster_weathered-nor_gl-2k.jpg",
        "blue_plaster_weathered-rough-2k.jpg",
    )
    warm_plaster = texture_set(
        "painted_plaster_wall",
        "painted_plaster_wall_diff_2k.jpg",
        "painted_plaster_wall_nor_gl_2k.jpg",
        "painted_plaster_wall_rough_2k.jpg",
    )
    brick = texture_set(
        "brick_wall_006",
        "brick_wall_006-diffuse-2k.jpg",
        "brick_wall_006-nor_gl-2k.jpg",
        "brick_wall_006-rough-2k.jpg",
    )
    concrete = texture_set(
        "concrete_wall_006",
        "concrete_wall_006-diffuse-2k.jpg",
        "concrete_wall_006-nor_gl-2k.jpg",
        "concrete_wall_006-rough-2k.jpg",
    )
    roof = texture_set("roof_07", "roof_07_diff_2k.jpg", "roof_07_nor_gl_2k.jpg", "roof_07_rough_2k.jpg")
    metal = texture_set("metal_plate_02", "metal_plate_02_diff_2k.jpg", "metal_plate_02_nor_gl_2k.jpg", "metal_plate_02_rough_2k.jpg")
    asphalt = texture_set("asphalt_02", "asphalt_02_diff_2k.jpg", "asphalt_02_nor_gl_2k.jpg", "asphalt_02_rough_2k.jpg")
    return {
        "plaster_blue": base.material_pbr("M_M01_CornerBlock_BluePlaster", (0.55, 0.67, 0.72, 1), 0.0, 0.72, 8.0, 0.08, texture_set=plaster, texture_scale=5.0),
        "plaster_warm": base.material_pbr("M_M01_CornerBlock_WarmPlaster", (0.82, 0.72, 0.58, 1), 0.0, 0.70, 7.0, 0.07, texture_set=warm_plaster, texture_scale=5.2),
        "brick": base.material_pbr("M_M01_CornerBlock_WeatheredBrick", (0.68, 0.45, 0.34, 1), 0.0, 0.78, 7.0, 0.06, texture_set=brick, texture_scale=4.5),
        "stone": base.material_pbr("M_M01_CornerBlock_StoneTrim", (0.66, 0.65, 0.60, 1), 0.0, 0.82, 9.0, 0.08, texture_set=concrete, texture_scale=3.2),
        "roof": base.material_pbr("M_M01_CornerBlock_MansardRoof", (0.20, 0.26, 0.30, 1), 0.18, 0.54, 8.0, 0.07, texture_set=roof, texture_scale=5.0),
        "metal": base.material_pbr("M_M01_CornerBlock_PaintedMetal", (0.08, 0.11, 0.13, 1), 0.72, 0.34, 12.0, 0.05, texture_set=metal, texture_scale=4.0),
        "glass": base.material_pbr("M_M01_CornerBlock_StorefrontGlass", (0.035, 0.11, 0.15, 1), 0.0, 0.11, alpha=0.36, transmission=0.60),
        "interior": base.material_pbr("M_M01_CornerBlock_InteriorBacking", (0.12, 0.08, 0.055, 1), 0.0, 0.74),
        "door": base.material_pbr("M_M01_CornerBlock_EntranceDoor", (0.08, 0.11, 0.13, 1), 0.46, 0.42, 14.0, 0.08),
        "concrete": base.material_pbr("M_M01_CornerBlock_ReviewConcrete", (0.11, 0.12, 0.13, 1), 0.0, 0.86, 5.0, 0.12, texture_set=asphalt, texture_scale=4.0),
        "planter": base.material_pbr("M_M01_CornerBlock_Planter", (0.22, 0.24, 0.23, 1), 0.1, 0.68, 8.0, 0.08, texture_set=concrete, texture_scale=4.0),
    }


def add_custom_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    smart_uv: bool = True,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    base.assign(obj, material)
    group.append(obj)
    if smart_uv:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(60.0), island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def add_frustum(
    name: str,
    bottom: tuple[float, float],
    top: tuple[float, float],
    z0: float,
    z1: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
) -> bpy.types.Object:
    bx, by = bottom[0] * 0.5, bottom[1] * 0.5
    tx, ty = top[0] * 0.5, top[1] * 0.5
    vertices = [
        (-bx, -by, z0), (bx, -by, z0), (bx, by, z0), (-bx, by, z0),
        (-tx, -ty, z1), (tx, -ty, z1), (tx, ty, z1), (-tx, ty, z1),
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return add_custom_mesh(name, vertices, faces, material, group)


def add_gable_roof(
    name: str,
    center: tuple[float, float, float],
    width: float,
    depth: float,
    eave_z: float,
    ridge_z: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
) -> bpy.types.Object:
    cx, cy, _ = center
    half_w, half_d = width * 0.5, depth * 0.5
    vertices = [
        (cx - half_w, cy - half_d, eave_z), (cx + half_w, cy - half_d, eave_z),
        (cx - half_w, cy + half_d, eave_z), (cx + half_w, cy + half_d, eave_z),
        (cx, cy - half_d, ridge_z), (cx, cy + half_d, ridge_z),
    ]
    faces = [(0, 1, 4), (3, 2, 5), (0, 4, 5, 2), (1, 3, 5, 4), (0, 2, 3, 1)]
    return add_custom_mesh(name, vertices, faces, material, group)


def append_window_sources() -> dict[str, bpy.types.Object]:
    require(WINDOW_BLEND.is_file(), f"Accepted window source missing: {WINDOW_BLEND}")
    with bpy.data.libraries.load(str(WINDOW_BLEND), link=False) as (source, target):
        missing = [name for name in WINDOW_OBJECTS if name not in source.objects]
        require(not missing, f"Accepted window objects missing: {missing}")
        target.objects = list(WINDOW_OBJECTS)
    appended: dict[str, bpy.types.Object] = {}
    for obj in target.objects:
        require(obj is not None, "Window append returned null object")
        bpy.context.scene.collection.objects.link(obj)
        appended[obj.name] = obj
        obj.hide_render = True
        obj.hide_set(True)
    require(set(appended) == set(WINDOW_OBJECTS), "Window append identity mismatch")
    return appended


def duplicate_window_group(
    sources: dict[str, bpy.types.Object],
    prefix: str,
    location: tuple[float, float, float],
    yaw: float,
    structural: list[bpy.types.Object],
    glazing: list[bpy.types.Object],
    interior: list[bpy.types.Object],
) -> None:
    targets = {
        WINDOW_OBJECTS[0]: structural,
        WINDOW_OBJECTS[1]: glazing,
        WINDOW_OBJECTS[2]: interior,
    }
    for source_name, target_group in targets.items():
        source = sources[source_name]
        obj = source.copy()
        obj.data = source.data.copy()
        obj.name = f"{prefix}_{source_name.rsplit('_', 1)[-1]}"
        bpy.context.scene.collection.objects.link(obj)
        obj.hide_render = False
        obj.hide_set(False)
        obj.location = location
        obj.rotation_euler = (0.0, 0.0, yaw)
        target_group.append(obj)


def join_preserve(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    meshes = [obj for obj in objects if obj is not None and obj.type == "MESH"]
    require(meshes, f"No mesh objects for {name}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.hide_render = False
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    result = bpy.context.object
    result.name = name
    base.apply_transform(result)
    result["asset_id"] = ASSET_ID
    result["production_candidate"] = True
    result["failed_whole_building_mesh_reused"] = False
    result["accepted_window_dependency"] = "m01-hero-prewar-window-bay-a01-recovery06-unrealready01-grok-mcp"
    return result


def build_geometry(materials: dict[str, bpy.types.Material]):
    structural: list[bpy.types.Object] = []
    glazing: list[bpy.types.Object] = []
    interior: list[bpy.types.Object] = []
    details: list[bpy.types.Object] = []

    # Main massing: open facade construction rather than a solid box hidden
    # behind windows.  Rear/side walls and floor slabs leave the governed
    # window, entrance and storefront modules optically unobstructed.
    base.add_box("Ground_RearWall", (0, 7.25, 2.05), (27.2, 0.70, 4.1), materials["brick"], structural, bevel_width=0.08)
    base.add_box("Ground_WestWall", (-13.25, 0, 2.05), (0.70, 14.6, 4.1), materials["brick"], structural, bevel_width=0.08)
    base.add_box("Ground_EastWall", (13.25, 0, 2.05), (0.70, 14.6, 4.1), materials["brick"], structural, bevel_width=0.08)
    base.add_box("Ground_FloorSlab", (0, 0, 0.10), (27.2, 15.2, 0.20), materials["stone"], structural, bevel_width=0.04)
    base.add_box("Ground_CeilingSlab", (0, 0, 4.00), (27.2, 15.2, 0.22), materials["stone"], structural, bevel_width=0.04)
    for pier_index, (x, width) in enumerate(((-11.45, 3.5), (-2.70, 3.4), (2.75, 3.5), (11.65, 3.9)), 1):
        base.add_box(f"Ground_FrontPier_{pier_index:02d}", (x, -7.25, 2.05), (width, 0.70, 4.1), materials["brick"], structural, bevel_width=0.07)

    base.add_box("Upper_RearWall_Warm", (-4.0, 7.00, 10.4), (19.2, 0.60, 12.6), materials["plaster_warm"], structural, bevel_width=0.07)
    base.add_box("Upper_RearWall_Blue", (9.2, 6.85, 10.4), (7.2, 0.60, 12.6), materials["plaster_blue"], structural, bevel_width=0.07)
    base.add_box("Upper_WestWall", (-13.25, 0, 10.4), (0.70, 14.6, 12.6), materials["plaster_warm"], structural, bevel_width=0.08)
    base.add_box("Upper_EastWall", (13.25, -0.2, 10.4), (0.70, 14.2, 12.6), materials["plaster_blue"], structural, bevel_width=0.08)
    for floor_index, z in enumerate((4.12, 8.30, 12.50, 16.55), 1):
        base.add_box(f"Upper_FloorSlab_{floor_index:02d}", (0, 0, z), (27.2, 14.6, 0.22), materials["stone"], structural, bevel_width=0.04)
    for infill_index, (x, width, material_key) in enumerate(((-12.0, 2.0, "plaster_warm"), (-6.1, 2.1, "plaster_warm"), (0.25, 2.0, "plaster_warm"), (6.35, 1.8, "plaster_blue"), (11.5, 2.2, "plaster_blue")), 1):
        base.add_box(f"Upper_FrontInfill_{infill_index:02d}", (x, -7.25, 10.35), (width, 0.62, 12.4), materials[material_key], structural, bevel_width=0.06)
    base.add_box("Shell_RearStairCore", (-10.8, 4.3, 10.0), (4.5, 6.0, 11.8), materials["brick"], structural, bevel_width=0.08)

    add_frustum("Roof_Mansard_Main", (27.8, 15.8), (21.4, 10.4), 16.65, 20.15, materials["roof"], structural)
    base.add_box("Roof_Deck", (0, 0, 20.2), (21.5, 10.5, 0.32), materials["metal"], structural, bevel_width=0.06)
    base.add_cylinder("Roof_CornerPavilion", (9.2, -1.0, 20.3), 2.55, 3.2, materials["plaster_blue"], structural, vertices=12, bevel_width=0.05)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=3.05, radius2=0.25, depth=3.1, location=(9.2, -1.0, 23.45))
    pavilion_roof = bpy.context.object
    pavilion_roof.name = "Roof_CornerPavilion_Cap"
    base.assign(pavilion_roof, materials["roof"])
    structural.append(pavilion_roof)

    # Accepted window module placement, deliberately varied by floor and wing.
    sources = append_window_sources()
    front_rows = [
        (4.15, (-9.2, -3.0, 3.4, 9.3)),
        (8.35, (-9.0, -2.4, 4.2, 9.4)),
        (12.55, (-7.0, 0.2, 7.2)),
    ]
    index = 0
    for z, xs in front_rows:
        for x in xs:
            index += 1
            duplicate_window_group(sources, f"FrontWindow_{index:02d}", (x, -7.55, z), math.pi, structural, glazing, interior)
    side_rows = [(4.15, (-3.2, 3.2)), (8.35, (-2.2, 3.7)), (12.55, (1.4,))]
    for z, ys in side_rows:
        for y in ys:
            index += 1
            duplicate_window_group(sources, f"SideWindow_{index:02d}", (13.55, y, z), -math.pi * 0.5, structural, glazing, interior)
    for obj in sources.values():
        bpy.data.objects.remove(obj, do_unlink=True)

    # Deep ground-floor frontage with an arched entrance and two storefronts.
    base.add_box("Entrance_Recess", (0.0, -7.78, 2.0), (3.1, 0.42, 3.7), materials["interior"], details, bevel_width=0.05)
    base.add_box("Entrance_Door", (0.0, -8.02, 1.78), (1.55, 0.14, 3.15), materials["door"], details, bevel_width=0.04)
    for x in (-0.82, 0.82):
        base.add_box(f"Entrance_Jamb_{x:+.2f}", (x, -8.08, 1.95), (0.18, 0.32, 3.75), materials["stone"], details, bevel_width=0.03)
    base.add_box("Entrance_Lintel", (0, -8.08, 3.76), (2.0, 0.34, 0.28), materials["stone"], details, bevel_width=0.04)
    base.add_box("Entrance_Canopy", (0, -8.7, 3.45), (3.4, 1.8, 0.18), materials["metal"], details, bevel_width=0.05)
    for x in (-1.38, 1.38):
        base.cylinder_between(f"CanopyTie_{x:+.2f}", Vector((x, -8.45, 3.45)), Vector((x, -7.65, 4.25)), 0.035, materials["metal"], details, vertices=12)

    for shop_index, x in enumerate((-7.0, 7.1), 1):
        base.add_box(f"Storefront{shop_index}_Recess", (x, -7.82, 2.05), (5.2, 0.35, 3.55), materials["interior"], interior, bevel_width=0.03)
        base.add_box(f"Storefront{shop_index}_Glass", (x, -8.04, 2.1), (4.75, 0.08, 3.2), materials["glass"], glazing, bevel_width=0.02)
        for mullion_x in (-1.55, 0.0, 1.55):
            base.add_box(f"Storefront{shop_index}_Mullion_{mullion_x:+.2f}", (x + mullion_x, -8.12, 2.1), (0.09, 0.11, 3.25), materials["metal"], details, bevel_width=0.015)
        base.add_box(f"Storefront{shop_index}_Transom", (x, -8.12, 3.12), (4.8, 0.11, 0.09), materials["metal"], details, bevel_width=0.015)
        base.add_box(f"Storefront{shop_index}_InteriorFloor", (x, -4.7, 0.16), (5.0, 5.8, 0.16), materials["interior"], interior, bevel_width=0.02)
        base.add_box(f"Storefront{shop_index}_InteriorBack", (x, -2.0, 2.0), (5.0, 0.18, 3.65), materials["interior"], interior, bevel_width=0.02)
        for shelf in (-1.2, 0.0, 1.2):
            base.add_box(f"Storefront{shop_index}_Shelf_{shelf:+.1f}", (x + shelf, -2.25, 1.55), (0.82, 0.55, 2.45), materials["door"], interior, bevel_width=0.04)

    # Cornices, pilasters and asymmetric balcony rhythm break the repeated grid.
    for z, depth in ((4.12, 0.36), (8.30, 0.30), (12.50, 0.30), (16.55, 0.48)):
        base.add_box(f"Front_Cornice_{z:.2f}", (0, -7.74, z), (27.8, depth, 0.24 if z < 16 else 0.34), materials["stone"], details, bevel_width=0.04)
    for x in (-13.35, -4.85, 5.65, 12.9):
        base.add_box(f"Front_Pilaster_{x:+.2f}", (x, -7.69, 10.25), (0.42, 0.42, 12.8), materials["stone"], details, bevel_width=0.035)

    for balcony_index, (x, z, width) in enumerate(((-9.0, 7.0, 4.2), (3.8, 11.2, 4.5), (8.8, 7.0, 4.0), (-2.4, 15.35, 5.0)), 1):
        base.add_box(f"Balcony{balcony_index}_Slab", (x, -8.12, z - 1.45), (width, 1.25, 0.18), materials["stone"], details, bevel_width=0.04)
        rail_z = z - 0.82
        for rail_x in (x - width * 0.45, x, x + width * 0.45):
            base.cylinder_between(f"Balcony{balcony_index}_Post_{rail_x:+.2f}", Vector((rail_x, -8.68, z - 1.34)), Vector((rail_x, -8.68, rail_z + 0.65)), 0.035, materials["metal"], details, vertices=10)
        base.cylinder_between(f"Balcony{balcony_index}_TopRail", Vector((x - width * 0.48, -8.68, rail_z + 0.65)), Vector((x + width * 0.48, -8.68, rail_z + 0.65)), 0.045, materials["metal"], details, vertices=12)
        for step in range(1, 7):
            rx = x - width * 0.48 + width * step / 7.0
            base.cylinder_between(f"Balcony{balcony_index}_Picket_{step:02d}", Vector((rx, -8.68, z - 1.34)), Vector((rx, -8.68, rail_z + 0.60)), 0.022, materials["metal"], details, vertices=8)

    # Dormers and rooftop utility silhouette.
    for dormer_index, x in enumerate((-7.2, -1.3, 4.7), 1):
        base.add_box(f"Dormer{dormer_index}_Body", (x, -6.55, 19.15), (3.0, 2.25, 2.75), materials["plaster_warm"], details, bevel_width=0.06)
        add_gable_roof(f"Dormer{dormer_index}_Roof", (x, -6.55, 0), 3.5, 2.75, 20.55, 21.65, materials["roof"], details)
        base.add_box(f"Dormer{dormer_index}_Glass", (x, -7.72, 19.18), (1.45, 0.08, 1.45), materials["glass"], glazing, bevel_width=0.02)
        for dx in (-0.82, 0.82):
            base.add_box(f"Dormer{dormer_index}_Trim_{dx:+.2f}", (x + dx, -7.78, 19.18), (0.16, 0.16, 1.82), materials["stone"], details, bevel_width=0.02)
    for chimney_index, x in enumerate((-8.6, 2.4), 1):
        base.add_box(f"Chimney{chimney_index}", (x, 2.5, 21.55), (1.05, 1.15, 2.8), materials["brick"], details, bevel_width=0.06)
        base.add_box(f"Chimney{chimney_index}_Cap", (x, 2.5, 23.0), (1.28, 1.38, 0.18), materials["stone"], details, bevel_width=0.04)
    base.add_box("Roof_HVAC_Base", (-2.5, 1.2, 20.8), (3.2, 2.1, 1.15), materials["metal"], details, bevel_width=0.12)
    base.add_cylinder("Roof_Vent", (4.7, 2.2, 21.3), 0.38, 2.2, materials["metal"], details, vertices=24, bevel_width=0.04)

    # Grounded frontage elements; vegetation itself remains the accepted Unreal source set.
    for planter_index, x in enumerate((-10.6, -5.1, 5.2, 10.8), 1):
        base.add_box(f"FrontagePlanter{planter_index}", (x, -9.05, 0.48), (3.3, 1.15, 0.92), materials["planter"], details, bevel_width=0.10)
    base.add_box("Corner_AddressPlinth", (12.7, -8.25, 1.2), (0.95, 0.55, 2.25), materials["stone"], details, bevel_width=0.07)

    render_meshes = [
        join_preserve(structural, RENDER_MESHES[0]),
        join_preserve(glazing, RENDER_MESHES[1]),
        join_preserve(interior, RENDER_MESHES[2]),
        join_preserve(details, RENDER_MESHES[3]),
    ]
    return render_meshes, {"accepted_window_instances": index, "front_window_instances": sum(len(xs) for _, xs in front_rows), "side_window_instances": sum(len(ys) for _, ys in side_rows)}


def create_collision_and_sockets(materials: dict[str, bpy.types.Material]):
    collisions: list[bpy.types.Object] = []
    sockets: list[bpy.types.Object] = []
    base.add_box(COLLISIONS[0], (0, 0, 8.3), (27.2, 15.2, 16.6), materials["concrete"], collisions, bevel_width=0.0)
    base.add_box(COLLISIONS[1], (0, 0, 18.4), (21.4, 10.4, 3.6), materials["concrete"], collisions, bevel_width=0.0)
    base.add_box(COLLISIONS[2], (9.2, -1.0, 22.0), (5.3, 5.3, 6.3), materials["concrete"], collisions, bevel_width=0.0)
    for obj in collisions:
        obj.display_type = "WIRE"
        obj.hide_render = True
        obj["collision_role"] = "UCX"
    for name, location in (
        (SOCKETS[0], (0.0, 0.0, 0.0)),
        (SOCKETS[1], (0.0, -8.25, 0.0)),
        (SOCKETS[2], (0.0, 0.0, 20.25)),
        (SOCKETS[3], (-13.6, 0.0, 0.0)),
        (SOCKETS[4], (13.6, 0.0, 0.0)),
    ):
        obj = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.45
        obj["socket_role"] = name
        sockets.append(obj)
    return collisions, sockets


def glb_inventory(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        magic, version, total_length = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2, "Invalid GLB header")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "GLB JSON chunk missing")
        payload = json.loads(stream.read(chunk_length).decode("utf-8").rstrip("\x00 \t\r\n"))
    require(total_length == path.stat().st_size, "GLB byte declaration mismatch")
    return {
        "nodes": [node.get("name") for node in payload.get("nodes", [])],
        "mesh_count": len(payload.get("meshes", [])),
        "material_count": len(payload.get("materials", [])),
        "image_count": len(payload.get("images", [])),
    }


def export_glb(path: Path, render_meshes, collisions, sockets) -> dict[str, object]:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [*render_meshes, *collisions, *sockets]:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = render_meshes[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    require(path.is_file(), "GLB missing")
    result = glb_inventory(path)
    for name in (*RENDER_MESHES, *COLLISIONS, *SOCKETS):
        require(name in result["nodes"], f"GLB missing node: {name}")
    return result


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def render_view(output: Path, filename: str, location, target, lens: float, mode: str, materials) -> dict[str, object]:
    result = base.render_view(output, filename, location, target, lens, mode, materials)
    require(png_dimensions(output / filename) == (2048, 1152), f"Render dimensions changed: {filename}")
    return result


def main() -> int:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args(values)
    output = Path(args.output)
    contract_path = Path(args.contract)
    renders = output / "renders"
    exports = output / "exports"
    receipts = output / "receipts"
    for directory in (renders, exports, receipts):
        directory.mkdir(parents=True, exist_ok=False)
    blend_path = output / "M01_CoastalCornerBlock_Production01.blend"
    glb_path = exports / "M01_CoastalCornerBlock_Production01.glb"
    receipt_path = receipts / "production_receipt.json"
    report: dict[str, object] = {
        "schema": "skyguard.m01-coastal-corner-block-production01.receipt.v1",
        "created_at_utc": utc_now(),
        "classification": "FAILED_WITH_EVIDENCE",
        "asset_id": ASSET_ID,
        "error": None,
        "traceback": None,
        "render_count": 0,
    }
    exit_code = 3
    try:
        require(args.asset_id == ASSET_ID, f"Asset identity mismatch: {args.asset_id}")
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_CORNER_BLOCK_PRODUCTION01_BLENDER_EXECUTION", "Contract classification changed")
        for entry in contract["authorities"]:
            path = Path(str(entry["path"]))
            require(path.is_file(), f"Authority missing: {path}")
            require(path.stat().st_size == int(entry["bytes"]), f"Authority byte mismatch: {path}")
            require(sha256(path) == str(entry["sha256"]), f"Authority hash mismatch: {path}")

        base.clear_scene()
        materials = make_materials()
        render_meshes, dependency_record = build_geometry(materials)
        collisions, sockets = create_collision_and_sockets(materials)
        for obj in render_meshes:
            base.move_to_collection(obj, "PRODUCTION_RENDER")
        for obj in collisions:
            base.move_to_collection(obj, "PRODUCTION_COLLISION")
        for obj in sockets:
            base.move_to_collection(obj, "PRODUCTION_SOCKETS")

        minimum, maximum = base.bounds(render_meshes)
        size = maximum - minimum
        require(26.0 <= size.x <= 30.5, f"Width outside contract: {size.x}")
        require(14.0 <= size.y <= 19.5, f"Depth outside contract: {size.y}")
        require(23.0 <= size.z <= 26.5, f"Height outside contract: {size.z}")
        require(-0.08 <= minimum.z <= 0.08, f"Asset not grounded: {minimum.z}")
        vertices = sum(len(obj.data.vertices) for obj in render_meshes)
        polygons = sum(len(obj.data.polygons) for obj in render_meshes)
        triangles = 0
        for obj in render_meshes:
            obj.data.calc_loop_triangles()
            triangles += len(obj.data.loop_triangles)
            require(len(obj.data.uv_layers) > 0, f"UV missing: {obj.name}")
        require(vertices >= 150000, f"Accepted-window detail dependency absent: {vertices} vertices")
        require(triangles >= 250000, f"Insufficient authored detail: {triangles} triangles")

        scene = bpy.context.scene
        base.set_supported(scene.render, "engine", ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"))
        scene.render.resolution_x = 2048
        scene.render.resolution_y = 1152
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.image_settings.color_depth = "8"
        scene.render.image_settings.compression = 15
        scene.render.film_transparent = False
        for obj in collisions:
            obj.hide_render = True

        views = [
            ("01_daylight_front_full.png", (0, -61, 13), (0, 0, 10.8), 52.0, "daylight"),
            ("02_daylight_corner_oblique.png", (42, -51, 16), (1.5, 0, 10.5), 54.0, "daylight"),
            ("03_overcast_west_oblique.png", (-42, -49, 15), (-1.5, 0, 10.5), 54.0, "overcast"),
            ("04_wet_street_level.png", (28, -42, 5.0), (2.0, -1.0, 8.5), 48.0, "wet"),
            ("05_night_frontage.png", (-25, -43, 7.5), (0.0, -1.5, 8.5), 50.0, "night"),
            ("06_cockpit_height_context.png", (48, -82, 25), (1.0, 0.0, 10.0), 62.0, "cockpit"),
            ("07_facade_window_balcony_detail.png", (-7.5, -22, 10.0), (-6.5, -7.4, 9.5), 68.0, "daylight"),
            ("08_entrance_storefront_detail.png", (7.0, -21, 4.2), (2.0, -7.7, 2.4), 64.0, "overcast"),
            ("09_mansard_roofline_detail.png", (25, -31, 24.0), (2.0, 0.0, 20.0), 66.0, "daylight"),
            ("10_east_side_facade.png", (47, -8, 13.0), (8.0, 0.0, 10.0), 56.0, "overcast"),
            ("11_wet_balcony_and_cornice.png", (-20, -28, 13.0), (-3.0, -7.2, 11.0), 68.0, "wet"),
            ("12_night_corner_pavilion.png", (34, -36, 20.0), (6.0, -1.0, 17.0), 65.0, "night"),
        ]
        render_rows = [render_view(renders, *view, materials) for view in views]
        require(len(render_rows) == 12, "Render count mismatch")

        base.clear_review()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        require(blend_path.is_file(), "Blend missing")
        glb = export_glb(glb_path, render_meshes, collisions, sockets)
        report.update(
            {
                "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
                "identity": "Project-authored asymmetric Ukrainian coastal corner block",
                "dimensions_m": [float(size.x), float(size.y), float(size.z)],
                "bounds_min_m": [float(value) for value in minimum],
                "bounds_max_m": [float(value) for value in maximum],
                "vertices": vertices,
                "polygons": polygons,
                "triangles": triangles,
                "render_meshes": list(RENDER_MESHES),
                "collision_meshes": list(COLLISIONS),
                "sockets": list(SOCKETS),
                "authored_material_names": sorted(material.name for material in materials.values()),
                "dependency_record": dependency_record,
                "failed_whole_building_mesh_reused": False,
                "uv_complete": True,
                "render_count": len(render_rows),
                "renders": render_rows,
                "blend": record(blend_path),
                "glb": {**record(glb_path), **glb},
                "runtime_promotion_authorized": False,
                "unreal_import_authorized": False,
                "remaining_gate": "Direct full-resolution review, then fresh reversible Stage04 Unreal import and mapped D3D12 proof.",
            }
        )
        exit_code = 0
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(receipt_path, report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
