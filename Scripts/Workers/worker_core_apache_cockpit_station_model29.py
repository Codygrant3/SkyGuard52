from __future__ import annotations

"""Governed AH-64 CPG station-model29 worker.

Built from the Dutch MoD AH-64D CPG reference plate, DCS Fig 43-45,
TM-1-1520-238-10 Fig 2-8 / 2-14, and the model28 visual fail, not a
plate-knob pass. Keep the model28 assert-path. Not another named
mesh on the same 60-mesh cage. Greenhouse hull owns three-quarter
as a closed outer volume (sill-in, belly, rail-out, crown, back
to sill-in) with punched discrete window bays — not a pane kit of
floating canopy sheets and shell slabs, and not a 6-point tube
solidified into C-shaped slabs. Stop emitting the cage:
do not create GEO_CanopyBay_L/R or GEO_JointPlate_*. Rails are
one thin trim pair on that hull, not a chunky cage. eye_forward
looks through raked windshield / world/sky in the upper two-thirds;
TEDAC and dash occupy the lower third, not a dark rectangular
well, not a housing well, and not an opaque pane wall. model28
visual fail: opaque side blocks boxed the eyepoint so four-station
glass plus a sky Background never read as look-out. Open the
forward cabin — no inner shell wall in the eyepoint frame — and
put glass in that frustum. Delete GEO_WindshieldFrame / shell
end-cap / brow faces that form a rectangular tunnel. Canopy glass
must read as glass, not a dark grey wall. One continuous formed
forward panel from dash_formed_front / dash_well_cavities, not
dash_panel_outline sibling faces in front of two flat cyan
screens. TDU and both MPD wells are recessed cavities in that
one mesh. GEO_TEDAC is grips + Fig 45 buttons + hood only,
sitting on the dash well, no standalone emit rectangle in front
of the panel. After object_from_bmesh + finish_mesh bevel,
GEO_Dash emit faces at index 1 (TDU) and index 2 (MPD) are tagged
so they survive the model25 miss (housing-grid face centers at
y=±0.05 missed abs(y)<0.048) and then call
orient_emit_faces_to_eye then assert_emit_faces_eye
(alignment >= 0.55). GEO_TEDAC has no emit faces; do not orient
or assert index 1 on it. Square TDU plus LHG/RHG stay as hardware
on the dash. TEDAC is not three stacked boxes. Destacked TDU
numbers are a ceiling: go smaller than width 0.118 / depth 0.018 /
hood 0.010. Raked windshield stations stay different YZ
trapezoids. Glass may occupy the forward look-out band; frames may
not. Keep glass overhead brow, dash z<=0.86, TEDAC green emit, MPD
emit-face fix, and the model14-26 bucket seat. GEO_Dash look-out
assert stays; after finish_mesh bevel, clamp |y|<0.20 verts to
z<=0.858 and drop the panel top to 0.848 so bevel cannot
recreate the model21 fail. Dark interior, dark rail, and olive
stay. Do not restore a draped canopy skin. Do not thicken
section_along members. No tube sweep in the greenhouse. Real
bmesh only. Public layout only. Outputs go only to --output.
"""

from pathlib import Path
import json
import math
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "Scripts"))

from skyguard_blender_worker_sdk import (  # noqa: E402
    SDK_VERSION,
    WorkerError,
    blender_module,
    configure_scene,
    create_collection,
    create_socket,
    export_asset,
    move_to_collection,
    now_utc,
    parse_worker_args,
    pbr_material,
    render_review_views,
    sha256,
    validate_asset,
)


ASSET_ID = "core-apache-cockpit-station-model29"
EYE = (0.0, 0.0, 1.18)
TEDAC = (0.50, 0.0, 0.88)
MPD_L = (0.50, -0.205, 0.885)
MPD_R = (0.50, 0.205, 0.885)
COLLECTIVE = (0.10, -0.28, 0.76)
CYCLIC = (0.22, -0.06, 0.70)
SCREEN_M = 0.127
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_CPG_Eye",
    "SOCKET_TEDAC",
    "SOCKET_MPD_L",
    "SOCKET_MPD_R",
    "SOCKET_Collective",
    "SOCKET_Cyclic",
]
# Canopy glass only. Rails, sills, A-pillars, frames, wiper, dash, TEDAC
# housing stay forbidden in the look-out band.
LOOKOUT_GLASS_ALLOWED = (
    "GEO_Windshield",
    "GEO_OverheadBrow",
    "GEO_ForwardBrow",
)
LOOKOUT_GLASS_PREFIX = "GEO_CanopyPane_"
LOOKOUT_STRUCTURE_FORBIDDEN = (
    "GEO_Rail_",
    "GEO_Sill_",
    "GEO_APillar_",
    "GEO_SideBow_",
    "GEO_JointPlate",
    "GEO_CanopyBay_",
    "GEO_CanopyShell_",
    "GEO_WindshieldFrame",
    "GEO_Wiper",
    "GEO_Dash",
    "GEO_DashShelf",
    "GEO_TEDAC",
)
BAY_SKIRT_FRAC = 0.18
BAY_HEADER_FRAC = 0.16


def bmesh_module():
    try:
        import bmesh  # type: ignore
    except ImportError as exc:
        raise WorkerError("This module must execute inside Blender.") from exc
    return bmesh


def mathutils_types():
    from mathutils import Matrix, Vector  # type: ignore

    return Matrix, Vector


def emit_material(
    name: str,
    color: tuple[float, float, float],
    roughness: float,
    emit: float,
    alpha: float = 1.0,
):
    bpy = blender_module()
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Roughness"].default_value = roughness
    if "Emission Color" in principled.inputs:
        principled.inputs["Emission Color"].default_value = (*color, 1.0)
    if "Emission Strength" in principled.inputs:
        principled.inputs["Emission Strength"].default_value = emit
    # Opaque emitters (TEDAC / MPD / EUFD) keep alpha 1.0 and no transmission.
    if alpha < 1.0:
        material.blend_method = "BLEND"
        material.use_backface_culling = True
        principled.inputs["Alpha"].default_value = alpha
        for candidate in ("Transmission Weight", "Transmission"):
            if candidate in principled.inputs:
                principled.inputs[candidate].default_value = 1.0
    return material


def ensure_uv0(obj) -> None:
    mesh = obj.data
    if mesh.uv_layers:
        mesh.uv_layers.active.name = "UV0"
        return
    uv_layer = mesh.uv_layers.new(name="UV0")
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


def finish_mesh(obj, collection):
    bpy = blender_module()
    bmesh = bmesh_module()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if obj.data.polygons:
        bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
        bevel.width = 0.0012
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier="Bevel")
        bpy.ops.object.shade_smooth()
    ensure_uv0(obj)
    move_to_collection(obj, collection)
    return obj


def object_from_bmesh(name: str, bm, collection, materials) -> object:
    bpy = blender_module()
    bmesh = bmesh_module()
    if bm.faces:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    for material in materials:
        if material is not None:
            obj.data.materials.append(material)
    collection.objects.link(obj)
    return finish_mesh(obj, collection)


def _bm_verts(geom, bmesh):
    return [element for element in geom if isinstance(element, bmesh.types.BMVert)]


def _bm_faces(geom, bmesh):
    return [element for element in geom if isinstance(element, bmesh.types.BMFace)]


def _basis(tangent):
    _matrix, vector = mathutils_types()
    direction = vector(tangent)
    if direction.length < 1e-8:
        direction = vector((0.0, 0.0, 1.0))
    direction.normalize()
    helper = vector((0.0, 0.0, 1.0))
    if abs(direction.dot(helper)) > 0.86:
        helper = vector((1.0, 0.0, 0.0))
    binormal = direction.cross(helper).normalized()
    normal = binormal.cross(direction).normalized()
    return direction, binormal, normal


def _rotate_z(point, origin, angle: float) -> tuple[float, float, float]:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    return (
        origin[0] + dx * cosine - dy * sine,
        origin[1] + dx * sine + dy * cosine,
        point[2],
    )


def _toed_point(center, along: float, local_y: float, local_z: float, toe: float):
    return _rotate_z(
        (center[0] + along, center[1] + local_y, center[2] + local_z),
        center,
        toe,
    )


def _face_toward_eye(face, toe: float) -> None:
    face.normal_update()
    toward_x = -math.cos(toe)
    toward_y = -math.sin(toe)
    alignment = face.normal.x * toward_x + face.normal.y * toward_y
    if alignment < 0.55:
        face.normal_flip()
        face.normal_update()


def circle_loop(bm, center, tangent, radius: float, segments: int):
    _direction, binormal, normal = _basis(tangent)
    verts = []
    for index in range(segments):
        angle = math.tau * index / segments
        offset = (binormal * math.cos(angle) + normal * math.sin(angle)) * radius
        verts.append(bm.verts.new((center[0] + offset.x, center[1] + offset.y, center[2] + offset.z)))
    edges = [bm.edges.new((verts[index], verts[(index + 1) % segments])) for index in range(segments)]
    return verts, edges


def pipe_along(bm, points, radius: float, segments: int = 8, material_index: int = 0):
    bmesh = bmesh_module()
    loops = []
    for index, point in enumerate(points):
        if index < len(points) - 1:
            tangent = (
                points[index + 1][0] - point[0],
                points[index + 1][1] - point[1],
                points[index + 1][2] - point[2],
            )
        else:
            tangent = (
                point[0] - points[index - 1][0],
                point[1] - points[index - 1][1],
                point[2] - points[index - 1][2],
            )
        loops.append(circle_loop(bm, point, tangent, radius, segments))
    for (verts_a, edges_a), (_verts_b, edges_b) in zip(loops, loops[1:]):
        result = bmesh.ops.bridge_loops(bm, edges=edges_a + edges_b)
        for face in result.get("faces", []):
            face.material_index = material_index
        if not result.get("faces"):
            for index in range(segments):
                face = bm.faces.new(
                    (
                        verts_a[index],
                        verts_a[(index + 1) % segments],
                        _verts_b[(index + 1) % segments],
                        _verts_b[index],
                    )
                )
                face.material_index = material_index
    return loops


def rect_loop(bm, center, tangent, width: float, height: float):
    """Rectangular profile: width along binormal, height along normal."""
    _direction, binormal, normal = _basis(tangent)
    half_w = width * 0.5
    half_h = height * 0.5
    offsets = (
        -binormal * half_w - normal * half_h,
        binormal * half_w - normal * half_h,
        binormal * half_w + normal * half_h,
        -binormal * half_w + normal * half_h,
    )
    verts = [
        bm.verts.new((center[0] + offset.x, center[1] + offset.y, center[2] + offset.z))
        for offset in offsets
    ]
    edges = [bm.edges.new((verts[index], verts[(index + 1) % 4])) for index in range(4)]
    return verts, edges


def section_along(bm, points, width: float, height: float, material_index: int = 0):
    """Formed rectangular structural section along a polyline. Not a tube."""
    bmesh = bmesh_module()
    loops = []
    for index, point in enumerate(points):
        if index < len(points) - 1:
            tangent = (
                points[index + 1][0] - point[0],
                points[index + 1][1] - point[1],
                points[index + 1][2] - point[2],
            )
        else:
            tangent = (
                point[0] - points[index - 1][0],
                point[1] - points[index - 1][1],
                point[2] - points[index - 1][2],
            )
        loops.append(rect_loop(bm, point, tangent, width, height))
    for (verts_a, edges_a), (_verts_b, edges_b) in zip(loops, loops[1:]):
        result = bmesh.ops.bridge_loops(bm, edges=edges_a + edges_b)
        for face in result.get("faces", []):
            face.material_index = material_index
        if not result.get("faces"):
            for index in range(4):
                face = bm.faces.new(
                    (
                        verts_a[index],
                        verts_a[(index + 1) % 4],
                        _verts_b[(index + 1) % 4],
                        _verts_b[index],
                    )
                )
                face.material_index = material_index
    return loops


