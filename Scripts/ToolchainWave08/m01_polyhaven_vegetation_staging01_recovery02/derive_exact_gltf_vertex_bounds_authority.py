"""Derive exact transformed glTF vertex bounds without Blender or Unreal."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Skyguard52")
QUARANTINE = ROOT / "Saved/SourceQuarantine/M01_POLYHAVEN_VEGETATION_QUARANTINE01"
OUT = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY.json"
ASSETS = ["fir_sapling", "pine_sapling_small", "shrub_02", "shrub_04", "grass_medium_02"]

COMPONENT_DTYPES = {
    5120: np.dtype("<i1"),
    5121: np.dtype("<u1"),
    5122: np.dtype("<i2"),
    5123: np.dtype("<u2"),
    5125: np.dtype("<u4"),
    5126: np.dtype("<f4"),
}
TYPE_COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def node_matrix(node: dict[str, object]) -> np.ndarray:
    if "matrix" in node:
        return np.array(node["matrix"], dtype=np.float64).reshape((4, 4), order="F")
    translation = np.array(node.get("translation", [0, 0, 0]), dtype=np.float64)
    scale = np.array(node.get("scale", [1, 1, 1]), dtype=np.float64)
    x, y, z, w = [float(value) for value in node.get("rotation", [0, 0, 0, 1])]
    rotation = np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w, 0],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w, 0],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y, 0],
        [0, 0, 0, 1],
    ], dtype=np.float64)
    rotation[:3, :3] = rotation[:3, :3] @ np.diag(scale)
    rotation[:3, 3] = translation
    return rotation


def load_buffers(document: dict[str, object], directory: Path) -> list[bytes]:
    values: list[bytes] = []
    for row in document.get("buffers", []):
        uri = str(row["uri"])
        if uri.startswith("data:"):
            values.append(base64.b64decode(uri.split(",", 1)[1]))
        else:
            values.append((directory / uri).read_bytes())
    return values


def accessor_array(document: dict[str, object], buffers: list[bytes], index: int) -> np.ndarray:
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    dtype = COMPONENT_DTYPES[int(accessor["componentType"])]
    components = TYPE_COMPONENTS[str(accessor["type"])]
    count = int(accessor["count"])
    start = int(view.get("byteOffset", 0)) + int(accessor.get("byteOffset", 0))
    packed = dtype.itemsize * components
    stride = int(view.get("byteStride", packed))
    raw = buffers[int(view["buffer"])]
    if stride == packed:
        values = np.frombuffer(raw, dtype=dtype, count=count * components, offset=start).reshape((count, components))
    else:
        values = np.ndarray(shape=(count, components), dtype=dtype, buffer=raw, offset=start, strides=(stride, dtype.itemsize))
    return values.astype(np.float64, copy=False)


def asset_record(asset_id: str) -> dict[str, object]:
    path = QUARANTINE / asset_id / f"{asset_id}_2k.gltf"
    document = json.loads(path.read_text(encoding="utf-8"))
    buffers = load_buffers(document, path.parent)
    nodes = document["nodes"]
    scene_index = int(document.get("scene", 0))
    scenes = document.get("scenes", [])
    roots = list(scenes[scene_index]["nodes"]) if scenes else list(range(len(nodes)))
    transforms: dict[int, np.ndarray] = {}

    def visit(index: int, parent: np.ndarray) -> None:
        world = parent @ node_matrix(nodes[index])
        transforms[index] = world
        for child in nodes[index].get("children", []):
            visit(int(child), world)

    for root in roots:
        visit(int(root), np.identity(4, dtype=np.float64))

    minima: list[np.ndarray] = []
    maxima: list[np.ndarray] = []
    vertex_count = 0
    primitive_count = 0
    for node_index, node in enumerate(nodes):
        if "mesh" not in node:
            continue
        transform = transforms.get(node_index, node_matrix(node))
        for primitive in document["meshes"][int(node["mesh"])]["primitives"]:
            points = accessor_array(document, buffers, int(primitive["attributes"]["POSITION"]))[:, :3]
            homogeneous = np.column_stack((points, np.ones((len(points),), dtype=np.float64)))
            world_points = (transform @ homogeneous.T).T[:, :3]
            minima.append(world_points.min(axis=0))
            maxima.append(world_points.max(axis=0))
            vertex_count += len(points)
            primitive_count += 1
    minimum = np.vstack(minima).min(axis=0)
    maximum = np.vstack(maxima).max(axis=0)
    dimensions = maximum - minimum
    return {
        "asset_id": asset_id,
        "gltf": {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)},
        "buffer_records": [
            {"path": str(path.parent / row["uri"]), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for row, data in zip(document.get("buffers", []), buffers)
            if not str(row["uri"]).startswith("data:")
        ],
        "scene_index": scene_index,
        "root_nodes": roots,
        "primitive_count": primitive_count,
        "position_vertex_count": vertex_count,
        "minimum_m": minimum.tolist(),
        "maximum_m": maximum.tolist(),
        "dimensions_m": dimensions.tolist(),
        "dimensions_cm": (dimensions * 100.0).tolist(),
        "sorted_dimensions_cm": sorted((dimensions * 100.0).tolist()),
        "method": "Exact POSITION accessor vertices transformed through glTF scene-node matrices",
    }


records = [asset_record(asset_id) for asset_id in ASSETS]
value = {
    "schema": "skyguard.m01-polyhaven-vegetation-exact-gltf-vertex-bounds-authority.v1",
    "classification": "PASSED_OFFLINE_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY",
    "assets": records,
    "source_mutated": False,
    "unreal_launched": False,
    "blender_launched": False,
    "next_gate": "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_OFFLINE_DESIGN",
}
OUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"path": str(OUT), "bytes": OUT.stat().st_size, "sha256": sha(OUT), "assets": [{"id": row["asset_id"], "dimensions_cm": row["dimensions_cm"], "sorted_dimensions_cm": row["sorted_dimensions_cm"]} for row in records]}, indent=2))
