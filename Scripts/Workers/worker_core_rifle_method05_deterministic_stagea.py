from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ASSET_ID = "core-rifle-method05-stagea"
GATE = "P0_CORE_RIFLE_ARTIST_GRADE_METHOD05_DETERMINISTIC_STAGEA"
SEED = 520805

RAIL_TOP_WIDTH_M = 0.021209
RAIL_PROFILE_HEIGHT_M = 0.009322
RAIL_DOVETAIL_WIDTH_M = 0.018999
RAIL_GROOVE_WIDTH_M = 0.005232
RAIL_PITCH_M = 0.010008

HANDGUARD_LENGTH_M = 0.320
HANDGUARD_HALF_WIDTH_M = 0.028
HANDGUARD_HALF_HEIGHT_M = 0.032
HANDGUARD_WALL_M = 0.0032
BARREL_RADIUS_M = 0.0087
BARREL_END_X_M = 0.425

CHECKPOINT_RESOLUTION = (1600, 900)
FINAL_RESOLUTION = (2560, 1440)
REQUIRED_SOCKETS = (
    "SOCKET_Rail_Origin",
    "SOCKET_Muzzle",
    "SOCKET_Receiver_Interface",
    "SOCKET_SupportHand",
)
REQUIRED_COLLISION = "UCX_M05A_ForwardAssembly"


class WorkerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkerError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Skyguard deterministic rifle Method05 StageA worker")
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args(values)


def blender_modules():
    import bpy  # type: ignore
    import bmesh  # type: ignore
    from mathutils import Vector  # type: ignore

    return bpy, bmesh, Vector


def reset_scene() -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.resolution_x = CHECKPOINT_RESOLUTION[0]
    scene.render.resolution_y = CHECKPOINT_RESOLUTION[1]
    if scene.world is None:
        scene.world = bpy.data.worlds.new("WORLD_M05A_Review")
    scene.world.use_nodes = True
    return scene


def collection(name: str, parent: Any | None = None) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    result = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(result)
    else:
        parent.children.link(result)
    return result


