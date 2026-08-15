from __future__ import annotations

"""Automatic postflight for the continuous Mission 1 coastal corridor."""

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


ASSET_ID = "m01-coastal-corridor-correction06"
EXPECTED_RENDER_NAMES = {
    "daylight_route_aerial.png",
    "daylight_shoreline_oblique.png",
    "daylight_promenade_road.png",
    "overcast_integrated_intersection.png",
    "daylight_urban_shoulder.png",
    "overcast_wet_contact_close.png",
}
REQUIRED_RECEIPTS = {
    "artifact_manifest.json",
    "geometry_receipt.json",
    "pbr_receipt.json",
    "render_receipt.json",
    "export_receipt.json",
}
REQUIRED_NODES = {
    "SM_M01_C06_WetSand",
    "SM_M01_C06_DrySand",
    "SM_M01_C06_DuneTransition",
    "SM_M01_C06_Promenade",
    "SM_M01_C06_MainRoad",
    "SM_M01_C06_InlandSidewalk",
    "SOCKET_M01_CoastalCorridor_C06_Origin",
    "UCX_SM_M01_CoastalCorridor_C06_00",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_glb(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("invalid GLB magic or length")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_length != len(data):
        raise ValueError("invalid GLB version or declared length")
    offset = 12
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_length]
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.rstrip(b" \t\r\n\x00").decode("utf-8"))
    raise ValueError("GLB JSON chunk missing")


def image_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
        width, height = image.size
    linear = np.power(rgb, 2.2)
    luma = linear[..., 0] * 0.2126 + linear[..., 1] * 0.7152 + linear[..., 2] * 0.0722
    gray = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    return {
        "width": width,
        "height": height,
        "mean_luma_linear": float(luma.mean()),
        "black_fraction_linear_0_01": float((luma < 0.01).mean()),
        "white_fraction_linear_0_95": float((luma > 0.95).mean()),
        "edge_fraction_0_025": float((np.concatenate((dx.ravel(), dy.ravel())) > 0.025).mean()),
    }


