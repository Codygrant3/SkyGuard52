"""
Skyguard 52 — Core Rifle Artist-Grade Method 03, Stage A
Forward assembly only: free-float ventilated handguard, integrated Picatinny,
barrel, provisional open-tine muzzle, side QD socket.

Original geometry only. No Method 01/02 assets. No external downloads.
Units: meters (Unreal-compatible). +Y = muzzle forward. Origin at receiver interface.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SOURCE_DIR = Path(r"D:\Skyguard52\Production\Sources\core-rifle\artist_grade_method_03_grok_staged")
ATTEMPT_DIR = Path(r"D:\Skyguard52\Production\Attempts\core-rifle-artist-grade-method03\stage_A_attempt_01")
OUTPUT_DIR = Path(r"D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD03\stage_A")
BLEND_PATH = OUTPUT_DIR / "core-rifle-method03-stageA.blend"
ROOT = Path(r"D:\Skyguard52")

REFERENCE_CROPS = [
    r"References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0435_0014.500s_rifle_crop.png",
    r"References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0450_0015.000s_rifle_crop.png",
    r"References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0510_0017.000s_rifle_crop.png",
    r"References\CombatAssets\TechnicalIntake_Cycle02\rifle_crops\frame_0675_0022.500s_rifle_crop.png",
]

# ---------------------------------------------------------------------------
# Parametric dimensions (meters)
# ---------------------------------------------------------------------------
HG_LEN = 0.305
HG_HALF_W = 0.0195
HG_HALF_H = 0.0180
CHAMFER = 0.0055
WALL = 0.0027
FRONT_RING = 0.012
REAR_RING = 0.016

WIN_COUNT = 4
WIN_LEN = 0.048
WIN_H = 0.0115
WIN_CORNER_R = 0.0028
WIN_START = 0.048
WIN_PITCH = 0.062

SLOT_COUNT = 4
SLOT_LEN = 0.028
SLOT_H = 0.0042
SLOT_START = 0.058
SLOT_PITCH = 0.062
SLOT_Z = 0.0075

BOT_WIN_COUNT = 3
BOT_WIN_LEN = 0.042
BOT_WIN_W = 0.010
BOT_START = 0.072
BOT_PITCH = 0.068

RAIL_BASE_H = 0.0048
RAIL_BASE_W = 0.0205
RAIL_TOOTH_PITCH = 0.0100
RAIL_TOOTH_W = 0.0052
RAIL_TOOTH_H = 0.0028
RAIL_TOOTH_D = 0.0185
RAIL_SIDE_WALL = 0.0018

BARREL_R = 0.0072
BARREL_INNER_R = 0.0028
BARREL_START = -0.006
BARREL_END = HG_LEN + 0.092
GAS_BLOCK_Y = HG_LEN * 0.72
GAS_BLOCK_LEN = 0.018
GAS_BLOCK_R = 0.0105

MUZZLE_BASE_LEN = 0.014
MUZZLE_TINE_LEN = 0.036
MUZZLE_OUTER_R = 0.0110
MUZZLE_INNER_R = 0.0082
MUZZLE_BORE_R = 0.0030
TINE_COUNT = 4
TINE_GAP_DEG = 30.0

QD_Y = 0.095
QD_Z = -0.001
QD_R = 0.0075
QD_DEPTH = 0.0035

BEVEL_WIDTH = 0.00032
BEVEL_SEG = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _link(obj: bpy.types.Object, coll: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def _get_or_create_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
    root = parent or bpy.context.scene.collection
    try:
        if coll.name not in {c.name for c in root.children}:
            root.children.link(coll)
    except RuntimeError:
        pass
    return coll


def _new_mesh_object(name: str, mesh: bpy.types.Mesh, coll: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    _link(obj, coll)
    return obj


def _delete_object(obj: bpy.types.Object) -> None:
    mesh = obj.data if getattr(obj, "type", None) == "MESH" else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def _set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def _apply_mods(obj: bpy.types.Object) -> None:
    _set_active(obj)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"mod apply fail {obj.name}/{mod.name}: {e}")


def _boolean(target: bpy.types.Object, other: bpy.types.Object, operation: str = "DIFFERENCE") -> None:
    _set_active(target)
    mod = target.modifiers.new(name=f"Bool_{operation}_{other.name}", type="BOOLEAN")
    mod.operation = operation
    mod.solver = "EXACT"
    mod.object = other
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        mod = target.modifiers.get(f"Bool_{operation}_{other.name}")
        if mod is None:
            mod = target.modifiers.new(name=f"BoolF_{operation}_{other.name}", type="BOOLEAN")
            mod.operation = operation
            mod.object = other
        mod.solver = "FLOAT"
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"boolean fail {target.name} {operation} {other.name}: {e}")


def _apply_scale_rot(obj: bpy.types.Object) -> None:
    _set_active(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def _shade_and_bevel(obj: bpy.types.Object, width: float = BEVEL_WIDTH, segments: int = BEVEL_SEG) -> None:
    _set_active(obj)
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = True
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass

    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(28)
    mod.harden_normals = True
    mod.miter_outer = "MITER_ARC"
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception as e:
        print(f"bevel fail {obj.name}: {e}")

    # Weighted normals
    wn = obj.modifiers.new(name="WN", type="WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.weight = 50
    wn.keep_sharp = True
    try:
        bpy.ops.object.modifier_apply(modifier=wn.name)
    except Exception:
        pass

    # Sharp edges by angle
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for e in bm.edges:
        if e.is_boundary:
            e.smooth = False
        else:
            lf = e.link_faces
            if len(lf) == 2:
                e.smooth = lf[0].normal.angle(lf[1].normal) < math.radians(35)
            else:
                e.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def _octagon_profile(half_w: float, half_h: float, chamfer: float) -> list[tuple[float, float]]:
    c = chamfer
    return [
        (half_w, half_h - c),
        (half_w - c, half_h),
        (-half_w + c, half_h),
        (-half_w, half_h - c),
        (-half_w, -half_h + c),
        (-half_w + c, -half_h),
        (half_w - c, -half_h),
        (half_w, -half_h + c),
    ]


def _extrude_profile_solid(name: str, profile: list[tuple[float, float]], y0: float, y1: float, coll) -> bpy.types.Object:
    """Create a solid prism from 2D profile (x,z) extruded along Y."""
    bm = bmesh.new()
    n = len(profile)
    bottom = [bm.verts.new((p[0], y0, p[1])) for p in profile]
    top = [bm.verts.new((p[0], y1, p[1])) for p in profile]
    bm.faces.new(bottom)
    bm.faces.new(list(reversed(top)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    return _new_mesh_object(name, mesh, coll)


def _rounded_box(name: str, sx: float, sy: float, sz: float, corner_r: float, segs: int = 3) -> bpy.types.Mesh:
    """Centered rounded box mesh for cutters."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    r = min(corner_r, sx * 0.45, sy * 0.45, sz * 0.45)
    if r > 1e-6:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=segs, affect="EDGES", profile=0.5)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _cylinder_y(name: str, radius: float, y0: float, y1: float, segs: int, coll, radius2: float | None = None) -> bpy.types.Object:
    bm = bmesh.new()
    r2 = radius if radius2 is None else radius2
    depth = abs(y1 - y0)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=radius, radius2=r2, depth=depth)
    bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    mid = (y0 + y1) * 0.5
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=(0, mid, 0))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    return _new_mesh_object(name, mesh, coll)