def move_to_collection(obj: Any, target: Any) -> Any:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def activate(obj: Any) -> None:
    bpy, _bmesh, _Vector = blender_modules()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def finish_mesh(
    obj: Any,
    target: Any,
    material: Any,
    *,
    bevel: float = 0.00055,
    bevel_segments: int = 2,
    smooth: bool = True,
    unwrap: bool = True,
) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    move_to_collection(obj, target)
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new(name="BEVEL_M05A_ControlledSupport", type="BEVEL")
        modifier.width = bevel
        modifier.segments = bevel_segments
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(28.0)
    if smooth:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    if unwrap:
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UV0")
        activate(obj)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(62.0), island_margin=0.012)
        bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def material_fde() -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    material = bpy.data.materials.new("MAT_M05A_FDE_CoatedAluminum")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    require(principled is not None, "FDE material lacks Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.285, 0.185, 0.085, 1.0)
    principled.inputs["Metallic"].default_value = 0.72
    principled.inputs["Roughness"].default_value = 0.39
    texcoord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")
    noise.inputs["Scale"].default_value = 145.0
    noise.inputs["Detail"].default_value = 3.5
    noise.inputs["Roughness"].default_value = 0.58
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = (0.055, 0.032, 0.014, 1.0)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.62, 0.46, 0.25, 1.0)
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.00032
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def material_steel() -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    material = bpy.data.materials.new("MAT_M05A_DarkPhosphatedSteel")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    require(principled is not None, "Steel material lacks Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.018, 0.021, 0.024, 1.0)
    principled.inputs["Metallic"].default_value = 0.92
    principled.inputs["Roughness"].default_value = 0.31
    noise = nodes.new("ShaderNodeTexNoise")
    bump = nodes.new("ShaderNodeBump")
    noise.inputs["Scale"].default_value = 210.0
    noise.inputs["Detail"].default_value = 2.2
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.00018
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def material_review_wire() -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    material = bpy.data.materials.new("MAT_M05A_REVIEW_Wire")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    require(principled is not None, "Wire material lacks Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.03, 0.55, 0.95, 1.0)
    principled.inputs["Metallic"].default_value = 0.1
    principled.inputs["Roughness"].default_value = 0.24
    return material


def superellipse_point(angle: float, half_width: float, half_height: float) -> tuple[float, float]:
    exponent = 4.0
    cosine = math.cos(angle)
    sine = math.sin(angle)
    y = half_width * math.copysign(abs(cosine) ** (2.0 / exponent), cosine)
    z = half_height * math.copysign(abs(sine) ** (2.0 / exponent), sine)
    return y, z


def window_open(x_mid: float, y_mid: float, z_mid: float) -> bool:
    side_zone = abs(y_mid) >= HANDGUARD_HALF_WIDTH_M * 0.69
    vertical_zone = abs(z_mid) <= HANDGUARD_HALF_HEIGHT_M * 0.64
    if not side_zone or not vertical_zone:
        return False
    centers = (0.050, 0.108, 0.166, 0.224, 0.282)
    for center in centers:
        normalized_x = abs((x_mid - center) / 0.0225)
        normalized_z = abs(z_mid / 0.0172)
        if normalized_x**4 + normalized_z**4 < 1.0:
            return True
    return False


def build_handguard_shell_geometry() -> tuple[
    list[tuple[float, float, float]],
    list[tuple[int, ...]],
    dict[tuple[int, int], bool],
]:
    """Build the deterministic cage without importing Blender.

    Keeping this portion pure lets the offline gate prove the intended shell is
    closed and consistently connected before a governed Blender process is
    ever authorized.
    """
    longitudinal_cells = 80
    circumference_cells = 48
    vertices: list[tuple[float, float, float]] = []
    outer_index: dict[tuple[int, int], int] = {}
    inner_index: dict[tuple[int, int], int] = {}

    for longitudinal in range(longitudinal_cells + 1):
        x = HANDGUARD_LENGTH_M * longitudinal / longitudinal_cells
        taper = 1.0 - 0.045 * (x / HANDGUARD_LENGTH_M)
        for circumferential in range(circumference_cells):
            angle = 2.0 * math.pi * circumferential / circumference_cells
            outer_y, outer_z = superellipse_point(
                angle,
                HANDGUARD_HALF_WIDTH_M * taper,
                HANDGUARD_HALF_HEIGHT_M * taper,
            )
            inner_y, inner_z = superellipse_point(
                angle,
                (HANDGUARD_HALF_WIDTH_M - HANDGUARD_WALL_M) * taper,
                (HANDGUARD_HALF_HEIGHT_M - HANDGUARD_WALL_M) * taper,
            )
            outer_index[(longitudinal, circumferential)] = len(vertices)
            vertices.append((x, outer_y, outer_z))
            inner_index[(longitudinal, circumferential)] = len(vertices)
            vertices.append((x, inner_y, inner_z))

    solid: dict[tuple[int, int], bool] = {}
    for longitudinal in range(longitudinal_cells):
        x_mid = HANDGUARD_LENGTH_M * (longitudinal + 0.5) / longitudinal_cells
        for circumferential in range(circumference_cells):
            next_circumferential = (circumferential + 1) % circumference_cells
            angle_a = 2.0 * math.pi * circumferential / circumference_cells
            angle_b = 2.0 * math.pi * next_circumferential / circumference_cells
            y_a, z_a = superellipse_point(angle_a, HANDGUARD_HALF_WIDTH_M, HANDGUARD_HALF_HEIGHT_M)
            y_b, z_b = superellipse_point(angle_b, HANDGUARD_HALF_WIDTH_M, HANDGUARD_HALF_HEIGHT_M)
            end_band = x_mid < 0.017 or x_mid > HANDGUARD_LENGTH_M - 0.017
            solid[(longitudinal, circumferential)] = end_band or not window_open(
                x_mid,
                (y_a + y_b) * 0.5,
                (z_a + z_b) * 0.5,
            )

    faces: list[tuple[int, ...]] = []
    for longitudinal in range(longitudinal_cells):
        for circumferential in range(circumference_cells):
            if not solid[(longitudinal, circumferential)]:
                continue
            next_circumferential = (circumferential + 1) % circumference_cells
            o00 = outer_index[(longitudinal, circumferential)]
            o10 = outer_index[(longitudinal + 1, circumferential)]
            o11 = outer_index[(longitudinal + 1, next_circumferential)]
            o01 = outer_index[(longitudinal, next_circumferential)]
            i00 = inner_index[(longitudinal, circumferential)]
            i10 = inner_index[(longitudinal + 1, circumferential)]
            i11 = inner_index[(longitudinal + 1, next_circumferential)]
            i01 = inner_index[(longitudinal, next_circumferential)]
            faces.append((o00, o10, o11, o01))
            faces.append((i01, i11, i10, i00))

            previous_x_solid = longitudinal > 0 and solid[(longitudinal - 1, circumferential)]
            next_x_solid = longitudinal + 1 < longitudinal_cells and solid[(longitudinal + 1, circumferential)]
            previous_circ = (circumferential - 1) % circumference_cells
            previous_circ_solid = solid[(longitudinal, previous_circ)]
            next_circ_solid = solid[(longitudinal, next_circumferential)]
            if not previous_x_solid:
                faces.append((o00, o01, i01, i00))
            if not next_x_solid:
                faces.append((o11, o10, i10, i11))
            if not previous_circ_solid:
                faces.append((o10, o00, i00, i10))
            if not next_circ_solid:
                faces.append((o01, o11, i11, i01))

    used_indices = sorted({index for face in faces for index in face})
    remap = {old_index: new_index for new_index, old_index in enumerate(used_indices)}
    compact_vertices = [vertices[index] for index in used_indices]
    compact_faces = [tuple(remap[index] for index in face) for face in faces]
    return compact_vertices, compact_faces, solid


def create_handguard_shell(target: Any, material: Any) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    vertices, faces, _solid = build_handguard_shell_geometry()

    mesh = bpy.data.meshes.new("SM_M05A_HandguardShell_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=True)
    mesh.update()
    obj = bpy.data.objects.new("SM_M05A_HandguardShell", mesh)
    target.objects.link(obj)
    return finish_mesh(obj, target, material, bevel=0.00048, bevel_segments=2, smooth=True)


def append_prism(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    x_start: float,
    x_end: float,
    profile: list[tuple[float, float]],
) -> None:
    base = len(vertices)
    count = len(profile)
    vertices.extend((x_start, y, z) for y, z in profile)
    vertices.extend((x_end, y, z) for y, z in profile)
    faces.append(tuple(base + index for index in reversed(range(count))))
    faces.append(tuple(base + count + index for index in range(count)))
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((base + index, base + next_index, base + count + next_index, base + count + index))


def mesh_from_prisms(name: str, prisms: list[tuple[float, float, list[tuple[float, float]]]], target: Any, material: Any) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for x_start, x_end, profile in prisms:
        append_prism(vertices, faces, x_start, x_end, profile)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    return finish_mesh(obj, target, material, bevel=0.00032, bevel_segments=2, smooth=False)


def create_rail(target: Any, material: Any) -> list[Any]:
    shell_top = HANDGUARD_HALF_HEIGHT_M
    spine_profile = [
        (-RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top - 0.0010),
        (RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top - 0.0010),
        (RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top + 0.0022),
        (-RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top + 0.0022),
    ]
    spine = mesh_from_prisms("SM_M05A_RailSpine", [(0.0, HANDGUARD_LENGTH_M, spine_profile)], target, material)
    ridge_profile = [
        (-RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top + 0.0016),
        (-RAIL_TOP_WIDTH_M * 0.5, shell_top + 0.0051),
        (-RAIL_TOP_WIDTH_M * 0.5, shell_top + RAIL_PROFILE_HEIGHT_M),
        (RAIL_TOP_WIDTH_M * 0.5, shell_top + RAIL_PROFILE_HEIGHT_M),
        (RAIL_TOP_WIDTH_M * 0.5, shell_top + 0.0051),
        (RAIL_DOVETAIL_WIDTH_M * 0.5, shell_top + 0.0016),
    ]
    ridge_length = RAIL_PITCH_M - RAIL_GROOVE_WIDTH_M
    ridge_prisms: list[tuple[float, float, list[tuple[float, float]]]] = []
    index = 0
    while True:
        center = index * RAIL_PITCH_M + RAIL_PITCH_M * 0.5
        x_start = center - ridge_length * 0.5
        x_end = center + ridge_length * 0.5
        if x_start >= HANDGUARD_LENGTH_M:
            break
        ridge_prisms.append((max(0.0, x_start), min(HANDGUARD_LENGTH_M, x_end), ridge_profile))
        index += 1
    ridges = mesh_from_prisms("SM_M05A_RailRidges", ridge_prisms, target, material)
    return [spine, ridges]


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    target: Any,
    material: Any,
    *,
    axis: str = "X",
    vertices: int = 48,
    bevel: float = 0.00045,
) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    rotation = {
        "X": (0.0, math.pi / 2.0, 0.0),
        "Y": (math.pi / 2.0, 0.0, 0.0),
        "Z": (0.0, 0.0, 0.0),
    }[axis]
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, target, material, bevel=bevel, bevel_segments=2, smooth=True)


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    target: Any,
    material: Any,
) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=12,
        location=location,
        rotation=(0.0, math.pi / 2.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, target, material, bevel=0.0, smooth=True)


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    target: Any,
    material: Any,
    *,
    bevel: float = 0.0005,
) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish_mesh(obj, target, material, bevel=bevel, bevel_segments=2, smooth=False)


