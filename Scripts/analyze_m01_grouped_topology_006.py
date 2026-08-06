"""Offline GLB topology classifier for Mission 01 grouped bake Build 006.

This script deliberately has no Blender Python dependency and launches no DCC. It
reads the persisted Build 006 low GLB plus author manifest, welds exporter
vertex splits by position, and emits deterministic evidence for Build 007
topology repair planning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(r"D:\Skyguard52")
DEFAULT_GLB = (
    ROOT
    / "Content/Skyguard/Meshes/Source/Mission01/HeroGroupedTopology_006"
    / "bld_m01_hero_grouped_topology_006_low.glb"
)
DEFAULT_MANIFEST = (
    ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_BAKE_MANIFEST_006.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_CLASSIFICATION_007.json"
)

COMPONENT_FORMATS = {
    5120: ("b", 1),
    5121: ("B", 1),
    5122: ("h", 2),
    5123: ("H", 2),
    5125: ("I", 4),
    5126: ("f", 4),
}
TYPE_WIDTHS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_glb(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError("Invalid GLB 2.0 header")
    offset = 12
    json_chunk: bytes | None = None
    binary_chunk: bytes | None = None
    while offset < total:
        length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset : offset + length]
        offset += length
        if chunk_type == 0x4E4F534A:
            json_chunk = payload
        elif chunk_type == 0x004E4942:
            binary_chunk = payload
    if json_chunk is None or binary_chunk is None:
        raise ValueError("GLB is missing JSON or BIN chunk")
    return json.loads(json_chunk.decode("utf-8")), binary_chunk


def read_accessor(
    document: dict[str, Any],
    binary: bytes,
    accessor_index: int,
) -> list[tuple[float, ...] | int]:
    accessor = document["accessors"][accessor_index]
    view = document["bufferViews"][accessor["bufferView"]]
    component_type = accessor["componentType"]
    fmt, component_size = COMPONENT_FORMATS[component_type]
    width = TYPE_WIDTHS[accessor["type"]]
    stride = view.get("byteStride", component_size * width)
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    unpack = struct.Struct("<" + fmt * width)
    values: list[tuple[float, ...] | int] = []
    for item_index in range(accessor["count"]):
        value = unpack.unpack_from(binary, start + item_index * stride)
        values.append(value[0] if width == 1 else value)
    return values


def sub(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def length(value: tuple[float, ...]) -> float:
    return math.sqrt(dot(value, value))


def triangle_area(
    a: tuple[float, ...],
    b: tuple[float, ...],
    c: tuple[float, ...],
) -> float:
    return 0.5 * length(cross(sub(b, a), sub(c, a)))


def weld_positions(
    positions: list[tuple[float, ...]],
) -> tuple[list[tuple[float, float, float]], list[int], float]:
    minimum = [min(value[axis] for value in positions) for axis in range(3)]
    maximum = [max(value[axis] for value in positions) for axis in range(3)]
    diagonal = math.sqrt(
        sum((maximum[axis] - minimum[axis]) ** 2 for axis in range(3))
    )
    epsilon = max(diagonal * 1.0e-7, 1.0e-8)
    lookup: dict[tuple[int, int, int], int] = {}
    welded: list[tuple[float, float, float]] = []
    remap: list[int] = []
    for value in positions:
        key = tuple(round(value[axis] / epsilon) for axis in range(3))
        if key not in lookup:
            lookup[key] = len(welded)
            welded.append((float(value[0]), float(value[1]), float(value[2])))
        remap.append(lookup[key])
    return welded, remap, epsilon


def triangle_components(
    triangles: list[tuple[int, int, int]],
) -> list[list[int]]:
    edge_to_triangles: dict[tuple[int, int], list[int]] = defaultdict(list)
    for triangle_index, triangle in enumerate(triangles):
        for start, end in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            edge_to_triangles[tuple(sorted((start, end)))].append(triangle_index)
    adjacency: dict[int, set[int]] = {
        index: set() for index in range(len(triangles))
    }
    for linked in edge_to_triangles.values():
        for left in linked:
            adjacency[left].update(right for right in linked if right != left)
    remaining = set(adjacency)
    components: list[list[int]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue: deque[int] = deque([seed])
        component: list[int] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            neighbors = adjacency[current] & remaining
            remaining.difference_update(neighbors)
            queue.extend(sorted(neighbors))
        components.append(sorted(component))
    return components


def edge_diagnostics(
    triangles: list[tuple[int, int, int]],
    component: Iterable[int],
) -> tuple[int, int, int]:
    uses: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for triangle_index in component:
        triangle = triangles[triangle_index]
        for start, end in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            uses[tuple(sorted((start, end)))].append((start, end))
    boundary = sum(len(items) == 1 for items in uses.values())
    nonmanifold = sum(len(items) > 2 for items in uses.values())
    inconsistent = sum(
        len(items) == 2 and items[0] == items[1] for items in uses.values()
    )
    return boundary, nonmanifold, inconsistent


def component_metrics(
    positions: list[tuple[float, float, float]],
    triangles: list[tuple[int, int, int]],
    component: list[int],
) -> dict[str, Any]:
    vertex_indices = sorted(
        {
            vertex
            for triangle_index in component
            for vertex in triangles[triangle_index]
        }
    )
    points = [positions[index] for index in vertex_indices]
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    area = 0.0
    signed_volume = 0.0
    for triangle_index in component:
        ia, ib, ic = triangles[triangle_index]
        a, b, c = positions[ia], positions[ib], positions[ic]
        area += triangle_area(a, b, c)
        signed_volume += dot(a, cross(b, c)) / 6.0
    boundary, nonmanifold, inconsistent = edge_diagnostics(
        triangles,
        component,
    )
    return {
        "triangles": len(component),
        "vertices": len(vertex_indices),
        "bounds_min": [round(value, 8) for value in minimum],
        "bounds_max": [round(value, 8) for value in maximum],
        "surface_area": round(area, 10),
        "signed_volume": round(signed_volume, 10),
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "inconsistent_winding_edges": inconsistent,
        "closed_manifold": boundary == 0 and nonmanifold == 0,
        "_vertex_indices": vertex_indices,
        "_triangle_indices": component,
    }


def point_in_component(
    point: tuple[float, float, float],
    positions: list[tuple[float, float, float]],
    triangles: list[tuple[int, int, int]],
    component: dict[str, Any],
) -> bool:
    direction = (1.0, 0.17320508075688773, 0.337)
    hits = 0
    epsilon = 1.0e-9
    for triangle_index in component["_triangle_indices"]:
        ia, ib, ic = triangles[triangle_index]
        a, b, c = positions[ia], positions[ib], positions[ic]
        edge1 = sub(b, a)
        edge2 = sub(c, a)
        h = cross(direction, edge2)
        determinant = dot(edge1, h)
        if abs(determinant) <= epsilon:
            continue
        inverse = 1.0 / determinant
        s = sub(point, a)
        u = inverse * dot(s, h)
        if u < -epsilon or u > 1.0 + epsilon:
            continue
        q = cross(s, edge1)
        v = inverse * dot(direction, q)
        if v < -epsilon or u + v > 1.0 + epsilon:
            continue
        distance = inverse * dot(edge2, q)
        if distance > epsilon:
            hits += 1
    return hits % 2 == 1


def classify_mesh(
    name: str,
    primitive_payloads: list[tuple[list[tuple[float, ...]], list[int]]],
) -> dict[str, Any]:
    raw_positions: list[tuple[float, ...]] = []
    raw_triangles: list[tuple[int, int, int]] = []
    for positions, indices in primitive_payloads:
        offset = len(raw_positions)
        raw_positions.extend(positions)
        raw_triangles.extend(
            (
                offset + indices[index],
                offset + indices[index + 1],
                offset + indices[index + 2],
            )
            for index in range(0, len(indices), 3)
        )
    welded, remap, epsilon = weld_positions(raw_positions)
    area_epsilon = max(epsilon * epsilon, 1.0e-16)
    triangles: list[tuple[int, int, int]] = []
    degenerate = 0
    duplicate_keys: dict[tuple[int, int, int], int] = defaultdict(int)
    for raw in raw_triangles:
        triangle = tuple(remap[index] for index in raw)
        if (
            len(set(triangle)) < 3
            or triangle_area(
                welded[triangle[0]],
                welded[triangle[1]],
                welded[triangle[2]],
            )
            <= area_epsilon
        ):
            degenerate += 1
            continue
        duplicate_keys[tuple(sorted(triangle))] += 1
        triangles.append(triangle)
    components = [
        component_metrics(welded, triangles, item)
        for item in triangle_components(triangles)
    ]
    nested_pairs: list[dict[str, int]] = []
    for inner_index, inner in enumerate(components):
        points = [welded[index] for index in inner["_vertex_indices"]]
        centroid = tuple(
            sum(point[axis] for point in points) / len(points)
            for axis in range(3)
        )
        for outer_index, outer in enumerate(components):
            if inner_index == outer_index or not outer["closed_manifold"]:
                continue
            bounds_contain = all(
                outer["bounds_min"][axis] - epsilon
                <= inner["bounds_min"][axis]
                and inner["bounds_max"][axis]
                <= outer["bounds_max"][axis] + epsilon
                for axis in range(3)
            )
            if bounds_contain and point_in_component(
                centroid,
                welded,
                triangles,
                outer,
            ):
                nested_pairs.append(
                    {"inner": inner_index, "outer": outer_index}
                )
    public_components = []
    for component in components:
        public_components.append(
            {
                key: value
                for key, value in component.items()
                if not key.startswith("_")
            }
        )
    boundary_total = sum(item["boundary_edges"] for item in components)
    nonmanifold_total = sum(item["nonmanifold_edges"] for item in components)
    inconsistent_total = sum(
        item["inconsistent_winding_edges"] for item in components
    )
    inward_closed = sum(
        item["closed_manifold"] and item["signed_volume"] < 0.0
        for item in components
    )
    duplicate_triangles = sum(
        count - 1 for count in duplicate_keys.values() if count > 1
    )
    classifications: list[str] = []
    if degenerate:
        classifications.append("degenerate")
    if duplicate_triangles:
        classifications.append("duplicate_surface")
    if nonmanifold_total:
        classifications.append("nonmanifold")
    if boundary_total:
        classifications.append("open_shell")
    if nested_pairs:
        classifications.append("nested_shell")
    if inward_closed:
        classifications.append("interior_or_inward_shell")
    if not classifications:
        classifications.append("closed_exterior_candidate")
    return {
        "mesh": name,
        "raw_vertices": len(raw_positions),
        "welded_vertices": len(welded),
        "raw_triangles": len(raw_triangles),
        "valid_triangles": len(triangles),
        "degenerate_triangles": degenerate,
        "duplicate_triangles": duplicate_triangles,
        "component_count": len(components),
        "closed_component_count": sum(
            item["closed_manifold"] for item in components
        ),
        "boundary_edges": boundary_total,
        "nonmanifold_edges": nonmanifold_total,
        "inconsistent_winding_edges": inconsistent_total,
        "inward_closed_components": inward_closed,
        "nested_component_pairs": nested_pairs,
        "classification": classifications,
        "weld_epsilon": epsilon,
        "components": public_components,
    }


def manifest_groups(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for asset in manifest["assets"]:
        for group in asset["groups"]:
            ao = next(item for item in group["maps"] if item["type"] == "AO")
            result[group["low"]["mesh_datablock"]] = {
                "asset": asset["id"],
                "group": group["id"],
                "ao_black_pixel_fraction": ao["diagnostics"][
                    "black_pixel_fraction"
                ],
                "ao_contract_pass": ao["diagnostics"][
                    "black_pixel_fraction"
                ]
                <= 0.35,
            }
    return result


def recommended_repair(record: dict[str, Any]) -> dict[str, Any]:
    classes = set(record["classification"])
    operations: list[str] = []
    if "degenerate" in classes:
        operations.append("delete_zero_area_faces_and_orphan_geometry")
    if "duplicate_surface" in classes:
        operations.append("remove_duplicate_coplanar_faces")
    if "nonmanifold" in classes:
        operations.append("split_or_rebuild_nonmanifold_edges")
    if "open_shell" in classes:
        operations.append("exclude_open_shell_from_direct_self_ao")
    if "nested_shell" in classes:
        operations.append("classify_nested_components_as_exterior_or_interior")
        operations.append("exclude_interior_nested_shells_from_low_ao_target")
    if "interior_or_inward_shell" in classes:
        operations.append("reverse_or_exclude_inward_closed_components")
    if not operations and not record["ao_contract_pass"]:
        operations.append("author_bounded_group_ao_occluder")
    elif not record["ao_contract_pass"]:
        operations.append("author_bounded_group_ao_occluder_after_repair")
    return {
        "operations": operations,
        "ao_policy": (
            "direct_low_self_occlusion"
            if record["ao_contract_pass"] and not operations
            else "selected_to_active_from_dedicated_bounded_ao_occluder"
        ),
        "deterministic_order": [
            "remove_degenerate_and_duplicate_faces",
            "repair_or_split_nonmanifold_edges",
            "classify_components",
            "remove_interior_ao_components",
            "recalculate_component_normals",
            "construct_bounded_ao_occluder",
            "validate_topology_then_bake",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", type=Path, default=DEFAULT_GLB)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    document, binary = load_glb(args.glb)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    lookup = manifest_groups(manifest)
    records: list[dict[str, Any]] = []
    for mesh in document["meshes"]:
        payloads = []
        for primitive in mesh["primitives"]:
            positions = read_accessor(
                document,
                binary,
                primitive["attributes"]["POSITION"],
            )
            indices = read_accessor(document, binary, primitive["indices"])
            payloads.append((positions, [int(value) for value in indices]))
        record = classify_mesh(mesh["name"], payloads)
        identity = lookup.get(mesh["name"], {})
        record.update(identity)
        record["repair"] = recommended_repair(record)
        records.append(record)
    records.sort(key=lambda item: (item.get("asset", ""), item.get("group", "")))
    report = {
        "schema": "skyguard.m01.grouped-topology-classification.v1",
        "source_build_id": manifest["build_id"],
        "target_build_id": "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
        "analysis_mode": "offline_glb_only_no_blender_no_unreal",
        "source_glb": str(args.glb),
        "source_glb_sha256": sha256_file(args.glb),
        "source_manifest": str(args.manifest),
        "source_manifest_sha256": sha256_file(args.manifest),
        "group_count": len(records),
        "groups": records,
        "summary": {
            "degenerate_groups": sum(
                "degenerate" in item["classification"] for item in records
            ),
            "open_shell_groups": sum(
                "open_shell" in item["classification"] for item in records
            ),
            "nested_shell_groups": sum(
                "nested_shell" in item["classification"] for item in records
            ),
            "interior_or_inward_shell_groups": sum(
                "interior_or_inward_shell" in item["classification"]
                for item in records
            ),
            "nonmanifold_groups": sum(
                "nonmanifold" in item["classification"] for item in records
            ),
            "ao_failed_groups": sum(
                not item.get("ao_contract_pass", False) for item in records
            ),
            "dedicated_ao_occluder_groups": sum(
                item["repair"]["ao_policy"]
                == "selected_to_active_from_dedicated_bounded_ao_occluder"
                for item in records
            ),
        },
        "gate": "PASS",
        "terminal_state": "BUILD007_TOPOLOGY_CLASSIFICATION_READY",
        "non_claims": [
            "No Blender or Unreal process was launched.",
            "Classification does not authorize a bake or asset promotion.",
            "GLB welding reconstructs topology across exporter UV/normal splits.",
            "Build 006 remains immutable failed evidence.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
