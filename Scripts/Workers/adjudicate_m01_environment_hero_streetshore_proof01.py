from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


ASSET_ID = "m01-environment-hero-streetshore-proof01"
EXPECTED_CONDITIONS = ("daylight", "wet_overcast", "night")
EXPECTED_CAMERAS = ("route_composite", "facade_close", "shoreline_close")
REQUIRED_RECEIPTS = (
    "artifact_manifest.json",
    "geometry_receipt.json",
    "pbr_receipt.json",
    "render_receipt.json",
    "export_receipt.json",
)
REQUIRED_SOCKETS = (
    "SOCKET_District_W",
    "SOCKET_District_E",
    "SOCKET_Shoreline_Origin",
    "SOCKET_Road_Origin",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_glb(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("Invalid GLB magic or length")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_length != len(data):
        raise ValueError("Invalid GLB version or declared length")
    offset = 12
    document = None
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_length]
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.rstrip(b" \t\r\n\x00").decode("utf-8"))
            break
    if not isinstance(document, dict):
        raise ValueError("GLB JSON chunk missing")
    return document


def image_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
        width, height = image.size
    linear = np.power(rgb, 2.2)
    luma = linear[..., 0] * 0.2126 + linear[..., 1] * 0.7152 + linear[..., 2] * 0.0722
    gray = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    edge_fraction = float((np.concatenate((dx.ravel(), dy.ravel())) > 0.035).mean())
    return {
        "width": width,
        "height": height,
        "mean_luma_linear": float(luma.mean()),
        "black_fraction_linear_0_01": float((luma < 0.01).mean()),
        "edge_fraction_0_035": edge_fraction,
    }


