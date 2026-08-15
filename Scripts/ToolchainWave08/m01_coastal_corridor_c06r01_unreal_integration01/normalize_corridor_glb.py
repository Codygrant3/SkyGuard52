"""Create an Unreal-safe metadata-only derivative of the accepted corridor GLB."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / (
    r"Production\Attempts\m01-coastal-corridor-correction06-recovery01-unrealready01"
    r"\attempt_20260810T203315932981Z\output"
    r"\M01_CoastalCorridor_Correction06_Recovery01_UnrealReady01.glb"
)
OUTPUT_ROOT = ROOT / (
    r"Production\Derived"
    r"\m01-coastal-corridor-correction06-recovery01-unrealready01-normalized01"
)
OUTPUT = OUTPUT_ROOT / "M01_CoastalCorridor_C06R01_UNREAL_READY.glb"
RECEIPT = OUTPUT_ROOT / "metadata_normalization_receipt.json"
INVENTORY = OUTPUT_ROOT / "artifact_inventory.json"
SOURCE_BYTES = 48_367_648
SOURCE_SHA256 = "aebc15a9daa38843fc8795c3e6e467b5ff737c195cc6ade238b8f40a2239d284"
EXPECTED_MESH_NAMES = {
    "SM_M01_CoastalCorridor_C06R01_CONTACT_MESH",
    "SM_M01_CoastalCorridor_C06R01_DETAILS_MESH",
    "SM_M01_CoastalCorridor_C06R01_HARDSCAPE_MESH",
    "SM_M01_CoastalCorridor_C06R01_TERRAIN_MESH",
    "UCX_SM_M01_CoastalCorridor_C06R01_TERRAIN_00_MESH",
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
    require(len(raw) >= 20, "GLB is too short")
    magic, version, total = struct.unpack_from("<4sII", raw, 0)
    require(magic == b"glTF" and version == 2 and total == len(raw), "Invalid GLB header")
    offset = 12
    chunks: list[tuple[int, bytes]] = []
    while offset < len(raw):
        length, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        payload = raw[offset : offset + length]
        require(len(payload) == length, "Truncated GLB chunk")
        chunks.append((kind, payload))
        offset += length
    require(chunks and chunks[0][0] == 0x4E4F534A, "GLB JSON chunk is absent")
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


def validate_source() -> tuple[dict[str, object], list[tuple[int, bytes]]]:
    require(SOURCE.is_file(), f"Accepted GLB is missing: {SOURCE}")
    require(SOURCE.stat().st_size == SOURCE_BYTES, "Accepted GLB byte count changed")
    require(sha256(SOURCE) == SOURCE_SHA256, "Accepted GLB hash changed")
    document, chunks = read_glb(SOURCE)
    names = {str(mesh.get("name", "")) for mesh in document.get("meshes", [])}
    require(names == EXPECTED_MESH_NAMES, f"Accepted mesh-name contract changed: {sorted(names)}")
    nodes = [str(node.get("name", "")) for node in document.get("nodes", [])]
    require(nodes.count("SOCKET_M01_CoastalCorridor_C06R01_Origin") == 1, "Origin socket contract changed")
    return document, chunks


def normalize(document: dict[str, object]) -> list[dict[str, str]]:
    changes = []
    for index, mesh in enumerate(document.get("meshes", [])):
        before = str(mesh.get("name", ""))
        require(before.endswith("_MESH"), f"Unexpected pre-normalization mesh name: {before}")
        after = before[:-5]
        mesh["name"] = after
        changes.append({"path": f"meshes[{index}].name", "before": before, "after": after})
    require(len(changes) == 5, "Expected exactly five metadata changes")
    return changes


def run_offline_contract_test() -> int:
    document, chunks = validate_source()
    binary_hashes = [sha256_bytes(payload) for _, payload in chunks[1:]]
    changes = normalize(document)
    require(len(changes) == 5, "Normalization plan is incomplete")
    require(binary_hashes == [sha256_bytes(payload) for _, payload in chunks[1:]], "Binary chunks changed in memory")
    require(not OUTPUT_ROOT.exists(), f"Fresh normalized namespace already exists: {OUTPUT_ROOT}")
    print("PASS_CORRIDOR_GLB_METADATA_NORMALIZATION_CONTRACT")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        return run_offline_contract_test()

    require(not OUTPUT_ROOT.exists(), f"Fresh normalized namespace already exists: {OUTPUT_ROOT}")
    document, chunks = validate_source()
    binary_before = [sha256_bytes(payload) for _, payload in chunks[1:]]
    changes = normalize(document)
    OUTPUT_ROOT.mkdir(parents=True)
    write_glb(OUTPUT, document, chunks)
    normalized, normalized_chunks = read_glb(OUTPUT)
    binary_after = [sha256_bytes(payload) for _, payload in normalized_chunks[1:]]
    require(binary_after == binary_before, "Geometry or embedded image chunks changed")
    mesh_names = [str(mesh.get("name", "")) for mesh in normalized.get("meshes", [])]
    require(not any(name.endswith("_MESH") for name in mesh_names), "A normalized mesh retained _MESH")
    require(len(set(mesh_names)) == 5, "Normalized mesh names are not unique")
    receipt = {
        "schema": "skyguard.m01-c06r01-unrealready01-normalized01.receipt.v1",
        "classification": "PASSED_METADATA_NORMALIZATION_READY_FOR_UNREAL_IMPORT",
        "source": record(SOURCE),
        "output": record(OUTPUT),
        "changes": changes,
        "normalized_mesh_names": mesh_names,
        "binary_geometry_and_embedded_image_chunks_unchanged": True,
        "geometry_modified": False,
        "materials_modified": False,
    }
    write_json_atomic(RECEIPT, receipt)
    write_json_atomic(INVENTORY, {
        "schema": "skyguard.m01-c06r01-unrealready01-normalized01.inventory.v1",
        "files": [record(OUTPUT), record(RECEIPT)],
    })
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