def _box(name: str, x0, x1, y0, y1, z0, z1, coll) -> bpy.types.Object:
    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    for idxs in (
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ):
        bm.faces.new([verts[i] for i in idxs])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    return _new_mesh_object(name, mesh, coll)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_handguard(fwd, cutters_coll) -> bpy.types.Object:
    outer_prof = _octagon_profile(HG_HALF_W, HG_HALF_H, CHAMFER)
    inner_prof = _octagon_profile(HG_HALF_W - WALL, HG_HALF_H - WALL, max(0.001, CHAMFER - WALL * 0.35))

    outer = _extrude_profile_solid("M03A_HG_Outer", outer_prof, 0.0, HG_LEN, fwd)
    # Inner cutter leaves solid front/rear rings
    inner = _extrude_profile_solid(
        "M03A_CUT_HG_Inner",
        inner_prof,
        REAR_RING,
        HG_LEN - FRONT_RING,
        cutters_coll,
    )
    _boolean(outer, inner, "DIFFERENCE")
    _delete_object(inner)

    # Front & rear bore openings (barrel path)
    bore_r = BARREL_R + 0.0018
    rear_bore = _cylinder_y("M03A_CUT_RearBore", bore_r, -0.01, REAR_RING + 0.005, 24, cutters_coll)
    front_bore = _cylinder_y("M03A_CUT_FrontBore", bore_r, HG_LEN - FRONT_RING - 0.005, HG_LEN + 0.01, 24, cutters_coll)
    _boolean(outer, rear_bore, "DIFFERENCE")
    _boolean(outer, front_bore, "DIFFERENCE")
    _delete_object(rear_bore)
    _delete_object(front_bore)

    # Side large windows
    for side_sign, side_tag in ((-1.0, "L"), (1.0, "R")):
        for i in range(WIN_COUNT):
            y = WIN_START + i * WIN_PITCH
            mesh = _rounded_box(f"cut_win_{side_tag}_{i}", WALL * 5.0, WIN_LEN, WIN_H, WIN_CORNER_R, 3)
            cutter = _new_mesh_object(f"M03A_CUT_Win_{side_tag}_{i}", mesh, cutters_coll)
            cutter.location = (side_sign * (HG_HALF_W - WALL * 0.2), y, 0.0)
            bpy.context.view_layer.update()
            _boolean(outer, cutter, "DIFFERENCE")
            _delete_object(cutter)

        # Upper small slots
        for i in range(SLOT_COUNT):
            y = SLOT_START + i * SLOT_PITCH
            mesh = _rounded_box(f"cut_slot_{side_tag}_{i}", WALL * 5.0, SLOT_LEN, SLOT_H, 0.0015, 2)
            cutter = _new_mesh_object(f"M03A_CUT_Slot_{side_tag}_{i}", mesh, cutters_coll)
            cutter.location = (side_sign * (HG_HALF_W - WALL * 0.2), y, SLOT_Z)
            bpy.context.view_layer.update()
            _boolean(outer, cutter, "DIFFERENCE")
            _delete_object(cutter)

    # Bottom windows
    for i in range(BOT_WIN_COUNT):
        y = BOT_START + i * BOT_PITCH
        mesh = _rounded_box(f"cut_bot_{i}", BOT_WIN_W, BOT_WIN_LEN, WALL * 5.0, 0.0022, 3)
        cutter = _new_mesh_object(f"M03A_CUT_Bot_{i}", mesh, cutters_coll)
        cutter.location = (0.0, y, -(HG_HALF_H - WALL * 0.2))
        bpy.context.view_layer.update()
        _boolean(outer, cutter, "DIFFERENCE")
        _delete_object(cutter)

    outer.name = "M03A_Handguard"
    return outer