def create_body_cap_and_muzzle(target: Any, fde: Any, steel: Any) -> list[Any]:
    objects: list[Any] = []
    objects.append(add_torus("SM_M05A_BodyCapOuterRing", (HANDGUARD_LENGTH_M - 0.002, 0.0, 0.0), 0.0258, 0.0032, target, fde))
    objects.append(add_cylinder("SM_M05A_BodyCapInnerCollar", (HANDGUARD_LENGTH_M - 0.004, 0.0, 0.0), 0.0185, 0.012, target, fde, vertices=64))
    objects.append(add_cylinder("SM_M05A_Barrel", ((BARREL_END_X_M - 0.018) * 0.5, 0.0, 0.0), BARREL_RADIUS_M, BARREL_END_X_M + 0.018, target, steel, vertices=64, bevel=0.0003))
    muzzle_base_start = BARREL_END_X_M - 0.046
    objects.append(add_cylinder("SM_M05A_MuzzleBase", (muzzle_base_start + 0.010, 0.0, 0.0), 0.0112, 0.020, target, steel, vertices=56))
    tine_start = muzzle_base_start + 0.016
    tine_end = BARREL_END_X_M
    tine_length = tine_end - tine_start
    for index in range(5):
        angle = 2.0 * math.pi * index / 5.0
        radius = 0.0082
        objects.append(
            add_cylinder(
                f"SM_M05A_MuzzleTine_{index + 1:02d}",
                ((tine_start + tine_end) * 0.5, math.cos(angle) * radius, math.sin(angle) * radius),
                0.00215,
                tine_length,
                target,
                steel,
                vertices=24,
                bevel=0.00025,
            )
        )
    return objects


