"""Build the source-bound Mission 01 grouped-topology corrective package.

Build 008 preserves the eighteen maps accepted by Build 007 and rebakes only
the six maps rejected by direct original-resolution review.  Corrective maps
use deterministic component-exploded bake copies so disconnected or nested
components cannot cross-project.  Production-low geometry is never exploded.

All reused inputs are hash-bound to the immutable Build 007 manifest and
review receipt.  Artifact checks remain candidate-only; every replacement map
still requires direct original-resolution review before mapped-mesh or Unreal
promotion.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
DEFAULT_CONTRACT = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_HERO_GROUPED_TOPOLOGY_BAKE_008_CONTRACT.json"
)


def contract_path_from_argv() -> Path:
    if "--" not in sys.argv:
        return DEFAULT_CONTRACT
    values = sys.argv[sys.argv.index("--") + 1 :]
    for index, value in enumerate(values):
        if value == "--contract" and index + 1 < len(values):
            return Path(values[index + 1]).resolve()
    return DEFAULT_CONTRACT


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_evidence(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def resolve(raw: str) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else ROOT / candidate


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_effective_contract(path: Path) -> tuple[dict[str, Any], Path | None]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    base_raw = raw.get("extends_contract")
    if not isinstance(base_raw, str) or not base_raw:
        return raw, None
    base_path = resolve(base_raw)
    expected_hash = raw.get("extends_contract_sha256")
    if (
        not isinstance(expected_hash, str)
        or sha256(base_path) != expected_hash
    ):
        raise RuntimeError("Extended grouped-topology contract hash mismatch")
    base = json.loads(base_path.read_text(encoding="utf-8-sig"))
    return deep_merge(base, raw), base_path


def select_only(objects, active=None) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active or objects[-1]


def duplicate_mesh(source, name: str, collection):
    obj = source.copy()
    obj.data = source.data.copy()
    obj.animation_data_clear()
    obj.name = name
    obj.data.name = name + "_Mesh"
    collection.objects.link(obj)
    obj.matrix_world = source.matrix_world.copy()
    return obj


def material_name_for_face(obj, material_index: int) -> str | None:
    if material_index < 0 or material_index >= len(obj.data.materials):
        return None
    material = obj.data.materials[material_index]
    return material.name if material is not None else None


def source_material_face_counts(obj) -> dict[str, int]:
    counts: dict[str, int] = {}
    for polygon in obj.data.polygons:
        name = material_name_for_face(obj, polygon.material_index)
        if name is None:
            name = "<UNBOUND>"
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items()))


def extract_material_group(source, name: str, materials: set[str], collection):
    obj = duplicate_mesh(source, name, collection)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    rejected = [
        face
        for face in bm.faces
        if material_name_for_face(obj, face.material_index) not in materials
    ]
    if rejected:
        bmesh.ops.delete(bm, geom=rejected, context="FACES")
    orphan_edges = [edge for edge in bm.edges if not edge.link_faces]
    if orphan_edges:
        bmesh.ops.delete(bm, geom=orphan_edges, context="EDGES")
    orphan_vertices = [vertex for vertex in bm.verts if not vertex.link_faces]
    if orphan_vertices:
        bmesh.ops.delete(bm, geom=orphan_vertices, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(clean_customdata=True)
    obj.data.update()
    return obj


def connected_component_count(obj) -> int:
    adjacency: dict[int, set[int]] = {
        vertex.index: set() for vertex in obj.data.vertices
    }
    for edge in obj.data.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(adjacency)
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            current = stack.pop()
            neighbors = adjacency[current] & remaining
            remaining.difference_update(neighbors)
            stack.extend(neighbors)
    return components


def topology_defect_counts(obj) -> dict[str, int | float]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    diagonal = max(float(obj.dimensions.length), 1.0e-6)
    area_epsilon = max(diagonal * diagonal * 1.0e-12, 1.0e-14)
    result = {
        "zero_area_faces": sum(
            face.calc_area() <= area_epsilon for face in bm.faces
        ),
        "boundary_edges": sum(len(edge.link_faces) == 1 for edge in bm.edges),
        "nonmanifold_edges": sum(
            len(edge.link_faces) > 2 for edge in bm.edges
        ),
        "area_epsilon": area_epsilon,
    }
    bm.free()
    return result


def repair_partition_topology(obj, policy: dict[str, Any]) -> dict[str, Any]:
    """Apply only contract-declared, deterministic topology repairs."""
    before = topology_defect_counts(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    removed_zero_area_faces = 0
    split_nonmanifold_edges = 0
    if policy.get("remove_zero_area_faces") is True:
        degenerate = [
            face
            for face in bm.faces
            if face.calc_area() <= float(before["area_epsilon"])
        ]
        removed_zero_area_faces = len(degenerate)
        if degenerate:
            bmesh.ops.delete(bm, geom=degenerate, context="FACES")
    orphan_edges = [edge for edge in bm.edges if not edge.link_faces]
    if orphan_edges:
        bmesh.ops.delete(bm, geom=orphan_edges, context="EDGES")
    orphan_vertices = [vertex for vertex in bm.verts if not vertex.link_faces]
    if orphan_vertices:
        bmesh.ops.delete(bm, geom=orphan_vertices, context="VERTS")
    if policy.get("split_nonmanifold_edges") is True:
        nonmanifold = [
            edge for edge in bm.edges if len(edge.link_faces) > 2
        ]
        split_nonmanifold_edges = len(nonmanifold)
        if nonmanifold:
            bmesh.ops.split_edges(bm, edges=nonmanifold)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(clean_customdata=True)
    obj.data.update()
    after = topology_defect_counts(obj)
    return {
        "policy": policy,
        "before": before,
        "after": after,
        "removed_zero_area_faces": removed_zero_area_faces,
        "split_nonmanifold_edges": split_nonmanifold_edges,
    }


def author_consistent_face_normals(obj) -> dict[str, Any]:
    """Recalculate each connected component before AO and cage generation.

    The Wave 1 source contains several disconnected closed shells.  Retaining
    their inherited winding after a material partition can leave a whole UV
    island facing inward; Cycles then bakes that island as fully occluded.
    Recalculating the partitioned mesh makes the winding component-consistent
    before smoothing, high-source construction, or cage offsets are authored.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    faces = list(bm.faces)
    before = [face.normal.copy() for face in faces]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    flipped_faces = sum(
        1
        for previous, face in zip(before, faces)
        if previous.length_squared > 1.0e-12
        and face.normal.length_squared > 1.0e-12
        and previous.dot(face.normal) < 0.0
    )
    zero_normal_faces = sum(
        1 for face in faces if face.normal.length_squared <= 1.0e-12
    )
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return {
        "method": "bmesh_recalc_face_normals_per_partition",
        "faces": len(obj.data.polygons),
        "flipped_faces": flipped_faces,
        "zero_normal_faces": zero_normal_faces,
        "component_consistent": zero_normal_faces == 0,
    }