def build_top_rail(fwd) -> bpy.types.Object:
    body_z0 = HG_HALF_H - 0.0012
    body_z1 = body_z0 + RAIL_BASE_H
    half_w = RAIL_BASE_W * 0.5

    # Continuous rail body
    rail = _box("M03A_TopRail", -half_w, half_w, 0.001, HG_LEN - 0.001, body_z0, body_z1, fwd)

    # Side rails continuous under teeth
    wall = RAIL_SIDE_WALL
    left_w = _box(
        "M03A_RailSide_L",
        -half_w,
        -half_w + wall,
        0.001,
        HG_LEN - 0.001,
        body_z1 - 0.0003,
        body_z1 + RAIL_TOOTH_H * 0.4,
        fwd,
    )
    right_w = _box(
        "M03A_RailSide_R",
        half_w - wall,
        half_w,
        0.001,
        HG_LEN - 0.001,
        body_z1 - 0.0003,
        body_z1 + RAIL_TOOTH_H * 0.4,
        fwd,
    )
    _boolean(rail, left_w, "UNION")
    _boolean(rail, right_w, "UNION")
    _delete_object(left_w)
    _delete_object(right_w)

    # Teeth on continuous body
    tooth_half = RAIL_TOOTH_W * 0.5
    d_half = RAIL_TOOTH_D * 0.5
    y = 0.007
    n = 0
    while y + tooth_half < HG_LEN - 0.005:
        tooth = _box(
            f"M03A_RailTooth_{n}",
            -d_half,
            d_half,
            y - tooth_half,
            y + tooth_half,
            body_z1,
            body_z1 + RAIL_TOOTH_H,
            fwd,
        )
        _boolean(rail, tooth, "UNION")
        _delete_object(tooth)
        y += RAIL_TOOTH_PITCH
        n += 1

    rail.name = "M03A_TopRail"
    return rail


