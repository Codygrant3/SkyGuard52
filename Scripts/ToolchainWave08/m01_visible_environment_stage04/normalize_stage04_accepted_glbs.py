"""Create metadata-only Unreal-safe derivatives of two accepted Stage04 GLBs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
OUTPUT_ROOT = ROOT / "Production/Derived/m01-visible-environment-stage04-accepted-glbs-normalized01"
RECEIPT = OUTPUT_ROOT / "metadata_normalization_receipt.json"
INVENTORY = OUTPUT_ROOT / "artifact_inventory.json"

ASSETS = {
    "facade": {
        "source": ROOT / r"Production\Attempts\m01-coastal-facade-bay-production01-recovery02\attempt_20260812T234648713102Z\output\exports\M01_CoastalFacadeBay_Production01.glb",
        "bytes": 38_550_760,
        "sha256": "659eb58bacd4f7cfb5fd9e17daffa18a1da9f438bb8c98f22a4d9fbeedfe2085",
        "output": "M01_CoastalFacadeBay_Production01_UE.glb",
        "render_nodes": {
            "SM_M01_CoastalFacadeBay_A_BalconyDetails": 3,
            "SM_M01_CoastalFacadeBay_A_Glass": 1,
            "SM_M01_CoastalFacadeBay_A_Interior": 9,
            "SM_M01_CoastalFacadeBay_A_StructureFrame": 8,
        },
        "collisions": {
            "UCX_SM_M01_CoastalFacadeBay_A_BalconyDetails_00",
            "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_00",
            "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_01",
            "UCX_SM_M01_CoastalFacadeBay_A_StructureFrame_02",
        },
        "sockets": {
            "SOCKET_M01_CoastalFacadeBay_AttachLeft",
            "SOCKET_M01_CoastalFacadeBay_AttachRight",
            "SOCKET_M01_CoastalFacadeBay_Balcony",
            "SOCKET_M01_CoastalFacadeBay_Origin",
            "SOCKET_M01_CoastalFacadeBay_WindowCenter",
        },
    },
    "lighthouse": {
        "source": ROOT / r"Saved\BuildAttempts\M01_LIGHTHOUSE_PRODUCTION_REFINEMENT01_RECOVERY04\attempt_01\output\exports\M01_Lighthouse_Production_Refinement01.glb",
        "bytes": 38_247_728,
        "sha256": "4c853ca72b2f095700401be5d2d4177765527acc7e07dee599f6db66fd0ecee8",
        "output": "M01_Lighthouse_Production_Refinement01_UE.glb",
        "render_nodes": {
            "SM_M01_Lighthouse_Details_A": 7,
            "SM_M01_Lighthouse_Lantern_A": 7,
            "SM_M01_Lighthouse_Tower_A": 3,
        },
        "collisions": {
            "UCX_SM_M01_Lighthouse_Lantern_A_00",
            "UCX_SM_M01_Lighthouse_Tower_A_00",
        },
        "sockets": {
            "SOCKET_Lighthouse_Door",
            "SOCKET_Lighthouse_Gallery",
            "SOCKET_Lighthouse_Lamp",
            "SOCKET_Lighthouse_Origin",
        },
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_glb(path: Path) -> tuple[dict[str, object], list[tuple[int, bytes]]]:
    raw = path.read_bytes()
    require(len(raw) >= 20, f"GLB is too short: {path}")
    magic, version, total = struct.unpack_from("<4sII", raw, 0)
    require(magic == b"glTF" and version == 2 and total == len(raw), f"Invalid GLB header: {path}")
    offset = 12
    chunks: list[tuple[int, bytes]] = []
    while offset < len(raw):
        length, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        payload = raw[offset : offset + length]
        require(len(payload) == length, f"Truncated GLB chunk: {path}")
        chunks.append((kind, payload))
        offset += length
    require(chunks and chunks[0][0] == 0x4E4F534A, f"GLB JSON chunk missing: {path}")
    document = json.loads(chunks[0][1].decode("utf-8").rstrip("\x00 \t\r\n"))
    return document, chunks


def write_glb(path: Path, document: dict[str, object], chunks: list[tuple[int, bytes]]) -> None:
    json_payload = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    json_payload += b" " * ((4 - len(json_payload) % 4) % 4)
    output_chunks = [(0x4E4F534A, json_payload), *chunks[1:]]
    total = 12 + sum(8 + len(payload) for _, payload in output_chunks)
    data = bytearray(struct.pack("<4sII", b"glTF", 2, total))
    for kind, payload in output_chunks:
        data.extend(struct.pack("<II", len(payload), kind))
        data.extend(payload)
    path.write_bytes(bytes(data))


def validate_and_normalize(key: str, spec: dict[str, object], write: bool) -> dict[str, object]:
    source = Path(spec["source"])
    require(source.is_file(), f"Accepted {key} GLB missing")
    require(source.stat().st_size == spec["bytes"] and sha256(source) == spec["sha256"], f"Accepted {key} GLB authority changed")
    document, chunks = read_glb(source)
    binary_before = [sha256_bytes(payload) for _, payload in chunks[1:]]
    nodes = document.get("nodes", [])
    meshes = document.get("meshes", [])
    node_names = [str(node.get("name", "")) for node in nodes]
    required_nodes = set(spec["render_nodes"]) | set(spec["collisions"]) | set(spec["sockets"])
    require(required_nodes.issubset(set(node_names)), f"{key} node contract changed")
    changes = []
    seen_mesh_indices: set[int] = set()
    for node_index, node in enumerate(nodes):
        if "mesh" not in node:
            continue
        mesh_index = int(node["mesh"])
        require(0 <= mesh_index < len(meshes), f"{key} node references invalid mesh")
        require(mesh_index not in seen_mesh_indices, f"{key} mesh is instanced by multiple semantic nodes")
        seen_mesh_indices.add(mesh_index)
        node_name = str(node.get("name", ""))
        require(node_name in set(spec["render_nodes"]) | set(spec["collisions"]), f"Unexpected meshed node in {key}: {node_name}")
        before = str(meshes[mesh_index].get("name", ""))
        meshes[mesh_index]["name"] = node_name
        if before != node_name:
            changes.append({"path": f"meshes[{mesh_index}].name", "before": before, "after": node_name})
    require(len(seen_mesh_indices) == len(meshes), f"{key} contains an unreferenced mesh")
    observed = {str(mesh.get("name", "")): len(mesh.get("primitives", [])) for mesh in meshes}
    expected = {**spec["render_nodes"], **{name: 1 for name in spec["collisions"]}}
    require(observed == expected, f"{key} normalized mesh contract mismatch: {observed}")
    row: dict[str, object] = {
        "asset": key,
        "source": record(source),
        "changes": changes,
        "normalized_mesh_primitives": observed,
        "socket_nodes": sorted(spec["sockets"]),
        "geometry_and_embedded_image_chunks_unchanged": True,
    }
    if write:
        output = OUTPUT_ROOT / str(spec["output"])
        write_glb(output, document, chunks)
        normalized, normalized_chunks = read_glb(output)
        require([sha256_bytes(payload) for _, payload in normalized_chunks[1:]] == binary_before, f"{key} binary chunks changed")
        normalized_observed = {str(mesh.get("name", "")): len(mesh.get("primitives", [])) for mesh in normalized.get("meshes", [])}
        require(normalized_observed == expected, f"{key} written metadata changed")
        row["output"] = record(output)
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        require(not OUTPUT_ROOT.exists(), f"Fresh normalized namespace exists: {OUTPUT_ROOT}")
        rows = [validate_and_normalize(key, spec, False) for key, spec in ASSETS.items()]
        require(sum(len(row["changes"]) for row in rows) > 0, "No metadata normalization is required")
        print("PASS_STAGE04_ACCEPTED_GLB_METADATA_NORMALIZATION_CONTRACT")
        return 0

    require(not OUTPUT_ROOT.exists(), f"Fresh normalized namespace exists: {OUTPUT_ROOT}")
    OUTPUT_ROOT.mkdir(parents=True)
    rows = [validate_and_normalize(key, spec, True) for key, spec in ASSETS.items()]
    payload = {
        "schema": "skyguard.m01-visible-environment-stage04.accepted-glbs-normalized01.v1",
        "classification": "PASSED_METADATA_NORMALIZATION_READY_FOR_STAGE04_UNREAL_IMPORT",
        "assets": rows,
        "geometry_modified": False,
        "materials_modified": False,
    }
    write_json_atomic(RECEIPT, payload)
    write_json_atomic(INVENTORY, {
        "schema": "skyguard.m01-visible-environment-stage04.accepted-glbs-normalized01.inventory.v1",
        "files": [record(OUTPUT_ROOT / str(spec["output"])) for spec in ASSETS.values()] + [record(RECEIPT)],
    })
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
