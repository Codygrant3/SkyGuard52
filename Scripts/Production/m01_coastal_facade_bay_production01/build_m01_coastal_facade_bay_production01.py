"""Build one reference-driven Mission 1 coastal facade bay.

This is a fresh modular facade shell around the accepted Recovery06 window
dependency.  It deliberately proves one bay, one balcony and one material
language before any whole-building duplication.  Failed corner-block geometry
is never opened, appended or reused.
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
ASSET_ID = "m01-coastal-facade-bay-production01"
RENDER_MESHES = (
    "SM_M01_CoastalFacadeBay_A_StructureFrame",
    "SM_M01_CoastalFacadeBay_A_Glass",
    "SM_M01_CoastalFacadeBay_A_Interior",
    "SM_M01_CoastalFacadeBay_A_BalconyDetails",
)
COLLISIONS = (
    "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_00",
    "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_01",
    "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_02",
    "UCX_SM_M01_CoastalFacadeBay_A_BalconyDetails_00",
)
SOCKETS = (
    "SOCKET_M01_CoastalFacadeBay_Origin",
    "SOCKET_M01_CoastalFacadeBay_WindowCenter",
    "SOCKET_M01_CoastalFacadeBay_Balcony",
    "SOCKET_M01_CoastalFacadeBay_AttachLeft",
    "SOCKET_M01_CoastalFacadeBay_AttachRight",
)
WINDOW_OBJECTS = (
    "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "SM_M01_PrewarWindowBay_A01_Glass",
    "SM_M01_PrewarWindowBay_A01_Interior",
)


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_facade_asset_base", BASE_SCRIPT)
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
    result = {
        "base": TEXTURE_ROOT / folder / base_name,
        "normal": TEXTURE_ROOT / folder / normal_name,
        "roughness": TEXTURE_ROOT / folder / rough_name,
    }
    for path in result.values():
        require(path.is_file(), f"Texture authority missing: {path}")
    return result


def make_materials() -> dict[str, bpy.types.Material]:
    plaster = texture_set(
        "painted_plaster_wall",
        "painted_plaster_wall_diff_2k.jpg",
        "painted_plaster_wall_nor_gl_2k.jpg",
        "painted_plaster_wall_rough_2k.jpg",
    )
    concrete = texture_set(
        "concrete_wall_006",
        "concrete_wall_006-diffuse-2k.jpg",
        "concrete_wall_006-nor_gl-2k.jpg",
        "concrete_wall_006-rough-2k.jpg",
    )
    metal = texture_set(
        "metal_plate_02",
        "metal_plate_02_diff_2k.jpg",
        "metal_plate_02_nor_gl_2k.jpg",
        "metal_plate_02_rough_2k.jpg",
    )
    asphalt = texture_set(
        "asphalt_02",
        "asphalt_02_diff_2k.jpg",
        "asphalt_02_nor_gl_2k.jpg",
        "asphalt_02_rough_2k.jpg",
    )
    return {
        "plaster": base.material_pbr(
            "M_M01_CoastalFacadeBay_WarmPlaster", (0.72, 0.67, 0.57, 1), 0.0, 0.74,
            8.0, 0.07, texture_set=plaster, texture_scale=4.5,
        ),
        "stone": base.material_pbr(
            "M_M01_CoastalFacadeBay_StoneTrim", (0.52, 0.54, 0.51, 1), 0.0, 0.80,
            9.0, 0.08, texture_set=concrete, texture_scale=3.2,
        ),
        "metal": base.material_pbr(
            "M_M01_CoastalFacadeBay_BlackenedSteel", (0.045, 0.055, 0.060, 1), 0.78, 0.34,
            13.0, 0.045, texture_set=metal, texture_scale=3.0,
        ),
        "bronze": base.material_pbr(
            "M_M01_CoastalFacadeBay_AgedBronze", (0.22, 0.13, 0.065, 1), 0.76, 0.42,
            16.0, 0.04,
        ),
        "review_ground": base.material_pbr(
            "M_M01_CoastalFacadeBay_ReviewGround", (0.10, 0.11, 0.12, 1), 0.0, 0.88,
            5.0, 0.12, texture_set=asphalt, texture_scale=3.5,
        ),
        "collision": base.material_pbr(
            "M_REVIEW_M01_CoastalFacadeBay_Collision", (0.86, 0.08, 0.05, 1), 0.0, 0.7,
        ),
    }


def append_accepted_window() -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object, dict[str, object]]:
    require(WINDOW_BLEND.is_file(), f"Accepted window source missing: {WINDOW_BLEND}")
    with bpy.data.libraries.load(str(WINDOW_BLEND), link=False) as (source, target):
        missing = [name for name in WINDOW_OBJECTS if name not in source.objects]
        require(not missing, f"Accepted window objects missing: {missing}")
        target.objects = list(WINDOW_OBJECTS)
    appended: dict[str, bpy.types.Object] = {}
    for obj in target.objects:
        require(obj is not None, "Accepted window append returned null")
        bpy.context.scene.collection.objects.link(obj)
        obj.hide_render = False
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        appended[obj.name] = obj
    require(set(appended) == set(WINDOW_OBJECTS), "Accepted window identity mismatch")
    frame = appended[WINDOW_OBJECTS[0]]
    glass = appended[WINDOW_OBJECTS[1]]
    interior = appended[WINDOW_OBJECTS[2]]
    frame_min, frame_max = base.bounds([frame])
    glass_min, glass_max = base.bounds([glass])
    interior_min, interior_max = base.bounds([interior])
    axis = {
        "source_front_axis": "-Y",
        "facade_camera_side": "negative_y",
        "applied_yaw_radians": 0.0,
        "frame_min": list(frame_min),
        "frame_max": list(frame_max),
        "glass_min": list(glass_min),
        "glass_max": list(glass_max),
        "interior_min": list(interior_min),
        "interior_max": list(interior_max),
    }
    require(frame_min.y < glass_min.y, "Accepted window exterior depth order changed")
    require(interior_max.y > glass_max.y + 1.0, "Accepted interior does not extend behind glazing")
    require(2.4 <= frame_max.x - frame_min.x <= 3.2, "Accepted window width changed")
    require(3.7 <= frame_max.z - frame_min.z <= 4.3, "Accepted window height changed")
    return frame, glass, interior, axis


def join_preserve(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    meshes = [obj for obj in objects if obj is not None and obj.type == "MESH"]
    require(meshes, f"No mesh objects for {name}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.hide_render = False
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    result = bpy.context.object
    result.name = name
    base.apply_transform(result)
    result["asset_id"] = ASSET_ID
    result["production_candidate"] = True
    result["accepted_window_dependency"] = "m01-hero-prewar-window-bay-a01-recovery06-unrealready01-grok-mcp"
    result["failed_corner_block_geometry_reused"] = False
    return result


def build_geometry(materials: dict[str, bpy.types.Material]):
    structural: list[bpy.types.Object] = []
    glazing: list[bpy.types.Object] = []
    interior_group: list[bpy.types.Object] = []
    details: list[bpy.types.Object] = []

    frame, glass, interior, axis = append_accepted_window()
    structural.append(frame)
    glazing.append(glass)
    interior_group.append(interior)

    # Open construction: only the flanks, plinth and head around the accepted
    # window.  No solid facade slab is hidden behind it.
    base.add_box("Facade_LeftWing", (-2.18, 0.23, 2.15), (1.34, 0.52, 4.30), materials["plaster"], structural, bevel_width=0.035)
    base.add_box("Facade_RightWing", (2.18, 0.23, 2.15), (1.34, 0.52, 4.30), materials["plaster"], structural, bevel_width=0.035)
    base.add_box("Facade_LeftPlinth", (-2.18, -0.01, 0.36), (1.42, 0.18, 0.72), materials["stone"], structural, bevel_width=0.025)
    base.add_box("Facade_RightPlinth", (2.18, -0.01, 0.36), (1.42, 0.18, 0.72), materials["stone"], structural, bevel_width=0.025)
    base.add_box("Facade_HeadBand", (0.0, 0.06, 4.22), (5.74, 0.32, 0.30), materials["stone"], structural, bevel_width=0.035)
    base.add_box("Facade_Cornice", (0.0, -0.04, 4.47), (6.08, 0.56, 0.20), materials["stone"], structural, bevel_width=0.035)
    base.add_box("Facade_LeftPilaster", (-2.86, 0.12, 2.28), (0.18, 0.64, 4.56), materials["stone"], structural, bevel_width=0.025)
    base.add_box("Facade_RightPilaster", (2.86, 0.12, 2.28), (0.18, 0.64, 4.56), materials["stone"], structural, bevel_width=0.025)

    # Restrained attached Juliet balcony.  Every rail physically meets either
    # the platform, the front rail or the facade return.
    base.add_box("Balcony_Platform", (0.0, -0.91, 0.73), (2.46, 1.02, 0.14), materials["stone"], details, bevel_width=0.035)
    front_y = -1.40
    wall_y = -0.40
    rail_bottom = 0.83
    rail_top = 1.74
    for index, x in enumerate((-1.10, -0.82, -0.55, -0.28, 0.0, 0.28, 0.55, 0.82, 1.10), 1):
        base.cylinder_between(
            f"Balcony_FrontBaluster_{index:02d}", Vector((x, front_y, rail_bottom)),
            Vector((x, front_y, rail_top)), 0.025, materials["metal"], details, vertices=12,
        )
    base.cylinder_between("Balcony_FrontTopRail", Vector((-1.24, front_y, rail_top)), Vector((1.24, front_y, rail_top)), 0.045, materials["metal"], details, vertices=16)
    base.cylinder_between("Balcony_FrontMidRail", Vector((-1.20, front_y, 1.26)), Vector((1.20, front_y, 1.26)), 0.025, materials["metal"], details, vertices=12)
    for side, x in (("L", -1.20), ("R", 1.20)):
        base.cylinder_between(f"Balcony_{side}_TopReturn", Vector((x, front_y, rail_top)), Vector((x, wall_y, rail_top)), 0.045, materials["metal"], details, vertices=16)
        for y_index, y in enumerate((-1.15, -0.88, -0.61), 1):
            base.cylinder_between(f"Balcony_{side}_ReturnBaluster_{y_index:02d}", Vector((x, y, rail_bottom)), Vector((x, y, rail_top)), 0.025, materials["metal"], details, vertices=12)
        base.cylinder_between(f"Balcony_{side}_Bracket", Vector((x * 0.82, -0.46, 0.18)), Vector((x, -1.23, 0.67)), 0.055, materials["metal"], details, vertices=16)
    base.add_box("Balcony_PatinaEdge", (0.0, -1.42, 0.72), (2.52, 0.08, 0.18), materials["bronze"], details, bevel_width=0.02)

    # A plaque and narrow drip bands give readable scale without adding a new
    # competing material system.
    base.add_box("Facade_NumberPlaque", (2.30, -0.095, 2.65), (0.30, 0.05, 0.42), materials["bronze"], details, bevel_width=0.025)
    base.add_box("Facade_LeftDripBand", (-2.18, -0.075, 3.28), (1.20, 0.07, 0.11), materials["stone"], details, bevel_width=0.018)
    base.add_box("Facade_RightDripBand", (2.18, -0.075, 1.72), (1.20, 0.07, 0.11), materials["stone"], details, bevel_width=0.018)

    render_meshes = [
        join_preserve(structural, RENDER_MESHES[0]),
        join_preserve(glazing, RENDER_MESHES[1]),
        join_preserve(interior_group, RENDER_MESHES[2]),
        join_preserve(details, RENDER_MESHES[3]),
    ]
    return render_meshes, axis


def create_collision_and_sockets(materials: dict[str, bpy.types.Material]):
    collisions: list[bpy.types.Object] = []
    sockets: list[bpy.types.Object] = []
    base.add_box(COLLISIONS[0], (-2.18, 0.23, 2.15), (1.34, 0.52, 4.30), materials["collision"], collisions, bevel_width=0.0)
    base.add_box(COLLISIONS[1], (2.18, 0.23, 2.15), (1.34, 0.52, 4.30), materials["collision"], collisions, bevel_width=0.0)
    base.add_box(COLLISIONS[2], (0.0, 0.06, 4.22), (5.74, 0.32, 0.30), materials["collision"], collisions, bevel_width=0.0)
    base.add_box(COLLISIONS[3], (0.0, -0.91, 0.73), (2.46, 1.02, 0.14), materials["collision"], collisions, bevel_width=0.0)
    for obj in collisions:
        obj.display_type = "WIRE"
        obj.hide_render = True
        obj["collision_role"] = "UCX"
    socket_data = (
        (SOCKETS[0], (0.0, 0.0, 0.0)),
        (SOCKETS[1], (0.0, 0.0, 2.12)),
        (SOCKETS[2], (0.0, -0.91, 0.73)),
        (SOCKETS[3], (-3.04, 0.0, 0.0)),
        (SOCKETS[4], (3.04, 0.0, 0.0)),
    )
    for name, location in socket_data:
        obj = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.28
        obj["socket_role"] = name
        sockets.append(obj)
    return collisions, sockets


def review_light(name: str, location, energy: float, size: float, color, target=(0.0, 0.0, 2.2)) -> None:
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    base.ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    base.look_at(obj, target)


def review_sun(name: str, rotation, energy: float, color) -> None:
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.5)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    base.ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.rotation_euler = rotation


def review_ground(material: bpy.types.Material, wet: bool) -> None:
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.035))
    obj = bpy.context.object
    obj.name = "REVIEW_Ground"
    base.move_to_collection(obj, "REVIEW_ONLY")
    if wet:
        wet_material = material.copy()
        wet_material.name = "REVIEW_WetGround"
        bsdf = wet_material.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            base.principled_socket(bsdf, "Roughness").default_value = 0.14
        obj.data.materials.append(wet_material)
    else:
        obj.data.materials.append(material)


def stage(mode: str, materials: dict[str, bpy.types.Material]) -> None:
    base.clear_review()
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    require(background is not None, "Background node missing")
    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    base.set_supported(scene.view_settings, "look", ("AgX - Medium High Contrast", "Medium High Contrast", "None"))
    scene.view_settings.exposure = 0.7
    if mode == "night":
        background.inputs["Color"].default_value = (0.008, 0.014, 0.026, 1)
        background.inputs["Strength"].default_value = 0.18
        review_light("REVIEW_Moon", (-8, -12, 12), 1800, 8, (0.30, 0.50, 1.0))
        review_light("REVIEW_WarmInterior", (2.2, 2.0, 2.6), 900, 4, (1.0, 0.42, 0.14), target=(0, 0, 2.0))
        scene.view_settings.exposure = 1.5
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.13, 0.18, 0.25, 1)
        background.inputs["Strength"].default_value = 0.54
        review_light("REVIEW_WetKey", (-8, -12, 12), 2800, 10, (0.54, 0.72, 1.0))
        review_light("REVIEW_WetRim", (7, 4, 8), 1400, 6, (1.0, 0.47, 0.20))
        scene.view_settings.exposure = 0.95
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.34, 0.40, 0.50, 1)
        background.inputs["Strength"].default_value = 0.76
        review_light("REVIEW_CloudKey", (-9, -12, 13), 3200, 11, (0.76, 0.86, 1.0))
        review_light("REVIEW_CloudFill", (8, 4, 9), 1800, 9, (0.64, 0.72, 0.84))
        scene.view_settings.exposure = 0.62
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.10, 0.18, 0.29, 1)
        background.inputs["Strength"].default_value = 0.58
        review_light("REVIEW_HighSky", (-10, -16, 16), 3600, 12, (0.56, 0.74, 1.0))
        review_light("REVIEW_SunBounce", (9, 3, 8), 1600, 7, (1.0, 0.62, 0.32))
        scene.view_settings.exposure = 0.85
    else:
        background.inputs["Color"].default_value = (0.38, 0.55, 0.76, 1)
        background.inputs["Strength"].default_value = 0.82
        review_sun("REVIEW_Sun", (math.radians(31), math.radians(-18), math.radians(-32)), 3.0, (1.0, 0.84, 0.66))
        review_light("REVIEW_Sky", (-8, -12, 13), 2700, 10, (0.58, 0.76, 1.0))
        review_light("REVIEW_Bounce", (8, 4, 7), 1200, 7, (1.0, 0.58, 0.28))
        scene.view_settings.exposure = 0.62
    review_ground(materials["review_ground"], wet=(mode == "wet"))


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def render_view(output: Path, filename: str, location, target, lens: float, mode: str, materials) -> dict[str, object]:
    stage(mode, materials)
    scene = bpy.context.scene
    scene.camera = base.review_camera(location, target, lens)
    path = output / filename
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file(), f"Render missing: {path}")
    width, height = png_dimensions(path)
    require((width, height) == (2048, 1152), f"Wrong render dimensions: {path} {width}x{height}")
    require(path.stat().st_size >= 150000, f"Render is unexpectedly small: {path}")
    # Do not query Blender's transient Render Result here.  Blender 5.2 may
    # release that buffer after a successful background write.  The persisted
    # PNG is the governed evidence.
    return {**record(path), "mode": mode, "width": width, "height": height}


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
        filepath=str(path), export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True, export_extras=True,
        export_materials="EXPORT", export_cameras=False, export_lights=False,
    )
    require(path.is_file(), "GLB missing")
    result = glb_inventory(path)
    for name in (*RENDER_MESHES, *COLLISIONS, *SOCKETS):
        require(name in result["nodes"], f"GLB missing node: {name}")
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
    checkpoints = output / "checkpoints"
    renders = output / "renders"
    exports = output / "exports"
    receipts = output / "receipts"
    for directory in (checkpoints, renders, exports, receipts):
        directory.mkdir(parents=True, exist_ok=False)
    blend_path = output / "M01_CoastalFacadeBay_Production01.blend"
    glb_path = exports / "M01_CoastalFacadeBay_Production01.glb"
    receipt_path = receipts / "production_receipt.json"
    report: dict[str, object] = {
        "schema": "skyguard.m01-coastal-facade-bay-production01.receipt.v1",
        "created_at_utc": utc_now(),
        "classification": "FAILED_WITH_EVIDENCE",
        "asset_id": ASSET_ID,
        "error": None,
        "traceback": None,
        "checkpoint_render_count": 0,
        "final_render_count": 0,
    }
    exit_code = 3
    try:
        require(args.asset_id == ASSET_ID, f"Asset identity mismatch: {args.asset_id}")
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        require(
            contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_FACADE_BAY_PRODUCTION01_BLENDER_EXECUTION",
            "Contract classification changed",
        )
        for entry in contract["authorities"]:
            path = Path(str(entry["path"]))
            require(path.is_file(), f"Authority missing: {path}")
            require(path.stat().st_size == int(entry["bytes"]), f"Authority byte mismatch: {path}")
            require(sha256(path) == str(entry["sha256"]), f"Authority hash mismatch: {path}")

        base.clear_scene()
        materials = make_materials()
        render_meshes, axis_record = build_geometry(materials)
        collisions, sockets = create_collision_and_sockets(materials)
        for obj in render_meshes:
            base.move_to_collection(obj, "PRODUCTION_RENDER")
        for obj in collisions:
            base.move_to_collection(obj, "PRODUCTION_COLLISION")
            obj.hide_render = True
        for obj in sockets:
            base.move_to_collection(obj, "PRODUCTION_SOCKETS")

        minimum, maximum = base.bounds(render_meshes)
        size = maximum - minimum
        require(5.7 <= size.x <= 6.3, f"Width outside contract: {size.x}")
        require(3.7 <= size.y <= 4.6, f"Depth outside contract: {size.y}")
        require(4.4 <= size.z <= 4.7, f"Height outside contract: {size.z}")
        require(-0.06 <= minimum.z <= 0.06, f"Asset not grounded: {minimum.z}")
        vertices = sum(len(obj.data.vertices) for obj in render_meshes)
        polygons = sum(len(obj.data.polygons) for obj in render_meshes)
        triangles = 0
        for obj in render_meshes:
            obj.data.calc_loop_triangles()
            triangles += len(obj.data.loop_triangles)
            require(len(obj.data.uv_layers) > 0, f"UV missing: {obj.name}")
        require(vertices >= 20000, f"Accepted-window detail dependency absent: {vertices}")
        require(triangles >= 25000, f"Insufficient production detail: {triangles}")

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

        checkpoint_views = [
            ("checkpoint_01_axis_front.png", (0.0, -12.5, 2.35), (0.0, 0.15, 2.20), 56.0, "daylight"),
            ("checkpoint_02_left_oblique_depth.png", (-7.4, -10.0, 3.1), (0.0, 0.10, 2.10), 58.0, "overcast"),
            ("checkpoint_03_balcony_attachment.png", (3.2, -7.0, 1.8), (0.0, -0.55, 1.30), 70.0, "daylight"),
        ]
        checkpoint_rows = [render_view(checkpoints, *view, materials) for view in checkpoint_views]
        require(len(checkpoint_rows) == 3, "Checkpoint render count mismatch")
        report["checkpoint_render_count"] = len(checkpoint_rows)

        final_views = [
            ("01_daylight_front_full.png", (0.0, -14.5, 2.5), (0.0, 0.10, 2.20), 55.0, "daylight"),
            ("02_daylight_left_oblique.png", (-8.5, -11.5, 3.4), (0.0, 0.10, 2.15), 58.0, "daylight"),
            ("03_overcast_right_oblique.png", (8.5, -11.0, 3.2), (0.0, 0.10, 2.15), 58.0, "overcast"),
            ("04_wet_street_level.png", (-5.7, -9.4, 1.35), (0.0, -0.30, 1.75), 52.0, "wet"),
            ("05_night_front.png", (0.0, -12.8, 2.25), (0.0, 0.20, 2.10), 56.0, "night"),
            ("06_cockpit_distance_readability.png", (14.0, -27.0, 8.0), (0.0, 0.0, 2.15), 68.0, "cockpit"),
            ("07_plaster_stone_window_detail.png", (-3.8, -7.3, 2.85), (-1.0, -0.05, 2.55), 72.0, "overcast"),
            ("08_balcony_metal_attachment_detail.png", (3.4, -6.7, 1.55), (0.35, -0.65, 1.20), 74.0, "wet"),
        ]
        render_rows = [render_view(renders, *view, materials) for view in final_views]
        require(len(render_rows) == 8, "Final render count mismatch")
        report["final_render_count"] = len(render_rows)

        base.clear_review()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        require(blend_path.is_file(), "Blend missing")
        glb = export_glb(glb_path, render_meshes, collisions, sockets)
        report.update({
            "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
            "identity": "Project-authored modular Ukrainian coastal facade bay with accepted Recovery06 window dependency",
            "accepted_window_instances": 1,
            "axis_validation": axis_record,
            "dimensions_m": [size.x, size.y, size.z],
            "bounds_min_m": list(minimum),
            "bounds_max_m": list(maximum),
            "vertices": vertices,
            "polygons": polygons,
            "triangles": triangles,
            "render_meshes": list(RENDER_MESHES),
            "collision_meshes": list(COLLISIONS),
            "sockets": list(SOCKETS),
            "checkpoint_renders": checkpoint_rows,
            "final_renders": render_rows,
            "blend": record(blend_path),
            "glb": {**record(glb_path), **glb},
            "failed_corner_block_geometry_reused": False,
            "unreal_import_allowed": False,
            "runtime_promotion_allowed": False,
            "error": None,
            "traceback": None,
        })
        exit_code = 0
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        report["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(receipt_path, report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
