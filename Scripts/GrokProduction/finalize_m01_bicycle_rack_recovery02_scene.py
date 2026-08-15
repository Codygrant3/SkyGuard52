from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy


PROJECT = Path(r"D:\Skyguard52")
BASE_FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_bicycle_rack_recovery01_scene.py"
BASE_FINALIZER_BYTES = 12217
BASE_FINALIZER_SHA = "3fb5f1d55db5cc66b69ac932ac73bee2c5f1e360fce8630219604a975928a9c3"
OUTPUT = PROJECT / "Production" / "Attempts" / "m01-bicycle-rack-grok-mcp-recovery02" / "attempt_20260811T073000000000Z" / "output"
RECEIPT = OUTPUT / "receipts" / "loop_profile_receipt.json"

RADIUS = 0.26
BASE_Z = 0.07
CENTER_Z = 0.50
CROWN_SAMPLES = 65
POINT_COUNT = 67
TOLERANCE = 0.0001


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_source_curves() -> dict:
    records = []
    x_positions = []
    for index in range(1, 6):
        name = f"SRC_BicycleRack_Loop_{index:02d}"
        obj = bpy.data.objects.get(name)
        require(obj is not None, f"Missing retained construction curve: {name}")
        require(obj.type == "CURVE", f"Construction object is not a curve: {name}")
        require(len(obj.data.splines) == 1, f"Expected one spline: {name}")
        spline = obj.data.splines[0]
        require(spline.type == "POLY", f"Expected POLY spline: {name}")
        require(len(spline.points) == POINT_COUNT, f"Expected {POINT_COUNT} points: {name}")
        require(all(abs(value - 1.0) <= 1e-6 for value in obj.scale), f"Nonidentity scale: {name}")
        require(all(abs(value) <= 1e-6 for value in obj.rotation_euler), f"Nonidentity rotation: {name}")
        require(all(abs(value) <= 1e-6 for value in obj.location), f"Nonidentity location: {name}")
        require(bool(obj.hide_render), f"Construction curve must be hidden from renders: {name}")

        points = [point.co.xyz.copy() for point in spline.points]
        x = points[0].x
        x_positions.append(x)
        require(max(abs(point.x - x) for point in points) <= TOLERANCE, f"Curve left its X plane: {name}")
        require(abs(points[0].y + RADIUS) <= TOLERANCE and abs(points[0].z - BASE_Z) <= TOLERANCE, f"Wrong first leg endpoint: {name}")
        require(abs(points[-1].y - RADIUS) <= TOLERANCE and abs(points[-1].z - BASE_Z) <= TOLERANCE, f"Wrong final leg endpoint: {name}")

        maximum_error = 0.0
        for sample_index in range(CROWN_SAMPLES):
            theta = math.pi - (math.pi * sample_index / 64.0)
            expected_y = RADIUS * math.cos(theta)
            expected_z = CENTER_Z + RADIUS * math.sin(theta)
            actual = points[sample_index + 1]
            error = math.hypot(actual.y - expected_y, actual.z - expected_z)
            maximum_error = max(maximum_error, error)
        require(maximum_error <= TOLERANCE, f"Semicircle residual exceeds tolerance for {name}: {maximum_error}")
        records.append({
            "name": name,
            "x_m": x,
            "point_count": len(points),
            "maximum_semicircle_residual_m": maximum_error,
            "hide_render": bool(obj.hide_render),
        })

    ordered = sorted(x_positions)
    spacings = [ordered[i + 1] - ordered[i] for i in range(4)]
    require(1.45 <= ordered[-1] - ordered[0] <= 1.65, "Loop X spread outside governed range")
    require(max(spacings) - min(spacings) <= TOLERANCE, "Loop X spacing is not uniform")
    require(abs((ordered[0] + ordered[-1]) * 0.5) <= TOLERANCE, "Loop array is not centered on X=0")

    value = {
        "schema": "skyguard.m01-bicycle-rack.loop-profile-receipt.v1",
        "classification": "PASS",
        "radius_m": RADIUS,
        "base_z_m": BASE_Z,
        "center_z_m": CENTER_Z,
        "crown_samples": CROWN_SAMPLES,
        "points_per_curve": POINT_COUNT,
        "tolerance_m": TOLERANCE,
        "x_positions_m": ordered,
        "uniform_spacing_m": sum(spacings) / len(spacings),
        "curves": records,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return value


def execute_frozen_finalizer() -> None:
    require(BASE_FINALIZER.is_file(), f"Missing base finalizer: {BASE_FINALIZER}")
    require(BASE_FINALIZER.stat().st_size == BASE_FINALIZER_BYTES, "Base finalizer byte mismatch")
    require(sha256(BASE_FINALIZER) == BASE_FINALIZER_SHA, "Base finalizer SHA-256 mismatch")
    source = BASE_FINALIZER.read_text(encoding="utf-8")

    replacements = [
        (
            r"m01-bicycle-rack-grok-mcp-recovery01\attempt_20260811T072500000000Z",
            r"m01-bicycle-rack-grok-mcp-recovery02\attempt_20260811T073000000000Z",
            1,
        ),
        ("M01_Promenade_BicycleRack_Recovery01", "M01_Promenade_BicycleRack_Recovery02", 2),
        ("skyguard.m01-bicycle-rack.grok-mcp.recovery01.report.v1", "skyguard.m01-bicycle-rack.grok-mcp.recovery02.report.v1", 1),
        (
            'for item in bpy.data.objects:\n    item.hide_render = False\nreview = bpy.data.collections.get("REVIEW_ONLY")',
            'for item in bpy.data.objects:\n    if not item.name.startswith("SRC_BicycleRack_Loop_"):\n        item.hide_render = False\nreview = bpy.data.collections.get("REVIEW_ONLY")',
            1,
        ),
    ]
    for old, new, expected_count in replacements:
        require(source.count(old) == expected_count, f"Expected {expected_count} finalizer replacement targets: {old}")
        source = source.replace(old, new)
    exec(compile(source, str(BASE_FINALIZER) + "::recovery02", "exec"), {"__name__": "__main__"})


validate_source_curves()
execute_frozen_finalizer()
