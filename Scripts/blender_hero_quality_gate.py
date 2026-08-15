from __future__ import annotations

"""Cheap, fail-closed triage for generated Blender hero-asset attempts.

This is not a visual acceptance system. It catches objective proxy-quality
symptoms before a human spends time on all full-resolution renders. Passing it
never authorizes Unreal import.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


class QualityGateError(RuntimeError):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise QualityGateError(f"Invalid JSON {path}: {exc}") from exc


def _image_metrics(
    path: Path,
    dark_threshold: float,
    bright_threshold: float = 0.98,
    roi_normalized: list[float] | None = None,
) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    source_height, source_width = int(rgb.shape[0]), int(rgb.shape[1])
    roi_pixels: list[int] | None = None
    if roi_normalized is not None:
        if len(roi_normalized) != 4:
            raise QualityGateError(f"ROI must have four normalized coordinates: {roi_normalized}")
        x0, y0, x1, y1 = (float(value) for value in roi_normalized)
        if not (0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0):
            raise QualityGateError(f"Invalid normalized ROI: {roi_normalized}")
        left = int(round(x0 * source_width))
        top = int(round(y0 * source_height))
        right = int(round(x1 * source_width))
        bottom = int(round(y1 * source_height))
        if right <= left or bottom <= top:
            raise QualityGateError(f"ROI has no pixels in {path}: {roi_normalized}")
        rgb = rgb[top:bottom, left:right]
        roi_pixels = [left, top, right, bottom]
    luminance = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    return {
        "path": str(path),
        "source_width": source_width,
        "source_height": source_height,
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "roi_normalized": roi_normalized,
        "roi_pixels": roi_pixels,
        "mean_luminance": float(luminance.mean()),
        "luminance_stddev": float(luminance.std()),
        "dark_pixel_fraction": float((luminance < dark_threshold).mean()),
        "bright_pixel_fraction": float((luminance > bright_threshold).mean()),
        "dark_threshold": dark_threshold,
        "bright_threshold": bright_threshold,
    }


def evaluate(attempt: Path, contract: dict[str, Any]) -> dict[str, Any]:
    configuration = contract.get("quality_gate")
    if not isinstance(configuration, dict):
        return {
            "schema": "skyguard.blender-hero-quality-gate.v1",
            "configured": False,
            "pass": True,
            "errors": [],
            "human_visual_review_still_required": True,
            "unreal_import_authorized": False,
        }

    output = attempt / "output"
    errors: list[str] = []
    report: dict[str, Any] = {
        "schema": "skyguard.blender-hero-quality-gate.v1",
        "configured": True,
        "profile": configuration.get("profile"),
        "pass": False,
        "errors": errors,
        "human_visual_review_still_required": True,
        "unreal_import_authorized": False,
    }

    topology_config = configuration.get("topology")
    if isinstance(topology_config, dict):
        receipt_path = output / str(topology_config["receipt"])
        if not receipt_path.is_file():
            errors.append(f"Missing topology receipt: {receipt_path}")
        else:
            receipt = _load_json(receipt_path)
            excluded_roles = {str(role) for role in topology_config.get("excluded_roles", [])}
            renderable = [
                item
                for item in receipt.get("objects", [])
                if item.get("type") == "MESH"
                and int(item.get("polygons", 0)) > 0
                and str(item.get("role")) not in excluded_roles
            ]
            total_vertices = sum(int(item.get("vertices", 0)) for item in renderable)
            missing_uvs = sorted(
                str(item.get("name"))
                for item in renderable
                if int(item.get("uv_layers", 0)) < 1
            )
            primary_roles = {str(role) for role in topology_config.get("primary_roles", [])}
            primary_vertices = sum(
                int(item.get("vertices", 0))
                for item in renderable
                if str(item.get("role")) in primary_roles
            )
            material_names = {
                str(material)
                for item in renderable
                for material in item.get("materials", [])
                if material
            }
            minimum_total = int(topology_config.get("minimum_total_renderable_vertices", 0))
            minimum_primary = int(topology_config.get("minimum_primary_vertices", 0))
            minimum_materials = int(topology_config.get("minimum_material_count", 0))
            if missing_uvs:
                errors.append(f"Renderable meshes without UVs: {missing_uvs}")
            if total_vertices < minimum_total:
                errors.append(f"Renderable vertex count {total_vertices} is below {minimum_total}.")
            if primary_vertices < minimum_primary:
                errors.append(f"Primary-form vertex count {primary_vertices} is below {minimum_primary}.")
            if len(material_names) < minimum_materials:
                errors.append(
                    f"Distinct renderable material count {len(material_names)} is below {minimum_materials}."
                )
            report["topology"] = {
                "receipt": str(receipt_path),
                "excluded_roles": sorted(excluded_roles),
                "renderable_mesh_count": len(renderable),
                "total_renderable_vertices": total_vertices,
                "minimum_total_renderable_vertices": minimum_total,
                "primary_vertices": primary_vertices,
                "minimum_primary_vertices": minimum_primary,
                "distinct_material_count": len(material_names),
                "minimum_material_count": minimum_materials,
                "missing_uvs": missing_uvs,
            }

    image_results: list[dict[str, Any]] = []
    for rule in configuration.get("image_rules", []):
        paths = sorted(output.glob(str(rule["glob"])))
        if not paths:
            errors.append(f"Image quality rule matched no files: {rule['glob']}")
            continue
        dark_threshold = float(rule.get("dark_threshold", 0.02))
        bright_threshold = float(rule.get("bright_threshold", 0.98))
        minimum_mean = float(rule.get("minimum_mean_luminance", 0.0))
        maximum_mean = float(rule.get("maximum_mean_luminance", 1.0))
        maximum_dark = float(rule.get("maximum_dark_pixel_fraction", 1.0))
        maximum_bright = float(rule.get("maximum_bright_pixel_fraction", 1.0))
        minimum_stddev = float(rule.get("minimum_luminance_stddev", 0.0))
        roi_normalized = rule.get("roi_normalized")
        for path in paths:
            metrics = _image_metrics(
                path,
                dark_threshold,
                bright_threshold,
                roi_normalized=roi_normalized,
            )
            metrics["minimum_mean_luminance"] = minimum_mean
            metrics["maximum_mean_luminance"] = maximum_mean
            metrics["maximum_dark_pixel_fraction"] = maximum_dark
            metrics["maximum_bright_pixel_fraction"] = maximum_bright
            metrics["minimum_luminance_stddev"] = minimum_stddev
            metrics["pass"] = (
                metrics["mean_luminance"] >= minimum_mean
                and metrics["mean_luminance"] <= maximum_mean
                and metrics["luminance_stddev"] >= minimum_stddev
                and metrics["dark_pixel_fraction"] <= maximum_dark
                and metrics["bright_pixel_fraction"] <= maximum_bright
            )
            if not metrics["pass"]:
                errors.append(
                    f"Unreadable or clipped review frame/region {path.name}: mean_luminance="
                    f"{metrics['mean_luminance']:.4f}, dark_pixel_fraction="
                    f"{metrics['dark_pixel_fraction']:.4f}, bright_pixel_fraction="
                    f"{metrics['bright_pixel_fraction']:.4f}, luminance_stddev="
                    f"{metrics['luminance_stddev']:.4f}."
                )
            image_results.append(metrics)
    report["images"] = image_results
    report["pass"] = not errors
    return report