def create_receiver_interface(target: Any, fde: Any) -> list[Any]:
    return [
        add_torus("SM_M05A_ReceiverInterfaceRing", (0.008, 0.0, 0.0), 0.0274, 0.0025, target, fde),
        add_box("SM_M05A_ReceiverInterfaceTopBridge", (0.006, 0.0, 0.0255), (0.018, 0.022, 0.010), target, fde),
    ]


def create_side_attachment(target: Any, fde: Any, steel: Any) -> list[Any]:
    x = 0.205
    y = -HANDGUARD_HALF_WIDTH_M - 0.0035
    return [
        add_cylinder("SM_M05A_SupportedSideBoss", (x, y, -0.002), 0.0075, 0.007, target, fde, axis="Y", vertices=40),
        add_cylinder("SM_M05A_SupportedSideBossFastener", (x, y - 0.0045, -0.002), 0.0033, 0.0018, target, steel, axis="Y", vertices=32, bevel=0.0002),
    ]


def create_socket(name: str, location: tuple[float, float, float], target: Any) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.018
    obj.location = location
    target.objects.link(obj)
    return obj


def create_collision(target: Any) -> Any:
    bpy, _bmesh, _Vector = blender_modules()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(HANDGUARD_LENGTH_M * 0.5, 0.0, 0.005))
    obj = bpy.context.object
    obj.name = REQUIRED_COLLISION
    obj.dimensions = (HANDGUARD_LENGTH_M + 0.010, 0.060, 0.084)
    finish_mesh(obj, target, None, bevel=0.0, smooth=False, unwrap=True)
    obj.display_type = "WIRE"
    obj.hide_render = True
    return obj