def build_barrel(fwd, cutters_coll):
    barrel = _cylinder_y("M03A_Barrel", BARREL_R, BARREL_START, BARREL_END, 32, fwd)
    bore = _cylinder_y("M03A_CUT_BarrelBore", BARREL_INNER_R, BARREL_START - 0.01, BARREL_END + 0.01, 24, cutters_coll)
    _boolean(barrel, bore, "DIFFERENCE")
    _delete_object(bore)

    gas = _cylinder_y(
        "M03A_GasBlock",
        GAS_BLOCK_R,
        GAS_BLOCK_Y - GAS_BLOCK_LEN * 0.5,
        GAS_BLOCK_Y + GAS_BLOCK_LEN * 0.5,
        16,
        fwd,
        radius2=GAS_BLOCK_R * 0.95,
    )
    return barrel, gas


def build_muzzle(fwd, cutters_coll) -> bpy.types.Object:
    """PROJECT_PROVISIONAL_OPEN_TINE_MUZZLE"""
    y0 = BARREL_END - 0.002
    y1 = y0 + MUZZLE_BASE_LEN
    y2 = y1 + MUZZLE_TINE_LEN

    base = _cylinder_y("M03A_Muzzle_ProvisionalOpenTine", MUZZLE_OUTER_R * 0.92, y0, y1, 40, fwd, radius2=MUZZLE_OUTER_R)

    # Tine shell tube
    shell = _cylinder_y("M03A_MuzzleTineShell", MUZZLE_OUTER_R, y1 - 0.001, y2, 40, fwd, radius2=MUZZLE_OUTER_R * 0.97)
    hollow = _cylinder_y("M03A_CUT_MuzzleHollow", MUZZLE_INNER_R, y1 - 0.005, y2 + 0.005, 32, cutters_coll)
    _boolean(shell, hollow, "DIFFERENCE")
    _delete_object(hollow)

    # Radial gap cutters for open tines
    gap = math.radians(TINE_GAP_DEG)
    sector = (2.0 * math.pi) / TINE_COUNT
    for i in range(TINE_COUNT):
        angle = i * sector + sector * 0.5
        # thin radial slab
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        gap_w = MUZZLE_OUTER_R * 2.2 * math.sin(gap * 0.5)
        for v in bm.verts:
            v.co.x *= MUZZLE_OUTER_R * 2.5
            v.co.y *= (MUZZLE_TINE_LEN + 0.012)
            v.co.z *= max(0.004, gap_w * 2.0)
        bmesh.ops.translate(bm, verts=list(bm.verts), vec=(MUZZLE_OUTER_R * 0.5, 0, 0))
        bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(angle, 3, "Y"))
        bmesh.ops.translate(bm, verts=list(bm.verts), vec=(0, (y1 + y2) * 0.5, 0))
        mesh = bpy.data.meshes.new(f"M03A_CUT_TineGap_{i}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        cutter = _new_mesh_object(f"M03A_CUT_TineGap_{i}", mesh, cutters_coll)
        _boolean(shell, cutter, "DIFFERENCE")
        _delete_object(cutter)

    _boolean(base, shell, "UNION")
    _delete_object(shell)

    # Continuous bore
    bore = _cylinder_y("M03A_CUT_MuzzleBore", MUZZLE_BORE_R, y0 - 0.005, y2 + 0.005, 24, cutters_coll)
    _boolean(base, bore, "DIFFERENCE")
    _delete_object(bore)

    base.name = "M03A_Muzzle_ProvisionalOpenTine"
    return base


def build_qd(fwd, cutters_coll):
    # Disc on left face
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=32, radius=QD_R)
    res = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=verts, vec=(-QD_DEPTH, 0, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("M03A_SideSocket_QD_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    qd = _new_mesh_object("M03A_SideSocket_QD", mesh, fwd)
    qd.location = (-(HG_HALF_W + 0.0004), QD_Y, QD_Z)

    # Recess
    recess = _cylinder_y("M03A_CUT_QD", QD_R * 0.55, -0.01, 0.01, 24, cutters_coll)
    # orient along X — recreate as X-axis cylinder
    _delete_object(recess)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=QD_R * 0.55, radius2=QD_R * 0.55, depth=QD_DEPTH * 1.6)
    bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    mesh = bpy.data.meshes.new("M03A_CUT_QD_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    recess = _new_mesh_object("M03A_CUT_QD", mesh, cutters_coll)
    recess.location = (-(HG_HALF_W + 0.0004) - 0.001, QD_Y, QD_Z)
    bpy.context.view_layer.update()
    _boolean(qd, recess, "DIFFERENCE")
    _delete_object(recess)

    # Button
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=QD_R * 0.22)
    mesh = bpy.data.meshes.new("M03A_SideSocket_Button_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    btn = _new_mesh_object("M03A_SideSocket_Button", mesh, fwd)
    btn.location = (-(HG_HALF_W + 0.0008), QD_Y, QD_Z)
    btn.scale = (0.35, 1.0, 1.0)
    _apply_scale_rot(btn)
    return qd, btn


def create_materials() -> dict:
    mats = {}

    def principled(name, color, metallic, roughness):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        out.location = (500, 0)
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        noise = nodes.new("ShaderNodeTexNoise")
        noise.location = (-350, -120)
        noise.inputs["Scale"].default_value = 90.0
        noise.inputs["Detail"].default_value = 8.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.location = (-100, -120)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (min(1.0, roughness + 0.12),) * 3 + (1,)
        ramp.color_ramp.elements[1].position = 0.75
        ramp.color_ramp.elements[1].color = (max(0.05, roughness - 0.1),) * 3 + (1,)
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
        # slight edge lighten for FDE
        if "FDE" in name:
            lw = nodes.new("ShaderNodeLayerWeight")
            lw.location = (-350, 100)
            lw.inputs["Blend"].default_value = 0.38
            mix = nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.location = (0, 80)
            mix.inputs["A"].default_value = (*color, 1.0)
            mix.inputs["B"].default_value = (0.55, 0.48, 0.38, 1.0)
            links.new(lw.outputs["Facing"], mix.inputs["Factor"])
            links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        return mat

    mats["fde"] = principled("M03A_MAT_FDE_AnodizedAlu", (0.36, 0.27, 0.175), 0.68, 0.46)
    mats["steel"] = principled("M03A_MAT_DarkPhosSteel", (0.045, 0.045, 0.048), 0.88, 0.48)
    mats["qd"] = principled("M03A_MAT_QD_Dark", (0.03, 0.03, 0.032), 0.35, 0.55)
    return mats


def create_sockets(fwd) -> list[str]:
    names = []
    specs = [
        ("SOCKET_M03A_Receiver_Interface", (0.0, 0.0, 0.0)),
        ("SOCKET_M03A_Muzzle", (0.0, BARREL_END + MUZZLE_BASE_LEN + MUZZLE_TINE_LEN, 0.0)),
        ("SOCKET_M03A_TopRail_Origin", (0.0, 0.0, HG_HALF_H + RAIL_BASE_H)),
    ]
    for name, loc in specs:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "ARROWS"
        empty.empty_display_size = 0.02
        empty.location = loc
        _link(empty, fwd)
        names.append(name)
    return names


def setup_scene_and_lighting(review):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons.get("cycles")
    # prefer GPU if available
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    try:
        scene.cycles.device = "GPU"
    except Exception:
        pass
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False

    if "M03A_World" in bpy.data.worlds:
        world = bpy.data.worlds["M03A_World"]
    else:
        world = bpy.data.worlds.new("M03A_World")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.18, 0.18, 0.19, 1.0)
    bg.inputs["Strength"].default_value = 0.55
    links.new(bg.outputs["Background"], out.inputs["Surface"])

    # Remove old M03A lights
    for obj in list(bpy.data.objects):
        if obj.type == "LIGHT" and obj.name.startswith("M03A_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    def add_area(name, loc, energy, color, size, rot):
        data = bpy.data.lights.new(name + "_data", type="AREA")
        data.energy = energy
        data.color = color
        data.size = size
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        obj.rotation_euler = rot
        _link(obj, review)
        return obj

    add_area("M03A_Key", (0.35, 0.05, 0.42), 140.0, (1.0, 0.97, 0.93), 0.35, (math.radians(-50), 0, math.radians(40)))
    add_area("M03A_Fill", (-0.42, 0.10, 0.28), 50.0, (0.85, 0.90, 1.0), 0.50, (math.radians(-35), 0, math.radians(-55)))
    add_area("M03A_Rim", (0.05, 0.55, 0.22), 90.0, (1.0, 0.95, 0.90), 0.28, (math.radians(-20), math.radians(180), 0))
    add_area("M03A_Top", (0.0, 0.18, 0.55), 40.0, (1.0, 1.0, 1.0), 0.55, (math.radians(-90), 0, 0))

    if "M03A_ReviewCam" in bpy.data.objects:
        cam = bpy.data.objects["M03A_ReviewCam"]
    else:
        cam_data = bpy.data.cameras.new("M03A_ReviewCam_data")
        cam = bpy.data.objects.new("M03A_ReviewCam", cam_data)
        _link(cam, review)
    cam.data.lens = 50
    cam.data.clip_start = 0.01
    cam.data.clip_end = 20.0
    cam.data.dof.use_dof = False
    scene.camera = cam
    return cam


def _look_at(cam, target: Vector, loc: Vector):
    cam.location = loc
    direction = target - loc
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_reviews(cam) -> list[str]:
    scene = bpy.context.scene
    target = Vector((0.0, HG_LEN * 0.50, 0.005))
    paths = []

    # Full-assembly framing (handguard + barrel + provisional muzzle in frame)
    shots = [
        ("stageA_left_oblique.png", Vector((-0.28, HG_LEN * 0.22, 0.14)), 45, target),
        ("stageA_right_oblique.png", Vector((0.28, HG_LEN * 0.22, 0.14)), 45, target),
        ("stageA_top_mechanical.png", Vector((-0.22, HG_LEN * 0.45, 0.30)), 50, target),
        (
            "stageA_reference_match.png",
            Vector((-0.07, -0.04, 0.045)),
            30,
            Vector((0.0, HG_LEN * 0.85, 0.012)),
        ),
    ]

    for fname, loc, lens, tgt in shots:
        # Pull camera back so complete forward assembly stays in frame with margin
        dir_vec = loc - tgt
        if dir_vec.length < 1e-6:
            dir_vec = Vector((0.2, -0.2, 0.15))
        loc = tgt + dir_vec.normalized() * max(0.34, dir_vec.length)
        cam.data.lens = lens
        _look_at(cam, tgt, loc)
        out_path = ATTEMPT_DIR / fname
        scene.render.filepath = str(out_path)
        bpy.ops.render.render(write_still=True)
        paths.append(str(out_path))
        print(f"RENDERED {out_path}")
    return paths


def count_stats() -> dict:
    mesh_objs = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith("M03A_") and "CUT" not in o.name
    ]
    tris = 0
    for o in mesh_objs:
        m = o.data
        m.calc_loop_triangles()
        tris += len(m.loop_triangles)
    return {
        "production_mesh_objects": len(mesh_objs),
        "object_names": sorted(o.name for o in mesh_objs),
        "triangle_count": tris,
        "material_names": sorted(m.name for m in bpy.data.materials if m.name.startswith("M03A_MAT_")),
        "socket_names": sorted(o.name for o in bpy.data.objects if o.name.startswith("SOCKET_M03A_")),
        "total_objects": len(
            [o for o in bpy.data.objects if o.name.startswith("M03A_") or o.name.startswith("SOCKET_M03A_")]
        ),
    }


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(stats: dict, render_paths: list[str], blender_version: str) -> Path:
    artifacts = []
    candidates = [BLEND_PATH, SOURCE_DIR / "build_core_rifle_method03_stageA.py"]
    candidates += [Path(p) for p in render_paths]
    for p in candidates:
        if p.exists():
            role = "blend_source"
            if p.suffix == ".py":
                role = "construction_script"
            elif p.suffix == ".png":
                role = "review_render"
            artifacts.append(
                {
                    "role": role,
                    "path": str(p.relative_to(ROOT)),
                    "bytes": p.stat().st_size,
                    "sha256": file_sha256(p),
                }
            )

    manifest = {
        "gate": "core-rifle-method03-stageA",
        "stage": "A",
        "attempt": "stage_A_attempt_01",
        "method": "artist_grade_method_03_grok_staged",
        "blender_version": blender_version,
        "units": "meters",
        "axis": "+Y_muzzle_forward",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": [
            "free-float ventilated handguard",
            "continuous integrated top Picatinny rail",
            "dark barrel through real openings",
            "PROJECT_PROVISIONAL_OPEN_TINE_MUZZLE",
            "circular side QD/attachment socket",
        ],
        "excluded_from_stage": [
            "receiver",
            "stock",
            "magazine",
            "pistol_grip",
            "sights",
            "optics",
            "hands",
            "markings",
        ],
        "object_counts": {
            "production_mesh_objects": stats["production_mesh_objects"],
            "total_named_objects": stats["total_objects"],
            "triangle_count": stats["triangle_count"],
        },
        "object_names": stats["object_names"],
        "material_names": stats["material_names"],
        "socket_names": stats["socket_names"],
        "render_dimensions": {"width": 2560, "height": 1440},
        "reference_files_used": REFERENCE_CROPS,
        "identity_boundary": (
            "AR/M4-pattern free-float ventilated handguard; exact manufacturer unresolved; "
            "muzzle is PROJECT_PROVISIONAL_OPEN_TINE_MUZZLE"
        ),
        "artifacts": artifacts,
    }
    man_path = ATTEMPT_DIR / "stageA_artifact_manifest.json"
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {man_path}")
    return man_path


