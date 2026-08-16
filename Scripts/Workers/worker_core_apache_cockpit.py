from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "Scripts"))

from skyguard_blender_worker_sdk import (  # noqa: E402
    blender_module,
    create_socket,
    move_to_collection,
    pbr_material,
    run_worker,
)


ASSET_ID = "core-apache-cockpit"
EYE = (0.0, 0.0, 1.18)
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


def build_asset(asset_collection) -> None:
    """Public AH-64 CPG first-person blockout. Metres. Eye at (0, 0, 1.18)."""
    olive = pbr_material("MAT_CPG_InteriorOlive", (0.18, 0.20, 0.12, 1.0), 0.0, 0.7)
    dark = pbr_material("MAT_CPG_Bezel", (0.04, 0.045, 0.05, 1.0), 0.35, 0.35)
    seat = pbr_material("MAT_CPG_Seat", (0.08, 0.07, 0.05, 1.0), 0.0, 0.8)
    grip = pbr_material("MAT_CPG_Grip", (0.03, 0.03, 0.03, 1.0), 0.0, 0.55)
    rail = pbr_material("MAT_CPG_CanopyRail", (0.12, 0.13, 0.1, 1.0), 0.4, 0.4)
    tedac = emit_material("MAT_CPG_TEDAC", (0.05, 0.18, 0.08), 0.25, 1.8)
    mpd = emit_material("MAT_CPG_MPD", (0.04, 0.12, 0.16), 0.25, 1.4)
    eufd = emit_material("MAT_CPG_EUFD", (0.15, 0.22, 0.08), 0.3, 0.9)
    glass = emit_material("MAT_CPG_CanopyGlass", (0.25, 0.35, 0.4), 0.05, 0.0, 0.12)

    create_socket("SOCKET_Origin", (0.0, 0.0, 0.0), asset_collection)
    create_socket("SOCKET_CPG_Eye", EYE, asset_collection)
    create_socket("SOCKET_TEDAC", (0.40, 0.0, 0.90), asset_collection)
    create_socket("SOCKET_MPD_L", (0.40, 0.23, 0.92), asset_collection)
    create_socket("SOCKET_MPD_R", (0.40, -0.23, 0.92), asset_collection)
    create_socket("SOCKET_Collective", (0.05, 0.30, 0.70), asset_collection)
    create_socket("SOCKET_Cyclic", (0.18, -0.16, 0.62), asset_collection)

    add_box("GEO_SeatPan", (-0.12, 0.0, 0.58), (0.38, 0.42, 0.08), seat, asset_collection)
    add_box("GEO_SeatBack", (-0.28, 0.0, 0.95), (0.08, 0.42, 0.70), seat, asset_collection)
    add_box("GEO_Headrest", (-0.26, 0.0, 1.32), (0.07, 0.22, 0.12), seat, asset_collection)

    add_box("GEO_Floor", (0.10, 0.0, 0.36), (0.90, 0.78, 0.04), olive, asset_collection)
    add_box("GEO_Kick", (0.48, 0.0, 0.50), (0.06, 0.70, 0.28), olive, asset_collection)

    add_box("GEO_Dash", (0.50, 0.0, 0.72), (0.18, 0.76, 0.08), olive, asset_collection)
    add_box("GEO_GlareShield", (0.58, 0.0, 0.86), (0.20, 0.78, 0.02), dark, asset_collection)

    add_box("GEO_TEDAC_Bezel", (0.46, 0.0, 0.74), (0.04, 0.16, 0.16), dark, asset_collection)
    add_box("GEO_TEDAC_Screen", (0.482, 0.0, 0.74), (0.008, 0.127, 0.127), tedac, asset_collection)
    add_cylinder(
        "GEO_TEDAC_Grip_L",
        (0.44, 0.12, 0.64),
        0.018,
        0.11,
        grip,
        asset_collection,
        (1.2, 0.0, 0.0),
    )
    add_cylinder(
        "GEO_TEDAC_Grip_R",
        (0.44, -0.12, 0.64),
        0.018,
        0.11,
        grip,
        asset_collection,
        (-1.2, 0.0, 0.0),
    )

    add_box("GEO_MPD_L_Bezel", (0.47, 0.24, 0.76), (0.035, 0.18, 0.15), dark, asset_collection)
    add_box("GEO_MPD_L_Screen", (0.490, 0.24, 0.76), (0.006, 0.16, 0.13), mpd, asset_collection)
    add_box("GEO_MPD_R_Bezel", (0.47, -0.24, 0.76), (0.035, 0.18, 0.15), dark, asset_collection)
    add_box("GEO_MPD_R_Screen", (0.490, -0.24, 0.76), (0.006, 0.16, 0.13), mpd, asset_collection)
    add_box("GEO_EUFD", (0.50, 0.0, 0.90), (0.03, 0.34, 0.03), eufd, asset_collection)

    add_box("GEO_Console_L", (0.08, 0.36, 0.62), (0.55, 0.10, 0.16), olive, asset_collection)
    add_box("GEO_Console_R", (0.08, -0.36, 0.62), (0.55, 0.10, 0.16), olive, asset_collection)

    add_cylinder(
        "GEO_Collective",
        (0.05, 0.30, 0.70),
        0.022,
        0.28,
        grip,
        asset_collection,
        (0.0, 1.15, 0.2),
    )
    add_box("GEO_CollectiveHead", (0.16, 0.30, 0.78), (0.07, 0.04, 0.05), grip, asset_collection)
    add_cylinder(
        "GEO_Cyclic",
        (0.18, -0.16, 0.62),
        0.018,
        0.34,
        grip,
        asset_collection,
        (0.25, 0.0, 0.0),
    )
    add_box("GEO_CyclicHead", (0.18, -0.16, 0.80), (0.05, 0.035, 0.07), grip, asset_collection)

    add_box("GEO_Rail_L", (0.25, 0.42, 1.20), (1.20, 0.025, 0.035), rail, asset_collection)
    add_box("GEO_Rail_R", (0.25, -0.42, 1.20), (1.20, 0.025, 0.035), rail, asset_collection)
    add_box("GEO_BowFrame", (0.82, 0.0, 1.12), (0.03, 0.86, 0.05), rail, asset_collection)
    add_box("GEO_AftFrame", (-0.32, 0.0, 1.28), (0.03, 0.82, 0.04), rail, asset_collection)
    add_box("GEO_Glass_L", (0.30, 0.41, 1.18), (1.10, 0.008, 0.42), glass, asset_collection)
    add_box("GEO_Glass_R", (0.30, -0.41, 1.18), (1.10, 0.008, 0.42), glass, asset_collection)
    add_box("GEO_IHADSS_Frame", (0.06, 0.0, 1.20), (0.008, 0.14, 0.07), dark, asset_collection)


if __name__ == "__main__":
    raise SystemExit(run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS))