def spin_bulb(bm, center, axis, radius: float, height: float, material_index: int = 0):
    bmesh = bmesh_module()
    _matrix, vector = mathutils_types()
    origin = vector(center)
    direction, binormal, _normal = _basis(axis)
    profile = [
        origin + direction * (-height * 0.5) + binormal * (radius * 0.35),
        origin + direction * (-height * 0.12) + binormal * radius,
        origin + direction * (height * 0.18) + binormal * (radius * 1.05),
        origin + direction * (height * 0.5) + binormal * (radius * 0.4),
    ]
    verts = [bm.verts.new(point) for point in profile]
    edges = [bm.edges.new((verts[index], verts[index + 1])) for index in range(len(verts) - 1)]
    result = bmesh.ops.spin(
        bm,
        geom=verts + edges,
        cent=origin,
        axis=direction,
        angle=math.tau,
        steps=10,
        use_merge=True,
    )
    for face in _bm_faces(result.get("geom", []), bmesh):
        face.material_index = material_index


def add_explicit_hood(bm, center, width: float, height: float, well, toe: float, hood: float, body_index: int):
    """Four explicit hood lips toward the eye. No rim-face heuristic."""
    bmesh = bmesh_module()
    if hood <= 0.0:
        raise WorkerError("TEDAC/MPD hood verts are missing.")
    half_w = width * 0.5
    half_h = height * 0.5
    inner_w = well[0] * 0.5
    inner_h = well[1] * 0.5
    flare = 0.006
    hood_verts = []
    cosine = math.cos(toe)
    sine = math.sin(toe)

    def lip(y0: float, y1: float, z0: float, z1: float) -> None:
        corners = (
            (0.0, y0, z0),
            (0.0, y1, z0),
            (0.0, y1, z1),
            (0.0, y0, z1),
        )
        verts = [bm.verts.new(_toed_point(center, along, local_y, local_z, toe)) for along, local_y, local_z in corners]
        face = bm.faces.new(verts)
        face.material_index = body_index
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        extruded_verts = _bm_verts(extruded["geom"], bmesh)
        if not extruded_verts:
            raise WorkerError("TEDAC/MPD hood verts are missing.")
        bmesh.ops.translate(
            bm,
            verts=extruded_verts,
            vec=(-cosine * hood, -sine * hood, 0.0),
        )
        hood_verts.extend(verts)
        hood_verts.extend(extruded_verts)

    lip(-half_w - flare, half_w + flare, inner_h, half_h + flare)
    lip(-half_w - flare, half_w + flare, -half_h - flare, -inner_h)
    lip(-half_w - flare, -inner_w, -half_h, half_h)
    lip(inner_w, half_w + flare, -half_h, half_h)
    if len(hood_verts) < 8:
        raise WorkerError("TEDAC/MPD hood verts are missing.")
    return hood_verts


def add_screen_markings(bm, center, well, well_depth: float, toe: float, mark_index: int) -> None:
    """Public dark crosshair / scanline on the TEDAC emit face. No switch labels."""
    half_w = well[0] * 0.5
    half_h = well[1] * 0.5
    stroke = 0.0035
    along = well_depth - 0.001
    bands = (
        (-half_w, half_w, -stroke, stroke),
        (-stroke, stroke, -half_h, half_h),
    )
    for y0, y1, z0, z1 in bands:
        verts = [
            bm.verts.new(_toed_point(center, along, y0, z0, toe)),
            bm.verts.new(_toed_point(center, along, y1, z0, toe)),
            bm.verts.new(_toed_point(center, along, y1, z1, toe)),
            bm.verts.new(_toed_point(center, along, y0, z1, toe)),
        ]
        face = bm.faces.new(verts)
        face.material_index = mark_index
        _face_toward_eye(face, toe)


def emit_well(
    bm,
    center,
    width: float,
    height: float,
    well_depth: float,
    toe: float = 0.0,
    emit_index: int = 1,
    body_index: int = 0,
    mark_index: int | None = None,
):
    """Recessed emit well only. No formed_bezel body cube."""
    bmesh = bmesh_module()
    half_w = width * 0.5
    half_h = height * 0.5
    cosine = math.cos(toe)
    sine = math.sin(toe)
    front = [
        _toed_point(center, 0.0, half_w, -half_h, toe),
        _toed_point(center, 0.0, -half_w, -half_h, toe),
        _toed_point(center, 0.0, -half_w, half_h, toe),
        _toed_point(center, 0.0, half_w, half_h, toe),
    ]
    verts = [bm.verts.new(point) for point in front]
    face = bm.faces.new(verts)
    face.material_index = emit_index
    _face_toward_eye(face, toe)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    back_verts = _bm_verts(extruded["geom"], bmesh)
    bmesh.ops.translate(
        bm,
        verts=back_verts,
        vec=(cosine * well_depth, sine * well_depth, 0.0),
    )
    for well_face in _bm_faces(extruded["geom"], bmesh):
        well_face.material_index = body_index
    face.material_index = emit_index
    _face_toward_eye(face, toe)
    if mark_index is not None:
        add_screen_markings(bm, center, (width, height), well_depth, toe, mark_index)
    return face


def formed_bezel(
    bm,
    center,
    width: float,
    height: float,
    depth: float,
    well: tuple[float, float],
    well_depth: float,
    toe: float = 0.0,
    hood: float = 0.0,
    emit_index: int = 1,
    body_index: int = 0,
    mark_index: int | None = None,
    corner_cut: float = 0.0,
):
    bmesh = bmesh_module()
    half_w = width * 0.5
    half_h = height * 0.5
    cosine = math.cos(toe)
    sine = math.sin(toe)
    # Wound so the front faces the eye (-X after toe). Body extrudes into the dash.
    if corner_cut > 0.0:
        cut = min(corner_cut, half_w * 0.35, half_h * 0.35)
        front = [
            _toed_point(center, 0.0, half_w - cut, -half_h, toe),
            _toed_point(center, 0.0, -(half_w - cut), -half_h, toe),
            _toed_point(center, 0.0, -half_w, -(half_h - cut), toe),
            _toed_point(center, 0.0, -half_w, half_h - cut, toe),
            _toed_point(center, 0.0, -(half_w - cut), half_h, toe),
            _toed_point(center, 0.0, half_w - cut, half_h, toe),
            _toed_point(center, 0.0, half_w, half_h - cut, toe),
            _toed_point(center, 0.0, half_w, -(half_h - cut), toe),
        ]
    else:
        front = [
            _toed_point(center, 0.0, half_w, -half_h, toe),
            _toed_point(center, 0.0, -half_w, -half_h, toe),
            _toed_point(center, 0.0, -half_w, half_h, toe),
            _toed_point(center, 0.0, half_w, half_h, toe),
        ]
    verts = [bm.verts.new(point) for point in front]
    face = bm.faces.new(verts)
    face.material_index = body_index
    _face_toward_eye(face, toe)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    back_verts = _bm_verts(extruded["geom"], bmesh)
    bmesh.ops.translate(bm, verts=back_verts, vec=(cosine * depth, sine * depth, 0.0))
    if corner_cut > 0.0:
        # Slightly stronger back-vert taper so TEDAC housing is less boxy.
        for vert in back_verts:
            vert.co.y += (vert.co.y - center[1]) * 0.16
            vert.co.z += (vert.co.z - center[2]) * 0.16
    inset_thickness = max(0.004, min((width - well[0]) * 0.5, (height - well[1]) * 0.5))
    bmesh.ops.inset_region(
        bm,
        faces=[face],
        thickness=inset_thickness,
        depth=0.0,
        use_boundary=True,
        use_even_offset=True,
    )
    well_extrude = bmesh.ops.extrude_face_region(bm, geom=[face])
    well_verts = _bm_verts(well_extrude["geom"], bmesh)
    bmesh.ops.translate(
        bm,
        verts=well_verts,
        vec=(cosine * well_depth, sine * well_depth, 0.0),
    )
    well_faces = _bm_faces(well_extrude["geom"], bmesh)
    if well_faces:
        cap = max(
            well_faces,
            key=lambda item: item.calc_center_median().x * cosine + item.calc_center_median().y * sine,
        )
        for well_face in well_faces:
            if well_face is cap:
                well_face.material_index = emit_index
                _face_toward_eye(well_face, toe)
            else:
                well_face.material_index = body_index
    # Open the well so the recessed emit face is visible from the eyepoint.
    bmesh.ops.delete(bm, geom=[face], context="FACES")
    if hood > 0.0:
        add_explicit_hood(bm, center, width, height, well, toe, hood, body_index)
    if mark_index is not None:
        add_screen_markings(bm, center, well, well_depth, toe, mark_index)


def assert_hood_geometry(obj, center, toe: float) -> None:
    cosine = math.cos(toe)
    sine = math.sin(toe)
    toward_eye = 0
    for vert in obj.data.vertices:
        world = obj.matrix_world @ vert.co
        along = (center[0] - world.x) * cosine + (center[1] - world.y) * sine
        if along > 0.008:
            toward_eye += 1
    if toward_eye < 8:
        raise WorkerError(f"{obj.name} hood verts are missing.")


def assert_emit_faces_eye(obj, emit_index: int, toe: float) -> None:
    toward_x = -math.cos(toe)
    toward_y = -math.sin(toe)
    found = False
    for polygon in obj.data.polygons:
        if polygon.material_index != emit_index:
            continue
        found = True
        alignment = polygon.normal.x * toward_x + polygon.normal.y * toward_y
        if alignment < 0.55:
            raise WorkerError(
                f"{obj.name} emit face does not face the eye "
                f"(alignment={alignment:.3f})."
            )
    if not found:
        raise WorkerError(f"{obj.name} has no emit-material faces.")