def validate(attempt_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    output = attempt_dir / "output"
    terminal_path = attempt_dir / "terminal.json"
    stdout_path = attempt_dir / "blender.stdout.log"
    stderr_path = attempt_dir / "blender.stderr.log"

    terminal: dict[str, Any] = {}
    if not terminal_path.is_file():
        errors.append("terminal.json missing")
    else:
        terminal = read_json(terminal_path)
        if terminal.get("asset_id") != ASSET_ID:
            errors.append("terminal asset id mismatch")
        if terminal.get("status") != "awaiting_review":
            errors.append(f"terminal status is {terminal.get('status')!r}")
        if terminal.get("launch_count") != 1:
            errors.append("launch count is not one")
        if terminal.get("retry_count") != 0:
            errors.append("retry count is not zero")
        if terminal.get("exit_code") != 0 or terminal.get("exit_code_type") not in ("int", "System.Int32"):
            errors.append("numeric successful Blender exit evidence missing")

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
    if {path.name for path in png_files} != EXPECTED_RENDER_NAMES:
        errors.append(
            "render set mismatch: "
            f"missing={sorted(EXPECTED_RENDER_NAMES - {path.name for path in png_files})} "
            f"unexpected={sorted({path.name for path in png_files} - EXPECTED_RENDER_NAMES)}"
        )
    for receipt in sorted(REQUIRED_RECEIPTS):
        if not (output / receipt).is_file():
            errors.append(f"missing receipt: {receipt}")

    receipts: dict[str, dict[str, Any]] = {}
    for receipt in sorted(REQUIRED_RECEIPTS):
        path = output / receipt
        if path.is_file():
            try:
                receipts[receipt] = read_json(path)
            except Exception as exc:
                errors.append(f"invalid receipt {receipt}: {exc}")

    geometry = receipts.get("geometry_receipt.json", {})
    stats = geometry.get("statistics", {})
    if geometry:
        if geometry.get("fresh_geometry") is not True:
            errors.append("fresh geometry flag missing")
        if geometry.get("external_model_use") is not False:
            errors.append("external-model prohibition failed")
        if geometry.get("continuous_world_aligned_uv") is not True:
            errors.append("continuous UV contract failed")
        if geometry.get("tile_gap_count") != 0 or geometry.get("repeating_ground_slab_count") != 0:
            errors.append("tile-gap or repeated-slab contract failed")
        if geometry.get("integrated_cross_street_count") != 5:
            errors.append("integrated cross-street count is not five")
        if int(stats.get("mesh_objects", 0)) < 70:
            errors.append("mesh-object count below 70")
        if int(stats.get("vertices", 0)) < 3500:
            errors.append("vertex count below 3500")
        if stats.get("uv_missing"):
            errors.append(f"render meshes missing UV0: {stats.get('uv_missing')}")

    pbr = receipts.get("pbr_receipt.json", {})
    authorities = pbr.get("texture_authorities", [])
    if pbr and len(authorities) != 13:
        errors.append(f"expected thirteen texture authorities, found {len(authorities)}")
    for authority in authorities:
        path = Path(authority.get("path", ""))
        if not path.is_file():
            errors.append(f"texture authority missing: {path}")
        elif path.stat().st_size != int(authority.get("bytes", -1)) or sha256(path) != authority.get("sha256"):
            errors.append(f"texture authority mismatch: {path}")

    image_results = []
    for path in png_files:
        try:
            metrics = image_metrics(path)
            if (metrics["width"], metrics["height"]) != (1920, 1080):
                errors.append(f"wrong PNG dimensions: {path.name}")
            if metrics["mean_luma_linear"] < 0.026:
                errors.append(f"underexposed PNG: {path.name}")
            if metrics["black_fraction_linear_0_01"] > 0.46:
                errors.append(f"excessive crushed-black coverage: {path.name}")
            if metrics["white_fraction_linear_0_95"] > 0.08:
                errors.append(f"excessive clipped-white coverage: {path.name}")
            if metrics["edge_fraction_0_025"] < 0.006:
                errors.append(f"insufficient readable detail: {path.name}")
            image_results.append(
                {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path), "metrics": metrics}
            )
        except Exception as exc:
            errors.append(f"PNG validation failed for {path.name}: {exc}")

    glb_result: dict[str, Any] = {}
    if len(glb_files) == 1:
        try:
            document = parse_glb(glb_files[0])
            node_names = {node.get("name", "") for node in document.get("nodes", [])}
            missing_nodes = sorted(REQUIRED_NODES - node_names)
            cross_street_nodes = sorted(name for name in node_names if name.startswith("SM_M01_C06_IntegratedCrossStreet_"))
            parcel_nodes = sorted(name for name in node_names if name.startswith("SM_M01_C06_UrbanParcel_"))
            if missing_nodes:
                errors.append(f"GLB missing required nodes: {missing_nodes}")
            if len(cross_street_nodes) != 5:
                errors.append(f"GLB cross-street count is {len(cross_street_nodes)}, expected five")
            if len(parcel_nodes) != 6:
                errors.append(f"GLB parcel count is {len(parcel_nodes)}, expected six")
            if len(document.get("meshes", [])) < 70:
                errors.append("GLB mesh count below 70")
            if len(document.get("materials", [])) < 9:
                errors.append("GLB material count below 9")
            glb_result = {
                "path": str(glb_files[0]),
                "bytes": glb_files[0].stat().st_size,
                "sha256": sha256(glb_files[0]),
                "node_count": len(document.get("nodes", [])),
                "mesh_count": len(document.get("meshes", [])),
                "material_count": len(document.get("materials", [])),
                "image_count": len(document.get("images", [])),
                "missing_nodes": missing_nodes,
                "cross_street_count": len(cross_street_nodes),
                "parcel_count": len(parcel_nodes),
            }
        except Exception as exc:
            errors.append(f"GLB validation failed: {exc}")

    return {
        "schema": "skyguard.m01-coastal-corridor-correction06.postflight.v1",
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
        "blend": {
            "path": str(blend_files[0]),
            "bytes": blend_files[0].stat().st_size,
            "sha256": sha256(blend_files[0]),
        }
        if len(blend_files) == 1
        else None,
        "glb": glb_result,
        "images": image_results,
        "receipt_hashes": {
            name: sha256(output / name) for name in sorted(REQUIRED_RECEIPTS) if (output / name).is_file()
        },
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
    write_json(Path(args.report).resolve(), report)
    print(json.dumps(report, indent=2))
    return 0 if report["classification"].startswith("PASSED_") else 4


if __name__ == "__main__":
    raise SystemExit(main())