def author_smoothing(obj, hard_angle_degrees: float) -> dict[str, Any]:
    threshold = math.radians(hard_angle_degrees)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    sharp_count = 0
    for face in bm.faces:
        face.smooth = True
    for edge in bm.edges:
        boundary = len(edge.link_faces) != 2
        angle = (
            edge.calc_face_angle(0.0)
            if len(edge.link_faces) == 2
            else math.pi
        )
        sharp = boundary or angle >= threshold
        edge.smooth = not sharp
        if sharp:
            sharp_count += 1
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return {
        "polygon_smoothing": True,
        "hard_edge_angle_degrees": hard_angle_degrees,
        "sharp_edges": sharp_count,
        "smooth_polygons": sum(
            1 for polygon in obj.data.polygons if polygon.use_smooth
        ),
        "polygon_count": len(obj.data.polygons),
    }


def author_group_uv(
    obj,
    uv_layer_name: str,
    island_margin: float,
) -> dict[str, Any]:
    source_layer = (
        obj.data.uv_layers.get("UV_M01_AAA_0")
        or obj.data.uv_layers.active
    )
    if source_layer is None:
        raise RuntimeError(f"{obj.name}: no source UV chart seed")
    source_layer_name = source_layer.name
    for layer_item in list(obj.data.uv_layers):
        if layer_item != source_layer:
            obj.data.uv_layers.remove(layer_item)
    source_layer.name = uv_layer_name
    layer = source_layer
    obj.data.uv_layers.active = layer
    # Blender 5.2 expects the MeshUVLoopLayer datablock, not a boolean.
    obj.data.uv_layers.active_render = layer

    select_only([obj], obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(
        rotate=True,
        scale=True,
        merge_overlap=False,
        margin=island_margin,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    authored_seam_edges = mark_uv_chart_seams(obj, uv_layer_name)

    layer = obj.data.uv_layers[uv_layer_name]
    coordinates = [loop.uv.copy() for loop in layer.data]
    finite = all(
        math.isfinite(float(uv.x)) and math.isfinite(float(uv.y))
        for uv in coordinates
    )
    minimum = [
        min(float(uv[index]) for uv in coordinates)
        for index in (0, 1)
    ]
    maximum = [
        max(float(uv[index]) for uv in coordinates)
        for index in (0, 1)
    ]
    return {
        "layer": uv_layer_name,
        "method": (
            "semantic_group_connected_source_charts_repacked_and_seams_authored"
        ),
        "source_chart_seed_layer": source_layer_name,
        "smart_project_used": False,
        "authored_seam_edges": authored_seam_edges,
        "expected_islands": None,
        "finite": finite,
        "bounds_min": [round(value, 8) for value in minimum],
        "bounds_max": [round(value, 8) for value in maximum],
        "average_island_scale": True,
        "packed": True,
        "margin_fraction": island_margin,
    }


def mark_uv_chart_seams(obj, uv_layer_name: str) -> int:
    layer = obj.data.uv_layers[uv_layer_name]
    edge_samples: dict[
        tuple[int, int],
        list[dict[int, tuple[float, float]]],
    ] = {}
    for polygon in obj.data.polygons:
        loops = list(polygon.loop_indices)
        for index, loop_index in enumerate(loops):
            next_loop_index = loops[(index + 1) % len(loops)]
            loop = obj.data.loops[loop_index]
            next_loop = obj.data.loops[next_loop_index]
            key = tuple(sorted((loop.vertex_index, next_loop.vertex_index)))
            edge_samples.setdefault(key, []).append(
                {
                    loop.vertex_index: tuple(layer.data[loop_index].uv),
                    next_loop.vertex_index: tuple(
                        layer.data[next_loop_index].uv
                    ),
                }
            )
    edge_lookup = {
        tuple(sorted(edge.vertices)): edge for edge in obj.data.edges
    }
    seam_count = 0
    tolerance = 1.0e-5
    for key, samples in edge_samples.items():
        seam = len(samples) != 2
        if len(samples) == 2:
            for vertex_index in key:
                first = samples[0].get(vertex_index)
                second = samples[1].get(vertex_index)
                if (
                    first is None
                    or second is None
                    or abs(first[0] - second[0]) > tolerance
                    or abs(first[1] - second[1]) > tolerance
                ):
                    seam = True
                    break
        edge = edge_lookup.get(key)
        if edge is not None:
            edge.use_seam = seam
        if seam:
            seam_count += 1
    obj.data.update()
    return seam_count


def apply_high_bevel(obj, width: float) -> None:
    modifier = obj.modifiers.new("GROUPED003_HighSourceBevel", "BEVEL")
    modifier.width = width
    modifier.segments = 3
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(20.0)
    modifier.harden_normals = True
    modifier.affect = "EDGES"
    select_only([obj], obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def ensure_high_density(obj, low_vertex_count: int) -> str:
    if len(obj.data.vertices) > low_vertex_count:
        return "three_segment_angle_bevel"
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(
        bm,
        edges=list(bm.edges),
        cuts=1,
        use_grid_fill=True,
    )
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return "three_segment_angle_bevel_plus_linear_edge_subdivision"


def make_normal_offset_cage(low, name: str, extrusion: float, collection):
    cage = duplicate_mesh(low, name, collection)
    cage.data.update()
    normals = [vertex.normal.copy() for vertex in cage.data.vertices]
    zero_normals = 0
    for vertex, normal in zip(cage.data.vertices, normals):
        if normal.length_squared <= 1.0e-12:
            zero_normals += 1
            continue
        vertex.co += normal.normalized() * extrusion
    cage.data.update()
    cage.display_type = "WIRE"
    cage.hide_render = True
    cage["SKG_BakeRole"] = "group_projection_cage"
    cage["SKG_CageMethod"] = "vertex_normal_offset"
    cage["SKG_CageExtrusionM"] = extrusion
    return cage, zero_normals


def mesh_stats(obj) -> dict[str, Any]:
    triangles = sum(
        max(0, len(polygon.vertices) - 2)
        for polygon in obj.data.polygons
    )
    material_counts = source_material_face_counts(obj)
    vertices_used_by_edges = {
        vertex_index
        for edge in obj.data.edges
        for vertex_index in edge.vertices
    }
    return {
        "object": obj.name,
        "mesh_datablock": obj.data.name,
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "faces": len(obj.data.polygons),
        "triangles": triangles,
        "components": connected_component_count(obj),
        "dimensions_m": [
            round(float(value), 7) for value in obj.dimensions
        ],
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
        "material_face_counts": material_counts,
        "orphan_vertices": sum(
            1
            for vertex in obj.data.vertices
            if vertex.index not in vertices_used_by_edges
        ),
    }


def new_image(name: str, resolution: int, map_spec: dict[str, Any]):
    image = bpy.data.images.new(
        name=name,
        width=resolution,
        height=resolution,
        alpha=False,
        float_buffer=False,
    )
    background = map_spec["neutral_background"]
    image.generated_color = (*background, 1.0)
    image.colorspace_settings.name = map_spec["color_space"]
    return image


def attach_bake_image(low, image, tag: str):
    nodes = []
    for index, slot in enumerate(low.material_slots):
        material = slot.material
        if material is None:
            continue
        material.use_nodes = True
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.name = f"SKG_GROUPED003_BAKE_{tag}_{index}"
        node.label = node.name
        node.image = image
        material.node_tree.nodes.active = node
        node.select = True
        nodes.append((material, node))
    return nodes


def remove_bake_nodes(nodes) -> None:
    for material, node in nodes:
        material.node_tree.nodes.remove(node)


def isolate_render_meshes(visible_objects) -> None:
    visible = {obj.name for obj in visible_objects}
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in visible


def connected_component_vertex_sets(obj) -> list[list[int]]:
    """Return deterministic connected vertex sets for an object's mesh."""
    adjacency: dict[int, set[int]] = {
        vertex.index: set() for vertex in obj.data.vertices
    }
    for edge in obj.data.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(adjacency)
    components: list[list[int]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        stack = [seed]
        component = [seed]
        while stack:
            current = stack.pop()
            neighbors = sorted(adjacency[current] & remaining)
            remaining.difference_update(neighbors)
            stack.extend(neighbors)
            component.extend(neighbors)
        components.append(sorted(component))
    return components


def component_descriptors(obj) -> list[dict[str, Any]]:
    descriptors: list[dict[str, Any]] = []
    for vertices in connected_component_vertex_sets(obj):
        coordinates = [obj.data.vertices[index].co.copy() for index in vertices]
        minimum = Vector(
            tuple(min(value[axis] for value in coordinates) for axis in range(3))
        )
        maximum = Vector(
            tuple(max(value[axis] for value in coordinates) for axis in range(3))
        )
        center = sum(coordinates, Vector()) / len(coordinates)
        descriptors.append(
            {
                "vertices": vertices,
                "center": center,
                "dimensions": maximum - minimum,
            }
        )
    return descriptors


def match_components(
    reference: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
) -> list[int]:
    """Match candidate components to reference components by center and size."""
    if len(reference) != len(candidate):
        raise RuntimeError(
            "Corrective component isolation requires matching component counts"
        )
    reference_scale = max(
        (
            item["dimensions"].length
            for item in reference
        ),
        default=1.0,
    )
    reference_scale = max(reference_scale, 1.0e-6)
    unused = set(range(len(reference)))
    mapping: list[int] = []
    for item in candidate:
        match = min(
            unused,
            key=lambda index: (
                (item["center"] - reference[index]["center"]).length
                / reference_scale
                + (
                    item["dimensions"] - reference[index]["dimensions"]
                ).length
                / reference_scale
            ),
        )
        unused.remove(match)
        mapping.append(match)
    return mapping


def component_explosion_offsets(
    descriptors: list[dict[str, Any]],
    spacing_multiplier: float,
) -> list[Vector]:
    count = len(descriptors)
    if count <= 1:
        return [Vector()]
    largest_diagonal = max(
        item["dimensions"].length for item in descriptors
    )
    spacing = max(largest_diagonal * spacing_multiplier, 1.0)
    columns = math.ceil(math.sqrt(count))
    rows = math.ceil(count / columns)
    center_x = (columns - 1) * 0.5
    center_y = (rows - 1) * 0.5
    return [
        Vector(
            (
                ((index % columns) - center_x) * spacing,
                ((index // columns) - center_y) * spacing,
                0.0,
            )
        )
        for index in range(count)
    ]


def apply_component_explosion(
    obj,
    reference_descriptors: list[dict[str, Any]],
    offsets: list[Vector],
) -> None:
    descriptors = component_descriptors(obj)
    mapping = match_components(reference_descriptors, descriptors)
    for descriptor, reference_index in zip(descriptors, mapping):
        offset = offsets[reference_index]
        for vertex_index in descriptor["vertices"]:
            obj.data.vertices[vertex_index].co += offset
    obj.data.update()


def make_component_exploded_bake_set(
    high,
    low,
    cage,
    ao_occluder,
    scratch_collection,
    spacing_multiplier: float,
) -> dict[str, Any]:
    """Create translated bake-only copies while preserving production meshes."""
    exploded = {
        "high": duplicate_mesh(
            high,
            high.name + "_COMPONENT_BAKE",
            scratch_collection,
        ),
        "low": duplicate_mesh(
            low,
            low.name + "_COMPONENT_BAKE",
            scratch_collection,
        ),
        "cage": duplicate_mesh(
            cage,
            cage.name + "_COMPONENT_BAKE",
            scratch_collection,
        ),
        "ao_occluder": (
            duplicate_mesh(
                ao_occluder,
                ao_occluder.name + "_COMPONENT_BAKE",
                scratch_collection,
            )
            if ao_occluder is not None
            else None
        ),
    }
    reference = component_descriptors(exploded["low"])
    offsets = component_explosion_offsets(reference, spacing_multiplier)
    for key in ("low", "high", "cage", "ao_occluder"):
        item = exploded[key]
        if item is not None:
            apply_component_explosion(item, reference, offsets)
    exploded["component_count"] = len(reference)
    exploded["spacing_multiplier"] = spacing_multiplier
    return exploded


def remove_bake_objects(objects: list[Any]) -> None:
    for obj in objects:
        if obj is None:
            continue
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def bake_group_map(
    high,
    low,
    cage,
    ao_occluder,
    image,
    map_type: str,
    group_spec: dict[str, Any],
    ao_policy: str,
    projection_policy: str,
    scratch_collection,
    component_spacing_multiplier: float,
) -> dict[str, Any]:
    bake = bpy.context.scene.render.bake
    exploded = None
    bake_high = high
    bake_low = low
    bake_cage = cage
    bake_ao_occluder = ao_occluder
    if projection_policy.startswith("component_exploded_"):
        exploded = make_component_exploded_bake_set(
            high,
            low,
            cage,
            ao_occluder,
            scratch_collection,
            component_spacing_multiplier,
        )
        bake_high = exploded["high"]
        bake_low = exploded["low"]
        bake_cage = exploded["cage"]
        bake_ao_occluder = exploded["ao_occluder"]
    nodes = attach_bake_image(bake_low, image, map_type)
    try:
        if map_type == "AO":
            if ao_policy == "direct_low_self_occlusion":
                bake.use_selected_to_active = False
                bake.use_cage = False
                bake.cage_extrusion = 0.0
                bake.max_ray_distance = 0.0
                isolate_render_meshes([bake_low])
                select_only([bake_low], bake_low)
            else:
                bake.use_selected_to_active = True
                bake.use_cage = True
                bake.cage_object = bake_cage
                bake.cage_extrusion = float(group_spec["cage_extrusion_m"])
                bake.max_ray_distance = float(group_spec["max_ray_distance_m"])
                isolate_render_meshes(
                    [bake_ao_occluder, bake_low, bake_cage]
                )
                select_only(
                    [bake_ao_occluder, bake_low],
                    bake_low,
                )
        else:
            bake.use_selected_to_active = True
            bake.use_cage = True
            bake.cage_object = bake_cage
            bake.cage_extrusion = float(group_spec["cage_extrusion_m"])
            bake.max_ray_distance = float(group_spec["max_ray_distance_m"])
            isolate_render_meshes([bake_high, bake_low, bake_cage])
            select_only([bake_high, bake_low], bake_low)
        bpy.ops.object.bake(type=map_type.upper())
    finally:
        remove_bake_nodes(nodes)
        if exploded is not None:
            remove_bake_objects(
                [
                    exploded["high"],
                    exploded["low"],
                    exploded["cage"],
                    exploded["ao_occluder"],
                ]
            )
    return {
        "policy": projection_policy,
        "component_isolated": exploded is not None,
        "component_count": (
            exploded["component_count"] if exploded is not None else None
        ),
        "component_spacing_multiplier": (
            exploded["spacing_multiplier"] if exploded is not None else None
        ),
        "production_geometry_translated": False,
    }


def channel_stats_and_diagnostics(
    image,
    map_type: str,
    neutral_background: list[float],
) -> dict[str, Any]:
    pixels = list(image.pixels[:])
    channel_min = [1.0, 1.0, 1.0, 1.0]
    channel_max = [0.0, 0.0, 0.0, 0.0]
    neutral_pixels = 0
    black_pixels = 0
    total_pixels = len(pixels) // 4
    sample_unit_errors: list[float] = []
    sample_stride = max(1, total_pixels // 32768)
    for pixel_index in range(total_pixels):
        base = pixel_index * 4
        rgb = pixels[base : base + 3]
        for channel in range(4):
            value = pixels[base + channel]
            channel_min[channel] = min(channel_min[channel], value)
            channel_max[channel] = max(channel_max[channel], value)
        if all(
            abs(rgb[channel] - neutral_background[channel]) <= 1.0 / 255.0
            for channel in range(3)
        ):
            neutral_pixels += 1
        if max(rgb) <= 1.0 / 255.0:
            black_pixels += 1
        if map_type == "Normal" and pixel_index % sample_stride == 0:
            vector = [2.0 * value - 1.0 for value in rgb]
            length = math.sqrt(sum(value * value for value in vector))
            sample_unit_errors.append(abs(length - 1.0))
    ranges = [
        channel_max[index] - channel_min[index] for index in range(4)
    ]
    result: dict[str, Any] = {
        "min": [round(value, 7) for value in channel_min],
        "max": [round(value, 7) for value in channel_max],
        "range": [round(value, 7) for value in ranges],
        "neutral_background_fraction": round(
            neutral_pixels / max(1, total_pixels), 8
        ),
        "black_pixel_fraction": round(
            black_pixels / max(1, total_pixels), 8
        ),
    }
    if sample_unit_errors:
        result["sampled_normal_unit_error_mean"] = round(
            sum(sample_unit_errors) / len(sample_unit_errors),
            7,
        )
        result["sampled_normal_unit_error_max"] = round(
            max(sample_unit_errors),
            7,
        )
    return result


def save_png(image, path: Path) -> None:
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    image.file_format = "PNG"
    image.filepath_raw = str(path)
    image.save()


def export_low_glb(low_objects, path: Path) -> None:
    select_only(low_objects, low_objects[0])
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
    )


def validate_source_partition(
    asset_spec: dict[str, Any],
    source,
) -> list[str]:
    failures: list[str] = []
    actual_counts = source_material_face_counts(source)
    actual_materials = set(actual_counts)
    required_materials = set(asset_spec["required_source_materials"])
    memberships = [
        material
        for group in asset_spec["groups"]
        for material in group["materials"]
    ]
    if actual_materials != required_materials:
        failures.append(
            f"{asset_spec['id']}: source materials {sorted(actual_materials)} "
            f"do not match contract {sorted(required_materials)}"
        )
    if set(memberships) != required_materials:
        failures.append(
            f"{asset_spec['id']}: grouped material coverage is incomplete"
        )
    if len(memberships) != len(set(memberships)):
        failures.append(
            f"{asset_spec['id']}: a source material appears in multiple groups"
        )
    return failures


def manifest_map_lookup(
    manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for asset in manifest.get("assets", []):
        for group in asset.get("groups", []):
            for map_item in group.get("maps", []):
                key = f"{asset['id']}/{group['id']}/{map_item['type']}"
                records[key] = map_item
    return records


def load_corrective_inputs(
    contract: dict[str, Any],
) -> dict[str, Any] | None:
    corrective = contract.get("corrective_map_contract")
    if not isinstance(corrective, dict):
        return None
    classification_path = resolve(contract["visual_failure_classification"])
    if sha256(classification_path) != contract[
        "visual_failure_classification_sha256"
    ]:
        raise RuntimeError("Build 008 visual-failure classification hash mismatch")
    classification = json.loads(
        classification_path.read_text(encoding="utf-8-sig")
    )
    if (
        classification.get("gate") != "PASS"
        or classification.get("target_build_id")
        != "BLD_M01_HERO_GROUPED_TOPOLOGY_008"
    ):
        raise RuntimeError("Build 008 visual-failure classification is not PASS")

    previous_manifest_path = resolve(corrective["source_manifest"])
    previous_receipt_path = resolve(corrective["source_review_receipt"])
    if sha256(previous_manifest_path) != corrective["source_manifest_sha256"]:
        raise RuntimeError("Build 007 manifest hash mismatch")
    if (
        sha256(previous_receipt_path)
        != corrective["source_review_receipt_sha256"]
    ):
        raise RuntimeError("Build 007 direct-review receipt hash mismatch")
    previous_manifest = json.loads(
        previous_manifest_path.read_text(encoding="utf-8-sig")
    )
    previous_receipt = json.loads(
        previous_receipt_path.read_text(encoding="utf-8-sig")
    )
    previous_maps = manifest_map_lookup(previous_manifest)
    receipt_results = {
        f"{item['asset']}/{item['group']}/{item['map_type']}": item
        for item in previous_receipt.get("maps", [])
    }
    rebake_targets = {
        item["key"] for item in classification["rebake_targets"]
    }
    reused_maps = {
        item["key"]: item
        for item in classification["reused_accepted_maps"]
    }
    if (
        len(rebake_targets) != corrective["rebake_map_count"]
        or len(reused_maps) != corrective["reuse_map_count"]
        or len(rebake_targets | set(reused_maps)) != 24
        or rebake_targets & set(reused_maps)
    ):
        raise RuntimeError("Build 008 corrective map partition is invalid")
    for key, evidence in reused_maps.items():
        map_item = previous_maps.get(key, {})
        receipt_item = receipt_results.get(key, {})
        source_path = Path(evidence["source_path"])
        if (
            receipt_item.get("result") != "PASS"
            or map_item.get("sha256") != evidence.get("sha256")
            or not source_path.is_file()
            or sha256(source_path) != evidence.get("sha256")
        ):
            raise RuntimeError(f"Build 008 reuse evidence invalid: {key}")
    return {
        "contract": corrective,
        "classification_path": classification_path,
        "classification": classification,
        "previous_manifest_path": previous_manifest_path,
        "previous_manifest": previous_manifest,
        "previous_receipt_path": previous_receipt_path,
        "previous_receipt": previous_receipt,
        "previous_maps": previous_maps,
        "rebake_targets": rebake_targets,
        "reused_maps": reused_maps,
        "group_policies": classification["group_policies"],
    }


def reuse_accepted_map(
    key: str,
    output: Path,
    corrective_inputs: dict[str, Any],
) -> dict[str, Any]:
    evidence = corrective_inputs["reused_maps"][key]
    source_path = Path(evidence["source_path"])
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, output)
    copied = file_evidence(output)
    if copied["sha256"] != evidence["sha256"]:
        raise RuntimeError(f"Build 008 copied map hash mismatch: {key}")
    record = copy.deepcopy(corrective_inputs["previous_maps"][key])
    record.update(copied)
    record["provenance"] = {
        "mode": "hash_verified_reuse",
        "source_build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
        "source_path": str(source_path),
        "source_sha256": evidence["sha256"],
        "source_review_result": "PASS",
        "rebaked": False,
    }
    return record


def main() -> None:
    started = time.perf_counter()
    contract_path = contract_path_from_argv()
    contract, base_contract_path = load_effective_contract(contract_path)
    corrective_inputs = load_corrective_inputs(contract)
    source_path = resolve(contract["source_blend"])
    if sha256(source_path) != contract["source_sha256"]:
        raise RuntimeError("Source blend hash does not match grouped 003 contract")

    output_paths = {
        key: resolve(value)
        for key, value in contract["outputs"].items()
        if key != "texture_root"
    }
    texture_root = resolve(contract["outputs"]["texture_root"])
    for path in [*output_paths.values(), texture_root]:
        (path if path.suffix == "" else path.parent).mkdir(
            parents=True,
            exist_ok=True,
        )

    bpy.ops.wm.open_mainfile(filepath=str(source_path))
    scene = bpy.context.scene
    bake_contract = contract["bake_contract"]
    scene.render.engine = bake_contract["engine"]
    scene.cycles.device = bake_contract["device"]
    scene.cycles.samples = int(bake_contract["samples"])
    scene.render.bake.margin = int(bake_contract["margin_pixels"])
    # Preserve the map-specific neutral generated background instead of
    # allowing the bake operator to clear unoccupied atlas pixels to black.
    scene.render.bake.use_clear = False
    scene.render.bake.target = "IMAGE_TEXTURES"
    scene.render.bake.normal_space = bake_contract["normal_space"]

    low_collection = bpy.data.collections.new("GROUPED008_LOW_TARGETS")
    high_collection = bpy.data.collections.new("GROUPED008_HIGH_SOURCES")
    cage_collection = bpy.data.collections.new("GROUPED008_CAGES")
    ao_collection = bpy.data.collections.new("GROUPED008_AO_OCCLUDERS")
    scratch_collection = bpy.data.collections.new(
        "GROUPED008_COMPONENT_BAKE_SCRATCH"
    )
    scene.collection.children.link(low_collection)
    scene.collection.children.link(high_collection)
    scene.collection.children.link(cage_collection)
    scene.collection.children.link(ao_collection)
    scene.collection.children.link(scratch_collection)
    repair_contract = contract.get("topology_repair_contract", {})
    group_policies = repair_contract.get("group_policies", {})
    corrective_group_policies = (
        corrective_inputs["group_policies"]
        if corrective_inputs is not None
        else {}
    )

    failures: list[str] = []
    asset_records: list[dict[str, Any]] = []
    all_low_objects = []
    all_map_hashes: list[str] = []
    resolution = int(bake_contract["resolution"])
    uv_layer = bake_contract["uv_layer"]
    uv_margin = float(bake_contract["margin_pixels"]) / resolution

    for asset_spec in contract["assets"]:
        source = bpy.data.objects.get(asset_spec["source_object"])
        if source is None or source.type != "MESH":
            failures.append(
                f"{asset_spec['id']}: missing mesh source "
                f"{asset_spec['source_object']}"
            )
            continue
        failures.extend(validate_source_partition(asset_spec, source))
        source_counts = source_material_face_counts(source)
        group_records: list[dict[str, Any]] = []
        retained_face_total = 0

        for group_spec in asset_spec["groups"]:
            group_key = f"{asset_spec['id']}/{group_spec['id']}"
            repair_policy = group_policies.get(
                group_key,
                {
                    "remove_zero_area_faces": False,
                    "split_nonmanifold_edges": False,
                    "ao_policy": "direct_low_self_occlusion",
                },
            )
            corrective_policy = corrective_group_policies.get(group_key, {})
            group_materials = set(group_spec["materials"])
            low = extract_material_group(
                source,
                group_spec["low_object"],
                group_materials,
                low_collection,
            )
            if not low.data.polygons:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: empty group"
                )
                continue
            partition_source_face_count = len(low.data.polygons)
            low["SKG_BakeRole"] = "semantic_production_low"
            low["SKG_BakeAsset"] = asset_spec["id"]
            low["SKG_BakeGroup"] = group_spec["id"]
            low["SKG_SourceMaterials"] = json.dumps(
                sorted(group_spec["materials"])
            )
            topology_repair = repair_partition_topology(
                low,
                repair_policy,
            )
            low["SKG_TopologyRepair"] = json.dumps(
                topology_repair,
                sort_keys=True,
            )
            low_face_orientation = author_consistent_face_normals(low)
            low["SKG_FaceNormalAuthoring"] = low_face_orientation["method"]
            smoothing = author_smoothing(
                low,
                float(group_spec["hard_edge_angle_degrees"]),
            )
            uv = author_group_uv(low, uv_layer, uv_margin)
            low["SKG_UVAuthoring"] = uv["method"]
            low["SKG_SmoothingAngleDegrees"] = float(
                group_spec["hard_edge_angle_degrees"]
            )

            high = duplicate_mesh(
                low,
                group_spec["high_object"],
                high_collection,
            )
            high["SKG_BakeRole"] = "semantic_group_high_source"
            high["SKG_BakeAsset"] = asset_spec["id"]
            high["SKG_BakeGroup"] = group_spec["id"]
            apply_high_bevel(high, float(group_spec["bevel_width_m"]))
            high_density_method = ensure_high_density(
                high,
                len(low.data.vertices),
            )
            high_face_orientation = author_consistent_face_normals(high)
            high["SKG_FaceNormalAuthoring"] = high_face_orientation["method"]
            high_smoothing = author_smoothing(
                high,
                float(group_spec["hard_edge_angle_degrees"]),
            )
            ao_policy = repair_policy["ao_policy"]
            ao_occluder = None
            ao_occluder_stats = None
            if (
                ao_policy
                == "selected_to_active_from_dedicated_bounded_ao_occluder"
            ):
                ao_occluder = duplicate_mesh(
                    high,
                    repair_policy["ao_occluder_object"],
                    ao_collection,
                )
                ao_occluder["SKG_BakeRole"] = "dedicated_bounded_ao_occluder"
                ao_occluder["SKG_BakeAsset"] = asset_spec["id"]
                ao_occluder["SKG_BakeGroup"] = group_spec["id"]
                ao_occluder["SKG_MaxRayDistanceM"] = float(
                    group_spec["max_ray_distance_m"]
                )
                ao_occluder_stats = mesh_stats(ao_occluder)

            cage, zero_cage_normals = make_normal_offset_cage(
                low,
                group_spec["cage_object"],
                float(group_spec["cage_extrusion_m"]),
                cage_collection,
            )
            cage["SKG_BakeAsset"] = asset_spec["id"]
            cage["SKG_BakeGroup"] = group_spec["id"]

            low_stats = mesh_stats(low)
            high_stats = mesh_stats(high)
            cage_stats = mesh_stats(cage)
            retained_face_total += partition_source_face_count
            all_low_objects.append(low)

            ratio = high_stats["vertices"] / max(1, low_stats["vertices"])
            if low_stats["orphan_vertices"] != 0:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: low has orphan vertices"
                )
            minimum_sharp_edges = int(
                contract["topology_contract"]["smoothing"].get(
                    "minimum_sharp_edges",
                    0,
                )
            )
            if smoothing["sharp_edges"] < minimum_sharp_edges:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: authored sharp "
                    f"edge count below {minimum_sharp_edges}"
                )
            if uv["authored_seam_edges"] < 1 or not uv["finite"]:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: invalid authored UV"
                )
            epsilon = 1.0e-5
            if min(uv["bounds_min"]) < -epsilon or max(uv["bounds_max"]) > 1.0 + epsilon:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: UV outside 0-1"
                )
            if ratio < float(
                contract["topology_contract"]["high_source"][
                    "minimum_high_to_low_vertex_ratio"
                ]
            ):
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: high/low "
                    f"vertex ratio {ratio:.4f} below contract"
                )
            if low.data is high.data or low.data is cage.data:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: mesh datablocks overlap"
                )
            if (
                cage_stats["vertices"] != low_stats["vertices"]
                or cage_stats["edges"] != low_stats["edges"]
                or cage_stats["faces"] != low_stats["faces"]
            ):
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: cage topology mismatch"
                )
            if zero_cage_normals:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: "
                    f"{zero_cage_normals} cage vertices have zero normals"
                )
            if not low_face_orientation["component_consistent"]:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: "
                    "low has zero-normal faces after normal authoring"
                )
            if not high_face_orientation["component_consistent"]:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: "
                    "high has zero-normal faces after normal authoring"
                )
            if topology_repair["after"]["zero_area_faces"] != 0:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: "
                    "zero-area faces remain after topology repair"
                )
            if topology_repair["after"]["nonmanifold_edges"] != 0:
                failures.append(
                    f"{asset_spec['id']}/{group_spec['id']}: "
                    "nonmanifold edges remain after topology repair"
                )

            map_records: list[dict[str, Any]] = []
            group_dir = texture_root / asset_spec["id"] / group_spec["id"]
            group_dir.mkdir(parents=True, exist_ok=True)
            for map_spec in bake_contract["maps"]:
                map_type = map_spec["type"]
                map_key = f"{group_key}/{map_type}"
                output = (
                    group_dir
                    / f"{group_spec['texture_prefix']}_{map_type}.png"
                )
                if (
                    corrective_inputs is not None
                    and map_key not in corrective_inputs["rebake_targets"]
                ):
                    record = reuse_accepted_map(
                        map_key,
                        output,
                        corrective_inputs,
                    )
                    map_records.append(record)
                    all_map_hashes.append(record["sha256"])
                    continue
                image = new_image(
                    f"{group_spec['texture_prefix']}_{map_type}",
                    resolution,
                    map_spec,
                )
                projection_policy = (
                    corrective_policy.get(
                        "ao_projection_policy",
                        (
                            "direct_low_self_occlusion"
                            if ao_policy == "direct_low_self_occlusion"
                            else (
                                "selected_to_active_from_"
                                "dedicated_bounded_ao_occluder"
                            )
                        ),
                    )
                    if map_type == "AO"
                    else corrective_policy.get(
                        "normal_projection_policy",
                        "selected_to_active_tangent_normal",
                    )
                )
                isolation_evidence = bake_group_map(
                    high,
                    low,
                    cage,
                    ao_occluder,
                    image,
                    map_type,
                    group_spec,
                    ao_policy,
                    projection_policy,
                    scratch_collection,
                    float(
                        corrective_policy.get(
                            "component_spacing_multiplier",
                            3.0,
                        )
                    ),
                )
                diagnostics = channel_stats_and_diagnostics(
                    image,
                    map_type,
                    map_spec["neutral_background"],
                )
                save_png(image, output)
                evidence = file_evidence(output)
                all_map_hashes.append(evidence["sha256"])
                varied_channels = sum(
                    value > 0.0005
                    for value in diagnostics["range"][:3]
                )
                if varied_channels < int(
                    map_spec["minimum_varied_rgb_channels"]
                ):
                    failures.append(
                        f"{asset_spec['id']}/{group_spec['id']}/{map_type}: "
                        "map content is insufficiently varied"
                    )
                maximum_black_fraction = float(
                    map_spec.get(
                        "maximum_black_pixel_fraction",
                        1.0,
                    )
                )
                if (
                    diagnostics["black_pixel_fraction"]
                    > maximum_black_fraction
                ):
                    failures.append(
                        f"{asset_spec['id']}/{group_spec['id']}/{map_type}: "
                        "black-pixel fraction "
                        f"{diagnostics['black_pixel_fraction']:.6f} exceeds "
                        f"{maximum_black_fraction:.6f}"
                    )
                projection = (
                    {
                        "isolated_group": True,
                        "mode": "direct_low_self_occlusion",
                        "selected_to_active": False,
                        "cage_object": None,
                        "cage_method": None,
                        "cage_extrusion_m": 0.0,
                        "max_ray_distance_m": 0.0,
                        "render_visibility_isolated": True,
                    }
                    if map_type == "AO"
                    and ao_policy == "direct_low_self_occlusion"
                    else {
                        "isolated_group": True,
                        "mode": (
                            projection_policy
                        ),
                        "selected_to_active": True,
                        "cage_object": cage.name,
                        "cage_method": "vertex_normal_offset",
                        "cage_extrusion_m": group_spec[
                            "cage_extrusion_m"
                        ],
                        "max_ray_distance_m": group_spec[
                            "max_ray_distance_m"
                        ],
                        "ao_occluder_object": (
                            ao_occluder.name
                            if map_type == "AO"
                            else None
                        ),
                        "render_visibility_isolated": True,
                    }
                    if map_type == "AO"
                    else {
                        "isolated_group": True,
                        "mode": projection_policy,
                        "selected_to_active": True,
                        "cage_object": cage.name,
                        "cage_method": "vertex_normal_offset",
                        "cage_extrusion_m": group_spec[
                            "cage_extrusion_m"
                        ],
                        "max_ray_distance_m": group_spec[
                            "max_ray_distance_m"
                        ],
                        "render_visibility_isolated": True,
                    }
                )
                map_records.append(
                    {
                        **evidence,
                        "type": map_type,
                        "width": resolution,
                        "height": resolution,
                        "channels": 3,
                        "color_space": map_spec["color_space"],
                        "neutral_background": map_spec[
                            "neutral_background"
                        ],
                        "varied_rgb_channels": varied_channels,
                        "diagnostics": diagnostics,
                        "projection": {
                            **projection,
                            **isolation_evidence,
                        },
                        "provenance": {
                            "mode": "corrective_rebake",
                            "source_build_id": (
                                "BLD_M01_HERO_GROUPED_TOPOLOGY_007"
                            ),
                            "source_review_result": "FAIL",
                            "rebaked": True,
                        },
                    }
                )
                bpy.data.images.remove(image)

            group_records.append(
                {
                    "id": group_spec["id"],
                    "materials": group_spec["materials"],
                    "partition_source_face_count": partition_source_face_count,
                    "low": low_stats,
                    "high": high_stats,
                    "cage": cage_stats,
                    "low_smoothing": smoothing,
                    "high_smoothing": high_smoothing,
                    "uv": uv,
                    "high_density_method": high_density_method,
                    "high_to_low_vertex_ratio": round(ratio, 7),
                    "topology_repair": topology_repair,
                    "low_face_orientation": low_face_orientation,
                    "high_face_orientation": high_face_orientation,
                    "cage_zero_normal_vertices": zero_cage_normals,
                    "ao_policy": ao_policy,
                    "ao_occluder": ao_occluder_stats,
                    "corrective_policy": corrective_policy,
                    "maps": map_records,
                }
            )

        expected_faces = sum(source_counts.values())
        if retained_face_total != expected_faces:
            failures.append(
                f"{asset_spec['id']}: retained {retained_face_total} of "
                f"{expected_faces} source faces"
            )
        asset_records.append(
            {
                "id": asset_spec["id"],
                "source_object": asset_spec["source_object"],
                "source_material_face_counts": source_counts,
                "source_face_count": expected_faces,
                "retained_group_face_count": retained_face_total,
                "groups": group_records,
            }
        )

    if len(all_low_objects) != 12:
        failures.append(
            f"Expected 12 low bake groups, found {len(all_low_objects)}"
        )
    if len(all_map_hashes) != 24:
        failures.append(
            f"Expected 24 baked maps, found {len(all_map_hashes)}"
        )

    for obj in all_low_objects:
        obj.hide_render = False
    for obj in high_collection.objects:
        obj.hide_render = True
    for obj in cage_collection.objects:
        obj.hide_render = True
    for obj in ao_collection.objects:
        obj.hide_render = True

    bpy.ops.wm.save_as_mainfile(filepath=str(output_paths["master_blend"]))
    export_low_glb(all_low_objects, output_paths["low_glb"])

    package_fingerprint = hashlib.sha256(
        "\n".join(sorted(all_map_hashes)).encode("ascii")
    ).hexdigest()
    manifest = {
        "schema": "skyguard.m01.hero-grouped-topology-bake.manifest.v1",
        "build_id": contract["build_id"],
        "generated_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
        "blender_version": bpy.app.version_string,
        "source": file_evidence(source_path),
        "contract": file_evidence(contract_path),
        "base_contract": (
            file_evidence(base_contract_path)
            if base_contract_path is not None
            else None
        ),
        "generator": file_evidence(Path(__file__).resolve()),
        "bake_contract": bake_contract,
        "topology_contract": contract["topology_contract"],
        "topology_repair_contract": contract.get(
            "topology_repair_contract"
        ),
        "corrective_map_contract": contract.get("corrective_map_contract"),
        "visual_failure_classification": (
            file_evidence(corrective_inputs["classification_path"])
            if corrective_inputs is not None
            else None
        ),
        "source_build_manifest": (
            file_evidence(corrective_inputs["previous_manifest_path"])
            if corrective_inputs is not None
            else None
        ),
        "source_direct_review_receipt": (
            file_evidence(corrective_inputs["previous_receipt_path"])
            if corrective_inputs is not None
            else None
        ),
        "assets": asset_records,
        "outputs": {
            "master_blend": file_evidence(output_paths["master_blend"]),
            "low_glb": file_evidence(output_paths["low_glb"]),
        },
        "map_count": len(all_map_hashes),
        "rebaked_map_count": (
            len(corrective_inputs["rebake_targets"])
            if corrective_inputs is not None
            else len(all_map_hashes)
        ),
        "reused_map_count": (
            len(corrective_inputs["reused_maps"])
            if corrective_inputs is not None
            else 0
        ),
        "group_count": len(all_low_objects),
        "package_fingerprint_sha256": package_fingerprint,
        "validation": {
            "pass": not failures,
            "failures": failures,
        },
        "promotion": contract["promotion"],
    }
    output_paths["manifest"].write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-bake.author-report.v1",
        "build_id": contract["build_id"],
        "gate": "PASS" if not failures else "FAIL",
        "terminal_state": (
            "GROUPED_ARTIFACTS_AUTHORED_AWAITING_INDEPENDENT_VERIFICATION"
            if not failures
            else "GROUPED_AUTHOR_VALIDATION_FAILED"
        ),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "group_count": len(all_low_objects),
        "map_count": len(all_map_hashes),
        "package_fingerprint_sha256": package_fingerprint,
        "failures": failures,
        "direct_original_resolution_map_review": "NOT_RUN",
        "mapped_mesh_grazing_angle_review": "NOT_RUN",
        "unreal_acceptance": "NOT_RUN",
        "p3_4_closed": False,
    }
    output_paths["report"].write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if failures:
        raise RuntimeError(
            f"Grouped topology author validation failed: {len(failures)} issue(s)"
        )


if __name__ == "__main__":
    main()
