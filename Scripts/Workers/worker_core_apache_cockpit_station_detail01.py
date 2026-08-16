from __future__ import annotations

"""Governed AH-64 CPG station-detail01 worker.

Ports the public CPG station layout (boxes / cylinders / spheres with bevels)
into the Skyguard Blender worker SDK. Outputs go only to --output. This worker
does not import a missing .blend/.glb and does not write local-only source folders.
"""

from pathlib import Path
import json
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


ASSET_ID = "core-apache-cockpit-station-detail01"
EYE = (0.0, 0.0, 1.18)
TEDAC = (0.50, 0.0, 0.88)
MPD_L = (0.482, -0.205, 0.885)
MPD_R = (0.482, 0.205, 0.885)
COLLECTIVE = (0.10, -0.28, 0.76)
CYCLIC = (0.22, -0.06, 0.70)
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_CPG_Eye",
    "SOCKET_TEDAC",
    "SOCKET_MPD_L",
    "SOCKET_MPD_R",
    "SOCKET_Collective",
    "SOCKET_Cyclic",
]


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
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.0018
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    ensure_uv0(obj)
    move_to_collection(obj, collection)
    return obj


def add_box(
    name: str,
    loc: tuple[float, float, float],
    size: tuple[float, float, float],
    material,
    collection,
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    bpy = blender_module()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return finish_mesh(obj, collection)


def add_cylinder(
    name: str,
    loc: tuple[float, float, float],
    radius: float,
    depth: float,
    material,
    collection,
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    bpy = blender_module()
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=loc,
        rotation=rot,
        vertices=24,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return finish_mesh(obj, collection)


def add_sphere(
    name: str,
    loc: tuple[float, float, float],
    radius: float,
    material,
    collection,
):
    bpy = blender_module()
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=loc,
        segments=16,
        ring_count=10,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return finish_mesh(obj, collection)


def build_asset(asset_collection) -> None:
    """Public AH-64 CPG station. Metres. +X forward, +Z up, eye at (0, 0, 1.18)."""
    olive = pbr_material("MAT_CPG_InteriorOlive", (0.18, 0.20, 0.12, 1.0), 0.0, 0.7)
    dark = pbr_material("MAT_CPG_Bezel", (0.04, 0.045, 0.05, 1.0), 0.35, 0.35)
    seat = pbr_material("MAT_CPG_Seat", (0.08, 0.07, 0.05, 1.0), 0.0, 0.8)
    grip = pbr_material("MAT_CPG_Grip", (0.03, 0.03, 0.03, 1.0), 0.0, 0.55)
    rail = pbr_material("MAT_CPG_CanopyRail", (0.12, 0.13, 0.1, 1.0), 0.4, 0.4)
    tedac = emit_material("MAT_CPG_TEDAC", (0.05, 0.18, 0.08), 0.25, 1.8)
    mpd = emit_material("MAT_CPG_MPD", (0.04, 0.12, 0.16), 0.25, 1.4)
    eufd = emit_material("MAT_CPG_EUFD", (0.15, 0.22, 0.08), 0.3, 0.9)

    create_socket("SOCKET_Origin", EYE, asset_collection)
    create_socket("SOCKET_CPG_Eye", EYE, asset_collection)
    create_socket("SOCKET_TEDAC", TEDAC, asset_collection)
    create_socket("SOCKET_MPD_L", MPD_L, asset_collection)
    create_socket("SOCKET_MPD_R", MPD_R, asset_collection)
    create_socket("SOCKET_Collective", COLLECTIVE, asset_collection)
    create_socket("SOCKET_Cyclic", CYCLIC, asset_collection)

    add_box("GEO_SeatPan", (-0.14, 0.0, 0.56), (0.40, 0.44, 0.07), seat, asset_collection)
    add_box("GEO_SeatBack", (-0.30, 0.0, 0.94), (0.08, 0.44, 0.72), seat, asset_collection)
    add_box("GEO_Headrest", (-0.28, 0.0, 1.32), (0.07, 0.22, 0.12), seat, asset_collection)
    add_box("GEO_Thigh_L", (0.06, -0.12, 0.60), (0.28, 0.12, 0.06), seat, asset_collection)
    add_box("GEO_Thigh_R", (0.06, 0.12, 0.60), (0.28, 0.12, 0.06), seat, asset_collection)
    add_box("GEO_Knee_L", (0.22, -0.13, 0.52), (0.10, 0.11, 0.10), seat, asset_collection)
    add_box("GEO_Knee_R", (0.22, 0.13, 0.52), (0.10, 0.11, 0.10), seat, asset_collection)

    add_box("GEO_Dash", (0.50, 0.0, 0.70), (0.16, 0.78, 0.08), olive, asset_collection)
    add_box("GEO_GlareShield", (0.58, 0.0, 0.84), (0.18, 0.80, 0.02), dark, asset_collection)
    add_box("GEO_Kick", (0.48, 0.0, 0.50), (0.06, 0.72, 0.28), olive, asset_collection)

    add_cylinder(
        "GEO_TEDAC_Stalk",
        (0.46, 0.0, 0.76),
        0.016,
        0.16,
        dark,
        asset_collection,
        (0.0, 1.15, 0.0),
    )
    add_box("GEO_TEDAC_Body", (0.50, 0.0, 0.88), (0.07, 0.15, 0.15), dark, asset_collection)
    add_box("GEO_TEDAC_Hood_Top", (0.535, 0.0, 0.955), (0.05, 0.15, 0.02), dark, asset_collection)
    add_box("GEO_TEDAC_Hood_Bot", (0.535, 0.0, 0.805), (0.05, 0.15, 0.02), dark, asset_collection)
    add_box("GEO_TEDAC_Hood_L", (0.535, -0.075, 0.88), (0.05, 0.02, 0.13), dark, asset_collection)
    add_box("GEO_TEDAC_Hood_R", (0.535, 0.075, 0.88), (0.05, 0.02, 0.13), dark, asset_collection)
    add_box("GEO_TEDAC_Screen", (0.538, 0.0, 0.88), (0.008, 0.118, 0.118), tedac, asset_collection)
    add_cylinder(
        "GEO_TEDAC_Optic",
        (0.56, 0.0, 0.88),
        0.018,
        0.03,
        dark,
        asset_collection,
        (0.0, 1.5708, 0.0),
    )
    add_sphere("GEO_TEDAC_Lens", (0.578, 0.0, 0.88), 0.014, tedac, asset_collection)
    add_cylinder(
        "GEO_TEDAC_Grip_L",
        (0.48, -0.12, 0.78),
        0.018,
        0.12,
        grip,
        asset_collection,
        (-1.15, 0.15, 0.0),
    )
    add_cylinder(
        "GEO_TEDAC_Grip_R",
        (0.48, 0.12, 0.78),
        0.018,
        0.12,
        grip,
        asset_collection,
        (1.15, 0.15, 0.0),
    )

    add_box(
        "GEO_MPD_L_Bezel",
        MPD_L,
        (0.04, 0.17, 0.15),
        dark,
        asset_collection,
        (0.0, 0.0, 0.22),
    )
    add_box(
        "GEO_MPD_L_Face",
        (0.500, -0.205, 0.885),
        (0.006, 0.15, 0.13),
        mpd,
        asset_collection,
        (0.0, 0.0, 0.22),
    )
    add_box(
        "GEO_MPD_R_Bezel",
        MPD_R,
        (0.04, 0.17, 0.15),
        dark,
        asset_collection,
        (0.0, 0.0, -0.22),
    )
    add_box(
        "GEO_MPD_R_Face",
        (0.500, 0.205, 0.885),
        (0.006, 0.15, 0.13),
        mpd,
        asset_collection,
        (0.0, 0.0, -0.22),
    )
    add_box("GEO_EUFD", (0.52, 0.0, 1.00), (0.03, 0.36, 0.028), eufd, asset_collection)

    add_box("GEO_Console_L", (0.08, -0.36, 0.62), (0.55, 0.10, 0.16), olive, asset_collection)
    add_box("GEO_Console_R", (0.08, 0.36, 0.62), (0.55, 0.10, 0.16), olive, asset_collection)
    for index, x_off in enumerate((-0.12, 0.02, 0.16, 0.30)):
        add_cylinder(
            f"GEO_Knob_L_{index + 1}",
            (0.08 + x_off, -0.36, 0.71),
            0.014,
            0.03,
            dark,
            asset_collection,
        )
        add_cylinder(
            f"GEO_Knob_R_{index + 1}",
            (0.08 + x_off, 0.36, 0.71),
            0.014,
            0.03,
            dark,
            asset_collection,
        )

    add_cylinder(
        "GEO_Collective",
        COLLECTIVE,
        0.022,
        0.28,
        grip,
        asset_collection,
        (0.0, 1.15, -0.2),
    )
    add_box("GEO_CollectiveHead", (0.20, -0.28, 0.84), (0.07, 0.04, 0.05), grip, asset_collection)
    add_cylinder(
        "GEO_Cyclic",
        CYCLIC,
        0.018,
        0.34,
        grip,
        asset_collection,
        (0.20, 0.0, 0.0),
    )
    add_box("GEO_CyclicHead", (0.22, -0.06, 0.88), (0.05, 0.035, 0.07), grip, asset_collection)

    add_box("GEO_Rail_L", (0.25, -0.42, 1.20), (1.20, 0.025, 0.035), rail, asset_collection)
    add_box("GEO_Rail_R", (0.25, 0.42, 1.20), (1.20, 0.025, 0.035), rail, asset_collection)
    add_box("GEO_Sill_L", (0.22, -0.40, 0.98), (1.00, 0.03, 0.02), rail, asset_collection)
    add_box("GEO_Sill_R", (0.22, 0.40, 0.98), (1.00, 0.03, 0.02), rail, asset_collection)
    add_box("GEO_BowFrame", (0.82, 0.0, 1.12), (0.03, 0.86, 0.05), rail, asset_collection)
    add_box("GEO_AftFrame", (-0.32, 0.0, 1.28), (0.03, 0.82, 0.04), rail, asset_collection)


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


def run_station_detail_worker(argv: list[str] | None = None) -> int:
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
    raise SystemExit(run_station_detail_worker())