def write_handoff(classification: str, stats: dict, render_paths: list[str], notes: list[str]) -> Path:
    handoff = {
        "project": "Skyguard52",
        "asset": "core-rifle",
        "method": "artist_grade_method_03_grok_staged",
        "stage": "A",
        "attempt": "stage_A_attempt_01",
        "classification": classification,
        "classification_allowed_values": [
            "PASSED_STAGE_A_AWAITING_CODEX_VISUAL_REVIEW",
            "FAILED_STAGE_A_WITH_EVIDENCE",
        ],
        "not_claimed": [
            "AAA",
            "final",
            "Unreal-ready",
            "production-accepted",
            "exact manufacturer identity",
        ],
        "muzzle_identity": "PROJECT_PROVISIONAL_OPEN_TINE_MUZZLE",
        "blend_path": str(BLEND_PATH.relative_to(ROOT)),
        "source_script": str((SOURCE_DIR / "build_core_rifle_method03_stageA.py").relative_to(ROOT)),
        "renders": [str(Path(p).relative_to(ROOT)) for p in render_paths],
        "manifest": str((ATTEMPT_DIR / "stageA_artifact_manifest.json").relative_to(ROOT)),
        "stats": stats,
        "self_review_notes": notes,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "next_step": "Codex direct visual inspection of Stage A renders and geometry",
    }
    path = ATTEMPT_DIR / "grok_method03_stageA_handoff.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2)
    print(f"Wrote {path}")
    return path


