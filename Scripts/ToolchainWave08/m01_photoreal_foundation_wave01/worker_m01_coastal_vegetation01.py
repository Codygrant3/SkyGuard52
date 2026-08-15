from __future__ import annotations

"""Build a fresh, project-authored Mission 1 coastal vegetation set.

The asset deliberately replaces the inherited clustered-sphere tree language
with tapered branch topology and individually modelled leaf silhouettes.  It
does not read or reuse any failed environment geometry and imports no external
model or generated mesh.
"""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


ASSET_ID = "m01-photoreal-foundation-wave01-coastal-vegetation01"
EXPECTED_RENDER_COUNT = 11
TREE_SPECS = (
    {
        "name": "SM_M01_CoastalTree_Tamarisk_A",
        "kind": "tamarisk",
        "height": 5.4,
        "crown_width": 6.2,
        "seed": 5201,
        "leaf_color": (0.105, 0.205, 0.075, 1.0),
    },
    {
        "name": "SM_M01_CoastalTree_Poplar_A",
        "kind": "poplar",
        "height": 9.1,
        "crown_width": 3.8,
        "seed": 5202,
        "leaf_color": (0.135, 0.285, 0.075, 1.0),
    },
    {
        "name": "SM_M01_CoastalTree_MaritimePine_A",
        "kind": "pine",
        "height": 7.6,
        "crown_width": 7.0,
        "seed": 5203,
        "leaf_color": (0.035, 0.135, 0.055, 1.0),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    argv = []
    if "--" in __import__("sys").argv:
        argv = __import__("sys").argv[__import__("sys").argv.index("--") + 1 :]
    return parser.parse_args(argv)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def safe_input(node, name: str, value: object) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def make_bark_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_M01_CoastalTree_Bark_ProjectAuthored")
    material.use_nodes = True
    material.diffuse_color = (0.095, 0.052, 0.026, 1.0)
    material.use_backface_culling = False
    material["source"] = "PROJECT_AUTHORED_PROCEDURAL"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    safe_input(principled, "Base Color", (0.095, 0.052, 0.026, 1.0))
    safe_input(principled, "Roughness", 0.78)
    safe_input(principled, "Specular IOR Level", 0.28)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 7.5
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.28
    bump.inputs["Distance"].default_value = 0.08
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def make_leaf_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    material.use_backface_culling = False
    material["source"] = "PROJECT_AUTHORED_PROCEDURAL"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    safe_input(principled, "Base Color", color)
    safe_input(principled, "Roughness", 0.64)
    safe_input(principled, "Specular IOR Level", 0.24)
    safe_input(principled, "Subsurface Weight", 0.04)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.0
    noise.inputs["Detail"].default_value = 2.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = tuple(max(0.0, channel * 0.55) for channel in color[:3]) + (1.0,)
    ramp.color_ramp.elements[1].color = tuple(min(1.0, channel * 1.35) for channel in color[:3]) + (1.0,)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    return material


def add_tapered_segment(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    face_materials: list[int],
    start: Vector,
    end: Vector,
    start_radius: float,
    end_radius: float,
    sides: int = 9,
) -> None:
    axis = end - start
    require(axis.length > 0.0001, "Degenerate branch segment")
    direction = axis.normalized()
    helper = Vector((0.0, 0.0, 1.0)) if abs(direction.z) < 0.92 else Vector((1.0, 0.0, 0.0))
    tangent = direction.cross(helper).normalized()
    bitangent = direction.cross(tangent).normalized()
    base = len(vertices)
    for point, radius in ((start, start_radius), (end, end_radius)):
        for index in range(sides):
            angle = 2.0 * math.pi * index / sides
            offset = tangent * (math.cos(angle) * radius) + bitangent * (math.sin(angle) * radius)
            vertex = point + offset
            vertices.append((vertex.x, vertex.y, vertex.z))
    for index in range(sides):
        following = (index + 1) % sides
        faces.append((base + index, base + following, base + sides + following, base + sides + index))
        face_materials.append(0)
    faces.append(tuple(base + index for index in reversed(range(sides))))
    face_materials.append(0)
    faces.append(tuple(base + sides + index for index in range(sides)))
    face_materials.append(0)


def add_leaf(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    face_materials: list[int],
    center: Vector,
    direction: Vector,
    normal_hint: Vector,
    length: float,
    width: float,
    material_index: int,
) -> None:
    forward = direction.normalized()
    normal = normal_hint.normalized()
    right = forward.cross(normal)
    if right.length < 0.001:
        normal = Vector((0.0, 0.0, 1.0)) if abs(forward.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        right = forward.cross(normal)
    right.normalize()
    normal = right.cross(forward).normalized()
    base = center - forward * (length * 0.43)
    tip = center + forward * (length * 0.57)
    middle_a = center - forward * (length * 0.08)
    middle_b = center + forward * (length * 0.22) + normal * (length * 0.04)
    points = (
        base,
        middle_a - right * (width * 0.48),
        middle_b - right * (width * 0.38),
        tip,
        middle_b + right * (width * 0.38),
        middle_a + right * (width * 0.48),
    )
    first = len(vertices)
    vertices.extend((point.x, point.y, point.z) for point in points)
    leaf_faces = (
        (first + 0, first + 1, first + 5),
        (first + 1, first + 2, first + 4, first + 5),
        (first + 2, first + 3, first + 4),
    )
    faces.extend(leaf_faces)
    face_materials.extend([material_index] * len(leaf_faces))


def random_direction(rng: random.Random, azimuth: float, upward: float, spread: float) -> Vector:
    return Vector(
        (
            math.cos(azimuth) * spread + rng.uniform(-0.08, 0.08),
            math.sin(azimuth) * spread + rng.uniform(-0.08, 0.08),
            upward + rng.uniform(-0.06, 0.06),
        )
    ).normalized()


def foliage_cluster(
    rng: random.Random,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    face_materials: list[int],
    center: Vector,
    axis: Vector,
    kind: str,
    material_index: int,
    density: int,
) -> None:
    if kind == "pine":
        leaf_length, leaf_width, radius = 0.24, 0.025, 0.38
    elif kind == "tamarisk":
        leaf_length, leaf_width, radius = 0.13, 0.045, 0.42
    else:
        leaf_length, leaf_width, radius = 0.18, 0.09, 0.34
    for index in range(density):
        angle = 2.0 * math.pi * index / max(1, density) + rng.uniform(-0.35, 0.35)
        radial = Vector((math.cos(angle), math.sin(angle), rng.uniform(-0.45, 0.55))).normalized()
        position = center + radial * rng.uniform(radius * 0.25, radius)
        direction = (axis * rng.uniform(0.25, 0.65) + radial * rng.uniform(0.45, 0.95)).normalized()
        add_leaf(
            vertices,
            faces,
            face_materials,
            position,
            direction,
            radial.cross(direction) if radial.cross(direction).length > 0.001 else Vector((0.0, 1.0, 0.0)),
            leaf_length * rng.uniform(0.78, 1.22),
            leaf_width * rng.uniform(0.75, 1.20),
            material_index,
        )


def build_tree(spec: dict[str, object], bark: bpy.types.Material, leaf: bpy.types.Material) -> bpy.types.Object:
    rng = random.Random(int(spec["seed"]))
    name = str(spec["name"])
    kind = str(spec["kind"])
    height = float(spec["height"])
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    face_materials: list[int] = []
    trunk_points = [Vector((0.0, 0.0, 0.0))]
    trunk_segments = 9
    for index in range(1, trunk_segments + 1):
        fraction = index / trunk_segments
        if kind == "tamarisk":
            x = fraction * fraction * 0.72 + math.sin(index * 1.2) * 0.045
            y = math.sin(index * 0.83) * 0.07
        elif kind == "pine":
            x = math.sin(index * 0.61) * 0.055
            y = math.cos(index * 0.49) * 0.06
        else:
            x = math.sin(index * 0.78) * 0.045
            y = math.cos(index * 0.66) * 0.04
        trunk_points.append(Vector((x, y, height * fraction)))
    base_radius = 0.23 if kind != "tamarisk" else 0.27
    for index in range(trunk_segments):
        fraction = index / trunk_segments
        add_tapered_segment(
            vertices,
            faces,
            face_materials,
            trunk_points[index],
            trunk_points[index + 1],
            base_radius * (1.0 - fraction * 0.72),
            base_radius * (1.0 - (index + 1) / trunk_segments * 0.72),
            11,
        )

    if kind == "tamarisk":
        level_indices, branches_per_level = range(2, 9), 5
        spread, upward, primary_scale = 0.88, 0.34, 0.31
    elif kind == "pine":
        level_indices, branches_per_level = range(4, 9), 7
        spread, upward, primary_scale = 0.98, 0.18, 0.34
    else:
        level_indices, branches_per_level = range(2, 9), 5
        spread, upward, primary_scale = 0.46, 0.76, 0.22

    leaf_clusters = 0
    branch_segments = 0
    for level in level_indices:
        level_fraction = level / trunk_segments
        origin = trunk_points[level]
        for branch_index in range(branches_per_level):
            azimuth = (
                2.0 * math.pi * branch_index / branches_per_level
                + level * 1.73
                + rng.uniform(-0.24, 0.24)
            )
            direction = random_direction(rng, azimuth, upward, spread)
            if kind == "tamarisk":
                direction = (direction + Vector((0.38, 0.0, 0.05))).normalized()
            primary_length = height * primary_scale * (1.12 - level_fraction * 0.34) * rng.uniform(0.78, 1.22)
            branch_points = [origin]
            for segment in range(1, 4):
                bend = Vector(
                    (
                        rng.uniform(-0.10, 0.10),
                        rng.uniform(-0.10, 0.10),
                        0.09 + segment * 0.025,
                    )
                )
                next_direction = (direction + bend).normalized()
                branch_points.append(branch_points[-1] + next_direction * (primary_length / 3.0))
                direction = next_direction
            initial_radius = base_radius * (0.34 - level_fraction * 0.11) * rng.uniform(0.88, 1.12)
            for segment in range(3):
                add_tapered_segment(
                    vertices,
                    faces,
                    face_materials,
                    branch_points[segment],
                    branch_points[segment + 1],
                    initial_radius * (1.0 - segment * 0.25),
                    initial_radius * (0.72 - segment * 0.22),
                    8,
                )
                branch_segments += 1

            for fork_index in range(2):
                fork_origin = branch_points[2]
                fork_azimuth = azimuth + (-0.52 if fork_index == 0 else 0.52) + rng.uniform(-0.18, 0.18)
                fork_direction = random_direction(
                    rng,
                    fork_azimuth,
                    0.55 if kind != "pine" else 0.32,
                    0.70 if kind != "poplar" else 0.42,
                )
                if kind == "tamarisk":
                    fork_direction = (fork_direction + Vector((0.26, 0.0, 0.0))).normalized()
                fork_end = fork_origin + fork_direction * primary_length * rng.uniform(0.28, 0.46)
                add_tapered_segment(
                    vertices,
                    faces,
                    face_materials,
                    fork_origin,
                    fork_end,
                    initial_radius * 0.46,
                    initial_radius * 0.12,
                    7,
                )
                branch_segments += 1
                foliage_cluster(
                    rng,
                    vertices,
                    faces,
                    face_materials,
                    fork_end,
                    fork_direction,
                    kind,
                    1,
                    22 if kind == "pine" else 18,
                )
                leaf_clusters += 1
            foliage_cluster(
                rng,
                vertices,
                faces,
                face_materials,
                branch_points[-1],
                direction,
                kind,
                1,
                24 if kind == "pine" else 20,
            )
            leaf_clusters += 1

    foliage_cluster(
        rng,
        vertices,
        faces,
        face_materials,
        trunk_points[-1],
        Vector((0.0, 0.0, 1.0)),
        kind,
        1,
        40 if kind == "pine" else 28,
    )
    leaf_clusters += 1

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(bark)
    mesh.materials.append(leaf)
    for polygon, material_index in zip(mesh.polygons, face_materials):
        polygon.material_index = material_index
        polygon.use_smooth = True
    uv_layer = mesh.uv_layers.new(name="UVMap")
    bounds_scale = max(height, float(spec["crown_width"]), 1.0)
    for loop in mesh.loops:
        coordinate = mesh.vertices[loop.vertex_index].co
        uv_layer.data[loop.index].uv = (
            (coordinate.x / bounds_scale + 0.5) % 1.0,
            max(0.0, min(1.0, coordinate.z / max(height, 0.001))),
        )
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["asset_id"] = ASSET_ID
    obj["species_class"] = kind
    obj["project_authored"] = True
    obj["branch_segment_count"] = branch_segments + trunk_segments
    obj["leaf_cluster_count"] = leaf_clusters
    obj["collision_policy"] = "trunk capsule only; foliage is nonblocking"
    return obj


def add_collision_and_socket(tree: bpy.types.Object, height: float, radius: float) -> tuple[bpy.types.Object, bpy.types.Object]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=height * 0.82, location=(0.0, 0.0, height * 0.41))
    collision = bpy.context.object
    collision.name = "UCX_" + tree.name + "_00"
    collision.display_type = "WIRE"
    collision.hide_render = True
    collision["collision_role"] = "trunk_only"
    socket = bpy.data.objects.new("SOCKET_" + tree.name + "_Origin", None)
    socket.empty_display_type = "PLAIN_AXES"
    socket.empty_display_size = 0.35
    bpy.context.collection.objects.link(socket)
    socket["socket_role"] = "placement_origin"
    return collision, socket


def make_review_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    safe_input(principled, "Base Color", color)
    safe_input(principled, "Roughness", roughness)
    return material


def look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def configure_lighting(mode: str, sun: bpy.types.Object, key: bpy.types.Object, fill: bpy.types.Object) -> None:
    world = bpy.context.scene.world
    background = world.node_tree.nodes.get("Background")
    settings = {
        "day": ((0.055, 0.085, 0.14, 1.0), 0.48, 2.4, 1050.0, 520.0),
        "overcast": ((0.095, 0.11, 0.13, 1.0), 0.62, 1.0, 760.0, 440.0),
        "sunset": ((0.085, 0.045, 0.025, 1.0), 0.38, 1.8, 1150.0, 380.0),
        "silhouette": ((0.014, 0.022, 0.04, 1.0), 0.16, 4.0, 80.0, 30.0),
        "close": ((0.075, 0.085, 0.095, 1.0), 0.52, 1.4, 900.0, 620.0),
    }
    color, strength, sun_energy, key_energy, fill_energy = settings[mode]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    sun.data.energy = sun_energy
    sun.data.color = (1.0, 0.83, 0.66) if mode == "sunset" else (1.0, 0.955, 0.86)
    key.data.energy = key_energy
    fill.data.energy = fill_energy


def render_review(
    output: Path,
    name: str,
    camera: bpy.types.Object,
    target: tuple[float, float, float],
    location: tuple[float, float, float],
    lens: float,
    mode: str,
    sun: bpy.types.Object,
    key: bpy.types.Object,
    fill: bpy.types.Object,
) -> Path:
    configure_lighting(mode, sun, key, fill)
    camera.location = location
    camera.data.lens = lens
    look_at(camera, Vector(target))
    path = output / "renders" / f"{name}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file() and path.stat().st_size > 1024, f"Render failed: {path}")
    return path


def iter_export_objects(trees: Iterable[bpy.types.Object], auxiliaries: Iterable[bpy.types.Object]) -> Iterable[bpy.types.Object]:
    yield from trees
    yield from auxiliaries


def main() -> None:
    args = parse_args()
    output = Path(args.output).resolve()
    require(not output.exists(), f"Fresh output namespace already exists: {output}")
    output.mkdir(parents=True, exist_ok=False)
    (output / "renders").mkdir()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.world = bpy.data.worlds.new("M01_CoastalVegetation_ReviewWorld")
    scene.world.use_nodes = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    bark = make_bark_material()
    trees: list[bpy.types.Object] = []
    auxiliaries: list[bpy.types.Object] = []
    for spec in TREE_SPECS:
        leaf = make_leaf_material("M_" + str(spec["name"]) + "_Leaves", spec["leaf_color"])
        tree = build_tree(spec, bark, leaf)
        trees.append(tree)
        collision, socket = add_collision_and_socket(tree, float(spec["height"]), 0.34)
        auxiliaries.extend((collision, socket))

    ground_material = make_review_material("M_REVIEW_CoastalSand", (0.24, 0.18, 0.105, 1.0), 0.88)
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.025))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    ground.data.materials.append(ground_material)

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 12.0))
    sun = bpy.context.object
    sun.name = "REVIEW_Sun"
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(-36.0))
    sun.data.angle = math.radians(4.0)
    bpy.ops.object.light_add(type="AREA", location=(-7.0, -8.0, 11.0))
    key = bpy.context.object
    key.name = "REVIEW_Key"
    key.data.shape = "DISK"
    key.data.size = 7.0
    key.data.color = (0.82, 0.90, 1.0)
    key.rotation_euler = (math.radians(24.0), 0.0, math.radians(-28.0))
    bpy.ops.object.light_add(type="AREA", location=(8.0, -3.0, 6.0))
    fill = bpy.context.object
    fill.name = "REVIEW_Fill"
    fill.data.size = 5.0
    fill.data.color = (1.0, 0.78, 0.60)
    fill.rotation_euler = (math.radians(50.0), 0.0, math.radians(105.0))
    bpy.ops.object.camera_add(location=(12.0, -16.0, 7.0))
    camera = bpy.context.object
    camera.name = "REVIEW_Camera"
    camera.data.sensor_width = 36.0
    scene.camera = camera

    render_paths: list[Path] = []
    for tree in trees:
        tree.hide_render = True
    lineup = (-5.2, 0.0, 5.2)
    for tree, x_position in zip(trees, lineup):
        tree.location.x = x_position
        tree.hide_render = False
    render_paths.append(render_review(output, "R01_DAY_LINEUP", camera, (0.0, 0.0, 3.4), (16.0, -20.0, 8.2), 53.0, "day", sun, key, fill))
    render_paths.append(render_review(output, "R02_OVERCAST_LINEUP", camera, (0.0, 0.0, 3.5), (-16.0, -20.0, 7.4), 55.0, "overcast", sun, key, fill))
    render_paths.append(render_review(output, "R03_SUNSET_LINEUP", camera, (0.0, 0.0, 3.6), (15.0, -19.0, 6.3), 58.0, "sunset", sun, key, fill))
    render_paths.append(render_review(output, "R04_SILHOUETTE_LINEUP", camera, (0.0, 0.0, 3.5), (0.0, -22.0, 5.5), 58.0, "silhouette", sun, key, fill))

    for tree in trees:
        tree.location.x = 0.0
        tree.hide_render = True
    per_tree = (
        (trees[0], "TAMARISK", 3.0, 56.0),
        (trees[1], "POPLAR", 4.6, 58.0),
        (trees[2], "MARITIME_PINE", 4.0, 56.0),
    )
    for tree, label, target_z, lens in per_tree:
        tree.hide_render = False
        render_paths.append(render_review(output, f"R_{label}_FRONT", camera, (0.0, 0.0, target_z), (9.5, -13.5, target_z + 2.0), lens, "day", sun, key, fill))
        render_paths.append(render_review(output, f"R_{label}_SIDE", camera, (0.0, 0.0, target_z), (-12.5, -7.0, target_z + 1.2), lens, "overcast", sun, key, fill))
        tree.hide_render = True

    trees[0].hide_render = False
    render_paths.append(render_review(output, "R11_BRANCH_LEAF_CLOSE", camera, (0.8, 0.0, 3.6), (3.4, -4.3, 4.2), 72.0, "close", sun, key, fill))
    require(len(render_paths) == EXPECTED_RENDER_COUNT, "Governed render count changed")

    for tree in trees:
        tree.hide_render = False
        tree.location = (0.0, 0.0, 0.0)
    ground.hide_render = True
    sun.hide_render = True
    key.hide_render = True
    fill.hide_render = True
    camera.hide_render = True

    blend_path = output / "SKG_M01_CoastalVegetation01.blend"
    glb_path = output / "SKG_M01_CoastalVegetation01.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    selected = list(iter_export_objects(trees, auxiliaries))
    for obj in selected:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = trees[0]
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=True,
    )
    require(blend_path.is_file() and blend_path.stat().st_size > 0, "Blend output missing")
    require(glb_path.is_file() and glb_path.stat().st_size > 20, "GLB output missing")

    dimensions = []
    for tree, spec in zip(trees, TREE_SPECS):
        dimensions.append(
            {
                "name": tree.name,
                "species_class": spec["kind"],
                "bounds_m": [round(float(value), 4) for value in tree.dimensions],
                "target_height_m": spec["height"],
                "target_crown_width_m": spec["crown_width"],
                "vertices": len(tree.data.vertices),
                "polygons": len(tree.data.polygons),
                "materials": len(tree.data.materials),
                "uv_layers": len(tree.data.uv_layers),
                "branch_segment_count": tree["branch_segment_count"],
                "leaf_cluster_count": tree["leaf_cluster_count"],
            }
        )
    write_json(
        output / "dimension_receipt.json",
        {
            "schema": "skyguard.m01-coastal-vegetation01-dimensions.v1",
            "asset_id": ASSET_ID,
            "unit_system": "meters",
            "tree_count": len(trees),
            "trees": dimensions,
            "placement_origin_at_ground": True,
            "collision_objects": [obj.name for obj in auxiliaries if obj.type == "MESH"],
            "sockets": [obj.name for obj in auxiliaries if obj.type == "EMPTY"],
        },
    )
    write_json(
        output / "production_receipt.json",
        {
            "schema": "skyguard.m01-coastal-vegetation01-production.v1",
            "asset_id": ASSET_ID,
            "classification": "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW",
            "project_authored_geometry": True,
            "external_models_used": False,
            "external_ai_used": False,
            "failed_geometry_reused": False,
            "tree_count": len(trees),
            "render_count": len(render_paths),
            "render_resolution": [1920, 1080],
            "blend": {"path": blend_path.name, "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": glb_path.name, "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "renders": [
                {"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in render_paths
            ],
        },
    )


if __name__ == "__main__":
    main()