def validate(attempt_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    output = attempt_dir / "output"
    terminal_path = attempt_dir / "terminal.json"
    stdout_path = attempt_dir / "blender.stdout.log"
    stderr_path = attempt_dir / "blender.stderr.log"

    if not terminal_path.is_file():
        errors.append("terminal.json missing")
        terminal = {}
    else:
        terminal = load_json(terminal_path)
        if terminal.get("asset_id") != ASSET_ID:
            errors.append("terminal asset id mismatch")
        if terminal.get("status") != "awaiting_review":
            errors.append(f"terminal status is {terminal.get('status')!r}")
        if terminal.get("launch_count") != 1:
            errors.append("launch count is not one")
        if terminal.get("retry_count") != 0:
            errors.append("retry count is not zero")
        if terminal.get("exit_code") != 0 or terminal.get("exit_code_type") not in ("int", "System.Int32"):
            errors.append("numeric successful exit evidence missing")

    stdout = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.is_file() else ""
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.is_file() else ""
    combined = stdout + "\n" + stderr
    if "Traceback (most recent call last)" in combined:
        errors.append("traceback found in Blender logs")
    if "FAILED_WITH_EVIDENCE" in combined:
        errors.append("failure classification found in Blender logs")

    blend_files = sorted(output.glob("*.blend")) if output.is_dir() else []
    glb_files = sorted(output.glob("*.glb")) if output.is_dir() else []
    png_files = sorted((output / "renders").glob("*.png")) if (output / "renders").is_dir() else []
    if len(blend_files) != 1:
        errors.append(f"expected one blend, found {len(blend_files)}")
    if len(glb_files) != 1:
        errors.append(f"expected one GLB, found {len(glb_files)}")
    if len(png_files) != 9:
        errors.append(f"expected nine PNGs, found {len(png_files)}")
    for receipt in REQUIRED_RECEIPTS:
        if not (output / receipt).is_file():
            errors.append(f"missing receipt: {receipt}")

    receipt_payloads: dict[str, dict[str, Any]] = {}
    for receipt in REQUIRED_RECEIPTS:
        path = output / receipt
        if path.is_file():
            try:
                receipt_payloads[receipt] = load_json(path)
            except Exception as exc:
                errors.append(f"invalid receipt {receipt}: {exc}")

    geometry = receipt_payloads.get("geometry_receipt.json", {})
    stats = geometry.get("statistics", {})
    if geometry and geometry.get("fresh_geometry") is not True:
        errors.append("fresh geometry flag missing")
    if geometry and geometry.get("recovery10_mesh_reuse") is not False:
        errors.append("Recovery10 mesh-reuse prohibition failed")
    if int(stats.get("mesh_objects", 0)) < 260:
        errors.append("mesh object count below 260")
    if int(stats.get("vertices", 0)) < 12000:
        errors.append("vertex count below 12000")

    pbr = receipt_payloads.get("pbr_receipt.json", {})
    authorities = pbr.get("texture_authorities", [])
    if pbr and len(authorities) != 20:
        errors.append(f"expected 20 texture authorities, found {len(authorities)}")
    if pbr and int(pbr.get("material_count", 0)) < 20:
        errors.append("material count below 20")
    for authority in authorities:
        path = Path(authority.get("path", ""))
        if not path.is_file():
            errors.append(f"texture authority missing: {path}")
            continue
        if path.stat().st_size != int(authority.get("bytes", -1)) or sha256(path) != authority.get("sha256"):
            errors.append(f"texture authority mismatch: {path}")

    image_results = []
    expected_names = {f"{condition}_{camera}.png" for condition in EXPECTED_CONDITIONS for camera in EXPECTED_CAMERAS}
    actual_names = {path.name for path in png_files}
    if actual_names != expected_names:
        errors.append(f"render names differ: missing={sorted(expected_names-actual_names)} unexpected={sorted(actual_names-expected_names)}")
    for path in png_files:
        try:
            metrics = image_metrics(path)
            condition = path.stem.split("_", 1)[0]
            if path.stem.startswith("wet_overcast_"):
                condition = "wet_overcast"
            thresholds = {
                "daylight": (0.035, 0.45, 0.025),
                "wet_overcast": (0.020, 0.58, 0.022),
                "night": (0.008, 0.78, 0.012),
            }[condition]
            if (metrics["width"], metrics["height"]) != (1920, 1080):
                errors.append(f"wrong PNG dimensions: {path.name}")
            if metrics["mean_luma_linear"] < thresholds[0]:
                errors.append(f"underexposed PNG: {path.name}")
            if metrics["black_fraction_linear_0_01"] > thresholds[1]:
                errors.append(f"excessively black PNG: {path.name}")
            if metrics["edge_fraction_0_035"] < thresholds[2]:
                errors.append(f"insufficient visual detail density: {path.name}")
            image_results.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path), "metrics": metrics})
        except Exception as exc:
            errors.append(f"PNG validation failed for {path.name}: {exc}")

    glb_result: dict[str, Any] = {}
    if len(glb_files) == 1:
        try:
            document = parse_glb(glb_files[0])
            node_names = [node.get("name", "") for node in document.get("nodes", [])]
            missing_sockets = [name for name in REQUIRED_SOCKETS if name not in node_names]
            if missing_sockets:
                errors.append(f"GLB missing sockets: {missing_sockets}")
            if not any(name.startswith("UCX_") for name in node_names):
                errors.append("GLB contains no UCX collision node")
            if len(document.get("meshes", [])) < 200:
                errors.append("GLB mesh count below 200")
            if len(document.get("materials", [])) < 16:
                errors.append("GLB material count below 16")
            glb_result = {
                "path": str(glb_files[0]),
                "bytes": glb_files[0].stat().st_size,
                "sha256": sha256(glb_files[0]),
                "node_count": len(document.get("nodes", [])),
                "mesh_count": len(document.get("meshes", [])),
                "material_count": len(document.get("materials", [])),
                "image_count": len(document.get("images", [])),
                "missing_sockets": missing_sockets,
            }
        except Exception as exc:
            errors.append(f"GLB validation failed: {exc}")

    return {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.postflight.v1",
        "asset_id": ASSET_ID,
        "attempt_dir": str(attempt_dir),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW" if not errors else "FAILED_WITH_EVIDENCE",
        "errors": errors,
        "terminal": {
            "path": str(terminal_path),
            "sha256": sha256(terminal_path) if terminal_path.is_file() else None,
            "launch_count": terminal.get("launch_count"),
            "retry_count": terminal.get("retry_count"),
            "exit_code": terminal.get("exit_code"),
            "exit_code_type": terminal.get("exit_code_type"),
        },
        "blend": {"path": str(blend_files[0]), "bytes": blend_files[0].stat().st_size, "sha256": sha256(blend_files[0])} if len(blend_files) == 1 else None,
        "glb": glb_result,
        "images": image_results,
        "receipt_hashes": {name: sha256(output / name) for name in REQUIRED_RECEIPTS if (output / name).is_file()},
        "direct_full_resolution_review_required": True,
        "promotion_authorized": False,
        "unreal_import_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = validate(Path(args.attempt_dir).resolve())
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["classification"].startswith("PASSED_") else 4


if __name__ == "__main__":
    raise SystemExit(main())
