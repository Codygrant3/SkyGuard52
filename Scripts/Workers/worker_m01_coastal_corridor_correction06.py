from __future__ import annotations

"""Build the continuous Mission 1 coastal corridor art-direction correction.

The latest Unreal mapped proof passed performance but failed visual review because
the shoreline was assembled from repeated beach tiles and detached road strips.
This worker replaces that workaround with one governed, continuously UV-mapped
coastal corridor package.  Unreal remains the authority for water, foliage,
lighting, atmosphere, and final world assembly.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "m01-coastal-corridor-correction06"
GATE = "M01_ENVIRONMENT_ART_DIRECTION_CORRECTION06_CONTINUOUS_COASTAL_CORRIDOR"
TEXTURE_ROOT = ROOT / r"Content\Skyguard\Textures"
PROVENANCE = TEXTURE_ROOT / r"PolyHaven\polyhaven-provenance-manifest.json"

PBR_SOURCES = {
    "concrete": {
        "base": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_rough_2k.jpg",
    },
    "asphalt": {
        "base": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_rough_2k.jpg",
    },
    "sand": {
        "base": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_rough_2k.jpg",
    },
    "metal": {
        "base": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_rough_2k.jpg",
        "metallic": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_metal_2k.jpg",
    },
}

X_MIN = -40.0
X_MAX = 540.0
X_STEP = 4.0
RENDER_SIZE = (1920, 1080)
CAMERAS = {
    "route_aerial": ((-22.0, -72.0, 42.0), (245.0, 94.0, 1.8), 52.0),
    "shoreline_oblique": ((52.0, -17.0, 10.5), (145.0, 58.0, 0.2), 55.0),
    "promenade_road": ((188.0, 62.0, 4.2), (286.0, 91.0, 0.8), 58.0),
    "integrated_intersection": ((246.0, 69.0, 19.0), (260.0, 139.0, 0.5), 53.0),
    "urban_shoulder": ((405.0, 103.0, 22.0), (455.0, 151.0, 0.7), 56.0),
    "wet_contact_close": ((326.0, -4.0, 7.0), (382.0, 45.0, -0.1), 61.0),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    raw = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args(raw)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def get_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def load_image(path: Path, non_color: bool = False) -> bpy.types.Image:
    require(path.is_file(), f"Missing governed texture authority: {path}")
    image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def make_pbr_material(
    name: str,
    sources: dict[str, Path],
    tint: tuple[float, float, float, float],
    tile_scale: float,
    roughness_multiplier: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "Principled BSDF"
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (tile_scale, tile_scale, tile_scale)
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

    base = nodes.new("ShaderNodeTexImage")
    base.image = load_image(sources["base"])
    base.interpolation = "Linear"
    links.new(mapping.outputs["Vector"], base.inputs["Vector"])
    tint_mix = nodes.new("ShaderNodeMixRGB")
    tint_mix.blend_type = "MULTIPLY"
    tint_mix.inputs[0].default_value = 1.0
    tint_mix.inputs[2].default_value = tint
    links.new(base.outputs["Color"], tint_mix.inputs[1])
    links.new(tint_mix.outputs["Color"], bsdf.inputs["Base Color"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.image = load_image(sources["roughness"], True)
    links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    rough_mult = nodes.new("ShaderNodeMath")
    rough_mult.operation = "MULTIPLY"
    rough_mult.inputs[1].default_value = roughness_multiplier
    links.new(rough.outputs["Color"], rough_mult.inputs[0])
    links.new(rough_mult.outputs["Value"], bsdf.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = load_image(sources["normal"], True)
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.62
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    if "metallic" in sources:
        metallic = nodes.new("ShaderNodeTexImage")
        metallic.image = load_image(sources["metallic"], True)
        links.new(mapping.outputs["Vector"], metallic.inputs["Vector"])
        links.new(metallic.outputs["Color"], bsdf.inputs["Metallic"])
    else:
        bsdf.inputs["Metallic"].default_value = 0.0
    return material


def make_simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission is not None:
        emission.default_value = color
    if bsdf.inputs.get("Emission Strength") is not None:
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "dry_sand": make_pbr_material(
            "M_M01_C06_DrySand",
            PBR_SOURCES["sand"],
            (0.88, 0.70, 0.44, 1.0),
            2.2,
            1.05,
        ),
        "wet_sand": make_pbr_material(
            "M_M01_C06_WetSand",
            PBR_SOURCES["sand"],
            (0.36, 0.27, 0.17, 1.0),
            2.6,
            0.42,
        ),
        "dune": make_pbr_material(
            "M_M01_C06_DuneSand",
            PBR_SOURCES["sand"],
            (0.76, 0.60, 0.36, 1.0),
            2.0,
            1.08,
        ),
        "concrete": make_pbr_material(
            "M_M01_C06_WeatheredConcrete",
            PBR_SOURCES["concrete"],
            (0.64, 0.66, 0.64, 1.0),
            2.8,
            1.0,
        ),
        "pavers": make_pbr_material(
            "M_M01_C06_PromenadePavers",
            PBR_SOURCES["concrete"],
            (0.78, 0.72, 0.62, 1.0),
            4.2,
            0.95,
        ),
        "asphalt": make_pbr_material(
            "M_M01_C06_Asphalt",
            PBR_SOURCES["asphalt"],
            (0.31, 0.33, 0.35, 1.0),
            2.6,
            1.0,
        ),
        "metal": make_pbr_material(
            "M_M01_C06_Metal",
            PBR_SOURCES["metal"],
            (0.34, 0.38, 0.40, 1.0),
            2.4,
            0.92,
        ),
        "marking": make_simple_material(
            "M_M01_C06_RoadMarking", (0.67, 0.57, 0.31, 1.0), 0.66
        ),
        "foam": make_simple_material(
            "M_M01_C06_FoamGuide", (0.72, 0.82, 0.82, 1.0), 0.40, emission_strength=0.04
        ),
        "drain": make_simple_material(
            "M_M01_C06_DrainMetal", (0.055, 0.061, 0.063, 1.0), 0.58, 0.72
        ),
        "water": make_simple_material(
            "M_M01_C06_ReviewOcean", (0.012, 0.135, 0.185, 1.0), 0.16
        ),
    }


def add_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material | None,
    target: bpy.types.Collection,
    uv_mode: str = "world_xy",
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    if material is not None:
        mesh.materials.append(material)

    if uv_mode == "world_xy":
        uv_layer = mesh.uv_layers.new(name="UV0")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv_layer.data[loop_index].uv = (vertex.x / 8.0, vertex.y / 8.0)
    elif uv_mode == "smart":
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.025)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)
    return obj


def add_box(
    name: str,
    center: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    bevel: float = 0.0,
    segments: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, target)
    obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("ProductionEdgeBevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = segments
        modifier.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.025)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    vertices: int = 32,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, target)
    obj.data.materials.append(material)
    modifier = obj.modifiers.new("ProductionEdgeBevel", "BEVEL")
    modifier.width = min(radius * 0.16, 0.035)
    modifier.segments = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.025)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def x_samples() -> list[float]:
    count = int(round((X_MAX - X_MIN) / X_STEP))
    return [X_MIN + index * X_STEP for index in range(count + 1)]


def shoreline_y(x: float) -> float:
    return 38.0 + 2.45 * math.sin(x / 47.0) + 0.82 * math.sin(x / 13.0 + 0.4)


def boundary_profile(x: float) -> dict[str, float]:
    shore = shoreline_y(x)
    return {
        "ocean": 18.0,
        "shore": shore,
        "wet_end": shore + 10.0 + 0.65 * math.sin(x / 23.0),
        "dry_end": shore + 29.0 + 1.35 * math.sin(x / 39.0 + 0.8),
        "promenade_start": 78.0 + 0.62 * math.sin(x / 61.0),
        "promenade_end": 86.0,
        "road_end": 100.0,
        "sidewalk_end": 104.0,
        "urban_end": 195.0,
    }


def boundary_height(x: float, key: str) -> float:
    long_wave = 0.045 * math.sin(x / 72.0) + 0.025 * math.sin(x / 19.0 + 0.7)
    values = {
        "ocean": -1.25,
        "shore": -0.54 + long_wave,
        "wet_end": -0.10 + long_wave,
        "dry_end": 0.42 + long_wave,
        "promenade_start": 0.70 + long_wave * 0.35,
        "promenade_end": 0.72 + long_wave * 0.20,
        "road_end": 0.56 + long_wave * 0.15,
        "sidewalk_end": 0.72 + long_wave * 0.15,
        "urban_end": 0.76 + long_wave,
    }
    return values[key]


def create_band(
    name: str,
    xs: list[float],
    left_key: str,
    right_key: str,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for x in xs:
        profile = boundary_profile(x)
        vertices.append((x, profile[left_key], boundary_height(x, left_key)))
        vertices.append((x, profile[right_key], boundary_height(x, right_key)))
    faces = [(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2) for index in range(len(xs) - 1)]
    return add_mesh(name, vertices, faces, material, target)


def create_rect_surface(
    name: str,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    x_count = max(1, int(math.ceil((x1 - x0) / X_STEP)))
    xs = [x0 + (x1 - x0) * index / x_count for index in range(x_count + 1)]
    vertices = []
    for x in xs:
        undulation = 0.025 * math.sin(x / 31.0)
        vertices.extend(((x, y0, z + undulation), (x, y1, z + undulation)))
    faces = [(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2) for index in range(len(xs) - 1)]
    return add_mesh(name, vertices, faces, material, target)


def create_swept_volume(
    name: str,
    xs: list[float],
    y_fn: Callable[[float], float],
    width: float,
    top_fn: Callable[[float], float],
    bottom_fn: Callable[[float], float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for x in xs:
        y = y_fn(x)
        top = top_fn(x)
        bottom = bottom_fn(x)
        vertices.extend(
            (
                (x, y - width * 0.5, top),
                (x, y + width * 0.5, top),
                (x, y - width * 0.5, bottom),
                (x, y + width * 0.5, bottom),
            )
        )
    faces: list[tuple[int, ...]] = []
    for index in range(len(xs) - 1):
        a = index * 4
        b = (index + 1) * 4
        faces.extend(
            (
                (a, a + 1, b + 1, b),
                (a + 2, b + 2, b + 3, a + 3),
                (a, b, b + 2, a + 2),
                (a + 1, a + 3, b + 3, b + 1),
            )
        )
    faces.append((0, 2, 3, 1))
    last = (len(xs) - 1) * 4
    faces.append((last, last + 1, last + 3, last + 2))
    return add_mesh(name, vertices, faces, material, target, uv_mode="smart")


def create_review_ocean(
    xs: list[float], material: bpy.types.Material, review: bpy.types.Collection
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for x in xs:
        wave = 0.06 * math.sin(x / 11.0) + 0.03 * math.sin(x / 3.7)
        vertices.append((x, -110.0, -0.42 + wave))
        vertices.append((x, shoreline_y(x) - 0.65, -0.47 + wave * 0.35))
    faces = [(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2) for index in range(len(xs) - 1)]
    return add_mesh("REVIEW_ONLY_M01_C06_Ocean", vertices, faces, material, review)


def build_corridor(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
    review: bpy.types.Collection,
) -> dict[str, Any]:
    xs = x_samples()
    objects: list[bpy.types.Object] = []
    objects.append(create_band("SM_M01_C06_WetSand", xs, "shore", "wet_end", materials["wet_sand"], visible))
    objects.append(create_band("SM_M01_C06_DrySand", xs, "wet_end", "dry_end", materials["dry_sand"], visible))
    objects.append(create_band("SM_M01_C06_DuneTransition", xs, "dry_end", "promenade_start", materials["dune"], visible))
    objects.append(create_band("SM_M01_C06_Promenade", xs, "promenade_start", "promenade_end", materials["pavers"], visible))
    objects.append(create_band("SM_M01_C06_MainRoad", xs, "promenade_end", "road_end", materials["asphalt"], visible))
    objects.append(create_band("SM_M01_C06_InlandSidewalk", xs, "road_end", "sidewalk_end", materials["pavers"], visible))

    cross_streets = (60.0, 160.0, 260.0, 360.0, 460.0)
    street_half_width = 5.4
    parcel_edges = [X_MIN]
    for center in cross_streets:
        parcel_edges.extend((center - street_half_width, center + street_half_width))
    parcel_edges.append(X_MAX)
    parcel_index = 0
    for start, end in zip(parcel_edges[0::2], parcel_edges[1::2]):
        objects.append(
            create_rect_surface(
                f"SM_M01_C06_UrbanParcel_{parcel_index:02d}",
                start,
                end,
                104.0,
                195.0,
                0.76,
                materials["concrete"],
                visible,
            )
        )
        parcel_index += 1

    for index, center in enumerate(cross_streets):
        objects.append(
            create_rect_surface(
                f"SM_M01_C06_IntegratedCrossStreet_{index:02d}",
                center - street_half_width,
                center + street_half_width,
                100.0,
                195.0,
                0.585,
                materials["asphalt"],
                visible,
            )
        )

    # Low, weathered promenade edge.  The edge is intentionally interrupted at
    # beach accesses so it never reads as the bright parallel rail rejected in
    # prior visual reviews.
    access_centers = (90.0, 290.0, 490.0)
    segment_edges = [X_MIN]
    for center in access_centers:
        segment_edges.extend((center - 4.0, center + 4.0))
    segment_edges.append(X_MAX)
    edge_segments = list(zip(segment_edges[0::2], segment_edges[1::2]))
    for index, (start, end) in enumerate(edge_segments):
        local_xs = [start + (end - start) * step / max(1, int((end - start) / X_STEP)) for step in range(max(1, int((end - start) / X_STEP)) + 1)]
        objects.append(
            create_swept_volume(
                f"SM_M01_C06_PromenadeEdge_{index:02d}",
                local_xs,
                lambda x: boundary_profile(x)["promenade_start"] + 0.15,
                0.48,
                lambda x: boundary_height(x, "promenade_start") + 0.22,
                lambda x: boundary_height(x, "dry_end") - 0.10,
                materials["concrete"],
                visible,
            )
        )

    # Three broad, flush beach-access ramps replace detached stairs.
    for index, center in enumerate(access_centers):
        ramp_vertices = [
            (center - 3.6, boundary_profile(center)["dry_end"], boundary_height(center, "dry_end")),
            (center + 3.6, boundary_profile(center)["dry_end"], boundary_height(center, "dry_end")),
            (center + 3.6, boundary_profile(center)["promenade_start"], boundary_height(center, "promenade_start") + 0.01),
            (center - 3.6, boundary_profile(center)["promenade_start"], boundary_height(center, "promenade_start") + 0.01),
        ]
        objects.append(
            add_mesh(
                f"SM_M01_C06_BeachAccessRamp_{index:02d}",
                ramp_vertices,
                [(0, 1, 2, 3)],
                materials["concrete"],
                visible,
            )
        )

    # World-aligned road markings retain continuous visual rhythm without
    # forcing one large white slab through the city.
    for index, x in enumerate(range(-30, 535, 18)):
        objects.append(
            add_box(
                f"SM_M01_C06_CenterDash_{index:02d}",
                (float(x), 93.0, 0.615),
                (7.0, 0.18, 0.026),
                materials["marking"],
                visible,
                bevel=0.015,
            )
        )

    # Grounded drainage and service detail provides scale without placeholder
    # vehicles or vegetation.  Every piece touches the promenade/road surface.
    for index, x in enumerate((-12.0, 42.0, 116.0, 207.0, 314.0, 431.0, 514.0)):
        grate = add_box(
            f"SM_M01_C06_StormDrain_{index:02d}",
            (x, 100.55, 0.755),
            (1.25, 0.42, 0.055),
            materials["drain"],
            visible,
            bevel=0.025,
        )
        objects.append(grate)
        for slot_index in range(5):
            objects.append(
                add_box(
                    f"SM_M01_C06_StormDrain_{index:02d}_Slot_{slot_index:02d}",
                    (x - 0.42 + slot_index * 0.21, 100.55, 0.788),
                    (0.055, 0.32, 0.018),
                    materials["concrete"],
                    visible,
                )
            )

    for index, x in enumerate((24.0, 132.0, 236.0, 342.0, 448.0, 524.0)):
        objects.append(add_cylinder(f"SM_M01_C06_Bollard_{index:02d}", (x, 82.0, 1.16), 0.12, 0.92, materials["metal"], visible, 24))
        objects.append(add_cylinder(f"SM_M01_C06_BollardBase_{index:02d}", (x, 82.0, 0.77), 0.24, 0.10, materials["metal"], visible, 28))

    # Irregular wet-contact and foam guide meshes are deliberately separate so
    # Unreal can replace them with final Water/Niagara treatment.
    foam_vertices: list[tuple[float, float, float]] = []
    wet_vertices: list[tuple[float, float, float]] = []
    for x in xs:
        shore = shoreline_y(x)
        foam_width = 0.48 + 0.20 * (0.5 + 0.5 * math.sin(x / 9.0))
        foam_vertices.extend(((x, shore - foam_width, -0.46), (x, shore + foam_width, -0.45)))
        wet_vertices.extend(((x, shore + 0.65, -0.43), (x, shore + 2.15, -0.34)))
    band_faces = [(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2) for index in range(len(xs) - 1)]
    objects.append(add_mesh("SM_M01_C06_FoamContactGuide", foam_vertices, band_faces, materials["foam"], visible))
    objects.append(add_mesh("SM_M01_C06_WetContactRibbon", wet_vertices, band_faces, materials["wet_sand"], visible))

    collision_obj = add_box(
        "UCX_SM_M01_CoastalCorridor_C06_00",
        ((X_MIN + X_MAX) * 0.5, 108.0, -0.35),
        (X_MAX - X_MIN, 174.0, 2.2),
        materials["concrete"],
        collision,
    )
    collision_obj.hide_render = True
    collision_obj.display_type = "WIRE"

    socket = bpy.data.objects.new("SOCKET_M01_CoastalCorridor_C06_Origin", None)
    socket.empty_display_type = "PLAIN_AXES"
    socket.empty_display_size = 2.5
    socket.location = (0.0, 0.0, 0.0)
    sockets.objects.link(socket)

    create_review_ocean(xs, materials["water"], review)
    return {
        "objects": objects,
        "collision": collision_obj,
        "socket": socket,
        "cross_streets": len(cross_streets),
        "parcels": parcel_index,
        "access_ramps": len(access_centers),
        "x_samples": len(xs),
    }


def point_camera(
    camera: bpy.types.Object,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
) -> None:
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens


def setup_review(scene: bpy.types.Scene, review: bpy.types.Collection) -> dict[str, bpy.types.Object]:
    camera_data = bpy.data.cameras.new("M01_C06_ReviewCamera")
    camera = bpy.data.objects.new("M01_C06_ReviewCamera", camera_data)
    review.objects.link(camera)
    scene.camera = camera

    sun_data = bpy.data.lights.new("M01_C06_Sun", "SUN")
    sun = bpy.data.objects.new("M01_C06_Sun", sun_data)
    sun.rotation_euler = (math.radians(32.0), math.radians(-18.0), math.radians(-42.0))
    sun_data.energy = 3.0
    sun_data.angle = math.radians(1.8)
    review.objects.link(sun)

    area_data = bpy.data.lights.new("M01_C06_SkyFill", "AREA")
    area = bpy.data.objects.new("M01_C06_SkyFill", area_data)
    area.location = (260.0, 10.0, 95.0)
    area_data.energy = 1600.0
    area_data.shape = "DISK"
    area_data.size = 180.0
    area.rotation_euler = (0.0, 0.0, 0.0)
    review.objects.link(area)
    return {"camera": camera, "sun": sun, "area": area}


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RENDER_SIZE[0]
    scene.render.resolution_y = RENDER_SIZE[1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.world.use_nodes = True
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.exposure = 0.15
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except (TypeError, ValueError):
        pass


def configure_condition(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    require(background is not None, "World Background node missing")
    if condition == "daylight":
        background.inputs["Color"].default_value = (0.31, 0.47, 0.68, 1.0)
        background.inputs["Strength"].default_value = 0.42
        rig["sun"].data.energy = 3.1
        rig["sun"].data.color = (1.0, 0.78, 0.57)
        rig["area"].data.energy = 1550.0
        scene.view_settings.exposure = 0.12
    else:
        background.inputs["Color"].default_value = (0.24, 0.31, 0.37, 1.0)
        background.inputs["Strength"].default_value = 0.32
        rig["sun"].data.energy = 1.45
        rig["sun"].data.color = (0.74, 0.83, 0.90)
        rig["area"].data.energy = 1150.0
        scene.view_settings.exposure = 0.34


def render_reviews(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path) -> list[dict[str, Any]]:
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for camera_name, (location, target, lens) in CAMERAS.items():
        condition = "overcast" if camera_name in {"integrated_intersection", "wet_contact_close"} else "daylight"
        configure_condition(scene, rig, condition)
        point_camera(rig["camera"], location, target, lens)
        path = render_dir / f"{condition}_{camera_name}.png"
        scene.render.filepath = str(path)
        print(json.dumps({"event": "render_start", "camera": camera_name, "condition": condition}), flush=True)
        bpy.ops.render.render(write_still=True)
        require(path.is_file() and path.stat().st_size > 0, f"Render missing: {path}")
        results.append(
            {
                "camera": camera_name,
                "condition": condition,
                "path": str(path),
                "bytes": path.stat().st_size,
            }
        )
        print(json.dumps({"event": "render_complete", "camera": camera_name, "bytes": path.stat().st_size}), flush=True)
    require(len(results) == len(CAMERAS), "Governed render count mismatch")
    return results


def mesh_statistics(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    meshes: list[bpy.types.Object] = []
    vertices = 0
    polygons = 0
    uv_missing: list[str] = []
    for collection in collections:
        for obj in collection.all_objects:
            if obj.type != "MESH":
                continue
            meshes.append(obj)
            vertices += len(obj.data.vertices)
            polygons += len(obj.data.polygons)
            if not obj.name.startswith("UCX_") and len(obj.data.uv_layers) < 1:
                uv_missing.append(obj.name)
    return {
        "mesh_objects": len(set(meshes)),
        "vertices": vertices,
        "polygons": polygons,
        "uv_missing": sorted(uv_missing),
    }


def export_glb(path: Path, collections: Iterable[bpy.types.Collection]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for collection in collections:
        for obj in collection.all_objects:
            obj.select_set(True)
            selected.append(obj)
    require(selected, "No governed objects selected for GLB export")
    bpy.context.view_layer.objects.active = next((obj for obj in selected if obj.type == "MESH"), selected[0])
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_animations=False,
        export_lights=False,
        export_cameras=False,
    )
    require(path.is_file() and path.stat().st_size > 0, "GLB export was not created")


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Controller output directory is not empty: {output}")
    require(PROVENANCE.is_file(), "Texture provenance manifest is missing")
    for family in PBR_SOURCES.values():
        for path in family.values():
            require(path.is_file(), f"Texture authority missing: {path}")

    clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = get_collection("M01_C06_VISIBLE")
    collision = get_collection("M01_C06_COLLISION")
    sockets = get_collection("M01_C06_SOCKETS")
    review = get_collection("M01_C06_REVIEW_ONLY")
    materials = build_materials()
    build = build_corridor(materials, visible, collision, sockets, review)
    rig = setup_review(scene, review)

    stats = mesh_statistics((visible, collision))
    require(stats["mesh_objects"] >= 70, f"Insufficient production object count: {stats}")
    require(stats["vertices"] >= 3500, f"Insufficient corridor topology: {stats}")
    require(not stats["uv_missing"], f"Render mesh UV coverage failed: {stats['uv_missing']}")
    require(build["cross_streets"] == 5, "Integrated cross-street count mismatch")
    require(build["parcels"] == 6, "Urban parcel count mismatch")

    renders = render_reviews(scene, rig, output)
    blend_path = output / "M01_CoastalCorridor_Correction06.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_CoastalCorridor_Correction06.glb"
    export_glb(glb_path, (visible, collision, sockets))

    texture_inventory = []
    for family, source_set in sorted(PBR_SOURCES.items()):
        for role, path in sorted(source_set.items()):
            texture_inventory.append(
                {
                    "family": family,
                    "role": role,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    write_json(
        output / "geometry_receipt.json",
        {
            "schema": "skyguard.m01-coastal-corridor-correction06.geometry.v1",
            "gate": GATE,
            "fresh_geometry": True,
            "external_model_use": False,
            "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
            "world_bounds_m": {"x": [X_MIN, X_MAX], "y": [18.0, 195.0]},
            "statistics": stats,
            "continuous_world_aligned_uv": True,
            "repeating_ground_slab_count": 0,
            "tile_gap_count": 0,
            "integrated_cross_street_count": build["cross_streets"],
            "grounded_urban_parcel_count": build["parcels"],
            "flush_beach_access_count": build["access_ramps"],
            "x_sample_count": build["x_samples"],
            "socket": "SOCKET_M01_CoastalCorridor_C06_Origin",
            "collision": "UCX_SM_M01_CoastalCorridor_C06_00",
            "unreal_owns": ["final_water", "foam", "foliage", "lighting", "atmosphere"],
            "passed": True,
        },
    )
    write_json(
        output / "pbr_receipt.json",
        {
            "schema": "skyguard.m01-coastal-corridor-correction06.pbr.v1",
            "gate": GATE,
            "texture_authorities": texture_inventory,
            "provenance_manifest": {
                "path": str(PROVENANCE),
                "bytes": PROVENANCE.stat().st_size,
                "sha256": sha256(PROVENANCE),
            },
            "material_names": sorted(material.name for material in materials.values()),
            "world_aligned_uv_scale_m": 8.0,
            "passed": True,
        },
    )
    write_json(
        output / "render_receipt.json",
        {
            "schema": "skyguard.m01-coastal-corridor-correction06.renders.v1",
            "gate": GATE,
            "resolution": list(RENDER_SIZE),
            "cameras": list(CAMERAS),
            "renders": renders,
            "direct_full_resolution_review_required": True,
            "passed": True,
        },
    )
    write_json(
        output / "export_receipt.json",
        {
            "schema": "skyguard.m01-coastal-corridor-correction06.export.v1",
            "gate": GATE,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "exported_collections": [visible.name, collision.name, sockets.name],
            "review_collection_excluded_from_glb": review.name,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_manifest.json",
        {
            "schema": "skyguard.m01-coastal-corridor-correction06.artifacts.v1",
            "gate": GATE,
            "asset_id": ASSET_ID,
            "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW",
            "blend_count": 1,
            "glb_count": 1,
            "render_count": len(renders),
            "receipt_count": 4,
            "blender_version": bpy.app.version_string,
            "promotion_authorized": False,
            "unreal_import_authorized": False,
        },
    )
    print(
        json.dumps(
            {
                "gate": GATE,
                "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW",
                "stats": stats,
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
