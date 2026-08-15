"""Create Unreal-safe GLB identities without touching geometry or materials."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01"
EXPORTS = OUTPUT / "exports"
RECEIPT = OUTPUT / "metadata_normalization_receipt.json"
INVENTORY = OUTPUT / "artifact_inventory.json"
MAX_UNREAL_OBJECT_NAME = 40

RULES = {
    "SM_M01_Apartment_Production_A_CONSOLIDATED.glb": {
        "sha256": "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080",
        "old": "SM_M01_Apartment_Production_A",
        "new": "SM_M01_ApartmentA",
        "output": "M01_APARTMENT_A.glb",
    },
    "SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb": {
        "sha256": "7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a",
        "old": "SM_M01_CoastalDistrict_Production_A",
        "new": "SM_M01_CoastalA",
        "output": "M01_COASTAL_DISTRICT_A.glb",
    },
    "SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb": {
        "sha256": "6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8",
        "old": "SM_M01_CornerResidence_Production_C",
        "new": "SM_M01_CornerC",
        "output": "M01_CORNER_RESIDENCE_C.glb",
    },
    "SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb": {
        "sha256": "50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301",
        "old": "SM_M01_Lighthouse_Production_A",
        "new": "SM_M01_LighthouseA",
        "output": "M01_LIGHTHOUSE_A.glb",
    },
    "SM_M01_Midrise_Production_B_CONSOLIDATED.glb": {
        "sha256": "6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155",
        "old": "SM_M01_Midrise_Production_B",
        "new": "SM_M01_MidriseB",
        "output": "M01_MIDRISE_B.glb",
    },
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


def read_glb(path: Path) -> tuple[dict, list[tuple[int, bytes]]]:
    raw = path.read_bytes()
    require(len(raw) >= 20, f"GLB too short: {path}")
    magic, version, length = struct.unpack_from("<4sII", raw, 0)
    require(magic == b"glTF" and version == 2 and length == len(raw), f"Invalid GLB header: {path}")
    offset = 12
    chunks = []
    while offset < len(raw):
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        payload = raw[offset : offset + chunk_length]
        require(len(payload) == chunk_length, f"Truncated GLB chunk: {path}")
        chunks.append((chunk_type, payload))
        offset += chunk_length
    require(chunks and chunks[0][0] == 0x4E4F534A, f"GLB JSON chunk absent: {path}")
    return json.loads(chunks[0][1].decode("utf-8").rstrip("\x00 \t\r\n")), chunks


def write_glb(path: Path, document: dict, chunks: list[tuple[int, bytes]]) -> None:
    json_payload = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    json_payload += b" " * ((4 - len(json_payload) % 4) % 4)
    new_chunks = [(0x4E4F534A, json_payload)] + chunks[1:]
    total = 12 + sum(8 + len(payload) for _, payload in new_chunks)
    data = bytearray(struct.pack("<4sII", b"glTF", 2, total))
    for chunk_type, payload in new_chunks:
        data.extend(struct.pack("<II", len(payload), chunk_type))
        data.extend(payload)
    path.write_bytes(bytes(data))


def normalize_document(document: dict, old_prefix: str, new_prefix: str) -> list[dict]:
    original = copy.deepcopy(document)
    changes = []
    for collection_name in ("meshes", "nodes"):
        for index, item in enumerate(document.get(collection_name, [])):
            old = str(item.get("name", ""))
            if old_prefix in old:
                new = old.replace(old_prefix, new_prefix)
                require(len(new) <= MAX_UNREAL_OBJECT_NAME, f"Normalized identity remains too long: {new}")
                item["name"] = new
                changes.append({"path": f"{collection_name}[{index}].name", "before": old, "after": new})
    restored = copy.deepcopy(document)
    for change in changes:
        collection, remainder = change["path"].split("[", 1)
        index_text, key = remainder.split("]", 1)
        restored[collection][int(index_text)][key.lstrip(".")] = change["before"]
    require(restored == original, "Metadata normalization exceeded the mesh/node-name allowlist")
    require(changes, f"No identity changes found for {old_prefix}")
    return changes


def validate_normalized(path: Path, new_prefix: str) -> dict:
    document, chunks = read_glb(path)
    mesh_names = [str(row.get("name", "")) for row in document.get("meshes", [])]
    node_names = [str(row.get("name", "")) for row in document.get("nodes", [])]
    governed = [name for name in mesh_names + node_names if new_prefix in name]
    require(governed and all(len(name) <= MAX_UNREAL_OBJECT_NAME for name in governed), f"Unsafe normalized identity: {path}")
    sockets = [name for name in node_names if name.startswith("SOCKET_")]
    require(len(sockets) == 1 and len(sockets[0]) <= MAX_UNREAL_OBJECT_NAME, f"Invalid socket identity: {path}")
    render_meshes = [name for name in mesh_names if not name.startswith("UCX_")]
    collision_meshes = [name for name in mesh_names if name.startswith("UCX_")]
    require(len(render_meshes) in (2, 3) and len(collision_meshes) == 1, f"Mesh budget changed: {path}")
    return {"mesh_names": mesh_names, "socket": sockets[0], "render_mesh_count": len(render_meshes), "collision_mesh_count": len(collision_meshes), "non_json_chunk_hashes": [sha256_bytes(payload) for _, payload in chunks[1:]]}


def offline_contract_test() -> int:
    for filename, rule in RULES.items():
        source = SOURCE / filename
        require(source.is_file() and sha256(source) == rule["sha256"], f"Source GLB authority changed: {source}")
        document, chunks = read_glb(source)
        before = [sha256_bytes(payload) for _, payload in chunks[1:]]
        changes = normalize_document(document, rule["old"], rule["new"])
        require(changes and before == [sha256_bytes(payload) for _, payload in chunks[1:]], "In-memory binary chunk changed")
    require(not OUTPUT.exists(), f"Governed output exists during offline test: {OUTPUT}")
    print("PASS_UNREAL_SAFE_IDENTITY_CONTRACT")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        return offline_contract_test()
    require(not OUTPUT.exists(), f"Fresh output namespace already exists: {OUTPUT}")
    EXPORTS.mkdir(parents=True)
    results = []
    for filename, rule in RULES.items():
        source = SOURCE / filename
        require(source.is_file() and sha256(source) == rule["sha256"], f"Source authority failed: {source}")
        document, chunks = read_glb(source)
        non_json_before = [sha256_bytes(payload) for _, payload in chunks[1:]]
        changes = normalize_document(document, rule["old"], rule["new"])
        destination = EXPORTS / rule["output"]
        write_glb(destination, document, chunks)
        validated = validate_normalized(destination, rule["new"])
        require(validated["non_json_chunk_hashes"] == non_json_before, f"Non-JSON GLB chunk changed: {source}")
        results.append({"source": record(source), "output": record(destination), "changes": changes, "validation": validated, "binary_geometry_images_and_material_payloads_unchanged": True})
    receipt = {
        "schema": "skyguard.m01-visible-environment-metadata-normalization02-receipt.v1",
        "created_utc": utc_now(),
        "classification": "PASSED_UNREAL_SAFE_METADATA_READY_FOR_FULL_KIT_IMPORT_RECOVERY01",
        "failed_import_freeze": str(ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_ATTEMPT01_TERMINAL_FREEZE.json"),
        "files": results,
        "geometry_modified": False,
        "materials_modified": False,
        "binary_chunks_modified": False,
        "max_unreal_object_name": MAX_UNREAL_OBJECT_NAME,
        "allowed_metadata_changes": ["meshes[*].name semantic prefix shortening", "nodes[*].name semantic prefix shortening", "output GLB filename shortening"],
        "next_gate": "FULL_KIT_IMPORT_RECOVERY01_IN_FRESH_SHORT_DESTINATION",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path != INVENTORY)
    INVENTORY.write_text(json.dumps({"schema": "skyguard.m01-visible-environment-metadata-normalization02-inventory.v1", "created_utc": utc_now(), "files": [record(path) for path in files]}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