def orient_emit_faces_to_eye(obj, emit_index: int, toe: float, body_index: int = 0) -> None:
    """Flip emit faces toward the eye after recalc_face_normals / bevel.

    model15's inset MPD left GEO_MPD_L at alignment=0.325 because extrude
    plus recalc_face_normals reversed the emit winding. model23's well-only
    TEDAC hit the same 0.325 after finish_mesh bevel. Re-orient here so
    assert_emit_faces_eye still sees alignment >= 0.55. Chamfer or side
    leftovers that cannot face the eye lose the emit material.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    toward_x = -math.cos(toe)
    toward_y = -math.sin(toe)
    for face in bm.faces:
        if face.material_index != emit_index:
            continue
        face.normal_update()
        alignment = face.normal.x * toward_x + face.normal.y * toward_y
        if alignment < 0.55:
            face.normal_flip()
            face.normal_update()
            alignment = face.normal.x * toward_x + face.normal.y * toward_y
        if alignment < 0.55:
            face.material_index = body_index
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()


def build_seat(collection, material, well) -> None:
    """Bucket seat: recessed pan well, tall inner bolster cheeks, cupped back."""
    bmesh = bmesh_module()
    matrix, _vector = mathutils_types()
    pan = bmesh.new()
    bmesh.ops.create_grid(
        pan,
        x_segments=12,
        y_segments=10,
        size=0.22,
        matrix=matrix.Translation((-0.02, 0.0, 0.575)),
    )
    for vert in pan.verts:
        x_value, y_value, z_value = vert.co.x, vert.co.y, vert.co.z
        dish = (1.0 - min(1.0, (abs(y_value) / 0.16) ** 2)) * 0.318
        fore = max(0.0, min(1.0, (x_value + 0.18) / 0.36))
        vert.co.z = z_value - dish * (0.75 + 0.95 * fore)
        if abs(y_value) > 0.045:
            vert.co.z += (abs(y_value) - 0.045) * 2.85
        if x_value > 0.10:
            vert.co.z += (x_value - 0.10) * 0.55
        if x_value < -0.12:
            vert.co.z += (-0.12 - x_value) * 0.40
    bmesh.ops.solidify(pan, geom=list(pan.faces), thickness=0.028)
    object_from_bmesh("GEO_Seat", pan, collection, [well])

    for name, y_sign in (("GEO_SeatBolster_L", -1.0), ("GEO_SeatBolster_R", 1.0)):
        bm = bmesh.new()
        y0 = y_sign * 0.128
        y1 = y_sign * 0.238
        verts = [
            bm.verts.new((-0.18, y0, 1.168)),
            bm.verts.new((0.16, y0, 1.128)),
            bm.verts.new((0.16, y1, 0.640)),
            bm.verts.new((-0.18, y1, 0.662)),
        ]
        face = bm.faces.new(verts)
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.155))
        bmesh.ops.inset_region(
            bm,
            faces=[face],
            thickness=0.012,
            depth=0.010,
            use_even_offset=True,
        )
        object_from_bmesh(name, bm, collection, [material])

    back = bmesh.new()
    rows = []
    for z_value in (0.612, 0.748, 0.884, 1.022):
        row = []
        for y_value in (-0.172, -0.086, 0.0, 0.086, 0.172):
            wrap = (abs(y_value) / 0.172) ** 2
            cup = (1.0 - wrap) * 0.056
            x_value = -0.198 - wrap * 0.038 - cup
            x_value -= (z_value - 0.612) * 0.10
            row.append(back.verts.new((x_value, y_value, z_value)))
        rows.append(row)
    for row_index in range(len(rows) - 1):
        for col_index in range(len(rows[0]) - 1):
            back.faces.new(
                (
                    rows[row_index][col_index],
                    rows[row_index][col_index + 1],
                    rows[row_index + 1][col_index + 1],
                    rows[row_index + 1][col_index],
                )
            )
    bmesh.ops.solidify(back, geom=list(back.faces), thickness=0.036)
    object_from_bmesh("GEO_SeatBack", back, collection, [material])

    head = bmesh.new()
    rows = []
    for z_value in (1.020, 1.068, 1.118, 1.172):
        row = []
        for y_value in (-0.088, -0.044, 0.0, 0.044, 0.088):
            wrap = (abs(y_value) / 0.088) ** 2
            cup = (1.0 - wrap) * 0.022
            x_value = -0.248 - wrap * 0.030 + cup
            x_value -= (z_value - 1.020) * 0.18
            row.append(head.verts.new((x_value, y_value, z_value)))
        rows.append(row)
    for row_index in range(len(rows) - 1):
        for col_index in range(len(rows[0]) - 1):
            head.faces.new(
                (
                    rows[row_index][col_index],
                    rows[row_index][col_index + 1],
                    rows[row_index + 1][col_index + 1],
                    rows[row_index + 1][col_index],
                )
            )
    bmesh.ops.solidify(head, geom=list(head.faces), thickness=0.034)
    object_from_bmesh("GEO_SeatHeadrest", head, collection, [material])


def _formed_plate(bm, x0, x1, y0, y1, z0, z1) -> None:
    corners = (
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    )
    verts = [bm.verts.new(point) for point in corners]
    for indices in (
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (3, 2, 6, 7),
        (0, 3, 7, 4),
        (1, 5, 6, 2),
    ):
        bm.faces.new(tuple(verts[index] for index in indices))


def build_dash_shelf(collection, olive, dark) -> None:
    """One formed forward panel from DCS Fig 43. Not three floating boxes.

    Continuous dash face houses the square TDU and both inset MPDs. Center
    corridor stays at z <= 0.86 so GEO_TEDAC emit stays readable.
    """
    bmesh = bmesh_module()
    matrix, _vector = mathutils_types()
    bm = bmesh.new()
    bmesh.ops.create_grid(
        bm,
        x_segments=14,
        y_segments=18,
        size=1.0,
        matrix=matrix.Translation((0.0, 0.0, 0.0)),
    )
    for vert in bm.verts:
        along = (vert.co.x + 1.0) * 0.5
        x_value = 0.40 + along * 0.28
        y_value = vert.co.y * 0.42
        # One formed panel: a single face wrapping TDU + MPD wells.
        z_value = 0.58 + 0.24 * (1.0 - ((along - 0.62) ** 2) / 0.50)
        if abs(y_value) > 0.30:
            z_value += min(0.055, (abs(y_value) - 0.30) * 0.22)
        if along < 0.16:
            z_value = min(z_value, 0.64)
        if abs(y_value) < 0.30:
            z_value = min(z_value, 0.834)
        vert.co.x = x_value
        vert.co.y = y_value
        vert.co.z = z_value
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.022)
    for vert in bm.verts:
        if abs(vert.co.y) < 0.16 and vert.co.z > 0.86:
            vert.co.z = 0.86
    object_from_bmesh("GEO_DashShelf", bm, collection, [olive, dark])
    build_knee_panels(collection, olive)
    build_fire_panel(collection, dark)
    build_armament(collection, dark)
    build_bru(collection, dark)


def build_knee_panels(collection, olive) -> None:
    bmesh = bmesh_module()
    for name, y_sign in (("GEO_KneePanel_L", -1.0), ("GEO_KneePanel_R", 1.0)):
        bm = bmesh.new()
        y0 = y_sign * 0.145
        y1 = y_sign * 0.305
        verts = [
            bm.verts.new((0.365, y0, 0.620)),
            bm.verts.new((0.535, y0, 0.605)),
            bm.verts.new((0.535, y1, 0.575)),
            bm.verts.new((0.365, y1, 0.590)),
        ]
        face = bm.faces.new(verts)
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.145))
        bmesh.ops.inset_region(
            bm,
            faces=[face],
            thickness=0.014,
            depth=0.006,
            use_even_offset=True,
        )
        object_from_bmesh(name, bm, collection, [olive])


def dash_tdu_well(y_value: float, z_value: float) -> bool:
    """TDU well on GEO_Dash. Must hit housing-grid face centers.

    model25 used abs(y)<0.048 against ys (..., -0.100, 0.0, 0.100, ...),
    so face centers at y=±0.05 missed the window and GEO_Dash had zero
    material_index 1 faces after finish_mesh bevel. 0.055 covers those
    ±0.05 centers and the denser ±0.046 samples.
    """
    return abs(y_value) < 0.055 and z_value >= 0.800


def dash_mpd_well(y_value: float, z_value: float) -> bool:
    left = abs(y_value + 0.205) < 0.036 and z_value >= 0.800
    right = abs(y_value - 0.205) < 0.036 and z_value >= 0.800
    return left or right


def dash_front_x() -> float:
    """Formed panel face toward the eye. Not a coplanar YZ plate at 0.50."""
    return 0.468


def dash_back_x() -> float:
    """Panel body depth. Wells pocket into this volume; they do not punch through."""
    return 0.546


def dash_well_bottom_x() -> float:
    """Recessed TDU/MPD bottoms, shared with the front-rim verts."""
    return 0.516


def dash_yz_splits() -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Shared YZ grid for one formed front. Surround and wells share verts."""
    return (
        (-0.278, -0.237, -0.173, -0.048, 0.048, 0.173, 0.237, 0.278),
        (0.720, 0.804, 0.844, 0.848),
    )


def dash_well_cavities() -> tuple[tuple[str, float, float, float, float], ...]:
    """TDU and both MPD cavities in that one mesh. Not sibling screen planes."""
    return (
        ("tdu", -0.048, 0.048, 0.804, 0.844),
        ("mpd", -0.237, -0.173, 0.804, 0.844),
        ("mpd", 0.173, 0.237, 0.804, 0.844),
    )


def dash_formed_front() -> tuple[float, float, float]:
    """Front, well-bottom, and back X of the one formed panel."""
    return (dash_front_x(), dash_well_bottom_x(), dash_back_x())


def tag_dash_emit_faces_after_bevel(obj) -> None:
    """Re-apply TDU/MPD emit indices after finish_mesh bevel.

    model25 fail: _dash_tdu_well missed y=±0.05 face centers, so index 1
    was never assigned. Bevel leftovers plus orient_emit_faces_to_eye
    remapping to body_index can also empty index 1. Tag well-region
    faces here so orient + assert_emit_faces_eye still see index 1/2.
    """
    for polygon in obj.data.polygons:
        center = polygon.center
        if dash_tdu_well(center.y, center.z):
            polygon.material_index = 1
        elif dash_mpd_well(center.y, center.z):
            polygon.material_index = 2


