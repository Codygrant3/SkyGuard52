"""BLD-M01-YAK-PROD-001 production-direction Yak-52 source generator.

Run only with Blender 5.2 in a supervised, serialized build attempt.  The L88
GLB is hash-bound as datum lineage but is never imported, linked, appended, or
copied.  All geometry is authored from a clean scene and the governed real-world
dimension contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


BUILD_ID = "BLD-M01-YAK-PROD-001"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_001_CONTRACT.json"
)
L88_REFERENCE_PATH = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "L88"
    / "yak52_l88_silhouette_blockout.glb"
)
OUTPUT_DIR = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Production"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_PROD_001_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_prod_001.glb"
MANIFEST_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_YAK_PROD_001_MANIFEST.json"
COLLECTION_NAME = "BLD_M01_YAK_PROD_001_EXPORT"
FORBIDDEN_NAME_TOKENS = {
    "blockout",
    "proxy",
    "placeholder",
    "temp",
    "default",
    "cube",
}
REQUIRED_EXPORT_MESH_NAMES = (
    "GEO_PROD_Fuselage",
    "GEO_PROD_EngineCowling",
    "GEO_PROD_Wing_L",
    "GEO_PROD_Wing_R",
    "GEO_PROD_Flap_L",
    "GEO_PROD_Flap_R",
    "GEO_PROD_Aileron_L",
    "GEO_PROD_Aileron_R",
    "GEO_PROD_HorizontalStabilizer_L",
    "GEO_PROD_HorizontalStabilizer_R",
    "GEO_PROD_Elevator_L",
    "GEO_PROD_Elevator_R",
    "GEO_PROD_VerticalStabilizer",
    "GEO_PROD_Rudder",
    "GEO_PROD_PropHub",
    "GEO_PROD_PropBlade_A",
    "GEO_PROD_PropBlade_B",
    "GEO_PROD_CanopyFrontGlass",
    "GEO_PROD_CanopyRearSlidingGlass",
    "GEO_PROD_CanopyBowFront",
    "GEO_PROD_CanopyBowCenter",
    "GEO_PROD_CanopyBowRear",
    "GEO_PROD_CockpitTubRear",
    "GEO_PROD_InstrumentPanelRear",
    "GEO_PROD_SeatRear",
    "GEO_PROD_SeatHarnessRear",
    "GEO_PROD_ControlStickRear",
    "GEO_PROD_ThrottleRear",
    "GEO_PROD_PedalRear_L",
    "GEO_PROD_PedalRear_R",
    "GEO_PROD_CockpitRail_L",
    "GEO_PROD_CockpitRail_R",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    if contract["build_id"] != BUILD_ID:
        raise RuntimeError("Build contract id mismatch")
    return contract


def require_blender_52() -> None:
    version = bpy.app.version
    if version[:2] != (5, 2):
        raise RuntimeError(
            f"{BUILD_ID} requires Blender 5.2, found {version[0]}.{version[1]}"
        )


def verify_reference_only(contract: dict) -> None:
    expected = contract["l88_reference"]["sha256"]
    if not L88_REFERENCE_PATH.is_file():
        raise RuntimeError(f"L88 datum reference missing: {L88_REFERENCE_PATH}")
    actual = sha256_file(L88_REFERENCE_PATH)
    if actual != expected:
        raise RuntimeError(
            "L88 datum reference hash mismatch; refusing to author against drift"
        )


def reset_factory_scene() -> bpy.types.Collection:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    return collection


def link_exclusively(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def material(
    name: str,
    base_color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    transmission: float = 0.0,
    alpha: float = 1.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = base_color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.surface_render_method = "DITHERED"
        mat.use_transparency_overlap = False
    return mat


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "MAT_YakPaint": material(
            "MAT_YakPaint", (0.30, 0.34, 0.36, 1.0), 0.15, 0.32
        ),
        "MAT_YakBareMetal": material(
            "MAT_YakBareMetal", (0.48, 0.51, 0.52, 1.0), 0.82, 0.23
        ),
        "MAT_CockpitGreen": material(
            "MAT_CockpitGreen", (0.16, 0.25, 0.21, 1.0), 0.05, 0.48
        ),
        "MAT_CockpitBlack": material(
            "MAT_CockpitBlack", (0.018, 0.021, 0.020, 1.0), 0.08, 0.36
        ),
        "MAT_CanopyGlass": material(
            "MAT_CanopyGlass", (0.32, 0.48, 0.54, 0.18), 0.0, 0.08, 0.92, 0.18
        ),
        "MAT_SeatVinyl": material(
            "MAT_SeatVinyl", (0.19, 0.20, 0.18, 1.0), 0.0, 0.62
        ),
        "MAT_HarnessWebbing": material(
            "MAT_HarnessWebbing", (0.47, 0.08, 0.055, 1.0), 0.0, 0.72
        ),
        "MAT_Propeller": material(
            "MAT_Propeller", (0.055, 0.060, 0.064, 1.0), 0.18, 0.28
        ),
    }


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def finish_mesh(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
    bevel_width: float = 0.0,
) -> bpy.types.Object:
    link_exclusively(obj, collection)
    for mat in materials:
        obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if bevel_width > 0.0:
        bevel = obj.modifiers.new("MOD_ProductionBevel", "BEVEL")
        bevel.width = bevel_width
        bevel.segments = 4
        bevel.limit_method = "ANGLE"
    set_active(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.modifier_apply(
        modifier="MOD_ProductionBevel"
    ) if bevel_width > 0.0 else None
    ensure_uv0(obj)
    return obj


def ensure_uv0(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    while obj.data.uv_layers:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
    obj.data.uv_layers.new(name="UV0")
    set_active(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def mesh_from_data(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
    bevel_width: float = 0.0,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, collection, materials, bevel_width)


def create_fuselage(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> bpy.types.Object:
    stations = [
        (-3.10, 0.10, 0.16, 0.62),
        (-3.05, 0.22, 0.27, 0.60),
        (-2.55, 0.35, 0.42, 0.55),
        (-1.85, 0.48, 0.60, 0.48),
        (-1.10, 0.55, 0.72, 0.42),
        (-0.25, 0.59, 0.76, 0.36),
        (0.60, 0.61, 0.77, 0.34),
        (1.40, 0.62, 0.75, 0.31),
        (2.20, 0.66, 0.73, 0.28),
        (2.95, 0.72, 0.72, 0.25),
        (3.65, 0.78, 0.76, 0.21),
        (4.15, 0.67, 0.68, 0.16),
        (4.445, 0.36, 0.42, 0.12),
    ]
    segments = 64
    vertices: list[tuple[float, float, float]] = []
    for x, ry, rz, z_center in stations:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            vertices.append(
                (x, ry * math.sin(angle), z_center + rz * math.cos(angle))
            )
    faces: list[tuple[int, ...]] = []
    for ring in range(len(stations) - 1):
        start = ring * segments
        nxt = (ring + 1) * segments
        for index in range(segments):
            following = (index + 1) % segments
            faces.append(
                (start + index, start + following, nxt + following, nxt + index)
            )
    faces.append(tuple(reversed(range(segments))))
    last = (len(stations) - 1) * segments
    faces.append(tuple(last + index for index in range(segments)))
    return mesh_from_data(
        "GEO_PROD_Fuselage",
        vertices,
        faces,
        collection,
        [mats["MAT_YakPaint"], mats["MAT_YakBareMetal"]],
    )


def airfoil_z(chord_t: float, thickness: float) -> float:
    x = max(0.001, min(0.999, chord_t))
    return (
        5.0
        * thickness
        * (
            0.2969 * math.sqrt(x)
            - 0.1260 * x
            - 0.3516 * x * x
            + 0.2843 * x**3
            - 0.1015 * x**4
        )
    )


def create_lifting_surface(
    name: str,
    side: int,
    x_le_root: float,
    root_chord: float,
    tip_chord: float,
    y_root: float,
    y_tip: float,
    z_root: float,
    z_tip: float,
    sweep: float,
    thickness: float,
    chord_start: float,
    chord_end: float,
    span_steps: int,
    chord_steps: int,
    collection: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    row = chord_steps + 1
    for surface_sign in (1.0, -1.0):
        for span_index in range(span_steps + 1):
            span_t = span_index / span_steps
            chord = root_chord + (tip_chord - root_chord) * span_t
            y = side * (y_root + (y_tip - y_root) * span_t)
            z_center = z_root + (z_tip - z_root) * span_t
            leading_x = x_le_root + sweep * span_t
            for chord_index in range(chord_steps + 1):
                local_t = chord_start + (
                    chord_end - chord_start
                ) * chord_index / chord_steps
                x = leading_x + chord * local_t
                z = z_center + surface_sign * airfoil_z(local_t, thickness) * chord
                vertices.append((x, y, z))
    plane_size = (span_steps + 1) * row
    for plane in range(2):
        offset = plane * plane_size
        reverse = plane == 1
        for span_index in range(span_steps):
            for chord_index in range(chord_steps):
                a = offset + span_index * row + chord_index
                quad = (a, a + 1, a + row + 1, a + row)
                faces.append(tuple(reversed(quad)) if reverse else quad)
    for span_index in range(span_steps):
        for chord_index in (0, chord_steps):
            top = span_index * row + chord_index
            top_next = (span_index + 1) * row + chord_index
            bottom = plane_size + top
            bottom_next = plane_size + top_next
            faces.append((top, bottom, bottom_next, top_next))
    for span_index in (0, span_steps):
        base = span_index * row
        for chord_index in range(chord_steps):
            top = base + chord_index
            bottom = plane_size + top
            faces.append((top, top + 1, plane_size + top + 1, bottom))
    obj = mesh_from_data(name, vertices, faces, collection, [mat])
    hinge_t = chord_start
    if chord_start > 0.0:
        obj["pivot_role"] = "control_hinge"
        obj["hinge_chord_fraction"] = hinge_t
    return obj


def add_cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    rotation: tuple[float, float, float],
    collection: bpy.types.Collection,
    mats: Iterable[bpy.types.Material],
    vertices: int = 64,
    bevel: float = 0.01,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        end_fill_type="NGON",
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, collection, mats, bevel)


def add_beveled_box(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    collection: bpy.types.Collection,
    mats: Iterable[bpy.types.Material],
    bevel: float,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return finish_mesh(obj, collection, mats, bevel)


def create_canopy_shell(
    name: str,
    x_start: float,
    x_end: float,
    width: float,
    rail_z: float,
    crown_z: float,
    collection: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    x_steps = 12
    arch_steps = 24
    vertices: list[tuple[float, float, float]] = []
    for x_index in range(x_steps + 1):
        x_t = x_index / x_steps
        x = x_start + (x_end - x_start) * x_t
        longitudinal = math.sin(math.pi * x_t) ** 0.55
        local_crown = rail_z + (crown_z - rail_z) * (0.86 + 0.14 * longitudinal)
        for arch_index in range(arch_steps + 1):
            arch_t = arch_index / arch_steps
            angle = math.pi * arch_t
            y = width * math.cos(angle)
            z = rail_z + (local_crown - rail_z) * math.sin(angle)
            vertices.append((x, y, z))
    faces = []
    row = arch_steps + 1
    for x_index in range(x_steps):
        for arch_index in range(arch_steps):
            a = x_index * row + arch_index
            faces.append((a, a + row, a + row + 1, a + 1))
    obj = mesh_from_data(name, vertices, faces, collection, [mat])
    solidify = obj.modifiers.new("MOD_GlassThickness", "SOLIDIFY")
    solidify.thickness = 0.008
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=solidify.name)
    obj["pivot_role"] = "canopy_slide_origin" if "RearSliding" in name else "fixed"
    return obj


def create_arch(
    name: str,
    x: float,
    width: float,
    rail_z: float,
    crown_z: float,
    collection: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.018
    curve.bevel_resolution = 4
    spline = curve.splines.new("POLY")
    count = 33
    spline.points.add(count - 1)
    for index, point in enumerate(spline.points):
        angle = math.pi * index / (count - 1)
        point.co = (
            x,
            width * math.cos(angle),
            rail_z + (crown_z - rail_z) * math.sin(angle),
            1.0,
        )
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(mat)
    set_active(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, collection, [mat])


def create_propeller(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    hub_x = 4.50
    add_cylinder(
        "GEO_PROD_PropHub",
        0.19,
        0.29,
        (hub_x, 0.0, 0.12),
        (0.0, math.pi / 2.0, 0.0),
        collection,
        [mats["MAT_YakBareMetal"], mats["MAT_Propeller"]],
        64,
        0.018,
    )["pivot_role"] = "propeller_axis"
    sections = 20
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for blade_sign, name in (
        (1.0, "GEO_PROD_PropBlade_A"),
        (-1.0, "GEO_PROD_PropBlade_B"),
    ):
        vertices.clear()
        faces.clear()
        for index in range(sections + 1):
            t = index / sections
            radial = 0.18 + 1.02 * t
            chord = 0.17 - 0.07 * t
            twist = math.radians(28.0 - 20.0 * t)
            for side in (-1.0, 1.0):
                y = side * chord * 0.5 * math.cos(twist)
                x = hub_x + side * chord * 0.5 * math.sin(twist)
                z = 0.12 + blade_sign * radial
                vertices.append((x, y, z))
        for index in range(sections):
            a = index * 2
            faces.append((a, a + 2, a + 3, a + 1))
        obj = mesh_from_data(
            name,
            list(vertices),
            list(faces),
            collection,
            [mats["MAT_Propeller"]],
        )
        solidify = obj.modifiers.new("MOD_BladeThickness", "SOLIDIFY")
        solidify.thickness = 0.018
        bevel = obj.modifiers.new("MOD_BladeEdge", "BEVEL")
        bevel.width = 0.008
        bevel.segments = 3
        set_active(obj)
        bpy.ops.object.modifier_apply(modifier=solidify.name)
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        obj["pivot_role"] = "propeller_axis"
        obj["pivot_world"] = [hub_x, 0.0, 0.12]


def create_tail(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    for side, suffix in ((1, "R"), (-1, "L")):
        create_lifting_surface(
            f"GEO_PROD_HorizontalStabilizer_{suffix}",
            side,
            -2.93,
            1.22,
            0.70,
            0.08,
            1.58,
            0.58,
            0.65,
            0.10,
            0.09,
            0.0,
            0.70,
            12,
            18,
            collection,
            mats["MAT_YakPaint"],
        )
        create_lifting_surface(
            f"GEO_PROD_Elevator_{suffix}",
            side,
            -2.93,
            1.22,
            0.70,
            0.08,
            1.58,
            0.58,
            0.65,
            0.10,
            0.09,
            0.70,
            1.0,
            12,
            10,
            collection,
            mats["MAT_YakPaint"],
        )
    fin_vertices = [
        (-3.10, -0.055, 0.58),
        (-3.10, 0.055, 0.58),
        (-2.52, -0.045, 1.94),
        (-2.52, 0.045, 1.94),
        (-1.62, -0.06, 0.65),
        (-1.62, 0.06, 0.65),
    ]
    fin_faces = [
        (0, 4, 2),
        (1, 3, 5),
        (0, 1, 5, 4),
        (2, 4, 5, 3),
        (0, 2, 3, 1),
    ]
    mesh_from_data(
        "GEO_PROD_VerticalStabilizer",
        fin_vertices,
        fin_faces,
        collection,
        [mats["MAT_YakPaint"]],
        0.015,
    )
    rudder = mesh_from_data(
        "GEO_PROD_Rudder",
        [
            (-3.08, -0.05, 0.62),
            (-3.08, 0.05, 0.62),
            (-3.00, -0.04, 1.72),
            (-3.00, 0.04, 1.72),
            (-2.52, -0.035, 1.94),
            (-2.52, 0.035, 1.94),
        ],
        [(0, 2, 4), (1, 5, 3), (0, 1, 3, 2), (2, 3, 5, 4)],
        collection,
        [mats["MAT_YakPaint"]],
        0.012,
    )
    rudder["pivot_role"] = "rudder_hinge"
    rudder["pivot_world"] = [-2.55, 0.0, 1.28]


def create_rear_cockpit(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    add_beveled_box(
        "GEO_PROD_CockpitTubRear",
        (-0.64, 0.0, 0.72),
        (1.05, 0.68, 0.48),
        collection,
        [mats["MAT_CockpitGreen"]],
        0.09,
    )
    add_beveled_box(
        "GEO_PROD_InstrumentPanelRear",
        (0.12, 0.0, 1.05),
        (0.12, 0.66, 0.38),
        collection,
        [mats["MAT_CockpitBlack"], mats["MAT_CockpitGreen"]],
        0.035,
    )
    add_beveled_box(
        "GEO_PROD_SeatRear",
        (-1.05, 0.0, 0.83),
        (0.62, 0.50, 0.16),
        collection,
        [mats["MAT_SeatVinyl"]],
        0.06,
    )
    add_beveled_box(
        "GEO_PROD_SeatHarnessRear",
        (-1.02, 0.0, 1.02),
        (0.72, 0.045, 0.055),
        collection,
        [mats["MAT_HarnessWebbing"]],
        0.018,
    )
    add_cylinder(
        "GEO_PROD_ControlStickRear",
        0.027,
        0.54,
        (-0.62, 0.0, 0.82),
        (0.0, 0.12, 0.0),
        collection,
        [mats["MAT_CockpitBlack"]],
        32,
        0.006,
    )["pivot_role"] = "control_stick_base"
    add_beveled_box(
        "GEO_PROD_ThrottleRear",
        (-0.52, -0.61, 0.91),
        (0.18, 0.08, 0.10),
        collection,
        [mats["MAT_CockpitBlack"]],
        0.018,
    )["pivot_role"] = "throttle_axis"
    for side, suffix in ((-1, "L"), (1, "R")):
        add_beveled_box(
            f"GEO_PROD_PedalRear_{suffix}",
            (-0.12, side * 0.20, 0.56),
            (0.16, 0.10, 0.045),
            collection,
            [mats["MAT_YakBareMetal"]],
            0.012,
        )["pivot_role"] = "pedal_hinge"
        add_beveled_box(
            f"GEO_PROD_CockpitRail_{suffix}",
            (-0.58, side * 0.58, 1.34),
            (1.62, 0.045, 0.045),
            collection,
            [mats["MAT_YakBareMetal"]],
            0.012,
        )["pivot_role"] = "canopy_rail"


def add_empty(
    name: str,
    location: tuple[float, float, float],
    rotation: tuple[float, float, float],
    collection: bpy.types.Collection,
    display: str = "ARROWS",
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = display
    obj.empty_display_size = 0.12
    obj.location = location
    obj.rotation_euler = rotation
    obj["datum_contract"] = BUILD_ID
    collection.objects.link(obj)
    return obj


def create_datums(collection: bpy.types.Collection) -> None:
    specs = {
        "DATUM_AircraftOrigin": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        "DATUM_PropAxis": ((4.50, 0.0, 0.12), (0.0, math.pi / 2.0, 0.0)),
        "DATUM_RearSeatEye": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
        "DATUM_LengthNose": ((4.645, 0.0, 0.12), (0.0, 0.0, 0.0)),
        "DATUM_LengthTail": ((-3.10, 0.0, 0.62), (0.0, 0.0, 0.0)),
        "DATUM_Wingtip_L": ((0.0, -4.65, 0.24), (0.0, 0.0, 0.0)),
        "DATUM_Wingtip_R": ((0.0, 4.65, 0.24), (0.0, 0.0, 0.0)),
        "DATUM_HeightTop": ((0.0, 0.0, 2.09), (0.0, 0.0, 0.0)),
        "DATUM_HeightBottom": ((0.0, 0.0, -0.61), (0.0, 0.0, 0.0)),
        "DATUM_PropTipTop": ((4.50, 0.0, 1.32), (0.0, 0.0, 0.0)),
        "DATUM_PropTipBottom": ((4.50, 0.0, -1.08), (0.0, 0.0, 0.0)),
        "DATUM_CockpitClear_L": ((-0.88, -0.36, 1.34), (0.0, 0.0, 0.0)),
        "DATUM_CockpitClear_R": ((-0.88, 0.36, 1.34), (0.0, 0.0, 0.0)),
        "DATUM_CockpitRail": ((-0.88, 0.0, 1.34), (0.0, 0.0, 0.0)),
        "SOCKET_PilotSeat": ((0.82, 0.0, 0.84), (0.0, 0.0, 0.0)),
        "SOCKET_RearGunnerSeat": ((-0.92, 0.0, 0.84), (0.0, 0.0, 0.0)),
        "SOCKET_ADSEye": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
        "SOCKET_RifleGrip_R": ((-0.42, 0.25, 1.35), (0.0, 0.0, 0.0)),
        "SOCKET_RifleGrip_L": ((0.02, 0.25, 1.38), (0.0, 0.0, 0.0)),
        "SOCKET_RifleMuzzle": ((1.03, 0.25, 1.43), (0.0, 0.0, 0.0)),
        "SOCKET_IglaGrip_R": ((-0.34, 0.30, 1.30), (0.0, 0.0, 0.0)),
        "SOCKET_IglaGrip_L": ((0.10, 0.30, 1.34), (0.0, 0.0, 0.0)),
        "SOCKET_IglaLaunchAxis": ((1.28, 0.30, 1.42), (0.0, 0.0, 0.0)),
        "SOCKET_CanopyRearTravel": ((-1.25, 0.0, 1.43), (0.0, 0.0, 0.0)),
        "SOCKET_CockpitSafetyOrigin": ((-0.30, 0.0, 1.20), (0.0, 0.0, 0.0)),
        "SOCKET_CameraRearGunner": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
    }
    for name, (location, rotation) in specs.items():
        add_empty(name, location, rotation, collection)


def create_aircraft(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    create_fuselage(collection, mats)
    add_cylinder(
        "GEO_PROD_EngineCowling",
        0.80,
        1.12,
        (3.84, 0.0, 0.15),
        (0.0, math.pi / 2.0, 0.0),
        collection,
        [mats["MAT_YakPaint"], mats["MAT_YakBareMetal"]],
        96,
        0.025,
    )
    for side, suffix in ((-1, "L"), (1, "R")):
        create_lifting_surface(
            f"GEO_PROD_Wing_{suffix}",
            side,
            1.15,
            1.68,
            0.84,
            0.42,
            4.65,
            0.19,
            0.26,
            0.22,
            0.12,
            0.0,
            0.72,
            18,
            24,
            collection,
            mats["MAT_YakPaint"],
        )
        flap = create_lifting_surface(
            f"GEO_PROD_Flap_{suffix}",
            side,
            1.15,
            1.68,
            0.84,
            0.55,
            2.05,
            0.20,
            0.22,
            0.22,
            0.10,
            0.72,
            1.0,
            10,
            10,
            collection,
            mats["MAT_YakPaint"],
        )
        flap["pivot_role"] = "flap_hinge"
        flap["pivot_world"] = [0.0, side * 0.55, 0.21]
        aileron = create_lifting_surface(
            f"GEO_PROD_Aileron_{suffix}",
            side,
            1.15,
            1.68,
            0.84,
            2.05,
            4.65,
            0.22,
            0.26,
            0.22,
            0.10,
            0.72,
            1.0,
            14,
            10,
            collection,
            mats["MAT_YakPaint"],
        )
        aileron["pivot_world"] = [0.0, side * 2.05, 0.23]
    create_tail(collection, mats)
    create_propeller(collection, mats)
    create_canopy_shell(
        "GEO_PROD_CanopyFrontGlass",
        (0.10),
        1.48,
        0.57,
        1.34,
        2.10,
        collection,
        mats["MAT_CanopyGlass"],
    )
    create_canopy_shell(
        "GEO_PROD_CanopyRearSlidingGlass",
        -1.53,
        -0.02,
        0.58,
        1.34,
        2.08,
        collection,
        mats["MAT_CanopyGlass"],
    )
    for name, x in (
        ("GEO_PROD_CanopyBowFront", 1.45),
        ("GEO_PROD_CanopyBowCenter", -0.02),
        ("GEO_PROD_CanopyBowRear", -1.53),
    ):
        create_arch(
            name,
            x,
            0.59,
            1.34,
            2.09,
            collection,
            mats["MAT_YakBareMetal"],
        )
    create_rear_cockpit(collection, mats)
    create_datums(collection)


def reject_forbidden_names(collection: bpy.types.Collection) -> None:
    violations = []
    for obj in collection.all_objects:
        lowered = obj.name.lower()
        tokens = [token for token in FORBIDDEN_NAME_TOKENS if token in lowered]
        if tokens:
            violations.append({"object": obj.name, "tokens": tokens})
    if violations:
        raise RuntimeError(f"Forbidden shipping names: {violations}")


def validate_contract(
    contract: dict, collection: bpy.types.Collection
) -> dict[str, object]:
    if set(contract["required_mesh_objects"]) != set(REQUIRED_EXPORT_MESH_NAMES):
        raise RuntimeError("Generator/contract required-mesh drift")
    objects = {obj.name: obj for obj in collection.all_objects}
    required_meshes = set(contract["required_mesh_objects"])
    required_sockets = set(contract["required_socket_objects"])
    required_datums = set(contract["required_datum_objects"])
    missing_meshes = sorted(required_meshes - set(objects))
    missing_sockets = sorted(required_sockets - set(objects))
    missing_datums = sorted(required_datums - set(objects))
    uv_failures = []
    material_failures = []
    vertex_failures = []
    for name in required_meshes:
        obj = objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        if contract["required_uv_layer"] not in obj.data.uv_layers:
            uv_failures.append(name)
        if not obj.data.materials:
            material_failures.append(name)
        minimum = contract["minimum_mesh_vertices"].get(name)
        if minimum is not None and len(obj.data.vertices) < minimum:
            vertex_failures.append(
                {"name": name, "actual": len(obj.data.vertices), "minimum": minimum}
            )
    return {
        "missing_meshes": missing_meshes,
        "missing_sockets": missing_sockets,
        "missing_datums": missing_datums,
        "uv_failures": sorted(uv_failures),
        "material_failures": sorted(material_failures),
        "minimum_vertex_failures": vertex_failures,
        "pass": not (
            missing_meshes
            or missing_sockets
            or missing_datums
            or uv_failures
            or material_failures
            or vertex_failures
        ),
    }


def object_record(obj: bpy.types.Object) -> dict:
    record = {
        "name": obj.name,
        "type": obj.type,
        "location_m": [round(value, 6) for value in obj.location],
        "rotation_radians": [round(value, 6) for value in obj.rotation_euler],
        "scale": [round(value, 6) for value in obj.scale],
    }
    if obj.type == "MESH":
        record.update(
            {
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "uv_layers": [layer.name for layer in obj.data.uv_layers],
                "material_slots": [
                    slot.material.name for slot in obj.material_slots if slot.material
                ],
                "bounds_m": [
                    [round(value, 6) for value in corner]
                    for corner in obj.bound_box
                ],
            }
        )
    return record


def measured_dimensions(collection: bpy.types.Collection) -> dict[str, float]:
    objects = {obj.name: obj for obj in collection.all_objects}

    def distance(a: str, b: str) -> float:
        return (objects[a].location - objects[b].location).length

    return {
        "overall_length": distance("DATUM_LengthNose", "DATUM_LengthTail"),
        "wingspan": distance("DATUM_Wingtip_L", "DATUM_Wingtip_R"),
        "overall_height": distance("DATUM_HeightTop", "DATUM_HeightBottom"),
        "propeller_diameter": distance("DATUM_PropTipTop", "DATUM_PropTipBottom"),
        "rear_cockpit_clear_width": distance(
            "DATUM_CockpitClear_L", "DATUM_CockpitClear_R"
        ),
        "rear_cockpit_rail_height": objects["DATUM_CockpitRail"].location.z,
    }


def save_and_export(collection: bpy.types.Collection) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.all_objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_animations=False,
    )


def write_manifest(
    contract: dict,
    collection: bpy.types.Collection,
    validation: dict[str, object],
    elapsed_seconds: float,
) -> None:
    manifest = {
        "schema": "skyguard.bld-m01-yak-prod-001.artifact-manifest.v1",
        "build_id": BUILD_ID,
        "blender_version": ".".join(str(value) for value in bpy.app.version),
        "coordinate_contract": contract["coordinate_contract"],
        "reference_dimensions_m": contract["reference_dimensions_m"],
        "measured_dimensions_m": measured_dimensions(collection),
        "l88_reference": {
            "path": str(L88_REFERENCE_PATH),
            "sha256": sha256_file(L88_REFERENCE_PATH),
            "use": "datum_reference_only_not_imported",
        },
        "generator": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "contract": {
            "path": str(CONTRACT_PATH),
            "sha256": sha256_file(CONTRACT_PATH),
        },
        "outputs": {
            "blend": {
                "path": str(BLEND_PATH),
                "bytes": BLEND_PATH.stat().st_size,
                "sha256": sha256_file(BLEND_PATH),
            },
            "glb": {
                "path": str(GLB_PATH),
                "bytes": GLB_PATH.stat().st_size,
                "sha256": sha256_file(GLB_PATH),
            },
        },
        "objects": [
            object_record(obj)
            for obj in sorted(collection.all_objects, key=lambda item: item.name)
        ],
        "validation": validation,
        "forbidden_name_violations": [],
        "elapsed_seconds": round(elapsed_seconds, 3),
        "gate": "PASS" if validation["pass"] else "FAIL",
        "promotion": contract["promotion"],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    started = time.perf_counter()
    require_blender_52()
    contract = load_contract()
    verify_reference_only(contract)
    collection = reset_factory_scene()
    mats = build_materials()
    create_aircraft(collection, mats)
    reject_forbidden_names(collection)
    validation = validate_contract(contract, collection)
    if not validation["pass"]:
        raise RuntimeError(f"Offline source contract failed: {validation}")
    save_and_export(collection)
    write_manifest(contract, collection, validation, time.perf_counter() - started)
    print(f"[{BUILD_ID}] source build complete")
    print(f"[{BUILD_ID}] blend={BLEND_PATH}")
    print(f"[{BUILD_ID}] glb={GLB_PATH}")
    print(f"[{BUILD_ID}] manifest={MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[{BUILD_ID}] FAILED: {exc}", file=sys.stderr)
        raise
