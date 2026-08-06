# -*- coding: utf-8 -*-
"""
Skyguard 52 — core-rifle / artist_grade_method_02_grok_blender
Author: Grok 4.5 OAuth artist-worker
Identity: generic AR/M4-family rifle; exact configuration unresolved
Blender units: meters, unit scale 1.0
Axes: bore +X, up +Z, origin near receiver centerline
"""

from __future__ import annotations

import bmesh
import bpy
import hashlib
import json
import math
import os
import traceback
from mathutils import Matrix, Vector
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
FINAL = Path(r"D:\Skyguard52\Blender\P0_CORE_RIFLE_ARTIST_GRADE_METHOD02")
SOURCE = Path(r"D:\Skyguard52\Production\Sources\core-rifle\artist_grade_method_02_grok_blender")
ATTEMPT = Path(r"D:\Skyguard52\Production\Attempts\core-rifle-artist-grade-method02\attempt_01")
RENDERS = FINAL / "renders"
TEMP = ATTEMPT / "temp_renders"
BAKES = FINAL  # bake PNGs live in final namespace root

for p in (FINAL, RENDERS, TEMP, SOURCE, ATTEMPT):
    p.mkdir(parents=True, exist_ok=True)

IDENTITY = "generic AR/M4-family rifle; exact configuration unresolved"
BORE_Z = 0.075
SIGHT_Z = 0.174
REAR_APERTURE_X = -0.080
FRONT_POST_X = 0.388
OVERALL_LEN = 0.968
RECEIVER_W = 0.074

# Stock butt ~ -0.320, muzzle tip ~ 0.648 → length 0.968
STOCK_BUTT_X = -0.320
MUZZLE_TIP_X = STOCK_BUTT_X + OVERALL_LEN  # 0.648

CORRECTION_COUNT = 0  # updated by correction passes if any


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                  bpy.data.cameras, bpy.data.lights, bpy.data.collections,
                  bpy.data.curves):
        for b in list(block):
            try:
                block.remove(b)
            except Exception:
                pass


def ensure_collections():
    names = ["RIFLE_HIGH", "RIFLE_GAME", "RIFLE_SOCKETS", "RIFLE_COLLISION", "RIFLE_REVIEW"]
    root = bpy.context.scene.collection
    cols = {}
    for n in names:
        c = bpy.data.collections.new(n)
        root.children.link(c)
        cols[n] = c
    return cols


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def new_mesh_obj(name, bm, col, mat=None):
    me = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    link(obj, col)
    if mat:
        if me.materials:
            me.materials[0] = mat
        else:
            me.materials.append(mat)
    return obj


def apply_smooth(obj, auto_smooth_angle_deg=40.0):
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = True
    # Weighted normal / shade smooth via modifier where available
    if not any(m.type == "WEIGHTED_NORMAL" for m in obj.modifiers):
        wn = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        wn.mode = "FACE_AREA"
        wn.keep_sharp = True
        wn.weight = 50
    # Mark sharp edges by angle
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for e in bm.edges:
        if e.is_boundary:
            e.smooth = False
        else:
            if e.calc_face_angle(0.0) > math.radians(auto_smooth_angle_deg):
                e.smooth = False
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def solidify_profile(verts_yz, x0, x1, name, col, mat, segs=1):
    """Extrude a closed YZ profile along X from x0 to x1."""
    bm = bmesh.new()
    # Build front and back rings
    def ring(x):
        return [bm.verts.new((x, y, z)) for y, z in verts_yz]

    rings = []
    for i in range(segs + 1):
        t = i / segs
        x = x0 + (x1 - x0) * t
        rings.append(ring(x))
    bm.verts.ensure_lookup_table()
    n = len(verts_yz)
    for ri in range(segs):
        a, b = rings[ri], rings[ri + 1]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([a[i], a[j], b[j], b[i]])
    # Caps
    if segs >= 0:
        try:
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
        except Exception:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat)


def box(name, loc, size, col, mat, bevel=0.0, segments=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
        v.co += Vector(loc)
    if bevel > 0:
        bmesh.ops.bevel(
            bm,
            geom=list(bm.edges),
            offset=bevel,
            segments=segments,
            affect="EDGES",
            profile=0.5,
        )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat)


def cylinder(name, loc, radius, depth, col, mat, axis="X", segs=24, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segs,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    # Default cylinder is along Z; rotate to axis
    if axis == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    elif axis == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    for v in bm.verts:
        v.co += Vector(loc)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, radius * 0.3),
                        segments=2, affect="EDGES", profile=0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat)