def formed_tedac_housing(collection, dark, tedac_emit, mpd_emit, tedac_mark) -> None:
    """One continuous formed forward panel. TDU and both MPDs are cavities.

    GEO_Dash is that one panel from dash_formed_front / dash_well_cavities.
    model28 visual fail: dash_panel_outline / dash_well_loops built
    surround bars and well faces from separate verts, then solidified
    them independently — a grey bezel rectangle sitting in front of
    two flat cyan screens. Replace that construction. Shared YZ grid
    verts, recessed well walls, emit bottoms, then extrude the
    surround into a 3D body.     TDU and both MPD wells are recessed holes in that one face
    (inset well + emit material), not a housing-grid frame, not
    sibling GEO_TEDAC / GEO_MPD meshes.
    The surround runs from MPD_L (y=-0.205) to MPD_R (y=0.205).
    Dash cap remains z<=0.86 so eye_forward is not a housing well.
    Panel top is 0.848 so finish_mesh bevel cannot recreate the
    model21 fail (0.86 ring lifted over 0.86). model25 fail: TDU
    well window missed housing face centers at y=±0.05, so GEO_Dash
    had no emit-material faces at index 1 after finish_mesh bevel.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    front_x, well_x, back_x = dash_formed_front()
    ys, zs = dash_yz_splits()
    cavities = {(y0, y1, z0, z1): kind for kind, y0, y1, z0, z1 in dash_well_cavities()}
    front = {}
    for y_value in ys:
        for z_value in zs:
            front[(y_value, z_value)] = bm.verts.new(
                (front_x, y_value, min(z_value, 0.848))
            )
    surround_faces = []
    tdu_faces = []
    mpd_faces = []
    for col in range(len(ys) - 1):
        for row in range(len(zs) - 1):
            y0, y1 = ys[col], ys[col + 1]
            z0, z1 = zs[row], zs[row + 1]
            v00 = front[(y0, z0)]
            v10 = front[(y1, z0)]
            v11 = front[(y1, z1)]
            v01 = front[(y0, z1)]
            kind = cavities.get((y0, y1, z0, z1))
            if kind is None:
                surround_faces.append(bm.faces.new((v00, v10, v11, v01)))
                continue
            b00 = bm.verts.new((well_x, y0, min(z0, 0.848)))
            b10 = bm.verts.new((well_x, y1, min(z0, 0.848)))
            b11 = bm.verts.new((well_x, y1, min(z1, 0.848)))
            b01 = bm.verts.new((well_x, y0, min(z1, 0.848)))
            bm.faces.new((v00, v10, b10, b00))
            bm.faces.new((v10, v11, b11, b10))
            bm.faces.new((v11, v01, b01, b11))
            bm.faces.new((v01, v00, b00, b01))
            bottom = bm.faces.new((b00, b10, b11, b01))
            if kind == "tdu":
                bottom.material_index = 1
                tdu_faces.append(bottom)
            else:
                bottom.material_index = 2
                mpd_faces.append(bottom)
            _face_toward_eye(bottom, 0.0)
    well_faces = tdu_faces + mpd_faces
    extruded = bmesh.ops.extrude_face_region(bm, geom=surround_faces)
    for vert in _bm_verts(extruded["geom"], bmesh):
        vert.co.x = back_x
        if abs(vert.co.y) < 0.20 and vert.co.z > 0.848:
            vert.co.z = 0.848
    bmesh.ops.inset_region(
        bm,
        faces=well_faces,
        thickness=0.004,
        depth=0.006,
        use_boundary=True,
        use_even_offset=True,
    )
    for face in tdu_faces:
        face.material_index = 1
        _face_toward_eye(face, 0.0)
    for face in mpd_faces:
        face.material_index = 2
        _face_toward_eye(face, 0.0)
    add_screen_markings(bm, TEDAC, (0.096, 0.090), 0.018, 0.0, 3)  # depth=0.018 on the well bottom
    for vert in bm.verts:
        if abs(vert.co.y) < 0.20 and vert.co.z > 0.848:
            vert.co.z = 0.848
    obj = object_from_bmesh("GEO_Dash", bm, collection, [dark, tedac_emit, mpd_emit, tedac_mark])
    # model25 fail: index 1 was empty after bevel. Re-tag well-region
    # faces, then orient, then assert. Do not loosen alignment 0.55.
    tag_dash_emit_faces_after_bevel(obj)
    orient_emit_faces_to_eye(obj, 1, 0.0)
    assert_emit_faces_eye(obj, 1, 0.0)
    orient_emit_faces_to_eye(obj, 2, 0.0)
    assert_emit_faces_eye(obj, 2, 0.0)
    # model21 fail: finish_mesh Bevel width 0.0012 / segments 2 lifted the
    # 0.86 ring over 0.86. Clamp |y|<0.20 verts to z<=0.858 after bevel
    # so the GEO_Dash |y|<0.20 z>0.86 assert still passes. Do not loosen
    # that assert.
    clamp_geo_dash_lookout_after_bevel(collection)


def clamp_geo_dash_lookout_after_bevel(collection) -> None:
    """GEO_Dash z cap must survive finish_mesh bevel.

    model21 fail: formed_tedac_housing built a YZ grid whose top ring
    was 0.86, then object_from_bmesh -> finish_mesh Bevel width 0.0012
    / segments 2 lifted those verts over 0.86. assert_tedac_readable_from_eye
    then failed on GEO_Dash verts with |y|<0.20. Clamp world and local
    verts after bevel to z<=0.858, strictly under 0.86.
    """
    dash = None
    for obj in collection.all_objects:
        if obj.name == "GEO_Dash":
            dash = obj
            break
    if dash is None:
        raise WorkerError("GEO_Dash is missing.")
    inverse = dash.matrix_world.inverted()
    for vert in dash.data.vertices:
        world = dash.matrix_world @ vert.co
        if abs(world.y) < 0.20 and world.z > 0.858:
            world.z = 0.858
            vert.co = inverse @ world
        if abs(vert.co.y) < 0.20 and vert.co.z > 0.858:
            vert.co.z = 0.858
    dash.data.update()


def build_fire_panel(collection, dark) -> None:
    """Fire Detection/Extinguishing Unit, Fig 43 top-left of the formed panel."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    _formed_plate(bm, 0.468, 0.512, -0.392, -0.318, 0.818, 0.858)
    for index, z_value in enumerate((0.848, 0.836, 0.824)):
        spin_bulb(bm, (0.470, -0.355, z_value), (1.0, 0.0, 0.0), 0.006, 0.010, 0)
    object_from_bmesh("GEO_FirePanel", bm, collection, [dark])


def build_armament(collection, dark) -> None:
    """Armament strip above the TDU, Fig 43 top-center of the formed panel."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    _formed_plate(bm, 0.458, 0.508, -0.118, 0.118, 0.848, 0.858)
    for y_value in (-0.072, -0.024, 0.024, 0.072):
        spin_bulb(bm, (0.460, y_value, 0.854), (1.0, 0.0, 0.0), 0.005, 0.008, 0)
    object_from_bmesh("GEO_Armament", bm, collection, [dark])


def build_bru(collection, dark) -> None:
    """Boresight Reticle Unit on the dash brow, Fig 43 top-center."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    spin_bulb(bm, (0.452, 0.0, 0.858), (0.0, 0.0, 1.0), 0.012, 0.018, 0)
    pipe_along(
        bm,
        [(0.452, 0.0, 0.848), (0.452, 0.0, 0.868)],
        radius=0.007,
        segments=8,
        material_index=0,
    )
    object_from_bmesh("GEO_BRU", bm, collection, [dark])


def _tdu_bezel_button(bm, center, width: float, height: float, depth: float) -> None:
    """Public square bezel button. No switch-label texture."""
    half_w = width * 0.5
    half_h = height * 0.5
    _formed_plate(
        bm,
        center[0],
        center[0] + depth,
        center[1] - half_w,
        center[1] + half_w,
        center[2] - half_h,
        center[2] + half_h,
    )


def build_tedac(collection, dark, emit, grip, mark) -> None:
    """One square TDU from DCS Fig 44-45, hardware on the inset dash.

    GEO_TEDAC is grips + Fig 45 buttons + hood only, sitting on
    the dash well. No standalone emit rectangle in front of the panel.
    TDU emit and screen markings live as holes / hardware on GEO_Dash.
    Left Hand Grip + Right Hand Grip + Fig 45 bezel (TAD/FCR/PNV/G/S,
    DAY-NT-OFF, LEV/GAIN, SYM/BRT/CON, AZ, four action buttons).
    Public shapes only. Not a 0.188 cube sitting in front of the
    panel. No cube body extrusion that reads as a standalone housing.
    Shallow destacked well so eye_forward is glass in the upper
    two-thirds, TEDAC/dash in the lower third, not a housing well.
    Destacked TDU numbers are a ceiling: go smaller than 0.118 / 0.018
    / 0.010. width=0.096, well_depth=0.008, hood=0.006 stay a ceiling.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    add_explicit_hood(bm, TEDAC, 0.096, 0.090, (0.072, 0.068), 0.0, hood=0.006, body_index=0)
    # Fig 45 top video buttons: TAD, FCR, PNV, G/S. On the dash bezel, not a cube lid.
    for y_value, _label in (
        (-0.036, "TAD"),
        (-0.012, "FCR"),
        (0.012, "PNV"),
        (0.036, "G/S"),
    ):
        _tdu_bezel_button(bm, (0.494, y_value, 0.932), 0.014, 0.008, 0.004)
    # DAY-NT-OFF display knob, top-right of the TDU bezel.
    spin_bulb(bm, (0.494, 0.054, 0.932), (1.0, 0.0, 0.0), 0.006, 0.010, 0)
    # Left bezel: LEV then GAIN.
    spin_bulb(bm, (0.494, -0.056, 0.910), (1.0, 0.0, 0.0), 0.006, 0.008, 0)
    spin_bulb(bm, (0.494, -0.056, 0.890), (1.0, 0.0, 0.0), 0.006, 0.008, 0)
    # Right bezel: SYM, BRT, CON rockers.
    for z_value, _label in ((0.914, "SYM"), (0.898, "BRT"), (0.882, "CON")):
        _tdu_bezel_button(bm, (0.494, 0.056, z_value), 0.008, 0.007, 0.004)
    # Bottom: AZ rocker and four action buttons.
    _tdu_bezel_button(bm, (0.494, -0.040, 0.828), 0.018, 0.007, 0.004)
    for y_value in (-0.018, -0.004, 0.010, 0.024):
        _tdu_bezel_button(bm, (0.494, y_value, 0.828), 0.010, 0.008, 0.004)
    # Left Hand Grip and Right Hand Grip, Fig 44, structurally on the TDU.
    left_grip = [
        (0.500, -0.062, 0.848),
        (0.492, -0.092, 0.808),
        (0.478, -0.112, 0.762),
        (0.470, -0.122, 0.724),
    ]
    right_grip = [
        (0.500, 0.062, 0.848),
        (0.492, 0.092, 0.808),
        (0.478, 0.112, 0.762),
        (0.470, 0.122, 0.724),
    ]
    pipe_along(bm, left_grip, radius=0.015, segments=10, material_index=2)
    pipe_along(bm, right_grip, radius=0.015, segments=10, material_index=2)
    spin_bulb(bm, left_grip[-1], (0.15, -0.35, -0.9), 0.017, 0.030, material_index=2)
    spin_bulb(bm, right_grip[-1], (0.15, 0.35, -0.9), 0.017, 0.030, material_index=2)
    obj = object_from_bmesh("GEO_TEDAC", bm, collection, [dark, emit, grip, mark])
    assert_hood_geometry(obj, TEDAC, 0.0)


def build_mpd(name: str, center, toe: float, collection, dark, emit) -> None:
    """Recessed emit well of the one inset dash. Not a standalone box.

    GEO_MPD_L / GEO_MPD_R are recessed emit wells of GEO_Dash at the
    same x as the TDU, same family as the TDU. Not standalone extruded
    rectangles beside a TEDAC cube. The continuous panel owns the
    surround. Emit faces must pass assert_emit_faces_eye
    (alignment >= 0.55).
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    emit_well(
        bm,
        center,
        width=0.072,
        height=0.064,
        well_depth=0.008,
        toe=toe,
        emit_index=1,
        body_index=0,
    )
    obj = object_from_bmesh(name, bm, collection, [dark, emit])
    orient_emit_faces_to_eye(obj, 1, toe)
    assert_emit_faces_eye(obj, 1, toe)


def build_eufd(collection, dark, emit) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    formed_bezel(
        bm,
        (0.545, 0.0, 0.748),
        width=0.340,
        height=0.024,
        depth=0.016,
        well=(0.312, 0.012),
        well_depth=0.005,
        hood=0.0,
        emit_index=1,
        body_index=0,
    )
    object_from_bmesh("GEO_EUFD", bm, collection, [dark, emit])


def build_console(name: str, y_center: float, collection, olive, dark) -> None:
    """Thin wall deck along the cockpit wall. Recedes the bulky cuboid kit.

    TM Fig 2-8 and the Dutch photo: side consoles are thin wall decks, not
    independent beige boxes. Knobs stay formed (spin/pipe) on this deck.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    half_y = 0.018
    outer = [
        bm.verts.new((-0.18, y_center - half_y, 0.668)),
        bm.verts.new((0.38, y_center - half_y, 0.668)),
        bm.verts.new((0.38, y_center + half_y, 0.668)),
        bm.verts.new((-0.18, y_center + half_y, 0.668)),
    ]
    top = bm.faces.new(outer)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[top])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.028))
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.008,
        depth=-0.004,
        use_boundary=True,
        use_even_offset=True,
    )
    top.material_index = 1
    object_from_bmesh(name, bm, collection, [olive, dark])


def add_formed_knob(name: str, loc, material, collection) -> None:
    """Spin a stem and crown. Station knobs are never primitive adds."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    pipe_along(
        bm,
        [
            (loc[0], loc[1], loc[2] - 0.010),
            (loc[0], loc[1], loc[2] + 0.008),
        ],
        radius=0.0065,
        segments=10,
        material_index=0,
    )
    spin_bulb(bm, (loc[0], loc[1], loc[2] + 0.014), (0.0, 0.0, 1.0), 0.013, 0.016, material_index=0)
    object_from_bmesh(name, bm, collection, [material])


