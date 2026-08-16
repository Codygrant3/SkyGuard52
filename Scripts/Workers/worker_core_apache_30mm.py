from __future__ import annotations

"""Governed AH-64 M230 30 mm chin-gun worker.

Chin turret modeled with bmesh (extrude, inset, solidify, spin, pipe).
Public layout only. Outputs go only to --output.
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


ASSET_ID = "core-apache-30mm"
# Metres. +X forward, +Y right, +Z up. Origin at chin-turret pivot.
MUZZLE = (1.52, 0.0, -0.02)
AMMO_FEED = (-0.08, -0.18, 0.06)
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_Turret_Pivot",
    "SOCKET_Muzzle",
    "SOCKET_Ammo_Feed",
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
    """Glass-only transmission: set alpha < 1 when any optic glass is needed."""
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


def spin_cylinder(bm, center, axis, radius: float, length: float, steps: int = 16, material_index: int = 0):
    bmesh = bmesh_module()
    _matrix, vector = mathutils_types()
    origin = vector(center)
    direction, binormal, _normal = _basis(axis)
    half = length * 0.5
    profile = [
        origin + direction * (-half) + binormal * (radius * 0.92),
        origin + direction * (-half * 0.55) + binormal * radius,
        origin + direction * (half * 0.55) + binormal * radius,
        origin + direction * half + binormal * (radius * 0.88),
    ]
    verts = [bm.verts.new(point) for point in profile]
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


def build_turret_ring(collection, gunmetal) -> None:
    bmesh = bmesh_module()
    matrix, _vector = mathutils_types()
    bm = bmesh.new()
    bmesh.ops.create_circle(
        bm,
        cap_ends=True,
        radius=0.24,
        segments=32,
        matrix=matrix.Translation((0.0, 0.0, 0.0)),
    )
    face = bm.faces[0]
    face.material_index = 0
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, 0.055))
    bmesh.ops.inset_region(
        bm,
        faces=[face],
        thickness=0.045,
        depth=0.0,
        use_boundary=True,
        use_even_offset=True,
    )
    well = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(well["geom"], bmesh), vec=(0.0, 0.0, -0.028))
    for well_face in _bm_faces(well["geom"], bmesh):
        well_face.material_index = 0
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.012)
    object_from_bmesh("GEO_TurretRing", bm, collection, [gunmetal])


def build_elevation_yoke(collection, gunmetal) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    for y_sign in (-1.0, 1.0):
        half_y = 0.028
        half_z = 0.055
        x0, x1 = -0.06, 0.18
        y0 = y_sign * 0.14
        verts = [
            bm.verts.new((x0, y0 - half_y, -half_z)),
            bm.verts.new((x1, y0 - half_y, -half_z)),
            bm.verts.new((x1, y0 + half_y, -half_z)),
            bm.verts.new((x0, y0 + half_y, -half_z)),
        ]
        face = bm.faces.new(verts)
        face.material_index = 0
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, half_z * 2.0))
        bm.faces.ensure_lookup_table()
        outer = max(
            bm.faces,
            key=lambda item: abs(item.calc_center_median().y) * (1 if item.calc_center_median().y * y_sign > 0 else 0),
        )
        bmesh.ops.inset_region(
            bm,
            faces=[outer],
            thickness=0.008,
            depth=0.004,
            use_boundary=True,
            use_even_offset=True,
        )
    # Cross-tube between yoke arms (elevation axle).
    pipe_along(
        bm,
        [(-0.01, -0.14, 0.0), (-0.01, 0.14, 0.0)],
        radius=0.022,
        segments=12,
        material_index=0,
    )
    object_from_bmesh("GEO_ElevationYoke", bm, collection, [gunmetal])


def build_receiver(collection, gunmetal) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    half_y = 0.075
    half_z = 0.070
    front = [
        bm.verts.new((0.05, -half_y, -half_z)),
        bm.verts.new((0.42, -half_y, -half_z)),
        bm.verts.new((0.42, half_y, -half_z)),
        bm.verts.new((0.05, half_y, -half_z)),
    ]
    face = bm.faces.new(front)
    face.material_index = 0
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, half_z * 2.0))
    bm.faces.ensure_lookup_table()
    top = max(bm.faces, key=lambda item: item.calc_center_median().z)
    bmesh.ops.inset_region(
        bm,
        faces=[top],
        thickness=0.014,
        depth=0.008,
        use_boundary=True,
        use_even_offset=True,
    )
    # Drive-motor housing bulge on the right.
    motor = [
        bm.verts.new((0.12, 0.070, -0.04)),
        bm.verts.new((0.34, 0.070, -0.04)),
        bm.verts.new((0.34, 0.125, -0.04)),
        bm.verts.new((0.12, 0.125, -0.04)),
    ]
    motor_face = bm.faces.new(motor)
    motor_face.material_index = 0
    motor_ex = bmesh.ops.extrude_face_region(bm, geom=[motor_face])
    bmesh.ops.translate(bm, verts=_bm_verts(motor_ex["geom"], bmesh), vec=(0.0, 0.0, 0.09))
    object_from_bmesh("GEO_Receiver", bm, collection, [gunmetal])


def build_barrel(collection, barrel_mat) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    # Main tube along +X via spin.
    spin_cylinder(
        bm,
        center=(0.95, 0.0, -0.02),
        axis=(1.0, 0.0, 0.0),
        radius=0.024,
        length=1.10,
        steps=18,
        material_index=0,
    )
    # Flash hider flare near muzzle.
    spin_cylinder(
        bm,
        center=(1.48, 0.0, -0.02),
        axis=(1.0, 0.0, 0.0),
        radius=0.038,
        length=0.085,
        steps=14,
        material_index=0,
    )
    object_from_bmesh("GEO_Barrel", bm, collection, [barrel_mat])


def build_barrel_clamp(collection, gunmetal) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    half_y = 0.038
    half_z = 0.038
    verts = [
        bm.verts.new((0.38, -half_y, -0.02 - half_z)),
        bm.verts.new((0.52, -half_y, -0.02 - half_z)),
        bm.verts.new((0.52, half_y, -0.02 - half_z)),
        bm.verts.new((0.38, half_y, -0.02 - half_z)),
    ]
    face = bm.faces.new(verts)
    face.material_index = 0
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=_bm_verts(extruded["geom"], bmesh), vec=(0.0, 0.0, half_z * 2.0))
    bm.faces.ensure_lookup_table()
    front = max(bm.faces, key=lambda item: item.calc_center_median().x)
    bmesh.ops.inset_region(
        bm,
        faces=[front],
        thickness=0.010,
        depth=0.006,
        use_boundary=True,
        use_even_offset=True,
    )
    object_from_bmesh("GEO_BarrelClamp", bm, collection, [gunmetal])


def build_ammo_chute(collection, chute_mat) -> None:
    bmesh = bmesh_module()
    bm = bmesh.new()
    # Flexible feed from receiver left side aft/up toward magazine path.
    pipe_along(
        bm,
        [
            AMMO_FEED,
            (-0.02, -0.22, 0.02),
            (0.10, -0.26, -0.04),
            (0.22, -0.20, -0.06),
            (0.30, -0.12, -0.04),
        ],
        radius=0.028,
        segments=10,
        material_index=0,
    )
    # Chute mouth collar at feed attach.
    spin_cylinder(
        bm,
        center=AMMO_FEED,
        axis=(0.2, -0.9, 0.2),
        radius=0.036,
        length=0.05,
        steps=12,
        material_index=0,
    )
    object_from_bmesh("GEO_AmmoChute", bm, collection, [chute_mat])


def build_asset(asset_collection) -> None:
    """Public AH-64 M230 chin gun. Metres. Origin at chin-turret pivot."""
    gunmetal = pbr_material("MAT_M230_Gunmetal", (0.08, 0.085, 0.09, 1.0), 0.85, 0.38)
    barrel = pbr_material("MAT_M230_BarrelHeat", (0.12, 0.07, 0.05, 1.0), 0.55, 0.42)
    chute = pbr_material("MAT_M230_ChuteOD", (0.16, 0.18, 0.10, 1.0), 0.05, 0.72)
    # emit_material reserved for glass-only optics (alpha < 1). Not required on this gun.

    create_socket("SOCKET_Origin", (0.0, 0.0, 0.0), asset_collection)
    create_socket("SOCKET_Turret_Pivot", (0.0, 0.0, 0.0), asset_collection)
    create_socket("SOCKET_Muzzle", MUZZLE, asset_collection)
    create_socket("SOCKET_Ammo_Feed", AMMO_FEED, asset_collection)

    build_turret_ring(asset_collection, gunmetal)
    build_elevation_yoke(asset_collection, gunmetal)
    build_receiver(asset_collection, gunmetal)
    build_barrel(asset_collection, barrel)
    build_barrel_clamp(asset_collection, gunmetal)
    build_ammo_chute(asset_collection, chute)


def render_extra_orbit_views(asset_collection, output: Path) -> list[Path]:
    """Two supplemental orbit angles so renders/*.png totals 8 with SDK's six."""
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    scene = bpy.context.scene
    camera = scene.camera
    if camera is None:
        raise WorkerError("REVIEW_Camera missing after render_review_views.")
    center, radius = asset_bounds(asset_collection)
    target = Vector(center)
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    extras = [
        ("bottom", (0.0, -0.4, -3.4)),
        ("three_quarter_rear", (-2.4, 2.4, 1.5)),
    ]
    paths = []
    for name, direction in extras:
        camera.location = target + Vector(direction) * radius
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = 55
        path = render_dir / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def run_m230_worker(argv: list[str] | None = None) -> int:
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
    extra_renders = render_extra_orbit_views(asset_collection, output)
    blend_path, glb_path = export_asset(ASSET_ID, asset_collection, output)
    artifacts = [blend_path, glb_path, *orbit_renders, *extra_renders]
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
    raise SystemExit(run_m230_worker())
