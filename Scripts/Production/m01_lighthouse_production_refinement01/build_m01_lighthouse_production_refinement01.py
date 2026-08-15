"""Build a fresh Mission 1 coastal lighthouse production candidate in Blender 5.2.

The asset is authored from primitive construction logic and uses the selected
project lighthouse only as dimensional/material reference. No rejected mesh is
copied or modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ASSET_ID = "m01-lighthouse-production-refinement01"
RENDER_MESHES = (
    "SM_M01_Lighthouse_Tower_A",
    "SM_M01_Lighthouse_Lantern_A",
    "SM_M01_Lighthouse_Details_A",
)
COLLISIONS = (
    "UCX_SM_M01_Lighthouse_Tower_A_00",
    "UCX_SM_M01_Lighthouse_Lantern_A_00",
)
SOCKETS = (
    "SOCKET_Lighthouse_Origin",
    "SOCKET_Lighthouse_Door",
    "SOCKET_Lighthouse_Gallery",
    "SOCKET_Lighthouse_Lamp",
)
TEXTURE_ROOT = Path(r"D:\Skyguard52\Content\Skyguard\Textures\PolyHaven")
TEXTURE_SETS = {
    "plaster": {
        "base": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_diff_2k.jpg",
        "normal": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_rough_2k.jpg",
    },
    "concrete": {
        "base": TEXTURE_ROOT / "concrete_wall_006" / "concrete_wall_006-diffuse-2k.jpg",
        "normal": TEXTURE_ROOT / "concrete_wall_006" / "concrete_wall_006-nor_gl-2k.jpg",
        "roughness": TEXTURE_ROOT / "concrete_wall_006" / "concrete_wall_006-rough-2k.jpg",
    },
    "metal": {
        "base": TEXTURE_ROOT / "metal_plate" / "metal_plate_diff_2k.jpg",
        "normal": TEXTURE_ROOT / "metal_plate" / "metal_plate_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / "metal_plate" / "metal_plate_rough_2k.jpg",
    },
    "rust": {
        "base": TEXTURE_ROOT / "green_metal_rust" / "green_metal_rust-diffuse-2k.jpg",
        "normal": TEXTURE_ROOT / "green_metal_rust" / "green_metal_rust-nor_gl-2k.jpg",
        "roughness": TEXTURE_ROOT / "green_metal_rust" / "green_metal_rust-rough-2k.jpg",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection_name: str) -> bpy.types.Object:
    collection = ensure_collection(collection_name)
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def set_supported(target: object, attribute: str, candidates: tuple[str, ...]) -> str:
    failures: list[str] = []
    for candidate in candidates:
        try:
            setattr(target, attribute, candidate)
            return candidate
        except (TypeError, ValueError) as exc:
            failures.append(f"{candidate}: {exc}")
    raise RuntimeError(
        f"No supported value for {type(target).__name__}.{attribute}; "
        + " | ".join(failures)
    )


def principled_socket(node: bpy.types.Node, *names: str):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return socket
    raise RuntimeError(f"Missing Principled input: {names}")


def material_pbr(
    name: str,
    base: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    noise_scale: float = 0.0,
    noise_strength: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
    transmission: float = 0.0,
    texture_set: dict[str, Path] | None = None,
    texture_scale: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    require(bsdf is not None, f"Principled BSDF missing: {name}")
    principled_socket(bsdf, "Base Color").default_value = base
    principled_socket(bsdf, "Metallic", "Metallic IOR Level").default_value = metallic
    principled_socket(bsdf, "Roughness").default_value = roughness
    principled_socket(bsdf, "Alpha").default_value = alpha
    transmission_socket = bsdf.inputs.get("Transmission Weight")
    if transmission_socket is None:
        transmission_socket = bsdf.inputs.get("Transmission")
    if transmission_socket is not None:
        transmission_socket.default_value = transmission
    if emission is not None:
        emission_color = bsdf.inputs.get("Emission Color")
        if emission_color is None:
            emission_color = bsdf.inputs.get("Emission")
        if emission_color is not None:
            emission_color.default_value = emission
        emission_power = bsdf.inputs.get("Emission Strength")
        if emission_power is not None:
            emission_power.default_value = emission_strength
    mapped_vector = None
    material_normal = None
    if texture_set is not None:
        for texture_path in texture_set.values():
            require(texture_path.is_file(), f"Texture missing: {texture_path}")
        texcoord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (texture_scale, texture_scale, texture_scale)
        links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])
        mapped_vector = mapping.outputs["Vector"]

        base_texture = nodes.new("ShaderNodeTexImage")
        base_texture.image = bpy.data.images.load(str(texture_set["base"]), check_existing=True)
        base_texture.interpolation = "Linear"
        base_texture.extension = "REPEAT"
        tint = nodes.new("ShaderNodeMixRGB")
        tint.blend_type = "MULTIPLY"
        tint.inputs[0].default_value = 1.0
        tint.inputs[2].default_value = base
        links.new(mapped_vector, base_texture.inputs["Vector"])
        links.new(base_texture.outputs["Color"], tint.inputs[1])
        links.new(tint.outputs["Color"], principled_socket(bsdf, "Base Color"))

        rough_texture = nodes.new("ShaderNodeTexImage")
        rough_texture.image = bpy.data.images.load(str(texture_set["roughness"]), check_existing=True)
        rough_texture.image.colorspace_settings.name = "Non-Color"
        rough_texture.interpolation = "Linear"
        rough_texture.extension = "REPEAT"
        rough_range = nodes.new("ShaderNodeMapRange")
        rough_range.inputs["To Min"].default_value = max(roughness - 0.22, 0.0)
        rough_range.inputs["To Max"].default_value = min(roughness + 0.22, 1.0)
        links.new(mapped_vector, rough_texture.inputs["Vector"])
        links.new(rough_texture.outputs["Color"], rough_range.inputs["Value"])
        links.new(rough_range.outputs["Result"], principled_socket(bsdf, "Roughness"))

        normal_texture = nodes.new("ShaderNodeTexImage")
        normal_texture.image = bpy.data.images.load(str(texture_set["normal"]), check_existing=True)
        normal_texture.image.colorspace_settings.name = "Non-Color"
        normal_texture.interpolation = "Linear"
        normal_texture.extension = "REPEAT"
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = 0.62
        links.new(mapped_vector, normal_texture.inputs["Vector"])
        links.new(normal_texture.outputs["Color"], normal_map.inputs["Color"])
        material_normal = normal_map.outputs["Normal"]

    if noise_scale > 0.0 and noise_strength > 0.0:
        texcoord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        noise = nodes.new("ShaderNodeTexNoise")
        bump = nodes.new("ShaderNodeBump")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 4.0
        noise.inputs["Roughness"].default_value = 0.62
        bump.inputs["Strength"].default_value = noise_strength
        bump.inputs["Distance"].default_value = 0.08
        links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        if material_normal is not None:
            links.new(material_normal, bump.inputs["Normal"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    elif material_normal is not None:
        links.new(material_normal, bsdf.inputs["Normal"])
    if alpha < 1.0:
        if hasattr(material, "surface_render_method"):
            set_supported(material, "surface_render_method", ("DITHERED", "BLENDED"))
        elif hasattr(material, "blend_method"):
            material.blend_method = "BLEND"
        material.diffuse_color = (*base[:3], alpha)
    return material


def make_materials() -> dict[str, bpy.types.Material]:
    return {
        "white": material_pbr("M_M01_Lighthouse_WhiteMasonry", (0.93, 0.94, 0.92, 1), 0.0, 0.74, 7.0, 0.15, texture_set=TEXTURE_SETS["plaster"], texture_scale=4.2),
        "red": material_pbr("M_M01_Lighthouse_RedMasonry", (0.72, 0.075, 0.038, 1), 0.0, 0.68, 6.0, 0.13, texture_set=TEXTURE_SETS["plaster"], texture_scale=4.2),
        "stone": material_pbr("M_M01_Lighthouse_FoundationStone", (0.50, 0.54, 0.58, 1), 0.0, 0.82, 9.0, 0.18, texture_set=TEXTURE_SETS["concrete"], texture_scale=3.0),
        "joint": material_pbr("M_M01_Lighthouse_MasonryJoint", (0.085, 0.09, 0.095, 1), 0.0, 0.92),
        "metal": material_pbr("M_M01_Lighthouse_BlackMarineMetal", (0.16, 0.18, 0.20, 1), 0.82, 0.31, 12.0, 0.05, texture_set=TEXTURE_SETS["metal"], texture_scale=5.0),
        "aged_metal": material_pbr("M_M01_Lighthouse_AgedMarineMetal", (0.42, 0.47, 0.42, 1), 0.68, 0.48, 10.0, 0.08, texture_set=TEXTURE_SETS["rust"], texture_scale=4.0),
        "glass": material_pbr("M_M01_Lighthouse_LanternGlass", (0.055, 0.15, 0.19, 1), 0.0, 0.08, alpha=0.34, transmission=0.72),
        "lens": material_pbr("M_M01_Lighthouse_FresnelLens", (0.58, 0.31, 0.055, 1), 0.12, 0.16, emission=(1.0, 0.32, 0.045, 1), emission_strength=2.8, alpha=0.82, transmission=0.42),
        "door": material_pbr("M_M01_Lighthouse_WeatheredDoor", (0.055, 0.07, 0.075, 1), 0.48, 0.48, 18.0, 0.16),
        "brass": material_pbr("M_M01_Lighthouse_BrassHardware", (0.31, 0.19, 0.045, 1), 0.88, 0.25, 15.0, 0.05),
        "window": material_pbr("M_M01_Lighthouse_WindowGlass", (0.025, 0.09, 0.13, 1), 0.0, 0.09, alpha=0.46, transmission=0.58),
        "concrete": material_pbr("M_M01_Lighthouse_ReviewConcrete", (0.10, 0.115, 0.125, 1), 0.0, 0.86, 5.0, 0.16),
    }


def assign(obj: bpy.types.Object, material: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def apply_transform(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> bpy.types.Object:
    modifier = obj.modifiers.new("ProductionEdgeBevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel_width: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transform(obj)
    if bevel_width > 0.0:
        bevel(obj, bevel_width, 3)
    assign(obj, material)
    group.append(obj)
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    vertices: int = 64,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel_width: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if bevel_width > 0.0:
        bevel(obj, bevel_width, 3)
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def add_cone(
    name: str,
    location: tuple[float, float, float],
    radius1: float,
    radius2: float,
    depth: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    vertices: int = 96,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    major_segments: int = 96,
    minor_segments: int = 10,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=major_segments,
        minor_segments=minor_segments,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transform(obj)
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def cylinder_between(
    name: str,
    start: Vector,
    end: Vector,
    radius: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    vertices: int = 16,
) -> bpy.types.Object:
    delta = end - start
    length = delta.length
    require(length > 0.0001, f"Degenerate cylinder: {name}")
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=(start + end) * 0.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    obj.rotation_mode = "XYZ"
    apply_transform(obj)
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def add_annulus(
    name: str,
    inner_radius: float,
    outer_radius: float,
    height: float,
    z: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    segments: int = 96,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for ring_z in (-height * 0.5, height * 0.5):
        for radius in (outer_radius, inner_radius):
            for index in range(segments):
                angle = 2.0 * math.pi * index / segments
                vertices.append((radius * math.cos(angle), radius * math.sin(angle), z + ring_z))
    outer_bottom = 0
    inner_bottom = segments
    outer_top = segments * 2
    inner_top = segments * 3
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((outer_bottom + index, outer_bottom + nxt, outer_top + nxt, outer_top + index))
        faces.append((inner_bottom + nxt, inner_bottom + index, inner_top + index, inner_top + nxt))
        faces.append((outer_top + index, outer_top + nxt, inner_top + nxt, inner_top + index))
        faces.append((outer_bottom + nxt, outer_bottom + index, inner_bottom + index, inner_bottom + nxt))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    smooth(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def add_arch_panel(
    name: str,
    width: float,
    bottom: float,
    spring: float,
    radius: float,
    thickness: float,
    radial_angle: float,
    radial_distance: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    arc_segments: int = 20,
) -> bpy.types.Object:
    points = [(-width * 0.5, bottom), (-width * 0.5, spring)]
    for index in range(arc_segments + 1):
        angle = math.pi - math.pi * index / arc_segments
        points.append((radius * math.cos(angle), spring + radius * math.sin(angle)))
    points.extend(((width * 0.5, spring), (width * 0.5, bottom)))
    vertices: list[tuple[float, float, float]] = []
    for y in (-thickness * 0.5, thickness * 0.5):
        vertices.extend((x, y, z) for x, z in points)
    count = len(points)
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = (radial_distance * math.cos(radial_angle), radial_distance * math.sin(radial_angle), 0.0)
    obj.rotation_euler.z = radial_angle - math.pi * 0.5
    apply_transform(obj)
    assign(obj, material)
    group.append(obj)
    return obj


def radius_at(z: float) -> float:
    lower_z, upper_z = 1.2, 19.0
    lower_r, upper_r = 3.20, 2.46
    t = max(0.0, min(1.0, (z - lower_z) / (upper_z - lower_z)))
    return lower_r + (upper_r - lower_r) * t


def add_radial_box(
    name: str,
    angle: float,
    radius: float,
    z: float,
    tangent_width: float,
    radial_depth: float,
    height: float,
    material: bpy.types.Material,
    group: list[bpy.types.Object],
    bevel_width: float = 0.018,
) -> bpy.types.Object:
    location = (radius * math.cos(angle), radius * math.sin(angle), z)
    rotation = (0.0, 0.0, angle - math.pi * 0.5)
    return add_box(name, location, (tangent_width, radial_depth, height), material, group, rotation, bevel_width)


def add_window(
    index: int,
    angle: float,
    z: float,
    materials: dict[str, bpy.types.Material],
    details: list[bpy.types.Object],
) -> None:
    radius = radius_at(z) + 0.035
    add_radial_box(f"Window{index:02d}_Glass", angle, radius + 0.08, z, 0.68, 0.09, 0.96, materials["window"], details, 0.015)
    trim_r = radius + 0.14
    add_radial_box(f"Window{index:02d}_TrimL", angle, trim_r, z, 0.10, 0.13, 1.18, materials["stone"], details)
    left = details[-1]
    tangent = Vector((-math.sin(angle), math.cos(angle), 0.0))
    left.location += tangent * -0.40
    add_radial_box(f"Window{index:02d}_TrimR", angle, trim_r, z, 0.10, 0.13, 1.18, materials["stone"], details)
    details[-1].location += tangent * 0.40
    add_radial_box(f"Window{index:02d}_Lintel", angle, trim_r, z + 0.56, 0.92, 0.14, 0.12, materials["stone"], details)
    add_radial_box(f"Window{index:02d}_Sill", angle, trim_r + 0.03, z - 0.56, 0.94, 0.21, 0.12, materials["stone"], details)
    add_radial_box(f"Window{index:02d}_Mullion", angle, trim_r + 0.15, z, 0.055, 0.06, 0.90, materials["metal"], details, 0.008)


def join_group(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    meshes = [obj for obj in objects if obj and obj.type == "MESH"]
    require(meshes, f"No mesh objects for {name}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = name
    apply_transform(joined)
    bpy.context.view_layer.objects.active = joined
    joined.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode="OBJECT")
    for polygon in joined.data.polygons:
        polygon.use_smooth = True
    joined["asset_id"] = ASSET_ID
    joined["production_candidate"] = True
    return joined


def build_geometry(materials: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], list[bpy.types.Object], list[bpy.types.Object]]:
    tower: list[bpy.types.Object] = []
    lantern: list[bpy.types.Object] = []
    details: list[bpy.types.Object] = []

    # Grounded foundation and stepped marine plinth.
    add_cylinder("Foundation_Footing", (0, 0, 0.22), 4.15, 0.44, materials["stone"], tower, 96, bevel_width=0.06)
    add_cylinder("Foundation_Step01", (0, 0, 0.52), 3.92, 0.30, materials["stone"], tower, 96, bevel_width=0.05)
    add_cylinder("Foundation_Step02", (0, 0, 0.84), 3.66, 0.34, materials["stone"], tower, 96, bevel_width=0.045)
    add_cylinder("Foundation_Cap", (0, 0, 1.10), 3.43, 0.20, materials["stone"], tower, 96, bevel_width=0.035)
    for z in (0.32, 0.62, 0.92):
        add_torus(f"Foundation_Course_{z:.2f}", (0, 0, z), 3.75 - z * 0.22, 0.028, materials["joint"], details, 96, 8)

    # Tapered tower sections avoid overlapping shells.
    sections = [
        (1.20, 5.95, materials["white"], "WhiteLower"),
        (5.95, 8.15, materials["red"], "RedLower"),
        (8.15, 13.00, materials["white"], "WhiteMiddle"),
        (13.00, 15.20, materials["red"], "RedUpper"),
        (15.20, 19.00, materials["white"], "WhiteUpper"),
    ]
    for lower, upper, material, label in sections:
        add_cone(
            f"Tower_{label}",
            (0, 0, (lower + upper) * 0.5),
            radius_at(lower),
            radius_at(upper),
            upper - lower,
            material,
            tower,
            128,
        )

    # Subtle masonry courses, alternating offsets prevent a toy striped read.
    course_index = 0
    z = 1.72
    while z < 18.82:
        add_torus(
            f"MasonryCourse_{course_index:02d}",
            (0, 0, z),
            radius_at(z) + 0.006,
            0.014 if course_index % 3 else 0.020,
            materials["joint"],
            details,
            128,
            6,
        )
        course_index += 1
        z += 0.58 if course_index % 2 else 0.62

    # Arched entrance, threshold, trim and hardware at seaward/front side.
    front = -math.pi * 0.5
    add_arch_panel("Entrance_StonePortal", 1.72, 0.18, 1.70, 0.86, 0.24, front, 3.32, materials["stone"], details, 24)
    add_arch_panel("Entrance_Door", 1.28, 0.28, 1.62, 0.64, 0.18, front, 3.46, materials["door"], details, 24)
    add_radial_box("Entrance_Threshold", front, 3.54, 0.23, 1.65, 0.52, 0.16, materials["stone"], details, 0.025)
    add_radial_box("Entrance_DoorSeam", front, 3.57, 1.12, 0.035, 0.035, 1.52, materials["metal"], details, 0.006)
    add_radial_box("Entrance_KickPlate", front, 3.58, 0.52, 0.86, 0.025, 0.28, materials["aged_metal"], details, 0.008)
    add_uv_sphere("Entrance_Handle", (0.43, -3.61, 1.23), 0.07, materials["brass"], details, (1.0, 0.65, 1.0))
    for side in (-1, 1):
        for row in range(4):
            angle = front + side * 0.19
            add_radial_box(
                f"Entrance_Voussoir_{side}_{row}",
                angle,
                3.38,
                1.58 + row * 0.28,
                0.27,
                0.18,
                0.20,
                materials["stone"],
                details,
                0.018,
            )

    # Four staggered service windows and one lower ventilation pair.
    for idx, (angle, height) in enumerate(((-0.78, 5.0), (0.72, 9.6), (2.35, 13.7), (-2.45, 16.7)), 1):
        add_window(idx, angle, height, materials, details)
    for idx, angle in enumerate((0.35, math.pi - 0.35), 1):
        add_radial_box(f"Vent{idx}_Recess", angle, 3.34, 1.55, 0.58, 0.11, 0.34, materials["metal"], details, 0.012)
        for bar in range(4):
            add_radial_box(f"Vent{idx}_Louver{bar}", angle, 3.42, 1.42 + bar * 0.085, 0.50, 0.055, 0.035, materials["aged_metal"], details, 0.004)

    # Rear marine downpipe with brackets.
    rear = math.pi * 0.5
    pipe_radius = radius_at(10.0) + 0.20
    cylinder_between("Service_Downpipe", Vector((0, pipe_radius, 1.15)), Vector((0, radius_at(18.5) + 0.20, 18.55)), 0.065, materials["aged_metal"], details, 18)
    for idx, height in enumerate((2.0, 4.5, 7.0, 9.5, 12.0, 14.5, 17.0)):
        add_radial_box(f"Downpipe_Bracket_{idx}", rear, radius_at(height) + 0.13, height, 0.34, 0.08, 0.08, materials["metal"], details, 0.008)

    # Gallery deck, corbels, braces and railings.
    add_annulus("Gallery_Deck", 2.18, 3.40, 0.24, 19.35, materials["aged_metal"], lantern, 128)
    add_torus("Gallery_FasciaUpper", (0, 0, 19.47), 3.37, 0.085, materials["metal"], lantern, 128, 12)
    add_torus("Gallery_FasciaLower", (0, 0, 19.22), 3.23, 0.070, materials["metal"], lantern, 128, 10)
    for idx in range(24):
        angle = 2.0 * math.pi * idx / 24
        radial = Vector((math.cos(angle), math.sin(angle), 0.0))
        cylinder_between(
            f"Gallery_Corbel_{idx:02d}",
            radial * 2.36 + Vector((0, 0, 18.72)),
            radial * 3.16 + Vector((0, 0, 19.28)),
            0.075,
            materials["metal"],
            lantern,
            14,
        )
        cylinder_between(
            f"Gallery_RailPost_{idx:02d}",
            radial * 3.23 + Vector((0, 0, 19.47)),
            radial * 3.23 + Vector((0, 0, 20.72)),
            0.040,
            materials["metal"],
            lantern,
            12,
        )
    for height in (19.58, 20.10, 20.72):
        add_torus(f"Gallery_Rail_{height:.2f}", (0, 0, height), 3.23, 0.040, materials["metal"], lantern, 128, 8)

    # Lantern base, glazing cylinder, frame, Fresnel optic and roof.
    add_cylinder("Lantern_BasePlinth", (0, 0, 19.85), 2.52, 0.62, materials["stone"], lantern, 128, bevel_width=0.055)
    add_cylinder("Lantern_LowerSill", (0, 0, 20.30), 2.38, 0.30, materials["metal"], lantern, 128, bevel_width=0.035)
    add_cylinder("Lantern_GlassShell", (0, 0, 21.68), 2.22, 2.55, materials["glass"], lantern, 96)
    add_torus("Lantern_FrameLower", (0, 0, 20.48), 2.23, 0.075, materials["metal"], lantern, 128, 10)
    add_torus("Lantern_FrameMiddle", (0, 0, 21.68), 2.23, 0.045, materials["metal"], lantern, 128, 8)
    add_torus("Lantern_FrameUpper", (0, 0, 22.88), 2.23, 0.075, materials["metal"], lantern, 128, 10)
    for idx in range(16):
        angle = 2.0 * math.pi * idx / 16
        radial = Vector((math.cos(angle), math.sin(angle), 0.0))
        cylinder_between(
            f"Lantern_Mullion_{idx:02d}",
            radial * 2.23 + Vector((0, 0, 20.46)),
            radial * 2.23 + Vector((0, 0, 22.92)),
            0.047,
            materials["metal"],
            lantern,
            12,
        )
    add_cylinder("Lens_CentralPedestal", (0, 0, 20.98), 0.46, 0.90, materials["brass"], lantern, 48, bevel_width=0.025)
    add_cylinder("Lens_FresnelCore", (0, 0, 21.92), 0.72, 1.38, materials["lens"], lantern, 64)
    for idx, z in enumerate((21.36, 21.60, 21.84, 22.08, 22.32, 22.56)):
        add_torus(f"Lens_FresnelRing_{idx}", (0, 0, z), 0.74 + 0.02 * math.sin(idx), 0.055, materials["lens"], lantern, 64, 8)
    add_cylinder("Lens_TopCap", (0, 0, 22.67), 0.55, 0.18, materials["brass"], lantern, 48, bevel_width=0.018)

    add_cylinder("Roof_DripRing", (0, 0, 23.05), 2.50, 0.20, materials["metal"], lantern, 128, bevel_width=0.035)
    add_cone("Roof_Main", (0, 0, 24.05), 2.92, 0.40, 2.10, materials["red"], lantern, 128)
    add_torus("Roof_Eave", (0, 0, 23.08), 2.86, 0.090, materials["metal"], lantern, 128, 12)
    add_cylinder("Roof_Vent", (0, 0, 25.22), 0.34, 0.55, materials["metal"], lantern, 48, bevel_width=0.025)
    add_uv_sphere("Roof_Finial", (0, 0, 25.58), 0.22, materials["brass"], lantern, (0.80, 0.80, 1.25))
    cylinder_between("Lightning_Rod", Vector((0, 0, 25.72)), Vector((0, 0, 27.00)), 0.035, materials["aged_metal"], lantern, 12)
    cylinder_between("WeatherVane_Crossbar", Vector((-0.62, 0, 26.43)), Vector((0.62, 0, 26.43)), 0.028, materials["aged_metal"], lantern, 10)
    add_box("WeatherVane_Pointer", (0.52, 0, 26.43), (0.34, 0.06, 0.16), materials["aged_metal"], lantern, rotation=(0, math.radians(-18), 0), bevel_width=0.008)

    # Gallery service hatch and lamp-house maintenance details.
    add_radial_box("Lantern_ServiceDoor", front, 2.48, 21.16, 0.78, 0.10, 1.44, materials["door"], details, 0.025)
    for height in (20.72, 21.20, 21.68, 22.16, 22.64):
        add_radial_box(f"Lantern_ServiceLadder_Rung_{height:.2f}", 0.0, 2.36, height, 0.68, 0.08, 0.045, materials["metal"], details, 0.006)
    for side in (-0.30, 0.30):
        cylinder_between(
            f"Lantern_ServiceLadder_Rail_{side:+.2f}",
            Vector((2.36, side, 20.55)),
            Vector((2.36, side, 22.82)),
            0.032,
            materials["metal"],
            details,
            10,
        )

    return tower, lantern, details


def create_collision_and_sockets(materials: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    collision_group: list[bpy.types.Object] = []
    add_cone(COLLISIONS[0], (0, 0, 9.60), 3.92, 2.52, 19.20, materials["stone"], collision_group, 16)
    add_cylinder(COLLISIONS[1], (0, 0, 22.15), 3.38, 6.10, materials["metal"], collision_group, 16)
    for obj in collision_group:
        obj.display_type = "WIRE"
        obj.hide_render = True
        obj["collision_role"] = "UCX"

    socket_group: list[bpy.types.Object] = []
    socket_data = {
        SOCKETS[0]: (0.0, 0.0, 0.0),
        SOCKETS[1]: (0.0, -3.55, 1.20),
        SOCKETS[2]: (0.0, -3.25, 19.55),
        SOCKETS[3]: (0.0, 0.0, 21.92),
    }
    for name, location in socket_data.items():
        obj = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.35
        obj["socket_role"] = name.removeprefix("SOCKET_")
        socket_group.append(obj)
    return collision_group, socket_group


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    require(points, "No bounds")
    return (
        Vector(tuple(min(point[index] for point in points) for index in range(3))),
        Vector(tuple(max(point[index] for point in points) for index in range(3))),
    )


def clear_review() -> None:
    collection = bpy.data.collections.get("REVIEW_ONLY")
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float] | Vector) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def review_area(name: str, location, energy: float, size: float, color, target=(0, 0, 12)) -> None:
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, target)


def review_sun(name: str, rotation, energy: float, color) -> None:
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.5)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.rotation_euler = rotation


def review_ground(material: bpy.types.Material, wet: bool = False) -> None:
    bpy.ops.mesh.primitive_plane_add(size=120.0, location=(0, 0, -0.025))
    obj = bpy.context.object
    obj.name = "REVIEW_Ground"
    move_to_collection(obj, "REVIEW_ONLY")
    if wet:
        wet_material = material.copy()
        wet_material.name = "REVIEW_WetGround"
        bsdf = wet_material.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            principled_socket(bsdf, "Roughness").default_value = 0.16
        obj.data.materials.append(wet_material)
    else:
        obj.data.materials.append(material)


def stage(mode: str, materials: dict[str, bpy.types.Material]) -> None:
    clear_review()
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    require(background is not None, "Background node missing")
    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    set_supported(scene.view_settings, "look", ("AgX - Medium High Contrast", "Medium High Contrast", "None"))
    scene.view_settings.exposure = 0.8
    if mode == "night":
        background.inputs["Color"].default_value = (0.008, 0.015, 0.030, 1)
        background.inputs["Strength"].default_value = 0.16
        review_area("REVIEW_Moon", (-20, -28, 38), 5200, 18, (0.28, 0.48, 1.0))
        review_area("REVIEW_LanternRim", (16, 10, 25), 2600, 10, (1.0, 0.32, 0.08))
        scene.view_settings.exposure = 1.6
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.12, 0.17, 0.24, 1)
        background.inputs["Strength"].default_value = 0.48
        review_area("REVIEW_WetKey", (-22, -28, 40), 7200, 22, (0.48, 0.70, 1.0))
        review_area("REVIEW_WetRim", (18, 12, 25), 4200, 14, (1.0, 0.44, 0.18))
        scene.view_settings.exposure = 1.05
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.31, 0.38, 0.49, 1)
        background.inputs["Strength"].default_value = 0.72
        review_area("REVIEW_CloudKey", (-25, -32, 44), 8500, 26, (0.74, 0.84, 1.0))
        review_area("REVIEW_CloudFill", (24, 16, 30), 5200, 22, (0.62, 0.70, 0.82))
        scene.view_settings.exposure = 0.7
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.02, 0.035, 0.055, 1)
        background.inputs["Strength"].default_value = 0.22
        review_area("REVIEW_Worklight", (18, -28, 24), 6800, 18, (0.42, 0.70, 1.0))
        review_area("REVIEW_Amber", (-16, 10, 18), 3900, 12, (1.0, 0.36, 0.10))
        scene.view_settings.exposure = 1.35
    else:
        background.inputs["Color"].default_value = (0.34, 0.51, 0.74, 1)
        background.inputs["Strength"].default_value = 0.78
        review_sun("REVIEW_Sun", (math.radians(30), math.radians(-20), math.radians(-34)), 3.4, (1.0, 0.82, 0.62))
        review_area("REVIEW_Sky", (24, -34, 42), 5400, 22, (0.52, 0.72, 1.0))
        review_area("REVIEW_Bounce", (-22, 16, 18), 2800, 18, (1.0, 0.52, 0.28))
        scene.view_settings.exposure = 0.65
    review_ground(materials["concrete"], wet=(mode == "wet"))


def review_camera(location, target, lens: float) -> bpy.types.Object:
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.05
    data.clip_end = 500.0
    obj = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def mean_luminance() -> float:
    image = bpy.data.images.get("Render Result")
    require(image is not None and image.has_data, "Render result unavailable")
    pixels = image.pixels[:]
    count = len(pixels) // 4
    stride = max(count // 16384, 1)
    values = []
    for index in range(0, count, stride):
        r, g, b = pixels[index * 4 : index * 4 + 3]
        values.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
    return sum(values) / len(values)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def render_view(output: Path, filename: str, location, target, lens: float, mode: str, materials) -> dict[str, object]:
    stage(mode, materials)
    scene = bpy.context.scene
    scene.camera = review_camera(location, target, lens)
    path = output / filename
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    luminance = mean_luminance()
    if luminance < 0.08:
        scene.view_settings.exposure += 1.25
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    elif luminance > 0.72:
        scene.view_settings.exposure -= 0.85
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    require(path.is_file(), f"Render missing: {path}")
    width, height = png_dimensions(path)
    require((width, height) == (2048, 1152), f"Wrong render dimensions: {path} {width}x{height}")
    return {**record(path), "mode": mode, "mean_luminance": luminance, "width": width, "height": height}


def glb_inventory(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        magic, version, total_length = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2, "Invalid GLB header")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "GLB JSON chunk missing")
        payload = json.loads(stream.read(chunk_length).decode("utf-8").rstrip("\x00 \t\r\n"))
    require(total_length == path.stat().st_size, "GLB byte declaration mismatch")
    return {
        "nodes": [node.get("name") for node in payload.get("nodes", [])],
        "mesh_count": len(payload.get("meshes", [])),
        "material_count": len(payload.get("materials", [])),
        "image_count": len(payload.get("images", [])),
    }


def export_glb(path: Path, render_meshes, collisions, sockets) -> dict[str, object]:
    bpy.ops.object.select_all(action="DESELECT")
    export_objects = [*render_meshes, *collisions, *sockets]
    for obj in export_objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = render_meshes[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    require(path.is_file(), "GLB missing")
    inventory = glb_inventory(path)
    for name in (*RENDER_MESHES, *COLLISIONS, *SOCKETS):
        require(name in inventory["nodes"], f"GLB missing node: {name}")
    return inventory


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args(argv)
    contract_path = Path(args.contract)
    attempt = Path(args.attempt)
    output = attempt / "output"
    renders = output / "renders"
    exports = output / "exports"
    receipts = output / "receipts"
    for directory in (output, renders, exports, receipts):
        directory.mkdir(parents=True, exist_ok=False)
    blend_path = output / "M01_Lighthouse_Production_Refinement01.blend"
    glb_path = exports / "M01_Lighthouse_Production_Refinement01.glb"
    receipt_path = receipts / "production_receipt.json"
    report: dict[str, object] = {
        "schema": "skyguard.m01-lighthouse-production-refinement01.receipt.v1",
        "created_at_utc": utc_now(),
        "classification": "FAILED_WITH_EVIDENCE",
        "asset_id": ASSET_ID,
        "error": None,
        "traceback": None,
        "render_count": 0,
    }
    exit_code = 3
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_BLENDER_EXECUTION", "Contract classification changed")
        for entry in contract["authorities"]:
            path = Path(entry["path"])
            require(path.is_file(), f"Authority missing: {path}")
            require(path.stat().st_size == int(entry["bytes"]), f"Authority byte mismatch: {path}")
            require(sha256(path) == entry["sha256"], f"Authority hash mismatch: {path}")

        clear_scene()
        materials = make_materials()
        tower_parts, lantern_parts, detail_parts = build_geometry(materials)
        tower = join_group(tower_parts, RENDER_MESHES[0])
        lantern = join_group(lantern_parts, RENDER_MESHES[1])
        details = join_group(detail_parts, RENDER_MESHES[2])
        render_meshes = [tower, lantern, details]
        collisions, sockets = create_collision_and_sockets(materials)
        for obj in render_meshes:
            move_to_collection(obj, "PRODUCTION_RENDER")
            obj.hide_render = False
        for obj in collisions:
            move_to_collection(obj, "PRODUCTION_COLLISION")
        for obj in sockets:
            move_to_collection(obj, "PRODUCTION_SOCKETS")

        minimum, maximum = bounds(render_meshes)
        size = maximum - minimum
        require(7.8 <= size.x <= 8.5, f"Width outside contract: {size.x}")
        require(7.8 <= size.y <= 8.5, f"Depth outside contract: {size.y}")
        require(26.8 <= size.z <= 27.3, f"Height outside contract: {size.z}")
        require(-0.05 <= minimum.z <= 0.05, f"Asset not grounded: {minimum.z}")
        vertices = sum(len(obj.data.vertices) for obj in render_meshes)
        polygons = sum(len(obj.data.polygons) for obj in render_meshes)
        triangles = 0
        for obj in render_meshes:
            obj.data.calc_loop_triangles()
            triangles += len(obj.data.loop_triangles)
            require(len(obj.data.uv_layers) > 0, f"UV missing: {obj.name}")
        require(vertices >= 25000, f"Insufficient authored detail: {vertices} vertices")
        require(triangles >= 45000, f"Insufficient authored detail: {triangles} triangles")

        scene = bpy.context.scene
        set_supported(scene.render, "engine", ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"))
        scene.render.resolution_x = 2048
        scene.render.resolution_y = 1152
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.film_transparent = False
        scene.render.use_file_extension = True
        scene.render.image_settings.color_depth = "8"
        scene.render.image_settings.compression = 15
        scene.camera = None
        for obj in collisions:
            obj.hide_render = True

        views = [
            ("01_daylight_front_full.png", (0, -76, 14.0), (0, 0, 13.2), 55.0, "daylight"),
            ("02_daylight_oblique_full.png", (50, -62, 18.5), (0, 0, 13.2), 58.0, "daylight"),
            ("03_overcast_rear_full.png", (-48, 62, 17.5), (0, 0, 13.0), 58.0, "overcast"),
            ("04_wet_low_angle_full.png", (0, -58, 5.5), (0, 0, 12.5), 54.0, "wet"),
            ("05_night_lantern_full.png", (43, -59, 17.0), (0, 0, 13.5), 58.0, "night"),
            ("06_cockpit_height_context.png", (-36, -68, 22.0), (0, 0, 13.2), 62.0, "cockpit"),
            ("07_gallery_lantern_detail.png", (11, -17, 22.5), (0, 0, 21.5), 70.0, "daylight"),
            ("08_roof_optic_detail.png", (-10, -15, 24.8), (0, 0, 23.0), 72.0, "overcast"),
            ("09_entrance_foundation_detail.png", (6.5, -13.5, 2.8), (0, -2.8, 1.4), 68.0, "daylight"),
            ("10_window_masonry_detail.png", (10, -16, 11.5), (0, 0, 11.0), 72.0, "overcast"),
            ("11_gallery_structure_wet.png", (-11, -17, 19.2), (0, 0, 19.8), 70.0, "wet"),
            ("12_night_lens_close.png", (8.5, -13, 22.4), (0, 0, 21.8), 76.0, "night"),
        ]
        render_rows = [render_view(renders, *view, materials) for view in views]
        require(len(render_rows) == 12, "Render count mismatch")

        clear_review()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        require(blend_path.is_file(), "Blend missing")
        glb = export_glb(glb_path, render_meshes, collisions, sockets)
        report.update(
            {
                "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
                "identity": "Project-authored non-branded Ukrainian coastal lighthouse landmark",
                "dimensions_m": [float(size.x), float(size.y), float(size.z)],
                "bounds_min_m": [float(v) for v in minimum],
                "bounds_max_m": [float(v) for v in maximum],
                "vertices": vertices,
                "polygons": polygons,
                "triangles": triangles,
                "render_meshes": list(RENDER_MESHES),
                "collision_meshes": list(COLLISIONS),
                "sockets": list(SOCKETS),
                "material_names": sorted(material.name for material in materials.values()),
                "uv_complete": True,
                "render_count": 12,
                "renders": render_rows,
                "blend": record(blend_path),
                "glb": {**record(glb_path), **glb},
                "runtime_promotion_authorized": False,
                "unreal_import_authorized": False,
                "remaining_gate": "Direct full-resolution review, then fresh reversible Unreal staging and D3D12 mapped proof.",
            }
        )
        exit_code = 0
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(receipt_path, report)
        inventory = []
        for path in sorted(attempt.rglob("*")):
            if path.is_file() and path.name != "artifact_inventory.json":
                inventory.append(record(path))
        write_json_atomic(
            attempt / "artifact_inventory.json",
            {
                "schema": "skyguard.m01-lighthouse-production-refinement01.artifact-inventory.v1",
                "created_at_utc": utc_now(),
                "classification": report["classification"],
                "artifacts": inventory,
            },
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