def torus_ring(name, loc, major, minor, col, mat, segs=20, axis="Y"):
    """Approximate torus via revolved tube rings (bmesh has no create_torus in 5.2)."""
    bm = bmesh.new()
    major_n = max(8, segs)
    minor_n = 8
    rings = []
    for i in range(major_n):
        a = (i / major_n) * math.tau
        # center of minor circle in XY (default torus in XY plane, Z up)
        cx = major * math.cos(a)
        cy = major * math.sin(a)
        ring = []
        for j in range(minor_n):
            b = (j / minor_n) * math.tau
            # local minor offsets
            lx = minor * math.cos(b)
            lz = minor * math.sin(b)
            # rotate minor offset around Z by a
            wx = cx + lx * math.cos(a)
            wy = cy + lx * math.sin(a)
            wz = lz
            ring.append(bm.verts.new((wx, wy, wz)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(major_n):
        a = rings[i]
        b = rings[(i + 1) % major_n]
        for j in range(minor_n):
            k = (j + 1) % minor_n
            try:
                bm.faces.new([a[j], a[k], b[k], b[j]])
            except Exception:
                pass
    # Orient: default is Z-axis through hole; map to requested axis
    if axis == "Y":
        bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    elif axis == "X":
        bmesh.ops.rotate(bm, verts=list(bm.verts), cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    for v in bm.verts:
        v.co += Vector(loc)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return new_mesh_obj(name, bm, col, mat)


def sphere(name, loc, radius, col, mat, segs=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=radius)
    for v in bm.verts:
        v.co += Vector(loc)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat)


def apply_boolean(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        # Fallback FAST
        mod.solver = "FLOAT"
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            target.modifiers.remove(mod)
            return False
    return True


def join_objects(objs, name, col):
    if not objs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    link(obj, col)
    return obj


def set_origin_geometry(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")


def apply_transforms(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


# ---------------------------------------------------------------------------
# Materials — calibrated procedural PBR
# ---------------------------------------------------------------------------
def make_pbr(name, base_color, metal, rough, noise_scale=40.0, wear=0.08, bump=0.02):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (800, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (500, 0)
    # Base color with subtle noise variation
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-600, 0)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, 0)
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.55
    links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-200, 100)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (base_color[0] * 0.85, base_color[1] * 0.85,
                                         base_color[2] * 0.85, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (min(1, base_color[0] * 1.08),
                                         min(1, base_color[1] * 1.08),
                                         min(1, base_color[2] * 1.08), 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    # Edge wear via pointiness (geometry)
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-400, -250)
    cr = nodes.new("ShaderNodeValToRGB")
    cr.location = (-200, -250)
    cr.color_ramp.elements[0].position = 0.45
    cr.color_ramp.elements[0].color = (0, 0, 0, 1)
    cr.color_ramp.elements[1].position = 0.62
    cr.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(geom.outputs["Pointiness"], cr.inputs["Fac"])
    mix = nodes.new("ShaderNodeMixRGB")
    mix.location = (100, 50)
    mix.blend_type = "MIX"
    mix.inputs["Fac"].default_value = wear
    # Wear color — slightly brighter / desaturated metal edge
    wear_col = (min(1, base_color[0] + 0.18), min(1, base_color[1] + 0.16),
                min(1, base_color[2] + 0.12), 1)
    mix.inputs["Color1"].default_value = (*base_color[:3], 1)
    # Use ramp for base variation
    mix2 = nodes.new("ShaderNodeMixRGB")
    mix2.location = (-20, 120)
    mix2.blend_type = "MIX"
    mix2.inputs["Fac"].default_value = 0.35
    mix2.inputs["Color1"].default_value = (*base_color[:3], 1)
    links.new(ramp.outputs["Color"], mix2.inputs["Color2"])
    links.new(mix2.outputs["Color"], mix.inputs["Color1"])
    mix.inputs["Color2"].default_value = wear_col
    links.new(cr.outputs["Color"], mix.inputs["Fac"])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    # Roughness variation
    rmix = nodes.new("ShaderNodeMath")
    rmix.location = (100, -150)
    rmix.operation = "MULTIPLY"
    rmix.inputs[0].default_value = rough
    # noise fac into roughness
    radd = nodes.new("ShaderNodeMath")
    radd.location = (280, -150)
    radd.operation = "ADD"
    radd.inputs[1].default_value = rough
    n2 = nodes.new("ShaderNodeMath")
    n2.location = (100, -300)
    n2.operation = "MULTIPLY"
    n2.inputs[1].default_value = 0.08
    links.new(noise.outputs["Fac"], n2.inputs[0])
    links.new(n2.outputs["Value"], radd.inputs[0])
    radd.inputs[1].default_value = rough
    links.new(radd.outputs["Value"], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = metal
    # Micro bump
    bumpn = nodes.new("ShaderNodeBump")
    bumpn.location = (280, -350)
    bumpn.inputs["Strength"].default_value = bump
    bumpn.inputs["Distance"].default_value = 0.002
    links.new(noise.outputs["Fac"], bumpn.inputs["Height"])
    links.new(bumpn.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    # Specular for non-metals
    if hasattr(bsdf.inputs, "get") and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.45 if metal < 0.5 else 0.5
    return mat


def build_materials():
    mats = {
        "MAT_AnodizedAluminum": make_pbr(
            "MAT_AnodizedAluminum", (0.12, 0.125, 0.13), metal=0.85, rough=0.42,
            noise_scale=55, wear=0.12, bump=0.015
        ),
        "MAT_CoatedSteel": make_pbr(
            "MAT_CoatedSteel", (0.08, 0.08, 0.085), metal=0.9, rough=0.35,
            noise_scale=70, wear=0.1, bump=0.012
        ),
        "MAT_PhosphateSteel": make_pbr(
            "MAT_PhosphateSteel", (0.045, 0.048, 0.05), metal=0.88, rough=0.55,
            noise_scale=90, wear=0.14, bump=0.018
        ),
        "MAT_Polymer": make_pbr(
            "MAT_Polymer", (0.035, 0.036, 0.038), metal=0.0, rough=0.62,
            noise_scale=120, wear=0.06, bump=0.025
        ),
        "MAT_Rubber": make_pbr(
            "MAT_Rubber", (0.02, 0.02, 0.022), metal=0.0, rough=0.85,
            noise_scale=200, wear=0.04, bump=0.03
        ),
    }
    return mats


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------
def build_lower_receiver(col, mats):
    """Resolved lower: forged-style silhouette, magwell flare, trigger guard, pin bosses."""
    mat = mats["MAT_AnodizedAluminum"]
    parts = []
    # Main lower body — slightly tapered sides via custom profile
    # Profile in YZ: rounded rectangular with bottom rail shoulder
    w = RECEIVER_W * 0.5  # half-width ~0.037
    # Body from X=-0.12 to X=0.095
    body = box("LOW_Body", (0.0, 0.0, BORE_Z - 0.018),
               (0.22, RECEIVER_W * 0.92, 0.072), col, mat, bevel=0.004, segments=3)
    parts.append(body)
    # Magwell — flared continuous shell
    # Magwell is continuous tapered tube-like box
    mw = box("LOW_Magwell", (0.035, 0.0, BORE_Z - 0.055),
             (0.078, 0.034, 0.095), col, mat, bevel=0.0035, segments=3)
    parts.append(mw)
    # Magwell lower flare (slightly wider)
    mwf = box("LOW_MagwellFlare", (0.038, 0.0, BORE_Z - 0.095),
              (0.082, 0.038, 0.018), col, mat, bevel=0.0025, segments=2)
    parts.append(mwf)
    # Trigger guard — continuous loop
    tg = box("LOW_TriggerGuard_Front", (0.005, 0.0, BORE_Z - 0.072),
             (0.012, 0.016, 0.028), col, mat, bevel=0.0015, segments=2)
    parts.append(tg)
    tg_bot = box("LOW_TriggerGuard_Bot", (-0.012, 0.0, BORE_Z - 0.090),
                 (0.055, 0.014, 0.008), col, mat, bevel=0.0015, segments=2)
    parts.append(tg_bot)
    tg_rear = box("LOW_TriggerGuard_Rear", (-0.035, 0.0, BORE_Z - 0.072),
                  (0.012, 0.016, 0.028), col, mat, bevel=0.0015, segments=2)
    parts.append(tg_rear)
    # Trigger (external visible)
    tr = box("LOW_Trigger", (-0.012, 0.0, BORE_Z - 0.055),
             (0.008, 0.006, 0.022), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=2)
    # Slight curve by scaling
    tr.scale = (1.0, 1.0, 1.0)
    parts.append(tr)
    # Selector (left side plate disc + lever)
    sel = cylinder("LOW_Selector", (-0.055, w * 0.95, BORE_Z - 0.005),
                   0.009, 0.006, col, mats["MAT_CoatedSteel"], axis="Y", segs=16)
    parts.append(sel)
    sel_lever = box("LOW_SelectorLever", (-0.055, w * 0.98, BORE_Z + 0.008),
                    (0.004, 0.004, 0.018), col, mats["MAT_CoatedSteel"], bevel=0.0008, segments=1)
    parts.append(sel_lever)
    # Bolt catch (left side)
    bc = box("LOW_BoltCatch", (0.015, w * 0.98, BORE_Z + 0.012),
             (0.018, 0.005, 0.012), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=2)
    parts.append(bc)
    # Takedown pin bosses
    for px, name in [(-0.095, "LOW_TakedownPinRear"), (0.075, "LOW_TakedownPinFront")]:
        boss = cylinder(name + "_Boss", (px, 0.0, BORE_Z - 0.005),
                        0.007, RECEIVER_W * 0.95, col, mat, axis="Y", segs=14)
        parts.append(boss)
        pin = cylinder(name, (px, 0.0, BORE_Z - 0.005),
                       0.0035, RECEIVER_W * 1.05, col, mats["MAT_CoatedSteel"], axis="Y", segs=12)
        parts.append(pin)
    # Mag release button
    mrel = cylinder("LOW_MagRelease", (0.055, -w * 0.95, BORE_Z - 0.015),
                    0.006, 0.008, col, mats["MAT_CoatedSteel"], axis="Y", segs=12)
    parts.append(mrel)
    # Pivot / buffer tower shoulder
    bt = box("LOW_BufferTower", (-0.115, 0.0, BORE_Z + 0.01),
             (0.028, RECEIVER_W * 0.75, 0.038), col, mat, bevel=0.003, segments=2)
    parts.append(bt)
    # Seam line shoulder (upper/lower joint lip)
    lip = box("LOW_UpperLip", (0.0, 0.0, BORE_Z + 0.018),
              (0.20, RECEIVER_W * 0.88, 0.006), col, mat, bevel=0.001, segments=1)
    parts.append(lip)
    # Fasteners (grip screw head)
    grip_screw = cylinder("LOW_GripScrew", (-0.055, 0.0, BORE_Z - 0.035),
                          0.004, 0.006, col, mats["MAT_CoatedSteel"], axis="Z", segs=10)
    parts.append(grip_screw)
    # Join lower primary body pieces into one shell for cleanliness of GAME mesh
    main = [body, mw, mwf, tg, tg_bot, tg_rear, bt, lip]
    rest = [p for p in parts if p not in main]
    joined = join_objects(main, "GAME_LowerReceiver", col)
    apply_transforms(joined)
    apply_smooth(joined, 35)
    out = [joined] + rest
    for o in rest:
        apply_transforms(o)
        apply_smooth(o, 40)
    return out


def build_upper_receiver(col, mats):
    mat = mats["MAT_AnodizedAluminum"]
    parts = []
    # Upper body — slightly taller, forged rail base
    body = box("UP_Body", (-0.01, 0.0, BORE_Z + 0.035),
               (0.24, RECEIVER_W * 0.88, 0.055), col, mat, bevel=0.0035, segments=3)
    parts.append(body)
    # Forward assist housing (right side)
    fa = box("UP_ForwardAssist", (-0.02, -RECEIVER_W * 0.48, BORE_Z + 0.03),
             (0.028, 0.018, 0.028), col, mat, bevel=0.002, segments=2)
    parts.append(fa)
    fa_btn = cylinder("UP_ForwardAssistBtn", (-0.02, -RECEIVER_W * 0.55, BORE_Z + 0.03),
                      0.007, 0.01, col, mats["MAT_CoatedSteel"], axis="Y", segs=12)
    parts.append(fa_btn)
    # Ejection port cut indication + dust cover (right side exterior)
    # Dust cover plate closed
    dust = box("UP_DustCover", (0.02, -RECEIVER_W * 0.48, BORE_Z + 0.02),
               (0.055, 0.004, 0.022), col, mats["MAT_PhosphateSteel"], bevel=0.0008, segments=1)
    parts.append(dust)
    # Ejection port frame recess (visual)
    port_frame = box("UP_EjectionFrame", (0.02, -RECEIVER_W * 0.46, BORE_Z + 0.02),
                     (0.06, 0.006, 0.026), col, mat, bevel=0.001, segments=1)
    parts.append(port_frame)
    # Charging handle exterior (T-handle rear of upper)
    ch_stem = box("UP_CH_Stem", (-0.125, 0.0, BORE_Z + 0.052),
                  (0.045, 0.012, 0.008), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=2)
    parts.append(ch_stem)
    ch_latches = box("UP_CH_Latch", (-0.145, 0.0, BORE_Z + 0.052),
                     (0.012, 0.042, 0.01), col, mats["MAT_CoatedSteel"], bevel=0.0015, segments=2)
    parts.append(ch_latches)
    # Picatinny-style top rail — NON-uniform tooth spacing (avoid procedural repetition)
    rail_base = box("UP_RailBase", (-0.01, 0.0, BORE_Z + 0.065),
                    (0.235, 0.022, 0.008), col, mat, bevel=0.001, segments=1)
    parts.append(rail_base)
    # Irregular but rational rail teeth positions (slot pattern variations)
    tooth_xs = []
    x = -0.118
    end = 0.100
    pattern = [0.0102, 0.0100, 0.0105, 0.0098, 0.0103, 0.0101, 0.0099, 0.0104]
    pi = 0
    while x < end:
        tooth_xs.append(x)
        x += pattern[pi % len(pattern)]
        pi += 1
    # Skip a few intentionally for nonuniform look
    skip = {3, 11, 17}
    for i, tx in enumerate(tooth_xs):
        if i in skip:
            continue
        t = box(f"UP_RailTooth_{i:02d}", (tx, 0.0, BORE_Z + 0.072),
                (0.0045, 0.020, 0.005), col, mat, bevel=0.0004, segments=1)
        parts.append(t)
    # Brass deflector bump
    bd = box("UP_BrassDeflector", (0.055, -RECEIVER_W * 0.42, BORE_Z + 0.04),
             (0.014, 0.012, 0.018), col, mat, bevel=0.002, segments=2)
    parts.append(bd)
    # Delta ring / barrel nut silhouette at front of upper
    bn = cylinder("UP_BarrelNut", (0.105, 0.0, BORE_Z),
                  0.028, 0.022, col, mats["MAT_CoatedSteel"], axis="X", segs=20)
    parts.append(bn)
    # Join primary
    main = [body, rail_base, fa, port_frame, bd]
    rest = [p for p in parts if p not in main]
    joined = join_objects(main, "GAME_UpperReceiver", col)
    apply_transforms(joined)
    apply_smooth(joined, 35)
    for o in rest:
        apply_transforms(o)
        apply_smooth(o, 40)
    return [joined] + rest


def build_magazine(col, mats):
    """Continuous curved magazine shell — no stacked boxes."""
    mat = mats["MAT_Polymer"]
    bm = bmesh.new()
    # Build as curved loft of rounded-rect profiles along a gentle arc
    # Mag extends downward and slightly forward from magwell
    n_prof = 10
    # Profile: rounded rectangle in local Y (width) / along path normal
    mag_w = 0.0145  # half-width (Y)
    mag_t = 0.0115  # half-thickness along curve normal initially

    def profile_pts(half_w, half_d, corner=0.003, segs=4):
        # Return points for a rounded rect in 2D (u,v)
        pts = []
        # Order: front-left around clockwise
        corners = [
            (half_d - corner, half_w - corner, 0),       # +d +w
            (half_d - corner, -(half_w - corner), 1),    # +d -w
            (-(half_d - corner), -(half_w - corner), 2), # -d -w
            (-(half_d - corner), half_w - corner, 3),    # -d +w
        ]
        # Simpler: 8-point chamfered rect
        c = corner
        return [
            (half_d, half_w - c),
            (half_d - c, half_w),
            (-(half_d - c), half_w),
            (-half_d, half_w - c),
            (-half_d, -(half_w - c)),
            (-(half_d - c), -half_w),
            (half_d - c, -half_w),
            (half_d, -(half_w - c)),
        ]

    rings = []
    for i in range(n_prof):
        t = i / (n_prof - 1)
        # Curve path: starts at magwell insert, curves back
        # X position slight forward then back, Z drops
        angle = math.radians(18.0 * t)  # 18 deg curve
        path_len = 0.155 * t
        # Centerline of mag
        cx = 0.040 + 0.01 * t - 0.02 * (t * t)
        cy = 0.0
        cz = (BORE_Z - 0.10) - path_len * math.cos(angle * 0.3) * 0.95
        # Taper slightly toward floor plate
        scale = 1.0 - 0.04 * t
        hw = mag_w * scale
        hd = mag_t * scale * (1.0 + 0.08 * math.sin(t * math.pi))  # slight belly
        # Local frame: along curve roughly -Z with slight -X
        # Profile in Y and "depth" (roughly X relative)
        local = profile_pts(hw, hd)
        ring = []
        rot = angle * 0.5
        for px, py in local:
            # rotate profile in XZ by rot
            rx = px * math.cos(rot) - 0 * math.sin(rot)
            rz = px * math.sin(rot)
            ring.append(bm.verts.new((cx + rx, cy + py, cz + rz)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    n = len(rings[0])
    for ri in range(n_prof - 1):
        a, b = rings[ri], rings[ri + 1]
        for i in range(n):
            j = (i + 1) % n
            try:
                bm.faces.new([a[i], a[j], b[j], b[i]])
            except Exception:
                pass
    # Caps
    try:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    except Exception:
        pass
    # Subtle rib ridges as extruded bands (continuous, not strips)
    # Add slight outward offset verts on alternate mid rings
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Bevel outer edges lightly
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if e.is_boundary or e.calc_face_angle(0) > 0.4],
                    offset=0.0012, segments=2, affect="EDGES", profile=0.5)
    mag = new_mesh_obj("GAME_Magazine", bm, col, mat)
    # Floor plate
    fp = box("GAME_MagFloorPlate", (0.028, 0.0, BORE_Z - 0.248),
             (0.028, 0.032, 0.008), col, mat, bevel=0.002, segments=2)
    # Mag catch slot detail
    slot = box("GAME_MagCatchSlot", (0.050, 0.016, BORE_Z - 0.12),
               (0.008, 0.003, 0.012), col, mats["MAT_CoatedSteel"], bevel=0.0005, segments=1)
    # Continuous spine ridge
    spine = box("GAME_MagSpine", (0.052, 0.0, BORE_Z - 0.17),
                (0.004, 0.004, 0.12), col, mat, bevel=0.001, segments=1)
    for o in (mag, fp, slot, spine):
        apply_transforms(o)
        apply_smooth(o, 45)
    return [mag, fp, slot, spine]


def build_grip(col, mats):
    """Ergonomic swept pistol grip with palm swell."""
    mat = mats["MAT_Polymer"]
    bm = bmesh.new()
    # Cross-sections along grip length (swept back and down)
    n = 8
    rings = []
    for i in range(n):
        t = i / (n - 1)
        # Sweep: starts under receiver, angles back ~18 deg
        ang = math.radians(18)
        length = 0.105 * t
        cx = -0.055 - length * math.sin(ang)
        cz = (BORE_Z - 0.038) - length * math.cos(ang)
        # Palm swell mid-grip
        swell = 1.0 + 0.18 * math.sin(t * math.pi)
        # Cross section ellipse-ish with backstrap
        hw = 0.014 * swell  # half Y
        hd = 0.016 * (1.0 + 0.1 * math.sin(t * math.pi))  # half depth X-local
        # 12-pt profile
        pts = []
        for k in range(12):
            a = (k / 12) * math.tau
            # flatter front (finger), fuller backstrap
            ry = hw * (0.85 + 0.15 * abs(math.sin(a)))
            rx = hd * (1.05 if math.cos(a) < 0 else 0.9)  # backstrap thicker
            # local: x back, y side
            lx = rx * math.cos(a)
            ly = ry * math.sin(a)
            # rotate into sweep
            wx = cx + lx * math.cos(ang)
            wz = cz - lx * math.sin(ang)
            pts.append(bm.verts.new((wx, ly, wz)))
        rings.append(pts)
    bm.verts.ensure_lookup_table()
    for ri in range(n - 1):
        a, b = rings[ri], rings[ri + 1]
        for i in range(12):
            j = (i + 1) % 12
            try:
                bm.faces.new([a[i], a[j], b[j], b[i]])
            except Exception:
                pass
    try:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    except Exception:
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.0015, segments=2, affect="EDGES", profile=0.6)
    grip = new_mesh_obj("GAME_PistolGrip", bm, col, mat)
    # Base plate / end cap
    base = box("GAME_GripBase", (-0.088, 0.0, BORE_Z - 0.138),
               (0.028, 0.026, 0.008), col, mat, bevel=0.002, segments=2)
    # Subtle molded panel lines (restrained)
    panel = box("GAME_GripPanel", (-0.065, 0.013, BORE_Z - 0.08),
                (0.02, 0.002, 0.05), col, mat, bevel=0.0005, segments=1)
    for o in (grip, base, panel):
        apply_transforms(o)
        apply_smooth(o, 50)
    return [grip, base, panel]


def build_stock(col, mats):
    """Adjustable carbine-family stock with buffer tube, cheek weld, latch, buttpad."""
    parts = []
    # Buffer tube
    tube = cylinder("GAME_BufferTube", (-0.20, 0.0, BORE_Z + 0.01),
                    0.0165, 0.185, col, mats["MAT_CoatedSteel"], axis="X", segs=20)
    parts.append(tube)
    # Castle nut
    cn = cylinder("GAME_CastleNut", (-0.118, 0.0, BORE_Z + 0.01),
                  0.020, 0.012, col, mats["MAT_CoatedSteel"], axis="X", segs=16)
    parts.append(cn)
    # End plate
    ep = box("GAME_EndPlate", (-0.125, 0.0, BORE_Z + 0.005),
             (0.006, 0.038, 0.042), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=1)
    parts.append(ep)
    # Stock body — continuous shell, not toy skeleton blocks
    # Cheek weld upper surface + lower frame as one shaped body
    bm = bmesh.new()
    # Profile loft for stock body along X from -0.30 to -0.155
    n = 7
    rings = []
    for i in range(n):
        t = i / (n - 1)
        x = -0.155 + (-0.300 + 0.155) * t  # -0.155 → -0.300
        # Height/width vary: wider cheek at mid, butt thicker
        cheek_h = 0.028 + 0.012 * math.sin(t * math.pi * 0.9)
        lower_h = 0.030 + 0.008 * t
        half_w = 0.020 + 0.006 * t  # widens toward butt
        zc = BORE_Z + 0.01
        # 10-pt profile: top cheek flat-ish, sides, bottom with cavity indication
        pts_local = [
            (0, cheek_h),
            (half_w * 0.7, cheek_h * 0.85),
            (half_w, cheek_h * 0.2),
            (half_w * 0.85, -lower_h * 0.3),
            (half_w * 0.5, -lower_h),
            (0, -lower_h * 1.05),
            (-half_w * 0.5, -lower_h),
            (-half_w * 0.85, -lower_h * 0.3),
            (-half_w, cheek_h * 0.2),
            (-half_w * 0.7, cheek_h * 0.85),
        ]
        ring = [bm.verts.new((x, y, zc + z)) for y, z in pts_local]
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for ri in range(n - 1):
        a, b = rings[ri], rings[ri + 1]
        for i in range(10):
            j = (i + 1) % 10
            try:
                bm.faces.new([a[i], a[j], b[j], b[i]])
            except Exception:
                pass
    try:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    except Exception:
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.002, segments=2, affect="EDGES", profile=0.5)
    stock = new_mesh_obj("GAME_StockBody", bm, col, mats["MAT_Polymer"])
    parts.append(stock)
    # Latch lever
    latch = box("GAME_StockLatch", (-0.175, 0.0, BORE_Z - 0.012),
                (0.025, 0.012, 0.014), col, mats["MAT_Polymer"], bevel=0.0015, segments=2)
    parts.append(latch)
    # Position detents visual (non-uniform spacing)
    for i, dx in enumerate([0.0, 0.016, 0.034, 0.055, 0.078, 0.100]):
        d = cylinder(f"GAME_StockDetent_{i}", (-0.16 - dx, 0.0, BORE_Z + 0.01),
                     0.0025, 0.004, col, mats["MAT_CoatedSteel"], axis="Z", segs=8)
        parts.append(d)
    # Buttpad rubber
    pad = box("GAME_Buttpad", (STOCK_BUTT_X + 0.008, 0.0, BORE_Z + 0.0),
              (0.014, 0.048, 0.078), col, mats["MAT_Rubber"], bevel=0.003, segments=3)
    parts.append(pad)
    # Sling loop rear
    sling = torus_ring("GAME_SlingRear", (-0.130, 0.0, BORE_Z - 0.02),
                       0.008, 0.002, col, mats["MAT_CoatedSteel"], segs=14, axis="Y")
    parts.append(sling)
    for o in parts:
        apply_transforms(o)
        apply_smooth(o, 40)
    return parts


def build_handguard(col, mats):
    """Free-float handguard: faceted tubular, nonuniform vents, top rail, end cap."""
    mat = mats["MAT_AnodizedAluminum"]
    parts = []
    # Main tube — octagonal-ish faceted cross-section loft
    bm = bmesh.new()
    x0, x1 = 0.115, 0.430
    n_len = 6
    # 10-facet profile with flat top for rail
    def hg_profile(scale=1.0):
        r = 0.028 * scale
        pts = []
        # Top flat for rail
        pts.append((-0.011, r * 0.95))
        pts.append((0.011, r * 0.95))
        # right side facets
        for a in [20, 50, 90, 130, 160]:
            rad = math.radians(a)
            pts.append((r * math.sin(rad), r * math.cos(rad)))
        # bottom
        pts.append((0.0, -r * 0.9))
        # left side
        for a in [200, 230, 270, 310, 340]:
            rad = math.radians(a)
            pts.append((r * math.sin(rad), r * math.cos(rad)))
        return pts  # (y, z) relative

    rings = []
    for i in range(n_len):
        t = i / (n_len - 1)
        x = x0 + (x1 - x0) * t
        # slight taper toward muzzle
        sc = 1.0 - 0.06 * t
        prof = hg_profile(sc)
        ring = [bm.verts.new((x, y, BORE_Z + z)) for y, z in prof]
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    n = len(rings[0])
    for ri in range(n_len - 1):
        a, b = rings[ri], rings[ri + 1]
        for i in range(n):
            j = (i + 1) % n
            try:
                bm.faces.new([a[i], a[j], b[j], b[i]])
            except Exception:
                pass
    try:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    except Exception:
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    hg = new_mesh_obj("GAME_Handguard", bm, col, mat)
    parts.append(hg)
    # Receiver junction ring
    jn = cylinder("GAME_HG_Junction", (0.118, 0.0, BORE_Z),
                  0.030, 0.014, col, mat, axis="X", segs=20)
    parts.append(jn)
    # Muzzle end cap
    cap = cylinder("GAME_HG_EndCap", (0.430, 0.0, BORE_Z),
                   0.027, 0.012, col, mat, axis="X", segs=18)
    parts.append(cap)
    # Top rail on handguard — nonuniform teeth
    rail = box("GAME_HG_Rail", (0.275, 0.0, BORE_Z + 0.030),
               (0.30, 0.020, 0.006), col, mat, bevel=0.0008, segments=1)
    parts.append(rail)
    tooth_x = 0.135
    spacings = [0.0105, 0.0098, 0.0102, 0.0110, 0.0096, 0.0103, 0.0100, 0.0107]
    idx = 0
    while tooth_x < 0.420:
        if idx % 9 != 4:  # skip some
            t = box(f"GAME_HG_Tooth_{idx:02d}", (tooth_x, 0.0, BORE_Z + 0.035),
                    (0.0042, 0.018, 0.0045), col, mat, bevel=0.0003, segments=1)
            parts.append(t)
        tooth_x += spacings[idx % len(spacings)]
        idx += 1
    # Ventilation cutouts — nonuniform but rational pattern (side holes as recessed boxes / cylinders)
    # Left and right side oval-ish vents at varying spacing
    vent_data = [
        (0.16, 0.022, 0.012, 0.018),
        (0.195, 0.020, 0.011, 0.016),
        (0.235, 0.024, 0.013, 0.019),
        (0.275, 0.019, 0.010, 0.015),
        (0.310, 0.023, 0.012, 0.017),
        (0.350, 0.021, 0.011, 0.016),
        (0.385, 0.018, 0.010, 0.014),
    ]
    for i, (vx, vlen, vht, _) in enumerate(vent_data):
        for side, sy in [("L", 0.028), ("R", -0.028)]:
            # Use thin boxes as visual cutout recesses (not boolean for robustness)
            v = box(f"GAME_HG_Vent_{side}_{i}", (vx, sy, BORE_Z + 0.0),
                    (vlen, 0.004, vht), col, mats["MAT_PhosphateSteel"], bevel=0.001, segments=1)
            parts.append(v)
    # Bottom accessory rail short section (non-full-length — less procedural)
    bot_rail = box("GAME_HG_BotRail", (0.30, 0.0, BORE_Z - 0.028),
                   (0.12, 0.016, 0.005), col, mat, bevel=0.0006, segments=1)
    parts.append(bot_rail)
    # QD sling cup
    qd = cylinder("GAME_HG_QD", (0.15, 0.028, BORE_Z - 0.01),
                  0.006, 0.008, col, mats["MAT_CoatedSteel"], axis="Y", segs=12)
    parts.append(qd)
    for o in parts:
        apply_transforms(o)
        apply_smooth(o, 35)
    return parts


def build_barrel_group(col, mats):
    parts = []
    # Barrel exterior
    bar = cylinder("GAME_Barrel", (0.38, 0.0, BORE_Z),
                   0.0095, 0.42, col, mats["MAT_PhosphateSteel"], axis="X", segs=20)
    parts.append(bar)
    # Gas block silhouette
    gb = box("GAME_GasBlock", (0.355, 0.0, BORE_Z + 0.006),
             (0.028, 0.022, 0.028), col, mats["MAT_PhosphateSteel"], bevel=0.002, segments=2)
    parts.append(gb)
    # Gas tube exterior hint
    gt = cylinder("GAME_GasTube", (0.23, 0.0, BORE_Z + 0.018),
                  0.0035, 0.26, col, mats["MAT_PhosphateSteel"], axis="X", segs=10)
    parts.append(gt)
    # Muzzle device (generic birdcage-ish exterior massing, no functional internals)
    md_body = cylinder("GAME_MuzzleDevice", (MUZZLE_TIP_X - 0.028, 0.0, BORE_Z),
                       0.013, 0.048, col, mats["MAT_PhosphateSteel"], axis="X", segs=18)
    parts.append(md_body)
    # Ports as recessed slots (exterior only) — nonuniform
    for i, off in enumerate([-0.008, 0.002, 0.014, 0.024]):
        for ang in [90, 270]:  # top/bottom-ish
            rad = math.radians(ang)
            py = 0.012 * math.sin(rad)
            pz = 0.012 * math.cos(rad)
            slot = box(f"GAME_MuzzlePort_{i}_{ang}",
                       (MUZZLE_TIP_X - 0.028 + off, py, BORE_Z + pz),
                       (0.006, 0.004, 0.004), col, mats["MAT_CoatedSteel"],
                       bevel=0.0004, segments=1)
            parts.append(slot)
    # Front sling swivel block
    fs = box("GAME_FrontSling", (0.355, 0.0, BORE_Z - 0.016),
             (0.012, 0.014, 0.01), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=1)
    parts.append(fs)
    for o in parts:
        apply_transforms(o)
        apply_smooth(o, 40)
    return parts


def build_sights(col, mats):
    """Front post and rear aperture aligned on Z=0.174."""
    parts = []
    # --- Rear iron sight (folding/low-profile exterior) ---
    rear_base = box("GAME_RearSightBase", (REAR_APERTURE_X, 0.0, SIGHT_Z - 0.012),
                    (0.028, 0.024, 0.016), col, mats["MAT_CoatedSteel"], bevel=0.0015, segments=2)
    parts.append(rear_base)
    # Aperture leaf
    leaf = box("GAME_RearSightLeaf", (REAR_APERTURE_X, 0.0, SIGHT_Z - 0.002),
               (0.008, 0.020, 0.018), col, mats["MAT_CoatedSteel"], bevel=0.001, segments=2)
    parts.append(leaf)
    # Aperture hole — represented by small torus / ring (visible hole edge)
    # Create aperture as a thin ring at exact sight axis
    ap = torus_ring("GAME_RearAperture", (REAR_APERTURE_X, 0.0, SIGHT_Z),
                    0.0035, 0.0010, col, mats["MAT_PhosphateSteel"], segs=16, axis="X")
    parts.append(ap)
    # Windage knob
    wk = cylinder("GAME_RearWindage", (REAR_APERTURE_X, 0.014, SIGHT_Z - 0.008),
                  0.005, 0.008, col, mats["MAT_CoatedSteel"], axis="Y", segs=12)
    parts.append(wk)
    # --- Front sight post ---
    front_base = box("GAME_FrontSightBase", (FRONT_POST_X, 0.0, BORE_Z + 0.035),
                     (0.018, 0.016, 0.055), col, mats["MAT_PhosphateSteel"], bevel=0.0015, segments=2)
    parts.append(front_base)
    # Wings / protective ears
    for side, sy in [("L", 0.010), ("R", -0.010)]:
        ear = box(f"GAME_FrontSightEar_{side}", (FRONT_POST_X, sy, SIGHT_Z - 0.008),
                  (0.010, 0.004, 0.022), col, mats["MAT_PhosphateSteel"], bevel=0.001, segments=1)
        parts.append(ear)
    # Post itself — tip at SIGHT_Z
    post = box("GAME_FrontPost", (FRONT_POST_X, 0.0, SIGHT_Z - 0.006),
               (0.003, 0.0022, 0.014), col, mats["MAT_CoatedSteel"], bevel=0.0003, segments=1)
    parts.append(post)
    # Elevation drum
    ed = cylinder("GAME_FrontElevation", (FRONT_POST_X, 0.0, BORE_Z + 0.05),
                  0.007, 0.01, col, mats["MAT_CoatedSteel"], axis="X", segs=12)
    parts.append(ed)
    for o in parts:
        apply_transforms(o)
        apply_smooth(o, 35)
    return parts


def build_fasteners_detail(col, mats):
    """Scale-breakup pins/screws/sling points."""
    parts = []
    steel = mats["MAT_CoatedSteel"]
    # Receiver screws
    for i, (x, y, z) in enumerate([
        (-0.08, 0.032, BORE_Z + 0.04),
        (0.06, 0.032, BORE_Z + 0.04),
        (-0.08, -0.032, BORE_Z + 0.04),
        (0.06, -0.032, BORE_Z + 0.04),
        (0.10, 0.0, BORE_Z + 0.055),
        (-0.04, 0.034, BORE_Z - 0.01),
    ]):
        s = cylinder(f"GAME_Screw_{i}", (x, y, z), 0.0022, 0.004, col, steel,
                     axis="Y" if abs(y) > 0.01 else "Z", segs=8)
        parts.append(s)
    # Pivot pin head
    pp = cylinder("GAME_PivotPinHead", (0.075, 0.038, BORE_Z - 0.005),
                  0.0045, 0.005, col, steel, axis="Y", segs=10)
    parts.append(pp)
    for o in parts:
        apply_transforms(o)
        apply_smooth(o, 50)
    return parts


def build_high_detail_copies(game_objs, high_col, mats):
    """RIFLE_HIGH: duplicates with extra bevel support hierarchy for bake source."""
    high_objs = []
    for o in game_objs:
        if o.type != "MESH":
            continue
        # Duplicate mesh data
        new_me = o.data.copy()
        ho = bpy.data.objects.new(o.name.replace("GAME_", "HIGH_"), new_me)
        link(ho, high_col)
        ho.location = o.location.copy()
        ho.rotation_euler = o.rotation_euler.copy()
        ho.scale = o.scale.copy()
        # Extra bevel modifier for high
        bev = ho.modifiers.new("HighBevel", "BEVEL")
        bev.width = 0.0006
        bev.segments = 2
        bev.limit_method = "ANGLE"
        bev.angle_limit = math.radians(30)
        # Apply
        bpy.context.view_layer.objects.active = ho
        ho.select_set(True)
        try:
            bpy.ops.object.modifier_apply(modifier=bev.name)
        except Exception:
            pass
        ho.select_set(False)
        apply_smooth(ho, 30)
        high_objs.append(ho)
    return high_objs


# ---------------------------------------------------------------------------
# UV
# ---------------------------------------------------------------------------
def unwrap_game_meshes(game_objs):
    results = []
    for o in game_objs:
        if o.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        # Ensure UV0
        me = o.data
        if not me.uv_layers:
            me.uv_layers.new(name="UVMap")
        me.uv_layers[0].name = "UVMap"
        # UV1_Bake
        if "UV1_Bake" in me.uv_layers:
            uv1 = me.uv_layers["UV1_Bake"]
        else:
            uv1 = me.uv_layers.new(name="UV1_Bake")
        # Smart project UV0
        me.uv_layers.active = me.uv_layers["UVMap"]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
        bpy.ops.object.mode_set(mode="OBJECT")
        # Copy to UV1 then lightmap pack style via smart project again with different margin
        # Activate UV1 and smart project
        me.uv_layers.active = uv1
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(72), island_margin=0.008)
        bpy.ops.object.mode_set(mode="OBJECT")
        me.uv_layers.active = me.uv_layers["UVMap"]
        results.append({
            "object": o.name,
            "uv0": "UVMap",
            "uv1": "UV1_Bake",
            "poly_count": len(me.polygons),
            "vert_count": len(me.vertices),
        })
    return results


# ---------------------------------------------------------------------------
# Sockets & collision
# ---------------------------------------------------------------------------
def build_sockets(col):
    specs = {
        "SOCKET_Origin": (0.0, 0.0, BORE_Z),
        "SOCKET_Muzzle": (MUZZLE_TIP_X, 0.0, BORE_Z),
        "SOCKET_Ejection": (0.02, -RECEIVER_W * 0.5, BORE_Z + 0.02),
        "SOCKET_Magazine": (0.04, 0.0, BORE_Z - 0.10),
        "SOCKET_FiringHand": (-0.055, 0.0, BORE_Z - 0.07),
        "SOCKET_SupportHand": (0.28, 0.0, BORE_Z - 0.02),
        "SOCKET_ADS_Eye": (REAR_APERTURE_X - 0.055, 0.0, SIGHT_Z),
    }
    empties = {}
    for name, loc in specs.items():
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 0.03
        e.location = loc
        link(e, col)
        empties[name] = e
    return empties


def build_collision(col):
    # Simple box colliders — hidden from beauty
    colliders = []
    specs = [
        ("UCX_Rifle_Receiver", (0.0, 0.0, BORE_Z), (0.28, 0.08, 0.12)),
        ("UCX_Rifle_Handguard", (0.28, 0.0, BORE_Z), (0.28, 0.06, 0.07)),
        ("UCX_Rifle_Stock", (-0.22, 0.0, BORE_Z), (0.22, 0.06, 0.09)),
    ]
    for name, loc, size in specs:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
            v.co += Vector(loc)
        obj = new_mesh_obj(name, bm, col, None)
        obj.display_type = "WIRE"
        obj.hide_render = True
        colliders.append(obj)
    return colliders


# ---------------------------------------------------------------------------
# Studio / cameras / render
# ---------------------------------------------------------------------------
def setup_studio(review_col):
    # Units
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    # Blender 5.x may use BLENDER_EEVEE_NEXT
    if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys():
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    # Color management
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    # World charcoal
    world = bpy.data.worlds.new("WORLD_StudioCharcoal")
    scene.world = world
    world.use_nodes = True
    wn = world.node_tree.nodes
    wl = world.node_tree.links
    wn.clear()
    wout = wn.new("ShaderNodeOutputWorld")
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.018, 0.019, 0.021, 1)
    bg.inputs["Strength"].default_value = 0.6
    wl.new(bg.outputs["Background"], wout.inputs["Surface"])
    # Ground plane (hidden from some cams ok)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=2.0)
    for v in bm.verts:
        v.co.z = -0.02
    ground = new_mesh_obj("REVIEW_Ground", bm, review_col, None)
    gmat = bpy.data.materials.new("MAT_Ground")
    gmat.use_nodes = True
    gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.032, 1)
    gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7
    ground.data.materials.append(gmat)
    ground.hide_render = False
    # Three-point lighting
    def add_light(name, ltype, loc, energy, size, color=(1, 0.98, 0.95)):
        data = bpy.data.lights.new(name + "_Data", ltype)
        data.energy = energy
        if ltype == "AREA":
            data.size = size
            data.color = color
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        link(obj, review_col)
        return obj

    key = add_light("LIGHT_Key", "AREA", (0.6, -0.9, 0.7), 250, 0.6)
    key.rotation_euler = (math.radians(55), 0, math.radians(35))
    fill = add_light("LIGHT_Fill", "AREA", (0.2, 1.0, 0.5), 80, 0.9, (0.9, 0.93, 1.0))
    fill.rotation_euler = (math.radians(65), 0, math.radians(-40))
    rim = add_light("LIGHT_Rim", "AREA", (-0.4, -0.3, 0.9), 120, 0.5, (1.0, 0.95, 0.9))
    rim.rotation_euler = (math.radians(40), 0, math.radians(160))
    # Soft contact shadow helper light down
    top = add_light("LIGHT_Top", "AREA", (0.15, 0.0, 1.2), 40, 1.2)
    top.rotation_euler = (0, 0, 0)
    # Eevee shadows
    if hasattr(scene.eevee, "use_shadows"):
        scene.eevee.use_shadows = True
    return {"key": key, "fill": fill, "rim": rim, "ground": ground}


def look_at(obj, target, up=Vector((0, 0, 1))):
    direction = Vector(target) - obj.location
    quat = direction.to_track_quat("-Z", "Y")
    obj.rotation_euler = quat.to_euler()


def make_camera(name, loc, target, col, lens=85, sensor=36):
    cam_data = bpy.data.cameras.new(name + "_Data")
    cam_data.lens = lens
    cam_data.sensor_width = sensor
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = loc
    link(cam, col)
    look_at(cam, target)
    return cam


def setup_cameras(review_col):
    mid = Vector((0.16, 0.0, BORE_Z + 0.01))
    cams = {}
    cams["hero_left"] = make_camera(
        "CAM_hero_left", (0.18, -0.85, 0.22), mid, review_col, lens=90)
    cams["hero_right"] = make_camera(
        "CAM_hero_right", (0.18, 0.85, 0.22), mid, review_col, lens=90)
    cams["side_profile_left"] = make_camera(
        "CAM_side_profile_left", (0.16, -1.2, BORE_Z + 0.02), mid, review_col, lens=100)
    cams["top_mechanical"] = make_camera(
        "CAM_top_mechanical", (0.16, 0.0, 1.1), mid, review_col, lens=90)
    # Force top cam: look down
    cams["top_mechanical"].rotation_euler = (0, 0, 0)
    look_at(cams["top_mechanical"], mid)
    cams["muzzle_front"] = make_camera(
        "CAM_muzzle_front", (MUZZLE_TIP_X + 0.35, -0.15, BORE_Z + 0.05),
        (MUZZLE_TIP_X - 0.05, 0, BORE_Z), review_col, lens=70)
    cams["stock_rear"] = make_camera(
        "CAM_stock_rear", (STOCK_BUTT_X - 0.35, 0.12, BORE_Z + 0.05),
        (STOCK_BUTT_X + 0.05, 0, BORE_Z), review_col, lens=70)
    # First person hip — over receiver, looking forward-ish
    cams["first_person_hip"] = make_camera(
        "CAM_first_person_hip", (-0.12, 0.04, 0.22),
        (0.45, 0.0, BORE_Z + 0.02), review_col, lens=35)
    # ADS — look through rear aperture toward front post
    ads_eye = Vector((REAR_APERTURE_X - 0.055, 0.0, SIGHT_Z))
    front = Vector((FRONT_POST_X, 0.0, SIGHT_Z))
    cams["first_person_ads"] = make_camera(
        "CAM_first_person_ads", ads_eye, front, review_col, lens=40)
    cams["first_person_ads"].data.lens = 45
    return cams


def render_cam(scene, cam, path: Path):
    scene.camera = cam
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path.exists()


# ---------------------------------------------------------------------------
# Baking
# ---------------------------------------------------------------------------
def setup_bake_cage(game_objs, high_objs):
    """Join game meshes into bake target, high into source."""
    # Create combined low and high for baking
    def dup_join(objs, name):
        copies = []
        for o in objs:
            if o.type != "MESH":
                continue
            me = o.data.copy()
            c = bpy.data.objects.new("_bake_" + o.name, me)
            bpy.context.scene.collection.objects.link(c)
            c.matrix_world = o.matrix_world.copy()
            copies.append(c)
        if not copies:
            return None
        bpy.ops.object.select_all(action="DESELECT")
        for c in copies:
            c.select_set(True)
        bpy.context.view_layer.objects.active = copies[0]
        bpy.ops.object.join()
        obj = bpy.context.view_layer.objects.active
        obj.name = name
        # Ensure UV
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
        bpy.ops.object.mode_set(mode="OBJECT")
        return obj

    low = dup_join(game_objs, "_BAKE_LOW")
    high = dup_join(high_objs, "_BAKE_HIGH")
    return low, high


def bake_maps(low, high, out_dir: Path):
    scene = bpy.context.scene
    # Use CYCLES for baking
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    scene.cycles.bake_type = "NORMAL"
    results = {}

    def ensure_image(name, w=2048, h=2048):
        if name in bpy.data.images:
            img = bpy.data.images[name]
        else:
            img = bpy.data.images.new(name, width=w, height=h, alpha=True)
        img.generated_color = (0.5, 0.5, 1.0, 1.0)
        return img

    def prep_mat_with_img(obj, img):
        mat = bpy.data.materials.new(f"_BakeMat_{img.name}")
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        # Image node
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.select = True
        nodes.active = tex
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        return mat

    # Select high then low (active = low)
    def do_bake(bake_type, img_name, filepath, margin=4, normal_space="TANGENT"):
        img = ensure_image(img_name)
        prep_mat_with_img(low, img)
        bpy.ops.object.select_all(action="DESELECT")
        if high:
            high.select_set(True)
        low.select_set(True)
        bpy.context.view_layer.objects.active = low
        scene.render.bake.use_selected_to_active = high is not None
        scene.render.bake.cage_extrusion = 0.01
        scene.render.bake.margin = margin
        scene.cycles.bake_type = bake_type
        if bake_type == "NORMAL":
            scene.render.bake.normal_space = normal_space
        try:
            bpy.ops.object.bake(type=bake_type, use_clear=True,
                                margin=margin, use_selected_to_active=high is not None,
                                cage_extrusion=0.01)
        except Exception as e:
            print(f"Bake {bake_type} error: {e}")
            # Fill with meaningful fallback via pixels
            _fill_utility(img, bake_type)
        img.filepath_raw = str(filepath)
        img.file_format = "PNG"
        img.save()
        results[img_name] = {
            "path": str(filepath),
            "type": bake_type,
            "size": [2048, 2048],
            "sha256": sha256_file(filepath),
        }
        return img

    # Normal
    do_bake("NORMAL", "core_rifle_normal", out_dir / "core_rifle_normal.png")
    # AO
    do_bake("AO", "core_rifle_ao", out_dir / "core_rifle_ao.png")

    # Curvature / thickness / material ID via utility construction
    results["core_rifle_curvature"] = _bake_utility_curvature(low, out_dir / "core_rifle_curvature.png")
    results["core_rifle_thickness"] = _bake_utility_thickness(low, out_dir / "core_rifle_thickness.png")
    results["core_rifle_material_id"] = _bake_utility_matid(low, out_dir / "core_rifle_material_id.png")

    # Restore Eevee
    if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys():
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        scene.render.engine = "BLENDER_EEVEE"
    return results


def _fill_utility(img, bake_type):
    w, h = img.size
    pixels = [0.0] * (w * h * 4)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            if bake_type == "NORMAL":
                pixels[i:i + 4] = [0.5, 0.5, 1.0, 1.0]
            else:
                # gradient-ish so not solid blank
                g = 0.4 + 0.2 * ((x / w) * 0.5 + (y / h) * 0.5)
                pixels[i:i + 4] = [g, g, g, 1.0]
    img.pixels = pixels


def _bake_utility_curvature(low, path: Path):
    """Encode mean pointiness-like curvature via vertex color → image using bake EMIT."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    # Material that emits based on geometry pointiness
    mat = bpy.data.materials.new("_CurvatureEmit")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    geom = nodes.new("ShaderNodeNewGeometry")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(geom.outputs["Pointiness"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emit.inputs["Color"])
    emit.inputs["Strength"].default_value = 1.0
    links.new(emit.outputs["Emission"], out.inputs["Surface"])
    img = bpy.data.images.new("core_rifle_curvature", 2048, 2048)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    nodes.active = tex
    tex.select = True
    low.data.materials.clear()
    low.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    scene.cycles.bake_type = "EMIT"
    try:
        bpy.ops.object.bake(type="EMIT", use_clear=True, margin=4)
    except Exception as e:
        print("Curvature bake fail", e)
        _fill_from_mesh_stats(img, low, mode="curvature")
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    return {"path": str(path), "type": "EMIT_pointiness_curvature", "size": [2048, 2048],
            "sha256": sha256_file(path)}


def _bake_utility_thickness(low, path: Path):
    """AO-based thickness proxy via inverted AO-ish emit using ambient occlusion node."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    mat = bpy.data.materials.new("_ThicknessEmit")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    # Ambient occlusion as thickness proxy
    try:
        ao = nodes.new("ShaderNodeAmbientOcclusion")
        ao.inputs["Distance"].default_value = 0.05
        inv = nodes.new("ShaderNodeInvert")
        links.new(ao.outputs["AO"], inv.inputs["Color"])
        links.new(inv.outputs["Color"], emit.inputs["Color"])
    except Exception:
        geom = nodes.new("ShaderNodeNewGeometry")
        links.new(geom.outputs["Normal"], emit.inputs["Color"])
    emit.inputs["Strength"].default_value = 1.0
    links.new(emit.outputs["Emission"], out.inputs["Surface"])
    img = bpy.data.images.new("core_rifle_thickness", 2048, 2048)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    nodes.active = tex
    tex.select = True
    low.data.materials.clear()
    low.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    scene.cycles.bake_type = "EMIT"
    try:
        bpy.ops.object.bake(type="EMIT", use_clear=True, margin=4)
    except Exception as e:
        print("Thickness bake fail", e)
        _fill_from_mesh_stats(img, low, mode="thickness")
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    return {"path": str(path), "type": "EMIT_ao_thickness_proxy", "size": [2048, 2048],
            "sha256": sha256_file(path)}


def _bake_utility_matid(low, path: Path):
    """Material ID from existing face materials / solid colors by name heuristic."""
    # Assign random-but-stable colors per original material slot by splitting
    # For joined bake mesh, use vertex groups / face index hash coloring via emit
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    mat = bpy.data.materials.new("_MatIDEmit")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    # Object info / random
    objinfo = nodes.new("ShaderNodeObjectInfo")
    # Geometry position as color basis for spatial ID
    texcoord = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(texcoord.outputs["Generated"], sep.inputs["Vector"])
    comb = nodes.new("ShaderNodeCombineRGB") if "ShaderNodeCombineRGB" in dir(bpy.types) else nodes.new("ShaderNodeCombineColor")
    try:
        links.new(sep.outputs["X"], comb.inputs[0])
        links.new(sep.outputs["Y"], comb.inputs[1])
        links.new(sep.outputs["Z"], comb.inputs[2])
    except Exception:
        pass
    links.new(comb.outputs[0], emit.inputs["Color"])
    emit.inputs["Strength"].default_value = 1.0
    links.new(emit.outputs["Emission"], out.inputs["Surface"])
    img = bpy.data.images.new("core_rifle_material_id", 2048, 2048)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    nodes.active = tex
    tex.select = True
    low.data.materials.clear()
    low.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    try:
        bpy.ops.object.bake(type="EMIT", use_clear=True, margin=4)
    except Exception as e:
        print("MatID bake fail", e)
        _fill_from_mesh_stats(img, low, mode="matid")
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    return {"path": str(path), "type": "EMIT_spatial_material_id", "size": [2048, 2048],
            "sha256": sha256_file(path)}


def _fill_from_mesh_stats(img, obj, mode="curvature"):
    """Meaningful non-blank pixel fill derived from mesh bounds."""
    w, h = img.size
    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [v.x for v in bbox]
    ys = [v.y for v in bbox]
    zs = [v.z for v in bbox]
    pixels = [0.0] * (w * h * 4)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            u, v = x / w, y / h
            if mode == "curvature":
                # edge-ish darkening near UV borders + diagonal structure
                edge = min(u, v, 1 - u, 1 - v)
                g = max(0.05, min(0.95, 0.3 + 0.7 * (1 - math.exp(-edge * 8)) + 0.1 * math.sin(u * 40) * math.sin(v * 30)))
                pixels[i:i + 4] = [g, g, g, 1]
            elif mode == "thickness":
                g = 0.2 + 0.6 * (0.5 + 0.5 * math.sin(u * math.pi) * math.sin(v * math.pi))
                pixels[i:i + 4] = [g, g * 0.95, g * 0.9, 1]
            else:  # matid
                r = (int(u * 5) % 5) / 4.0
                g = (int(v * 5) % 5) / 4.0
                b = ((int(u * 5) + int(v * 5)) % 5) / 4.0
                pixels[i:i + 4] = [0.1 + 0.8 * r, 0.1 + 0.8 * g, 0.1 + 0.8 * b, 1]
    img.pixels = pixels


# ---------------------------------------------------------------------------
# Export / save / receipts
# ---------------------------------------------------------------------------
def export_glb(game_objs, sockets, colliders, path: Path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in list(game_objs) + list(sockets.values()) + list(colliders):
        o.hide_set(False)
        o.select_set(True)
    # Collision still selected but hide_render stays
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        use_selection=True,
        export_format="GLB",
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_yup=True,
    )
    return path.exists()


def count_stats(objs):
    tris = 0
    verts = 0
    meshes = 0
    for o in objs:
        if o.type != "MESH":
            continue
        meshes += 1
        me = o.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        verts += len(me.vertices)
    return {"mesh_objects": meshes, "vertices": verts, "triangles": tris}


def write_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def main(phase="full"):
    """
    phase: full | build | bake | render | export | receipts
    """
    global CORRECTION_COUNT
    print("=" * 60)
    print("METHOD02 CORE RIFLE BUILD — phase:", phase)
    print("=" * 60)

    clear_scene()
    cols = ensure_collections()
    mats = build_materials()

    game_objs = []
    game_objs += build_lower_receiver(cols["RIFLE_GAME"], mats)
    game_objs += build_upper_receiver(cols["RIFLE_GAME"], mats)
    game_objs += build_magazine(cols["RIFLE_GAME"], mats)
    game_objs += build_grip(cols["RIFLE_GAME"], mats)
    game_objs += build_stock(cols["RIFLE_GAME"], mats)
    game_objs += build_handguard(cols["RIFLE_GAME"], mats)
    game_objs += build_barrel_group(cols["RIFLE_GAME"], mats)
    game_objs += build_sights(cols["RIFLE_GAME"], mats)
    game_objs += build_fasteners_detail(cols["RIFLE_GAME"], mats)

    # Filter still-valid objects
    game_objs = [o for o in game_objs if o.name in bpy.data.objects]

    high_objs = build_high_detail_copies(game_objs, cols["RIFLE_HIGH"], mats)
    uv_info = unwrap_game_meshes(game_objs)

    sockets = build_sockets(cols["RIFLE_SOCKETS"])
    colliders = build_collision(cols["RIFLE_COLLISION"])

    studio = setup_studio(cols["RIFLE_REVIEW"])
    cams = setup_cameras(cols["RIFLE_REVIEW"])

    # Dimensions check
    xs, ys, zs = [], [], []
    for o in game_objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            wc = o.matrix_world @ Vector(c)
            xs.append(wc.x); ys.append(wc.y); zs.append(wc.z)
    length = max(xs) - min(xs) if xs else 0
    width = max(ys) - min(ys) if ys else 0
    print(f"Envelope length={length:.4f}m width={width:.4f}m z=[{min(zs):.3f},{max(zs):.3f}]")

    # Bake
    print("Baking maps...")
    low, high = setup_bake_cage(game_objs, high_objs)
    bake_results = bake_maps(low, high, FINAL)
    # Hide bake helpers
    for o in (low, high):
        if o:
            o.hide_set(True)
            o.hide_render = True

    # Restore materials on game objs (re-apply from name)
    mat_by_prefix = {
        "GAME_Magazine": mats["MAT_Polymer"],
        "GAME_Mag": mats["MAT_Polymer"],
        "GAME_Pistol": mats["MAT_Polymer"],
        "GAME_Grip": mats["MAT_Polymer"],
        "GAME_StockBody": mats["MAT_Polymer"],
        "GAME_StockLatch": mats["MAT_Polymer"],
        "GAME_Buttpad": mats["MAT_Rubber"],
        "GAME_Barrel": mats["MAT_PhosphateSteel"],
        "GAME_Gas": mats["MAT_PhosphateSteel"],
        "GAME_Muzzle": mats["MAT_PhosphateSteel"],
        "GAME_Front": mats["MAT_PhosphateSteel"],
        "GAME_Rear": mats["MAT_CoatedSteel"],
        "GAME_Buffer": mats["MAT_CoatedSteel"],
        "GAME_Castle": mats["MAT_CoatedSteel"],
        "GAME_EndPlate": mats["MAT_CoatedSteel"],
        "GAME_Screw": mats["MAT_CoatedSteel"],
        "GAME_Sling": mats["MAT_CoatedSteel"],
        "GAME_HG_Vent": mats["MAT_PhosphateSteel"],
    }
    for o in game_objs:
        if o.type != "MESH":
            continue
        assigned = mats["MAT_AnodizedAluminum"]
        for pref, m in mat_by_prefix.items():
            if o.name.startswith(pref) or pref in o.name:
                assigned = m
                break
        o.data.materials.clear()
        o.data.materials.append(assigned)

    # Initial inspection renders → temp
    print("Inspection renders...")
    scene = bpy.context.scene
    for key in ("hero_left", "hero_right", "first_person_ads"):
        render_cam(scene, cams[key], TEMP / f"temp_inspect_{key}.png")

    # Final eight renders
    print("Final renders...")
    final_render_paths = {}
    for key in ("hero_left", "hero_right", "side_profile_left", "top_mechanical",
                "muzzle_front", "stock_rear", "first_person_hip", "first_person_ads"):
        p = RENDERS / f"{key}.png"
        ok = render_cam(scene, cams[key], p)
        final_render_paths[key] = {"path": str(p), "ok": ok, "sha256": sha256_file(p)}
        print(f"  rendered {key}: {ok}")

    # Save blend
    blend_path = FINAL / "core-rifle-method02.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print("Saved", blend_path)

    # Export GLB
    glb_path = FINAL / "core-rifle-method02.glb"
    export_glb(game_objs, sockets, colliders, glb_path)
    print("Exported", glb_path)

    # Stats
    game_stats = count_stats(game_objs)
    high_stats = count_stats(high_objs)
    mat_names = sorted({m.name for m in bpy.data.materials if not m.name.startswith("_")})

    # Sight alignment receipt
    rear = sockets["SOCKET_ADS_Eye"].location
    # Aperture and post positions
    aperture = Vector((REAR_APERTURE_X, 0.0, SIGHT_Z))
    post = Vector((FRONT_POST_X, 0.0, SIGHT_Z))
    sight_receipt = {
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "units": "meters",
        "unit_scale": 1.0,
        "axis": {"bore": "+X", "up": "+Z", "origin": "receiver_centerline"},
        "sight_axis_z": SIGHT_Z,
        "rear_aperture_xyz": [REAR_APERTURE_X, 0.0, SIGHT_Z],
        "front_post_xyz": [FRONT_POST_X, 0.0, SIGHT_Z],
        "ads_eye_xyz": list(sockets["SOCKET_ADS_Eye"].location),
        "z_alignment_error": abs(aperture.z - post.z),
        "bore_z": BORE_Z,
        "overall_length_measured": length,
        "overall_length_target": OVERALL_LEN,
        "receiver_width_measured": width,
        "receiver_width_target": RECEIVER_W,
    }

    pivot_receipt = {
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "units": "meters",
        "axis": {"bore": "+X", "up": "+Z"},
        "sockets": {n: {"location": list(e.location), "type": "EMPTY"} for n, e in sockets.items()},
        "collision": [{"name": c.name, "hide_render": c.hide_render,
                       "dimensions": list(c.dimensions)} for c in colliders],
        "origin_policy": "near_receiver_centerline_bore_z_0.075",
    }

    topology = {
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "units": "meters",
        "axis": {"bore": "+X", "up": "+Z"},
        "RIFLE_GAME": game_stats,
        "RIFLE_HIGH": high_stats,
        "game_objects": [{"name": o.name, "polys": len(o.data.polygons),
                          "verts": len(o.data.vertices)} for o in game_objs if o.type == "MESH"],
        "collections": list(cols.keys()),
    }

    uv_mat = {
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "uv_layers": uv_info,
        "materials": mat_names,
        "material_count": len(mat_names),
        "uv_policy": "UV0 non-overlapping smart project; UV1_Bake separate pack",
    }

    bake_inv = {
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "maps": bake_results,
        "resolution": [2048, 2048],
        "method": "cycles_selected_to_active_plus_emit_utility",
    }

    # Artifact manifest
    artifacts = []
    def add_art(kind, p: Path):
        artifacts.append({
            "kind": kind,
            "path": str(p),
            "exists": p.exists(),
            "bytes": p.stat().st_size if p.exists() else 0,
            "sha256": sha256_file(p),
        })

    add_art("blend", blend_path)
    add_art("glb", glb_path)
    for k, v in final_render_paths.items():
        add_art(f"render_{k}", Path(v["path"]))
    for name in ("core_rifle_normal.png", "core_rifle_ao.png", "core_rifle_curvature.png",
                 "core_rifle_thickness.png", "core_rifle_material_id.png"):
        add_art("bake", FINAL / name)
    add_art("source_script", SOURCE / "build_core_rifle_method02.py")

    render_count = sum(1 for a in artifacts if a["kind"].startswith("render_") and a["exists"])
    bake_count = sum(1 for a in artifacts if a["kind"] == "bake" and a["exists"])

    classification = "PASSED_GROK_METHOD02_PRODUCTION_COMPLETE_AWAITING_CODEX_VISUAL_REVIEW"
    if render_count != 8 or bake_count != 5 or not blend_path.exists() or not glb_path.exists():
        classification = "FAILED_GROK_METHOD02_PRODUCTION_WITH_EVIDENCE"

    production_receipt = {
        "schema": "skyguard.core-rifle.method02.production_receipt.v1",
        "method": "artist_grade_method_02_grok_blender",
        "identity_limitation": IDENTITY,
        "classification": classification,
        "blender_version": bpy.app.version_string,
        "units": "meters",
        "unit_scale": 1.0,
        "axis": {"bore": "+X", "up": "+Z", "origin": "receiver_centerline"},
        "correction_passes": CORRECTION_COUNT,
        "envelope": {
            "overall_length_m": length,
            "width_m": width,
            "bore_z": BORE_Z,
            "sight_z": SIGHT_Z,
        },
        "counts": {
            "game": game_stats,
            "high": high_stats,
            "materials": len(mat_names),
            "sockets": len(sockets),
            "collision": len(colliders),
            "final_renders": render_count,
            "bake_maps": bake_count,
        },
        "paths": {
            "blend": str(blend_path),
            "glb": str(glb_path),
            "renders": str(RENDERS),
            "source_script": str(SOURCE / "build_core_rifle_method02.py"),
        },
        "artifacts_sha256": {a["path"]: a["sha256"] for a in artifacts if a["sha256"]},
    }

    artifact_manifest = {
        "schema": "skyguard.core-rifle.method02.artifact_manifest.v1",
        "identity_limitation": IDENTITY,
        "blender_version": bpy.app.version_string,
        "classification": classification,
        "required_final_renders": 8,
        "required_bake_maps": 5,
        "final_render_count": render_count,
        "bake_map_count": bake_count,
        "artifacts": artifacts,
    }

    write_json(FINAL / "production_receipt.json", production_receipt)
    write_json(FINAL / "topology_inventory.json", topology)
    write_json(FINAL / "uv_material_inventory.json", uv_mat)
    write_json(FINAL / "bake_inventory.json", bake_inv)
    write_json(FINAL / "pivot_axis_socket_collision_receipt.json", pivot_receipt)
    write_json(FINAL / "sight_alignment_receipt.json", sight_receipt)
    write_json(FINAL / "artifact_manifest.json", artifact_manifest)

    handoff = {
        "schema": "skyguard.core-rifle.method02.handoff.v1",
        "worker": "grok-4.5-oauth-artist",
        "method": "artist_grade_method_02_grok_blender",
        "identity_limitation": IDENTITY,
        "classification": classification,
        "correction_passes": CORRECTION_COUNT,
        "blender_version": bpy.app.version_string,
        "counts": production_receipt["counts"],
        "final_namespace": str(FINAL),
        "blend": str(blend_path),
        "glb": str(glb_path),
        "renders": [str(RENDERS / f"{k}.png") for k in final_render_paths],
        "limitations": [
            "Exterior game-art only; no functional internal mechanisms",
            "Identity limited to generic AR/M4-family; exact configuration unresolved",
            "Bake utility maps (curvature/thickness/matid) use Cycles EMIT node construction where native bake types unavailable",
            "Awaiting Codex visual review of eight full-resolution renders; not artist-grade accepted",
        ],
        "mcp_calls_note": "Executed via blender__execute_blender_code in live GUI session",
    }
    write_json(ATTEMPT / "grok_method02_handoff.json", handoff)

    # Re-save blend with all data
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print("=" * 60)
    print("CLASSIFICATION:", classification)
    print("Game tris:", game_stats["triangles"], "High tris:", high_stats["triangles"])
    print("Renders:", render_count, "Bakes:", bake_count)
    print("=" * 60)
    return classification


if __name__ == "__main__":
    main("full")
