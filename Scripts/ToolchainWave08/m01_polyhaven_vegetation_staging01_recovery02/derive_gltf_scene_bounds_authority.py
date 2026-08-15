"""Derive transformed world-space glTF bounds without Blender or Unreal."""

from __future__ import annotations

import base64
import hashlib
import json
import struct
from pathlib import Path

import numpy as np


ROOT = Path(r"D:\Skyguard52")
QUARANTINE = ROOT / "Saved/SourceQuarantine/M01_POLYHAVEN_VEGETATION_QUARANTINE01"
OUT = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_GLTF_SCENE_BOUNDS_AUTHORITY.json"
ASSETS = ["fir_sapling", "pine_sapling_small", "shrub_02", "shrub_04", "grass_medium_02"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(node: dict[str, object]) -> np.ndarray:
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
    transform = rotation
    transform[:3, :3] = transform[:3, :3] @ np.diag(scale)
    transform[:3, 3] = translation
    return transform


def primitive_bounds(document: dict[str, object], primitive: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    accessor = document["accessors"][primitive["attributes"]["POSITION"]]
    return np.array(accessor["min"], dtype=np.float64), np.array(accessor["max"], dtype=np.float64)


def transformed_bounds(minimum: np.ndarray, maximum: np.ndarray, transform: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    corners = []
    for x in (minimum[0], maximum[0]):
        for y in (minimum[1], maximum[1]):
            for z in (minimum[2], maximum[2]):
                corners.append((transform @ np.array([x, y, z, 1.0], dtype=np.float64))[:3])
    values = np.array(corners)
    return values.min(axis=0), values.max(axis=0)


def asset_bounds(asset_id: str) -> dict[str, object]:
    path = QUARANTINE / asset_id / f"{asset_id}_2k.gltf"
    document = json.loads(path.read_text(encoding="utf-8"))
    nodes = document["nodes"]
    scenes = document.get("scenes", [])
    scene_index = int(document.get("scene", 0))
    roots = list(scenes[scene_index]["nodes"]) if scenes else list(range(len(nodes)))
    world: dict[int, np.ndarray] = {}

    def visit(index: int, parent: np.ndarray) -> None:
        current = parent @ matrix(nodes[index])
        world[index] = current
        for child in nodes[index].get("children", []):
            visit(int(child), current)

    for root in roots:
        visit(int(root), np.identity(4, dtype=np.float64))

    minima = []
    maxima = []
    mesh_node_count = 0
    primitive_count = 0
    for index, node in enumerate(nodes):
        if "mesh" not in node:
            continue
        mesh_node_count += 1
        transform = world.get(index, matrix(node))
        for primitive in document["meshes"][int(node["mesh"])]["primitives"]:
            minimum, maximum = primitive_bounds(document, primitive)
            actual_min, actual_max = transformed_bounds(minimum, maximum, transform)
            minima.append(actual_min)
            maxima.append(actual_max)
            primitive_count += 1
    minimum = np.vstack(minima).min(axis=0)
    maximum = np.vstack(maxima).max(axis=0)
    dimensions_m = maximum - minimum
    return {
        "asset_id": asset_id,
        "gltf": {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)},
        "scene_index": scene_index,
        "root_nodes": roots,
        "mesh_node_count": mesh_node_count,
        "primitive_count": primitive_count,
        "minimum_m": minimum.tolist(),
        "maximum_m": maximum.tolist(),
        "dimensions_m": dimensions_m.tolist(),
        "dimensions_cm": (dimensions_m * 100.0).tolist(),
        "method": "Accessor POSITION min/max transformed through glTF scene-node matrices",
    }


records = [asset_bounds(asset_id) for asset_id in ASSETS]
value = {
    "schema": "skyguard.m01-polyhaven-vegetation-gltf-scene-bounds-authority.v1",
    "classification": "PASSED_OFFLINE_GLTF_SCENE_BOUNDS_AUTHORITY",
    "assets": records,
    "source_mutated": False,
    "unreal_launched": False,
    "blender_launched": False,
    "next_gate": "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_OFFLINE_DESIGN",
}
OUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"path": str(OUT), "bytes": OUT.stat().st_size, "sha256": sha(OUT), "assets": [{"id": row["asset_id"], "dimensions_cm": row["dimensions_cm"]} for row in records]}, indent=2))