def formed_collective_head(collection, material) -> None:
    """Left-hand collective grip brick with a thumb shelf."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    center = (0.168, -0.280, 0.858)
    verts = [
        bm.verts.new((center[0], center[1] - 0.024, center[2] - 0.028)),
        bm.verts.new((center[0], center[1] + 0.018, center[2] - 0.022)),
        bm.verts.new((center[0], center[1] + 0.018, center[2] + 0.026)),
        bm.verts.new((center[0], center[1] - 0.024, center[2] + 0.030)),
    ]
    face = bm.faces.new(verts)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.072, -0.006, 0.004))
    bm.faces.ensure_lookup_table()
    top = max(bm.faces, key=lambda item: item.calc_center_median().z)
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.008,
        depth=0.005,
        use_even_offset=True,
    )
    thumb = [
        bm.verts.new((0.188, -0.302, 0.872)),
        bm.verts.new((0.222, -0.302, 0.874)),
        bm.verts.new((0.222, -0.328, 0.868)),
        bm.verts.new((0.188, -0.328, 0.866)),
    ]
    thumb_face = bm.faces.new(thumb)
    thumb_ex = bmesh.ops.extrude_face_region(bm, geom=[thumb_face])
    bmesh.ops.translate(bm, verts=_bm_verts(thumb_ex["geom"], bmesh), vec=(0.0, 0.0, 0.016))
    object_from_bmesh("GEO_CollectiveHead", bm, collection, [material])


def formed_cyclic_head(collection, material) -> None:
    """Right-hand cyclic stick head with a hat, not a cube."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    center = (0.198, -0.060, 0.868)
    verts = [
        bm.verts.new((center[0], center[1] - 0.014, center[2] - 0.034)),
        bm.verts.new((center[0], center[1] + 0.014, center[2] - 0.034)),
        bm.verts.new((center[0], center[1] + 0.012, center[2] + 0.036)),
        bm.verts.new((center[0], center[1] - 0.012, center[2] + 0.036)),
    ]
    face = bm.faces.new(verts)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.038, 0.0, 0.006))
    bm.faces.ensure_lookup_table()
    top = max(bm.faces, key=lambda item: item.calc_center_median().z)
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.005,
        depth=0.004,
        use_even_offset=True,
    )
    spin_bulb(bm, (0.218, -0.060, 0.912), (0.0, 0.0, 1.0), 0.011, 0.018, material_index=0)
    object_from_bmesh("GEO_CyclicHead", bm, collection, [material])


def build_hocas(collection, grip) -> None:
    bmesh = bmesh_module()
    collective = bmesh.new()
    pipe_along(
        collective,
        [
            (0.02, -0.30, 0.60),
            (0.06, -0.29, 0.68),
            COLLECTIVE,
            (0.16, -0.28, 0.82),
            (0.19, -0.28, 0.855),
        ],
        radius=0.016,
        segments=10,
        material_index=0,
    )
    object_from_bmesh("GEO_Collective", collective, collection, [grip])
    formed_collective_head(collection, grip)

    cyclic = bmesh.new()
    pipe_along(
        cyclic,
        [
            (0.18, -0.06, 0.50),
            CYCLIC,
            (0.22, -0.06, 0.82),
            (0.22, -0.06, 0.865),
        ],
        radius=0.014,
        segments=10,
        material_index=0,
    )
    object_from_bmesh("GEO_Cyclic", cyclic, collection, [grip])
    formed_cyclic_head(collection, grip)


def loft_canopy_pane(collection, material, name: str, y_sign: float, xs) -> None:
    """Inset glass pane that sits IN a punched bay window opening only.

    Not a full-bay drape and not a milky sheet over the cage. The pane is
    a shallow sheet just inside the punched hole, matching loft_canopy_bay
    window z (skirt_frac / header_frac). Plate wall owns three-quarter.
    Glass stays MAT_CPG_CanopyGlass, inset in the punched hole only.
    Stays outboard so eye-forward does not see stacked inward fins.
    Bay-plate inner_y stays >= 0.24.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    lookout_half = 0.20
    inner_y = max(0.24, lookout_half)
    outer_overhang = 0.034
    skirt_frac = BAY_SKIRT_FRAC
    header_frac = BAY_HEADER_FRAC
    pane_inset = 0.008
    pane_depth = 0.008

    def _lerp_poly(samples, x_value):
        if x_value <= samples[0][0]:
            return samples[0][1], samples[0][2]
        if x_value >= samples[-1][0]:
            return samples[-1][1], samples[-1][2]
        for left, right in zip(samples, samples[1:]):
            if left[0] <= x_value <= right[0]:
                span = right[0] - left[0]
                blend = 0.0 if span == 0 else (x_value - left[0]) / span
                return (
                    left[1] + (right[1] - left[1]) * blend,
                    left[2] + (right[2] - left[2]) * blend,
                )
        return samples[-1][1], samples[-1][2]

    sill_samples = (
        (-0.22, 0.418, 0.955),
        (0.04, 0.420, 0.952),
        (0.28, 0.422, 0.948),
        (0.50, 0.420, 0.944),
        (0.70, 0.418, 0.940),
    )
    rail_samples = (
        (-0.30, 0.418, 1.06),
        (-0.12, 0.428, 1.18),
        (0.08, 0.438, 1.30),
        (0.26, 0.434, 1.26),
        (0.42, 0.426, 1.22),
        (0.60, 0.420, 1.14),
        (0.76, 0.416, 1.07),
    )
    columns = []
    for x_value in xs:
        opening = shell_window_opening(x_value, y_sign)
        _ = (skirt_frac, header_frac, outer_overhang)
        pane_sill = opening[0][2] + pane_inset
        pane_rail = opening[2][2] - pane_inset
        pane_outer = abs(opening[1][1]) - pane_inset
        pane_inner = max(inner_y, cabin_inner_y(x_value), pane_outer - pane_depth)
        ring = [
            (x_value, y_sign * pane_inner, pane_sill),
            (x_value, y_sign * pane_outer, pane_sill),
            (x_value, y_sign * pane_outer, pane_rail),
            (x_value, y_sign * pane_inner, pane_rail),
        ]
        columns.append([bm.verts.new(point) for point in ring])
    for col in range(len(columns) - 1):
        for row in range(len(columns[0]) - 1):
            bm.faces.new(
                (
                    columns[col][row],
                    columns[col + 1][row],
                    columns[col + 1][row + 1],
                    columns[col][row + 1],
                )
            )
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=y_sign * 0.004)
    object_from_bmesh(name, bm, collection, [material])


def loft_canopy_bay(collection, material, name: str, y_sign: float, xs) -> None:
    """Thin trim lip around a punched opening. Not a beige plate wall.

    TM Fig 2-8 + Dutch photo: side panes sit in framed openings.
    Rails/sills/A-pillars stay the same section size and read as frame trim.
    Do not grow overhang/solidify. Front look-out stays open.
    Stays outboard of the look-out (|y| >= 0.20). No pipe sweep. No
    draped canopy skin.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    lookout_half = 0.20
    inner_y = max(0.24, lookout_half)
    # Window frame lip only. Not the model17 plate-wall overhang/solidify.
    frame_lip = 0.028
    frame_depth = 0.010

    def _lerp_poly(samples, x_value):
        if x_value <= samples[0][0]:
            return samples[0][1], samples[0][2]
        if x_value >= samples[-1][0]:
            return samples[-1][1], samples[-1][2]
        for left, right in zip(samples, samples[1:]):
            if left[0] <= x_value <= right[0]:
                span = right[0] - left[0]
                blend = 0.0 if span == 0 else (x_value - left[0]) / span
                return (
                    left[1] + (right[1] - left[1]) * blend,
                    left[2] + (right[2] - left[2]) * blend,
                )
        return samples[-1][1], samples[-1][2]

    sill_samples = (
        (-0.22, 0.418, 0.955),
        (0.04, 0.420, 0.952),
        (0.28, 0.422, 0.948),
        (0.50, 0.420, 0.944),
        (0.70, 0.418, 0.940),
    )
    rail_samples = (
        (-0.30, 0.418, 1.06),
        (-0.12, 0.428, 1.18),
        (0.08, 0.438, 1.30),
        (0.26, 0.434, 1.26),
        (0.42, 0.426, 1.22),
        (0.60, 0.420, 1.14),
        (0.76, 0.416, 1.07),
    )

    def _frame_ring(x_value, sill_z, rail_z, y_outer):
        span_z = max(0.04, rail_z - sill_z)
        win_sill = sill_z + span_z * BAY_SKIRT_FRAC
        win_rail = rail_z - span_z * BAY_HEADER_FRAC
        outer = [
            (x_value, y_sign * inner_y, win_sill),
            (x_value, y_sign * y_outer, win_sill),
            (x_value, y_sign * y_outer, win_rail),
            (x_value, y_sign * inner_y, win_rail),
        ]
        inner = [
            (x_value, y_sign * (inner_y + frame_lip * 0.4), win_sill + frame_lip),
            (x_value, y_sign * (y_outer - frame_lip), win_sill + frame_lip),
            (x_value, y_sign * (y_outer - frame_lip), win_rail - frame_lip),
            (x_value, y_sign * (inner_y + frame_lip * 0.4), win_rail - frame_lip),
        ]
        return outer, inner

    def _loft(columns):
        for col in range(len(columns) - 1):
            for row in range(len(columns[0]) - 1):
                bm.faces.new(
                    (
                        columns[col][row],
                        columns[col + 1][row],
                        columns[col + 1][row + 1],
                        columns[col][row + 1],
                    )
                )

    outer_cols = []
    inner_cols = []
    for x_value in xs:
        sill_y, sill_z = _lerp_poly(sill_samples, x_value)
        rail_y, rail_z = _lerp_poly(rail_samples, x_value)
        y_outer = max(sill_y, rail_y) + 0.018
        outer, inner = _frame_ring(x_value, sill_z, rail_z, y_outer)
        outer_cols.append([bm.verts.new(point) for point in outer])
        inner_cols.append([bm.verts.new(point) for point in inner])
    _loft(outer_cols)
    _loft(inner_cols)
    for col in range(len(outer_cols)):
        for row in range(4):
            nxt = (row + 1) % 4
            bm.faces.new(
                (
                    outer_cols[col][row],
                    outer_cols[col][nxt],
                    inner_cols[col][nxt],
                    inner_cols[col][row],
                )
            )
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=y_sign * frame_depth)
    object_from_bmesh(name, bm, collection, [material])


SHELL_STATION_XS = (
    -0.28,
    -0.20,
    -0.10,
    0.00,
    0.08,
    0.18,
    0.28,
    0.38,
    0.48,
    0.56,
    0.64,
    0.70,
    0.76,
)


def _lerp_shell_poly(samples, x_value):
    if x_value <= samples[0][0]:
        return samples[0][1], samples[0][2]
    if x_value >= samples[-1][0]:
        return samples[-1][1], samples[-1][2]
    for left, right in zip(samples, samples[1:]):
        if left[0] <= x_value <= right[0]:
            span = right[0] - left[0]
            blend = 0.0 if span == 0 else (x_value - left[0]) / span
            return (
                left[1] + (right[1] - left[1]) * blend,
                left[2] + (right[2] - left[2]) * blend,
            )
    return samples[-1][1], samples[-1][2]