def create_review_rig(asset: Any, shell: Any, wire_material: Any) -> dict[str, Any]:
    bpy, _bmesh, Vector = blender_modules()
    review = collection("M05A_REVIEW")
    camera_data = bpy.data.cameras.new("CAM_M05A_Review")
    camera = bpy.data.objects.new("CAM_M05A_Review", camera_data)
    review.objects.link(camera)
    bpy.context.scene.camera = camera
    camera.data.lens = 58.0
    camera.data.dof.use_dof = False
    camera.data.clip_start = 0.005
    camera.data.clip_end = 50.0

    ground_material = bpy.data.materials.new("MAT_M05A_REVIEW_Ground")
    ground_material.use_nodes = True
    ground_principled = ground_material.node_tree.nodes.get("Principled BSDF")
    require(ground_principled is not None, "Review ground lacks Principled BSDF")
    ground_principled.inputs["Base Color"].default_value = (0.025, 0.030, 0.038, 1.0)
    ground_principled.inputs["Roughness"].default_value = 0.82
    ground = add_box("REVIEW_M05A_Ground", (0.17, 0.0, -0.095), (1.4, 1.0, 0.02), review, ground_material, bevel=0.004)

    lights: list[Any] = []
    for name, location, energy, size in (
        ("REVIEW_M05A_Key", (0.10, -0.72, 0.55), 1250.0, 0.55),
        ("REVIEW_M05A_Fill", (0.26, 0.55, 0.28), 640.0, 0.42),
        ("REVIEW_M05A_Rim", (-0.10, 0.18, 0.62), 820.0, 0.34),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        move_to_collection(light, review)
        direction = Vector((0.17, 0.0, 0.0)) - light.location
        light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        lights.append(light)

    wire = bpy.data.objects.new("REVIEW_M05A_HandguardWire", shell.data.copy())
    review.objects.link(wire)
    wire.data.materials.append(wire_material)
    wire.scale = (1.0015, 1.0015, 1.0015)
    wire_modifier = wire.modifiers.new(name="REVIEW_M05A_Wireframe", type="WIREFRAME")
    wire_modifier.thickness = 0.00022
    wire_modifier.use_replace = True
    wire.hide_render = True

    return {
        "review": review,
        "camera": camera,
        "ground": ground,
        "lights": lights,
        "wire": wire,
        "asset": asset,
    }


def point_camera(camera: Any, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> None:
    _bpy, _bmesh, Vector = blender_modules()
    camera.location = location
    camera.data.lens = lens
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def configure_condition(scene: Any, rig: dict[str, Any], condition: str, fde: Any, steel: Any) -> None:
    world_nodes = scene.world.node_tree.nodes
    background = world_nodes.get("Background")
    require(background is not None, "World background node is missing")
    condition_values = {
        "daylight": ((0.19, 0.25, 0.34, 1.0), 0.72, (1250.0, 640.0, 820.0), 0.39, 0.31),
        "overcast": ((0.11, 0.13, 0.16, 1.0), 0.48, (860.0, 720.0, 520.0), 0.46, 0.38),
        "night": ((0.004, 0.008, 0.020, 1.0), 0.12, (330.0, 110.0, 520.0), 0.42, 0.28),
        "wet": ((0.075, 0.090, 0.110, 1.0), 0.36, (760.0, 520.0, 640.0), 0.24, 0.18),
        "cockpit": ((0.018, 0.024, 0.032, 1.0), 0.18, (510.0, 180.0, 720.0), 0.36, 0.26),
    }
    color, strength, energies, fde_roughness, steel_roughness = condition_values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    for light, energy in zip(rig["lights"], energies):
        light.data.energy = energy
    fde_principled = fde.node_tree.nodes.get("Principled BSDF")
    steel_principled = steel.node_tree.nodes.get("Principled BSDF")
    fde_principled.inputs["Roughness"].default_value = fde_roughness
    steel_principled.inputs["Roughness"].default_value = steel_roughness


def render_view(
    scene: Any,
    rig: dict[str, Any],
    output: Path,
    *,
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    resolution: tuple[int, int],
    condition: str,
    fde: Any,
    steel: Any,
    wire: bool = False,
) -> dict[str, Any]:
    bpy, _bmesh, _Vector = blender_modules()
    configure_condition(scene, rig, condition, fde, steel)
    rig["wire"].hide_render = not wire
    point_camera(rig["camera"], location, target, lens)
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.filepath = str(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    require(output.is_file() and output.stat().st_size > 4096, f"Render missing or too small: {output}")
    return {
        "name": name,
        "path": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "resolution": list(resolution),
        "condition": condition,
        "wire_overlay": wire,
        "camera_location": list(location),
        "camera_target": list(target),
        "lens_mm": lens,
    }


def checkpoint_views() -> dict[str, list[dict[str, Any]]]:
    return {
        "checkpoint_01_silhouette_section": [
            {"name": "cp1_side", "location": (0.17, -0.72, 0.03), "target": (0.17, 0.0, 0.005), "lens": 64.0},
            {"name": "cp1_top", "location": (0.17, -0.02, 0.74), "target": (0.17, 0.0, 0.005), "lens": 66.0},
            {"name": "cp1_front_section", "location": (0.57, -0.02, 0.02), "target": (0.30, 0.0, 0.0), "lens": 72.0},
            {"name": "cp1_rear_section", "location": (-0.30, -0.02, 0.02), "target": (0.025, 0.0, 0.0), "lens": 72.0},
            {"name": "cp1_oblique", "location": (0.46, -0.56, 0.30), "target": (0.17, 0.0, 0.005), "lens": 58.0},
        ],
        "checkpoint_02_topology_windows": [
            {"name": "cp2_left_wire", "location": (0.17, -0.62, 0.025), "target": (0.17, 0.0, 0.0), "lens": 68.0, "wire": True},
            {"name": "cp2_right_wire", "location": (0.17, 0.62, 0.025), "target": (0.17, 0.0, 0.0), "lens": 68.0, "wire": True},
            {"name": "cp2_window_close_wire", "location": (0.18, -0.25, 0.015), "target": (0.18, -0.012, 0.0), "lens": 78.0, "wire": True},
            {"name": "cp2_window_close_shaded", "location": (0.18, -0.25, 0.015), "target": (0.18, -0.012, 0.0), "lens": 78.0},
            {"name": "cp2_body_cap_transition", "location": (0.43, -0.30, 0.12), "target": (0.32, 0.0, 0.0), "lens": 78.0},
            {"name": "cp2_receiver_transition", "location": (-0.10, -0.30, 0.12), "target": (0.018, 0.0, 0.0), "lens": 78.0},
        ],
        "checkpoint_03_material_composition": [
            {"name": "cp3_daylight", "location": (0.46, -0.56, 0.27), "target": (0.17, 0.0, 0.005), "lens": 62.0, "condition": "daylight"},
            {"name": "cp3_overcast", "location": (0.44, 0.54, 0.24), "target": (0.17, 0.0, 0.005), "lens": 62.0, "condition": "overcast"},
            {"name": "cp3_cockpit_light", "location": (0.14, -0.52, 0.13), "target": (0.17, 0.0, 0.005), "lens": 66.0, "condition": "cockpit"},
            {"name": "cp3_ads_oriented", "location": (-0.31, 0.0, 0.052), "target": (0.36, 0.0, 0.045), "lens": 80.0, "condition": "daylight"},
        ],
    }


def final_views() -> list[dict[str, Any]]:
    return [
        {"name": "final_01_left_hero_daylight", "location": (0.46, -0.58, 0.29), "target": (0.17, 0.0, 0.005), "lens": 62.0, "condition": "daylight"},
        {"name": "final_02_right_hero_daylight", "location": (0.46, 0.58, 0.29), "target": (0.17, 0.0, 0.005), "lens": 62.0, "condition": "daylight"},
        {"name": "final_03_top_mechanical", "location": (0.17, -0.02, 0.70), "target": (0.17, 0.0, 0.004), "lens": 70.0, "condition": "daylight"},
        {"name": "final_04_bottom_mechanical", "location": (0.17, -0.02, -0.64), "target": (0.17, 0.0, -0.002), "lens": 70.0, "condition": "overcast"},
        {"name": "final_05_side_orthographic", "location": (0.17, -0.90, 0.01), "target": (0.17, 0.0, 0.01), "lens": 95.0, "condition": "overcast"},
        {"name": "final_06_top_orthographic", "location": (0.17, 0.0, 0.92), "target": (0.17, 0.0, 0.0), "lens": 95.0, "condition": "overcast"},
        {"name": "final_07_front_section", "location": (0.61, -0.01, 0.015), "target": (0.31, 0.0, 0.0), "lens": 78.0, "condition": "daylight"},
        {"name": "final_08_rear_section", "location": (-0.34, -0.01, 0.015), "target": (0.018, 0.0, 0.0), "lens": 78.0, "condition": "daylight"},
        {"name": "final_09_window_detail_wet", "location": (0.19, -0.235, 0.015), "target": (0.19, -0.012, 0.0), "lens": 86.0, "condition": "wet"},
        {"name": "final_10_bodycap_muzzle_detail", "location": (0.49, -0.30, 0.14), "target": (0.355, 0.0, 0.0), "lens": 82.0, "condition": "daylight"},
        {"name": "final_11_cockpit_light", "location": (0.40, -0.50, 0.18), "target": (0.17, 0.0, 0.005), "lens": 68.0, "condition": "cockpit"},
        {"name": "final_12_reference_match", "location": (0.35, -0.62, 0.18), "target": (0.17, 0.0, 0.005), "lens": 72.0, "condition": "overcast"},
    ]


def render_all(scene: Any, rig: dict[str, Any], output: Path, fde: Any, steel: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoint_results: list[dict[str, Any]] = []
    for checkpoint, views in checkpoint_views().items():
        rendered: list[dict[str, Any]] = []
        for view in views:
            condition = str(view.get("condition", "daylight"))
            rendered.append(
                render_view(
                    scene,
                    rig,
                    output / "renders" / "checkpoints" / checkpoint / f"{view['name']}.png",
                    name=str(view["name"]),
                    location=tuple(view["location"]),
                    target=tuple(view["target"]),
                    lens=float(view["lens"]),
                    resolution=CHECKPOINT_RESOLUTION,
                    condition=condition,
                    fde=fde,
                    steel=steel,
                    wire=bool(view.get("wire", False)),
                )
            )
        receipt = {
            "schema": "skyguard.rifle-method05-stagea.checkpoint.v1",
            "gate": GATE,
            "checkpoint": checkpoint,
            "classification": "PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_REVIEW",
            "automatic_checks": {
                "render_count": len(rendered),
                "all_files_nontrivial": all(item["bytes"] > 4096 for item in rendered),
                "resolution": list(CHECKPOINT_RESOLUTION),
            },
            "human_visual_review": "NOT_PERFORMED",
            "observed_visual_defects": [],
            "corrections_applied": [],
            "renders": rendered,
        }
        receipt_path = output / "receipts" / f"{checkpoint}_receipt.json"
        atomic_json(receipt_path, receipt)
        checkpoint_results.append({"checkpoint": checkpoint, "receipt": str(receipt_path), "renders": rendered})

    final_results: list[dict[str, Any]] = []
    for view in final_views():
        final_results.append(
            render_view(
                scene,
                rig,
                output / "renders" / "final" / f"{view['name']}.png",
                name=str(view["name"]),
                location=tuple(view["location"]),
                target=tuple(view["target"]),
                lens=float(view["lens"]),
                resolution=FINAL_RESOLUTION,
                condition=str(view["condition"]),
                fde=fde,
                steel=steel,
            )
        )
    require(len(checkpoint_results) == 3, "Checkpoint group count is not three")
    require(sum(len(item["renders"]) for item in checkpoint_results) == 15, "Checkpoint render count is not fifteen")
    require(len(final_results) == 12, "Final render count is not twelve")
    return checkpoint_results, final_results


def mesh_statistics(objects: Iterable[Any]) -> dict[str, Any]:
    _bpy, bmesh, _Vector = blender_modules()
    records: list[dict[str, Any]] = []
    total_vertices = 0
    total_edges = 0
    total_faces = 0
    total_triangles = 0
    non_manifold_total = 0
    zero_area_total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        mesh = obj.data
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
        zero_area = sum(1 for face in bm.faces if face.calc_area() <= 1e-12)
        bm.free()
        record = {
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
            "non_manifold_edges": non_manifold,
            "zero_area_faces": zero_area,
            "uv_layers": [layer.name for layer in mesh.uv_layers],
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
            "modifiers": [modifier.type for modifier in obj.modifiers],
        }
        records.append(record)
        total_vertices += record["vertices"]
        total_edges += record["edges"]
        total_faces += record["faces"]
        total_triangles += record["triangles"]
        if not obj.name.startswith("UCX_"):
            non_manifold_total += non_manifold
            zero_area_total += zero_area
    return {
        "objects": records,
        "object_count": len(records),
        "vertices": total_vertices,
        "edges": total_edges,
        "faces": total_faces,
        "triangles": total_triangles,
        "production_non_manifold_edges": non_manifold_total,
        "production_zero_area_faces": zero_area_total,
    }


def export_asset(asset_collection: Any, output: Path) -> tuple[Path, Path]:
    bpy, _bmesh, _Vector = blender_modules()
    blend_path = output / "core-rifle-method05-stageA.blend"
    glb_path = output / "core-rifle-method05-stageA.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    export_objects = list(asset_collection.all_objects)
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next((obj for obj in export_objects if obj.type == "MESH"), None)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    require(blend_path.is_file() and blend_path.stat().st_size > 1024, "Governed blend was not created")
    require(glb_path.is_file() and glb_path.stat().st_size > 1024, "Governed GLB was not created")
    return blend_path, glb_path


def inventory(root: Path, excluded: set[Path] | None = None) -> list[dict[str, Any]]:
    excluded = excluded or set()
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path not in excluded
    ]


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    if output.exists():
        require(not any(output.iterdir()), f"Output directory is not empty: {output}")
    else:
        output.mkdir(parents=True)

    scene = reset_scene()
    root = collection("M05A_FORWARD_ASSEMBLY")
    fde = material_fde()
    steel = material_steel()
    wire_material = material_review_wire()

    shell = create_handguard_shell(root, fde)
    create_rail(root, fde)
    create_receiver_interface(root, fde)
    create_body_cap_and_muzzle(root, fde, steel)
    create_side_attachment(root, fde, steel)
    create_socket("SOCKET_Rail_Origin", (0.0, 0.0, HANDGUARD_HALF_HEIGHT_M + RAIL_PROFILE_HEIGHT_M), root)
    create_socket("SOCKET_Muzzle", (BARREL_END_X_M, 0.0, 0.0), root)
    create_socket("SOCKET_Receiver_Interface", (0.0, 0.0, 0.0), root)
    create_socket("SOCKET_SupportHand", (0.175, 0.0, -HANDGUARD_HALF_HEIGHT_M), root)
    collision = create_collision(root)

    rig = create_review_rig(root, shell, wire_material)
    checkpoints, final_renders = render_all(scene, rig, output, fde, steel)
    rig["wire"].hide_render = True

    production_objects = [obj for obj in root.all_objects if obj != collision]
    statistics = mesh_statistics(production_objects)
    require(statistics["production_non_manifold_edges"] == 0, "Production mesh contains non-manifold edges")
    require(statistics["production_zero_area_faces"] == 0, "Production mesh contains zero-area faces")
    require(all(obj.data.uv_layers for obj in production_objects if obj.type == "MESH"), "A production mesh is missing UV0")
    names = {obj.name for obj in root.all_objects}
    require(all(name in names for name in REQUIRED_SOCKETS), "Required socket is missing")
    require(REQUIRED_COLLISION in names, "Required collision object is missing")

    blend_path, glb_path = export_asset(root, output)
    bpy, _bmesh, _Vector = blender_modules()

    atomic_json(
        output / "stageA_dimension_receipt.json",
        {
            "schema": "skyguard.rifle-method05-stagea.dimensions.v1",
            "gate": GATE,
            "unit": "meter",
            "rail": {
                "top_width": RAIL_TOP_WIDTH_M,
                "profile_minimum_height": RAIL_PROFILE_HEIGHT_M,
                "dovetail_width": RAIL_DOVETAIL_WIDTH_M,
                "groove_width": RAIL_GROOVE_WIDTH_M,
                "pitch": RAIL_PITCH_M,
                "authority": "accepted MIL-STD-1913 validation coupon Recovery05",
            },
            "project_provisional": {
                "handguard_length": HANDGUARD_LENGTH_M,
                "handguard_outer_width": HANDGUARD_HALF_WIDTH_M * 2.0,
                "handguard_outer_height": HANDGUARD_HALF_HEIGHT_M * 2.0,
                "wall_thickness": HANDGUARD_WALL_M,
                "barrel_radius": BARREL_RADIUS_M,
                "barrel_end_x": BARREL_END_X_M,
            },
            "passed": True,
        },
    )
    atomic_json(
        output / "stageA_topology_inventory.json",
        {
            "schema": "skyguard.rifle-method05-stagea.topology.v1",
            "gate": GATE,
            "construction": "explicit outer and inner superellipse cage with masked longitudinal cells and bridged opening boundaries",
            "slab_shell_boolean_foundation": False,
            "failed_method_geometry_reused": False,
            "window_negative_space": "real omitted shell cells with manifold boundary bridges",
            "statistics": statistics,
            "passed": True,
        },
    )
    atomic_json(
        output / "stageA_manifold_intersection_validation.json",
        {
            "schema": "skyguard.rifle-method05-stagea.manifold-intersection.v1",
            "gate": GATE,
            "production_non_manifold_edges": statistics["production_non_manifold_edges"],
            "production_zero_area_faces": statistics["production_zero_area_faces"],
            "mesh_validate_invoked": True,
            "separate_part_overlap_policy": "barrel, collars, rail spine, ridges, body cap and muzzle intentionally connect by controlled overlap",
            "self_intersection_claim": "NOT_PROVEN_BY_MESH_VALIDATE_ALONE_REQUIRES_VISUAL_AND_UNREAL_REVIEW",
            "passed": statistics["production_non_manifold_edges"] == 0 and statistics["production_zero_area_faces"] == 0,
        },
    )
    atomic_json(
        output / "stageA_material_inventory.json",
        {
            "schema": "skyguard.rifle-method05-stagea.materials.v1",
            "gate": GATE,
            "materials": [
                {"name": fde.name, "classification": "subdued FDE coated aluminum", "metallic": 0.72},
                {"name": steel.name, "classification": "dark phosphated or nitrided steel", "metallic": 0.92},
            ],
            "unsupported_markings": False,
            "logos": False,
            "text": False,
            "passed": True,
        },
    )
    atomic_json(
        output / "stageA_pivot_axis_socket_collision_contract.json",
        {
            "schema": "skyguard.rifle-method05-stagea.pivot-axis-socket-collision.v1",
            "gate": GATE,
            "unreal_scale": "1 Blender meter equals 100 Unreal centimeters",
            "forward_axis": "+X",
            "up_axis": "+Z",
            "origin": "receiver interface",
            "sockets": list(REQUIRED_SOCKETS),
            "collision": REQUIRED_COLLISION,
            "collision_hidden_from_render": collision.hide_render,
            "passed": True,
        },
    )
    atomic_json(
        output / "stageA_object_modifier_inventory.json",
        {
            "schema": "skyguard.rifle-method05-stagea.object-modifier-inventory.v1",
            "gate": GATE,
            "objects": [
                {
                    "name": obj.name,
                    "type": obj.type,
                    "modifiers": [modifier.type for modifier in obj.modifiers],
                    "materials": [slot.material.name for slot in obj.material_slots if slot.material] if obj.type == "MESH" else [],
                }
                for obj in root.all_objects
            ],
            "passed": True,
        },
    )
    atomic_json(
        output / "stageA_render_receipt.json",
        {
            "schema": "skyguard.rifle-method05-stagea.renders.v1",
            "gate": GATE,
            "checkpoint_groups": checkpoints,
            "checkpoint_render_count": sum(len(item["renders"]) for item in checkpoints),
            "final_renders": final_renders,
            "final_render_count": len(final_renders),
            "human_visual_review": "NOT_PERFORMED",
            "automatic_pass_is_visual_acceptance": False,
            "passed": len(checkpoints) == 3 and len(final_renders) == 12,
        },
    )
    atomic_json(
        output / "stageA_export_receipt.json",
        {
            "schema": "skyguard.rifle-method05-stagea.export.v1",
            "gate": GATE,
            "blend": {"path": blend_path.name, "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": glb_path.name, "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "required_nodes": [*REQUIRED_SOCKETS, REQUIRED_COLLISION],
            "blender_version": bpy.app.version_string,
            "passed": True,
        },
    )

    manifest_path = output / "stageA_artifact_manifest.json"
    terminal_path = output / "stageA_terminal_receipt.json"
    atomic_json(
        manifest_path,
        {
            "schema": "skyguard.rifle-method05-stagea.artifact-manifest.v1",
            "gate": GATE,
            "asset_id": ASSET_ID,
            "created_utc": utc_now(),
            "files": inventory(output, {manifest_path, terminal_path}),
        },
    )
    atomic_json(
        terminal_path,
        {
            "schema": "skyguard.rifle-method05-stagea.terminal.v1",
            "gate": GATE,
            "asset_id": ASSET_ID,
            "classification": "PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW",
            "created_utc": utc_now(),
            "blender_version": bpy.app.version_string,
            "blend_count": 1,
            "glb_count": 1,
            "checkpoint_group_count": 3,
            "checkpoint_render_count": 15,
            "final_render_count": 12,
            "automatic_validation_passed": True,
            "human_visual_review": "NOT_PERFORMED",
            "unreal_import_authorized": False,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW", "output": str(output)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "gate": GATE,
                    "classification": "FAILED_WITH_EVIDENCE",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            ),
            file=sys.stderr,
        )
        raise
