from __future__ import annotations

"""Governed AH-64 Hydra 70 / M261 19-tube rocket pod worker.

Public layout only. Metres. +X forward, +Y right, +Z up. Origin at the pylon attach.
Outputs go only to --output.
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
    asset_bounds,
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


ASSET_ID = "core-apache-hydra"
BODY_RADIUS = 0.205
BODY_Z = -0.240
FACE_X = 0.70
REAR_X = -0.70
TUBE_PITCH = 0.080
TUBE_ID = 0.070
TUBE_WALL = 0.036
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_Pylon",
    "SOCKET_Launch",
]
LAUNCH = (FACE_X, 0.0, BODY_Z)
PYLON = (0.0, 0.0, 0.0)


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
    # Transmission is glass-only. Opaque materials keep alpha 1.0.
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
        bevel.width = 0.0010
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


def tube_offsets(pitch: float) -> list[tuple[float, float]]:
    """19-tube hexagonal packing: 1 + 6 + 12."""
    cells = []
    for q in range(-2, 3):
        for r in range(-2, 3):
            if max(abs(q), abs(r), abs(-q - r)) <= 2:
                y_value = pitch * (q + r * 0.5)
                z_value = pitch * (r * math.sqrt(3.0) * 0.5)
                cells.append((y_value, z_value))
    if len(cells) != 19:
        raise WorkerError(f"M261 packing must be 19 tubes, got {len(cells)}.")
    return cells


def tube_world(offset: tuple[float, float], x_value: float) -> tuple[float, float, float]:
    return (x_value, offset[0], BODY_Z + offset[1])


def spin_profile_x(bm, profile, center_z: float, steps: int = 24, material_index: int = 0):
    """Spin an (x, radius) profile around +X through the body centerline."""
    bmesh = bmesh_module()
    _matrix, vector = mathutils_types()
    origin = vector((0.0, 0.0, center_z))
    axis = vector((1.0, 0.0, 0.0))
    verts = [bm.verts.new((x_value, 0.0, center_z + radius)) for x_value, radius in profile]
    edges = [bm.edges.new((verts[index], verts[index + 1])) for index in range(len(verts) - 1)]
    result = bmesh.ops.spin(
        bm,
        geom=verts + edges,
        cent=origin,
        axis=axis,
        angle=math.tau,
        steps=steps,
        use_merge=True,
    )
    for face in _bm_faces(result.get("geom", []), bmesh):
        face.material_index = material_index


def spin_ogive(bm, base, axis, radius: float, length: float, material_index: int = 0, steps: int = 12):
    bmesh = bmesh_module()
    _matrix, vector = mathutils_types()
    origin = vector(base)
    direction, binormal, _normal = _basis(axis)
    samples = (
        (0.00, 1.00),
        (0.18, 0.96),
        (0.40, 0.84),
        (0.62, 0.62),
        (0.82, 0.34),
        (1.00, 0.00),
    )
    verts = []
    for t_value, scale in samples:
        point = origin + direction * (length * t_value) + binormal * (radius * scale)
        verts.append(bm.verts.new(point))
    edges = [bm.edges.new((verts[index], verts[index + 1])) for index in range(len(verts) - 1)]
    result = bmesh.ops.spin(
        bm,
        geom=verts + edges,
        cent=origin,
        axis=direction,
        angle=math.tau,
        steps=steps,
        use_merge=True,
    )
    for face in _bm_faces(result.get("geom", []), bmesh):
        face.material_index = material_index


def add_mouth(bm, center, radius: float, depth: float, segments: int, lip: float, interior_index: int):
    bmesh = bmesh_module()
    verts, _edges = circle_loop(bm, center, (1.0, 0.0, 0.0), radius, segments)
    face = bm.faces.new(verts)
    face.material_index = 0
    bmesh.ops.inset_region(
        bm,
        faces=[face],
        thickness=lip,
        depth=0.0,
        use_boundary=True,
        use_even_offset=True,
    )
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    sign = -1.0 if depth > 0.0 else 1.0
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(sign * abs(depth), 0.0, 0.0))
    face.material_index = interior_index
    for well_face in _bm_faces(extruded["geom"], bmesh):
        well_face.material_index = interior_index


def build_pod_body(collection, olive, dark) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    spin_profile_x(
        bm,
        [
            (-0.88, 0.028),
            (-0.84, 0.090),
            (-0.78, 0.155),
            (REAR_X, BODY_RADIUS),
            (0.50, BODY_RADIUS),
            (0.62, 0.192),
            (FACE_X, 0.158),
            (0.72, 0.150),
            (0.72, 0.122),
        ],
        BODY_Z,
        steps=28,
        material_index=0,
    )
    if bm.faces:
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.006)
    for x_value, hoop_radius in ((-0.42, BODY_RADIUS + 0.004), (0.22, BODY_RADIUS + 0.004)):
        points = []
        for index in range(17):
            angle = math.tau * index / 16
            points.append((x_value, hoop_radius * math.cos(angle), BODY_Z + hoop_radius * math.sin(angle)))
        pipe_along(bm, points, radius=0.007, segments=6, material_index=0)
    conduit = [
        (-0.48, 0.0, BODY_Z + BODY_RADIUS + 0.012),
        (-0.10, 0.0, BODY_Z + BODY_RADIUS + 0.014),
        (0.18, 0.0, BODY_Z + BODY_RADIUS + 0.014),
        (0.46, 0.0, BODY_Z + BODY_RADIUS + 0.010),
    ]
    pipe_along(bm, conduit, radius=0.006, segments=8, material_index=1)
    object_from_bmesh("GEO_PodBody", bm, collection, [olive, dark])


def build_tube_cluster(collection, olive, dark) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    offsets = tube_offsets(TUBE_PITCH)
    for offset in offsets:
        pipe_along(
            bm,
            [tube_world(offset, REAR_X + 0.04), tube_world(offset, FACE_X - 0.004)],
            radius=TUBE_WALL,
            segments=10,
            material_index=0,
        )
        add_mouth(
            bm,
            tube_world(offset, FACE_X),
            radius=TUBE_ID * 0.5 + 0.004,
            depth=0.090,
            segments=12,
            lip=0.004,
            interior_index=1,
        )
        add_mouth(
            bm,
            tube_world(offset, REAR_X + 0.02),
            radius=TUBE_ID * 0.5 + 0.003,
            depth=-0.040,
            segments=10,
            lip=0.003,
            interior_index=1,
        )
    object_from_bmesh("GEO_TubeCluster", bm, collection, [olive, dark])


def build_rocket_noses(collection, warhead) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    seated = ((0.0, 0.0), (TUBE_PITCH, 0.0))
    for offset in seated:
        base = tube_world(offset, FACE_X - 0.018)
        spin_ogive(bm, base, (1.0, 0.0, 0.0), TUBE_ID * 0.48, 0.112, material_index=0, steps=14)
    object_from_bmesh("GEO_RocketNoses", bm, collection, [warhead])


def build_pylon_saddle(collection, olive, aluminum) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    top = [
        bm.verts.new((-0.12, -0.050, 0.002)),
        bm.verts.new((0.14, -0.050, 0.002)),
        bm.verts.new((0.14, 0.050, 0.002)),
        bm.verts.new((-0.12, 0.050, 0.002)),
    ]
    face = bm.faces.new(top)
    face.material_index = 0
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, -0.058))
    bmesh.ops.inset_region(
        bm,
        faces=[face],
        thickness=0.010,
        depth=0.004,
        use_boundary=True,
        use_even_offset=True,
    )
    for x_value in (-0.035, 0.055):
        plate = [
            bm.verts.new((x_value - 0.016, -0.028, 0.002)),
            bm.verts.new((x_value + 0.016, -0.028, 0.002)),
            bm.verts.new((x_value + 0.016, 0.028, 0.002)),
            bm.verts.new((x_value - 0.016, 0.028, 0.002)),
        ]
        lug = bm.faces.new(plate)
        lug.material_index = 1
        lug_ex = bmesh.ops.extrude_face_region(bm, geom=[lug])
        bmesh.ops.translate(bm, verts=_bm_verts(lug_ex["geom"], bmesh), vec=(0.0, 0.0, 0.018))
        bmesh.ops.inset_region(
            bm,
            faces=[lug],
            thickness=0.005,
            depth=0.0,
            use_boundary=True,
            use_even_offset=True,
        )
        hole = bmesh.ops.extrude_face_region(bm, geom=[lug])
        bmesh.ops.translate(bm, verts=_bm_verts(hole["geom"], bmesh), vec=(0.0, 0.0, -0.020))
        lug.material_index = 1
        pipe_along(
            bm,
            [(x_value, -0.034, 0.012), (x_value, 0.034, 0.012)],
            radius=0.0045,
            segments=8,
            material_index=1,
        )
    object_from_bmesh("GEO_PylonSaddle", bm, collection, [olive, aluminum])


def build_asset(asset_collection) -> None:
    """Public M261 19-tube 70 mm pod. Origin is the pylon attach."""
    olive = pbr_material("MAT_Hydra_OliveDrab", (0.14, 0.16, 0.08, 1.0), 0.05, 0.62)
    dark = pbr_material("MAT_Hydra_TubeInterior", (0.02, 0.02, 0.022, 1.0), 0.15, 0.72)
    aluminum = pbr_material("MAT_Hydra_AluminumLug", (0.55, 0.56, 0.57, 1.0), 0.82, 0.46)
    warhead = pbr_material("MAT_Hydra_RocketNose", (0.20, 0.21, 0.14, 1.0), 0.08, 0.48)

    create_socket("SOCKET_Origin", PYLON, asset_collection)
    create_socket("SOCKET_Pylon", PYLON, asset_collection)
    create_socket("SOCKET_Launch", LAUNCH, asset_collection)

    build_pod_body(asset_collection, olive, dark)
    build_tube_cluster(asset_collection, olive, dark)
    build_rocket_noses(asset_collection, warhead)
    build_pylon_saddle(asset_collection, olive, aluminum)


def render_extra_orbit_views(asset_collection, output: Path) -> list[Path]:
    """SDK review set is six views; add two more orbit stations for the 8-render contract."""
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    camera = bpy.context.scene.camera
    if camera is None:
        raise WorkerError("Review camera is missing after render_review_views.")
    center, radius = asset_bounds(asset_collection)
    target = Vector(center)
    views = [
        ("bottom", (0.0, -0.3, -3.6)),
        ("three_quarter_rear", (-2.6, 2.6, 1.8)),
    ]
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, direction in views:
        camera.location = target + Vector(direction) * radius
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = 55
        path = render_dir / f"{name}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def run_hydra_worker(argv: list[str] | None = None) -> int:
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
    orbit_renders.extend(render_extra_orbit_views(asset_collection, output))
    if len(orbit_renders) != 8:
        raise WorkerError(f"Expected 8 orbit renders, got {len(orbit_renders)}.")
    blend_path, glb_path = export_asset(ASSET_ID, asset_collection, output)
    artifacts = [blend_path, glb_path, *orbit_renders]
    receipt = {
        "schema": "skyguard.blender-worker-receipt.v1",
        "sdk_version": SDK_VERSION,
        "asset_id": ASSET_ID,
        "created_at_utc": now_utc(),
        "blender_version": blender_module().app.version_string,
        "unit_system": scene.unit_settings.system,
        "scale_length": scene.unit_settings.scale_length,
        "validation": validation,
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
    raise SystemExit(run_hydra_worker())