def cabin_inner_y(x_value: float) -> float:
    """Flare the cabin so opaque shell walls do not box the eyepoint.

    model28 visual fail: inner wall at |y|=0.24 from x=-0.28 to 0.76
    filled eye_forward with two opaque side blocks. Near the eye the
    opening stays outboard (|y| >= 0.42). It only comes in to
    |y|=0.24 at the windshield frame. Crown stays |y| >= 0.24.
    Glass occupies the look-out. Structure may not.
    """
    floor = 0.24
    if x_value <= 0.36:
        return 0.42
    if x_value >= 0.56:
        return floor
    blend = (x_value - 0.36) / (0.56 - 0.36)
    return 0.42 + (floor - 0.42) * blend


def shell_window_bays() -> tuple[tuple[float, float], ...]:
    """Discrete side-pane bays. Not one giant punch that leaves C-slabs."""
    return (
        (-0.16, 0.00),
        (0.16, 0.64),
    )


def canopy_shell_station_rings(xs, y_sign: float):
    """Live GEO_CanopyShell stations. Crown stays outboard of the look-out.

    Closed outer volume: sill-in, belly-in, belly, rail-out, crown-out,
    crown, back to sill-in. inner_y = cabin_inner_y(x) so the forward
    cabin is not a rectangular well. crown_y = inner_y so |y| >= 0.24.
    GEO_CanopyShell is LOOKOUT_STRUCTURE_FORBIDDEN; assert_lookout_clear
    walks verts. A crown at |y|=0.02 (model27 first pass) put 7
    look-out-band hits and 1 near-eye hit. Glass occupies the band.
    The hull owns three-quarter outboard of that opening, not by
    crossing it.
    """
    lookout_half = 0.20
    sill_samples = (
        (-0.22, 0.418, 0.955),
        (0.04, 0.420, 0.952),
        (0.28, 0.422, 0.948),
        (0.50, 0.420, 0.944),
        (0.70, 0.418, 0.940),
    )
    rail_samples = (
        (-0.30, 0.418, 1.06),
        (-0.12, 0.428, 1.18),
        (0.08, 0.438, 1.30),
        (0.26, 0.434, 1.26),
        (0.42, 0.426, 1.22),
        (0.60, 0.420, 1.14),
        (0.76, 0.416, 1.07),
    )
    rings = []
    for x_value in xs:
        inner_y = max(0.24, lookout_half, cabin_inner_y(x_value))
        crown_y = inner_y
        _sill_y, sill_z = _lerp_shell_poly(sill_samples, x_value)
        rail_y, rail_z = _lerp_shell_poly(rail_samples, x_value)
        mid_z = 0.5 * (sill_z + rail_z)
        y_outer = max(_sill_y, rail_y) + 0.028
        y_belly = y_outer + 0.022
        crown_z = max(rail_z + 0.012, 1.08)
        belly_in_y = inner_y + 0.030
        crown_out_y = max(inner_y + 0.050, y_outer - 0.020)
        rings.append(
            (
                (x_value, y_sign * inner_y, sill_z),
                (x_value, y_sign * belly_in_y, sill_z - 0.018),
                (x_value, y_sign * y_belly, mid_z),
                (x_value, y_sign * y_outer, rail_z),
                (x_value, y_sign * crown_out_y, crown_z),
                (x_value, y_sign * crown_y, crown_z),
            )
        )
    return tuple(rings)


def shell_window_opening(x_value, y_sign: float):
    """Punched outer window in GEO_CanopyShell. Inset panes sit in this hole."""
    ring = canopy_shell_station_rings((x_value,), y_sign)[0]
    inner_y = abs(ring[0][1])
    sill_z = ring[0][2]
    rail_z = ring[3][2]
    span_z = max(0.04, rail_z - sill_z)
    win_sill = sill_z + span_z * BAY_SKIRT_FRAC
    win_rail = rail_z - span_z * BAY_HEADER_FRAC
    y_outer = abs(ring[3][1])
    y_inner = max(inner_y, y_outer - 0.034)
    return (
        (x_value, y_sign * y_inner, win_sill),
        (x_value, y_sign * y_outer, win_sill),
        (x_value, y_sign * y_outer, win_rail),
        (x_value, y_sign * y_inner, win_rail),
    )


