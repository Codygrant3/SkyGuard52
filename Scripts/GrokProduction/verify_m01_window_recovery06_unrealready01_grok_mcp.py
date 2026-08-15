from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


SOURCE_BLEND = Path(
    r"D:\Skyguard52\Production\Attempts\m01-hero-prewar-window-bay-a01-recovery06\attempt_20260811T001334809772Z\output\M01_Hero_Prewar_Window_Bay_A01_Recovery06.blend"
)
SOURCE_BLEND_BYTES = 371733
SOURCE_BLEND_SHA256 = "70ebdc7e23fdcfc00acecdede5970b2d63ccbcfab7036d227399c21794de294b"
SOURCE_FREEZE = Path(
    r"D:\Skyguard52\Docs\AAA_Review\M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY06_ATTEMPT01_ACCEPTANCE_FREEZE.json"
)
SOURCE_FREEZE_BYTES = 6222
SOURCE_FREEZE_SHA256 = "6c929e8ae2e25d80de30b3a35a762086dbbe4520d61ffe6a2ba4e50dda82540c"

RENDER_MESHES = {
    "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "SM_M01_PrewarWindowBay_A01_Glass",
    "SM_M01_PrewarWindowBay_A01_Interior",
}
COLLISION_MESHES = {
    f"UCX_SM_M01_PrewarWindowBay_A01_FrameFacadeHardware_{index:02d}"
    for index in range(4)
}
SOCKETS = {
    "SOCKET_M01_PrewarWindowR03_Center",
    "SOCKET_M01_PrewarWindowR03_Latch",
    "SOCKET_M01_PrewarWindowR03_Origin",
}
RENDERS = {
    "01_front_daylight.png",
    "02_left_oblique_daylight.png",
    "03_right_oblique_overcast.png",
    "04_interior_parallax.png",
    "05_hardware_grazing.png",
    "06_night_glazing.png",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def authority(path: Path, expected_bytes: int, expected_hash: str, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing authority: {path}")
        return {"path": str(path), "exists": False}
    actual_bytes = path.stat().st_size
    actual_hash = sha256(path)
    matched = actual_bytes == expected_bytes and actual_hash == expected_hash
    if not matched:
        errors.append(f"authority mismatch: {path}")
    return {
        "path": str(path),
        "exists": True,
        "bytes": actual_bytes,
        "sha256": actual_hash,
        "expected_bytes": expected_bytes,
        "expected_sha256": expected_hash,
        "matched": matched,
    }


def parse_glb(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("GLB is too short")
    magic, version, declared_length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67 or version != 2 or declared_length != len(data):
        raise ValueError("invalid GLB header")
    json_length, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise ValueError("first GLB chunk is not JSON")
    payload = json.loads(data[20 : 20 + json_length].decode("utf-8").rstrip(" \t\r\n\x00"))
    node_names = {node.get("name") for node in payload.get("nodes", []) if node.get("name")}
    mesh_names = {mesh.get("name") for mesh in payload.get("meshes", []) if mesh.get("name")}
    material_names = {
        material.get("name") for material in payload.get("materials", []) if material.get("name")
    }
    return {
        "bytes": len(data),
        "sha256": sha256(path),
        "declared_length": declared_length,
        "node_count": len(payload.get("nodes", [])),
        "mesh_count": len(payload.get("meshes", [])),
        "material_count": len(payload.get("materials", [])),
        "node_names": sorted(node_names),
        "mesh_names": sorted(mesh_names),
        "material_names": sorted(material_names),
    }


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG header: {path}")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    attempt = args.attempt.resolve()
    output = attempt / "output"
    errors: list[str] = []
    authorities = [
        authority(SOURCE_BLEND, SOURCE_BLEND_BYTES, SOURCE_BLEND_SHA256, errors),
        authority(SOURCE_FREEZE, SOURCE_FREEZE_BYTES, SOURCE_FREEZE_SHA256, errors),
    ]

    blend = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery06_UnrealReady01.blend"
    glb = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery06_UnrealReady01.glb"
    required_json = [
        output / "grok_implementation_report.json",
        output / "receipts" / "validation_receipt.json",
        output / "receipts" / "glb_structure_receipt.json",
        output / "receipts" / "terminal_receipt.json",
        attempt / "grok_process_exit.json",
    ]
    for path in [blend, glb, *required_json]:
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty required output: {path}")

    parsed_json: dict[str, dict] = {}
    for path in required_json:
        if path.is_file() and path.stat().st_size:
            try:
                parsed_json[path.name] = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid JSON {path}: {exc}")

    glb_info: dict = {}
    if glb.is_file() and glb.stat().st_size:
        try:
            glb_info = parse_glb(glb)
            mesh_names = set(glb_info["mesh_names"])
            node_names = set(glb_info["node_names"])
            if mesh_names != RENDER_MESHES | COLLISION_MESHES:
                errors.append(f"unexpected GLB mesh set: {sorted(mesh_names)}")
            if not (RENDER_MESHES | COLLISION_MESHES | SOCKETS).issubset(node_names):
                errors.append("GLB is missing required render, collision, or socket nodes")
            if glb_info["mesh_count"] != 7:
                errors.append(f"expected 7 GLB meshes, got {glb_info['mesh_count']}")
            if glb_info["material_count"] != 15:
                errors.append(f"expected 15 exported material slots including collision, got {glb_info['material_count']}")
        except Exception as exc:
            errors.append(f"GLB validation failed: {exc}")

    image_records: list[dict] = []
    render_dir = output / "renders"
    actual_renders = {path.name for path in render_dir.glob("*.png")} if render_dir.is_dir() else set()
    if actual_renders != RENDERS:
        errors.append(f"unexpected render set: {sorted(actual_renders)}")
    for name in sorted(RENDERS):
        path = render_dir / name
        if not path.is_file():
            continue
        try:
            width, height = png_dimensions(path)
            if (width, height) != (1920, 1080):
                errors.append(f"wrong dimensions for {name}: {width}x{height}")
            image_records.append(
                {
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "width": width,
                    "height": height,
                }
            )
        except Exception as exc:
            errors.append(str(exc))

    validation = parsed_json.get("validation_receipt.json", {})
    expected_counts = {
        "production_render_mesh_count": 3,
        "ucx_count": 4,
        "socket_count": 3,
        "accepted_material_count_present": 14,
        "total_production_vertices": 21058,
        "total_production_polygons": 20496,
    }
    for key, expected in expected_counts.items():
        if validation.get(key) != expected:
            errors.append(f"validation receipt {key}: expected {expected}, got {validation.get(key)}")
    exit_receipt = parsed_json.get("grok_process_exit.json", {})
    if exit_receipt.get("exit_code") != 0 or exit_receipt.get("exit_code_type") != "System.Int32":
        errors.append("Grok process exit receipt is not numeric System.Int32 zero")

    artifacts = []
    if output.is_dir():
        for path in sorted((item for item in output.rglob("*") if item.is_file()), key=lambda p: str(p).lower()):
            artifacts.append(
                {
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    report = {
        "schema": "skyguard.m01-window-bay.unrealready01.independent-postflight.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW" if not errors else "FAILED_WITH_EVIDENCE"
        ),
        "passed": not errors,
        "errors": errors,
        "attempt": str(attempt),
        "authorities": authorities,
        "blend": (
            {"path": str(blend), "bytes": blend.stat().st_size, "sha256": sha256(blend)}
            if blend.is_file()
            else {"path": str(blend), "missing": True}
        ),
        "glb": glb_info,
        "renders": image_records,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": report["classification"], "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
