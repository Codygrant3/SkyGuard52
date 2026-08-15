"""Normalize only Blender-authored GLB metadata in a fresh import package."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01\exports"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01"
EXPORTS = OUTPUT / "exports"
RECEIPT = OUTPUT / "metadata_normalization_receipt.json"
INVENTORY = OUTPUT / "artifact_inventory.json"

SOURCE_HASHES = {
    "SM_M01_Apartment_Production_A_CONSOLIDATED.glb": "d6bcb3f1edd932cb5f38b8b143f91907bcef2b3d67f865d76166c79f17438f0a",
    "SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb": "645dabf20a63e00ddf7ab94ef9e20fce10a18b609078abc5a54feb59dfecc311",
    "SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb": "d0ff2891d286aa8afa1ff3c0a22a84a561544a8e61bdba913d965227a6275860",
    "SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb": "17549ec9e9b800d5ae09752aa8adde58a4f932b26b7bdb446726f13bc2284239",
    "SM_M01_Midrise_Production_B_CONSOLIDATED.glb": "e531d0071bbd1e2cc1e94a937a4027cc685fbae5f7c5c7ed6da7a1b610654574",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_glb(path: Path) -> tuple[dict[str, object], list[tuple[int, bytes]]]:
    raw = path.read_bytes()
    require(len(raw) >= 20, f"GLB too short: {path}")
    magic, version, length = struct.unpack_from("<4sII", raw, 0)
    require(magic == b"glTF" and version == 2 and length == len(raw), f"Invalid GLB header: {path}")
    offset = 12
    chunks: list[tuple[int, bytes]] = []
    while offset < len(raw):
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        payload = raw[offset : offset + chunk_length]
        require(len(payload) == chunk_length, f"Truncated GLB chunk: {path}")
        chunks.append((chunk_type, payload))
        offset += chunk_length
    require(chunks and chunks[0][0] == 0x4E4F534A, f"GLB JSON chunk absent: {path}")
    document = json.loads(chunks[0][1].decode("utf-8").rstrip("\x00 "))
    return document, chunks


def write_glb(path: Path, document: dict[str, object], chunks: list[tuple[int, bytes]]) -> None:
    json_payload = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    json_payload += b" " * ((4 - len(json_payload) % 4) % 4)
    new_chunks = [(0x4E4F534A, json_payload)] + chunks[1:]
    total = 12 + sum(8 + len(payload) for _, payload in new_chunks)
    data = bytearray(struct.pack("<4sII", b"glTF", 2, total))
    for chunk_type, payload in new_chunks:
        data.extend(struct.pack("<II", len(payload), chunk_type))
        data.extend(payload)
    path.write_bytes(bytes(data))


def normalize_document(document: dict[str, object]) -> list[dict[str, object]]:
    original = copy.deepcopy(document)
    changes: list[dict[str, object]] = []
    for index, mesh in enumerate(document.get("meshes", [])):
        old = str(mesh.get("name", ""))
        require(old.endswith("_MESH"), f"Unexpected mesh name before normalization: {old}")
        new = old[:-5]
        mesh["name"] = new
        changes.append({"path": f"meshes[{index}].name", "before": old, "after": new})
    for index, node in enumerate(document.get("nodes", [])):
        old = str(node.get("name", ""))
        if old.startswith("SOCKET_") and old.endswith(".001"):
            new = old[:-4]
            node["name"] = new
            changes.append({"path": f"nodes[{index}].name", "before": old, "after": new})

    restored = copy.deepcopy(document)
    for change in changes:
        container, suffix = change["path"].split("[", 1)
        index_text, key = suffix.split("]", 1)
        key = key.lstrip(".")
        restored[container][int(index_text)][key] = change["before"]
    require(restored == original, "Normalization changed semantics outside the exact metadata allowlist")
    require(changes, "No metadata changes were made")
    return changes


def validate_normalized(path: Path) -> dict[str, object]:
    document, chunks = read_glb(path)
    mesh_names = [str(mesh.get("name", "")) for mesh in document.get("meshes", [])]
    node_names = [str(node.get("name", "")) for node in document.get("nodes", [])]
    require(not any(name.endswith("_MESH") for name in mesh_names), f"Mesh suffix remained: {path}")
    sockets = [name for name in node_names if name.startswith("SOCKET_")]
    require(len(sockets) == 1, f"Expected exactly one socket: {path}")
    require(not sockets[0].endswith(".001"), f"Socket suffix remained: {path}")
    render_meshes = [name for name in mesh_names if not name.startswith("UCX_")]
    collision_meshes = [name for name in mesh_names if name.startswith("UCX_")]
    require(len(render_meshes) in (2, 3), f"Render mesh budget invalid: {path}")
    require(len(collision_meshes) == 1, f"Collision mesh budget invalid: {path}")
    return {
        "mesh_names": mesh_names,
        "socket": sockets[0],
        "render_mesh_count": len(render_meshes),
        "collision_mesh_count": len(collision_meshes),
        "non_json_chunk_hashes": [sha256_bytes(payload) for _, payload in chunks[1:]],
    }


def run_offline_contract_test() -> int:
    for name, expected in SOURCE_HASHES.items():
        path = SOURCE / name
        require(path.is_file(), f"Missing source GLB: {path}")
        require(sha256(path) == expected, f"Source GLB hash mismatch: {path}")
        document, chunks = read_glb(path)
        before_chunks = [sha256_bytes(payload) for _, payload in chunks[1:]]
        normalized = copy.deepcopy(document)
        changes = normalize_document(normalized)
        require(changes, f"No normalization plan for {path}")
        require(before_chunks == [sha256_bytes(payload) for _, payload in chunks[1:]], "Binary chunk changed in memory")
    require(not OUTPUT.exists(), f"Governed output exists during offline test: {OUTPUT}")
    print("PASS_OFFLINE_CONTRACT")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        return run_offline_contract_test()
    require(not OUTPUT.exists(), f"Fresh output namespace already exists: {OUTPUT}")
    EXPORTS.mkdir(parents=True)
    results = []
    for name, expected in SOURCE_HASHES.items():
        source = SOURCE / name
        require(source.is_file() and sha256(source) == expected, f"Source authority failed: {source}")
        document, chunks = read_glb(source)
        non_json_before = [sha256_bytes(payload) for _, payload in chunks[1:]]
        changes = normalize_document(document)
        destination = EXPORTS / name.replace("_CONSOLIDATED.glb", "_UNREAL_READY.glb")
        write_glb(destination, document, chunks)
        validated = validate_normalized(destination)
        require(validated["non_json_chunk_hashes"] == non_json_before, f"Non-JSON GLB chunk changed: {source}")
        results.append({
            "source": record(source),
            "output": record(destination),
            "changes": changes,
            "validation": validated,
            "binary_geometry_and_embedded_image_chunks_unchanged": True,
        })
    receipt = {
        "schema": "skyguard.m01-visible-environment-metadata-normalization01-receipt.v1",
        "created_utc": utc_now(),
        "classification": "PASSED_METADATA_NORMALIZATION_READY_FOR_UNREAL_IMPORT_REPROBE",
        "source_attempt_terminal": str(ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_ATTEMPT01_TERMINAL_FREEZE.json"),
        "files": results,
        "geometry_modified": False,
        "materials_modified": False,
        "binary_chunks_modified": False,
        "allowed_metadata_changes": ["meshes[*].name remove _MESH suffix", "socket node name remove .001 suffix"],
        "map_integration_authorized": False,
        "next_gate": "ONE_FRESH_UNREAL_IMPORT_REPROBE_OF_NORMALIZED_APARTMENT_GLB",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path != INVENTORY)
    INVENTORY.write_text(json.dumps({"schema": "skyguard.m01-visible-environment-metadata-normalization01-inventory.v1", "created_utc": utc_now(), "files": [record(path) for path in files]}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
