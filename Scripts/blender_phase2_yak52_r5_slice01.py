"""Bounded Yak-52 R5 first production-art slice.

Creates a new isolated Blender namespace proving the forward fuselage, radial
cowling, canopy greenhouse with an open rear-gunner station, wing roots, and
layered diagnostic PBR materials. It never edits or promotes the R4 baseline.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK52-R5-SLICE01"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
BASE = ROOT / "Scripts/blender_phase2_yak52_r4_slice01_silhouette.py"
CONTRACT = ROOT / "Docs/AAA_Review/PHASE2_YAK52_R5_SLICE01_CONTRACT.json"
CAMERAS = ROOT / "Docs/AAA_Review/PHASE2_YAK52_R5_SLICE01_CAMERAS.json"
OUTPUT_DIR = ROOT / "Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R5/Slice01"
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK52_R5_SLICE01_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak52_r5_slice01.glb"
MANIFEST_PATH = ROOT / "Saved/Reports/BLD_M01_YAK52_R5_SLICE01_MANIFEST.json"
SCREENSHOT_DIR = ROOT / "Saved/Screenshots/BLD_M01_YAK52_R5_SLICE01"


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("skyguard_yak52_r5_base", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the frozen R4 construction library")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mat(module: Any, name: str, rgba: tuple[float, ...], metallic: float, roughness: float) -> Any:
    material = module.bpy.data.materials.new(name)
    material.diffuse_color = rgba
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    material["SKG_R5_DiagnosticPBR"] = True
    material["SKG_PromotionAllowed"] = False
    return material


def finish(module: Any, obj: Any, name: str, collection: Any, material: Any, bevel: float = 0.0) -> Any:
    obj.name = name
    module.link_object(obj, collection)
    obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("R5_EdgeRadius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def cylinder(module: Any, name: str, radius: float, depth: float, location: tuple[float, ...],
             collection: Any, material: Any, vertices: int = 64) -> Any:
    module.bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location,
        rotation=(0.0, math.pi / 2.0, 0.0)
    )
    return finish(module, module.bpy.context.object, name, collection, material, 0.012)


def box(module: Any, name: str, location: tuple[float, ...], scale: tuple[float, ...],
        collection: Any, material: Any, bevel: float = 0.03) -> Any:
    module.bpy.ops.mesh.primitive_cube_add(location=location)
    obj = module.bpy.context.object
    obj.scale = scale
    module.bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(module, obj, name, collection, material, bevel)


def create_geometry(module: Any, ledger: dict[str, Any], collections: dict[str, Any],
                    inherited_materials: dict[str, Any]) -> None:
    primary = collections["primary"]
    paint = mat(module, "MAT_R5_PaintedAluminum", (0.18, 0.22, 0.24, 1.0), 0.58, 0.32)
    paint_light = mat(module, "MAT_R5_CowlingPaint", (0.48, 0.52, 0.54, 1.0), 0.46, 0.28)
    dark = mat(module, "MAT_R5_FrameRubber", (0.018, 0.022, 0.024, 1.0), 0.08, 0.46)
    steel = mat(module, "MAT_R5_BareMetal", (0.26, 0.29, 0.31, 1.0), 0.92, 0.24)
    glass = mat(module, "MAT_R5_CanopyGlass", (0.055, 0.16, 0.20, 0.34), 0.0, 0.09)
    glass.surface_render_method = "DITHERED"
    red = mat(module, "MAT_R5_PropHubRed", (0.42, 0.018, 0.012, 1.0), 0.35, 0.3)

    fuselage = module.mesh_from_sections(
        "GEO_R5_ForwardFuselage",
        [
            (-3.87, 0.08, 0.10, 0.36), (-3.45, 0.29, 0.31, 0.35),
            (-2.55, 0.43, 0.45, 0.34), (-1.45, 0.52, 0.56, 0.35),
            (-0.55, 0.60, 0.66, 0.32), (0.45, 0.64, 0.68, 0.28),
            (1.35, 0.69, 0.70, 0.23), (2.25, 0.72, 0.72, 0.17),
            (2.82, 0.70, 0.70, 0.14), (3.02, 0.69, 0.69, 0.13),
        ], 64, primary, paint
    )
    bevel = fuselage.modifiers.new("R5_FuselageWeightedBevel", "BEVEL")
    bevel.width, bevel.segments = 0.012, 2

    cylinder(module, "GEO_R5_CowlingShell", 0.69, 0.78, (3.39, 0.0, 0.13), primary, paint_light, 96)
    cylinder(module, "GEO_R5_CowlingFrontRing", 0.57, 0.09, (3.79, 0.0, 0.13), primary, steel, 96)
    cylinder(module, "GEO_R5_PropHub", 0.18, 0.34, (3.92, 0.0, 0.13), primary, red, 64)

    for index in range(12):
        angle = 2.0 * math.pi * index / 12.0
        y, z = math.cos(angle) * 0.47, 0.13 + math.sin(angle) * 0.47
        box(module, f"GEO_R5_CowlingShutter_{index:02d}", (3.845, y, z),
            (0.025, 0.12, 0.025), primary, dark, 0.008)

    # Airfoil-like wing slabs and substantial root fairings.
    module.prism_from_planform(
        "GEO_R5_Wing_L", [(1.08, 0.0), (0.34, 4.65), (-0.74, 4.65), (-1.03, 0.0)],
        -0.01, 0.13, primary, paint_light
    )
    module.prism_from_planform(
        "GEO_R5_Wing_R", [(1.08, 0.0), (-1.03, 0.0), (-0.74, -4.65), (0.34, -4.65)],
        -0.01, 0.13, primary, paint_light
    )
    for side in (-1.0, 1.0):
        module.bpy.ops.mesh.primitive_uv_sphere_add(
            segments=64, ring_count=32, location=(0.02, side * 0.58, 0.08)
        )
        fairing = module.bpy.context.object
        fairing.scale = (1.20, 0.60, 0.22)
        module.bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        finish(module, fairing, f"GEO_R5_WingRootFairing_{'L' if side > 0 else 'R'}",
               primary, paint_light)

    # Glazed greenhouse: pilot enclosed, rear station visibly open.
    module.mesh_from_sections(
        "GEO_R5_CanopyGlassFront",
        [(0.05, 0.44, 0.38, 0.91), (0.55, 0.42, 0.48, 0.93), (1.20, 0.34, 0.39, 0.88)],
        48, primary, glass
    )
    module.mesh_from_sections(
        "GEO_R5_CanopyGlassRearStowed",
        [(-1.43, 0.42, 0.34, 0.85), (-1.00, 0.44, 0.43, 0.90), (-0.48, 0.44, 0.45, 0.92)],
        48, primary, glass
    )
    for index, x in enumerate((-1.46, -0.98, -0.46, 0.04, 0.57, 1.17)):
        module.bpy.ops.mesh.primitive_torus_add(
            major_radius=0.43, minor_radius=0.025, major_segments=48,
            minor_segments=8, location=(x, 0.0, 0.91),
            rotation=(0.0, math.pi / 2.0, 0.0)
        )
        bow = module.bpy.context.object
        bow.scale.z = 1.08
        module.bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        finish(module, bow, f"GEO_R5_CanopyBow_{index:02d}", primary, dark)
    box(module, "GEO_R5_CanopyRail_L", (-0.15, 0.48, 0.57), (1.57, 0.035, 0.035), primary, dark, 0.012)
    box(module, "GEO_R5_CanopyRail_R", (-0.15, -0.48, 0.57), (1.57, 0.035, 0.035), primary, dark, 0.012)
    box(module, "GEO_R5_RearCockpitSill", (-0.82, 0.0, 0.56), (0.58, 0.45, 0.055), primary, dark, 0.018)
    box(module, "GEO_R5_InstrumentCoaming", (0.42, 0.0, 0.69), (0.16, 0.42, 0.075), primary, dark, 0.02)

    # Propeller blades establish the real front axis without a motion disc.
    for name, z, angle in (("A", 0.72, math.radians(7)), ("B", -0.46, math.radians(187))):
        blade = box(module, f"GEO_R5_PropBlade_{name}", (3.99, 0.0, z),
                    (0.045, 0.12, 0.52), primary, dark, 0.045)
        blade.rotation_euler.x = angle


def validate_scene(module: Any, contract: dict[str, Any], ledger: dict[str, Any],
                   camera_manifest: dict[str, Any], collections: dict[str, Any]) -> dict[str, Any]:
    objects = [obj for obj in collections["primary"].objects if obj.type == "MESH"]
    minimum, maximum = module.world_bounds(objects)
    triangles = sum(module.triangulated_face_count(obj) for obj in objects)
    errors = []
    required_prefixes = (
        "GEO_R5_ForwardFuselage", "GEO_R5_CowlingShell", "GEO_R5_CanopyGlassFront",
        "GEO_R5_CanopyGlassRearStowed", "GEO_R5_WingRootFairing_L",
        "GEO_R5_PropBlade_A", "GEO_R5_PropBlade_B"
    )
    names = {obj.name for obj in objects}
    for name in required_prefixes:
        if name not in names:
            errors.append(f"missing:{name}")
    if len(camera_manifest["cameras"]) != 10:
        errors.append("camera_count_not_10")
    if errors:
        raise RuntimeError("R5 slice validation failed: " + ";".join(errors))
    return {
        "bounds_min_m": list(minimum), "bounds_max_m": list(maximum),
        "overall_length_m": maximum.x - minimum.x,
        "wingspan_m": maximum.y - minimum.y,
        "primary_triangle_count": triangles,
        "primary_object_count": len(objects),
        "camera_count": 10,
        "validation_errors": []
    }


def main() -> None:
    module = load_base()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["authoring_script"]["sha256"] != module.sha256_file(SCRIPT_PATH):
        raise RuntimeError("R5 authoring source does not match frozen contract")
    module.BUILD_ID = BUILD_ID
    module.SCRIPT_PATH = SCRIPT_PATH
    module.OUTPUT_CONTRACT_PATH = CONTRACT
    module.CAMERA_MANIFEST_PATH = CAMERAS
    module.OUTPUT_DIR = OUTPUT_DIR
    module.BLEND_PATH = BLEND_PATH
    module.GLB_PATH = GLB_PATH
    module.MANIFEST_PATH = MANIFEST_PATH
    module.SCREENSHOT_DIR = SCREENSHOT_DIR
    module.CAMERA_IDS = tuple(contract["required_camera_ids"])
    module.PRIMARY_OBJECTS = tuple(contract["required_primary_objects"])
    module.create_primary_geometry = lambda ledger, collections, materials: create_geometry(
        module, ledger, collections, materials
    )
    module.validate_scene = lambda contract_, ledger, cameras, collections: validate_scene(
        module, contract_, ledger, cameras, collections
    )
    module.validate_authorities = lambda contract_: None
    frozen_configure = module.configure_render

    def configure(camera_manifest: dict[str, Any]) -> None:
        patched = copy.deepcopy(camera_manifest)
        patched["render_contract"]["engine"] = "BLENDER_EEVEE"
        if module.bpy.context.scene.world is None:
            module.bpy.context.scene.world = module.bpy.data.worlds.new("WORLD_R5")
        frozen_configure(patched)
        module.bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"

    module.configure_render = configure
    frozen_export = module.export_glb

    def export(primary: Any, requested: Path) -> None:
        frozen_export(primary, requested)
        appended = Path(str(requested) + ".glb")
        if not requested.is_file() and appended.is_file():
            appended.replace(requested)

    module.export_glb = export
    module.main()


if __name__ == "__main__":
    main()