def reset_scene() -> None:
    # Delete all objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Purge data blocks
    for coll in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.curves,
    ):
        for block in list(coll):
            try:
                coll.remove(block)
            except Exception:
                pass
    for c in list(bpy.data.collections):
        try:
            bpy.data.collections.remove(c)
        except Exception:
            pass


def build_all(do_render: bool = True) -> dict:
    _ensure_dir(SOURCE_DIR)
    _ensure_dir(ATTEMPT_DIR)
    _ensure_dir(OUTPUT_DIR)

    reset_scene()

    fwd = _get_or_create_collection("M03A_FORWARD_ASSEMBLY")
    review = _get_or_create_collection("M03A_REVIEW")
    cutters_coll = _get_or_create_collection("M03A_CUTTERS_TMP", parent=fwd)
    cutters_coll.hide_render = True
    cutters_coll.hide_viewport = True

    mats = create_materials()

    print("Building handguard...")
    hg = build_handguard(fwd, cutters_coll)
    print("Building top rail...")
    rail = build_top_rail(fwd)
    _boolean(hg, rail, "UNION")
    _delete_object(rail)
    hg.name = "M03A_Handguard_WithRail"

    print("Building barrel...")
    barrel, gas = build_barrel(fwd, cutters_coll)
    print("Building muzzle...")
    muzzle = build_muzzle(fwd, cutters_coll)
    print("Building QD socket...")
    qd, btn = build_qd(fwd, cutters_coll)

    # Assign materials
    for obj, matkey in (
        (hg, "fde"),
        (barrel, "steel"),
        (gas, "steel"),
        (muzzle, "steel"),
        (qd, "qd"),
        (btn, "qd"),
    ):
        obj.data.materials.clear()
        obj.data.materials.append(mats[matkey])

    print("Bevel / smooth...")
    for obj, w in (
        (hg, 0.00028),
        (barrel, 0.00014),
        (gas, 0.00018),
        (muzzle, 0.00022),
        (qd, 0.00018),
        (btn, 0.00012),
    ):
        _apply_scale_rot(obj)
        _shade_and_bevel(obj, width=w, segments=2)

    sockets = create_sockets(fwd)
    cam = setup_scene_and_lighting(review)

    print(f"Saving blend {BLEND_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    render_paths = []
    if do_render:
        print("Rendering reviews...")
        render_paths = render_reviews(cam)
        bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    stats = count_stats()
    stats["socket_names"] = sockets
    blender_version = bpy.app.version_string
    write_manifest(stats, render_paths, blender_version)

    result = {
        "stats": stats,
        "renders": render_paths,
        "blend": str(BLEND_PATH),
        "blender_version": blender_version,
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    build_all(do_render=True)
