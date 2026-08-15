"""Mandatory automatic postflight for consolidated Mission 1 exports."""

from __future__ import annotations

import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01"
RECEIPT = OUTPUT / "unreal_ready_export_receipt.json"
INVENTORY = OUTPUT / "artifact_inventory.json"
REPORT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_POSTFLIGHT.json"

EXPECTED_GROUPS = {
    "SM_M01_Apartment_Production_A": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_Midrise_Production_B": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_CornerResidence_Production_C": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_CoastalDistrict_Production_A": {"TERRAIN", "HARDSCAPE"},
    "SM_M01_Lighthouse_Production_A": {"STRUCTURAL", "GLAZING", "DETAILS"},
}
EXCLUDED = ("_WATER", "_FOAM_", "_WET_CONTACT", "_LEAF_", "_PLANT_", "_TRUNK", "_BRANCH_", "_TREE_", "_SHRUB_", "_FOLIAGE_")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def glb_json(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        magic, version, length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF" or version != 2 or length != path.stat().st_size:
            raise RuntimeError(f"Invalid GLB header: {path}")
        chunk_length, chunk_type = struct.unpack("<II", handle.read(8))
        if chunk_type != 0x4E4F534A:
            raise RuntimeError(f"GLB JSON chunk missing: {path}")
        return json.loads(handle.read(chunk_length).decode("utf-8").rstrip("\x00 "))


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Invalid PNG signature: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        if handle.read(4) != b"IHDR" or length < 8:
            raise RuntimeError(f"PNG IHDR missing: {path}")
        return struct.unpack(">II", handle.read(8))


def main() -> int:
    if REPORT.exists():
        raise RuntimeError(f"Fresh postflight namespace already exists: {REPORT}")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt["classification"] != "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_AND_UNREAL_IMPORT_REPROBE":
        raise RuntimeError("Generator receipt classification mismatch")
    if receipt["total_render_group_count"] != 14:
        raise RuntimeError("Expected fourteen consolidated render groups")

    checks: list[dict[str, object]] = []
    for asset, groups in EXPECTED_GROUPS.items():
        record = receipt["assets"][asset]
        actual_groups = {item["group"] for item in record["groups"]}
        if actual_groups != groups:
            raise RuntimeError(f"Group mismatch for {asset}: {sorted(actual_groups)}")
        for item in record["groups"]:
            if item["triangle_count_before"] != item["triangle_count_after"]:
                raise RuntimeError(f"Triangle parity failed for {asset}:{item['group']}")
            if item["uv_layer_count"] < 1:
                raise RuntimeError(f"UV layer missing for {asset}:{item['group']}")
            if item["material_slot_count"] < 1 or item["material_slot_count"] > 16:
                raise RuntimeError(f"Material-slot budget failed for {asset}:{item['group']}")

        path = OUTPUT / "exports" / f"{asset}_CONSOLIDATED.glb"
        doc = glb_json(path)
        nodes = [str(node.get("name", "")) for node in doc.get("nodes", [])]
        mesh_names = [str(mesh.get("name", "")) for mesh in doc.get("meshes", [])]
        render_names = [name for name in mesh_names if not name.startswith("UCX_")]
        expected_names = {f"{asset}_{group}" for group in groups}
        if set(render_names) != expected_names:
            raise RuntimeError(f"GLB render-mesh names mismatch for {asset}: {render_names}")
        if len(mesh_names) != len(groups) + 1:
            raise RuntimeError(f"GLB mesh budget failed for {asset}: {len(mesh_names)}")
        if not any(name.startswith("UCX_") for name in mesh_names):
            raise RuntimeError(f"Collision mesh missing from {asset}")
        if f"SOCKET_{asset}_Origin" not in nodes:
            raise RuntimeError(f"Origin socket node missing from {asset}")
        if any(token in name.upper() for token in EXCLUDED for name in nodes):
            raise RuntimeError(f"Runtime-excluded preview content found in {asset}")
        checks.append({
            "asset": asset,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "node_count": len(nodes),
            "mesh_count": len(mesh_names),
            "render_mesh_count": len(render_names),
            "material_count": len(doc.get("materials", [])),
        })

    renders = sorted((OUTPUT / "renders").glob("*.png"))
    if len(renders) != 5:
        raise RuntimeError(f"Expected five renders; found {len(renders)}")
    render_records = []
    for path in renders:
        width, height = png_dimensions(path)
        if (width, height) != (1600, 1200):
            raise RuntimeError(f"Render dimensions invalid for {path}: {width}x{height}")
        render_records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path), "width": width, "height": height})
    if not INVENTORY.is_file() or not (OUTPUT / "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_UNREAL_READY01.blend").is_file():
        raise RuntimeError("Required governed outputs missing")

    payload = {
        "schema": "skyguard.m01-visible-environment-unreal-ready01-postflight.v1",
        "created_utc": utc_now(),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_AND_UNREAL_IMPORT_REPROBE",
        "receipt": {"path": str(RECEIPT), "bytes": RECEIPT.stat().st_size, "sha256": sha256(RECEIPT)},
        "inventory": {"path": str(INVENTORY), "bytes": INVENTORY.stat().st_size, "sha256": sha256(INVENTORY)},
        "exports": checks,
        "renders": render_records,
        "total_render_mesh_count": sum(item["render_mesh_count"] for item in checks),
        "total_exported_mesh_count_including_collision": sum(item["mesh_count"] for item in checks),
        "next_gate": "DIRECT_VISUAL_REVIEW_THEN_FRESH_UNREAL_IMPORT_REPROBE",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