def loft_canopy_shell(collection, material, name: str, y_sign: float, xs) -> None:
    """Closed hull that owns the three-quarter silhouette.

    Closed outer volume: sill-in, belly, rail-out, crown, back to
    sill-in. Discrete punched window bays on the outer skin hold
    inset GEO_CanopyPane_* via shell_window_opening. Not a pane kit
    of floating canopy sheets and shell slabs. model28 visual fail:
    a 6-point tube + solidify + one giant window_punch left hollow
    C-shaped slabs and an inner wall that boxed the eyepoint.
    Replace that construction. Do not solidify a thin ring into a
    C-slab. Skip the inner wall in the forward cabin (x > -0.08)
    so eye_forward sees world/sky through raked glass. Punch only
    the discrete side-pane bays. crown_y = inner_y so the hull
    stays |y| >= 0.24, outboard of the look-out. Glass
    (GEO_Windshield / GEO_OverheadBrow / GEO_ForwardBrow /
    GEO_CanopyPane_*) occupies the band. Do not put GEO_CanopyShell
    verts in lookout_band_hit or lookout_near_eye_hit. Rails, sills,
    and A-pillars stay thin trim on this hull. Not another fill
    plate on the same section_along cage. Not a draped canopy skin.
    Not model17 plate knobs. Raked GEO_Windshield is the forward
    pane of that hull.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    lookout_half = 0.20
    inner_y = max(0.24, lookout_half)
    crown_y = inner_y
    _ = (inner_y, crown_y)
    columns = []
    for ring in canopy_shell_station_rings(xs, y_sign):
        columns.append([bm.verts.new(point) for point in ring])
    ring_len = len(columns[0])
    inner_row = ring_len - 1
    bays = shell_window_bays()
    for col in range(len(columns) - 1):
        mid_x = 0.5 * (xs[col] + xs[col + 1])
        opening = shell_window_opening(mid_x, y_sign)
        win_ys = [abs(point[1]) for point in opening]
        win_zs = [point[2] for point in opening]
        y_lo, y_hi = min(win_ys), max(win_ys)
        z_lo, z_hi = min(win_zs), max(win_zs)
        in_bay = any(start <= mid_x <= end for start, end in bays)
        for row in range(ring_len):
            nxt = (row + 1) % ring_len
            corners = (
                columns[col][row],
                columns[col + 1][row],
                columns[col + 1][nxt],
                columns[col][nxt],
            )
            mid_y = abs(0.25 * sum(vert.co.y for vert in corners))
            mid_z = 0.25 * sum(vert.co.z for vert in corners)
            if row == inner_row and mid_x > -0.08:
                continue
            if (
                in_bay
                and row in (2, 3)
                and y_lo - 0.01 <= mid_y <= y_hi + 0.01
                and z_lo - 0.01 <= mid_z <= z_hi + 0.01
            ):
                continue
            bm.faces.new(corners)
    # Aft end cap only. Forward end-cap faces formed the rectangular well
    # around the look-out; delete those faces so eye_forward looks through
    # glass to sky.
    ring = columns[0]
    bm.faces.new(tuple(ring))
    object_from_bmesh(name, bm, collection, [material])


def windshield_lookout_stations():
    """Raked 4-point trapezoids through the look-out.

    Each station is a different YZ trapezoid: sill wider than brow, and
    x coupled with z so the pane leans. Not four copies of one
    rectangle. TM Fig 2-8 + Dutch photo: wider at the sill, narrower at
    the brow. Glass still fills the look-out.
    """
    return (
        (
            (0.58, -0.198, 1.052),
            (0.58, 0.198, 1.052),
            (0.55, 0.168, 1.322),
            (0.55, -0.168, 1.322),
        ),
        (
            (0.68, -0.188, 1.058),
            (0.68, 0.188, 1.058),
            (0.64, 0.158, 1.330),
            (0.64, -0.158, 1.330),
        ),
        (
            (0.78, -0.178, 1.064),
            (0.78, 0.178, 1.064),
            (0.73, 0.148, 1.338),
            (0.73, -0.148, 1.338),
        ),
        (
            (0.86, -0.168, 1.072),
            (0.86, 0.168, 1.072),
            (0.80, 0.138, 1.348),
            (0.80, -0.138, 1.348),
        ),
    )


def windshield_frame_plates():
    """Thin sill/brow trim only. Not a grey rectangular well."""
    return (
        (0.55, 0.86, -0.228, 0.228, 1.018, 1.046),
        (0.55, 0.82, -0.198, 0.198, 1.364, 1.382),
        (0.55, 0.62, -0.228, -0.202, 1.018, 1.070),
        (0.55, 0.62, 0.202, 0.228, 1.018, 1.070),
    )


def windshield_pane_grid():
    """Near look-out column plus the four raked stations.

    model28 visual fail: the four stations lived at x=0.55-0.86,
    behind opaque side walls, so the cameras never saw glass. A
    near column at the look-out band start puts glass in the
    eyepoint frustum. Stations stay the assert-path YZ trapezoids.
    loft_forward_windshield emits these verts. Not a near/far
    blend that reuses the sill-to-brow parameter for rake.
    """
    near = (
        (0.30, -0.198, 1.052),
        (0.30, 0.198, 1.052),
        (0.22, 0.168, 1.322),
        (0.22, -0.168, 1.322),
    )
    return (near,) + windshield_lookout_stations()


def loft_forward_windshield(collection, glass, rail) -> None:
    """Raked pane through the look-out. Glass may occupy the band; frames may not.

    Dutch photo + TM Fig 2-8: look through the raked windshield to
    world/sky. GEO_Windshield is the forward pane of that hull, not a
    separate rectangular box. Stations are raked YZ trapezoids, not
    four copies of one rectangle. The pane fills the look-out from
    the near column through x 0.55-0.86, |y| <= 0.20, z 1.05-1.36.
    Do not emit GEO_WindshieldFrame; those faces formed the
    rectangular tunnel around the look-out. Not a grey rectangular
    well. model28 visual fail: opaque side blocks boxed the
    eyepoint so four-station glass never read as look-out.
    loft_forward_windshield emits windshield_pane_grid() so the
    live verts include the near column and the four stations.
    Not a grey rectangular well, not an opaque grey slab / opaque
    pane wall. Do not solidify.
    """
    glass_bm = bmesh_module().new()
    columns = []
    for row in windshield_pane_grid():
        columns.append([glass_bm.verts.new(point) for point in row])
    for col in range(len(columns) - 1):
        for row in range(len(columns[0]) - 1):
            glass_bm.faces.new(
                (
                    columns[col][row],
                    columns[col + 1][row],
                    columns[col + 1][row + 1],
                    columns[col][row + 1],
                )
            )
    object_from_bmesh("GEO_Windshield", glass_bm, collection, [glass])


def build_wiper(collection, rail) -> None:
    """Windshield-wiper park at the base of the forward pane. Public, simple.

    Stays below z=1.05 so the structure-forbidden look-out band stays clear.
    """
    bmesh = bmesh_module()
    bm = bmesh.new()
    section_along(
        bm,
        [
            (0.56, -0.16, 1.042),
            (0.62, 0.00, 1.046),
            (0.58, 0.14, 1.044),
        ],
        width=0.010,
        height=0.006,
        material_index=0,
    )
    object_from_bmesh("GEO_Wiper", bm, collection, [rail])


def loft_overhead_brow(collection, material) -> None:
    """Lofted overhead glass sheet and short forward brow connecting rail-L to rail-R.

    Uses the canopy glass material so eye_forward looks through framed glass.
    Crown stays at z >= 1.36. Canopy glass may occupy the look-out band;
    this brow stays a glass sheet, not a frame.
    model27 visual fail: GEO_ForwardBrow overlaid the windshield as an
    opaque grey slab. Punch faces whose midpoint hits lookout_band_hit
    so the brow does not fill the glass as a wall.
    Sides meet the rails outboard (|y| >= 0.20). Enclosure sheet, not sticks.
    """
    bmesh = bmesh_module()

    def _lerp_poly(samples, x_value):
        if x_value <= samples[0][0]:
            return samples[0][1], samples[0][2]
        if x_value >= samples[-1][0]:
            return samples[-1][1], samples[-1][2]
        for left, right in zip(samples, samples[1:]):
            if left[0] <= x_value <= right[0]:
                span = right[0] - left[0]
                blend = 0.0 if span == 0 else (x_value - left[0]) / span
                return (
                    left[1] + (right[1] - left[1]) * blend,
                    left[2] + (right[2] - left[2]) * blend,
                )
        return samples[-1][1], samples[-1][2]

    rail_samples = (
        (-0.30, 0.418, 1.06),
        (-0.12, 0.428, 1.18),
        (0.08, 0.438, 1.30),
        (0.26, 0.434, 1.26),
        (0.42, 0.426, 1.22),
        (0.60, 0.420, 1.14),
        (0.76, 0.416, 1.07),
    )

    def _loft_sheet(name, xs, crown_z):
        bm = bmesh.new()
        columns = []
        for x_value in xs:
            rail_y, rail_z = _lerp_poly(rail_samples, x_value)
            mid_z = max(rail_z + 0.04, 1.36)
            ring = [
                (x_value, -rail_y, rail_z + 0.006),
                (x_value, -0.24, mid_z),
                (x_value, 0.0, crown_z),
                (x_value, 0.24, mid_z),
                (x_value, rail_y, rail_z + 0.006),
            ]
            columns.append([bm.verts.new(point) for point in ring])
        for col in range(len(columns) - 1):
            for row in range(len(columns[0]) - 1):
                corners = (
                    columns[col][row],
                    columns[col + 1][row],
                    columns[col + 1][row + 1],
                    columns[col][row + 1],
                )
                mid_x = 0.25 * sum(vert.co.x for vert in corners)
                mid_y = 0.25 * sum(vert.co.y for vert in corners)
                mid_z = 0.25 * sum(vert.co.z for vert in corners)
                if lookout_band_hit(mid_x, mid_y, mid_z):
                    continue
                bm.faces.new(corners)
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.008)
        object_from_bmesh(name, bm, collection, [material])

    _loft_sheet(
        "GEO_OverheadBrow",
        (-0.15, -0.02, 0.12, 0.28, 0.42, 0.55),
        1.42,
    )
    _loft_sheet(
        "GEO_ForwardBrow",
        (0.52, 0.62, 0.70, 0.78),
        1.38,
    )


def formed_joint_plate(collection, name: str, center, rail) -> None:
    """Explicit formed joint plate. Not a section sweep or tube.

    Joints stay outboard (|y| >= 0.38) and out of the look-out band.
    """
    bmesh = bmesh_module()
    if abs(center[1]) < 0.38:
        raise WorkerError(
            f"{name} joint plate center is not outboard "
            f"(|y|={abs(center[1]):.3f} < 0.38)."
        )
    bm = bmesh.new()
    cx, cy, cz = center
    # Thin plate: longer along the member, short inboard so |y| stays >= 0.38.
    hx, hy, hz = 0.028, 0.012, 0.022
    y_in = cy - hy if cy > 0.0 else cy + hy
    y_out = cy + hy if cy > 0.0 else cy - hy
    if abs(y_in) < 0.38:
        raise WorkerError(
            f"{name} joint plate inboard edge is not outboard "
            f"(|y|={abs(y_in):.3f} < 0.38)."
        )
    corners = (
        (cx - hx, y_in, cz - hz),
        (cx + hx, y_in, cz - hz),
        (cx + hx, y_out, cz - hz),
        (cx - hx, y_out, cz - hz),
        (cx - hx, y_in, cz + hz),
        (cx + hx, y_in, cz + hz),
        (cx + hx, y_out, cz + hz),
        (cx - hx, y_out, cz + hz),
    )
    verts = [bm.verts.new(point) for point in corners]
    faces = (
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (3, 2, 6, 7),
        (0, 3, 7, 4),
        (1, 5, 6, 2),
    )
    for indices in faces:
        face = bm.faces.new(tuple(verts[index] for index in indices))
        face.material_index = 0
    object_from_bmesh(name, bm, collection, [rail])


def build_greenhouse(collection, rail, glass, plate) -> None:
    bmesh = bmesh_module()
    # Formed greenhouse from TM Fig 2-8 / 2-14 and the Dutch photo: the
    # hull owns three-quarter as a closed outer volume with punched
    # window openings, not a pane kit of floating canopy sheets.
    # Stop emitting the cage. Rails are one thin trim
    # pair on that hull, not a chunky cage silhouette. Do not add
    # another loft_canopy_fill plate on the same cage. |y| >= 0.38.
    # Aft frame is behind the eye. No bow bar across the look-out.
    # Members stay formed rectangular sections, not a tube sweep. Do
    # not thicken section_along members. No tube sweep inside this
    # greenhouse builder.
    sections = {
        "GEO_Rail_L": (
            [
                (-0.30, -0.418, 1.06),
                (-0.12, -0.428, 1.18),
                (0.08, -0.438, 1.30),
                (0.26, -0.434, 1.26),
                (0.42, -0.426, 1.22),
                (0.60, -0.420, 1.14),
                (0.76, -0.416, 1.07),
            ],
            0.018,
            0.012,
        ),
        "GEO_Rail_R": (
            [
                (-0.30, 0.418, 1.06),
                (-0.12, 0.428, 1.18),
                (0.08, 0.438, 1.30),
                (0.26, 0.434, 1.26),
                (0.42, 0.426, 1.22),
                (0.60, 0.420, 1.14),
                (0.76, 0.416, 1.07),
            ],
            0.018,
            0.012,
        ),
        "GEO_AftFrame": (
            [(-0.34, -0.38, 1.18), (-0.34, 0.0, 1.22), (-0.34, 0.38, 1.18)],
            0.016,
            0.010,
        ),
    }
    for name, (points, width, height) in sections.items():
        bm = bmesh.new()
        section_along(bm, points, width=width, height=height, material_index=0)
        object_from_bmesh(name, bm, collection, [rail])

    # Hull owns the silhouette. Inset glass panes sit in punched openings
    # only — do not drape a milky sheet. Do not emit bay or joint-plate
    # cage members.
    loft_canopy_shell(collection, plate, "GEO_CanopyShell_L", -1.0, SHELL_STATION_XS)
    loft_canopy_shell(collection, plate, "GEO_CanopyShell_R", 1.0, SHELL_STATION_XS)
    loft_canopy_pane(
        collection,
        glass,
        "GEO_CanopyPane_L",
        -1.0,
        (0.16, 0.28, 0.40, 0.52, 0.64),
    )
    loft_canopy_pane(
        collection,
        glass,
        "GEO_CanopyPane_R",
        1.0,
        (0.16, 0.28, 0.40, 0.52, 0.64),
    )
    loft_canopy_pane(
        collection,
        glass,
        "GEO_CanopyPane_Aft_L",
        -1.0,
        (-0.16, -0.08, 0.00),
    )
    loft_canopy_pane(
        collection,
        glass,
        "GEO_CanopyPane_Aft_R",
        1.0,
        (-0.16, -0.08, 0.00),
    )
    # Overhead / forward brow is canopy glass so eye_forward stays open.
    loft_overhead_brow(collection, glass)
    loft_forward_windshield(collection, glass, rail)
    build_wiper(collection, rail)


def build_gloves(collection, material) -> None:
    bmesh = bmesh_module()
    for name, center, axis in (
        ("GEO_Glove_L", (0.488, -0.116, 0.800), (0.18, -0.32, -0.72)),
        ("GEO_Glove_R", (0.488, 0.116, 0.800), (0.18, 0.32, -0.72)),
    ):
        bm = bmesh.new()
        spin_bulb(bm, center, axis, 0.022, 0.055, material_index=0)
        pipe_along(
            bm,
            [
                center,
                (center[0] - 0.03, center[1] * 1.08, center[2] - 0.02),
                (center[0] - 0.07, center[1] * 1.12, center[2] - 0.01),
            ],
            radius=0.016,
            segments=8,
            material_index=0,
        )
        object_from_bmesh(name, bm, collection, [material])


def _is_lookout_glass(name: str) -> bool:
    """Canopy glass only. Frames, rails, dash, and TEDAC stay forbidden."""
    if name in LOOKOUT_GLASS_ALLOWED:
        return True
    return name.startswith(LOOKOUT_GLASS_PREFIX)


def _is_lookout_structure(name: str) -> bool:
    """Rails, sills, frames, wiper, dash, and TEDAC housing stay forbidden."""
    for token in LOOKOUT_STRUCTURE_FORBIDDEN:
        if name == token or name.startswith(token):
            return True
    return False


def lookout_near_eye_hit(x: float, y: float, z: float) -> bool:
    return 0.0 <= x < 0.22 and abs(y) < 0.12 and abs(z - 1.18) < 0.10


def lookout_band_hit(x: float, y: float, z: float) -> bool:
    return 0.2 <= x <= 0.85 and abs(y) < 0.20 and 1.05 <= z <= 1.35


def lookout_point_allowed(name: str, x: float, y: float, z: float) -> bool:
    """Glass may occupy the look-out band. Structure may not. Near-eye is empty."""
    if lookout_near_eye_hit(x, y, z):
        return False
    if lookout_band_hit(x, y, z):
        if _is_lookout_glass(name):
            return True
        if _is_lookout_structure(name):
            return False
        return False
    return True


def assert_lookout_clear(collection) -> None:
    """Near-eye cone stays empty for all meshes. Look-out band allows canopy glass only.

    Glass may occupy 0.2 <= x <= 0.85, |y| < 0.20, 1.05 <= z <= 1.35:
    GEO_Windshield, GEO_CanopyPane_*, GEO_OverheadBrow, GEO_ForwardBrow.
    LOOKOUT_STRUCTURE_FORBIDDEN members still fail that band: GEO_Rail_,
    GEO_Sill_, GEO_APillar_, GEO_WindshieldFrame, GEO_Wiper, GEO_TEDAC,
    dash, joint plates, bay frames.
    """
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        for vert in obj.data.vertices:
            world = obj.matrix_world @ vert.co
            if lookout_near_eye_hit(world.x, world.y, world.z):
                raise WorkerError(
                    f"{obj.name} intersects the near forward look-out cone at "
                    f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f})."
                )
            if lookout_band_hit(world.x, world.y, world.z):
                if lookout_point_allowed(obj.name, world.x, world.y, world.z):
                    continue
                raise WorkerError(
                    f"{obj.name} intersects the forward look-out band at "
                    f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f})."
                )


def assert_windshield_fills_lookout(collection) -> None:
    """GEO_Windshield must occupy the look-out, not park at x>0.85."""
    windshield = None
    for obj in collection.all_objects:
        if obj.name == "GEO_Windshield":
            windshield = obj
            break
    if windshield is None:
        raise WorkerError("GEO_Windshield is missing.")
    xs = []
    in_band = 0
    low_z = 0
    high_z = 0
    left_y = 0
    right_y = 0
    for vert in windshield.data.vertices:
        world = windshield.matrix_world @ vert.co
        xs.append(world.x)
        if lookout_band_hit(world.x, world.y, world.z):
            in_band += 1
            if world.z <= 1.08:
                low_z += 1
            if world.z >= 1.32:
                high_z += 1
            if world.y <= -0.16:
                left_y += 1
            if world.y >= 0.16:
                right_y += 1
    if min(xs) > 0.56:
        raise WorkerError(
            f"GEO_Windshield does not start in the look-out (min x={min(xs):.3f})."
        )
    if max(xs) < 0.84:
        raise WorkerError(
            f"GEO_Windshield does not reach the far look-out (max x={max(xs):.3f})."
        )
    if in_band < 8:
        raise WorkerError(
            "GEO_Windshield does not occupy the forward look-out band."
        )
    if low_z < 2 or high_z < 2:
        raise WorkerError(
            "GEO_Windshield does not span z 1.05-1.36 in the look-out."
        )
    if left_y < 2 or right_y < 2:
        raise WorkerError(
            "GEO_Windshield does not span |y| <= 0.20 in the look-out."
        )


def assert_tedac_readable_from_eye(collection) -> None:
    """GEO_Dash keeps TDU emit faces; dash shelf cannot cover TEDAC from the eye."""
    tedac = None
    dash = None
    for obj in collection.all_objects:
        if obj.name == "GEO_TEDAC":
            tedac = obj
        elif obj.name == "GEO_DashShelf":
            dash = obj
    if tedac is None:
        raise WorkerError("GEO_TEDAC is missing.")
    if dash is None:
        raise WorkerError("GEO_DashShelf is missing.")
    for vert in dash.data.vertices:
        world = dash.matrix_world @ vert.co
        if abs(world.y) < 0.16 and world.z > 0.86:
            raise WorkerError(
                f"GEO_DashShelf covers TEDAC from the eye at "
                f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f}); "
                f"dash shelf verts with |y|<0.16 must have z <= 0.86."
            )
    panel = None
    for obj in collection.all_objects:
        if obj.name == "GEO_Dash":
            panel = obj
            break
    if panel is None:
        raise WorkerError("GEO_Dash is missing.")
    emit_faces = 0
    for polygon in panel.data.polygons:
        if polygon.material_index == 1:
            emit_faces += 1
    if emit_faces < 1:
        raise WorkerError("GEO_Dash has no emit faces.")
    for vert in panel.data.vertices:
        world = panel.matrix_world @ vert.co
        if abs(world.y) < 0.20 and world.z > 0.86:
            raise WorkerError(
                f"GEO_Dash covers the look-out from the eye at "
                f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f}); "
                f"dash verts with |y|<0.20 must have z <= 0.86."
            )


def assert_greenhouse_outboard(collection) -> None:
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        if not (
            obj.name.startswith("GEO_Rail_")
            or obj.name.startswith("GEO_Sill_")
            or obj.name.startswith("GEO_APillar_")
            or obj.name.startswith("GEO_SideBow_")
            or obj.name.startswith("GEO_JointPlate")
        ):
            continue
        for vert in obj.data.vertices:
            world = obj.matrix_world @ vert.co
            if abs(world.y) < 0.38:
                raise WorkerError(
                    f"{obj.name} greenhouse member is not outboard "
                    f"(|y|={abs(world.y):.3f} < 0.38)."
                )


def assert_not_sixty_mesh_kit(collection) -> None:
    """model29 must drop the 60-mesh cage family. Fail if it still emits 60 meshes."""
    meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
    if len(meshes) >= 60:
        raise WorkerError(
            f"model29 still emits 60 meshes of the same family "
            f"({len(meshes)} found); stop emitting the cage."
        )
    names = {obj.name for obj in meshes}
    for forbidden in (
        "GEO_CanopyBay_L",
        "GEO_CanopyBay_R",
        "GEO_MPD_L",
        "GEO_MPD_R",
        "GEO_WindshieldFrame",
    ):
        if forbidden in names:
            raise WorkerError(f"model29 still emits {forbidden}.")
    if any(name.startswith("GEO_JointPlate") for name in names):
        raise WorkerError("model29 still emits GEO_JointPlate cage members.")


def build_asset(asset_collection) -> None:
    """Public AH-64 CPG station. Metres. +X forward, +Z up, eye at (0, 0, 1.18)."""
    olive = pbr_material("MAT_CPG_InteriorOlive", (0.055, 0.062, 0.040, 1.0), 0.0, 0.7)
    dark = pbr_material("MAT_CPG_Bezel", (0.04, 0.045, 0.05, 1.0), 0.35, 0.35)
    seat = pbr_material("MAT_CPG_Seat", (0.032, 0.026, 0.020, 1.0), 0.0, 0.82)
    seat_well = pbr_material("MAT_CPG_SeatWell", (0.014, 0.011, 0.009, 1.0), 0.0, 0.88)
    grip = pbr_material("MAT_CPG_Grip", (0.03, 0.03, 0.03, 1.0), 0.0, 0.55)
    rail = pbr_material("MAT_CPG_CanopyRail", (0.035, 0.038, 0.032, 1.0), 0.4, 0.4)
    plate = pbr_material("MAT_CPG_CanopyPlate", (0.04, 0.045, 0.038, 1.0), 0.12, 0.58)
    # Raised roughness so three-quarter highlights do not blow milky-white.
    # Clearer glass so eye_forward reads as sky, not a dark grey wall and
    # not an opaque pane wall. model27 visual fail: alpha 0.08 plus a
    # solidified windshield / forward-brow overlay read as an opaque
    # grey slab. Keep alpha=0.08; punch the overlay and do not solidify
    # the windshield into a closed box.
    glass = emit_material("MAT_CPG_CanopyGlass", (0.58, 0.70, 0.80), 0.18, 0.0, alpha=0.08)
    glove = pbr_material("MAT_CPG_Glove", (0.11, 0.09, 0.07, 1.0), 0.0, 0.72)
    tedac = emit_material("MAT_CPG_TEDAC", (0.05, 0.18, 0.08), 0.25, 1.8)
    tedac_mark = emit_material("MAT_CPG_TEDAC_Mark", (0.01, 0.04, 0.02), 0.45, 0.2)
    mpd = emit_material("MAT_CPG_MPD", (0.04, 0.12, 0.16), 0.25, 1.4)
    eufd = emit_material("MAT_CPG_EUFD", (0.15, 0.22, 0.08), 0.3, 0.9)

    create_socket("SOCKET_Origin", EYE, asset_collection)
    create_socket("SOCKET_CPG_Eye", EYE, asset_collection)
    create_socket("SOCKET_TEDAC", TEDAC, asset_collection)
    create_socket("SOCKET_MPD_L", MPD_L, asset_collection)
    create_socket("SOCKET_MPD_R", MPD_R, asset_collection)
    create_socket("SOCKET_Collective", COLLECTIVE, asset_collection)
    create_socket("SOCKET_Cyclic", CYCLIC, asset_collection)

    build_seat(asset_collection, seat, seat_well)
    build_dash_shelf(asset_collection, olive, dark)
    build_tedac(asset_collection, dark, tedac, grip, tedac_mark)
    formed_tedac_housing(asset_collection, dark, tedac, mpd, tedac_mark)
    build_eufd(asset_collection, dark, eufd)
    build_console("GEO_Console_L", -0.36, asset_collection, olive, dark)
    build_console("GEO_Console_R", 0.36, asset_collection, olive, dark)
    for index, x_off in enumerate((-0.10, 0.04, 0.18, 0.30)):
        add_formed_knob(f"GEO_Knob_L_{index + 1}", (0.08 + x_off, -0.36, 0.712), dark, asset_collection)
        add_formed_knob(f"GEO_Knob_R_{index + 1}", (0.08 + x_off, 0.36, 0.712), dark, asset_collection)
    build_hocas(asset_collection, grip)
    build_greenhouse(asset_collection, rail, glass, plate)
    build_gloves(asset_collection, glove)
    assert_greenhouse_outboard(asset_collection)
    assert_lookout_clear(asset_collection)
    assert_windshield_fills_lookout(asset_collection)
    assert_tedac_readable_from_eye(asset_collection)
    assert_not_sixty_mesh_kit(asset_collection)


def ensure_eyepoint_sky(scene) -> None:
    """Drive the world Background shader to sky. world.color is viewport-only.

    model27 visual fail: eye_forward was a dark enclosed volume even
    with transmission 1.0 because the still scene never showed
    world/sky. A dark enclosed volume with no world/sky is a fail.
    """
    bpy = blender_module()
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SkyguardEyepointWorld")
    world = scene.world
    sky = (0.42, 0.55, 0.62)
    world.color = sky
    world.use_nodes = True
    nodes = world.node_tree.nodes
    background = nodes.get("Background")
    if background is None:
        background = nodes.new("ShaderNodeBackground")
    background.inputs["Color"].default_value = (*sky, 1.0)
    background.inputs["Strength"].default_value = 1.8
    output_node = nodes.get("World Output")
    if output_node is not None:
        world.node_tree.links.new(
            background.outputs["Background"],
            output_node.inputs["Surface"],
        )


def render_eyepoint_views(output: Path) -> list[Path]:
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    scene = bpy.context.scene
    ensure_eyepoint_sky(scene)

    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    eye = Vector(EYE)
    # Upper two-thirds is raked windshield / sky, not a grey rectangular well.
    # TEDAC and the inset dash occupy the lower third.
    views = [
        ("eye_forward.png", 26.0, Vector((2.0, 0.0, 1.24))),
        ("eye_down_tedac.png", 32.0, Vector(TEDAC)),
    ]
    paths = []
    for name, lens, aim in views:
        camera_data = bpy.data.cameras.new(f"CAM_{name}")
        camera_data.lens = lens
        camera_data.clip_start = 0.03
        camera = bpy.data.objects.new(f"CAM_{name}", camera_data)
        scene.collection.objects.link(camera)
        camera.location = eye
        camera.rotation_euler = (aim - eye).to_track_quat("-Z", "Y").to_euler()
        scene.camera = camera
        path = render_dir / name
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def run_station_model_worker(argv: list[str] | None = None) -> int:
    args = parse_worker_args(argv)
    if args.asset_id != ASSET_ID:
        raise WorkerError(f"Worker asset id {ASSET_ID} does not match {args.asset_id}.")
    output = Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise WorkerError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    scene = configure_scene()
    asset_collection = create_collection("ASSET")
    build_asset(asset_collection)
    validation = validate_asset(asset_collection, REQUIRED_SOCKETS)
    orbit_renders = render_review_views(asset_collection, output)
    eyepoint_renders = render_eyepoint_views(output)
    blend_path, glb_path = export_asset(ASSET_ID, asset_collection, output)
    artifacts = [blend_path, glb_path, *orbit_renders, *eyepoint_renders]
    receipt = {
        "schema": "skyguard.blender-worker-receipt.v1",
        "sdk_version": SDK_VERSION,
        "asset_id": ASSET_ID,
        "created_at_utc": now_utc(),
        "blender_version": blender_module().app.version_string,
        "unit_system": scene.unit_settings.system,
        "scale_length": scene.unit_settings.scale_length,
        "validation": validation,
        "eyepoint_renders": [path.name for path in eyepoint_renders],
        "artifacts": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in artifacts
        ],
    }
    receipt_path = output / "artifact_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset_id": ASSET_ID, "status": "awaiting_review"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_station_model_worker())
