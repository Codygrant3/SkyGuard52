from __future__ import annotations

"""Create a project-authored, Unreal-ready coastal vegetation library.

This method is intentionally independent of the failed capped-segment trees.
Wood is built from continuous Bezier splines, converted to smooth mesh, and
joined with dense species-specific leaf geometry.  No external model, external
AI geometry, or failed geometry is read or reused.
"""

import argparse
import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Vector


ASSET_ID = "m01-photoreal-foundation-wave01-coastal-vegetation02"
EXPECTED_RENDER_COUNT = 12
RENDER_SIZE = (1920, 1080)


@dataclass(frozen=True)
class TreeSpec:
    name: str
    species: str
    variant: str
    height: float
    crown_width: float
    base_radius: float
    seed: int
    bark_dark: tuple[float, float, float, float]
    bark_light: tuple[float, float, float, float]
    leaf_base: tuple[float, float, float, float]


TREE_SPECS = (
    TreeSpec("SM_M01_CoastalTree_Tamarisk_B01", "tamarisk", "B01", 5.7, 6.4, 0.29, 6211, (0.055, 0.028, 0.016, 1.0), (0.20, 0.105, 0.050, 1.0), (0.090, 0.240, 0.105, 1.0)),
    TreeSpec("SM_M01_CoastalTree_Tamarisk_B02", "tamarisk", "B02", 5.1, 7.0, 0.27, 6212, (0.060, 0.030, 0.017, 1.0), (0.22, 0.115, 0.055, 1.0), (0.105, 0.265, 0.120, 1.0)),
    TreeSpec("SM_M01_CoastalTree_Poplar_B01", "poplar", "B01", 10.2, 4.1, 0.34, 6221, (0.050, 0.042, 0.030, 1.0), (0.25, 0.205, 0.135, 1.0), (0.125, 0.305, 0.070, 1.0)),
    TreeSpec("SM_M01_CoastalTree_Poplar_B02", "poplar", "B02", 9.4, 4.7, 0.32, 6222, (0.048, 0.040, 0.030, 1.0), (0.23, 0.195, 0.125, 1.0), (0.145, 0.330, 0.080, 1.0)),
    TreeSpec("SM_M01_CoastalTree_MaritimePine_B01", "pine", "B01", 8.2, 7.4, 0.38, 6231, (0.042, 0.022, 0.012, 1.0), (0.28, 0.105, 0.040, 1.0), (0.025, 0.160, 0.060, 1.0)),
    TreeSpec("SM_M01_CoastalTree_MaritimePine_B02", "pine", "B02", 7.5, 8.0, 0.36, 6232, (0.044, 0.022, 0.012, 1.0), (0.30, 0.115, 0.042, 1.0), (0.030, 0.175, 0.065, 1.0)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
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


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def safe_input(node: bpy.types.Node, name: str, value: object) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def color_scale(color: tuple[float, float, float, float], factor: float) -> tuple[float, float, float, float]:
    return tuple(max(0.0, min(1.0, channel * factor)) for channel in color[:3]) + (1.0,)


def make_bark_material(spec: TreeSpec) -> bpy.types.Material:
    material = bpy.data.materials.new("M_" + spec.name + "_Bark")
    material.use_nodes = True
    material.use_backface_culling = False
    material.diffuse_color = spec.bark_light
    material["source"] = "PROJECT_AUTHORED_PROCEDURAL"
    material["unreal_material_intent"] = "MI_M01_CoastalTree_Bark"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    safe_input(principled, "Roughness", 0.82)
    safe_input(principled, "Specular IOR Level", 0.22)

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (5.0, 5.0, 1.25)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 5.5 if spec.species == "pine" else 7.5
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.78
    noise.inputs["Distortion"].default_value = 0.24
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 18.0
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 5.0
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 0.62
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = spec.bark_dark
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = spec.bark_light
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.34
    bump.inputs["Distance"].default_value = 0.045
    rough_ramp = nodes.new("ShaderNodeMapRange")
    rough_ramp.inputs["To Min"].default_value = 0.68
    rough_ramp.inputs["To Max"].default_value = 0.94

    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    links.new(noise.outputs["Fac"], multiply.inputs[1])
    links.new(wave.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(multiply.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    links.new(noise.outputs["Fac"], rough_ramp.inputs["Value"])
    links.new(rough_ramp.outputs["Result"], principled.inputs["Roughness"])
    return material


def make_leaf_materials(spec: TreeSpec) -> list[bpy.types.Material]:
    result: list[bpy.types.Material] = []
    for index, factor in enumerate((0.72, 0.92, 1.12, 1.28)):
        material = bpy.data.materials.new(f"M_{spec.name}_Leaves_{index + 1:02d}")
        material.use_nodes = True
        material.use_backface_culling = False
        color = color_scale(spec.leaf_base, factor)
        material.diffuse_color = color
        material["source"] = "PROJECT_AUTHORED_PROCEDURAL"
        material["unreal_material_intent"] = "MI_M01_CoastalTree_Foliage_TwoSided"
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        principled = nodes.get("Principled BSDF")
        safe_input(principled, "Base Color", color)
        safe_input(principled, "Roughness", 0.58 + index * 0.035)
        safe_input(principled, "Specular IOR Level", 0.20)
        safe_input(principled, "Subsurface Weight", 0.07 if spec.species != "pine" else 0.04)
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 5.0 + index
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.66
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = color_scale(color, 0.70)
        ramp.color_ramp.elements[1].color = color_scale(color, 1.18)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.11
        bump.inputs["Distance"].default_value = 0.02
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])
        result.append(material)
    return result


def add_bezier_spline(curve: bpy.types.Curve, points: list[Vector], radii: list[float]) -> None:
    require(len(points) == len(radii) and len(points) >= 2, "Invalid spline contract")
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate, radius in zip(spline.bezier_points, points, radii):
        point.co = coordinate
        point.radius = max(0.004, radius)
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    spline.resolution_u = 3


def trunk_path(rng: random.Random, height: float, count: int, lean: Vector) -> list[Vector]:
    points: list[Vector] = []
    for index in range(count):
        t = index / (count - 1)
        wind = Vector((math.sin(t * math.pi * 1.7), math.cos(t * math.pi * 1.35), 0.0)) * (0.045 + t * 0.08)
        jitter = Vector((rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), 0.0)) * t
        points.append(lean * (t * t) + wind + jitter + Vector((0.0, 0.0, height * t)))
    points[0] = Vector((0.0, 0.0, 0.0))
    return points


def branch_path(
    rng: random.Random,
    start: Vector,
    direction: Vector,
    length: float,
    point_count: int,
    droop: float,
    curl: float,
) -> list[Vector]:
    direction = direction.normalized()
    lateral = Vector((-direction.y, direction.x, 0.0))
    if lateral.length < 0.01:
        lateral = Vector((1.0, 0.0, 0.0))
    lateral.normalize()
    points = []
    for index in range(point_count):
        t = index / (point_count - 1)
        bend = lateral * math.sin(t * math.pi) * curl * length
        vertical = Vector((0.0, 0.0, droop * length * t * t))
        noise = Vector((rng.uniform(-0.025, 0.025), rng.uniform(-0.025, 0.025), rng.uniform(-0.015, 0.025))) * length * t
        points.append(start + direction * (length * t) + bend + vertical + noise)
    return points


def generate_wood_splines(spec: TreeSpec, curve: bpy.types.Curve) -> tuple[list[tuple[Vector, Vector]], int]:
    rng = random.Random(spec.seed)
    terminals: list[tuple[Vector, Vector]] = []
    spline_count = 0
    crown_radius = spec.crown_width * 0.5

    if spec.species == "tamarisk":
        stems = 5 if spec.variant == "B01" else 6
        for stem_index in range(stems):
            angle = (2.0 * math.pi * stem_index / stems) + rng.uniform(-0.28, 0.28)
            lean = Vector((math.cos(angle), math.sin(angle), 0.0)) * crown_radius * rng.uniform(0.18, 0.30)
            height = spec.height * rng.uniform(0.82, 1.02)
            points = trunk_path(rng, height, 7, lean)
            points[0] = Vector((math.cos(angle) * 0.035, math.sin(angle) * 0.035, -0.05))
            radii = [spec.base_radius * (1.0 - 0.77 * (i / (len(points) - 1))) * (0.60 if stems > 1 else 1.0) for i in range(len(points))]
            add_bezier_spline(curve, points, radii)
            spline_count += 1
            for level in range(2, 6):
                origin = points[level]
                for branch_index in range(2):
                    azimuth = angle + (branch_index * math.pi) + rng.uniform(-0.75, 0.75)
                    direction = Vector((math.cos(azimuth), math.sin(azimuth), rng.uniform(0.28, 0.58))).normalized()
                    length = crown_radius * rng.uniform(0.45, 0.88) * (1.0 - level * 0.035)
                    branch = branch_path(rng, origin - direction * radii[level] * 0.4, direction, length, 5, rng.uniform(-0.10, 0.12), rng.uniform(-0.08, 0.08))
                    branch_radii = [radii[level] * lerp(0.38, 0.06, i / 4) for i in range(5)]
                    add_bezier_spline(curve, branch, branch_radii)
                    spline_count += 1
                    terminals.append((branch[-1], (branch[-1] - branch[-2]).normalized()))
                    for side in (-1.0, 1.0):
                        fork_dir = (direction + Vector((-direction.y, direction.x, rng.uniform(0.2, 0.5))) * side * 0.45).normalized()
                        fork = branch_path(rng, branch[3], fork_dir, length * rng.uniform(0.28, 0.44), 4, rng.uniform(-0.05, 0.10), rng.uniform(-0.05, 0.05))
                        add_bezier_spline(curve, fork, [branch_radii[3] * lerp(0.50, 0.05, i / 3) for i in range(4)])
                        spline_count += 1
                        terminals.append((fork[-1], (fork[-1] - fork[-2]).normalized()))
            terminals.append((points[-1], (points[-1] - points[-2]).normalized()))
    else:
        lean = Vector((rng.uniform(-0.28, 0.28), rng.uniform(-0.20, 0.20), 0.0))
        trunk = trunk_path(rng, spec.height, 11, lean)
        radii = [spec.base_radius * lerp(1.0, 0.14, (i / 10) ** 0.88) for i in range(11)]
        add_bezier_spline(curve, trunk, radii)
        spline_count += 1
        if spec.species == "poplar":
            levels = range(2, 10)
            branch_count = 5 if spec.variant == "B01" else 6
            vertical_range = (0.55, 1.10)
            length_scale = (0.32, 0.58)
            droop_range = (0.10, 0.26)
        else:
            levels = range(4, 10)
            branch_count = 6 if spec.variant == "B01" else 7
            vertical_range = (0.04, 0.36)
            length_scale = (0.52, 0.94)
            droop_range = (-0.12, 0.08)
        for level in levels:
            t = level / 10
            origin = trunk[level]
            for branch_index in range(branch_count):
                azimuth = 2.0 * math.pi * branch_index / branch_count + level * 1.83 + rng.uniform(-0.24, 0.24)
                vertical = rng.uniform(*vertical_range)
                direction = Vector((math.cos(azimuth), math.sin(azimuth), vertical)).normalized()
                if spec.species == "poplar":
                    level_shape = 1.0 - abs(t - 0.58) * 0.92
                else:
                    level_shape = 0.76 + t * 0.40
                length = crown_radius * rng.uniform(*length_scale) * level_shape
                branch = branch_path(rng, origin - direction * radii[level] * 0.55, direction, length, 5, rng.uniform(*droop_range), rng.uniform(-0.07, 0.07))
                base_branch_radius = radii[level] * (0.44 if spec.species == "pine" else 0.34)
                branch_radii = [base_branch_radius * lerp(1.0, 0.07, i / 4) for i in range(5)]
                add_bezier_spline(curve, branch, branch_radii)
                spline_count += 1
                terminals.append((branch[-1], (branch[-1] - branch[-2]).normalized()))
                secondary_count = 2 if level < 9 else 1
                for secondary in range(secondary_count):
                    side = -1.0 if secondary == 0 else 1.0
                    local = (direction + Vector((-direction.y, direction.x, rng.uniform(0.18, 0.58))) * side * rng.uniform(0.35, 0.60)).normalized()
                    secondary_path = branch_path(rng, branch[3], local, length * rng.uniform(0.25, 0.42), 4, rng.uniform(-0.04, 0.14), rng.uniform(-0.05, 0.05))
                    add_bezier_spline(curve, secondary_path, [branch_radii[3] * lerp(0.55, 0.05, i / 3) for i in range(4)])
                    spline_count += 1
                    terminals.append((secondary_path[-1], (secondary_path[-1] - secondary_path[-2]).normalized()))
        terminals.append((trunk[-1], (trunk[-1] - trunk[-2]).normalized()))
    return terminals, spline_count


def make_wood(spec: TreeSpec, material: bpy.types.Material) -> tuple[bpy.types.Object, list[tuple[Vector, Vector]], int]:
    curve = bpy.data.curves.new(spec.name + "_WoodCurve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 3
    curve.bevel_depth = 1.0
    curve.bevel_resolution = 3
    curve.resolution_u = 3
    curve.use_fill_caps = True
    curve.twist_smooth = 10
    terminals, spline_count = generate_wood_splines(spec, curve)
    wood = bpy.data.objects.new(spec.name + "_Wood", curve)
    bpy.context.collection.objects.link(wood)
    wood.data.materials.append(material)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = wood
    wood.select_set(True)
    bpy.ops.object.convert(target="MESH")
    wood = bpy.context.object
    wood.name = spec.name + "_Wood"
    for polygon in wood.data.polygons:
        polygon.use_smooth = True
    if not wood.data.uv_layers:
        wood.data.uv_layers.new(name="UVMap")
    return wood, terminals, spline_count


def append_leaf(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material_indices: list[int],
    center: Vector,
    forward: Vector,
    length: float,
    width: float,
    camber: float,
    material_index: int,
) -> None:
    forward = forward.normalized()
    helper = Vector((0.0, 0.0, 1.0)) if abs(forward.z) < 0.86 else Vector((1.0, 0.0, 0.0))
    lateral = forward.cross(helper).normalized()
    normal = lateral.cross(forward).normalized()
    base = center - forward * (length * 0.48)
    tip = center + forward * (length * 0.52)
    left = center - lateral * (width * 0.50) + normal * camber
    ridge = center + normal * (camber * 1.65)
    right = center + lateral * (width * 0.50) + normal * camber
    first = len(vertices)
    vertices.extend(tuple(point) for point in (base, left, ridge, right, tip))
    faces.extend(((first, first + 1, first + 2), (first, first + 2, first + 3), (first + 1, first + 4, first + 2), (first + 2, first + 4, first + 3)))
    material_indices.extend((material_index,) * 4)


def make_foliage(spec: TreeSpec, terminals: list[tuple[Vector, Vector]], materials: list[bpy.types.Material]) -> tuple[bpy.types.Object, int]:
    rng = random.Random(spec.seed + 9000)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    if spec.species == "poplar":
        per_terminal, cluster_radius, leaf_length, leaf_width = 18, 0.46, 0.16, 0.075
    elif spec.species == "tamarisk":
        per_terminal, cluster_radius, leaf_length, leaf_width = 22, 0.52, 0.095, 0.025
    else:
        per_terminal, cluster_radius, leaf_length, leaf_width = 25, 0.48, 0.22, 0.018

    leaf_count = 0
    for terminal, axis in terminals:
        local_per_terminal = per_terminal + rng.randint(-3, 5)
        for _ in range(local_per_terminal):
            offset = Vector((rng.gauss(0.0, 0.45), rng.gauss(0.0, 0.45), rng.gauss(0.0, 0.28))) * cluster_radius
            center = terminal + offset
            direction = (axis * rng.uniform(0.20, 0.58) + Vector((rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(-0.35, 0.85)))).normalized()
            length = leaf_length * rng.uniform(0.72, 1.28)
            width = leaf_width * rng.uniform(0.68, 1.30)
            append_leaf(vertices, faces, material_indices, center, direction, length, width, width * rng.uniform(0.10, 0.30), rng.randrange(len(materials)))
            leaf_count += 1
            if spec.species == "pine" and rng.random() < 0.78:
                for rotation in (-0.42, 0.42):
                    rotated = Vector((
                        direction.x * math.cos(rotation) - direction.y * math.sin(rotation),
                        direction.x * math.sin(rotation) + direction.y * math.cos(rotation),
                        direction.z + rng.uniform(-0.08, 0.08),
                    )).normalized()
                    append_leaf(vertices, faces, material_indices, center, rotated, length * rng.uniform(0.86, 1.08), width, width * 0.12, rng.randrange(len(materials)))
                    leaf_count += 1

    mesh = bpy.data.meshes.new(spec.name + "_FoliageMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    for material in materials:
        mesh.materials.append(material)
    for polygon, material_index in zip(mesh.polygons, material_indices):
        polygon.material_index = material_index
        polygon.use_smooth = False
    uv = mesh.uv_layers.new(name="UVMap")
    for loop in mesh.loops:
        vertex = mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((vertex.x * 0.17) % 1.0, (vertex.y * 0.17 + vertex.z * 0.11) % 1.0)
    foliage = bpy.data.objects.new(spec.name + "_Foliage", mesh)
    bpy.context.collection.objects.link(foliage)
    return foliage, leaf_count


def join_tree(spec: TreeSpec, wood: bpy.types.Object, foliage: bpy.types.Object, spline_count: int, leaf_count: int) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    wood.select_set(True)
    foliage.select_set(True)
    bpy.context.view_layer.objects.active = wood
    bpy.ops.object.join()
    tree = bpy.context.object
    tree.name = spec.name
    tree.data.name = spec.name + "_Mesh"
    tree["project_authored"] = True
    tree["construction_method"] = "continuous_bezier_wood_plus_dense_species_foliage"
    tree["species"] = spec.species
    tree["variant"] = spec.variant
    tree["wood_spline_count"] = spline_count
    tree["leaf_count"] = leaf_count
    tree["wind_pivot_m"] = 0.18
    tree["wind_stiffness"] = 0.78 if spec.species == "pine" else 0.58
    tree["unreal_forward_axis"] = "+X"
    tree["unreal_up_axis"] = "+Z"
    tree["collision_policy"] = "trunk-only UCX; foliage nonblocking"
    return tree


def add_collision_and_socket(tree: bpy.types.Object, spec: TreeSpec) -> tuple[bpy.types.Object, bpy.types.Object]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=spec.base_radius * 0.92, depth=spec.height * 0.62, location=(0.0, 0.0, spec.height * 0.31))
    collision = bpy.context.object
    collision.name = "UCX_" + tree.name + "_00"
    collision.display_type = "WIRE"
    collision.hide_render = True
    collision["collision_role"] = "simple_trunk"
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
    socket = bpy.context.object
    socket.name = "SOCKET_" + tree.name + "_Origin"
    socket.empty_display_size = 0.35
    socket.hide_render = True
    return collision, socket


def make_review_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    safe_input(principled, "Base Color", color)
    safe_input(principled, "Roughness", roughness)
    return material


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def configure_lighting(mode: str, sun: bpy.types.Object, key: bpy.types.Object, fill: bpy.types.Object) -> None:
    background = bpy.context.scene.world.node_tree.nodes.get("Background")
    settings = {
        "day": ((0.055, 0.095, 0.16, 1.0), 0.36, 3.6, 850.0, 420.0),
        "overcast": ((0.085, 0.10, 0.12, 1.0), 0.52, 1.1, 620.0, 520.0),
        "sunset": ((0.075, 0.025, 0.012, 1.0), 0.20, 2.4, 940.0, 520.0),
        "silhouette": ((0.002, 0.004, 0.008, 1.0), 0.03, 0.20, 180.0, 80.0),
        "close": ((0.045, 0.065, 0.085, 1.0), 0.30, 2.1, 1050.0, 680.0),
    }
    color, strength, sun_energy, key_energy, fill_energy = settings[mode]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    sun.data.energy = sun_energy
    sun.data.color = (1.0, 0.72, 0.48) if mode == "sunset" else (1.0, 0.94, 0.82)
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
    point_camera(camera, Vector(target))
    path = output / "renders" / (name + ".png")
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file() and path.stat().st_size > 4096, "Render missing or truncated: " + str(path))
    return path


def main() -> None:
    args = parse_args()
    output = Path(args.output).resolve()
    require(not output.exists(), "Fresh output namespace already exists: " + str(output))
    output.mkdir(parents=True, exist_ok=False)
    (output / "renders").mkdir()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RENDER_SIZE[0]
    scene.render.resolution_y = RENDER_SIZE[1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("M01_CoastalVegetation02_ReviewWorld")
    scene.world.use_nodes = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    trees: list[bpy.types.Object] = []
    auxiliaries: list[bpy.types.Object] = []
    receipts: list[dict[str, object]] = []
    for spec in TREE_SPECS:
        bark = make_bark_material(spec)
        leaves = make_leaf_materials(spec)
        wood, terminals, spline_count = make_wood(spec, bark)
        foliage, leaf_count = make_foliage(spec, terminals, leaves)
        tree = join_tree(spec, wood, foliage, spline_count, leaf_count)
        collision, socket = add_collision_and_socket(tree, spec)
        trees.append(tree)
        auxiliaries.extend((collision, socket))
        receipts.append({
            "name": tree.name,
            "species": spec.species,
            "variant": spec.variant,
            "target_height_m": spec.height,
            "target_crown_width_m": spec.crown_width,
            "bounds_m": [round(float(value), 4) for value in tree.dimensions],
            "wood_spline_count": spline_count,
            "leaf_count": leaf_count,
            "vertices": len(tree.data.vertices),
            "polygons": len(tree.data.polygons),
            "material_slots": len(tree.data.materials),
            "uv_layers": len(tree.data.uv_layers),
        })

    ground_material = make_review_material("M_REVIEW_CoastalSand02", (0.24, 0.18, 0.105, 1.0), 0.88)
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, 0.0, -0.035))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    ground.data.materials.append(ground_material)
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 14.0))
    sun = bpy.context.object
    sun.name = "REVIEW_Sun"
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(-36.0))
    sun.data.angle = math.radians(3.0)
    bpy.ops.object.light_add(type="AREA", location=(-8.0, -10.0, 13.0))
    key = bpy.context.object
    key.name = "REVIEW_Key"
    key.data.shape = "DISK"
    key.data.size = 8.0
    key.data.color = (0.82, 0.90, 1.0)
    bpy.ops.object.light_add(type="AREA", location=(10.0, -4.0, 8.0))
    fill = bpy.context.object
    fill.name = "REVIEW_Fill"
    fill.data.size = 6.0
    fill.data.color = (1.0, 0.76, 0.58)
    bpy.ops.object.camera_add(location=(18.0, -24.0, 9.0))
    camera = bpy.context.object
    camera.name = "REVIEW_Camera"
    camera.data.sensor_width = 36.0
    scene.camera = camera

    render_paths: list[Path] = []
    lineup_x = (-9.0, -5.4, -1.8, 1.8, 5.4, 9.0)
    for tree, x_position in zip(trees, lineup_x):
        tree.location.x = x_position
    render_paths.append(render_review(output, "R01_DAY_LIBRARY_LINEUP", camera, (0.0, 0.0, 4.2), (22.0, -28.0, 10.0), 58.0, "day", sun, key, fill))
    render_paths.append(render_review(output, "R02_OVERCAST_LIBRARY_LINEUP", camera, (0.0, 0.0, 4.0), (-23.0, -27.0, 9.0), 60.0, "overcast", sun, key, fill))
    render_paths.append(render_review(output, "R03_SUNSET_LIBRARY_LINEUP", camera, (0.0, 0.0, 4.2), (20.0, -28.0, 8.0), 61.0, "sunset", sun, key, fill))
    render_paths.append(render_review(output, "R04_SILHOUETTE_LIBRARY_LINEUP", camera, (0.0, 0.0, 4.1), (0.0, -31.0, 7.0), 62.0, "silhouette", sun, key, fill))

    for tree in trees:
        tree.location.x = 0.0
        tree.hide_render = True
    for index, (tree, spec) in enumerate(zip(trees, TREE_SPECS), start=5):
        tree.hide_render = False
        target_z = spec.height * 0.48
        render_paths.append(render_review(output, f"R{index:02d}_{spec.species.upper()}_{spec.variant}", camera, (0.0, 0.0, target_z), (spec.crown_width * 1.25, -spec.crown_width * 1.65, target_z + spec.height * 0.16), 64.0, "day" if index % 2 else "overcast", sun, key, fill))
        tree.hide_render = True

    trees[2].hide_render = False
    render_paths.append(render_review(output, "R11_CONTINUOUS_WOOD_JUNCTION_CLOSE", camera, (0.0, 0.0, 3.2), (2.8, -4.1, 3.9), 78.0, "close", sun, key, fill))
    trees[2].hide_render = True
    trees[4].hide_render = False
    render_paths.append(render_review(output, "R12_PINE_FOLIAGE_CLUSTER_CLOSE", camera, (1.1, 0.0, 5.9), (4.2, -4.6, 6.5), 78.0, "close", sun, key, fill))
    require(len(render_paths) == EXPECTED_RENDER_COUNT, "Governed render count changed")

    for tree in trees:
        tree.hide_render = False
        tree.location = (0.0, 0.0, 0.0)
    for obj in (ground, sun, key, fill, camera):
        obj.hide_render = True

    blend_path = output / "SKG_M01_CoastalVegetation02.blend"
    glb_path = output / "SKG_M01_CoastalVegetation02.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [*trees, *auxiliaries]:
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

    write_json(output / "dimension_receipt.json", {
        "schema": "skyguard.m01-coastal-vegetation02-dimensions.v1",
        "asset_id": ASSET_ID,
        "unit_system": "meters",
        "tree_count": len(trees),
        "trees": receipts,
        "placement_origin_at_ground": True,
        "collision_objects": [obj.name for obj in auxiliaries if obj.type == "MESH"],
        "sockets": [obj.name for obj in auxiliaries if obj.type == "EMPTY"],
    })
    write_json(output / "production_receipt.json", {
        "schema": "skyguard.m01-coastal-vegetation02-production.v1",
        "asset_id": ASSET_ID,
        "classification": "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW",
        "construction_method": "continuous_bezier_wood_plus_dense_species_foliage",
        "project_authored_geometry": True,
        "external_models_used": False,
        "external_ai_used": False,
        "failed_geometry_reused": False,
        "tree_count": len(trees),
        "render_count": len(render_paths),
        "render_resolution": list(RENDER_SIZE),
        "blend": {"path": blend_path.name, "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
        "glb": {"path": glb_path.name, "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
        "renders": [{"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in render_paths],
    })


if __name__ == "__main__":
    main()
