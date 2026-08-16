from __future__ import annotations

"""Governed AH-64 CPG station-model04 worker.

Keeps the model03 layout, sockets, look-out, hoods, emit wells, formed
seat, spun knobs, and HOCAS heads. Restores TEDAC/MPD readability from
the eye by seating the dash eyebrow below and around the screens, and
connects the outboard canopy sill to the rail at the A-pillar and
side-bow. Real bmesh only. Public layout only. Outputs go only to --output.
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


ASSET_ID = "core-apache-cockpit-station-model04"
EYE = (0.0, 0.0, 1.18)
TEDAC = (0.50, 0.0, 0.88)
MPD_L = (0.482, -0.205, 0.885)
MPD_R = (0.482, 0.205, 0.885)
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
        principled.inputs["Alpha"].default_value = alpha
        for candidate in ("Transmission Weight", "Transmission"):
            if candidate in principled.inputs:
                principled.inputs[candidate].default_value = 0.85
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
    toward_x = -math.cos(toe)
    toward_y = -math.sin(toe)
    alignment = face.normal.x * toward_x + face.normal.y * toward_y
    if alignment < 0.55:
        face.normal_flip()


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
):
    bmesh = bmesh_module()
    half_w = width * 0.5
    half_h = height * 0.5
    cosine = math.cos(toe)
    sine = math.sin(toe)
    # Wound so the front faces the eye (-X after toe). Body extrudes into the dash.
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


def build_seat(collection, material) -> None:
    """Bucket seat: dished pan, side bolsters, separate back cushion, headrest."""
    bmesh = bmesh_module()
    matrix, _vector = mathutils_types()
    pan = bmesh.new()
    bmesh.ops.create_grid(
        pan,
        x_segments=10,
        y_segments=8,
        size=0.22,
        matrix=matrix.Translation((-0.02, 0.0, 0.575)),
    )
    for vert in pan.verts:
        x_value, y_value, z_value = vert.co.x, vert.co.y, vert.co.z
        dish = (1.0 - min(1.0, (abs(y_value) / 0.20) ** 2)) * 0.032
        fore = max(0.0, min(1.0, (x_value + 0.18) / 0.36))
        vert.co.z = z_value - dish * (0.45 + 0.55 * fore)
        if abs(y_value) > 0.12:
            vert.co.z += (abs(y_value) - 0.12) * 0.55
    bmesh.ops.solidify(pan, geom=list(pan.faces), thickness=0.028)
    object_from_bmesh("GEO_Seat", pan, collection, [material])

    for name, y_sign in (("GEO_SeatBolster_L", -1.0), ("GEO_SeatBolster_R", 1.0)):
        bm = bmesh.new()
        y0 = y_sign * 0.148
        y1 = y_sign * 0.228
        verts = [
            bm.verts.new((-0.18, y0, 0.705)),
            bm.verts.new((0.16, y0, 0.678)),
            bm.verts.new((0.16, y1, 0.655)),
            bm.verts.new((-0.18, y1, 0.682)),
        ]
        face = bm.faces.new(verts)
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.085))
        bmesh.ops.inset_region(
            bm,
            faces=[face],
            thickness=0.012,
            depth=0.008,
            use_even_offset=True,
        )
        object_from_bmesh(name, bm, collection, [material])

    back = bmesh.new()
    back_face = [
        back.verts.new((-0.205, -0.175, 0.620)),
        back.verts.new((-0.205, 0.175, 0.620)),
        back.verts.new((-0.248, 0.155, 1.015)),
        back.verts.new((-0.248, -0.155, 1.015)),
    ]
    face = back.faces.new(back_face)
    extruded = bmesh.ops.extrude_face_region(back, geom=[face])
    bmesh.ops.translate(back, verts=_bm_verts(extruded["geom"], bmesh), vec=(-0.048, 0.0, 0.012))
    bmesh.ops.inset_region(
        back,
        faces=[face],
        thickness=0.018,
        depth=0.010,
        use_even_offset=True,
    )
    object_from_bmesh("GEO_SeatBack", back, collection, [material])

    head = bmesh.new()
    head_face = [
        head.verts.new((-0.242, -0.092, 1.018)),
        head.verts.new((-0.242, 0.092, 1.018)),
        head.verts.new((-0.268, 0.078, 1.168)),
        head.verts.new((-0.268, -0.078, 1.168)),
    ]
    face = head.faces.new(head_face)
    extruded = bmesh.ops.extrude_face_region(head, geom=[face])
    bmesh.ops.translate(head, verts=_bm_verts(extruded["geom"], bmesh), vec=(-0.042, 0.0, 0.008))
    bmesh.ops.inset_region(
        head,
        faces=[face],
        thickness=0.010,
        depth=0.006,
        use_even_offset=True,
    )
    object_from_bmesh("GEO_SeatHeadrest", head, collection, [material])


def build_dash_shelf(collection, olive, dark) -> None:
    """Eyebrow shelf below and around TEDAC/MPD. Not a lofted slab over the wells."""
    bmesh = bmesh_module()
    matrix, _vector = mathutils_types()
    bm = bmesh.new()
    bmesh.ops.create_grid(
        bm,
        x_segments=12,
        y_segments=14,
        size=1.0,
        matrix=matrix.Translation((0.0, 0.0, 0.0)),
    )
    for vert in bm.verts:
        along = (vert.co.x + 1.0) * 0.5
        x_value = 0.38 + along * 0.32
        y_value = vert.co.y * 0.40
        peak = 1.0 - ((along - 0.70) ** 2) / 0.55
        z_value = 0.56 + 0.26 * max(0.18, peak)
        # Rise only outboard of the screens so the eyebrow wraps around them.
        if abs(y_value) > 0.28:
            z_value += min(0.070, (abs(y_value) - 0.28) * 0.28)
        if along < 0.18:
            z_value = min(z_value, 0.64)
        # Center/MPD corridors stay under the wells (TEDAC at z=0.88).
        if abs(y_value) < 0.28:
            z_value = min(z_value, 0.834)
        vert.co.x = x_value
        vert.co.y = y_value
        vert.co.z = z_value
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.026)
    for vert in bm.verts:
        if abs(vert.co.y) < 0.16 and vert.co.z > 0.86:
            vert.co.z = 0.86
    object_from_bmesh("GEO_DashShelf", bm, collection, [olive, dark])
    build_knee_panels(collection, olive)


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


def build_tedac(collection, dark, emit, grip, mark) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    formed_bezel(
        bm,
        TEDAC,
        width=0.188,
        height=0.188,
        depth=0.070,
        well=(SCREEN_M, SCREEN_M),
        well_depth=0.022,
        hood=0.038,
        emit_index=1,
        body_index=0,
        mark_index=3,
    )
    pipe_along(
        bm,
        [(0.490, 0.0, 0.715), (0.494, 0.0, 0.792), (0.498, 0.0, 0.842)],
        radius=0.014,
        segments=10,
        material_index=0,
    )
    pipe_along(
        bm,
        [(0.545, 0.0, 0.880), (0.572, 0.0, 0.880)],
        radius=0.015,
        segments=10,
        material_index=0,
    )
    spin_bulb(bm, (0.578, 0.0, 0.880), (1.0, 0.0, 0.0), 0.013, 0.016, material_index=0)
    left_grip = [
        (0.505, -0.086, 0.855),
        (0.492, -0.112, 0.812),
        (0.478, -0.128, 0.762),
        (0.470, -0.136, 0.724),
    ]
    right_grip = [
        (0.505, 0.086, 0.855),
        (0.492, 0.112, 0.812),
        (0.478, 0.128, 0.762),
        (0.470, 0.136, 0.724),
    ]
    pipe_along(bm, left_grip, radius=0.017, segments=10, material_index=2)
    pipe_along(bm, right_grip, radius=0.017, segments=10, material_index=2)
    spin_bulb(bm, left_grip[-1], (0.15, -0.35, -0.9), 0.019, 0.034, material_index=2)
    spin_bulb(bm, right_grip[-1], (0.15, 0.35, -0.9), 0.019, 0.034, material_index=2)
    obj = object_from_bmesh("GEO_TEDAC", bm, collection, [dark, emit, grip, mark])
    assert_hood_geometry(obj, TEDAC, 0.0)
    assert_emit_faces_eye(obj, 1, 0.0)


def build_mpd(name: str, center, toe: float, collection, dark, emit) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    formed_bezel(
        bm,
        center,
        width=0.168,
        height=0.148,
        depth=0.036,
        well=(0.128, 0.112),
        well_depth=0.010,
        toe=toe,
        hood=0.016,
        emit_index=1,
        body_index=0,
    )
    obj = object_from_bmesh(name, bm, collection, [dark, emit])
    assert_hood_geometry(obj, center, toe)
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
    """Beveled console deck, not a raw extruded box."""
    bmesh = bmesh_module()
    bm = bmesh.new()
    half_y = 0.058
    outer = [
        bm.verts.new((-0.16, y_center - half_y, 0.688)),
        bm.verts.new((0.36, y_center - half_y, 0.688)),
        bm.verts.new((0.36, y_center + half_y, 0.688)),
        bm.verts.new((-0.16, y_center + half_y, 0.688)),
    ]
    top = bm.faces.new(outer)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[top])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.150))
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.016,
        depth=-0.012,
        use_boundary=True,
        use_even_offset=True,
    )
    top.material_index = 1
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.010,
        depth=0.004,
        use_boundary=True,
        use_even_offset=True,
    )
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


def build_greenhouse(collection, rail) -> None:
    bmesh = bmesh_module()
    # Continuous outboard rails and sills. A-pillar and side-bow connect sill
    # to rail so the canopy reads as a welded frame, not floating sticks.
    # |y| >= 0.38. Aft frame is behind the eye. No bow bar across the look-out.
    paths = {
        "GEO_Rail_L": [
            (-0.30, -0.41, 1.06),
            (-0.12, -0.422, 1.18),
            (0.08, -0.435, 1.30),
            (0.26, -0.430, 1.26),
            (0.42, -0.42, 1.22),
            (0.60, -0.415, 1.14),
            (0.76, -0.41, 1.07),
        ],
        "GEO_Rail_R": [
            (-0.30, 0.41, 1.06),
            (-0.12, 0.422, 1.18),
            (0.08, 0.435, 1.30),
            (0.26, 0.430, 1.26),
            (0.42, 0.42, 1.22),
            (0.60, 0.415, 1.14),
            (0.76, 0.41, 1.07),
        ],
        "GEO_Sill_L": [
            (-0.22, -0.405, 0.955),
            (0.04, -0.408, 0.952),
            (0.28, -0.41, 0.948),
            (0.50, -0.408, 0.944),
            (0.70, -0.405, 0.940),
        ],
        "GEO_Sill_R": [
            (-0.22, 0.405, 0.955),
            (0.04, 0.408, 0.952),
            (0.28, 0.41, 0.948),
            (0.50, 0.408, 0.944),
            (0.70, 0.405, 0.940),
        ],
        "GEO_APillar_L": [
            (0.70, -0.405, 0.922),
            (0.70, -0.405, 0.940),
            (0.73, -0.418, 1.000),
            (0.76, -0.41, 1.07),
            (0.76, -0.41, 1.088),
        ],
        "GEO_APillar_R": [
            (0.70, 0.405, 0.922),
            (0.70, 0.405, 0.940),
            (0.73, 0.418, 1.000),
            (0.76, 0.41, 1.07),
            (0.76, 0.41, 1.088),
        ],
        "GEO_SideBow_L": [
            (0.08, -0.408, 0.934),
            (0.08, -0.408, 0.952),
            (0.08, -0.430, 1.120),
            (0.08, -0.435, 1.30),
            (0.08, -0.435, 1.318),
        ],
        "GEO_SideBow_R": [
            (0.08, 0.408, 0.934),
            (0.08, 0.408, 0.952),
            (0.08, 0.430, 1.120),
            (0.08, 0.435, 1.30),
            (0.08, 0.435, 1.318),
        ],
        "GEO_AftFrame": [(-0.34, -0.38, 1.18), (-0.34, 0.0, 1.22), (-0.34, 0.38, 1.18)],
    }
    joints = {
        "GEO_APillar_L": (
            ((0.70, -0.405, 0.940), (0.0, 0.0, 1.0)),
            ((0.76, -0.41, 1.07), (1.0, 0.0, 0.0)),
        ),
        "GEO_APillar_R": (
            ((0.70, 0.405, 0.940), (0.0, 0.0, 1.0)),
            ((0.76, 0.41, 1.07), (1.0, 0.0, 0.0)),
        ),
        "GEO_SideBow_L": (
            ((0.08, -0.408, 0.952), (0.0, 0.0, 1.0)),
            ((0.08, -0.435, 1.30), (0.0, 0.0, 1.0)),
        ),
        "GEO_SideBow_R": (
            ((0.08, 0.408, 0.952), (0.0, 0.0, 1.0)),
            ((0.08, 0.435, 1.30), (0.0, 0.0, 1.0)),
        ),
    }
    for name, points in paths.items():
        bm = bmesh.new()
        pipe_along(bm, points, radius=0.011, segments=8, material_index=0)
        for center, axis in joints.get(name, ()):
            spin_bulb(bm, center, axis, 0.014, 0.022, material_index=0)
        object_from_bmesh(name, bm, collection, [rail])


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


def assert_lookout_clear(collection) -> None:
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        for vert in obj.data.vertices:
            world = obj.matrix_world @ vert.co
            if 0.0 <= world.x < 0.22 and abs(world.y) < 0.12 and abs(world.z - 1.18) < 0.10:
                raise WorkerError(
                    f"{obj.name} intersects the near forward look-out cone at "
                    f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f})."
                )
            if 0.2 <= world.x <= 0.85 and abs(world.y) < 0.20 and 1.05 <= world.z <= 1.35:
                raise WorkerError(
                    f"{obj.name} intersects the forward look-out band at "
                    f"({world.x:.3f}, {world.y:.3f}, {world.z:.3f})."
                )


def assert_tedac_readable_from_eye(collection) -> None:
    """GEO_TEDAC keeps emit faces; dash shelf cannot cover TEDAC from the eye."""
    tedac = None
    dash = None
    for obj in collection.all_objects:
        if obj.name == "GEO_TEDAC":
            tedac = obj
        elif obj.name == "GEO_DashShelf":
            dash = obj
    if tedac is None:
        raise WorkerError("GEO_TEDAC is missing.")
    emit_faces = 0
    for polygon in tedac.data.polygons:
        if polygon.material_index == 1:
            emit_faces += 1
    if emit_faces < 1:
        raise WorkerError("GEO_TEDAC has no emit faces.")
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


def assert_greenhouse_outboard(collection) -> None:
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        if not (
            obj.name.startswith("GEO_Rail_")
            or obj.name.startswith("GEO_Sill_")
            or obj.name.startswith("GEO_APillar_")
            or obj.name.startswith("GEO_SideBow_")
        ):
            continue
        for vert in obj.data.vertices:
            world = obj.matrix_world @ vert.co
            if abs(world.y) < 0.38:
                raise WorkerError(
                    f"{obj.name} greenhouse member is not outboard "
                    f"(|y|={abs(world.y):.3f} < 0.38)."
                )


def build_asset(asset_collection) -> None:
    """Public AH-64 CPG station. Metres. +X forward, +Z up, eye at (0, 0, 1.18)."""
    olive = pbr_material("MAT_CPG_InteriorOlive", (0.18, 0.20, 0.12, 1.0), 0.0, 0.7)
    dark = pbr_material("MAT_CPG_Bezel", (0.04, 0.045, 0.05, 1.0), 0.35, 0.35)
    seat = pbr_material("MAT_CPG_Seat", (0.08, 0.07, 0.05, 1.0), 0.0, 0.8)
    grip = pbr_material("MAT_CPG_Grip", (0.03, 0.03, 0.03, 1.0), 0.0, 0.55)
    rail = pbr_material("MAT_CPG_CanopyRail", (0.12, 0.13, 0.1, 1.0), 0.4, 0.4)
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

    build_seat(asset_collection, seat)
    build_dash_shelf(asset_collection, olive, dark)
    build_tedac(asset_collection, dark, tedac, grip, tedac_mark)
    build_mpd("GEO_MPD_L", MPD_L, 0.22, asset_collection, dark, mpd)
    build_mpd("GEO_MPD_R", MPD_R, -0.22, asset_collection, dark, mpd)
    build_eufd(asset_collection, dark, eufd)
    build_console("GEO_Console_L", -0.36, asset_collection, olive, dark)
    build_console("GEO_Console_R", 0.36, asset_collection, olive, dark)
    for index, x_off in enumerate((-0.10, 0.04, 0.18, 0.30)):
        add_formed_knob(f"GEO_Knob_L_{index + 1}", (0.08 + x_off, -0.36, 0.712), dark, asset_collection)
        add_formed_knob(f"GEO_Knob_R_{index + 1}", (0.08 + x_off, 0.36, 0.712), dark, asset_collection)
    build_hocas(asset_collection, grip)
    build_greenhouse(asset_collection, rail)
    build_gloves(asset_collection, glove)
    assert_greenhouse_outboard(asset_collection)
    assert_lookout_clear(asset_collection)
    assert_tedac_readable_from_eye(asset_collection)


def render_eyepoint_views(output: Path) -> list[Path]:
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SkyguardEyepointWorld")
    scene.world.color = (0.42, 0.55, 0.62)

    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    eye = Vector(EYE)
    views = [
        ("eye_forward.png", 26.0, Vector((2.0, 0.0, 1.02))),
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
